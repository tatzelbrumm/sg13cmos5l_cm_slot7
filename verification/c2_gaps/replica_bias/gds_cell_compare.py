# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Compare cell <cell> of two GDS files (flattened per-layer XOR and texts, KLayout) and write the cell of the first
file (with its subcells) as a standalone GDS.
Usage: klayout -b -r gds_cell_compare.py -rd a=<slot_7.gds> -rd b=<macro.gds> -rd cell=<name> -rd out=<cell.gds>"""
import pya
la = pya.Layout(); la.read(a)
lb = pya.Layout(); lb.read(b)
ca, cb = la.cell(cell), lb.cell(cell)
assert ca and cb, 'cell %s missing' % cell
print('a: %s bbox=%s subcells=%d' % (a, ca.dbbox(), len(list(ca.each_child_cell()))))
print('b: %s bbox=%s subcells=%d' % (b, cb.dbbox(), len(list(cb.each_child_cell()))))
layers = set()
for L in (la, lb):
    for li in L.layer_indexes():
        i = L.get_info(li); layers.add((i.layer, i.datatype))
ndiff = npoly = 0
for (l, d) in sorted(layers):
    ia, ib = la.find_layer(l, d), lb.find_layer(l, d)
    ra = pya.Region(ca.begin_shapes_rec(ia)) if ia is not None else pya.Region()
    rb = pya.Region(cb.begin_shapes_rec(ib)) if ib is not None else pya.Region()
    ta = sorted((t.string, t.x, t.y) for t in pya.Texts(ca.begin_shapes_rec(ia)).each()) if ia is not None else []
    tb = sorted((t.string, t.x, t.y) for t in pya.Texts(cb.begin_shapes_rec(ib)).each()) if ib is not None else []
    x = ra ^ rb; npoly += ra.count()
    if not x.is_empty() or ta != tb:
        ndiff += 1
        print('DIFF layer %d/%d: xor polygons %d, area %g um2, texts %d vs %d' % (l, d, x.count(), x.area() * la.dbu ** 2, len(ta), len(tb)))
print('layers compared: %d, polygons (a, flattened): %d, layers with differences: %d' % (len(layers), npoly, ndiff))
print('XOR_RESULT %s: %s' % (cell, 'IDENTICAL' if ndiff == 0 else 'DIFFERENT'))
o = pya.Layout(); o.dbu = la.dbu
o.create_cell(cell).copy_tree(ca)
o.write(out)
print('wrote', out)
