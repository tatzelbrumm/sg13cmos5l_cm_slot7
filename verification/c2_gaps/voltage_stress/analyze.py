#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Collect the per-device terminal-voltage maxima of all vs.py runs; tables (Markdown), summary CSVs, plots.

Usage: python3 -I analyze.py <work_dir> <out_dir>
  reads <work_dir>/topo.csv, <work_dir>/dev/*.csv.gz, <work_dir>/nodes/*.csv.gz, <work_dir>/log/*.log
  writes <out_dir>/csv/*.csv, <out_dir>/tables.md, <out_dir>/plots/*.png

Limits compared (PDK process specification SG13CMOS5L Rev. 0.2, sections 2.1.4 ... 2.1.6, libs.doc/doc/
SG13CMOS5L_os_process_spec.pdf): VGS <= 3.3 V (maximum) at 27 C for HV-NMOS with LG >= 0.6 um and HV-PMOS with
LG >= 0.5 um (footnote: 1 FIT in 10 years for HCI); breakdown BVDSSNHV013 min 5.3 V, BVDSSPHV04 max -5.3 V
(i.e. |BVDSS| >= 5.3 V), BVDSSNIHV045 min 5.2 V (HV-iNMOS; no iNMOS is used in slot 7).
"""
import csv
import gzip
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

WORK, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
SPDX = '# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
PNGMETA = {'Copyright': '2026 Christoph Maier, Apache-2.0'}
VLIM = 3.3
VTOL = 0.001   # a device counts as above 3.3 V when it exceeds 3.3 V by more than 1 mV (numerical noise)
VFLAG = VLIM + VTOL
LG = {'sg13_hv_nmos': 0.6, 'sg13_hv_pmos': 0.5}
BVDSS = {'sg13_hv_nmos': 5.3, 'sg13_hv_pmos': 5.3}
QTY = ('vgs', 'vgd', 'vds', 'vgb', 'vsb', 'vdb')
QALL = QTY + ('vgx', 'vgs_held', 'vgd_held', 'vds_held', 'vgx_held')
TRAN = ('pu', 'en', 'step', 'mode', 'off')
CLASS_TXT = {'3.0': 'all 3.0 V runs', '3.3': 'all 3.3 V runs', '3.6': 'all 3.6 V runs',
             '3.3_27C': '3.3 V runs at 27 C', '3.6_27C': '3.6 V runs at 27 C',
             '3.3_dc': '3.3 V DC, enabled (dc)', '3.6_dc': '3.6 V DC, enabled (dc)',
             '3.3_fs': '3.3 V fail-safe (fs, fs0, fst)', '3.6_fs': '3.6 V fail-safe (fs, fs0, fst)',
             '3.3_tran': '3.3 V transients', '3.6_tran': '3.6 V transients'}
KIND_TXT = {'dc': 'DC, enabled default mode, S2D pad swept', 'fs': 'fail-safe: slot supplies 0, ring on, pads driven',
            'fs0': 'fail-safe: all supplies 0, pads driven',
            'fst': 'fail-safe as fs, as a slow transient (pad ramp 0 ... supply in 50 us)', 'off': 'disabled (enable 0), pad ramped',
            'pu': 'power-up transient', 'en': 'enable off / on edges', 'step': 'full-swing S2D pad steps',
            'mode': 'mode switching', 'topo': 'topology run (DC tt 27 C 3.3 V, as dc open)'}


def block(inst):
    p = inst.split('.')
    if p[1] == 'x2s':
        return 'S2D pad'
    if p[1] == 'x2d':
        return 'D2S pad'
    b = p[2]
    if b == 'xc':
        sub = p[3]
        if sub.startswith('xl'):
            return 's7_ctrl ls_up_fs'
        if sub.startswith('xt'):
            return 's7_ctrl tg_hv switches'
        return 's7_ctrl logic'
    return {'xbg': 'bg_core_pd', 'xd': 'bias_dist_pd', 'xr': 'pad_ref_rb', 'xdo': 's7_doutpd'}.get(b, b)


def load_topo():
    rows = []
    with open(WORK / 'topo.csv') as f:
        for r in csv.DictReader(f):
            r['L'] = round(float(r['l']) * 1e6, 4)
            r['W'] = round(float(r['w']) * 1e6, 4)
            r['NF'] = int(round(float(r['nf'] or 1)))
            r['block'] = block(r['inst'])
            r['type'] = 'HV-NMOS' if 'nmos' in r['dev'] else 'HV-PMOS'
            r['spec_L'] = r['L'] >= LG[r['dev']] - 1e-9
            r['cap'] = r['d'] == r['s']        # drain = source: MOS capacitor (or a shorted dummy)
            r['name'] = '.'.join(r['inst'].split('.')[:-1])  # subckt instance name (without the PDK's inner N)
            rows.append(r)
    return rows


def parse_tag(tag):
    m = re.match(r'^(\w+?)_(\w\w)_(-?\d+)_([\d.]+)(?:_(\w+))?$', tag)
    kind, c, t, v, var = m.groups()
    return dict(kind=kind, mos=c, temp=int(t), vdd=float(v), var=var or '')


def load_runs():
    runs = {}
    for f in sorted((WORK / 'dev').glob('*.csv.gz')):
        tag = f.name[:-7]
        info = parse_tag(tag)
        if info['kind'] == 'topo' or info['var'].startswith('chk'):
            continue   # topology run (= dc open tt 27 C 3.3 V, rerun as a dc job) and solver checks: not counted
        with gzip.open(f, 'rt') as fh:
            head = fh.readline()
            m = re.search(r'aid (\S+), (\d+) points', head)
            info['aid'], info['npts'] = (m.group(1).rstrip(','), int(m.group(2))) if m else ('?', 0)
            rd = csv.DictReader(fh)
            info['dev'] = {r['inst']: r for r in rd}
        runs[tag] = info
    return runs


def failed_runs(runs):
    out = []
    for f in sorted((WORK / 'log').glob('*.log')):
        tag = f.name[:-4]
        if tag not in runs and not tag.startswith('topo') and '_chk_' not in tag:
            txt = f.read_text(errors='replace')
            m = re.findall(r'(doAnalyses:[^\n]*|TIMEOUT[^\n]*|Error: Transient op failed[^\n]*|timestep too small[^\n]*)',
                           txt)
            t = re.findall(r'tran simulation\(s\) aborted|time = ([\d.e+-]+)', txt)
            out.append((tag, (m[-1] if m else 'no output').strip()[:160]))
    return out


def cond_txt(tag, x, q):
    if tag is None:
        return 'no run'
    i = parse_tag(tag)
    if x in ('', None):
        return f"{i['kind']}{(' ' + i['var']) if i['var'] else ''} {i['mos']} {i['temp']} C {i['vdd']} V"
    if i['kind'] in ('dc', 'fs', 'fs0', 'topo'):
        where = f'pad {float(x):.2f} V'
    else:
        where = f't = {float(x) * 1e6:.2f} us'
    return f"{i['kind']}{(' ' + i['var']) if i['var'] else ''} {i['mos']} {i['temp']} C {i['vdd']} V, {where}"


def supply_class(info):
    """Supply level the run belongs to: the ring / slot supply (fs0: the drive level, all supplies 0)."""
    return info['vdd']


def save_png(fig, path):
    """PNG with the copyright in its metadata and an SPDX sidecar <file>.license (REUSE convention)."""
    fig.savefig(path, dpi=150, metadata=PNGMETA)
    Path(str(path) + '.license').write_text(SPDX.replace('# ', ''))


def esc(s):
    return str(s).replace('|', '\\|')


def md_table(head, rows):
    out = ['| ' + ' | '.join(esc(h) for h in head) + ' |', '|' + '---|' * len(head)]
    for r in rows:
        assert len(r) == len(head), (head, r)
        out.append('| ' + ' | '.join(esc(c) for c in r) + ' |')
    return '\n'.join(out)


def main():
    topo = load_topo()
    runs = load_runs()
    fails = failed_runs(runs)
    (OUT / 'csv').mkdir(parents=True, exist_ok=True)
    (OUT / 'plots').mkdir(parents=True, exist_ok=True)
    nodeinfo = {r['inst']: r for r in topo}

    # per device x supply class x temperature filter: maximum of each |quantity| and where
    def devmax(sel):
        res = {}
        for r in topo:
            best = {q: (0.0, None, None) for q in QALL}
            for tag, info in runs.items():
                if not sel(info):
                    continue
                d = info['dev'][r['inst']]
                for q in QALL:
                    if q == 'vgx':      # gate stress: the larger of |VGS| and |VGD|
                        k = 'vgs' if abs(float(d['vgs'])) >= abs(float(d['vgd'])) else 'vgd'
                        v, x = float(d[k]), d['x_' + k]
                    elif q == 'vgx_held':
                        v, x = max(float(d['vgs_held']), float(d['vgd_held'])), ''
                    elif q.endswith('_held'):
                        v, x = float(d[q]), ''
                    else:
                        v, x = float(d[q]), d['x_' + q]
                    if abs(v) > abs(best[q][0]):
                        best[q] = (v, tag, x)
            res[r['inst']] = best
        return res

    classes = {
        '3.3': lambda i: i['vdd'] == 3.3,
        '3.6': lambda i: i['vdd'] == 3.6,
        '3.3_27C': lambda i: i['vdd'] == 3.3 and i['temp'] == 27,
        '3.6_27C': lambda i: i['vdd'] == 3.6 and i['temp'] == 27,
        '3.0': lambda i: i['vdd'] == 3.0,
        '3.3_dc': lambda i: i['vdd'] == 3.3 and i['kind'] == 'dc',
        '3.6_dc': lambda i: i['vdd'] == 3.6 and i['kind'] == 'dc',
        '3.3_fs': lambda i: i['vdd'] == 3.3 and i['kind'] in ('fs', 'fs0', 'fst'),
        '3.6_fs': lambda i: i['vdd'] == 3.6 and i['kind'] in ('fs', 'fs0', 'fst'),
        '3.3_tran': lambda i: i['vdd'] == 3.3 and i['kind'] in TRAN,
        '3.6_tran': lambda i: i['vdd'] == 3.6 and i['kind'] in TRAN,
    }
    M = {k: devmax(f) for k, f in classes.items()}

    # --- per-device CSV (all devices, 3.3 V and 3.6 V classes)
    with open(OUT / 'csv' / 'device_max.csv', 'w', newline='') as f:
        f.write(SPDX)
        f.write('# IHP sg13cmos5l simulation (ngspice-47, analyze.py): per MOS instance, max |V| over all runs of a '
                'supply class (3.3 / 3.6 V): signed value at the max, run tag, sweep value [V] or time [s]; *_held = '
                'largest |value| held for at least 100 ns (transients; DC points count as held), max of |VGS| and |VGD| '
                'for vgx_held; electrical source = lower (NMOS) / higher (PMOS) of the two diffusion terminals\n')
        w = csv.writer(f)
        hdr = ['inst', 'block', 'type', 'W_um', 'L_um', 'nf', 'meets_spec_LG', 'drain_eq_source', 'd', 'g', 's', 'b']
        for k in ('3.3', '3.6'):
            for q in ('vgs', 'vgd', 'vds', 'vgb'):
                hdr += [f'{q}_{k}', f'run_{q}_{k}', f'x_{q}_{k}']
            hdr += [f'vgx_held_{k}', f'run_vgx_held_{k}', f'vds_held_{k}', f'run_vds_held_{k}']
        w.writerow(hdr)
        for r in topo:
            row = [r['name'], r['block'], r['type'], r['W'], r['L'], r['NF'], int(r['spec_L']), int(r['cap']),
                   r['d'], r['g'], r['s'], r['b']]
            for k in ('3.3', '3.6'):
                for q in ('vgs', 'vgd', 'vds', 'vgb'):
                    v, tag, x = M[k][r['inst']][q]
                    row += [f'{v:.4f}', tag, x]
                for q in ('vgx_held', 'vds_held'):
                    v, tag, x = M[k][r['inst']][q]
                    row += [f'{v:.4f}', tag]
            w.writerow(row)

    lines = []
    lines.append('## Runs\n')
    kinds = defaultdict(list)
    for tag, i in runs.items():
        kinds[(i['kind'], i['var'])].append(i)
    rr = []
    for (k, var), lst in sorted(kinds.items()):
        aids = sorted(set(i['aid'] for i in lst))
        pv = sorted(set(f"{i['vdd']}" for i in lst))
        rr.append([f'{k} {var}'.strip(), KIND_TXT.get(k, k), len(lst), ', '.join(pv), ', '.join(aids)])
    lines.append(md_table(['job', 'what', 'runs ok', 'supply [V]', 'solver aid'], rr))
    lines.append(f'\nFailed runs (no result): {len(fails)}\n')
    if fails:
        lines.append(md_table(['run', 'last solver message'], [[t, m] for t, m in fails]))
    with open(OUT / 'csv' / 'runs.csv', 'w', newline='') as f:
        f.write(SPDX)
        w = csv.writer(f)
        w.writerow(['tag', 'kind', 'variant', 'mos', 'temp_C', 'vdd_V', 'status', 'aid', 'points'])
        for tag, i in sorted(runs.items()):
            w.writerow([tag, i['kind'], i['var'], i['mos'], i['temp'], i['vdd'], 'ok', i['aid'], i['npts']])
        for tag, m in fails:
            i = parse_tag(tag)
            w.writerow([tag, i['kind'], i['var'], i['mos'], i['temp'], i['vdd'], 'FAILED: ' + m, '', ''])

    groups = defaultdict(list)
    for r in topo:
        groups[(r['type'], r['L'])].append(r)

    def nm(r):
        return r['name'].replace('n.', '', 1)

    def gx(k, r, held=False):
        return abs(M[k][r['inst']]['vgx_held' if held else 'vgx'][0])

    summ = []
    for k in ('3.3', '3.6'):
        lines.append(f'\n## Maximum per device type and gate length, {CLASS_TXT[k]}\n')
        rows = []
        for (typ, L), lst in sorted(groups.items()):
            blocks = sorted(set(r['block'] for r in lst))
            row = [typ, f'{L:g}', 'yes' if lst[0]['spec_L'] else 'no', len(lst), ', '.join(blocks)]
            for q in ('vgs', 'vgd', 'vds'):
                best = max(lst, key=lambda r: abs(M[k][r['inst']][q][0]))
                v, tag, x = M[k][best['inst']][q]
                row.append(f'{abs(v):.3f}')
                if q in ('vgs', 'vds'):
                    row.append(f"{nm(best)} ({cond_txt(tag, x, q)})" if tag else '')
            row.append(f"{max(gx(k, r, True) for r in lst):.3f}")
            row.append(f"{max(abs(M[k][r['inst']]['vds_held'][0]) for r in lst):.3f}")
            row.append(f"{max(abs(M[k][r['inst']]['vgb'][0]) for r in lst):.3f}")
            nv = sum(1 for r in lst if gx(k, r) > VFLAG)
            nh = sum(1 for r in lst if gx(k, r, True) > VFLAG)
            n27 = sum(1 for r in lst if gx(k + '_27C', r) > VFLAG)
            row += [nv, nh, n27]
            rows.append(row)
            summ.append([k, typ, L, int(lst[0]['spec_L']), len(lst)] + row[5:])
        lines.append(md_table(['type', 'L [um]', 'L meets spec LG', 'devices', 'blocks', 'max |VGS| [V]',
                               'where (|VGS|)', 'max |VGD| [V]', 'max |VDS| [V]', 'where (|VDS|)',
                               'max of |VGS|, |VGD| held >= 100 ns [V]', 'max |VDS| held >= 100 ns [V]',
                               'max |VGB| [V]', 'devices with |VGS| or |VGD| > 3.301 V', 'same, held >= 100 ns',
                               'same (peak), 27 C runs only'], rows))
    with open(OUT / 'csv' / 'type_length_max.csv', 'w', newline='') as f:
        f.write(SPDX)
        w = csv.writer(f)
        w.writerow(['supply_V', 'type', 'L_um', 'meets_spec_LG', 'devices', 'max_abs_vgs_V', 'where_vgs',
                    'max_abs_vgd_V', 'max_abs_vds_V', 'where_vds', 'max_abs_vgx_held_V', 'max_abs_vds_held_V',
                    'max_abs_vgb_V', 'n_vgx_gt_3v3', 'n_vgx_held_gt_3v3', 'n_vgx_gt_3v3_27C'])
        w.writerows(summ)

    # --- flags: devices with |VGS| or |VGD| > 3.3 V, by spec-L class and run class
    lines.append('\n## Devices with |VGS| or |VGD| above 3.301 V, by run class and gate-length class\n')
    rows, flagrows = [], []
    for k in ('3.0', '3.3', '3.3_27C', '3.3_dc', '3.3_fs', '3.3_tran', '3.6', '3.6_27C', '3.6_dc', '3.6_fs',
              '3.6_tran'):
        for spec in (True, False):
            sel = [r for r in topo if r['spec_L'] == spec]
            over = [r for r in sel if gx(k, r) > VFLAG]
            overh = [r for r in sel if gx(k, r, True) > VFLAG]
            ov_gs = [r for r in sel if abs(M[k][r['inst']]['vgs'][0]) > VFLAG]
            mx = max((gx(k, r) for r in sel), default=0)
            mh = max((gx(k, r, True) for r in sel), default=0)
            blocks = defaultdict(int)
            for r in over:
                blocks[r['block']] += 1
            nruns = sum(1 for i in runs.values() if classes[k](i))
            rows.append([CLASS_TXT[k], nruns, 'L >= spec LG' if spec else 'L below spec LG (0.45 um)', len(sel),
                         len(ov_gs), len(over), len(overh), f'{mx:.3f}', f'{mh:.3f}',
                         ', '.join(f'{b} {n}' for b, n in sorted(blocks.items()))])
            for r in (over if k in ('3.3', '3.6', '3.3_dc', '3.6_dc') else []):   # csv: the main classes only
                v1, t1, x1 = M[k][r['inst']]['vgs']
                v2, t2, x2 = M[k][r['inst']]['vgd']
                flagrows.append([k, nm(r), r['block'], r['type'], r['W'], r['L'], int(spec), f'{v1:.4f}', t1, x1,
                                 f'{v2:.4f}', t2, x2, f'{gx(k, r, True):.4f}'])
    lines.append(md_table(['runs', 'number of runs', 'gate-length class', 'devices', '|VGS| > 3.301 V',
                           '|VGS| or |VGD| > 3.301 V', 'same, held >= 100 ns', 'max of |VGS|, |VGD| [V]',
                           'same, held >= 100 ns [V]', 'by block (|VGS| or |VGD| > 3.301 V)'], rows))
    with open(OUT / 'csv' / 'flags_over_3v3.csv', 'w', newline='') as f:
        f.write(SPDX)
        w = csv.writer(f)
        w.writerow(['runs', 'inst', 'block', 'type', 'W_um', 'L_um', 'meets_spec_LG', 'vgs_V', 'run_vgs', 'x_vgs',
                    'vgd_V', 'run_vgd', 'x_vgd', 'vgx_held_V'])
        w.writerows(flagrows)

    # --- distribution of the per-device gate stress over bins
    edges = [-1, VFLAG, 3.35, 3.5, 3.6, 3.65, 3.8, 4.0, 5.0, 99]
    binlab = ['<= 3.301', '3.301 ... 3.35', '3.35 ... 3.5', '3.5 ... 3.6', '3.6 ... 3.65', '3.65 ... 3.8', '3.8 ... 4.0',
              '4.0 ... 5.0', '> 5.0']
    lines.append('\n## Number of devices per bin of their max(|VGS|, |VGD|) [V], peak and held >= 100 ns\n')
    rows, bcsv = [], []
    for k in ('3.3', '3.3_dc', '3.3_tran', '3.6', '3.6_dc', '3.6_tran'):
        for spec in (True, False):
            for held in (False, True):
                y = np.array([gx(k, r, held) for r in topo if r['spec_L'] == spec])
                cnt = [int(((y > a) & (y <= b)).sum()) for a, b in zip(edges[:-1], edges[1:])]
                rows.append([CLASS_TXT[k], 'L >= spec LG' if spec else 'L = 0.45 um', 'held' if held else 'peak']
                            + cnt)
                bcsv.append([k, int(spec), int(held)] + cnt)
    lines.append(md_table(['runs', 'gate-length class', 'value'] + binlab, rows))
    lines.append('\nBins are half-open (lower, upper]. The first bin ends at 3.301 V: a device counts as above 3.3 V '
                 'when it exceeds it by more than 1 mV (at a 3.3 V supply, VGS = supply comes out a few uV above '
                 '3.3 V at some points).')
    with open(OUT / 'csv' / 'gate_stress_bins.csv', 'w', newline='') as f:
        f.write(SPDX)
        w = csv.writer(f)
        w.writerow(['runs', 'meets_spec_LG', 'held_100ns'] + [f'bin_{a:g}_{b:g}V' for a, b in
                                                              zip([0] + edges[1:-1], edges[1:])])
        w.writerows(bcsv)

    # --- devices meeting the spec LG with |VGS| or |VGD| > 3.3 V: list them
    for k in ('3.3', '3.6'):
        sel = sorted([r for r in topo if r['spec_L'] and gx(k, r) > VFLAG], key=lambda r: -gx(k, r))
        lines.append(f'\n### Devices with L meeting the spec LG and |VGS| or |VGD| > 3.301 V, {CLASS_TXT[k]}: '
                     f'{len(sel)}\n')
        if sel:
            rows = []
            for r in sel:
                v1, t1, x1 = M[k][r['inst']]['vgs']
                v2, t2, x2 = M[k][r['inst']]['vgd']
                rows.append([nm(r), r['block'], r['type'], f"{r['W']:g}/{r['L']:g}", 'yes' if r['cap'] else 'no',
                             f'{abs(v1):.3f}', cond_txt(t1, x1, 'vgs'), f'{abs(v2):.3f}', cond_txt(t2, x2, 'vgd'),
                             f'{gx(k, r, True):.3f}', f"{abs(M[k][r['inst']]['vds'][0]):.3f}",
                             f"g {r['g']}, s {r['s']}, d {r['d']}"])
            lines.append(md_table(['device', 'block', 'type', 'W/L [um]', 'd = s (capacitor)', '|VGS| [V]',
                                   'where', '|VGD| [V]', 'where', 'max of |VGS|, |VGD| held >= 100 ns [V]',
                                   'max |VDS| [V]', 'nodes'], rows))

    # --- BVDSS
    lines.append('\n## |VDS| against the breakdown voltage\n')
    rows = []
    for k in ('3.0', '3.3', '3.6'):
        for typ, dev in (('HV-NMOS', 'sg13_hv_nmos'), ('HV-PMOS', 'sg13_hv_pmos')):
            sel = [r for r in topo if r['dev'] == dev]
            for held in (False, True):
                q = 'vds_held' if held else 'vds'
                best = max(sel, key=lambda r: abs(M[k][r['inst']][q][0]))
                v, tag, x = M[k][best['inst']][q]
                rows.append([CLASS_TXT[k], typ, 'held >= 100 ns' if held else 'peak', f'{abs(v):.3f}',
                             f"{nm(best)} ({best['block']}, {best['W']:g}/{best['L']:g})",
                             cond_txt(tag, x, 'vds') if not held else cond_txt(tag, 0, 'vds').rsplit(',', 1)[0],
                             f'{BVDSS[dev]:.1f}', f'{BVDSS[dev] - abs(v):.3f}'])
    lines.append(md_table(['runs', 'type', 'value', 'max |VDS| [V]', 'device (block, W/L um)', 'where',
                           'spec |BVDSS| min [V]', 'margin [V]'], rows))

    # --- top 20 (3.6 V: held and peak values; 3.3 V: held values)
    for sup, q, lab in (('3.6', 'vgx_held', 'max of |VGS|, |VGD| held >= 100 ns'),
                        ('3.6', 'vds_held', '|VDS| held >= 100 ns'),
                        ('3.6', 'vgx', 'max of |VGS|, |VGD| (peak)'), ('3.6', 'vgs', '|VGS| (peak)'),
                        ('3.6', 'vds', '|VDS| (peak)'), ('3.6', 'vgb', '|VGB| (peak)'),
                        ('3.3', 'vgx_held', 'max of |VGS|, |VGD| held >= 100 ns'),
                        ('3.3', 'vds_held', '|VDS| held >= 100 ns')):
        oth = '3.3' if sup == '3.6' else '3.6'
        lines.append(f'\n## Top 20 devices by {lab}, all {sup} V runs\n')
        srt = sorted(topo, key=lambda r: -abs(M[sup][r['inst']][q][0]))[:20]
        rows = []
        for i, r in enumerate(srt, 1):
            v, tag, x = M[sup][r['inst']][q]
            hq = {'vgx': 'vgx_held', 'vgs': 'vgs_held', 'vds': 'vds_held', 'vgx_held': 'vgx_held',
                  'vds_held': 'vds_held'}.get(q)
            vh = f"{abs(M[sup][r['inst']][hq][0]):.3f}" if hq else ''
            vdc = abs(M[sup + '_dc'][r['inst']][q][0])
            rows.append([i, nm(r), r['block'], r['type'], f"{r['W']:g}/{r['L']:g}", 'yes' if r['spec_L'] else 'no',
                         f'{abs(v):.3f}', cond_txt(tag, x, q), vh, f'{vdc:.3f}',
                         f"{abs(M[sup + '_27C'][r['inst']][q][0]):.3f}", f"{abs(M[oth][r['inst']][q][0]):.3f}"])
        lines.append(md_table(['#', 'device', 'block', 'type', 'W/L [um]', 'L meets spec LG', f'{lab} [V]',
                               'where', 'held >= 100 ns [V]', 'DC enabled only [V]', '27 C runs only [V]',
                               f'all {oth} V runs [V]'], rows))
        with open(OUT / 'csv' / f'top20_{q}_{sup.replace(".", "v")}.csv', 'w', newline='') as f:
            f.write(SPDX)
            w = csv.writer(f)
            w.writerow(['rank', 'inst', 'block', 'type', 'W_um', 'L_um', 'meets_spec_LG', f'abs_{q}_V', 'where',
                        'held_100ns_V', 'dc_enabled_V', 'runs_27C_V', f'runs_{oth.replace(".", "v")}_V'])
            for row in rows:
                w.writerow(row[:4] + row[4].split('/') + row[5:])

    # --- per run class: overall maxima by kind (which condition dominates)
    lines.append('\n## Largest |VGS|, |VGD|, |VDS| per job kind (over all devices and runs of the kind)\n')
    rows = []
    for (k, var), lst in sorted(kinds.items()):
        for vdd in sorted(set(i['vdd'] for i in lst)):
            sub = [i for i in lst if i['vdd'] == vdd]
            row = [f'{k} {var}'.strip(), vdd, len(sub)]
            for q in ('vgs', 'vgd', 'vds'):
                best = (0, None, None, None)
                for i in sub:
                    tag = next(t for t, j in runs.items() if j is i)
                    for inst, d in i['dev'].items():
                        v = abs(float(d[q]))
                        if v > best[0]:
                            best = (v, inst, tag, d['x_' + q])
                row.append(f'{best[0]:.3f}')
                if q != 'vgd':
                    r = nodeinfo[best[1]]
                    row.append(f"{r['name'].replace('n.', '', 1)} {r['W']:g}/{r['L']:g} "
                               f"({cond_txt(best[2], best[3], q)})")
            rows.append(row)
    lines.append(md_table(['job', 'supply [V]', 'runs', 'max |VGS| [V]', 'device, where', 'max |VGD| [V]',
                           'max |VDS| [V]', 'device, where'], rows))

    # --- node overshoot in transients: highest node above the supply, lowest below 0
    lines.append('\n## Node extremes (transients and DC): highest node voltage and lowest node voltage per job kind\n')
    rows = []
    ncsv = []
    for (k, var), lst in sorted(kinds.items()):
        for vdd in sorted(set(i['vdd'] for i in lst)):
            hi, lo = (-9, None, None), (9, None, None)
            for tag, i in runs.items():
                if i['kind'] != k or i['var'] != var or i['vdd'] != vdd:
                    continue
                with gzip.open(WORK / 'nodes' / f'{tag}.csv.gz', 'rt') as fh:
                    fh.readline()
                    for r in csv.DictReader(fh):
                        nm = r['node']
                        if nm in ('v(v-sweep)', 'time') or nm.startswith('v(padin_s') or nm.startswith(
                                'v(padout_s') or nm.startswith('v(b0s') or nm.startswith('v(b1s') or \
                                nm.startswith('v(b2s') or nm.startswith('v(b3s') or nm in ('v(cf)', 'v(cx)'):
                            continue
                        if float(r['vmax']) > hi[0]:
                            hi = (float(r['vmax']), nm, cond_txt(tag, r['x_vmax'], ''))
                        if float(r['vmin']) < lo[0]:
                            lo = (float(r['vmin']), nm, cond_txt(tag, r['x_vmin'], ''))
            rows.append([f'{k} {var}'.strip(), vdd, f'{hi[0]:.3f}', f'{hi[1]} ({hi[2]})', f'{lo[0]:.3f}',
                         f'{lo[1]} ({lo[2]})'])
            ncsv.append([f'{k} {var}'.strip(), vdd, f'{hi[0]:.4f}', hi[1], hi[2], f'{lo[0]:.4f}', lo[1], lo[2]])
    lines.append(md_table(['job', 'supply [V]', 'highest node [V]', 'node (where)', 'lowest node [V]',
                           'node (where)'], rows))
    with open(OUT / 'csv' / 'node_extremes.csv', 'w', newline='') as f:
        f.write(SPDX)
        w = csv.writer(f)
        w.writerow(['job', 'supply_V', 'vmax_V', 'node_vmax', 'where_vmax', 'vmin_V', 'node_vmin', 'where_vmin'])
        w.writerows(ncsv)

    (OUT / 'tables.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: '
                                   'Apache-2.0\n-->\n# Generated tables (analyze.py)\n\n' + '\n'.join(lines) + '\n')

    # --- plots: ranked per-device max |VGS| and |VDS| at 3.6 V (and 3.3 V for reference)
    col = {True: '#2a6fdb', False: '#e8743b'}
    fig, axs = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
    for ax, q, lab in ((axs[0], 'vgx', 'max(|VGS|, |VGD|)'), (axs[1], 'vds', '|VDS|')):
        srt = sorted(topo, key=lambda r: -abs(M['3.6'][r['inst']][q][0]))
        y = [abs(M['3.6'][r['inst']][q][0]) for r in srt]
        y3 = [abs(M['3.3'][r['inst']][q][0]) for r in srt]
        yh = [abs(M['3.6'][r['inst']][q + '_held'][0]) for r in srt]
        c = [col[r['spec_L']] for r in srt]
        ax.bar(range(len(srt)), y, width=1.0, color=c, linewidth=0)
        ax.plot(range(len(srt)), yh, '_', ms=5, mew=1.5, color='#6a3d9a', label='same device, 3.6 V, held >= 100 ns')
        ax.plot(range(len(srt)), y3, '.', ms=2, color='#222222', label='same device, max over the 3.3 V runs')
        ax.axhline(VLIM, color='#b00020', lw=1, ls='--')
        ax.text(len(srt) * 0.99, VLIM + 0.05, 'spec VGS max 3.3 V (27 C, LG condition)' if q == 'vgx' else '3.3 V',
                ha='right', va='bottom', fontsize=8, color='#b00020')
        if q == 'vds':
            ax.axhline(5.3, color='#555555', lw=1, ls=':')
            ax.text(len(srt) * 0.99, 5.35, 'spec |BVDSS| min 5.3 V (HV-NMOS / HV-PMOS)', ha='right', va='bottom',
                    fontsize=8, color='#555555')
        ax.set_ylim(0, max(5.8, max(y) * 1.05))
        ax.set_ylabel(f'max {lab} [V]')
        ax.grid(axis='y', alpha=0.3)
        ax.set_title(f'per-device max {lab} over all 3.6 V runs, ranked ({len(srt)} MOS devices)', fontsize=10)
    from matplotlib.patches import Patch
    axs[0].legend(handles=[Patch(color=col[True], label='L meets spec LG (NMOS >= 0.6 um, PMOS >= 0.5 um)'),
                           Patch(color=col[False], label='L below spec LG (0.45 um)'),
                           axs[0].lines[0], axs[0].lines[1]], fontsize=8, loc='upper right')
    axs[1].set_xlabel('device rank')
    fig.suptitle('Slot 7 + both custom pads, IHP sg13cmos5l simulation (ngspice-47, pads KLayout-extracted)',
                 fontsize=10)
    fig.tight_layout()
    save_png(fig, OUT / 'plots' / 'ranked_vgs_vds_3v6.png')
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    for ax, q, lab in ((axs[0], 'vgx', 'max(|VGS|, |VGD|)'), (axs[1], 'vds', '|VDS|')):
        top_v = max(abs(M['3.6'][r['inst']][q][0]) for r in topo)
        bins = np.arange(0, top_v + 0.1, 0.1)
        for spec in (True, False):
            y = [abs(M['3.6'][r['inst']][q][0]) for r in topo if r['spec_L'] == spec]
            ax.hist(y, bins=bins, color=col[spec], alpha=0.75,
                    label=('L meets spec LG' if spec else 'L = 0.45 um (below spec LG)') + f', {len(y)} devices')
        ax.axvline(VLIM, color='#b00020', lw=1, ls='--')
        ax.set_xlabel(f'per-device max {lab} over the 3.6 V runs [V]')
        ax.set_ylabel('devices')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.suptitle('Histogram of per-device maxima at 3.6 V (IHP sg13cmos5l simulation)', fontsize=10)
    fig.tight_layout()
    save_png(fig, OUT / 'plots' / 'hist_vgs_vds_3v6.png')
    plt.close(fig)
    print('analyze: runs', len(runs), 'failed', len(fails))


if __name__ == '__main__':
    main()
