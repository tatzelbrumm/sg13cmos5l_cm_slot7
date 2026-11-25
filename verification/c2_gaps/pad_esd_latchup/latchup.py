# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Latch-up tests in the JESD78 style on the modeled pad ring, IHP sg13cmos5l simulation (PDK compact models; they
contain no parasitic thyristor, so latch-up itself cannot occur in these runs):
  itest : chip powered at 3.6 V (iovdd), both pads enabled at the slot operating point; a current forced into one
          pad, swept 0 -> +1 A and 0 -> -1 A (DC); where it flows, pad voltage, effect on outputs and bias lines
  ovt   : supply at 3.6 V and 5.4 V (1.5 x 3.6 V), operating point; terminal voltages of every MOS device
Usage: python3 latchup.py <work_dir> itest|ovt|post"""
import json
import sys
from pathlib import Path

import numpy as np

import common as C

CELLS = {'s2d': C.S2D, 'd2s': C.D2S}
VSUP = 3.6
IMAX = 1.0


def deck_head(work, var, title, paths):
    ring, _ = C.ring_netlist('powered', vsup=VSUP)
    return [f'* {title}', C.SPDX.strip(), C.model_block('tt', var, work),
            f'.include {paths[C.S2D]}', f'.include {paths[C.D2S]}', f'.include {paths["io"]}', ring,
            C.pad_instance(C.S2D, 'enabled', 'xs2d'), C.pad_instance(C.D2S, 'enabled', 'xd2s')]


def itest_jobs():
    out = []
    for var in ('pdk', 'esdproxy'):
        for t in CELLS:
            for sgn, tag in ((1, 'pos'), (-1, 'neg')):
                out.append(dict(name=f'itest_{var}_{t}_{tag}', var=var, pad=t, sgn=sgn))
    return out


def itest(work, filt=''):
    paths = C.prep_netlists(work)
    d = Path(work).resolve() / 'latchup'
    d.mkdir(parents=True, exist_ok=True)
    for job in itest_jobs():
        if filt and filt not in job['name']:
            continue
        txt = deck_head(work, job['var'], f'{job["name"]}: current forced into pad_{job["pad"]}, iovdd {VSUP} V',
                        paths)
        # Iinj: current from ground into the pad (positive = into the pad)
        txt.append(f'Iinj 0 pad_{job["pad"]} 0')
        txt.append(f"""Vsens_s2d s2d_outp_s 0 0
.option rshunt=1e12 itl1=500 itl2=500 gmin=1e-12
.temp 27
.control
set filetype=binary
op
write {job['name']}_op.raw
dc Iinj 0 {job['sgn'] * IMAX} {job['sgn'] * 1e-3}
write {job['name']}.raw
.endc
.end
""")
        p = d / f'{job["name"]}.spice'
        p.write_text('\n'.join(txt))
        rc = C.run_ngspice(p, p.with_suffix('.log'))
        print(job['name'], 'rc', rc, flush=True)


def ovt(work):
    paths = C.prep_netlists(work)
    d = Path(work).resolve() / 'latchup'
    d.mkdir(parents=True, exist_ok=True)
    for var in ('esdproxy',):
        txt = deck_head(work, var, f'ovt_{var}: supply swept 0 ... 5.4 V (op at each point), pads enabled', paths)
        txt.append(f"""Vsens_s2d s2d_outp_s 0 0
.option rshunt=1e12 itl1=500 itl2=500 gmin=1e-12
.temp 27
.control
set filetype=binary
dc Vsup 0 5.4 0.05
write ovt_{var}.raw
.endc
.end
""")
        p = d / f'ovt_{var}.spice'
        p.write_text('\n'.join(txt))
        rc = C.run_ngspice(p, p.with_suffix('.log'))
        print(p.name, 'rc', rc, flush=True)


def _vec(pl, n):
    return pl['v(%s)' % n] if 'v(%s)' % n in pl else pl[n]


def itest_post(work):
    d = Path(work).resolve() / 'latchup'
    rows, curves = [], {}
    for job in itest_jobs():
        raw = d / f'{job["name"]}.raw'
        if not raw.exists():
            rows.append(dict(run=job['name'], status='no raw'))
            continue
        pls = C.read_raw(raw)
        pl = pls[-1]['vars']
        sweep = pl[list(pl)[0]]
        t = job['pad']
        other = 'd2s' if t == 's2d' else 's2d'
        vpad = _vec(pl, f'pad_{t}')
        am = C.ammeter_vectors(CELLS[t], f'x{t}')
        cur = {k: pl['i(%s)' % v.replace('#branch', '')] for k, v in am.items()}
        isup = -pl['i(vsup)']                      # current delivered by the 3.6 V supply
        iss = sum(pl[k] for k in pl if k.startswith('i(vbp_vss'))   # current into the iovss bond pads (to ground)
        log = (d / f'{job["name"]}.log').read_text(errors='replace')
        status = 'ok' if abs(abs(sweep[-1]) - IMAX) < 2e-3 else 'stopped at %.3g A' % sweep[-1]
        curves[job['name']] = dict(i=sweep, vpad=vpad, isup=isup, cur=cur,
                                   outp=_vec(pl, 's2d_outp'), outn=_vec(pl, 's2d_outn'), vd2s=_vec(pl, 'pad_d2s'))
        lim = 5.4 if job['sgn'] > 0 else -1.8
        a = np.abs(vpad)
        i_lim = float(np.interp(abs(lim), a, np.abs(sweep))) if a.max() >= abs(lim) else float('nan')
        for itgt in (0.1,):
            x = itgt * job['sgn']
            k = int(np.argmin(np.abs(sweep - x)))
            if abs(sweep[k] - x) > 2e-3:
                continue
            r = dict(run=job['name'], diode_model=job['var'], pad=t, injection=('+' if job['sgn'] > 0 else '-') + '100 mA',
                     status=status, v_pad=float(vpad[k]), v_pad_at_0=float(vpad[0]),
                     i_at_vpad_limit_A=i_lim if np.isfinite(i_lim) else '> %g' % IMAX, vpad_limit=lim,
                     v_iovdd_at_pad=float(_vec(pl, f'vd_{t}')[k]), v_iovss_at_pad=float(_vec(pl, f'vs_{t}')[k]),
                     i_supply_mA=float(isup[k] * 1e3), i_supply_at_0_mA=float(isup[0] * 1e3),
                     i_iovss_pads_mA=float(iss[k] * 1e3))
            for kk, v in cur.items():
                r[f'i_{kk}_mA'] = float(v[k] * 1e3)
            if t == 's2d':
                r.update(s2d_outp=float(curves[job['name']]['outp'][k]), s2d_outn=float(curves[job['name']]['outn'][k]),
                         s2d_outp_at_0=float(curves[job['name']]['outp'][0]),
                         s2d_outn_at_0=float(curves[job['name']]['outn'][0]))
            r.update(d2s_pad=float(curves[job['name']]['vd2s'][k]), d2s_pad_at_0=float(curves[job['name']]['vd2s'][0]))
            for b in ('vbp', 'vbn', 'vbpc', 'vbnc'):
                for tt in CELLS:
                    n = f'x{tt}.{b}'
                    if 'v(%s)' % n in pl:
                        r[f'{tt}_{b}'] = float(pl['v(%s)' % n][k])
                        r[f'{tt}_{b}_at_0'] = float(pl['v(%s)' % n][0])
            rows.append(r)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    rows = [{k: (float('%.5g' % r[k]) if isinstance(r.get(k), float) else r.get(k, '')) for k in keys} for r in rows]
    C.write_csv(C.HERE / 'csv/itest.csv', rows,
                C.LABEL + f'\nJESD78-style I-test: iovdd {VSUP} V, both pads enabled (S2D vref 0.49 V / vcm 1.26 V, '
                'D2S vinp = vinn = vref = 1.26 V, iref 5 uA); DC current forced into one pad; values at +-100 mA\n'
                'i_<device>_mA: current from the pad into the device (DP/OP: + = toward iovdd; DN/ON: - = from iovss); '
                'i_supply_mA: current delivered by the 3.6 V supply (negative = the supply sinks); '
                'i_at_vpad_limit_A: forced current at which the pad reaches 5.4 V (+) / -1.8 V (-)')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 8.5, 'axes.grid': True, 'grid.color': '#d8d8d4', 'figure.facecolor': 'white'})
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4))
    col = {'pdk': '#eb6834', 'esdproxy': '#2a78d6'}
    for j, t in enumerate(CELLS):
        for name, c in curves.items():
            if f'_{t}_' not in name:
                continue
            var = 'pdk' if '_pdk_' in name else 'esdproxy'
            axs[j].plot(c['i'] * 1e3, c['vpad'], color=col[var],
                        label=var if 'pos' in name else None)
        axs[j].axhline(5.4, color='#52514e', ls='--', lw=0.8)
        axs[j].axhline(-1.8, color='#52514e', ls=':', lw=0.8)
        axs[j].axvline(100, color='#52514e', lw=0.5)
        axs[j].axvline(-100, color='#52514e', lw=0.5)
        axs[j].set_xlabel('current forced into the pad (mA)')
        axs[j].set_ylabel('pad voltage (V)')
        axs[j].set_title(f'{t.upper()} pad, iovdd 3.6 V, enabled')
        axs[j].set_ylim(-8, 15)
    axs[0].legend(title='antenna-diode model', fontsize=7)
    fig.suptitle(f'I-test (JESD78 style): pad voltage vs forced current, {C.LABEL}\ndashed: 1.5 x 3.6 V = 5.4 V; '
                 'dotted: -1.8 V', fontsize=8.5)
    fig.tight_layout()
    fig.savefig(C.HERE / 'plots/itest_vpad.png', dpi=150)
    plt.close(fig)
    return rows


def ovt_post(work):
    d = Path(work).resolve() / 'latchup'
    pl = C.read_raw(d / 'ovt_esdproxy.raw')[-1]['vars']
    vs = pl[list(pl)[0]]
    paths = C.prep_netlists(work)
    rows = []
    for t, cell in CELLS.items():
        line = C.pad_instance(cell, 'enabled', f'x{t}').split('\n')[0].split()
        devs = C.flatten(Path(paths[cell]).read_text(), cell, line[1:-1], f'x{t}')
        for vsup in (3.6, 5.4):
            k = int(np.argmin(np.abs(vs - vsup)))
            best = {}
            for dv in devs:
                if dv['kind'] not in ('nmos', 'pmos'):
                    continue
                v = [0.0 if n == '0' else float(pl['v(%s)' % n][k]) for n in dv['nodes']]
                dd, g, s_, b = v
                for q, val in (('vgs', abs(g - s_)), ('vgd', abs(g - dd)), ('vgb', abs(g - b)), ('vds', abs(dd - s_)),
                               ('vdb', abs(dd - b)), ('vsb', abs(s_ - b))):
                    if q not in best or val > best[q][0]:
                        best[q] = (val, dv['name'])
            r = dict(pad=t, v_supply=vsup, i_supply_mA=float(-pl['i(vsup)'][k] * 1e3))
            for q, (val, nm) in best.items():
                r[f'max_{q}'] = round(val, 3)
                r[f'dev_{q}'] = nm
            rows.append(r)
    C.write_csv(C.HERE / 'csv/overvoltage.csv', rows,
                C.LABEL + '\nsupply (iovdd at the IOVdd bond pads) at 3.6 and 5.4 V, operating point, both pads enabled; '
                'largest terminal-voltage difference of any MOS device of each pad and which device; i_supply_mA = '
                'total from the supply (both pads, the 5 RC clamps and IOVss diodes)')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 3.6))
    ax.semilogy(vs, np.abs(pl['i(vsup)']) * 1e3, color='#2a78d6')
    ax.axvline(3.6, color='#52514e', ls=':', lw=0.8)
    ax.axvline(5.4, color='#52514e', ls='--', lw=0.8)
    ax.set_xlabel('supply iovdd (V)')
    ax.set_ylabel('supply current (mA)')
    ax.set_title(f'Supply current vs supply, both pads enabled + ring clamps\n{C.LABEL}', fontsize=8)
    fig.tight_layout()
    fig.savefig(C.HERE / 'plots/overvoltage_isupply.png', dpi=150)
    plt.close(fig)
    return rows


if __name__ == '__main__':
    work = sys.argv[1]
    if sys.argv[2] == 'itest':
        itest(work, sys.argv[3] if len(sys.argv) > 3 else '')
    elif sys.argv[2] == 'ovt':
        ovt(work)
    elif sys.argv[2] == 'post':
        itest_post(work)
        ovt_post(work)
