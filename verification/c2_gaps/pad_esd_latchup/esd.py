# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""HBM zaps (JS-001-style 100 pF / 1.5 kOhm network) into the S2D and D2S pads on the modeled pad ring.
IHP sg13cmos5l simulation with the PDK's compact models, which are NOT calibrated for ESD currents.
Usage: python3 esd.py <work_dir> run [<filter>]   (runs the jobs whose name contains <filter>; one ngspice at a time)
       python3 esd.py <work_dir> post              (csv/ tables from the raw files)
       python3 esd.py <work_dir> wave              (HBM network check into a short and into 500 Ohm)"""
import sys
from pathlib import Path

import numpy as np

import common as C

CELLS = {'s2d': C.S2D, 'd2s': C.D2S}
VOLTS = [500, 1000, 2000]
MODES = {'gnd_vss': 'iovss grounded, iovdd floating', 'gnd_vdd': 'iovdd grounded, iovss floating',
         'p2p': 'pad to the other slot-7 pad (grounded), both rings floating'}
# Series inductance of the HBM network: set so that the 10-90 % rise into a short (2.197 L / 1.5 kOhm) sits at the
# two ends of the JS-001 rise-time window (2 ... 10 ns): L_FAST is the default, L_SLOW the sensitivity case.
L_FAST = 2e-9 / 2.197 * 1500
L_SLOW = 10e-9 / 2.197 * 1500
TIMEOUT = 240   # s wall time per HBM run (the PDK-diode runs can crawl at ps time steps)


def jobs():
    out = []
    ls = []
    for var in ('esdproxy', 'pdk'):
        for t in CELLS:
            for mode in MODES:
                for v in VOLTS:
                    for sgn in (+1, -1):
                        out.append(dict(name=f'hbm_{var}_{t}_{mode}_{"p" if sgn > 0 else "n"}{v}', var=var, pad=t,
                                        mode=mode, v=sgn * v, ls=L_FAST))
    for t in CELLS:
        for mode in ('gnd_vss', 'gnd_vdd'):
            for sgn in (+1, -1):
                ls.append(dict(name=f'hbmls_esdproxy_{t}_{mode}_{"p" if sgn > 0 else "n"}2000', var='esdproxy', pad=t,
                                mode=mode, v=sgn * 2000, ls=L_SLOW))
    main = [j for j in out if j['var'] == 'esdproxy']
    # PDK antenna-diode model as shipped: a subset (it is not meant for forward currents; see README)
    pdk = [j for j in out if j['var'] == 'pdk' and j['mode'] != 'p2p' and abs(j['v']) in (500, 2000)]
    return main + ls + pdk


def hbm_source(v0, node, ls):
    """100 pF charged to v0, closed by a switch at 1 ns, 1.5 kOhm (and optional ls) into `node`."""
    L = [f'Chbm hc 0 100p', f'.ic v(hc)={v0}',
         'Vctl ctl 0 pulse(0 1 1n 0.2n 0.2n 1 2)',
         'Shbm hc hs ctl 0 swhbm', '.model swhbm sw vt=0.5 vh=0.1 ron=0.01 roff=1e14',
         'Rhbm hs hl 1500']
    L += [f'Lhbm hl hm {ls:.6g}', f'Vzap hm {node} 0']
    return '\n'.join(L) + '\n'


def build(work, job, paths):
    mode = 'float' if job['mode'] == 'p2p' else job['mode']
    ring, _ = C.ring_netlist(mode)
    other = 'd2s' if job['pad'] == 's2d' else 's2d'
    txt = [f'* {job["name"]}: HBM {job["v"]} V into pad_{job["pad"]}, {MODES[job["mode"]]}; diode model {job["var"]}',
           C.SPDX.strip(), C.model_block('tt', job['var'], work),
           f'.include {paths[C.S2D]}', f'.include {paths[C.D2S]}', f'.include {paths["io"]}', ring,
           C.pad_instance(C.S2D, 'unpowered', 'xs2d'), C.pad_instance(C.D2S, 'unpowered', 'xd2s'),
           hbm_source(job['v'], f'pad_{job["pad"]}', job['ls'])]
    if job['mode'] == 'p2p':
        txt.append(f'Vret pad_{other} 0 0')
    else:
        txt.append(f'Rnz pad_{other} 0 1e12')
    txt.append(""".option method=gear reltol=1e-3 abstol=1e-10 vntol=1e-5 itl4=200
.temp 27
.control
set filetype=binary
tran 0.1n 1000n 0 0.5n
write %s.raw
.endc
.end
""" % job['name'])
    d = Path(work) / 'hbm'
    d.mkdir(parents=True, exist_ok=True)
    p = d / f'{job["name"]}.spice'
    p.write_text('\n'.join(txt))
    return p


PATH_DEVICES = {
    's2d': [('xs2d.xa.xs.xa1.xma', 'input device of unit XA1 (gate = pad)'),
            ('xs2d.xa.xs.xa2.xma', 'input device of unit XA2 (gate = pad)'),
            ('xs2d.xp.xmcp', 'clamp PMOS MCP (drain = pad, gate via rppd to iovdd)'),
            ('xs2d.xp.xmcn', 'clamp NMOS MCN (drain = pad, gate via rppd to iovss)')],
    'd2s': [('xd2s.xd.xc1.xmb', 'feedback input of unit C1 (gate = vfb = pad)'),
            ('xd2s.xd.xc2.xmb', 'feedback input of unit C2 (gate = vfb = pad)'),
            ('xd2s.xfp.xop', 'output PMOS OP (drain = pad)'),
            ('xd2s.xfn.xon', 'output NMOS ON (drain = pad)'),
            ('xd2s.xcma', 'Miller capacitor CMA (gate = a, body = pa: pad via 2 kOhm)'),
            ('xd2s.xcmb', 'Miller capacitor CMB (gate = pb: pad via 2 kOhm, body = b)'),
            ('xd2s.xd.xsa', 'disable switch SA (a to iovdd)'),
            ('xd2s.xd.xsb', 'disable switch SB (b to iovss)')],
}


def devices(paths):
    """Flattened MOS / diode lists of both pads with the testbench's node names."""
    out = {}
    for t, cell in CELLS.items():
        line = C.pad_instance(cell, 'unpowered', f'x{t}').split('\n')[0].split()
        out[t] = C.flatten(Path(paths[cell]).read_text(), cell, line[1:-1], f'x{t}')
    return out


def _v(pl, n):
    n = n.lower()
    if n == '0':
        return 0.0
    return pl['v(%s)' % n]


def _integ(t, y):
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(t)))


def analyze(job, pl, devs):
    """One run -> (summary row, diode rows, mos rows, waveform dict)."""
    t = pl['time']
    pad = job['pad']
    ip = pl['i(vzap)']
    vpad = _v(pl, f'pad_{pad}')
    k = int(np.argmax(np.abs(vpad)))
    row = dict(run=job['name'], diode_model=job['var'], pad=pad, config=job['mode'], v_hbm=job['v'],
               l_hbm_uH=round(job['ls'] * 1e6, 3),
               i_peak_A=float(ip[np.argmax(np.abs(ip))]), v_pad_peak=float(vpad[k]), t_v_pad_peak_ns=t[k] * 1e9,
               v_iovdd_peak=float(_v(pl, f'vd_{pad}')[np.argmax(np.abs(_v(pl, f'vd_{pad}')))]),
               v_iovss_peak=float(_v(pl, f'vs_{pad}')[np.argmax(np.abs(_v(pl, f'vs_{pad}')))]),
               v_ring_peak=float(np.max(np.abs(_v(pl, f'vd_{pad}') - _v(pl, f'vs_{pad}')))),
               i_rc_clamps_peak_A=float(np.max(np.abs(sum(pl[x] for x in pl if x.startswith('i(vcl_'))))),
               end_v_pad=float(vpad[-1]))
    drows = []
    for tt in CELLS:
        for d in devs[tt]:
            if d['kind'] != 'dio':
                continue
            nm = d['name']
            lab = {'xs2d.xp.xdp1': 'DP1', 'xs2d.xp.xdp2': 'DP2', 'xs2d.xp.xdn1': 'DN1', 'xs2d.xp.xdn2': 'DN2',
                   'xd2s.xdp0': 'DP0', 'xd2s.xdp1': 'DP1', 'xd2s.xdn0': 'DN0', 'xd2s.xdn1': 'DN1',
                   'xd2s.xspa.xd0': 'SP_DP_A', 'xd2s.xspb.xd0': 'SP_DP_B', 'xd2s.xspa.xd1': 'SP_DN_A',
                   'xd2s.xspb.xd1': 'SP_DN_B'}.get(nm)
            if lab is None:
                continue
            am = {'SP_DP_A': 'v.xd2s.xspa.vam_sp_dp', 'SP_DP_B': 'v.xd2s.xspb.vam_sp_dp',
                  'SP_DN_A': 'v.xd2s.xspa.vam_sp_dn', 'SP_DN_B': 'v.xd2s.xspb.vam_sp_dn'}.get(
                lab, ('v.xs2d.xp.vam_' if tt == 's2d' else 'v.xd2s.vam_') + lab.lower())
            i_am = pl['i(%s)' % am]
            anode, cathode = d['nodes']
            # ammeter sits on the anode for dpantenna (pad / core side = anode), on the cathode for dantenna
            ifwd = i_am if d['model'] == 'dpantenna' else -i_am
            vak = _v(pl, anode) - _v(pl, cathode)
            l = float(d['params']['l'].rstrip('u'))
            w = float(d['params']['w'].rstrip('u'))
            j = int(np.argmax(np.abs(ifwd)))
            drows.append(dict(run=job['name'], diode_model=job['var'], pad_zapped=pad, config=job['mode'],
                              v_hbm=job['v'], diode=f'{tt}.{lab}', type=d['model'], l_um=l, w_um=w,
                              area_um2=round(l * w, 3), perim_um=round(2 * (l + w), 2),
                              i_peak_A=float(ifwd[j]), j_area_mA_um2=float(ifwd[j] / (l * w) * 1e3),
                              j_perim_mA_um=float(ifwd[j] / (2 * (l + w)) * 1e3),
                              v_ak_at_peak=float(vak[j]),
                              energy_nJ=_integ(t, vak * ifwd) * 1e9))
    mrows = []
    for tt in CELLS:
        best = None
        for d in devs[tt]:
            if d['kind'] not in ('nmos', 'pmos'):
                continue
            dd, g, ss, b = (_v(pl, n) for n in d['nodes'])
            vgs = np.max(np.abs(g - ss)) if np.ndim(g - ss) else abs(g - ss)
            vgd = np.max(np.abs(g - dd)) if np.ndim(g - dd) else abs(g - dd)
            vgb = np.max(np.abs(g - b)) if np.ndim(g - b) else abs(g - b)
            vds = np.max(np.abs(dd - ss)) if np.ndim(dd - ss) else abs(dd - ss)
            vox = max(vgs, vgd, vgb)
            ent = dict(run=job['name'], diode_model=job['var'], pad_zapped=pad, config=job['mode'], v_hbm=job['v'],
                       pad=tt, device=d['name'], model=d['model'], w=d['params'].get('w'), l=d['params'].get('l'),
                       max_vgs=float(vgs), max_vgd=float(vgd), max_vgb=float(vgb), max_vox=float(vox),
                       max_vds=float(vds))
            if d['name'] in dict(PATH_DEVICES[tt]):
                ent['role'] = dict(PATH_DEVICES[tt])[d['name']]
                mrows.append(ent)
            if best is None or vox > best['max_vox']:
                best = dict(ent)
        best['role'] = 'largest max_vox of all MOS devices of this pad'
        mrows.append(best)
    tw = np.linspace(0, 400e-9, 801)
    wave = {'t_ns': tw * 1e9, 'i_zap': np.interp(tw, t, ip), 'v_pad': np.interp(tw, t, vpad),
            'v_iovdd': np.interp(tw, t, _v(pl, f'vd_{pad}')), 'v_iovss': np.interp(tw, t, _v(pl, f'vs_{pad}')),
            'i_rc_clamps': np.interp(tw, t, sum(pl[x] for x in pl if x.startswith('i(vcl_')))}
    for r in drows:
        if r['diode'].startswith(pad):
            pass
    return row, drows, mrows, wave


def run(work, filt='', keep=False):
    """Run the jobs one after the other; analyze each raw file at once and delete it (about 40 MB each) unless
    keep. Results: <work>/hbm/<run>.json (summary, diode and MOS rows, waveform)."""
    import json
    paths = C.prep_netlists(work)
    devs = devices(paths)
    for job in jobs():
        if filt and filt not in job['name']:
            continue
        p = build(work, job, paths)
        raw = p.with_suffix('.raw')
        res = p.with_suffix('.json')
        if res.exists() and '--force' not in sys.argv:
            print(job['name'], 'done before', flush=True)
            continue
        if raw.exists():
            raw.unlink()
        import re
        import subprocess
        try:
            rc = C.run_ngspice(p, p.with_suffix('.log'), timeout=TIMEOUT)
            timed_out = False
        except subprocess.TimeoutExpired:
            rc, timed_out = -1, True
        log = p.with_suffix('.log').read_text(errors='replace')
        ok = raw.exists() and 'aborted' not in log and 'Timestep too small' not in log
        status = 'ok' if ok else ('aborted' if raw.exists() else 'no raw')
        if timed_out:
            tr = re.findall(r'Reference value :\s*([0-9.eE+-]+)', log)
            status = 'stopped after %d s wall time at t = %.4g ns' % (TIMEOUT, float(tr[-1]) * 1e9 if tr else 0)
        out = {'job': job, 'status': status, 'rc': rc}
        if raw.exists():
            pl = C.read_raw(raw)[-1]['vars']
            out['t_end_ns'] = float(pl['time'][-1] * 1e9)
            if len(pl['time']) > 5:
                row, drows, mrows, wave = analyze(job, pl, devs)
                row['status'] = status
                row['t_end_ns'] = out['t_end_ns']
                out.update(summary=row, diodes=drows, mos=mrows, wave={k: v.tolist() for k, v in wave.items()})
            if not keep:
                raw.unlink()
        res.write_text(json.dumps(out))
        print(job['name'], 'rc', rc, status, 't_end %.1f ns' % out.get('t_end_ns', 0), flush=True)


def post(work):
    """Collect the per-run json files into csv/ and make the plots."""
    import json
    rows, drows, mrows = [], [], []
    waves = {}
    for job in jobs():
        f = Path(work) / 'hbm' / f'{job["name"]}.json'
        if not f.exists():
            continue
        d = json.loads(f.read_text())
        if 'summary' not in d:
            rows.append(dict(run=job['name'], diode_model=job['var'], pad=job['pad'], config=job['mode'],
                             v_hbm=job['v'], l_hbm_uH=round(job['ls'] * 1e6, 3), status=d['status']))
            continue
        s = d['summary']
        rows.append(s)
        if s['status'] != 'ok':
            continue
        for r in d['diodes']:
            if abs(r['i_peak_A']) > 1e-3:
                drows.append(r)
        mrows += d['mos']
        waves[job['name']] = d['wave']
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    rows = [{k: r.get(k, '') for k in keys} for r in rows]
    C.write_csv(C.HERE / 'csv/hbm_summary.csv', [_round(r) for r in rows],
                C.LABEL + '\nHBM 100 pF / 1.5 kOhm (+ series L, see l_hbm_uH); one row per run; status ok = run to 1 us\n'
                'v_pad_peak: signed peak pad voltage; v_ring_peak: max |iovdd - iovss| at the zapped pad; '
                'i_rc_clamps_peak_A: sum over the 5 IOPadIOVdd RC clamps')
    C.write_csv(C.HERE / 'csv/hbm_diodes.csv', [_round(r) for r in drows],
                C.LABEL + '\nper diode with |peak current| > 1 mA; i_peak_A > 0 = forward; j_* = i_peak / area or / '
                'perimeter (perimeter = 2 (l + w)); energy_nJ = integral of v_ak * i over the run')
    C.write_csv(C.HERE / 'csv/hbm_mos.csv', [_round(r) for r in mrows],
                C.LABEL + '\nmax over the run of |vg - vs|, |vg - vd|, |vg - vb|, |vd - vs| for the MOS devices on '
                'the pad path, and the device with the largest of these per pad (role column)')
    plots(rows, mrows, waves)


def _round(r):
    return {k: (float('%.5g' % v) if isinstance(v, float) else v) for k, v in r.items()}


def plots(rows, mrows, waves):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size': 8.5, 'axes.grid': True, 'grid.color': '#d8d8d4', 'figure.facecolor': 'white'})
    col = {'gnd_vss': '#2a78d6', 'gnd_vdd': '#eb6834', 'p2p': '#1baf7a'}
    # 1. waveforms at +-2 kV
    for pad in CELLS:
        fig, axs = plt.subplots(2, 2, figsize=(9, 6), sharex=True)
        for j, sgn in enumerate(('p', 'n')):
            for mode in MODES:
                nm = f'hbm_esdproxy_{pad}_{mode}_{sgn}2000'
                if nm not in waves:
                    continue
                w = waves[nm]
                axs[0, j].plot(w['t_ns'], w['v_pad'], color=col[mode], label=MODES[mode])
                axs[1, j].plot(w['t_ns'], w['i_zap'], color=col[mode])
            axs[0, j].set_title(f'{pad.upper()} pad, {"+" if sgn == "p" else "-"}2 kV HBM')
            axs[0, j].set_ylabel('pad voltage (V)')
            axs[1, j].set_ylabel('HBM current into pad (A)')
            axs[1, j].set_xlabel('time (ns)')
            axs[1, j].set_xlim(0, 400)
        axs[0, 0].legend(fontsize=7)
        fig.suptitle(f'HBM 2 kV into the {pad.upper()} pad on the modeled pad ring\n{C.LABEL}; antenna diodes: '
                     'ESD-diode proxy model', fontsize=8.5)
        fig.tight_layout()
        fig.savefig(C.HERE / f'plots/hbm_wave_{pad}.png', dpi=150)
        plt.close(fig)
    # 2. peak pad voltage vs HBM voltage
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    for j, pad in enumerate(CELLS):
        for mode in MODES:
            for var, ls in (('esdproxy', '-'), ('pdk', ':')):
                pts = sorted((r['v_hbm'], r['v_pad_peak']) for r in rows if r['pad'] == pad and r['config'] == mode
                             and r['diode_model'] == var and r.get('status') == 'ok' and r['l_hbm_uH'] < 2)
                if pts:
                    x, y = zip(*pts)
                    axs[j].plot(x, y, ls, marker='o', ms=3, color=col[mode],
                                label=f'{MODES[mode]} ({var})' if j == 0 else None)
        axs[j].set_title(f'{pad.upper()} pad')
        axs[j].set_xlabel('HBM precharge (V)')
        axs[j].set_ylabel('peak pad voltage (V)')
    axs[0].legend(fontsize=6)
    fig.suptitle(f'Peak pad voltage, {C.LABEL}\nsolid: antenna diodes as ESD-diode proxy; dotted: PDK antenna-diode '
                 'model (runs that finished)', fontsize=8.5)
    fig.tight_layout()
    fig.savefig(C.HERE / 'plots/hbm_vpad_peak.png', dpi=150)
    plt.close(fig)
    # 3. oxide voltage of the pad-path devices at +-2 kV (esdproxy, fast rise)
    fig, axs = plt.subplots(1, 2, figsize=(10, 5.2))
    for j, pad in enumerate(CELLS):
        devs = [d for d, _ in PATH_DEVICES[pad]]
        labels = [d.split('.')[-1] + ('' if d.count('.') < 3 else ' (' + d.split('.')[-2] + ')') for d in devs]
        k = 0
        width = 0.13
        for mode in MODES:
            for sgn in (2000, -2000):
                vals = []
                for dname in devs:
                    m = [r for r in mrows if r['run'] == f'hbm_esdproxy_{pad}_{mode}_{"p" if sgn > 0 else "n"}2000'
                         and r['device'] == dname and r['pad'] == pad]
                    vals.append(m[0]['max_vox'] if m else np.nan)
                axs[j].bar(np.arange(len(devs)) + (k - 2.5) * width, vals, width, color=col[mode],
                           alpha=1.0 if sgn > 0 else 0.5,
                           label=f'{MODES[mode]}, {"+" if sgn > 0 else "-"}2 kV' if j == 0 else None)
                k += 1
        axs[j].axhline(3.3, color='#52514e', ls='--', lw=0.8)
        axs[j].text(len(devs) - 0.5, 3.4, 'VGS max 3.3 V (PDK, HCI)', ha='right', fontsize=6.5)
        axs[j].set_xticks(np.arange(len(devs)))
        axs[j].set_xticklabels(labels, rotation=30, ha='right', fontsize=7)
        axs[j].set_ylabel('max |V| across gate oxide (V)')
        axs[j].set_title(f'{pad.upper()} pad: gate oxides on the pad path')
    fig.legend(fontsize=6.5, loc='lower center', ncol=3)
    fig.suptitle(f'Peak gate-oxide voltage (max of |vgs|, |vgd|, |vgb|), 2 kV HBM, {C.LABEL}; ESD-diode proxy',
                 fontsize=8.5)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.savefig(C.HERE / 'plots/hbm_oxide.png', dpi=150)
    plt.close(fig)


def wave_check(work):
    """HBM network into a short and into 500 Ohm, 2 kV, both inductances: peak current, 10-90 % rise, decay."""
    d = Path(work).resolve() / 'hbm'
    d.mkdir(parents=True, exist_ok=True)
    rows = []
    for ls, tag in ((L_FAST, 'L_fast'), (L_SLOW, 'L_slow')):
        for rl in (0.0, 500.0):
            p = d / f'wave_{tag}_{int(rl)}.spice'
            p.write_text(C.SPDX + f'* HBM network check\n' + hbm_source(2000, 'load', ls) +
                         (f'Rl load 0 {rl}\n' if rl > 0 else 'Rl load 0 1e-3\n') +
                         '.control\nset filetype=binary\ntran 0.05n 1000n 0 0.05n\nwrite %s.raw\n.endc\n.end\n' %
                         p.stem)
            C.run_ngspice(p, p.with_suffix('.log'))
            pl = C.read_raw(p.with_suffix('.raw'))[-1]['vars']
            t, i = pl['time'], pl['i(vzap)']
            ip = float(np.max(i))
            k = int(np.argmax(i))
            t10 = np.interp(0.1 * ip, i[:k + 1], t[:k + 1])
            t90 = np.interp(0.9 * ip, i[:k + 1], t[:k + 1])
            tail = i[k:]
            t37 = np.interp(-ip * np.exp(-1), -tail, t[k:])
            rows.append(dict(network=tag, l_uH=round(ls * 1e6, 3), load_ohm=rl, i_peak_A=round(ip, 4),
                             rise_10_90_ns=round((t90 - t10) * 1e9, 2), decay_to_1_over_e_ns=round((t37 - t[k]) * 1e9, 1)))
            p.with_suffix('.raw').unlink()
    C.write_csv(C.HERE / 'csv/hbm_network_check.csv', rows,
                'HBM network of esd.py (100 pF, 1.5 kOhm, series L) at 2 kV into a short (1 mOhm) and into 500 Ohm\n'
                'decay = time from the peak to 1/e of the peak (JS-001 decay time is defined differently; compare '
                'with care)')
    for r in rows:
        print(r)


if __name__ == '__main__':
    work = sys.argv[1]
    if sys.argv[2] == 'post':
        post(work)
    elif sys.argv[2] == 'wave':
        wave_check(work)
    elif sys.argv[2] == 'run':
        run(work, sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else '',
            keep='--keep' in sys.argv)
