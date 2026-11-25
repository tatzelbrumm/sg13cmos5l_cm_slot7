#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Per-run CSV of one CACE group, also for a group collated over Monte Carlo iterations.

CACE 2.11 nests the iterations of a collated group one level deeper (parameters/<group>/run_0/run_<k>/) than the
design repository's scripts/cace/cace_to_csv.py looks (parameters/<group>/run_*/): that is why the committed
mm_params.csv, ac_mm_params.csv and mc_params.csv of the S2D pad have a header only. This reads every *.data file
below parameters/<group>/ (as ../d2s_schematic_rerun/mm_collect.py and ../replica_bias/mc_collect.py).

CSV format as cace_to_csv.py: the group's conditions, then the yaml `variables` in the order of the data file; the
[unit] in the header is the yaml display unit, the values are what the testbench writes (SI: V, A, Hz; dB as dB).
Difference: a `null` variable (written by the testbench, not scored by CACE) is labelled with the name the template's
`echo $&... > ...data` line gives it, as `<name>(unscored)[]`, instead of cace_to_csv.py's `None[]` (which repeats the
last null value in every None column). Rows sorted by iteration. A run whose data file has the wrong number of values
(failed simulation) is left out and counted. Rows in run order (CACE's run_<k> numbers).
Usage: mm_collect.py <cell.yaml> <group> <run_dir> <out.csv> [<templates_dir>]"""
import csv, glob, os, re, sys
import yaml


def echo_names(tdir, template, n):
    try:
        txt = open(os.path.join(tdir, template)).read()
    except OSError:
        return None
    for line in txt.splitlines():
        if line.lstrip().startswith('echo') and '.data' in line:
            names = re.findall(r'\$&(\w+)', line)
            if len(names) == n:
                return names
    return None


def main(ycell, group, rundir, out, tdir=None):
    d = yaml.safe_load(open(ycell))
    g = d['parameters'][group]
    ng = g['tool']['ngspice']
    variables = list(ng['variables'])
    conds = list(g['conditions'])
    si = {'ns': 's', 'ps': 's', 'pA': 'A', 'nA': 'A', 'uA': 'A', 'fC': 'C', 'pC': 'C', 'fW⋅s': 'J', 'pW⋅s': 'J'}
    units = {k: si.get(v.get('unit', ''), v.get('unit', '')) for k, v in g['spec'].items()}
    names = echo_names(tdir, ng['template'], len(variables)) if tdir else None
    labels = []
    for i, v in enumerate(variables):
        if v is None:
            labels.append('%s(unscored)[]' % (names[i] if names else 'col%d' % i))
        else:
            labels.append('%s[%s]' % (v, units.get(v, '')))
    rows, bad = [], 0
    files = sorted(glob.glob(os.path.join(rundir, 'parameters', group, '**', '*.data'), recursive=True),
                   key=lambda p: [int(x) for x in re.findall(r'run_(\d+)', p)])
    leaves = [os.path.dirname(c) for c in glob.glob(os.path.join(rundir, 'parameters', group, '**', 'conditions.yaml'),
                                                    recursive=True)]
    leaves = [r for r in leaves if not glob.glob(os.path.join(r, 'run_*'))]
    for f in files:
        r = os.path.dirname(f)
        c = yaml.safe_load(open(os.path.join(r, 'conditions.yaml')))
        vals = open(f).read().split()
        if len(vals) != len(variables):
            bad += 1
            continue
        rows.append([c.get(k) for k in conds] + vals)
    if 'iterations' in conds:
        i = conds.index('iterations')
        rows.sort(key=lambda x: int(x[i] or 0))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(conds + labels)
        w.writerows(rows)
    print('%s: %d of %d runs -> %s (%d data files with a wrong value count)' % (group, len(rows), len(leaves), out, bad))


if __name__ == '__main__':
    if len(sys.argv) not in (5, 6):
        sys.exit(__doc__)
    main(*sys.argv[1:])
