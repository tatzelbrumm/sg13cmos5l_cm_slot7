#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Collect the per-iteration results of pad_ref_rb's CACE mm_params group (collate: iterations) into a CSV and print
statistics. CACE 2.11 nests the iterations one level deeper (parameters/mm_params/run_0/run_<k>/), which the design
repository's cace_to_csv.py (one level) does not find: that is why its committed mm_params.csv has a header only.
Usage: mc_collect.py <mm_params_run_folder> <out.csv> [<stats.csv>]"""
import csv, glob, os, re, sys, statistics as st
import yaml

def main(rundir, out, stats=None):
    rows = []
    for f in glob.glob(os.path.join(rundir, '**', '*.data'), recursive=True):
        d = os.path.dirname(f)
        c = yaml.safe_load(open(os.path.join(d, 'conditions.yaml')))
        v = open(f).read().split()
        if len(v) != 3: continue
        rows.append((int(c['iterations']), c.get('corner_mos'), c.get('temp'), float(v[0]), float(v[1]), float(v[2])))
    rows.sort()
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['iterations', 'corner_mos', 'temp', 'Vcm[V]', 'Vref[V]', 'Ib[A]'])
        for r in rows: w.writerow(r)
    print('%d runs -> %s' % (len(rows), out))
    res = []
    for name, i in (('Vcm[V]', 3), ('Vref[V]', 4), ('Ib[A]', 5)):
        x = [r[i] for r in rows]
        m, s = st.mean(x), st.stdev(x)
        res.append([name, len(x), '%.6g' % m, '%.4g' % s, '%.6g' % min(x), '%.6g' % max(x)])
        print('%-8s n=%d mean=%.6g sigma=%.4g min=%.6g max=%.6g' % (name, len(x), m, s, min(x), max(x)))
    if stats:
        with open(stats, 'w', newline='') as fh:
            w = csv.writer(fh); w.writerow(['quantity', 'n', 'mean', 'sigma', 'min', 'max']); w.writerows(res)

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    main(*sys.argv[1:])
