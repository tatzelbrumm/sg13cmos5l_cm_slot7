#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""S2D input range vs vref and vcm (the range_params grid), IHP sg13cmos5l simulation (schematic).

Usage: vrefvcm.py <work_out_dir> <dest_dir>   (reads <work_out_dir>/schematic/s2d_vrefvcm.csv.gz)

Grid: vref 0.5 / 0.8 / 1.2 / 1.65 V x vcm 1.0 / 1.2 / 1.4 / 1.65 V x iovdd 3.0 / 3.3 V x MOS ss / tt / ff x
-40 / 27 / 125 C (range_params: vref, vcm, ss / tt / ff, -40 / 125 C at 3.0 V; extended here by 27 C and 3.3 V).
Range per run: as s2d.py (|error from the small-signal line| < 1 mV, input-referred, contiguous around pad = vref;
pad swept -0.3 ... 3.3 V). Plotted per (vref, vcm, iovdd): the guaranteed range over the 9 corner / temperature runs
(highest low end ... lowest high end) as a bar, and tt 27 C as a marker pair.
"""
import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import LABEL, load, md_table, plt, save, style  # noqa: E402
from s2d import metrics  # noqa: E402

VREFS = [0.5, 0.8, 1.2, 1.65]
VCMS = [1.0, 1.2, 1.4, 1.65]
VCOL = {1.0: '#2a78d6', 1.2: '#eb6834', 1.4: '#1baf7a', 1.65: '#6250d6'}


def main(wout, dest):
    wout, dest = Path(wout), Path(dest)
    style()
    p = wout / 'schematic' / 's2d_vrefvcm.csv.gz'
    runs = load(p)
    ms = {k: metrics(d, k[3]) for k, d in runs.items()}
    vdds = sorted({k[2] for k in ms})
    fig, axs = plt.subplots(1, len(vdds), figsize=(7.6, 4.8), sharey=True, squeeze=False)
    rows, tab = [], []
    for ax, vdd in zip(axs[0], vdds):
        for i, vref in enumerate(VREFS):
            for j, vcm in enumerate(VCMS):
                sub = {k: m for k, m in ms.items() if k[2] == vdd and k[3] == vref and k[4] == vcm}
                if not sub:
                    continue
                lo = max(m['lo'] for m in sub.values())
                hi = min(m['hi'] for m in sub.values())
                t = next((m for k, m in sub.items() if k[:2] == ('tt', 27)), None)
                x = i + (j - 1.5) * 0.17
                if hi > lo:
                    ax.plot([x, x], [lo, hi], color=VCOL[vcm], lw=3, solid_capstyle='butt')
                else:
                    ax.plot([x], [vref], marker='x', color=VCOL[vcm], ms=6)
                if t is not None:
                    ax.plot([x, x], [t['lo'], t['hi']], ls='none', marker='_', color='#0b0b0b', ms=7, mew=1.2)
                rows.append([vdd, vref, vcm, len(sub), '%.4f' % lo, '%.4f' % hi,
                             '%.4f' % t['lo'] if t else '', '%.4f' % t['hi'] if t else ''])
            ax.plot([i - 0.4, i + 0.4], [vref, vref], color='#8a8984', lw=0.8, ls='-.')
        ax.set_xticks(range(len(VREFS)))
        ax.set_xticklabels(['%.2f' % v for v in VREFS])
        ax.set_xlabel('vref [V]')
        ax.set_title('iovdd %.1f V' % vdd, fontsize=8.5)
        ax.grid(axis='x', visible=False)
        ax.set_ylim(-0.35, 3.0)
    axs[0][0].set_ylabel('pad input range [V] (1 mV criterion)')
    h = [plt.Line2D([], [], color=VCOL[v], lw=3, label='vcm %.2f V' % v) for v in VCMS]
    h += [plt.Line2D([], [], ls='none', marker='_', color='#0b0b0b', ms=7, mew=1.2, label='tt 27 °C ends'),
          plt.Line2D([], [], ls='none', marker='x', color='#52514e', label='no common range'),
          plt.Line2D([], [], color='#8a8984', lw=0.8, ls='-.', label='pad = vref')]
    fig.legend(handles=h, loc='lower center', ncol=4)
    fig.suptitle('S2D pad: linear input range vs vref and vcm, %s\nbar = range met at all of ss / tt / ff × −40 / 27 / '
                 '125 °C (|error from small-signal line| < 1 mV, input-referred); iref 5 µA'
                 % LABEL['schematic'], fontsize=9.5)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    save(fig, str(dest / 'plots' / 's2d_vrefvcm_range'))
    head = ['vdd', 'vref', 'vcm', 'runs', 'worst_lo_V', 'worst_hi_V', 'tt27_lo_V', 'tt27_hi_V']
    with open(dest / 'csv' / 's2d_vrefvcm_summary.csv', 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                '# S2D input range vs vref / vcm, IHP sg13cmos5l simulation (schematic); worst = over ss / tt / ff x '
                '-40 / 27 / 125 C; vrefvcm.py\n')
        csv.writer(f).writerows([head] + rows)
        # per run as well (small)
    with open(dest / 'csv' / 's2d_vrefvcm_runs.csv', 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                '# S2D input range per run vs vref / vcm, IHP sg13cmos5l simulation (schematic); vrefvcm.py\n')
        w = csv.writer(f)
        w.writerow(['corner_mos', 'temp', 'vdd', 'vref', 'vcm', 'Gain', 'INL_pm0.5V_mV', 'Vcm_err_mV', 'Vin_min_V',
                    'Vin_max_V'])
        for k, m in ms.items():
            w.writerow([k[0], k[1], k[2], k[3], k[4], '%.5f' % m['G'], '%.4f' % (m['inl05'] * 1e3),
                        '%.2f' % (m['vc0'] * 1e3), '%.4f' % m['lo'], '%.4f' % m['hi']])
    for vdd in vdds:
        hd = ['vref \\ vcm'] + ['%.2f V' % v for v in VCMS]
        rr = []
        for vref in VREFS:
            r = ['%.2f V' % vref]
            for vcm in VCMS:
                x = next((x for x in rows if x[0] == vdd and x[1] == vref and x[2] == vcm), None)
                r.append('n/a' if x is None else ('%s ... %s' % (x[4], x[5]) if float(x[5]) > float(x[4])
                                                  else 'none'))
            rr.append(r)
        tab.append('\n#### S2D input range vs vref / vcm, iovdd %.1f V, %s\n\nPad range [V] met at all of ss / tt / ff '
                   '× −40 / 27 / 125 °C (1 mV criterion).\n' % (vdd, LABEL['schematic']))
        tab.append(md_table(hd, rr))
    (dest / 'tables' / 's2d_vrefvcm.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n<!-- generated by dc_curves/vrefvcm.py, do not edit -->\n' + '\n'.join(tab) + '\n')
    print('\n'.join(tab))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
