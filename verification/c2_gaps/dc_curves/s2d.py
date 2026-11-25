#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""S2D pad sg13cmos5l_IOPadSingle2Diff: DC-transfer plots, range table, summary CSV (IHP sg13cmos5l simulation).

Usage: s2d.py <work_out_dir> <dest_dir> [<group>]   (group default s2d_grid; reads <work_out_dir>/{schematic,pex}/<group>.csv.gz)

Quantities per run (u = pad source - vref, pad = the pad node behind the 50 Ohm source; vd = outp - outn,
vc = (outp + outn)/2):
  Gain, vd0  small-signal line of vd(u) as the CACE tb_dc: slope from u = +-0.1 V, value at u = 0
  err_ss     (vd - vd0 - Gain u) / Gain: deviation from the small-signal line, referred to the input (CACE INL / window)
  err_id     vd/2 - (pad - vref): deviation from the ideal transfer, referred to the input (includes gain error, offset)
  range      contiguous pad range around pad = vref with |err_ss| < 1 mV (= the CACE window_params criterion; the CACE
             testbench starts its sweep at pad = 0 V, this one at -0.3 V, so Vin_min < 0 is possible here)
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (COLOR, CORNERS, LABEL, LS, VCOLOR, VIEWNAME, contiguous_range, load, md_table, plt, save,  # noqa
                    ss_line, style)

LIM = 1e-3


def metrics(d, vref):
    u, pad = d['v(u)'], d['v(pad)']
    vd = d['v(outp)'] - d['v(outn)']
    vc = (d['v(outp)'] + d['v(outn)']) / 2 - d['v(vcm)']
    G, vd0 = ss_line(u, vd)
    err_ss = (vd - vd0 - G * u) / G
    err_id = vd / 2 - (pad - vref)
    lo, hi, loc, hic = contiguous_range(u, err_ss, LIM)
    vc0 = float(np.interp(0, u, vc))
    m = (pad >= 0) & (pad <= 1.0)
    inl05 = np.abs(err_ss[np.abs(u) <= 0.5 + 1e-9]).max()
    return dict(u=u, pad=pad, vd=vd, vc=vc, G=G, vd0=vd0, err_ss=err_ss, err_id=err_id, lo=lo + vref, hi=hi + vref,
                loc=loc, hic=hic, vc0=vc0, iio=-float(np.interp(0, u, d['i(vio)'])),
                eid01=np.abs(err_id[m]).max(), inl05=inl05)


def fmt_lo(m):
    return ('<= %.3f' % m['lo']) if m['loc'] else '%.3f' % m['lo']


def transfer_plot(view, k, d, m, dest, cond):
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    ax.axvspan(m['lo'], m['hi'], color='#2a78d6', alpha=0.08, lw=0)
    ax.plot(m['pad'], d['v(outp)'], color='#2a78d6', label='outp')
    ax.plot(m['pad'], d['v(outn)'], color='#eb6834', label='outn')
    ax.plot(m['pad'], m['vd'], color='#0b0b0b', label='outp - outn')
    ax.plot(m['pad'], (d['v(outp)'] + d['v(outn)']) / 2, color='#1baf7a', ls='--', label='(outp + outn)/2')
    ax.plot(m['pad'], 2 * (m['pad'] - cond['vref']), color='#8a8984', lw=0.8, ls=':', label='ideal 2 (pad - vref)')
    for x in (m['lo'], m['hi']):
        ax.axvline(x, color='#2a78d6', lw=0.8)
    ax.axvline(cond['vref'], color='#8a8984', lw=0.8, ls='-.')
    ax.text(2.45, 1.05, 'shaded: linear range\n%s ... %.3f V\n(|error from small-signal line|\n< 1 mV, input-referred)'
            % (fmt_lo(m).replace('<= ', '<='), m['hi']), ha='center', va='center', fontsize=7.5, color='#0b0b0b',
            bbox=dict(boxstyle='round', fc='white', ec='#2a78d6', lw=0.8))
    ax.text(cond['vref'] + 0.03, -1.85, 'vref = %.2f V' % cond['vref'], fontsize=7.5, color='#52514e')
    ax.set_xlim(-0.3, 3.3)
    ax.set_ylim(-2.0, 3.0)
    ax.set_xlabel('pad input voltage [V]')
    ax.set_ylabel('output voltage [V]')
    ax.set_title('S2D pad DC transfer: %s\n%s, %d °C, iovdd %.1f V, vref %.2f V, vcm %.2f V, iref 5 µA'
                 % (LABEL[view], k[0], k[1], k[2], cond['vref'], cond['vcm']))
    ax.legend(loc='lower right', ncol=1)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / f's2d_transfer_tt27_{view}'))


def corner_plot(view, runs, ms, dest, cond, vdd=3.3):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 7.0), sharex=True, gridspec_kw={'height_ratios': [1, 1.25]})
    for k, m in ms.items():
        if k[2] != vdd:
            continue
        kw = dict(color=COLOR[k[0]], ls=LS[k[1]], lw=1.1)
        a1.plot(m['pad'], m['vd'], **kw)
        a2.plot(m['pad'], m['err_id'] * 1e3, **kw)
    a1.plot([0, 1.3], [2 * (0 - cond['vref']), 2 * (1.3 - cond['vref'])], color='#8a8984', lw=0.8, ls='-.')
    a1.set_ylabel('outp - outn [V]')
    a1.set_ylim(-1.2, 1.8)
    a2.set_ylabel('vd/2 - (pad - vref) [mV]\n(error vs ideal, input-referred)')
    a2.set_yscale('symlog', linthresh=1, linscale=1)
    a2.set_ylim(-100, 100)
    a2.axhspan(-1, 1, color='#2a78d6', alpha=0.06, lw=0)
    a2.set_xlabel('pad input voltage [V]')
    a2.set_xlim(0, 1.3)
    a1.set_title('S2D pad: differential output and error vs ideal over corners: %s\niovdd %.1f V, vref %.2f V, '
                 'vcm %.2f V, iref 5 µA; color = MOS corner, line style = temperature' % (LABEL[view], vdd,
                                                                                            cond['vref'], cond['vcm']))
    h = [plt.Line2D([], [], color=COLOR[c], label=c) for c in CORNERS]
    h += [plt.Line2D([], [], color='#52514e', ls=LS[t], label='%d °C' % t) for t in (-40, 27, 125)]
    a2.legend(handles=h, loc='lower left', ncol=4)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / f's2d_corners_{view}'))


def criterion_plot(allms, dest, cond, vdd=3.3):
    views = [v for v in ('schematic', 'pex') if v in allms]
    fig, axs = plt.subplots(1, len(views), figsize=(7.6, 4.5), sharey=True, squeeze=False)
    for ax, view in zip(axs[0], views):
        for k, m in allms[view].items():
            if k[2] != vdd:
                continue
            ax.semilogy(m['pad'][::2], np.abs(m['err_ss'][::2]) * 1e3 + 1e-6, color=COLOR[k[0]], ls=LS[k[1]], lw=1.0)
        ax.axhline(1, color='#0b0b0b', lw=0.9)
        ax.text(0.02, 1.15, '1 mV criterion', fontsize=7.5)
        ax.set_xlim(-0.3, 1.45)
        ax.set_ylim(1e-3, 1e3)
        ax.set_xlabel('pad input voltage [V]')
        ax.set_title(LABEL[view], fontsize=8.5)
    axs[0][0].set_ylabel('|error from small-signal line| [mV], input-referred')
    h = [plt.Line2D([], [], color=COLOR[c], label=c) for c in CORNERS]
    h += [plt.Line2D([], [], color='#52514e', ls=LS[t], label='%d °C' % t) for t in (-40, 27, 125)]
    axs[0][-1].legend(handles=h, loc='lower center', ncol=3)
    fig.suptitle('S2D pad: linear-range criterion |(vd - vd0 - G u)/G| < 1 mV (G, vd0 from u = 0, ±0.1 V)\n'
                 'all MOS corners, −40 / 27 / 125 °C, iovdd %.1f V, vref %.2f V, vcm %.2f V' % (vdd, cond['vref'],
                                                                                            cond['vcm']), fontsize=9.5)
    fig.tight_layout()
    save(fig, str(dest / 'plots' / 's2d_linearity_criterion'))


def range_plot(allms, dest, cond, name='s2d_range', what='S2D pad: linear input range (1 mV criterion)',
               xlabel='pad input voltage [V]', xlim=(-0.3, 1.4), ref=None):
    """Range per corner / temperature / supply as horizontal bars, one panel per view."""
    views = [v for v in ('schematic', 'pex') if v in allms]
    fig, axs = plt.subplots(1, len(views), figsize=(max(7.2, 3.8 * len(views) + 0.8), 6.0), sharey=True,
                            squeeze=False)
    rows = [(c, t) for c in CORNERS for t in (-40, 27, 125)]
    for ax, view in zip(axs[0], views):
        ms = allms[view]
        for i, (c, t) in enumerate(rows):
            for j, v in enumerate((3.0, 3.3, 3.6)):
                k = next((k for k in ms if k[:3] == (c, t, v)), None)
                if k is None:
                    continue
                m = ms[k]
                y = i + (j - 1) * 0.25
                ax.plot([m['lo'], m['hi']], [y, y], color=VCOLOR[v], lw=2.2, solid_capstyle='butt')
                if m['loc']:
                    ax.plot([m['lo']], [y], marker='<', color=VCOLOR[v], ms=4)
                if m.get('hic'):
                    ax.plot([m['hi']], [y], marker='>', color=VCOLOR[v], ms=4)
        if ref is not None:
            ax.axvline(ref, color='#8a8984', lw=0.8, ls='-.')
        ax.set_yticks(range(len(rows)))
        ax.set_yticklabels(['%s %d °C' % r for r in rows])
        ax.set_ylim(len(rows) - 0.5, -0.5)
        ax.set_xlim(*xlim)
        ax.grid(axis='y', visible=False)
        ax.set_xlabel(xlabel)
        ax.set_title(LABEL[view], fontsize=8.5)
    h = [plt.Line2D([], [], color=VCOLOR[v], lw=2.2, label='iovdd %.1f V' % v) for v in (3.0, 3.3, 3.6)]
    fig.legend(handles=h, loc='lower center', ncol=3)
    fig.suptitle(what, fontsize=9.5)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    save(fig, str(dest / 'plots' / name))


def main(wout, dest, group='s2d_grid'):
    wout, dest = Path(wout), Path(dest)
    style()
    allms, rows = {}, []
    for view in ('schematic', 'pex'):
        p = wout / view / f'{group}.csv.gz'
        if not p.exists():
            continue
        runs = load(p)
        k0 = next(iter(runs))
        cond = dict(vref=k0[3], vcm=k0[4])
        ms = {k: metrics(d, k[3]) for k, d in runs.items()}
        allms[view] = ms
        if group == 's2d_grid':
            kt = [k for k in runs if k[:3] == ('tt', 27, 3.3)][0]
            transfer_plot(view, kt, runs[kt], ms[kt], dest, cond)
            corner_plot(view, runs, ms, dest, cond)
        for k, m in ms.items():
            rows.append([view, k[0], k[1], k[2], k[3], k[4], '%.5f' % m['G'], '%.4f' % (m['vd0'] / m['G'] * 1e3),
                         '%.2f' % (m['vc0'] * 1e3), '%.4f' % (m['inl05'] * 1e3), '%.4f' % m['lo'], int(m['loc']),
                         '%.4f' % m['hi'], int(m['hic']), '%.3f' % (m['eid01'] * 1e3), '%.2f' % (m['iio'] * 1e6)])
    if not allms:
        sys.exit('no data')
    if group == 's2d_slot':
        range_plot(allms, dest, cond, name='s2d_range_slot', ref=cond['vref'],
                   what='S2D pad at the slot\'s nominal replica vref / vcm: linear input range\n(|error from '
                   'small-signal line| < 1 mV, input-referred); vref %.2f V (dash-dot), vcm %.2f V, iref 5 µA'
                   % (cond['vref'], cond['vcm']))
    if group == 's2d_grid':
        criterion_plot(allms, dest, cond)
        range_plot(allms, dest, cond, what='S2D pad: linear input range per corner and supply (|error from small-'
                   'signal line| < 1 mV, input-referred)\nvref %.2f V (dash-dot), vcm %.2f V, iref 5 µA; '
                   '"<" = criterion still met at the sweep start -0.3 V' % (cond['vref'], cond['vcm']), ref=cond['vref'])
    head = ['view', 'corner_mos', 'temp', 'vdd', 'vref', 'vcm', 'Gain', 'Vos_in_mV', 'Vcm_err_mV', 'INL_pm0.5V_mV',
            'Vin_min_V', 'Vin_min_at_sweep_end', 'Vin_max_V', 'Vin_max_at_sweep_end', 'max_abs_err_ideal_0to1V_mV',
            'Iio_uA']
    with open(dest / 'csv' / f'{group}_summary.csv', 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                f'# S2D pad, {group}: IHP sg13cmos5l simulation (schematic | magic PEX); s2d.py; criteria in README.md\n')
        csv.writer(f).writerows([head] + rows)
    # markdown tables for results.md
    out = []
    for view, ms in allms.items():
        out.append(f'\n#### S2D input range, {LABEL[view]}\n\n'
                   'Vin_min ... Vin_max [V] = contiguous pad range around pad = vref with |error from the small-signal '
                   'line| < 1 mV (input-referred); vref %.2f V, vcm %.2f V. "<=" = criterion still met at the sweep '
                   'start (-0.3 V).\n' % (next(iter(ms))[3], next(iter(ms))[4]))
        hd = ['corner', 'T [°C]'] + ['%.1f V' % v for v in (3.0, 3.3, 3.6)]
        rr = []
        for c in CORNERS:
            for t in (-40, 27, 125):
                r = [c, t]
                for v in (3.0, 3.3, 3.6):
                    m = ms.get(next((k for k in ms if k[:3] == (c, t, v)), None))
                    r.append('%s ... %.3f' % (fmt_lo(m), m['hi']) if m else 'n/a')
                rr.append(r)
        out.append(md_table(hd, rr))
        lo = min(m['lo'] for m in ms.values()); hi = [m['hi'] for m in ms.values()]
        his = sorted(ms.items(), key=lambda kv: kv[1]['hi'])
        out.append('\nHigh end over all %d runs: %.3f V (%s %d °C %.1f V) ... %.3f V (%s %d °C %.1f V); low end '
                   'max %.3f V (%s); max |err vs ideal| over pad 0 ... 1 V: %.2f mV; gain %.5f ... %.5f.\n'
                   % (len(ms), his[0][1]['hi'], *his[0][0][:3], his[-1][1]['hi'], *his[-1][0][:3],
                      max(m['lo'] for m in ms.values()),
                      '%s %d °C %.1f V' % max(ms.items(), key=lambda kv: kv[1]['lo'])[0][:3],
                      max(m['eid01'] for m in ms.values()) * 1e3,
                      min(m['G'] for m in ms.values()), max(m['G'] for m in ms.values())))
    if 'schematic' in allms and 'pex' in allms:
        a, b = allms['schematic'], allms['pex']
        ks = [k for k in a if k in b]
        out.append('\nSchematic vs magic PEX over the %d common runs: max |diff| Vin_max %.2f mV, Vin_min %.2f mV, '
                   'gain %.1e, max over pad -0.3 ... 1.4 V of |diff of the error vs ideal| %.3f mV.\n'
                   % (len(ks), max(abs(a[k]['hi'] - b[k]['hi']) for k in ks) * 1e3,
                      max(abs(a[k]['lo'] - b[k]['lo']) for k in ks) * 1e3, max(abs(a[k]['G'] - b[k]['G']) for k in ks),
                      max(np.abs(a[k]['err_id'] - b[k]['err_id'])[a[k]['pad'] <= 1.4].max() for k in ks) * 1e3))
    (dest / 'tables' / f'{group}.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n<!-- generated by dc_curves/s2d.py, do not edit -->\n' + '\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
