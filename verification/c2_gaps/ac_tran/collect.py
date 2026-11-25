#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Collect the wrdata curves of one CACE ac_tran group into gzipped CSVs (work folder only, not committed).

Usage: collect.py <RUN_dir> <group> <out_prefix>
Each parameters/<group>/run_*/ holds conditions.yaml, the original <testbench>_<N>.data (CACE scalars) and the
appended curve files <testbench>_<N>.at_<suffix> (wrdata, single scale, vector names) / .at_ntot (two numbers).
Writes <out_prefix>.<suffix>.csv.gz (run, conditions, curve columns), <out_prefix>.scalars.csv (run, conditions,
the .data values as v0 v1 ..., the .at_ntot values) and <out_prefix>.failed.txt (runs with a missing file).
"""
import csv
import glob
import gzip
import os
import re
import sys

import yaml

KEYS = ['corner_mos', 'temp', 'vdd', 'vref', 'vcm', 'vicm', 'vterm', 'rload', 'cload', 'sel']


def main(rundir, group, out):
    runs = sorted(glob.glob(os.path.join(rundir, 'parameters', group, 'run_*')),
                  key=lambda p: int(re.search(r'run_(\d+)', p).group(1)))
    writers, files, failed, scal = {}, {}, [], []
    sfx_all = set()
    for r in runs:
        sfx_all |= {f.rsplit('.', 1)[1] for f in glob.glob(os.path.join(r, '*.at_*')) if not f.endswith('.at_ntot')}
    for n, r in enumerate(runs):
        c = yaml.safe_load(open(os.path.join(r, 'conditions.yaml')))
        cond = [c.get(k, '') for k in KEYS]
        data = glob.glob(os.path.join(r, '*.data'))
        dv = open(data[0]).read().split() if data and os.path.getsize(data[0]) else []
        nt = glob.glob(os.path.join(r, '*.at_ntot'))
        ntv = open(nt[0]).read().split() if nt else []
        scal.append([n] + cond + [len(dv)] + dv + ntv)
        miss = []
        for s in sorted(sfx_all):
            fs = glob.glob(os.path.join(r, f'*.{s}'))
            if not fs or os.path.getsize(fs[0]) == 0:
                miss.append(s)
                continue
            lines = open(fs[0]).read().split('\n')
            head = lines[0].split()
            if s not in writers:
                files[s] = gzip.open(f'{out}.{s}.csv.gz', 'wt', newline='')
                writers[s] = csv.writer(files[s])
                writers[s].writerow(['run'] + KEYS + head)
            for l in lines[1:]:
                t = l.split()
                if len(t) == len(head):
                    writers[s].writerow([n] + cond + t)
        if miss or not dv:
            failed.append(f'{os.path.basename(r)} {c} missing: {miss}{"" if dv else " .data"}')
    for f in files.values():
        f.close()
    with open(f'{out}.scalars.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['run'] + KEYS + ['ndata', 'data...'])
        w.writerows(scal)
    with open(f'{out}.failed.txt', 'w') as f:
        f.write(''.join(x + '\n' for x in failed))
    print(f'{group}: {len(runs)} runs, curves {sorted(sfx_all)} -> {out}.*' + (f' (failed: {len(failed)})' if failed else ''))
    for x in failed:
        print('FAILED', x, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
