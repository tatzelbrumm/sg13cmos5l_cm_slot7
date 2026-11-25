# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for the AC / transient / noise curves: loading the collected curves, scalar extraction with the
CACE testbench definitions, plot style (the colors / line styles / labels of ../dc_curves/common.py)."""
import csv
import gzip
import os
from collections import OrderedDict

import numpy as np

import importlib.util  # noqa: E402

# the plot style, colors, labels and save() of ../dc_curves/common.py (same names, loaded under another module name)
_spec = importlib.util.spec_from_file_location(
    'dc_common', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'dc_curves', 'common.py'))
_dc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_dc)
LABEL, VIEWNAME, CORNERS, COLOR, LS, style, md_table, plt = (_dc.LABEL, _dc.VIEWNAME, _dc.CORNERS, _dc.COLOR, _dc.LS,
                                                             _dc.style, _dc.md_table, _dc.plt)

KEYS = ['corner_mos', 'temp', 'vdd', 'vref', 'vcm', 'vicm', 'vterm', 'rload', 'cload', 'sel']
VLS = {'schematic': '-', 'pex': '-.', 'klayout': ':'}
TEMPLS = LS
LOADCOLOR = {'open': '#2a78d6', '10p': '#1baf7a', '100p': '#eb6834', '300p': '#eda100', '1n': '#e87ba4'}


def save(fig, path, svg_max=60e3):
    """PNG 150 dpi; SVG too if it stays below svg_max bytes (../dc_curves/common.save); then the PNG is re-encoded
    with an adaptive 256-color palette (no dithering) to stay well below 300 kB (folder size budget)."""
    _dc.save(fig, path, svg=True, svg_max=svg_max)
    from PIL import Image, PngImagePlugin
    im = Image.open(path + '.png').convert('RGB')
    meta = PngImagePlugin.PngInfo()
    meta.add_text('Copyright', '2026 Christoph Maier, Apache-2.0')
    im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
        path + '.png', optimize=True, pnginfo=meta)


def _f(x):
    try:
        return float(x)
    except ValueError:
        return None


def load(path):
    """collected curve file -> OrderedDict run -> {'cond': dict, <column>: np.array}"""
    runs = OrderedDict()
    with gzip.open(path, 'rt') as f:
        r = csv.reader(f)
        head = next(r)
        cols = head[1 + len(KEYS):]
        rows = {}
        for row in r:
            rows.setdefault(int(row[0]), []).append(row)
    for n, rr in rows.items():
        c = dict(zip(KEYS, rr[0][1:1 + len(KEYS)]))
        cond = {'corner_mos': c['corner_mos'], 'temp': int(float(c['temp'])) if c['temp'] else None}
        for k in KEYS[2:]:
            cond[k] = _f(c[k]) if c[k] not in ('', 'None') else None
        a = np.array([[float(x) for x in row[1 + len(KEYS):]] for row in rr])
        d = {'cond': cond}
        d.update({k: a[:, i] for i, k in enumerate(cols)})
        runs[n] = d
    return runs


def scalars(path):
    """<group>.scalars.csv -> OrderedDict run -> {'cond': ..., 'data': [floats], 'ntot': [floats]}"""
    out = OrderedDict()
    with open(path) as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            c = dict(zip(KEYS, row[1:1 + len(KEYS)]))
            cond = {'corner_mos': c['corner_mos'], 'temp': int(float(c['temp'])) if c['temp'] else None}
            for k in KEYS[2:]:
                cond[k] = _f(c[k]) if c[k] not in ('', 'None') else None
            nd = int(row[1 + len(KEYS)])
            vals = [float(x) for x in row[2 + len(KEYS):]]
            out[int(row[0])] = {'cond': cond, 'data': vals[:nd], 'ntot': vals[nd:]}
    return out


def committed(path):
    """committed CACE result CSV -> list of dicts (header names without the [unit] suffix; values as str)"""
    with open(path) as f:
        r = csv.reader(l for l in f if not l.startswith('#'))
        head = [h.split('[')[0] for h in next(r)]
        return [dict(zip(head, row)) for row in r]


def find(runs, **kw):
    """the runs whose conditions match kw (floats compared with a relative tolerance)"""
    res = []
    for n, d in runs.items():
        ok = True
        for k, v in kw.items():
            x = d['cond'].get(k)
            if isinstance(v, str) or x is None or v is None:
                ok &= (x == v)
            else:
                ok &= abs(x - v) <= 1e-9 * max(abs(v), 1e-30)
        if ok:
            res.append(d)
    return res


def logx_interp(f, y, f0):
    return float(np.interp(np.log10(f0), np.log10(f), y))


def first_fall(f, y, level, i0=0):
    """first frequency above f[i0] where y falls through level (linear interpolation in log f), else nan"""
    for i in range(i0, len(f) - 1):
        if y[i] >= level > y[i + 1]:
            lf = np.log10(f[i]) + (level - y[i]) * (np.log10(f[i + 1]) - np.log10(f[i])) / (y[i + 1] - y[i])
            return 10 ** lf
    return float('nan')


def cross_times(t, y, level):
    """all times where y crosses level (linear interpolation)"""
    s = np.sign(y - level)
    idx = np.where(s[:-1] * s[1:] < 0)[0]
    return [t[i] + (level - y[i]) * (t[i + 1] - t[i]) / (y[i + 1] - y[i]) for i in idx]


def first_cross(t, y, level, rising=True, t0=0.0, t1=np.inf):
    for i in range(len(t) - 1):
        if t[i] < t0 or t[i + 1] > t1:
            continue
        if (rising and y[i] < level <= y[i + 1]) or (not rising and y[i] > level >= y[i + 1]):
            return t[i] + (level - y[i]) * (t[i + 1] - t[i]) / (y[i + 1] - y[i])
    return float('nan')


def last_cross(t, y, level, t0=0.0, t1=np.inf):
    """last time in [t0, t1] where y crosses level (ngspice 'when y=level cross=last')"""
    m = (t >= t0) & (t <= t1)
    c = cross_times(t[m], y[m], level)
    return c[-1] if c else float('nan')


def integrate_psd(f, vn, f0=None, f1=None):
    """sqrt of the integral of vn^2 df (trapezoid in f), vn in V/rtHz"""
    m = np.ones_like(f, bool)
    if f0 is not None:
        m &= f >= f0 * (1 - 1e-9)
    if f1 is not None:
        m &= f <= f1 * (1 + 1e-9)
    return float(np.sqrt(np.trapezoid(vn[m] ** 2, f[m])))


def pvt_label(d):
    c = d['cond']
    return f"{c['corner_mos']} {c['temp']} °C"


def title(fig, ax, text, view):
    """suptitle: the view label, then the conditions, wrapped to the figure width; then tight_layout below it"""
    import textwrap
    lab = {'schematic': LABEL['schematic'], 'pex': LABEL['pex'], 'both': 'IHP sg13cmos5l simulation (schematic | magic PEX)',
           'slot3': 'IHP sg13cmos5l simulation (pads: schematic | magic PEX | KLayout-extracted)'}[view]
    w = fig.get_size_inches()
    width = int(w[0] * 14.5)
    lines = [lab] + [x for part in text.split('\n') for x in textwrap.wrap(part, width)]
    fig.suptitle('\n'.join(lines), fontsize=9, y=0.995, va='top')
    fig.tight_layout()  # matplotlib >= 3.x leaves room for the suptitle itself
