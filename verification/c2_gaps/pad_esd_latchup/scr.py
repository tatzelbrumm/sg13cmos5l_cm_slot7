# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Lumped parasitic-thyristor (PNPN) estimate for latch-up triggering by pad current injection. ngspice with
Gummel-Poon BJTs and resistors; EVERY parameter here is an ASSUMPTION (no PDK model of the parasitic bipolars
exists), swept over a range to show sensitivity. Structure (iovdd = 3.6 V, iovss = 0):
  QP  : vertical/lateral PNP, emitter = p+ at iovdd (PMOS source / ESD P cell), base = n-well node W, collector = S
  QN  : lateral NPN, emitter = n+ at iovss (NMOS source / ESD N cell), base = substrate node S, collector = W
  RNW : n-well resistance W -> iovdd tie;  RSUB : substrate resistance S -> iovss tie (p+ guard ring)
Injection (JESD78 I-test): a fraction ALPHA of the forced pad current reaches the victim structure behind the guard
rings: negative injection (pad n+ forward) -> electrons collected by the well, current ALPHA*I out of W;
positive injection (pad p+ forward) -> holes collected by the substrate, current ALPHA*I into S.
Trigger test: supply ramped 0 -> 3.6 V in 1 us (transient from all-zero, so the PNPN starts off), injection ramped
up from 2 to 3 us, held to 5 us, removed by 5.2 us; latched if the supply current is still > 1 mA at 8.9 us. The
trigger current is found by bisection (14 steps, geometric, 1 uA ... 1 A).
Usage: python3 scr.py <work_dir>   -> csv/scr_trigger.csv, plots/scr_trigger.png"""
import itertools
import sys
from pathlib import Path

import numpy as np

import common as C

BETA_N = [0.5, 2, 10]
BETA_P = [0.5, 2, 10]
RNW = [300, 3000]
RSUB = [300, 3000]
ALPHA = [0.01, 0.1]
IS_BJT = 1e-15      # assumed saturation current (Vbe ~ 0.72 V at 1 mA)
R_SER = 10          # assumed emitter and collector series resistance (Ohm) of each parasitic BJT
VSUP = 3.6


def deck(bn, bp, rnw, rsub, alpha, iinj, pol):
    src = (f'Binj W 0 I = {alpha} * {iinj} * v(ramp)' if pol == 'neg' else
           f'Binj 0 S I = {alpha} * {iinj} * v(ramp)')
    return f"""* lumped PNPN, assumed parameters
.model qn npn(is={IS_BJT} bf={bn} br=0.1 re={R_SER} rc={R_SER} cje=1p cjc=1p tf=1n)
.model qp pnp(is={IS_BJT} bf={bp} br=0.1 re={R_SER} rc={R_SER} cje=1p cjc=1p tf=1n)
Vdd vdd 0 pwl(0 0 1u {VSUP})
Vam vdd vdda 0
QP S W vdda qp
QN W S 0 qn
RNW W vdda {rnw}
RSUB S 0 {rsub}
Vramp ramp 0 pwl(0 0 2u 0 3u 1 5u 1 5.2u 0)
{src}
.option reltol=1e-4
.control
tran 5n 9u uic
let iend = -i(vdd)
meas tran ilast find iend at=8.9u
print ilast
.endc
.end
"""


def latched(work, bn, bp, rnw, rsub, alpha, iinj, pol):
    p = Path(work).resolve() / 'scr' / 'scr.spice'
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(C.SPDX + deck(bn, bp, rnw, rsub, alpha, iinj, pol))
    C.run_ngspice(p, p.with_suffix('.log'), timeout=120)
    for ln in p.with_suffix('.log').read_text(errors='replace').splitlines():
        if ln.strip().startswith('ilast'):
            return float(ln.split('=')[1].split()[0]) > 1e-3
    return None


def trigger(work, bn, bp, rnw, rsub, alpha, pol, imax=1.0):
    """Smallest injected pad current (A) that leaves the PNPN latched; inf if not up to imax; 0 if it latches
    during the supply ramp without injection."""
    if latched(work, bn, bp, rnw, rsub, alpha, 0.0, pol):
        return 0.0
    if not latched(work, bn, bp, rnw, rsub, alpha, imax, pol):
        return float('inf')
    lo, hi = 1e-6, imax
    if latched(work, bn, bp, rnw, rsub, alpha, lo, pol):
        return lo
    for _ in range(14):
        mid = np.sqrt(lo * hi)
        if latched(work, bn, bp, rnw, rsub, alpha, mid, pol):
            hi = mid
        else:
            lo = mid
    return hi


def main():
    work = sys.argv[1]
    rows = []
    for bn, bp, rnw, rsub, alpha in itertools.product(BETA_N, BETA_P, RNW, RSUB, ALPHA):
        for pol in ('neg', 'pos'):
            it = trigger(work, bn, bp, rnw, rsub, alpha, pol)
            rows.append(dict(beta_npn=bn, beta_pnp=bp, beta_product=bn * bp, r_nwell_ohm=rnw, r_sub_ohm=rsub,
                             alpha=alpha, injection=pol, i_trigger_A=it))
        print(bn, bp, rnw, rsub, alpha, rows[-2]['i_trigger_A'], rows[-1]['i_trigger_A'], flush=True)
    C.write_csv(C.HERE / 'csv/scr_trigger.csv', rows,
                'lumped PNPN latch-up estimate (scr.py); ALL parameters assumed, not from the PDK; ngspice Gummel-Poon\n'
                f'iovdd {VSUP} V; i_trigger_A = smallest forced pad current that leaves the PNPN latched '
                '(inf: not latched up to 1 A; 0: latches during the supply ramp without injection); alpha = fraction of the injected current reaching the victim well / '
                'substrate behind the guard rings')


if __name__ == '__main__':
    main()
