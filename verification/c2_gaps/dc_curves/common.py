# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for the DC-curve tables and plots: loading the collected sweeps, range criterion, plot style."""
import csv
import gzip
from collections import OrderedDict

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

LABEL = {'schematic': 'IHP sg13cmos5l simulation (schematic)', 'pex': 'IHP sg13cmos5l simulation (magic PEX)',
         'klayout': 'IHP sg13cmos5l simulation (KLayout-extracted pads, as the designer\'s tier-1 deck)'}
VIEWNAME = {'schematic': 'schematic', 'pex': 'magic PEX (C-coupled)', 'klayout': 'KLayout-extracted'}
# one fixed color per MOS corner (validated categorical order), line style per temperature
CORNERS = ['tt', 'ss', 'ff', 'sf', 'fs']
COLOR = {'tt': '#2a78d6', 'ss': '#eb6834', 'ff': '#1baf7a', 'sf': '#eda100', 'fs': '#e87ba4'}
LS = {-40: ':', 27: '-', 125: '--'}
VCOLOR = {3.0: '#eb6834', 3.3: '#2a78d6', 3.6: '#1baf7a'}


def style():
    plt.rcParams.update({'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 9, 'axes.titlesize': 9.5,
                         'axes.grid': True, 'grid.color': '#d8d8d4', 'grid.linewidth': 0.6, 'axes.edgecolor': '#52514e',
                         'axes.labelcolor': '#0b0b0b', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                         'lines.linewidth': 1.4, 'legend.fontsize': 7.5, 'legend.framealpha': 0.9,
                         'svg.fonttype': 'none', 'figure.facecolor': 'white'})


def load(path):
    """-> OrderedDict key -> dict of numpy arrays; key = (corner, temp, vdd, vref, vcm, vicm, vterm, rload) as typed."""
    runs = OrderedDict()
    with gzip.open(path, 'rt') as f:
        r = csv.reader(f)
        head = next(r)
        keys = head[1:9]
        cols = head[9:]
        rows = {}
        for row in r:
            rows.setdefault(int(row[0]), []).append(row)
    for n, rr in rows.items():
        c = rr[0][1:9]
        key = (c[0], int(float(c[1])), float(c[2]),
               *(float(x) if x not in ('', 'None') else None for x in c[3:8]))
        a = np.array([[float(x) for x in row[9:]] for row in rr])
        runs[key] = {k: a[:, i] for i, k in enumerate(cols)}
    return runs


def ss_line(x, y, x0=0.0, dx=0.1):
    """Small-signal line of y(x) as in the CACE tb_dc: slope from x0 +- dx, value at x0."""
    yp, ym, y0 = np.interp([x0 + dx, x0 - dx, x0], x, y)
    return (yp - ym) / (2 * dx), y0


def contiguous_range(x, err, lim, x0=0.0):
    """Contiguous range of x around x0 where |err| < lim; ends linearly interpolated at |err| = lim.
    Returns (lo, hi, lo_clipped, hi_clipped): *_clipped = True if the criterion holds up to the end of the sweep."""
    a = np.abs(err)
    i0 = int(np.argmin(np.abs(x - x0)))
    if a[i0] >= lim:
        return np.nan, np.nan, False, False
    i = i0
    while i + 1 < len(x) and a[i + 1] < lim:
        i += 1
    if i + 1 < len(x):
        hi, hic = x[i] + (lim - a[i]) * (x[i + 1] - x[i]) / (a[i + 1] - a[i]), False
    else:
        hi, hic = x[i], True
    i = i0
    while i - 1 >= 0 and a[i - 1] < lim:
        i -= 1
    if i - 1 >= 0:
        lo, loc = x[i] + (lim - a[i]) * (x[i - 1] - x[i]) / (a[i - 1] - a[i]), False
    else:
        lo, loc = x[i], True
    return lo, hi, loc, hic


def save(fig, path, svg=True, svg_max=60e3):
    """PNG at 150 dpi; SVG too if it stays below svg_max bytes (otherwise no SVG)."""
    import os
    fig.savefig(path + '.png', metadata={'Copyright': '2026 Christoph Maier, Apache-2.0'})
    if svg:
        fig.savefig(path + '.svg', metadata={'Date': None})
        if os.path.getsize(path + '.svg') > svg_max:
            os.remove(path + '.svg')
        else:
            t = open(path + '.svg').read()
            i = t.index('?>') + 2 if t.startswith('<?xml') else 0
            open(path + '.svg', 'w').write(t[:i] + '\n<!-- SPDX-FileCopyrightText: 2026 Christoph Maier -->\n'
                                           '<!-- SPDX-License-Identifier: Apache-2.0 -->' + t[i:])
    plt.close(fig)


def md_table(head, rows):
    out = ['| ' + ' | '.join(head) + ' |', '|' + '---|' * len(head)]
    out += ['| ' + ' | '.join(str(x) for x in r) + ' |' for r in rows]
    return '\n'.join(out)
