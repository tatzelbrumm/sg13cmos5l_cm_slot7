#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Device-only copy of a magic PEX netlist for netgen LVS: drop the parasitic capacitors and short the parasitic
resistors (full-RC extraction), i.e. merge the nodes each R card connects. Devices (X cards: MOS, rhigh, pnpMPA, ...)
are kept unchanged apart from the node renaming. A merged node takes the name of a subckt port if one is among them,
else of a node without the '.n<k>' / '.t<k>' suffix magic gives the pieces of a resistive net.

Usage: python3 -I lvs_collapse.py <pex.spice> <out.spice>
Prints the counts: R cards shorted, C cards dropped, nodes before / after.
"""
import re
import sys


def main(src, dst):
    stmts = []
    for ln in open(src).read().splitlines():
        if ln.startswith('+') and stmts:
            stmts[-1] += ' ' + ln[1:]
        else:
            stmts.append(ln)
    par = {}

    def find(a):
        while par.get(a, a) != a:
            par[a] = par.get(par[a], par[a])
            a = par[a]
        return a

    ports, nodes, nr, nc = set(), set(), 0, 0
    for s in stmts:
        t = s.split()
        if t and t[0].lower() == '.subckt':
            ports = set(t[2:])
        elif t and t[0][0] in 'Rr':
            nr += 1
            a, b = find(t[1]), find(t[2])
            nodes.update(t[1:3])
            if a != b:
                # keep the better name as the root
                def rank(n):
                    return (0 if n in ports else 1 if not re.search(r'\.[nt]\d+$', n) else 2, n)
                ra, rb = sorted([a, b], key=rank)
                par[rb] = ra
        elif t and t[0][0] in 'Xx':
            nodes.update(x for x in t[1:] if '=' not in x)
    out = []
    for s in stmts:
        t = s.split()
        if not t:
            out.append(s)
            continue
        if t[0][0] in 'Cc':
            nc += 1
            continue
        if t[0][0] in 'Rr':
            continue
        if t[0][0] in 'Xx':
            pos = [i for i, x in enumerate(t) if '=' not in x][1:-1]  # nodes: between name and model
            for i in pos:
                t[i] = find(t[i])
            out.append(' '.join(t))
        else:
            out.append(s)
    open(dst, 'w').write('\n'.join(out) + '\n')
    roots = {find(n) for n in nodes}
    print(f'{src}: {nr} R shorted, {nc} C dropped, {len(nodes)} device/R nodes -> {len(roots)}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
