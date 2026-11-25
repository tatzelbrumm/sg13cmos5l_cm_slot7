#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Assemble the magic PEX netlists of extract.sh (magic 8.3.685, IHP sg13cmos5l tech files of the PDK).

Usage: python3 -I pexfix.py c  <hier.spice> <flat.spice> <out.spice>
       python3 -I pexfix.py rc <rc.spice> <c.spice> <res.ext> <out.spice> [<report.csv>]

c   Why: sak-pex.sh (the IIC-OSIC-TOOLS script that made the earlier pad PEX netlists) writes the netlist with
    'ext2spice lvs', i.e. hierarchical output. With hierarchical output, this magic writes the coupling capacitors
    but none of the node-to-substrate capacitances of the (flattened) top cell, although the .ext file has them
    (e.g. slot_7 net enable: 33.77 fF substrate capacitance in slot_7.ext, absent from the netlist; with
    'ext2spice hierarchy off' it is there as 'C enable vss_3v3 33.7651f'). The flat output has no .subckt line.
    This takes the .subckt line (port order) from the hierarchical netlist and devices + capacitors from the flat one
    (same devices; checked: the X cards are identical).
rc  Why: in the full-RC netlist (ext2spice extresist on) every resistive net N carries, at its resistor nodes
    ('rnode' lines of <cell>.res.ext), capacitors to the substrate net whose sum is N's TOTAL capacitance (coupling
    included), and the coupling capacitors of N are written as well, so the coupling of the resistive nets is counted
    twice, once of it as capacitance to ground (e.g. slot_7 dig_in[1]: substrate 3.66 fF, rnode capacitances 124.2 fF,
    total in the C extraction 127.9 fF). The full-RC netlist written here keeps devices and resistors of <rc.spice>
    and takes every capacitor of the C-coupled netlist <c.spice> (same node names for the nets' main nodes); a
    capacitor between a resistive net N and the ground net is split over N's resistor nodes in proportion to their
    rnode capacitance (the distribution magic computed), all other capacitors stay where the C netlist has them (at
    the nets' main nodes, as magic's own full-RC output does with the coupling capacitors).
    <report.csv>: per resistive net: rnode capacitance sum, C-netlist total and ground part, as evidence.
"""
import csv
import re
import sys
from collections import defaultdict

SUF = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'a': 1e-18}


def val(s):
    m = re.fullmatch(r'([-+0-9.eE]+)([a-zA-Z]*)', s)
    return float(m.group(1)) * (SUF.get(m.group(2)[:1].lower(), 1.0) if m.group(2) else 1.0)


def stmts(path):
    st = []
    for ln in open(path).read().splitlines():
        if ln.startswith('+') and st:
            st[-1] += ' ' + ln[1:]
        else:
            st.append(ln)
    return st


def header(path):
    for s in stmts(path):
        if s.lower().startswith('.subckt'):
            return s.split()
    raise SystemExit(f'{path}: no .subckt')


def cmd_c(hier, flat, out):
    h = header(hier)
    body = [s for s in stmts(flat) if s[:1] and s[:1] in 'XxCcRr']
    xh = sorted(re.sub(r'^\S+', '', s) for s in stmts(hier) if s[:1] and s[:1] in 'Xx')
    xf = sorted(re.sub(r'^\S+', '', s) for s in body if s[:1] and s[:1] in 'Xx')
    assert xh == xf, 'device cards differ'
    nc = sum(1 for s in body if s[:1] and s[:1] in 'Cc')
    with open(out, 'w') as f:
        f.write(f'* magic C-coupled extraction, flat output (ext2spice hierarchy off) with the port order of the '
                f'hierarchical output; pexfix.py c\n* devices {len(xf)}, capacitors {nc}\n')
        f.write(' '.join(h) + '\n' + '\n'.join(body) + '\n.ends\n')
    print(f'{out}: {len(xf)} devices, {nc} capacitors (hierarchical output had '
          f'{sum(1 for s in stmts(hier) if s[:1] and s[:1] in "Cc")})')


def cmd_rc(rc, cnet, resext, out, report=None):
    gnd = None
    st_rc = stmts(rc)
    h = header(rc)
    # rnodes: name, capacitance (aF) per resistive net
    rn = defaultdict(dict)
    for ln in open(resext):
        t = ln.split()
        if t and t[0] == 'rnode':
            n = t[1].strip('"')
            m = re.fullmatch(r'(.+)\.[nt]\d+', n)
            rn[m.group(1) if m else n][n] = float(t[3]) * 1e-18
    # nets' main-node names in the rc netlist: the net name itself (magic keeps it for the first rnode)
    rc_nodes = set()
    for s in st_rc:
        t = s.split()
        if t and t[0][:1] in 'XxRr':
            rc_nodes.update(x for x in t[1:] if '=' not in x and not x.startswith(';'))
    caps = []
    for s in stmts(cnet):
        t = s.split(';')[0].split()
        if t and t[0][:1] in 'Cc':
            caps.append((t[1], t[2], val(t[3])))
    gnd = 'vss_3v3' if any('vss_3v3' in c[:2] for c in caps) else 'iovss'
    # main node of a resistive net: '<net>' with or without the trailing '#'
    main = {}
    for net in rn:
        cand = [x for x in (net, net + '#') if x in rn[net] or x in rc_nodes]
        main[net] = cand[0] if cand else None
    netof = {}
    for net, d in rn.items():
        for x in (net, net + '#'):
            netof[x] = net
    # only rnodes that the netlist has; a net whose main node magic removed ('killnode') is represented by its rnode
    # of largest capacitance
    for net in rn:
        rn[net] = {n: w for n, w in rn[net].items() if n in rc_nodes}
    rep = {}
    for net, d in rn.items():
        for x in (net, net + '#'):
            if x not in rc_nodes and d:
                rep[x] = max(d, key=d.get)
    out_caps, k = [], 0
    tot = defaultdict(float)
    gpart = defaultdict(float)
    for a, b, c in caps:
        for x in (a, b):
            if x in netof:
                tot[netof[x]] += c
        other = b if a == gnd else a if b == gnd else None
        net = netof.get(other) if other else None
        if net and net != netof.get(gnd) and rn[net]:
            gpart[net] += c
            s = sum(rn[net].values())
            items = list(rn[net].items())
            for n, w in items:
                share = c * (w / s if s > 0 else 1.0 / len(items))
                if share > 0:
                    out_caps.append(f'C{k} {n} {gnd} {share:.6g}')
                    k += 1
        else:
            out_caps.append(f'C{k} {rep.get(a, a)} {rep.get(b, b)} {c:.6g}')
            k += 1
    missing = sorted({rep.get(x, x) for a, b, _ in caps for x in (a, b)} - rc_nodes - {gnd})
    body = [s for s in st_rc if s[:1] and s[:1] in 'XxRr']
    with open(out, 'w') as f:
        f.write('* magic full-RC extraction: devices and resistors from the full-RC netlist, capacitors from the '
                'C-coupled netlist (ground capacitance of resistive nets split over their rnodes); pexfix.py rc\n')
        f.write(f'* devices {sum(1 for s in body if s[:1] and s[:1] in "Xx")}, resistors {sum(1 for s in body if s[:1] and s[:1] in "Rr")}'
                f', capacitors {len(out_caps)}\n')
        f.write(' '.join(h) + '\n' + '\n'.join(body + out_caps) + '\n.ends\n')
    rc_c = defaultdict(float)
    for s in st_rc:
        t = s.split(';')[0].split()
        if t and t[0][:1] in 'Cc':
            for x in t[1:3]:
                m = re.fullmatch(r'(.+)\.[nt]\d+', x)
                y = m.group(1) if m else x.rstrip('#')
                if y in rn:
                    rc_c[y] += val(t[3])
    if report:
        with open(report, 'w', newline='') as f:
            f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                    '# resistive nets of the magic full-RC extraction: rnode capacitance sum (res.ext), capacitance on '
                    'the net in magic\'s full-RC netlist and in the C-coupled netlist (total, to ground); fF; pexfix.py\n')
            w = csv.writer(f, lineterminator='\n')
            w.writerow(['net', 'n_rnodes', 'rnode_C_sum_fF', 'C_in_magic_rc_netlist_fF', 'C_total_c_netlist_fF',
                        'C_to_ground_c_netlist_fF'])
            for net in sorted(rn, key=lambda n: -sum(rn[n].values())):
                w.writerow([net, len(rn[net]), '%.4g' % (sum(rn[net].values()) * 1e15), '%.4g' % (rc_c[net] * 1e15),
                            '%.4g' % (tot[net] * 1e15), '%.4g' % (gpart[net] * 1e15)])
    print(f'{out}: {len(rn)} resistive nets, {len(rep)} main nodes mapped to an rnode, {len(out_caps)} capacitors; '
          f'capacitor nodes without device or resistor: '
          f'{missing[:5]}{" ..." if len(missing) > 5 else ""} ({len(missing)})')


if __name__ == '__main__':
    if len(sys.argv) < 5:
        sys.exit(__doc__)
    if sys.argv[1] == 'c':
        cmd_c(*sys.argv[2:5])
    elif sys.argv[1] == 'rc':
        cmd_rc(*sys.argv[2:])
    else:
        sys.exit(__doc__)
