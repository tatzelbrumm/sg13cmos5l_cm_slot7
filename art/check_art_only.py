# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Check that final/gds/slot_7.gds = <before> slot_7.gds + the cell tughra_art at (88.5, 141.3) um and nothing else.
Usage: python3 -I check_art_only.py <before slot_7.gds> <tughra_art.gds> <after slot_7.gds> [<reference with art>]
Exit 1 on any difference."""
import sys
import klayout.db as db
before, art, after = sys.argv[1:4]; ref = sys.argv[4] if len(sys.argv) > 4 else None
def load(p):
    l = db.Layout(); l.read(p); return l
B, A, N = load(before), load(art), load(after)
bad = []
def say(ok, msg):
    print(('OK   ' if ok else 'FAIL ') + msg)
    if not ok: bad.append(msg)
def cell_content(ly, c):
    sh = {}
    for li in ly.layer_indexes():
        info = ly.get_info(li); key = (info.layer, info.datatype)
        items = sorted(str(s) for s in c.shapes(li).each())
        if items: sh[key] = items
    inst = sorted((ly.cell(i.cell_index).name, str(i.cplx_trans), i.na, i.nb, str(i.a), str(i.b)) for i in c.each_inst())
    return sh, inst
say(N.dbu == B.dbu, f'dbu {N.dbu}')
say([c.name for c in N.top_cells()] == ['slot_7'], f'top cells {[c.name for c in N.top_cells()]}')
say(not any('CONTEXT' in c.name for c in N.each_cell()), 'no $$$CONTEXT_INFO$$$ cell')
bn = sorted(c.name for c in B.each_cell()); nn = sorted(c.name for c in N.each_cell())
say(sorted(bn + ['tughra_art']) == nn, f'cells: before {len(bn)}, after {len(nn)} = before + tughra_art')
diffcells = []
for c in B.each_cell():
    if c.name == 'slot_7': continue
    if N.cell(c.name) is None or cell_content(B, c) != cell_content(N, N.cell(c.name)): diffcells.append(c.name)
say(not diffcells, f'all {len(bn) - 1} sub-cells of slot_7 identical in shapes and instances' + (f': differ {diffcells}' if diffcells else ''))
bs, bi = cell_content(B, B.cell('slot_7')); ns, ni = cell_content(N, N.cell('slot_7'))
say(bs == ns, 'slot_7 own shapes and texts identical')
extra = [i for i in ni if i not in bi]; missing = [i for i in bi if i not in ni]
say(not missing and len(extra) == 1 and extra[0][0] == 'tughra_art' and extra[0][1] == 'r0 *1 88500,141300',
    f'slot_7 instances: before {len(bi)}, after {len(ni)}; added {extra}; missing {missing}')
say(N.cell('tughra_art') is not None and cell_content(A, A.top_cells()[0])[0] == cell_content(N, N.cell('tughra_art'))[0],
    'tughra_art cell identical to art/tughra_art.gds')
say(B.cell('slot_7').dbbox() == N.cell('slot_7').dbbox(), f'slot_7 bbox {N.cell("slot_7").dbbox()}')
# flat: after == before + placed art, per layer
t = db.Trans(88500, 141300); tot = 0
layers = set((N.get_info(l).layer, N.get_info(l).datatype) for l in N.layer_indexes())
for (L, D) in sorted(layers):
    def flat(ly, cellname, tr=None):
        li = ly.find_layer(L, D)
        if li is None: return db.Region()
        r = db.Region(ly.cell(cellname).begin_shapes_rec(li)); return r.transformed(tr) if tr else r
    exp = flat(B, 'slot_7') + flat(A, A.top_cells()[0].name, t)
    x = (flat(N, 'slot_7') ^ exp).count(); tot += x
say(tot == 0, f'flat XOR (after) vs (before + art at 88.5, 141.3), all {len(layers)} layers: {tot}')
# art keeps >= 1 um from every existing shape on its drawing layers (GatPoly: from all front-end shapes)
fe = [(1, 0), (5, 0), (6, 0), (31, 0), (7, 0), (14, 0), (25, 0), (44, 0), (45, 0), (46, 0)]
for (L, D) in [(5, 0), (8, 0), (10, 0), (30, 0), (50, 0)]:
    ali = A.find_layer(L, D); ar = db.Region(A.top_cells()[0].begin_shapes_rec(ali)).transformed(t)
    occ = db.Region()
    for (l2, d2) in (fe if L == 5 else [(L, d) for d in (0, 2, 25)]):
        li = B.find_layer(l2, d2)
        if li is not None: occ += db.Region(B.cell('slot_7').begin_shapes_rec(li))
    near = ar & occ.sized(999)
    say(near.is_empty(), f'art on {L}/{D}: no existing shape within 1 um ({ar.count()} art polygons)')
if ref:
    R = load(ref); tot = 0
    for (L, D) in sorted(layers | set((R.get_info(l).layer, R.get_info(l).datatype) for l in R.layer_indexes())):
        a = N.find_layer(L, D); r = R.find_layer(L, D)
        ra = db.Region(N.cell('slot_7').begin_shapes_rec(a)) if a is not None else db.Region()
        rr = db.Region(R.cell('slot_7').begin_shapes_rec(r)) if r is not None else db.Region()
        tot += (ra ^ rr).count()
    say(tot == 0, f'flat XOR vs reference {ref.split("/")[-1]} (design repo, v2 + art): {tot}')
print('RESULT', 'FAIL' if bad else 'PASS'); sys.exit(1 if bad else 0)
