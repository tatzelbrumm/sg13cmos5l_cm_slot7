#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Cross-check the DC-curve summaries against the committed CACE results of the design repository (commit 91a7da8b).

Usage: crosscheck.py <design_tree> <dest_dir> [<work_out_dir>]  -> <dest_dir>/tables/crosscheck.md
With <work_out_dir>: also the D2S rshunt check (group d2s_rshunt_chk, schematic, with and without rshunt=1e12).
S2D: Vin_min / Vin_max of window_params (schematic and _pex; vref 0.5 V; CACE sweeps the pad from 0 V in 10 mV steps,
     so its Vin_min is 0 where the criterion holds at 0 V) against the same criterion on the 2 mV sweeps here
     (Vin_min here clipped to >= 0 for the comparison).
D2S: Vout_min / Vout_max of drive_params (vd = -3 / +3 V) against the pad voltage at vd = -3 / +3 V here.
D2S: Gain and INL (deviation from the small-signal line over vd = +-1 V, gain from +-0.2 V) of dc_params (3.3 / 3.6 V)
     and dc_3v0_params (3.0 V), schematic only (no committed PEX CSV in the design repository; ../d2s_pex/csv has the
     PEX dc_params of this repository), against the same quantities on the 5 mV sweeps here.
"""
import csv
import sys
from pathlib import Path


def rd(p):
    with open(p) as f:
        return list(csv.DictReader(l for l in f if not l.startswith('#')))


def rshunt_check(wout):
    """D2S: Gain, offset and INL (+-1 V) of the same sweeps with and without ngspice rshunt=1e12 (schematic)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import load
    from d2s import metrics
    a, b = wout / 'schematic' / 'd2s_rshunt_chk.csv.gz', wout / 'schematic_norshunt' / 'd2s_rshunt_chk.csv.gz'
    if not (a.exists() and b.exists()):
        return []
    ma = {k[:3]: metrics(d) for k, d in load(a).items()}
    mb = {k[:3]: metrics(d) for k, d in load(b).items()}
    out = ['\n### D2S: effect of the solver aid rshunt = 1e12 (schematic, vd 0 ... +-1 V, same sweep otherwise)\n',
           '| corner | T [°C] | iovdd [V] | INL with / without [mV] | gain with / without | offset with / without [mV] |',
           '|---|---|---|---|---|---|']
    for k in sorted(set(ma) | set(mb)):
        x, y = ma.get(k), mb.get(k)
        f = lambda m, q, s=1, fm='%.3f': (fm % (m[q] * s)) if m is not None else 'failed'
        out.append(f'| {k[0]} | {k[1]} | {k[2]} | {f(x, "inl", 1e3)} / {f(y, "inl", 1e3)} | '
                   f'{f(x, "G", 1, "%.5f")} / {f(y, "G", 1, "%.5f")} | {f(x, "vo0", 1e3)} / {f(y, "vo0", 1e3)} |')
    return out


def main(tree, dest, wout=None):
    tree, dest = Path(tree), Path(dest)
    out = []
    res = tree / 'macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results'
    s = dest / 'csv' / 's2d_grid_summary.csv'
    if s.exists():
        mine = {(r['view'], r['corner_mos'], int(float(r['temp'])), float(r['vdd'])): r for r in rd(s)}
        out.append('### S2D window_params (committed CACE) vs this sweep\n')
        out.append('| view | runs compared | max abs diff Vin_max [mV] | max abs diff Vin_min (>= 0) [mV] | '
                   'committed Vin_max min ... max [V] | here min ... max [V] |')
        out.append('|---|---|---|---|---|---|')
        for view, sub in (('schematic', 'sg13cmos5l_IOPadSingle2Diff'), ('pex', 'sg13cmos5l_IOPadSingle2Diff_pex')):
            n, dmax, dmin, cv, hv = 0, 0, 0, [], []
            for r in rd(res / sub / 'window_params.csv'):
                k = (view, r['corner_mos'], int(float(r['temp'])), float(r['vdd']))
                if k not in mine:
                    continue
                m = mine[k]
                n += 1
                dmax = max(dmax, abs(float(m['Vin_max_V']) - float(r['Vin_max[V]'])))
                dmin = max(dmin, abs(max(float(m['Vin_min_V']), 0) - float(r['Vin_min[V]'])))
                cv.append(float(r['Vin_max[V]'])); hv.append(float(m['Vin_max_V']))
            if n:
                out.append(f'| {view} | {n} | {dmax*1e3:.2f} | {dmin*1e3:.2f} | {min(cv):.4f} ... {max(cv):.4f} | '
                           f'{min(hv):.4f} ... {max(hv):.4f} |')
    s = dest / 'csv' / 's2d_vrefvcm_runs.csv'
    if s.exists():
        mine = {(r['corner_mos'], int(float(r['temp'])), float(r['vdd']), float(r['vref']), float(r['vcm'])): r
                for r in rd(s)}
        n, dg, di, ci, hi = 0, 0, 0, [], []
        for r in rd(res / 'sg13cmos5l_IOPadSingle2Diff' / 'range_params.csv'):
            k = (r['corner_mos'], int(float(r['temp'])), float(r['vdd']), float(r['vref']), float(r['vcm']))
            if k not in mine:
                continue
            m = mine[k]
            n += 1
            dg = max(dg, abs(float(m['Gain']) - float(r['Gain[]'])))
            # the committed CSV column says mV but holds V (cace_to_csv.py writes the testbench's SI value)
            di = max(di, abs(float(m['INL_pm0.5V_mV']) - float(r['INL[mV]']) * 1e3))
            ci.append(float(r['INL[mV]']) * 1e3); hi.append(float(m['INL_pm0.5V_mV']))
        out.append('\n### S2D range_params (committed CACE, schematic; INL over u = +-0.5 V) vs this sweep\n')
        out.append('| runs compared | max abs diff Gain | max abs diff INL [mV] | committed INL min ... max [mV] | '
                   'here INL min ... max [mV] |')
        out.append('|---|---|---|---|---|')
        if n:
            out.append(f'| {n} | {dg:.5f} | {di:.3f} | {min(ci):.3f} ... {max(ci):.3f} | {min(hi):.3f} ... {max(hi):.3f} |')
    resd = tree / 'macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single'
    s = dest / 'csv' / 'd2s_grid_summary.csv'
    if s.exists():
        mine = {(r['view'], r['corner_mos'], int(float(r['temp'])), float(r['vdd'])): r for r in rd(s)}
        out.append('\n### D2S dc_params / dc_3v0_params (committed CACE, schematic) vs this sweep\n')
        out.append('| view here | runs compared | max abs diff Gain | max abs diff INL [mV] | committed INL min ... max [mV] '
                   '| here INL min ... max [mV] |')
        out.append('|---|---|---|---|---|---|')
        for view in ('schematic', 'pex'):
            n, dg, di, ci, hi = 0, 0, 0, [], []
            for f in ('dc_params.csv', 'dc_3v0_params.csv'):
                for r in rd(resd / f):
                    k = (view, r['corner_mos'], int(float(r['temp'])), float(r['vdd']))
                    if k not in mine:
                        continue
                    m = mine[k]
                    n += 1
                    dg = max(dg, abs(float(m['Gain']) - float(r['Gain[]'])))
                    # the committed CSV column says mV but holds V (cace_to_csv.py writes the testbench's SI value)
                    di = max(di, abs(float(m['INL_pm1V_mV']) - float(r['INL[mV]']) * 1e3))
                    ci.append(float(r['INL[mV]']) * 1e3); hi.append(float(m['INL_pm1V_mV']))
            if n:
                out.append(f'| {view} | {n} | {dg:.5f} | {di:.3f} | {min(ci):.3f} ... {max(ci):.3f} | '
                           f'{min(hi):.3f} ... {max(hi):.3f} |')
        out.append('\n### D2S drive_params (committed CACE, schematic; vd = -3 / +3 V, 1 kOhm to 1.65 V, iovdd 3.3 V) vs '
                   'this sweep\n')
        out.append('| view here | runs compared | max abs diff Vout_min [mV] | max abs diff Vout_max [mV] | committed '
                   'Vout_min ... Vout_max [V] | here [V] |')
        out.append('|---|---|---|---|---|---|')
        for view in ('schematic', 'pex'):
            n, d1, d2, c, h = 0, 0, 0, [], []
            for r in rd(resd / 'drive_params.csv'):
                k = (view, r['corner_mos'], int(float(r['temp'])), 3.3)
                if k not in mine:
                    continue
                m = mine[k]
                n += 1
                d1 = max(d1, abs(float(m['pad_at_vd_m3V']) - float(r['Vout_min[V]'])))
                d2 = max(d2, abs(float(m['pad_at_vd_p3V']) - float(r['Vout_max[V]'])))
                c += [float(r['Vout_min[V]']), float(r['Vout_max[V]'])]
                h += [float(m['pad_at_vd_m3V']), float(m['pad_at_vd_p3V'])]
            if n:
                out.append(f'| {view} | {n} | {d1*1e3:.2f} | {d2*1e3:.2f} | {min(c):.4f} ... {max(c):.4f} | '
                           f'{min(h):.4f} ... {max(h):.4f} |')
        out.append('\n(pex rows: this repository\'s PEX view against the committed *schematic* CSV, i.e. the '
                   'difference includes the layout effect; ../d2s_pex/csv/dc_params_pex_rshunt1e12.csv is the CACE PEX '
                   'reference.)')
    if wout:
        out += rshunt_check(Path(wout))
    (dest / 'tables' / 'crosscheck.md').write_text('<!--\nSPDX-FileCopyrightText: 2026 Christoph Maier\nSPDX-License-Identifier: Apache-2.0\n-->\n<!-- generated by dc_curves/crosscheck.py, do not edit -->\n' + '\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        sys.exit(__doc__)
    main(*sys.argv[1:])
