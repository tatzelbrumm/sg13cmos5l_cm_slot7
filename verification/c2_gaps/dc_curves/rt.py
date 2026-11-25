#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Round trip S2D -> slot 7 (default mode) -> D2S: plots, range table, summary CSV (IHP sg13cmos5l simulation).

Usage: rt.py <rt_out_dir> <dest_dir>   (reads rt_<view>_<mos>_<temp>_<vdd>.csv written by roundtrip.py)

expected = v(vcm_s2d) + v(padin) - v(vref_s2d) (replica values as simulated; the designer's run_tier1.py definition)
err      = v(padout) - expected
err_ss   = deviation of padout(padin) from its small-signal line (slope from padin = vref_s2d +- 0.1 V, value at
           vref_s2d); the round-trip gain is 1, so input- and output-referred are the same
range    = contiguous padin range around vref_s2d with |err_ss| < 1 mV (and < 10 mV), with the padout span
"""
import csv
import glob
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import LABEL, VIEWNAME, contiguous_range, md_table, plt, save, ss_line, style  # noqa: E402

PTS = [('tt', 27, 3.3), ('ss', -40, 3.0), ('ff', 125, 3.6), ('fs', 125, 3.6), ('sf', -40, 3.0)]
PCOL = {('tt', 27, 3.3): '#2a78d6', ('ss', -40, 3.0): '#eb6834', ('ff', 125, 3.6): '#1baf7a',
        ('fs', 125, 3.6): '#e87ba4', ('sf', -40, 3.0): '#eda100'}
VLS = {'schematic': '-', 'pex': '--', 'klayout': ':'}
VIEWS = ['schematic', 'pex', 'klayout']
RTLABEL = 'IHP sg13cmos5l simulation, slot 7 tier-1 deck (pads: schematic | magic PEX | KLayout-extracted)'


def load(d):
    runs = {}
    for f in sorted(glob.glob(str(Path(d) / 'rt_*.csv'))):
        m = re.match(r'rt_(\w+?)_(\w\w)_(-?\d+)_([\d.]+)\.csv', Path(f).name)
        lines = open(f).read().split('\n')
        head = lines[0].split()
        a = np.array([[float(x) for x in l.split()] for l in lines[1:] if len(l.split()) == len(head)])
        if len(a) == 0:
            continue
        runs[(m.group(1), m.group(2), int(m.group(3)), float(m.group(4)))] = {h: a[:, i] for i, h in enumerate(head)}
    return runs


def metrics(d):
    x, y = d['v(padin)'], d['v(padout)']
    vref = float(np.interp(0.5, x, d['v(vref_s2d)']))
    vcm = float(np.interp(0.5, x, d['v(vcm_s2d)']))
    vrefd = float(np.interp(0.5, x, d['v(vref_d2s)']))
    exp = d['v(vcm_s2d)'] + x - d['v(vref_s2d)']
    err = y - exp
    G, y0 = ss_line(x, y, x0=vref)
    err_ss = y - y0 - G * (x - vref)
    m = dict(x=x, y=y, err=err, err_ss=err_ss, G=G, vref=vref, vcm=vcm, vrefd=vrefd, off=y0 - vcm,
             emax01=np.abs(err[(x >= 0) & (x <= 1.0 + 1e-9)]).max())
    for tag, lim in (('1', 1e-3), ('10', 10e-3)):
        lo, hi, loc, hic = contiguous_range(x, err_ss, lim, x0=vref)
        m['lo' + tag], m['hi' + tag], m['loc' + tag] = lo, hi, loc
        m['olo' + tag], m['ohi' + tag] = float(np.interp(lo, x, y)), float(np.interp(hi, x, y))
    return m


def main(rdir, dest):
    dest = Path(dest)
    style()
    runs = load(rdir)
    if not runs:
        sys.exit('no round-trip data')
    ms = {k: metrics(d) for k, d in runs.items()}
    # 1. transfer at tt 27 C 3.3 V, all views
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ref = None
    for v in VIEWS:
        k = (v, 'tt', 27, 3.3)
        if k not in ms:
            continue
        m = ms[k]
        ax.plot(m['x'], m['y'], color={'schematic': '#2a78d6', 'pex': '#eb6834', 'klayout': '#1baf7a'}[v],
                ls=VLS[v], label='pad out, pads %s' % VIEWNAME[v])
        ref = ref or m
    if ref:
        ax.plot(ref['x'], ref['vcm'] + ref['x'] - ref['vref'], color='#8a8984', lw=0.8, ls='-.',
                label='expected vcm + (pad in - vref)')
        ax.axvspan(ref['lo1'], ref['hi1'], color='#2a78d6', alpha=0.08, lw=0)
        ax.text(2.3, 0.45, 'shaded: |error from small-signal line| < 1 mV\npad in %.3f ... %.3f V -> pad out %.3f ... '
                '%.3f V\n(pads schematic; replica vref %.3f V, vcm %.3f V)' % (ref['lo1'], ref['hi1'], ref['olo1'],
                                                                             ref['ohi1'], ref['vref'], ref['vcm']),
                ha='center', fontsize=7.3, bbox=dict(boxstyle='round', fc='white', ec='#2a78d6', lw=0.8))
    ax.set_xlim(-0.3, 3.3)
    ax.set_ylim(-0.1, 3.5)
    ax.set_xlabel('S2D pad input voltage (pad in) [V]')
    ax.set_ylabel('D2S pad output voltage (pad out) [V]')
    ax.set_title('Round trip S2D -> slot 7 default mode -> D2S, pad out unloaded (1 GΩ)\n%s\ntt, 27 °C, '
                 'vdd_3v3 = iovdd 3.3 V, vref / vcm from the slot\'s replica bias' % RTLABEL, fontsize=8.5)
    ax.legend(loc='upper left')
    fig.tight_layout()
    save(fig, str(dest / 'plots' / 'rt_transfer_tt27'))
    # 2. error vs input, PVT points (color) x views (line style)
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    for k, m in ms.items():
        sel = (m['x'] >= -0.3) & (m['x'] <= 1.5)
        ax.plot(m['x'][sel], m['err'][sel] * 1e3, color=PCOL[k[1:]], ls=VLS[k[0]], lw=1.1)
    ax.set_yscale('symlog', linthresh=1, linscale=1)
    ax.set_ylim(-1000, 1000)
    ax.axhspan(-1, 1, color='#2a78d6', alpha=0.06, lw=0)
    ax.set_xlim(-0.3, 1.5)
    ax.set_xlabel('S2D pad input voltage (pad in) [V]')
    ax.set_ylabel('pad out - (vcm + pad in - vref) [mV]')
    h = [plt.Line2D([], [], color=PCOL[p], label='%s %d °C %.1f V' % p) for p in PTS]
    h += [plt.Line2D([], [], color='#52514e', ls=VLS[v], label='pads ' + VIEWNAME[v]) for v in VIEWS]
    ax.legend(handles=h, loc='lower left', ncol=2)
    ax.set_title('Round trip: error vs expected (replica vcm / vref as simulated), pad out unloaded\n%s\n'
                 'corner extremes of the designer\'s tier-1 points; symlog axis, linear inside ±1 mV' % RTLABEL,
                 fontsize=8.5)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / 'rt_error_corners'))
    # table + CSV
    hd = ['pads', 'corner', 'T [°C]', 'V', 'replica vref / vcm [V]', 'D2S vref [V]', 'gain', 'offset [mV]',
          'max \\|err\\| pad in 0 ... 1 V [mV]', 'pad in range 1 mV [V]', 'pad out range 1 mV [V]', 'pad in range 10 mV [V]']
    rr, cr = [], []
    for p in PTS:
        for v in VIEWS:
            k = (v,) + p
            if k not in ms:
                rr.append([VIEWNAME[v], *p, 'not run / failed', '', '', '', '', '', '', ''])
                continue
            m = ms[k]
            part = '' if m['x'][-1] > 3.29 else ' (sweep aborted at pad in %.3f V)' % m['x'][-1]
            rr.append([VIEWNAME[v] + part, *p, '%.4f / %.4f' % (m['vref'], m['vcm']), '%.4f' % m['vrefd'], '%.5f' % m['G'],
                       '%.2f' % (m['off'] * 1e3), '%.2f' % (m['emax01'] * 1e3),
                       '%s%.3f ... %.3f' % ('<=' if m['loc1'] else '', m['lo1'], m['hi1']),
                       '%.3f ... %.3f' % (m['olo1'], m['ohi1']),
                       '%s%.3f ... %.3f' % ('<=' if m['loc10'] else '', m['lo10'], m['hi10'])])
            cr.append([v, *p, m['vref'], m['vcm'], m['vrefd'], '%.5f' % m['G'], '%.3f' % (m['off'] * 1e3),
                       '%.3f' % (m['emax01'] * 1e3), '%.4f' % m['lo1'], '%.4f' % m['hi1'], '%.4f' % m['olo1'],
                       '%.4f' % m['ohi1'], '%.4f' % m['lo10'], '%.4f' % m['hi10']])
    txt = ('\n#### Round trip S2D -> slot 7 -> D2S (pad out unloaded), %s\n\n' % RTLABEL + md_table(hd, rr) +
           '\n\noffset = pad out - vcm at pad in = vref (replica values); max |err| over pad in 0 ... 1 V against '
           'vcm + pad in - vref (run_tier1.py definition); ranges: contiguous around pad in = vref with |error from the '
           'small-signal line| < 1 mV / 10 mV. "<=-0.300" = criterion still met at the sweep start.\n')
    (dest / 'tables' / 'rt.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n<!-- generated by dc_curves/rt.py, do not edit -->\n' + txt)
    with open(dest / 'csv' / 'rt_summary.csv', 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                f'# round trip, {RTLABEL}; rt.py\n')
        csv.writer(f).writerows([['pads', 'corner_mos', 'temp', 'vdd', 'vref_s2d', 'vcm', 'vref_d2s', 'gain',
                                  'offset_mV', 'max_abs_err_0to1V_mV', 'in_lo_1mV', 'in_hi_1mV', 'out_lo_1mV',
                                  'out_hi_1mV', 'in_lo_10mV', 'in_hi_10mV']] + cr)
    print(txt)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
