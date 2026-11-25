# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Pad-ring model inputs, read from layout (no simulation):
1. resistance per um of the iovdd and iovss rings, from the metal bands of the IHP IO cell sg13cmos5l_Filler2000
   (PDK GDS) and the typical sheet resistances of the PDK process specification (SG13CMOS5L_os_process_spec.pdf
   Rev. 0.2, 2.3: Metal3 / Metal4 88 mOhm/sq, TopMetal1 18 mOhm/sq). Metal1 is left out (its bands do not follow
   the ring nets; leaving it out makes the ring resistance an upper bound);
2. positions of the supply pads, the ring splitters and the two slot-7 pads along the ring, from the harness
   padframe magic/sg13cmos5l_padframe.mag (tapeout_nov_2026 at 2ef5a869).
Usage: python3 ring.py <work_dir> <out_dir>   -> <out_dir>/csv/ring_metal.csv, ring_cells.csv"""
import csv
import os
import sys

import klayout.db as db

PDK = os.path.join(os.environ.get('PDK_ROOT', '/foss/pdks'), os.environ.get('PDK', 'ihp-sg13cmos5l'))
RSH = {'Metal3': (30, 0.088), 'Metal4': (50, 0.088), 'TopMetal1': (126, 0.018)}   # (GDS layer, Ohm/sq typ.)
LABEL_LAYER = (30, 25)   # Metal3.text: net labels of the ring bands


def ring_metal():
    ly = db.Layout()
    ly.read(os.path.join(PDK, 'libs.ref/sg13cmos5l_io/gds/sg13cmos5l_io.gds'))
    c = ly.cell('sg13cmos5l_Filler2000')
    cw = c.bbox().width()
    labels = []
    it = c.begin_shapes_rec(ly.layer(*LABEL_LAYER))
    while not it.at_end():
        s = it.shape()
        if s.is_text():
            labels.append((s.text.string, (it.trans() * s.text.trans).disp.y))
        it.next()
    rows = []
    for name, (lay, rsh) in RSH.items():
        reg = db.Region(c.begin_shapes_rec(ly.layer(lay, 0))).merged()
        for p in reg.each():
            b = p.bbox()
            if b.width() < 0.8 * cw:
                continue   # only bands that run through the cell (the ring)
            nets = {n for n, y in labels if b.bottom <= y <= b.top}
            if len(nets) != 1:
                continue
            net = nets.pop()
            if net not in ('iovdd', 'iovss'):
                continue
            rows.append({'net': net, 'layer': name, 'y0_um': b.bottom * ly.dbu, 'y1_um': b.top * ly.dbu,
                         'width_um': round(b.height() * ly.dbu, 3), 'rsh_ohm_sq': rsh})
    rper = {}
    for net in ('iovdd', 'iovss'):
        g = sum(r['width_um'] / r['rsh_ohm_sq'] for r in rows if r['net'] == net)
        rper[net] = 1.0 / g   # Ohm per um of ring
    return rows, rper


def perimeter(x, y):
    """Ring coordinate (um), counterclockwise from the south-east corner of the pad-cell origins
    (right edge x = 2080, top y = 3180, left x = 100, bottom y = 100, as in sg13cmos5l_padframe.mag)."""
    if abs(x - 2080) < 1:
        return y - 100
    if abs(y - 3180) < 1:
        return 3080 + (2080 - x)
    if abs(x - 100) < 1:
        return 5060 + (3180 - y)
    return 8140 + (x - 100)


def ring_cells(work):
    path = os.path.join(work, 'harness/magic/sg13cmos5l_padframe.mag')
    cells = []
    cur = None
    for line in open(path):
        w = line.split()
        if not w:
            continue
        if w[0] == 'use':
            cur = (w[1], w[2])
        elif w[0] == 'transform' and cur:
            x, y = int(w[3]) * 0.005, int(w[6]) * 0.005   # magscale 1 2: 5 nm units
            cells.append((cur[0], cur[1], x, y))
            cur = None
    keep = ('IOPadIOVdd', 'IOPadIOVss', 'IOPadVdd', 'IOPadVss', 'Split2000', 'IOPadSingle2Diff', 'IOPadDiff2Single',
            'Corner')
    out = []
    for cell, inst, x, y in cells:
        if any(k in cell for k in keep):
            out.append({'cell': cell, 'instance': inst, 'x_um': x, 'y_um': y, 's_um': perimeter(x, y)})
    out.sort(key=lambda r: r['s_um'])
    return out


def main():
    work, outdir = sys.argv[1], sys.argv[2]
    rows, rper = ring_metal()
    os.makedirs(os.path.join(outdir, 'csv'), exist_ok=True)
    with open(os.path.join(outdir, 'csv/ring_metal.csv'), 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n')
        f.write('# ring metal bands of sg13cmos5l_Filler2000 (PDK GDS); sheet resistance typ. (process spec 2.3)\n')
        f.write('# resistance per um: iovdd %.4g mOhm/um, iovss %.4g mOhm/um\n' % (rper['iovdd'] * 1e3, rper['iovss'] * 1e3))
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    cells = ring_cells(work)
    with open(os.path.join(outdir, 'csv/ring_cells.csv'), 'w', newline='') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n')
        f.write('# supply pads, splitters, corners and the slot-7 pads of sg13cmos5l_padframe.mag (tapeout_nov_2026 '
                '2ef5a869); s = ring coordinate of the cell origin, counterclockwise from the SE corner\n')
        w = csv.DictWriter(f, fieldnames=list(cells[0].keys()))
        w.writeheader()
        w.writerows(cells)
    print('ring resistance: iovdd %.4f mOhm/um, iovss %.4f mOhm/um; %d cells' %
          (rper['iovdd'] * 1e3, rper['iovss'] * 1e3, len(cells)))


if __name__ == '__main__':
    main()
