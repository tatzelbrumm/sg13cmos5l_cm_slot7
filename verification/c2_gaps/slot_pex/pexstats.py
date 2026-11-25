#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Parasitic totals of the magic extractions (slot_7 and the two pads, C-coupled and full-RC).

Usage: python3 -I pexstats.py <work_dir> <dest_dir>
Reads <work_dir>/x_<cell>/{sak,c,rc}/<cell>.pex.spice (extract.sh) for slot_7 and the two pads;
writes <dest_dir>/csv/pex_totals.csv (one row per netlist) and <dest_dir>/csv/pex_nets.csv (per selected net).

Definitions
  C to ground   capacitors with one terminal on the substrate / ground net (slot: vss_3v3; pads: iovss), i.e. magic's
                substrate capacitance plus the coupling to the grounded supply net
  C coupling    all other capacitors (between two non-ground nets, supply vdd included)
  floating      capacitors on nodes that no device and no resistor touches (tughra_art, unused metal): their total
  per net       C_total = sum of every capacitor with a terminal on the net (full-RC: on any piece net.n<k> / net.t<k>
                or the net itself), C_gnd = the part to ground; R: number of resistor cards in the net and
                R_max = the largest effective resistance between the net's port node and any node of the net
                (inverse of the net's conductance matrix with the port grounded; only for nets with a port node)
"""
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

SUF = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3, 'meg': 1e6, 'g': 1e9, 'a': 1e-18}
S2D, D2S = 'sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single'
NETS = {
    'slot_7': ['s7_an_0_outp', 's7_an_0_outn', 's7_an_1_vinp', 's7_an_1_vinn', 's7_an_0_vcm', 'analog_bus2',
               's7_an_1_vref', 's7_an_0_vref', 'analog_bus3', 's7_an_0_iref', 's7_an_1_iref', 'analog_bus0',
               'analog_bus1', 's7_an_1_en_3v3', 's7_an_1_en_3v3_b', 'enable', 'vdd_3v3', 'vss_3v3',
               'pad_ref_rb_0.iref', 's7_ctrl_0.vcm_rb', 's7_ctrl_0.vref_rb', 'bias_dist_pd_0.iin0',
               'bg_core_pd_0.bg_n4_0.g', 'bg_core_pd_0.bg_pmir_pcas_c_0.vpg', 'bg_core_pd_0.bg_n4_0.vpc'],
    S2D: ['pad', 'outp', 'outn', 'vcm', 'vref', 'iref', 'iovdd', 'iovss'],
    D2S: ['pad', 'vinp', 'vinn', 'vref', 'iref', 'iovdd', 'iovss'],
}
GND = {'slot_7': 'vss_3v3', S2D: 'iovss', D2S: 'iovss'}


def val(s):
    m = re.fullmatch(r'([-+0-9.eE]+)([a-zA-Z]*)', s)
    x, u = float(m.group(1)), m.group(2).lower()
    return x * SUF.get(u, SUF.get(u[:1], 1.0)) if u else x


def parse(path):
    st = []
    for ln in open(path).read().splitlines():
        if ln.startswith('+') and st:
            st[-1] += ' ' + ln[1:]
        else:
            st.append(ln)
    ports, caps, res, devn, models = [], [], [], set(), defaultdict(int)
    for s in st:
        t = s.split(';')[0].split()
        if not t:
            continue
        k = t[0][0].upper()
        if t[0].lower() == '.subckt':
            ports = t[2:]
        elif k == 'C':
            caps.append((t[1], t[2], val(t[3])))
        elif k == 'R':
            res.append((t[1], t[2], val(t[3])))
        elif k == 'X':
            nn = [x for x in t[1:] if '=' not in x]
            devn.update(nn[:-1])
            models[nn[-1]] += 1
    return ports, caps, res, devn, models


def base(n, names):
    """net a node belongs to: magic names the pieces of a resistive net <net>.n<k> / <net>.t<k>"""
    m = re.fullmatch(r'(.+)\.[nt]\d+', n)
    return m.group(1) if m and m.group(1) in names else n


def rmax(res, port):
    nodes = sorted({a for a, b, _ in res} | {b for a, b, _ in res})
    if port not in nodes or len(nodes) < 2:
        return float('nan')
    idx = {n: i for i, n in enumerate(nodes)}
    G = np.zeros((len(nodes), len(nodes)))
    for a, b, r in res:
        g = 1.0 / max(r, 1e-6)
        i, j = idx[a], idx[b]
        G[i, i] += g
        G[j, j] += g
        G[i, j] -= g
        G[j, i] -= g
    keep = [i for i in range(len(nodes)) if i != idx[port]]
    Gr = G[np.ix_(keep, keep)]
    try:
        return float(np.max(np.diag(np.linalg.inv(Gr))))
    except np.linalg.LinAlgError:
        return float('nan')


def stats(cell, view, path):
    ports, caps, res, devn, models = parse(path)
    gnd = GND[cell]
    names = set(ports) | devn | {a for a, b, _ in caps} | {b for a, b, _ in caps}
    rn = {a for a, b, _ in res} | {b for a, b, _ in res}
    roots = {base(n, names) for n in names}
    netof = {n: base(n, roots) for n in names | rn}
    ctot = sum(c for *_, c in caps)
    cg = sum(c for a, b, c in caps if gnd in (netof.get(a, a), netof.get(b, b)))
    flo = {n for n in names if n not in devn and n not in rn and n not in ports}
    cflo = sum(c for a, b, c in caps if a in flo or b in flo)
    row = dict(cell=cell, view=view, devices=sum(models.values()),
               device_models=' '.join(f'{m}:{n}' for m, n in sorted(models.items())), n_C=len(caps), C_total_pF=ctot * 1e12,
               C_to_ground_pF=cg * 1e12, C_coupling_pF=(ctot - cg) * 1e12, C_floating_nodes_pF=cflo * 1e12,
               n_floating_nodes=len(flo), n_R=len(res), R_sum_kohm=sum(r for *_, r in res) / 1e3, ground_net=gnd)
    nets = []
    for n in NETS[cell]:
        cs = [(a, b, c) for a, b, c in caps if n in (netof.get(a, a), netof.get(b, b))]
        if not cs and n not in names:
            continue
        rs = [(a, b, r) for a, b, r in res if netof.get(a, a) == n]
        nets.append(dict(cell=cell, view=view, net=n, C_total_fF=sum(c for *_, c in cs) * 1e15,
                         C_gnd_fF=sum(c for a, b, c in cs if gnd in (netof.get(a, a), netof.get(b, b))) * 1e15,
                         n_R=len(rs), R_max_ohm=rmax(rs, n) if rs else float('nan')))
    return row, nets


def main(work, dest):
    work, dest = Path(work), Path(dest)
    rows, nets = [], []
    for view in ('sak', 'c', 'rc'):
        for c in ('slot_7', S2D, D2S):
            r, n = stats(c, view, work / f'x_{c}' / view / f'{c}.pex.spice')
            rows.append(r)
            nets += n
    (dest / 'csv').mkdir(parents=True, exist_ok=True)
    hdr = ('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
           '# magic PEX of the taped-out slot_7.gds and pads (extract.sh: sak = sak-pex.sh -m 2 as the earlier pad PEX, no '
           'substrate capacitance; c = C-coupled with substrate capacitance; rc = full-RC); pexstats.py; %s\n')
    with open(dest / 'csv' / 'pex_totals.csv', 'w', newline='') as f:
        f.write(hdr % 'ground = vss_3v3 (slot) / iovss (pads); C_floating = on nodes no device or resistor touches')
        w = csv.DictWriter(f, list(rows[0]), lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.4g}' if isinstance(v, float) else v) for k, v in r.items()})
    with open(dest / 'csv' / 'pex_nets.csv', 'w', newline='') as f:
        f.write(hdr % 'per net: C_total = every capacitor on the net, C_gnd = to ground; R_max = largest effective '
                'resistance port node -> any node of the net (rc only)')
        w = csv.DictWriter(f, list(nets[0]), lineterminator='\n')
        w.writeheader()
        for r in nets:
            w.writerow({k: (f'{v:.4g}' if isinstance(v, float) else v) for k, v in r.items()})
    for r in rows:
        print(r)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
