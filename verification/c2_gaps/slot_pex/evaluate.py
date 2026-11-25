#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Evaluate the sim.py runs (IHP sg13cmos5l simulation, slot 7 with the slot extracted from final/gds/slot_7.gds).

Usage: python3 -I evaluate.py <work_dir> <dest_dir>
Reads <work_dir>/out/<view>_<mos>_<temp>_<vdd>_<analysis>[_<load>].<suffix>; writes <dest_dir>/csv/*_summary.csv,
<dest_dir>/csv/compare.csv, <dest_dir>/tables.md and <dest_dir>/plots/*.png.

Definitions (the same as the earlier folders, so the numbers compare):
  dc    (../dc_curves/rt.py) expected = v(vcm_s2d) + pad in - v(vref_s2d); err = pad out - expected; max |err| over
        pad in 0 ... 1 V; gain / offset = small-signal line from pad in = vref_s2d +- 0.1 V; 1 mV range = contiguous pad
        in range around vref_s2d with |pad out - small-signal line| < 1 mV
  ac    (../ac_tran/rt.py) gain at 1 kHz; f-3dB = first frequency above 1 kHz where the gain falls 3 dB below it;
        peaking = maximum above the 1 kHz gain; phase at f-3dB
  step  (../ac_tran/rt.py) settling to 1 % / 0.1 % of the step after the input edge start (2 us rise, 7 us fall),
        overshoot in % of the step, step gain = rise step / 0.5 V
  op    vcm = v(vcm_s2d), vref = v(vref_s2d) at pad in 0.5 V; I_slot = -i(Vslot), I_ring = -i(Vio) (enabled, and with
        enable 0 V: DC operating point, not the transient window of the designer's data sheet)
  pu    enable at 20 us: t_vcm98 / t_vref98 = last time v(vcm_s2d) / v(vref_s2d) cross 98 % of their value at 39.9 us,
        minus 20 us; t_out1mV = last time |pad out - its value at 39.9 us| > 1 mV, minus 20 us; currents at the
        end (*_end_*: pu 39.9 us, en 19.9 us);
        peak I_ring during the supply ramp (0 ... 20 us) and after enable (20 ... 40 us)
  mode  max |pad out - expected| over pad in 0 ... 1 V (feed: the op), expected as the designer's run_modes.py
"""
import csv
import importlib.util
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('dc_common', HERE.parent / 'dc_curves' / 'common.py')
DC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DC)
plt = DC.plt

PTS = [('tt', 27, 3.3), ('ss', -40, 3.0), ('ff', 125, 3.6), ('fs', 125, 3.6), ('sf', -40, 3.0)]
VIEWS = ['prev', 'c', 'cc', 'rc', 'cs', 'ps', 'hyb']
VNAME = {'prev': 'previous deck (schematic / KLayout blocks, pads sak-pex C)',
         'c': 'slot magic C, pads as previous', 'cc': 'slot magic C, pads magic C with substrate C',
         'rc': 'slot + pads magic full-RC', 'cs': 'c with SPARSE solver', 'ps': 'prev with SPARSE solver',
         'hyb': 'prev with pad_ref_rb magic C'}
VCOL = {'prev': '#52514e', 'c': '#2a78d6', 'cc': '#1baf7a', 'rc': '#eb6834', 'cs': '#e87ba4', 'ps': '#8a8984', 'hyb': '#eda100'}
VLS = {'prev': '-', 'c': '--', 'cc': '-.', 'rc': ':', 'cs': '-', 'ps': '-', 'hyb': '-'}
LOADS = ['open', '10p', '100p']
LN = {'open': 'unloaded', '10p': '1 kΩ ∥ 10 pF', '100p': '1 kΩ ∥ 100 pF'}
SPDX = '# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
LABEL = 'IHP sg13cmos5l simulation, slot 7 default mode, round trip pad_s2d → pad_d2s'


def rd(p):
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        return None
    with open(p) as f:
        head = f.readline().split()
    a = np.loadtxt(p, skiprows=1, ndmin=2)
    return {h: a[:, i] for i, h in enumerate(head)} if a.size else None


def tag(view, pt, ana, load=None):
    c, t, v = pt
    return f'{view}_{c}_{t}_{v}_{ana}' + (f'_{load}' if load else '')


def ok(work, view, pt, ana, load=None):
    p = Path(work) / 'out' / (tag(view, pt, ana, load) + '.log')
    if not p.exists():
        return False
    x = p.read_text()
    if '=== attempt' in x:  # sim.py with retries: the final verdict is the last line
        return 'SLOTDONE (final attempt ok)' in x
    return 'SLOTDONE' in x and 'aborted' not in x


def logx(f, y, f0):
    return float(np.interp(np.log10(f0), np.log10(f), y))


def first_fall(f, y, lev, i0):
    for i in range(i0, len(f) - 1):
        if y[i] >= lev > y[i + 1]:
            return 10 ** (np.log10(f[i]) + (lev - y[i]) * (np.log10(f[i + 1]) - np.log10(f[i])) / (y[i + 1] - y[i]))
    return float('nan')


def last_cross(t, y, lev, t0=0.0, t1=np.inf):
    m = (t >= t0) & (t <= t1)
    t, y = t[m], y[m]
    s = np.sign(y - lev)
    idx = np.where(s[:-1] * s[1:] < 0)[0]
    if not len(idx):
        return float('nan')
    i = idx[-1]
    return t[i] + (lev - y[i]) * (t[i + 1] - t[i]) / (y[i + 1] - y[i])


def m_op(d, doff):
    r = dict(vcm_V=d['v(vcm_s2d)'][0], vref_V=d['v(vref_s2d)'][0], vref_d2s_V=d['v(vref_d2s)'][0],
             s2d_out_cm_V=(d['v(outp)'][0] + d['v(outn)'][0]) / 2, I_slot_uA=-d['i(vslot)'][0] * 1e6,
             I_ring_uA=-d['i(vio)'][0] * 1e6)
    if doff:
        r.update(I_slot_off_nA=-doff['i(vslot)'][0] * 1e9, I_ring_off_nA=-doff['i(vio)'][0] * 1e9)
    return r


def m_dc(d):
    x, y = d['v(padin)'], d['v(padout)']
    vref = float(np.interp(0.5, x, d['v(vref_s2d)']))
    vcm = float(np.interp(0.5, x, d['v(vcm_s2d)']))
    err = y - (d['v(vcm_s2d)'] + x - d['v(vref_s2d)'])
    G, y0 = DC.ss_line(x, y, x0=vref)
    ess = y - y0 - G * (x - vref)
    lo, hi, _, _ = DC.contiguous_range(x, ess, 1e-3, x0=vref)
    sel = (x >= 0) & (x <= 1.0 + 1e-9)
    return dict(gain=G, offset_mV=(y0 - vcm) * 1e3, max_abs_err_0to1V_mV=float(np.abs(err[sel]).max()) * 1e3,
                in_lo_1mV_V=lo, in_hi_1mV_V=hi), dict(x=x, err=err)


def m_ac(d):
    f, g = d['frequency'], d['g_db']
    g1k = logx(f, g, 1e3)
    i0 = int(np.searchsorted(f, 1e3))
    f3 = first_fall(f, g - g1k, -3.0, i0)
    return dict(G_1k_dB=g1k, f3dB_MHz=f3 / 1e6, peak_dB=float((g - g1k)[i0:].max()), ph_f3dB_deg=logx(f, d['g_ph'], f3))


def m_step(d):
    t, o = d['time'], d['v(padout)']
    r = {}
    for e, (t0, t1) in (('rise', (2e-6, 7e-6)), ('fall', (7e-6, 12e-6))):
        vi, vf = np.interp([t0 - 0.01e-6, t1 - 0.1e-6], t, o)
        st = vf - vi
        for p in (1.0, 0.1):
            r[f'ts{p:g}_{e}_ns'] = (last_cross(t, np.abs(o - vf), p / 100 * abs(st), t0, t1 - 0.1e-6) - t0) * 1e9
        m = (t >= t0) & (t <= t1)
        r[f'overshoot_{e}_pct'] = 100 * float(((o - vi) / st)[m].max() - 1)
        if e == 'rise':
            r['step_gain'] = st / 0.5
    return r


def m_pu(d, ten=20e-6, tend=39.9e-6):
    t = d['time']
    i = int(np.searchsorted(t, tend))
    r = {}
    for k, n in (('vcm', 'v(vcm_s2d)'), ('vref', 'v(vref_s2d)')):
        fin = d[n][i]
        r[f'{k}_end_V'] = fin
        r[f't_{k}98_us'] = (last_cross(t, d[n], 0.98 * fin, ten, tend) - ten) * 1e6
    o = d['v(padout)']
    r['padout_end_V'] = o[i]
    r['t_out1mV_us'] = (last_cross(t, np.abs(o - o[i]), 1e-3, ten, tend) - ten) * 1e6
    ir = -d['i(vio)'] * 1e6
    r['I_slot_end_uA'] = -d['i(vslot)'][i] * 1e6
    r['I_ring_end_uA'] = ir[i]
    if ten > 10e-6:
        r['I_ring_peak_ramp_uA'] = float(ir[t < ten].max())
    r['I_ring_peak_enable_uA'] = float(ir[(t >= ten) & (t <= tend)].max())
    r['I_ring_before_enable_nA'] = float(ir[t < ten - 0.1e-6][-1]) * 1e3
    return r


def m_mode(d):
    e = np.abs(d['v(padout)'] - d['ex'])
    return dict(err_max_mV=float(e.max()) * 1e3)


def committed():
    """earlier slot results (committed CSVs of ../dc_curves and ../ac_tran), view 'pex' (magic PEX pads) and
    'schematic', keyed (view, pt, quantity[, load])"""
    out = {}

    def rows(p):
        with open(p) as f:
            return list(csv.DictReader(l for l in f if not l.startswith('#')))
    for r in rows(HERE.parent / 'dc_curves' / 'csv' / 'rt_summary.csv'):
        pt = (r['corner_mos'], int(r['temp']), float(r['vdd']))
        for q, k in (('gain', 'gain'), ('offset_mV', 'offset_mV'), ('max_abs_err_0to1V_mV', 'max_abs_err_0to1V_mV'),
                     ('in_lo_1mV_V', 'in_lo_1mV'), ('in_hi_1mV_V', 'in_hi_1mV'), ('vcm_V', 'vcm'),
                     ('vref_V', 'vref_s2d')):
            out[(r['pads'], pt, q, None)] = float(r[k])
    for r in rows(HERE.parent / 'ac_tran' / 'csv' / 'rt_ac_summary.csv'):
        c, t, _, v, _ = r['point'].split()
        pt = (c, int(t), float(v))
        out[(r['view'], pt, 'f3dB_MHz', r['load'])] = float(r['f3dB']) / 1e6
        out[(r['view'], pt, 'G_1k_dB', r['load'])] = float(r['G_1k_dB'])
        out[(r['view'], pt, 'peak_dB', r['load'])] = float(r['Peak_dB'])
    for r in rows(HERE.parent / 'ac_tran' / 'csv' / 'rt_step_summary.csv'):
        c, t, _, v, _ = r['point'].split()
        pt = (c, int(t), float(v))
        for e in ('rise', 'fall'):
            out[(r['view'], pt, f'ts1_{e}_ns', r['load'])] = float(r[f'ts1_{e}']) * 1e9
            out[(r['view'], pt, f'ts0.1_{e}_ns', r['load'])] = float(r[f'ts0.1_{e}']) * 1e9
            out[(r['view'], pt, f'overshoot_{e}_pct', r['load'])] = float(r[f'overshoot_{e}'])
        out[(r['view'], pt, 'step_gain', r['load'])] = float(r['gain_step'])
    return out


def write_csv(path, rows, note):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(path, 'w', newline='') as f:
        f.write(SPDX + f'# {LABEL}; evaluate.py; {note}\n')
        w = csv.DictWriter(f, keys, lineterminator='\n')
        w.writeheader()
        for r in rows:
            w.writerow({k: (f'{v:.6g}' if isinstance(v, float) else v) for k, v in r.items()})


def esc(s):
    return str(s).replace('|', '\\|')


def md(head, rows):
    out = ['| ' + ' | '.join(esc(h) for h in head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(esc(x) for x in r) + ' |' for r in rows]
    return '\n'.join(out)


def fmt(x, q):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return '–'
    if q.endswith('_nA') or q.endswith('_uA'):
        return f'{x:.2f}'
    if q.endswith('_V'):
        return f'{x:.4f}'
    if q in ('gain', 'step_gain'):
        return f'{x:.5f}'
    if q.endswith('_ns'):
        return f'{x:.0f}'
    if q.endswith('_MHz'):
        return f'{x:.3f}'
    return f'{x:.3g}' if abs(x) < 1e3 else f'{x:.0f}'


def chg(a, b, q):
    """change b vs a: absolute for voltages / dB / small mV values, relative otherwise"""
    if a is None or b is None or np.isnan(a) or np.isnan(b):
        return '–'
    if q.endswith('_V') or q.endswith('_mV'):
        return f'{(b - a) * (1e3 if q.endswith("_V") else 1):+.2f} mV'
    if q.endswith('_dB') or q.endswith('_deg') or q.endswith('_pct'):
        return f'{b - a:+.3f}'
    if q in ('gain', 'step_gain'):
        return f'{(b - a) * 1e6:+.0f} ppm'
    return f'{100 * (b - a) / a:+.1f} %' if a else '–'


def main(work, dest):
    work, dest = Path(work), Path(dest)
    (dest / 'csv').mkdir(exist_ok=True)
    (dest / 'plots').mkdir(exist_ok=True)
    DC.style()
    o = work / 'out'
    R = {}  # (view, pt, quantity, load) -> value
    curves = {}
    rows = {k: [] for k in ('op', 'dc', 'ac', 'step', 'pu', 'en', 'opi', 'mode')}
    fails = []
    for view in VIEWS:
        for pt in PTS:
            base = dict(view=view, point=f'{pt[0]} {pt[1]} C {pt[2]} V')
            d = rd(o / (tag(view, pt, 'op') + '.op'))
            if d and ok(work, view, pt, 'op'):
                r = m_op(d, rd(o / (tag(view, pt, 'op') + '.opoff')))
                rows['op'].append({**base, **r})
                R.update({(view, pt, q, None): x for q, x in r.items()})
            for an in ('op', 'dc', 'ac'):
                if (o / (tag(view, pt, an) + '.log')).exists() and not ok(work, view, pt, an):
                    fails.append(tag(view, pt, an))
            d = rd(o / (tag(view, pt, 'dc') + '.dc'))
            if d and ok(work, view, pt, 'dc'):
                r, cv = m_dc(d)
                curves[(view, pt, 'dc')] = cv
                rows['dc'].append({**base, **r})
                R.update({(view, pt, q, None): x for q, x in r.items()})
            for ld in LOADS:
                d = rd(o / (tag(view, pt, 'ac') + f'.ac_{ld}'))
                if d and ok(work, view, pt, 'ac'):
                    r = m_ac(d)
                    curves[(view, pt, 'ac', ld)] = d
                    rows['ac'].append({**base, 'load': ld, **r})
                    R.update({(view, pt, q, ld): x for q, x in r.items()})
                d = rd(o / (tag(view, pt, 'step', ld) + '.step'))
                if d is not None and ok(work, view, pt, 'step', ld):
                    r = m_step(d)
                    curves[(view, pt, 'step', ld)] = d
                    rows['step'].append({**base, 'load': ld, **r})
                    R.update({(view, pt, q, ld): x for q, x in r.items()})
                elif (o / (tag(view, pt, 'step', ld) + '.log')).exists():
                    fails.append(tag(view, pt, 'step', ld))
            d = rd(o / (tag(view, pt, 'pu') + '.pu'))
            if d is not None and ok(work, view, pt, 'pu'):
                r = m_pu(d)
                curves[(view, pt, 'pu')] = d
                rows['pu'].append({**base, **r})
                R.update({(view, pt, q, None): x for q, x in r.items()})
            elif (o / (tag(view, pt, 'pu') + '.log')).exists():
                fails.append(tag(view, pt, 'pu'))
            d = rd(o / (tag(view, pt, 'en') + '.en'))
            if d is not None and ok(work, view, pt, 'en'):
                r = {k + ('' if k.startswith('I_') or k.endswith('_V') else '_en'): x
                     for k, x in m_pu(d, 2e-6, 19.9e-6).items()}
                curves[(view, pt, 'en')] = d
                rows['en'].append({**base, **r})
                R.update({(view, pt, q, 'en'): x for q, x in r.items()})
            elif (o / (tag(view, pt, 'en') + '.log')).exists():
                fails.append(tag(view, pt, 'en'))
            d = rd(o / (tag(view, pt, 'opi') + '.opi'))
            if d is not None and ok(work, view, pt, 'opi'):
                r = dict(I_iref_s2d_uA=d['i(vpi0)'][0] * 1e6, I_iref_d2s_uA=d['i(vpi1)'][0] * 1e6)
                rows['opi'].append({**base, **r})
                R.update({(view, pt, q, None): x for q, x in r.items()})
            for m in ('swap', 'mon', 'feed', 'ext'):
                d = rd(o / (tag(view, pt, f'mode_{m}') + f'.mode_{m}'))
                if d is not None and ok(work, view, pt, f'mode_{m}'):
                    r = m_mode(d)
                    rows['mode'].append({**base, 'mode': m, **r})
                    R[(view, pt, f'mode_{m}_err_max_mV', None)] = r['err_max_mV']
                elif (o / (tag(view, pt, f'mode_{m}') + '.log')).exists():
                    fails.append(tag(view, pt, f'mode_{m}'))
    for k, note in (('op', 'op at pad in 0.5 V; *_off = enable 0 V (DC)'), ('dc', 'pad in -0.3 ... 3.3 V'),
                    ('ac', 'loads open / 1k|10p / 1k|100p'), ('step', '0.25 -> 0.75 -> 0.25 V'),
                    ('pu', 'supply ramp 0 ... 10 us, enable at 20 us; times after enable'),
                    ('en', 'from the disabled op, enable at 2 us; times after enable, values at 19.9 us'),
                    ('opi', 'current from the slot into the pads iref pins (0 V sources), op enabled'),
                    ('mode', 'tt 27 C, designer run_modes.py definitions')):
        write_csv(dest / 'csv' / f'{k}_summary.csv', rows[k], note)
    for pt in PTS:  # the disabled op of prev converges only with SPARSE (view ps)
        for q in ('I_slot_off_nA', 'I_ring_off_nA'):
            if R.get(('prev', pt, q, None)) is None and R.get(('ps', pt, q, None)) is not None:
                R[('prev', pt, q, None)] = R[('ps', pt, q, None)]
    C = committed()
    # comparison table
    Q = [('op', 'vcm_V', None), ('op', 'vref_V', None), ('op', 's2d_out_cm_V', None), ('op', 'I_slot_uA', None),
         ('op', 'I_ring_uA', None), ('op', 'I_slot_off_nA', None), ('op', 'I_ring_off_nA', None),
         ('opi', 'I_iref_s2d_uA', None), ('opi', 'I_iref_d2s_uA', None),
         ('dc', 'max_abs_err_0to1V_mV', None), ('dc', 'gain', None), ('dc', 'offset_mV', None),
         ('dc', 'in_lo_1mV_V', None), ('dc', 'in_hi_1mV_V', None)]
    Q += [('ac', q, ld) for ld in LOADS for q in ('f3dB_MHz', 'G_1k_dB', 'peak_dB')]
    Q += [('step', q, ld) for ld in LOADS for q in ('ts1_rise_ns', 'ts0.1_rise_ns', 'ts1_fall_ns', 'overshoot_rise_pct',
                                                       'step_gain')]
    Q += [('pu', q, None) for q in ('t_vcm98_us', 't_vref98_us', 't_out1mV_us', 'I_ring_end_uA',
                                    'I_ring_peak_ramp_uA', 'I_ring_peak_enable_uA')]
    Q += [('en', q, 'en') for q in ('t_vcm98_us_en', 't_vref98_us_en', 't_out1mV_us_en', 'I_ring_end_uA',
                                    'I_ring_peak_enable_uA', 'I_ring_before_enable_nA')]
    Q += [('mode', f'mode_{m}_err_max_mV', None) for m in ('swap', 'mon', 'feed', 'ext')]
    crow, md_rows = [], []
    for ana, q, ld in Q:
        for pt in PTS:
            vals = {v: R.get((v, pt, q, ld)) for v in VIEWS}
            com = C.get(('pex', pt, q, ld))
            if all(x is None for x in vals.values()):
                continue
            crow.append(dict(analysis=ana, quantity=q, load=ld or '', point=f'{pt[0]} {pt[1]} C {pt[2]} V',
                             committed_pex=com, committed_schematic=C.get(('schematic', pt, q, ld)),
                             **{f'v_{v}': vals[v] for v in VIEWS}))
            md_rows.append([q + (f' ({LN[ld]})' if ld in LN else ''), f'{pt[0]} {pt[1]} °C', fmt(com, q),
                            fmt(vals['prev'], q), fmt(vals['c'], q), chg(vals['prev'], vals['c'], q),
                            fmt(vals['cc'], q), fmt(vals['rc'], q), chg(vals['prev'], vals['rc'], q)])
    write_csv(dest / 'csv' / 'compare.csv', crow, 'committed_* = ../dc_curves, ../ac_tran CSVs; v_<view> = this run')
    with open(dest / 'tables.md', 'w') as f:
        f.write('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n')
        f.write('# Comparison table (generated by evaluate.py)\n\n')
        f.write('Views: ' + '; '.join(f'`{k}` = {v}' for k, v in VNAME.items()) + '. "committed" = the earlier '
                'run of the same deck with the magic PEX pads (`../dc_curves/csv/rt_summary.csv`, '
                '`../ac_tran/csv/rt_*_summary.csv`, view `pex`). Changes: absolute for V / mV / dB / %, ppm for '
                'gains, relative otherwise. "–" = not run or no result.\n\n')
        f.write(md(['quantity', 'PVT', 'committed', 'prev (rerun)', 'c', 'c vs prev', 'cc', 'rc', 'rc vs prev'],
                   md_rows) + '\n')
        if fails:
            f.write('\nRuns without a result (aborted or incomplete): ' + ', '.join(f'`{x}`' for x in fails) + '\n')
    plots(curves, dest)
    print(f'{len(crow)} comparison rows, failed: {fails}')


def plots(cv, dest):
    pc = {('tt', 27, 3.3): '#2a78d6', ('ss', -40, 3.0): '#eb6834', ('ff', 125, 3.6): '#1baf7a',
          ('fs', 125, 3.6): '#e87ba4', ('sf', -40, 3.0): '#eda100'}
    # DC error, all PVT, prev vs c vs rc, and the difference to prev
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 7.0), sharex=True, gridspec_kw=dict(height_ratios=[3, 2]))
    for (view, pt, a), d in [(k, v) for k, v in cv.items() if k[2] == 'dc' and k[0] in ('prev', 'c', 'cc', 'rc')]:
        s_ = (d['x'] >= -0.05) & (d['x'] <= 1.05)
        if view != 'cc':
            axs[0].plot(d['x'][s_], d['err'][s_] * 1e3, color=pc[pt], ls=VLS[view], lw=1.1)
        p = cv.get(('prev', pt, 'dc'))
        if view != 'prev' and p is not None:
            axs[1].plot(d['x'][s_], (d['err'][s_] - np.interp(d['x'][s_], p['x'], p['err'])) * 1e3, color=pc[pt],
                        ls=VLS[view], lw=1.1)
    h = [plt.Line2D([], [], color=pc[p], label='%s %d °C %.1f V' % p) for p in PTS]
    h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label=VNAME[v]) for v in ('prev', 'c', 'cc', 'rc')]
    axs[0].legend(handles=h, loc='lower left', ncol=2, fontsize=6.3)
    axs[1].set_xlabel('S2D pad input (pad in) [V]')
    axs[0].set_ylabel('pad out − (vcm + pad in − vref) [mV]')
    axs[1].set_ylabel('error − error of the\nprevious deck [mV]')
    axs[0].set_xlim(-0.05, 1.05)
    axs[0].set_title(f'{LABEL}\nDC error vs expected (replica vcm / vref as simulated), pad out unloaded (1 GΩ); '
                     'cc only in the lower panel', fontsize=8.5)
    fig.tight_layout()
    DC.save(fig, str(dest / 'plots' / 'dc_error'), svg=False)
    # Bode tt, three loads, with the difference to prev
    fig, axs = plt.subplots(3, 1, figsize=(7.4, 7.6), sharex=True, gridspec_kw=dict(height_ratios=[3, 2, 3]))
    lc = {'open': '#2a78d6', '10p': '#1baf7a', '100p': '#eb6834'}
    for (view, pt, a, ld), d in [(k, v) for k, v in cv.items() if k[2] == 'ac' and k[1] == PTS[0]
                                 and k[0] in ('prev', 'c', 'cc', 'rc')]:
        axs[0].semilogx(d['frequency'], d['g_db'], color=lc[ld], ls=VLS[view], lw=1.1)
        axs[2].semilogx(d['frequency'], d['g_ph'], color=lc[ld], ls=VLS[view], lw=1.1)
        p = cv.get(('prev', pt, 'ac', ld))
        if view != 'prev' and p is not None:
            axs[1].semilogx(d['frequency'], d['g_db'] - np.interp(d['frequency'], p['frequency'], p['g_db']),
                            color=lc[ld], ls=VLS[view], lw=1.1)
    axs[0].set_ylim(-30, 3)
    axs[1].set_ylim(-1.5, 0.5)
    axs[2].set_ylim(-270, 10)
    axs[0].set_xlim(1e4, 1e8)
    axs[0].set_ylabel('pad_d2s / pad_s2d [dB]')
    axs[1].set_ylabel('difference to\nprevious deck [dB]')
    axs[2].set_ylabel('phase [°]')
    axs[2].set_xlabel('frequency [Hz]')
    h = [plt.Line2D([], [], color=lc[l], label=LN[l]) for l in LOADS]
    h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label=VNAME[v]) for v in ('prev', 'c', 'cc', 'rc')]
    axs[0].legend(handles=h, loc='lower left', fontsize=6.5)
    axs[0].set_title(f'{LABEL}\nAC, tt 27 °C 3.3 V, pad in 0.5 V DC', fontsize=8.5)
    fig.tight_layout()
    DC.save(fig, str(dest / 'plots' / 'bode_tt27'), svg=False)
    # step tt
    fig, axs = plt.subplots(1, 2, figsize=(8.0, 4.4), sharey=True)
    for (view, pt, a, ld), d in [(k, v) for k, v in cv.items() if k[2] == 'step' and k[1] == PTS[0]
                                 and k[0] in ('prev', 'c', 'cc', 'rc')]:
        for ax, t0 in zip(axs, (2e-6, 7e-6)):
            s = (d['time'] >= t0 - 0.1e-6) & (d['time'] <= t0 + 1.2e-6)
            ax.plot((d['time'][s] - t0) * 1e9, d['v(padout)'][s], color=lc[ld], ls=VLS[view], lw=1.1)
    for ax, e in zip(axs, ('rising edge (2 µs)', 'falling edge (7 µs)')):
        ax.set_xlabel('time after the input edge [ns]')
        ax.set_title(e, fontsize=8.5)
    axs[0].set_ylabel('pad out [V]')
    h = [plt.Line2D([], [], color=lc[l], label=LN[l]) for l in LOADS]
    h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label=VNAME[v]) for v in ('prev', 'c', 'cc', 'rc')]
    axs[1].legend(handles=h, loc='center right', fontsize=6.0)
    fig.suptitle(f'{LABEL}\nstep pad in 0.25 → 0.75 → 0.25 V (10 ns edges), tt 27 °C 3.3 V', fontsize=8.5)
    fig.tight_layout()
    DC.save(fig, str(dest / 'plots' / 'step_tt27'), svg=False)
    # enable transient from the disabled op: tt, ss, ff
    if any(k[2] == 'en' for k in cv):
        fig, axs = plt.subplots(2, 1, figsize=(7.4, 6.0), sharex=True)
        for (view, pt, a), d in [(k, v) for k, v in cv.items() if k[2] == 'en' and k[0] in ('prev', 'c', 'rc')]:
            axs[0].plot(d['time'] * 1e6, d['v(vcm_s2d)'], color=pc[pt], ls=VLS[view], lw=1.1)
            axs[0].plot(d['time'] * 1e6, d['v(padout)'], color=pc[pt], ls=VLS[view], lw=0.8, alpha=0.6)
            axs[1].plot(d['time'] * 1e6, -d['i(vio)'] * 1e6, color=pc[pt], ls=VLS[view], lw=1.0)
        axs[0].set_ylabel('vcm (thick), pad out (thin) [V]')
        axs[1].set_ylabel('pad ring iovdd current [µA]')
        axs[1].set_xlabel('time [µs] (supplies on, enable 0 → 1.2 V at 2 µs)')
        axs[0].set_xlim(1, 12)
        pts = sorted({k[1] for k in cv if k[2] == 'en'}, key=PTS.index)
        h = [plt.Line2D([], [], color=pc[p], label='%s %d °C %.1f V' % p) for p in pts]
        h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label=VNAME[v]) for v in ('prev', 'c', 'rc')]
        axs[0].legend(handles=h, loc='lower right', fontsize=6.5)
        axs[0].set_title(f'{LABEL}\nenable transient from the disabled operating point, pad in 0.5 V, pad out 1 GΩ + '
                         '10 pF', fontsize=8.5)
        fig.tight_layout()
        DC.save(fig, str(dest / 'plots' / 'enable'), svg=False)
    if not any(k[2] == 'pu' for k in cv):
        return
    # power-up tt and ss
    fig, axs = plt.subplots(2, 1, figsize=(7.4, 6.0), sharex=True)
    for (view, pt, a), d in [(k, v) for k, v in cv.items() if k[2] == 'pu' and k[1] in (PTS[0], PTS[1])
                             and k[0] in ('prev', 'c', 'rc')]:
        axs[0].plot(d['time'] * 1e6, d['v(vcm_s2d)'], color=pc[pt], ls=VLS[view], lw=1.0)
        axs[0].plot(d['time'] * 1e6, d['v(padout)'], color=pc[pt], ls=VLS[view], lw=0.8, alpha=0.6)
        axs[1].plot(d['time'] * 1e6, -d['i(vio)'] * 1e6, color=pc[pt], ls=VLS[view], lw=1.0)
    axs[0].set_ylabel('vcm (thick), pad out (thin) [V]')
    axs[1].set_ylabel('pad ring iovdd current [µA]')
    axs[1].set_xlabel('time [µs] (supplies 0 → V in 10 µs, enable at 20 µs)')
    h = [plt.Line2D([], [], color=pc[p], label='%s %d °C %.1f V' % p) for p in PTS[:2]]
    h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label=VNAME[v]) for v in ('prev', 'c', 'rc')]
    axs[0].legend(handles=h, loc='upper left', fontsize=6.5)
    axs[0].set_title(f'{LABEL}\npower-up and enable, pad in 0.5 V, pad out 1 GΩ + 10 pF', fontsize=8.5)
    fig.tight_layout()
    DC.save(fig, str(dest / 'plots' / 'powerup'), svg=False)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
