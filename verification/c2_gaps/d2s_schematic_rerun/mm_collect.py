#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""cace_to_csv.py (design repository, scripts/cace) for a group that CACE 2.11 collates over iterations: CACE 2.11
nests the iterations one level deeper (parameters/<group>/run_0/run_<k>/), which cace_to_csv.py (one level) does not
find (that is why the committed mm_params.csv has a header only). Same CSV format and column labels as cace_to_csv.py
(conditions of the group, then the yaml variables in SI units); rows sorted by iteration.
Usage: mm_collect.py <cell.yaml> <group> <run_dir> <out.csv>"""
import csv, glob, os, sys
import yaml

def main(ycell, group, rundir, out):
    d = yaml.safe_load(open(ycell))
    g = d['parameters'][group]
    variables = g['tool']['ngspice']['variables']
    conds = list(g['conditions'])
    si = {'ns': 's', 'ps': 's', 'pA': 'A', 'nA': 'A', 'uA': 'A', 'fC': 'C', 'pC': 'C', 'fW⋅s': 'J', 'pW⋅s': 'J'}
    units = {k: si.get(v.get('unit', ''), v.get('unit', '')) for k, v in g['spec'].items()}
    rows = []
    leaves = [os.path.dirname(c) for c in glob.glob(os.path.join(rundir, 'parameters', group, '**', 'conditions.yaml'),
                                                    recursive=True)]
    leaves = [r for r in leaves if not glob.glob(os.path.join(r, 'run_*'))]
    for f in glob.glob(os.path.join(rundir, 'parameters', group, '**', '*.data'), recursive=True):
        r = os.path.dirname(f)
        c = yaml.safe_load(open(os.path.join(r, 'conditions.yaml')))
        vals = open(f).read().split()
        if len(vals) != len(variables):
            continue
        row = {k: c.get(k) for k in conds}
        row.update(dict(zip(variables, vals)))
        rows.append(row)
    rows.sort(key=lambda x: int(x.get('iterations') or 0))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(conds + ['%s[%s]' % (v, units.get(v, '')) for v in variables])
        for row in rows:
            w.writerow([row[k] for k in conds + variables])
    print('%s: %d of %d runs -> %s' % (group, len(rows), len(leaves), out))

if __name__ == '__main__':
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
