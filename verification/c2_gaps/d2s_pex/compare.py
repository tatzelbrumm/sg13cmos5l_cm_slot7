#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Schematic vs PEX table of sg13cmos5l_IOPadDiff2Single CACE results: min / median / max per quantity, as markdown.

Usage: compare.py <schematic_csv_dir> <pex_csv_dir> <group> [<group> ...] > results_table.md
A column whose header has a [unit] is a quantity, the others are conditions. Values are the CSV values as written by
cace_to_csv.py (SI: Hz, V, A, s, V/s, %, dB, Ohm; the header's display unit, e.g. [MHz], is not applied).
Runs are matched by their condition columns for the per-run change: max |PEX - sch| / |sch| in % over matched runs.
"""
import csv, os, statistics, sys

def load(path):
    rows = list(csv.reader(l for l in open(path) if not l.startswith('#')))
    return rows[0], rows[1:]

def num(x):
    try:
        return float(x)
    except ValueError:
        return None

def f(x):
    return '-' if x is None else '%.4g' % x

def main(sd, pd, groups):
    print('| group | quantity | N sch | sch min | sch median | sch max | N pex | pex min | pex median | pex max | max per-run change % |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for g in groups:
        ps, pp = os.path.join(sd, g + '.csv'), os.path.join(pd, g + '.csv')
        if not os.path.exists(ps) or not os.path.exists(pp):
            print('| %s | (missing %s) |||||||||| ' % (g, 'pex CSV' if os.path.exists(ps) else 'schematic CSV'))
            continue
        hs, rs = load(ps)
        hp, rp = load(pp)
        cond = [i for i, h in enumerate(hs) if '[' not in h]
        key = lambda r: tuple(r[i] for i in cond)
        mp = {key(r): r for r in rp}
        for i, h in enumerate(hs):
            if '[' not in h or h not in hp:
                continue
            j = hp.index(h)
            a = [v for v in (num(r[i]) for r in rs) if v is not None]
            b = [v for v in (num(r[j]) for r in rp) if v is not None]
            ch = []
            for r in rs:
                q = mp.get(key(r))
                if q is None:
                    continue
                x, y = num(r[i]), num(q[j])
                if x is not None and y is not None and x != 0:
                    ch.append(100.0 * (y - x) / abs(x))
            st = lambda v: (min(v), statistics.median(v), max(v)) if v else (None, None, None)
            sa, sb = st(a), st(b)
            mc = max(ch, key=abs) if ch else None
            print('| %s | %s | %d | %s | %s | %s | %d | %s | %s | %s | %s |' % (
                g, h, len(a), *map(f, sa), len(b), *map(f, sb), '-' if mc is None else '%+.3g' % mc))

if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
