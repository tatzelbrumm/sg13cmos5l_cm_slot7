#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""D2S pad sg13cmos5l_IOPadDiff2Single: DC-transfer plots, output-range table, summary CSV (IHP sg13cmos5l simulation).

Usage: d2s.py <work_out_dir> <dest_dir>   (reads <work_out_dir>/{schematic,pex}/{d2s_grid,d2s_noload,d2s_slot}.csv.gz)

Quantities per run (vd = vinp - vinn, the swept dp; vo = pad - vref; ideal vo = vd/2):
  Gain, vo0  small-signal line of vo(vd) as the CACE tb_dc: slope from vd = +-0.2 V, value at vd = 0
  INL        max |vo - vo0 - Gain vd| over |vd| <= 1 V, output-referred (= CACE dc_params INL, limit 10 mV)
  err_ss     vo - vo0 - Gain vd, output-referred (deviation from the small-signal line)
  err_id     vo - vd/2, output-referred (deviation from the ideal transfer; includes gain error and offset)
  range      contiguous vd range around 0 with |err_ss| < 10 mV (the CACE INL limit), given as the pad-voltage span
             vref + vo at its ends; also with 1 mV
  Vout_max / Vout_min  pad at vd = +3 / -3 V (as CACE drive_params) and at the sweep ends +-3.3 V
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (COLOR, CORNERS, LABEL, LS, VCOLOR, contiguous_range, load, md_table, plt, save,  # noqa: E402
                    ss_line, style)
from s2d import range_plot  # noqa: E402

LIM, LIM2 = 10e-3, 1e-3


def metrics(d):
    x, pad, vref = d['v(dp)'], d['v(pad)'], d['v(vref)']
    vo = pad - vref
    G, vo0 = ss_line(x, vo, dx=0.2)
    err_ss = vo - vo0 - G * x
    err_id = vo - x / 2
    m = {'x': x, 'pad': pad, 'vo': vo, 'G': G, 'vo0': vo0, 'err_ss': err_ss, 'err_id': err_id, 'vref': vref[0],
         'inl': np.abs(err_ss[np.abs(x) <= 1 + 1e-9]).max(),
         'p3': float(np.interp(3, x, pad)) if x[-1] >= 3 else np.nan,
         'm3': float(np.interp(-3, x, pad)) if x[0] <= -3 else np.nan, 'pmax': pad.max(), 'pmin': pad.min(),
         'xend': x[-1], 'pend': pad[-1], 'pstart': pad[0],
         'iio': -float(np.interp(0, x, d['i(vio)']))}
    for tag, lim in (('', LIM), ('1', LIM2)):
        lo, hi, loc, hic = contiguous_range(x, err_ss, lim)
        m['xlo' + tag], m['xhi' + tag] = lo, hi
        m['lo' + tag] = float(np.interp(lo, x, pad))
        m['hi' + tag] = float(np.interp(hi, x, pad))
        m['loc' + tag], m['hic' + tag] = loc, hic
    return m


def transfer_plot(view, k, d_l, m_l, d_u, m_u, dest):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.axvspan(m_l['xlo'], m_l['xhi'], color='#2a78d6', alpha=0.08, lw=0)
    ax.plot(m_l['x'], m_l['pad'], color='#2a78d6', label='pad, 1 kΩ to 1.65 V (CACE load) + 100 pF')
    if m_u is not None:
        ax.plot(m_u['x'], m_u['pad'], color='#eb6834', ls='--', label='pad, unloaded (1 TΩ)')
    ax.plot(m_l['x'], m_l['vref'] + m_l['x'] / 2, color='#8a8984', lw=0.8, ls=':', label='ideal vref + (vinp - vinn)/2')
    ax.axhline(k[2], color='#52514e', lw=0.6, ls='-.')
    ax.axhline(0, color='#52514e', lw=0.6, ls='-.')
    ax.text(2.45, 0.3, 'output range (1 kΩ):\n%.3f ... %.3f V\n(|error from small-signal line|\n< 10 mV, output-referred)'
            % (m_l['lo'], m_l['hi']), ha='center', fontsize=7.5,
            bbox=dict(boxstyle='round', fc='white', ec='#2a78d6', lw=0.8))
    ax.text(-0.9, k[2] + 0.06, 'iovdd %.1f V' % k[2], fontsize=7.5, color='#52514e')
    ax.text(-3.2, 2.45, 'pad at vinp - vinn = ±3 V:\n1 kΩ: %.3f / %.3f V' % (m_l['m3'], m_l['p3'])
            + ('\nunloaded: %.3f / %.3f V' % (m_u['m3'], m_u['p3']) if m_u is not None else ''), fontsize=7.5,
            va='top')
    ax.set_xlim(-3.3, 3.3)
    ax.set_ylim(-0.1, 3.7)
    ax.set_xlabel('differential input vinp - vinn [V] (around vicm = %.2f V)' % m_l['vref'])
    ax.set_ylabel('pad output voltage [V]')
    ax.set_title('D2S pad DC transfer: %s\n%s, %d °C, iovdd %.1f V, vref = vicm = %.2f V, iref 5 µA'
                 % (LABEL[view], k[0], k[1], k[2], m_l['vref']))
    ax.legend(loc='upper left', bbox_to_anchor=(0.0, 0.89))
    fig.tight_layout()
    save(fig, str(dest / 'plots' / f'd2s_transfer_tt27_{view}'))


def corner_plot(view, ms, dest, vdd, name, what):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True, gridspec_kw={'height_ratios': [1, 1.25]})
    for k, m in ms.items():
        if k[2] != vdd:
            continue
        kw = dict(color=COLOR[k[0]], ls=LS[k[1]], lw=1.1)
        a1.plot(m['x'], m['pad'], **kw)
        a2.plot(m['x'][::2], m['err_id'][::2] * 1e3, **kw)
    m0 = next(iter(ms.values()))
    a1.plot([-3.3, 3.3], [m0['vref'] - 1.65, m0['vref'] + 1.65], color='#8a8984', lw=0.8, ls='-.')
    xm = max(abs(m0['x'][0]), m0['x'][-1])
    a1.set_ylabel('pad [V]')
    a1.set_ylim(0, 3.7)
    a2.set_ylabel('pad - vref - (vinp - vinn)/2 [mV]\n(error vs ideal, output-referred)')
    a2.set_yscale('symlog', linthresh=1, linscale=1)
    a2.set_ylim(-3000, 3000)
    a2.axhspan(-10, 10, color='#2a78d6', alpha=0.06, lw=0)
    a2.set_xlabel('differential input vinp - vinn [V]')
    a2.set_xlim(-xm, xm)
    a1.set_title('D2S pad: output and error vs ideal over corners, %s\n%s, iovdd %.1f V, vref = vicm = %.2f V\n'
                 'color = MOS corner, line style = temperature' % (LABEL[view], what, vdd, m0['vref']))
    h = [plt.Line2D([], [], color=COLOR[c], label=c) for c in CORNERS]
    h += [plt.Line2D([], [], color='#52514e', ls=LS[t], label='%d °C' % t) for t in (-40, 27, 125)]
    a2.legend(handles=h, loc='lower right', ncol=4)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / name))


def criterion_plot(allms, dest, vdd, name, what):
    views = [v for v in ('schematic', 'pex') if v in allms]
    fig, axs = plt.subplots(1, len(views), figsize=(7.6, 4.5), sharey=True, squeeze=False)
    for ax, view in zip(axs[0], views):
        for k, m in allms[view].items():
            if k[2] != vdd:
                continue
            ax.semilogy(m['pad'][::2], np.abs(m['err_ss'][::2]) * 1e3 + 1e-6, color=COLOR[k[0]], ls=LS[k[1]], lw=1.0)
        ax.axhline(10, color='#0b0b0b', lw=0.9)
        ax.axhline(1, color='#0b0b0b', lw=0.6, ls='--')
        ax.text(0.05, 12, '10 mV criterion', fontsize=7.5)
        ax.set_xlim(0, 3.6 if vdd > 3.3 else 3.4)
        ax.set_ylim(1e-3, 3e3)
        ax.set_xlabel('pad output voltage [V]')
        ax.set_title(LABEL[view], fontsize=8.5)
    axs[0][0].set_ylabel('|error from small-signal line| [mV], output-referred')
    h = [plt.Line2D([], [], color=COLOR[c], label=c) for c in CORNERS]
    h += [plt.Line2D([], [], color='#52514e', ls=LS[t], label='%d °C' % t) for t in (-40, 27, 125)]
    axs[0][-1].legend(handles=h, loc='lower center', ncol=3)
    fig.suptitle('D2S pad: output-range criterion |vo - vo0 - G (vinp - vinn)| < 10 mV (G, vo0 from vinp - vinn = 0, '
                 '±0.2 V)\n%s, all MOS corners, −40 / 27 / 125 °C, iovdd %.1f V' % (what, vdd), fontsize=9.5)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / name))


def fmt(m, t=''):
    return '%.3f ... %.3f' % (m['lo' + t], m['hi' + t])


def main(wout, dest):
    wout, dest = Path(wout), Path(dest)
    style()
    rows, tables = [], []
    allm = {}
    for group, what in (('d2s_grid', '1 kΩ to 1.65 V + 100 pF (CACE load)'), ('d2s_noload', 'unloaded'),
                        ('d2s_slot', 'slot operating point: 1 kΩ to vref = 1.26 V + 100 pF')):
        allms = {}
        for view in ('schematic', 'pex'):
            p = wout / view / f'{group}.csv.gz'
            if p.exists():
                allms[view] = {k: metrics(d) for k, d in load(p).items()}
        if not allms:
            continue
        allm[group] = allms
        suf = {'d2s_grid': '', 'd2s_noload': '_noload', 'd2s_slot': '_slot'}[group]
        vr = next(iter(next(iter(allms.values())).values()))['vref']
        for view, ms in allms.items():
            # PEX corner figures only for the main case (CACE load, 3.3 V): the PEX curves of the other cases equal the
            # schematic ones within < 1 mV (tables), and the folder has a size budget
            if view == 'schematic' or group == 'd2s_grid':
                corner_plot(view, ms, dest, 3.3, f'd2s_corners{suf}_{view}', what)
            if group in ('d2s_grid', 'd2s_slot') and view == 'schematic':
                corner_plot(view, ms, dest, 3.0, f'd2s_corners{suf}_3v0_{view}', what)
            for k, m in ms.items():
                rows.append([group, view, k[0], k[1], k[2], m['vref'], '%.5f' % m['G'], '%.3f' % (m['vo0'] * 1e3),
                             '%.3f' % (m['inl'] * 1e3), '%.4f' % m['xlo'], '%.4f' % m['xhi'], '%.4f' % m['lo'],
                             '%.4f' % m['hi'], '%.4f' % m['lo1'], '%.4f' % m['hi1'], '%.4f' % m['m3'], '%.4f' % m['p3'],
                             '%.4f' % m['pmin'], '%.4f' % m['pmax'], '%.2f' % (m['iio'] * 1e6)])
        if group == 'd2s_grid':
            criterion_plot(allms, dest, 3.3, f'd2s_linearity_criterion{suf}', what)
        rp = {v: {k: dict(lo=m['lo'], hi=m['hi'], loc=False, hic=False) for k, m in ms.items()}
              for v, ms in allms.items()}
        range_plot(rp, dest, None, name=f'd2s_range{suf}', xlabel='pad output voltage [V]', xlim=(0, 3.6),
                   what='D2S pad: linear output range per corner and supply (|error from small-signal line| < 10 mV, '
                        'output-referred)\n%s, vref = vicm = %.2f V, iref 5 µA' % (what, vr), ref=vr)
        # tables
        for view, ms in allms.items():
            tables.append(f'\n#### D2S output range, {what}, {LABEL[view]}\n\nPad-voltage span [V] in which '
                          '|error from the small-signal line| < 10 mV (output-referred; CACE INL limit), in brackets '
                          '< 1 mV; then pad at vinp - vinn = -3 / +3 V; INL = CACE definition (max over |vd| <= 1 V).\n')
            xe = next(iter(ms.values()))['xend']
            hd = ['corner', 'T [°C]', 'iovdd [V]', 'range 10 mV', '(range 1 mV)', 'pad at vd = -%.2f / +%.2f V' % (xe, xe),
                  'INL ±1 V [mV]', 'Gain']
            rr = []
            for c in CORNERS:
                for t in (-40, 27, 125):
                    for v in (3.0, 3.3, 3.6):
                        k = next((k for k in ms if k[:3] == (c, t, v)), None)
                        if k is None:
                            continue
                        m = ms[k]
                        rr.append([c, t, v, fmt(m), '(%s)' % fmt(m, '1'), '%.3f / %.3f' % (m['pstart'], m['pend']),
                                   '%.2f' % (m['inl'] * 1e3), '%.4f' % m['G']])
            tables.append(md_table(hd, rr))
            for v in (3.0, 3.3, 3.6):
                sub = {k: m for k, m in ms.items() if k[2] == v}
                if not sub:
                    continue
                lo = max(sub.items(), key=lambda kv: kv[1]['lo'])
                hi = min(sub.items(), key=lambda kv: kv[1]['hi'])
                inl = max(sub.items(), key=lambda kv: kv[1]['inl'])
                tables.append('\niovdd %.1f V (%d runs): range 10 mV worst ends: low %.3f V (%s %d °C), high %.3f V '
                              '(%s %d °C); best low %.3f V, best high %.3f V; INL max %.2f mV (%s %d °C); pad at vd = '
                              '-%.2f V %.3f ... %.3f V, at +%.2f V %.3f ... %.3f V.\n'
                              % (v, len(sub), lo[1]['lo'], *lo[0][:2], hi[1]['hi'], *hi[0][:2],
                                 min(m['lo'] for m in sub.values()), max(m['hi'] for m in sub.values()),
                                 inl[1]['inl'] * 1e3, *inl[0][:2], xe, min(m['pstart'] for m in sub.values()),
                                 max(m['pstart'] for m in sub.values()), xe, min(m['pend'] for m in sub.values()),
                                 max(m['pend'] for m in sub.values())))
        if 'schematic' in allms and 'pex' in allms:
            a, b = allms['schematic'], allms['pex']
            ks = [k for k in a if k in b]
            tables.append('\nSchematic vs magic PEX (%s), %d common runs: max |diff| range low %.2f mV, high %.2f mV, '
                          'INL %.3f mV, gain %.1e, pad at the sweep ends %.2f mV.\n'
                          % (what, len(ks), max(abs(a[k]['lo'] - b[k]['lo']) for k in ks) * 1e3,
                             max(abs(a[k]['hi'] - b[k]['hi']) for k in ks) * 1e3,
                             max(abs(a[k]['inl'] - b[k]['inl']) for k in ks) * 1e3,
                             max(abs(a[k]['G'] - b[k]['G']) for k in ks),
                             max(max(abs(a[k]['pend'] - b[k]['pend']), abs(a[k]['pstart'] - b[k]['pstart']))
                                 for k in ks) * 1e3))
    # tt 27 C 3.3 V transfer, loaded and unloaded
    for view in ('schematic', 'pex'):
        g = allm.get('d2s_grid', {}).get(view)
        if not g:
            continue
        kt = [k for k in g if k[:3] == ('tt', 27, 3.3)][0]
        nl = allm.get('d2s_noload', {}).get(view, {})
        u = next((m for k, m in nl.items() if k[:3] == kt[:3]), None)
        transfer_plot(view, kt, None, g[kt], None, u, dest)
    head = ['group', 'view', 'corner_mos', 'temp', 'vdd', 'vref', 'Gain', 'Vos_out_mV', 'INL_pm1V_mV', 'vd_lo_10mV_V',
            'vd_hi_10mV_V', 'pad_lo_10mV_V', 'pad_hi_10mV_V', 'pad_lo_1mV_V', 'pad_hi_1mV_V', 'pad_at_vd_m3V',
            'pad_at_vd_p3V', 'pad_min_sweep', 'pad_max_sweep', 'Iio_uA']
    for group in ('d2s_grid', 'd2s_noload', 'd2s_slot'):
        rr = [r for r in rows if r[0] == group]
        if not rr:
            continue
        with open(dest / 'csv' / f'{group}_summary.csv', 'w', newline='') as f:
            f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                    f'# D2S pad, {group}: IHP sg13cmos5l simulation (schematic | magic PEX); d2s.py; criteria in '
                    'README.md\n')
            csv.writer(f).writerows([head[1:]] + [r[1:] for r in rr])
    (dest / 'tables' / 'd2s.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n<!-- generated by dc_curves/d2s.py, do not edit -->\n' + '\n'.join(tables) + '\n')
    print('\n'.join(tables))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
