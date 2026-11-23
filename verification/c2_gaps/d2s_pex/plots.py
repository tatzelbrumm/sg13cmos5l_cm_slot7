#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Per-corner plots of schematic vs PEX for sg13cmos5l_IOPadDiff2Single: f3dB (ac_params), INL (dc_params), and
quiescent output current IqP (dc_params). Usage: plots.py <schematic_csv_dir> <pex_csv_dir> <out_dir>"""
import csv, os, sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def load(path):
    rows = list(csv.DictReader(l for l in open(path) if not l.startswith('#')))
    return rows

def plot(sd, pd, od, group, col, scale, ylabel, fname, title):
    ps, pp = os.path.join(sd, group + '.csv'), os.path.join(pd, group + '.csv')
    if not (os.path.exists(ps) and os.path.exists(pp)):
        print('skip', fname)
        return
    s, p = load(ps), load(pp)
    keys = [k for k in s[0] if '[' not in k and k in ('corner_mos', 'temp', 'vdd')]
    lab = lambda r: '/'.join(str(r[k]) for k in keys)
    labels = [lab(r) for r in s]
    pm = {lab(r): r for r in p}
    def v(r):
        try:
            return float(r[col]) * scale
        except (ValueError, TypeError, KeyError):
            return None
    xs = range(len(labels))
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=90)
    ax.plot(xs, [v(r) for r in s], 'o', color='#1f5fa8', label='schematic (committed CSV)')
    ax.plot(xs, [v(pm[l]) if l in pm else None for l in labels], 'x', color='#c4501b', ms=8, label='PEX (magic C-coupled)')
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, rotation=60, fontsize=7)
    ax.set_xlabel('/'.join(keys))
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=9)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(od, fname))
    plt.close(fig)
    print('wrote', fname)

def main(sd, pd, od):
    t = 'IHP sg13cmos5l post-layout (magic PEX) simulation vs schematic: sg13cmos5l_IOPadDiff2Single'
    plot(sd, pd, od, 'ac_params', 'f3dB[MHz]', 1e-6, 'f3dB / MHz', 'f3dB_per_corner.png', t + ', ac_params')
    plot(sd, pd, od, 'dc_params', 'INL[mV]', 1e3, 'INL / mV', 'inl_per_corner.png', t + ', dc_params')
    plot(sd, pd, od, 'dc_params', 'IqP[A]', 1e6, 'IqP / uA', 'iqp_per_corner.png', t + ', dc_params')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
