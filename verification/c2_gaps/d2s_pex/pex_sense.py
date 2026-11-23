#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Give the extracted output devices of sg13cmos5l_IOPadDiff2Single a current sense, for the tb_dc template.

Usage: pex_sense.py <pex.spice>   (rewritten in place)

The tb_dc template reads the quiescent / minimum output-device currents as @n.x1.xfp.xop.nsg13_hv_pmos[ids] and
@n.x1.xfn.xon.nsg13_hv_nmos[ids]: the schematic devices XOP (ng=82, 6.66u/0.6u) and XON (ng=68, 4.4u/1u). Magic
extracts each finger as its own flat device, so that name does not exist in the PEX netlist. This moves the source
terminal (the one on iovdd / iovss; bulk unchanged) of every output finger (gate = the a / b node, the other
terminal = pad) to a new node and adds a 0 V source Vop_sense iovdd op_sense / Von_sense iovss on_sense, whose
current the pex copy of the template reads as i(v.x1.vop_sense) / i(v.x1.von_sense). Finger counts are checked.
"""
import sys

SETS = [  # model, gate net in the extraction, rail, sense node, expected fingers
    ('sg13_hv_pmos', 'd2s_cma_0.a', 'iovdd', 'op_sense', 82),
    ('sg13_hv_nmos', 'Clamp_N_M1_wiring_0.b', 'iovss', 'on_sense', 68),
]

def main(path):
    lines = open(path).read().split('\n')
    n = {s[3]: 0 for s in SETS}
    for i, l in enumerate(lines):
        t = l.split()
        if not t or t[0][0] not in 'Xx' or len(t) < 6:
            continue
        for model, gate, rail, node, _ in SETS:
            if t[5] == model and t[2] == gate and {t[1], t[3]} == {'pad', rail}:
                k = 1 if t[1] == rail else 3
                t[k] = node
                lines[i] = ' '.join(t)
                n[node] += 1
    for model, gate, rail, node, exp in SETS:
        if n[node] != exp:
            sys.exit(f'{path}: {n[node]} fingers for {node}, expected {exp}')
    stop = max(i for i, l in enumerate(lines) if l.lower().startswith('.ends'))
    lines[stop:stop] = [f'V{node} {rail} {node} 0' for _, _, rail, node, _ in SETS]
    open(path, 'w').write('\n'.join(lines))
    print(f'{path}: current sense on {n}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
