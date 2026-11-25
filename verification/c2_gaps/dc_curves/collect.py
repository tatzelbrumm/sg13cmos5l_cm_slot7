#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Collect the wrdata sweeps of one CACE DC-curve group into one gzipped CSV (work folder only, not committed).

Usage: collect.py <RUN_dir> <group> <out.csv.gz>
Each parameters/<group>/run_*/ holds conditions.yaml and <testbench>_<N>.sweep (wrdata, single scale, vector names),
or the two branches <testbench>_<N>.sweep_n / .sweep_p (merged here).
Output columns: run, the group's varying conditions (corner_mos, temp, vdd, vref, vcm, ...), then the sweep columns.
Runs without a sweep (ngspice failed) are listed on stderr and in <out>.failed.txt.
"""
import csv
import glob
import gzip
import os
import re
import sys

import yaml

KEYS = ['corner_mos', 'temp', 'vdd', 'vref', 'vcm', 'vicm', 'vterm', 'rload']


def main(rundir, group, out):
    runs = sorted(glob.glob(os.path.join(rundir, 'parameters', group, 'run_*')),
                  key=lambda p: int(re.search(r'run_(\d+)', p).group(1)))
    failed, n = [], 0
    with gzip.open(out, 'wt', newline='') as f:
        w = None
        for r in runs:
            c = yaml.safe_load(open(os.path.join(r, 'conditions.yaml')))
            # one sweep (.sweep) or two branches from the operating point (.sweep_n, .sweep_p): merged, sorted by the
            # swept value, duplicates (the common start point) dropped
            sw = glob.glob(os.path.join(r, '*.sweep')) or sorted(glob.glob(os.path.join(r, '*.sweep_[np]')))
            exp = 1 if sw and sw[0].endswith('.sweep') else 2
            if len(sw) != exp or any(os.path.getsize(x) == 0 for x in sw):
                failed.append(f'{os.path.basename(r)} {c}')
                continue
            data, head = {}, None
            for x in sw:
                lines = open(x).read().split('\n')
                head = lines[0].split()
                for l in lines[1:]:
                    t = l.split()
                    if len(t) == len(head):
                        data[round(float(t[0]), 9)] = t
            if w is None:
                w = csv.writer(f)
                w.writerow(['run'] + KEYS + head)
            cond = [c.get(k, '') for k in KEYS]
            for x in sorted(data):
                w.writerow([n] + cond + data[x])
            n += 1
    with open(out + '.failed.txt', 'w') as f:
        f.write(''.join(x + '\n' for x in failed))
    print(f'{group}: {n} of {len(runs)} runs -> {out}' + (f' (failed: {len(failed)})' if failed else ''))
    for x in failed:
        print('FAILED', x, file=sys.stderr)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
