# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Insert the cell tughra_art (art/tughra_art.gds) into slot_7 (final/gds/slot_7.gds) at (88.5, 141.3) um, the
placement of the design repo's art/slot7_with_art.gds, and write the result. Nothing else in slot_7 is touched:
every existing cell is copied as read, the only additions are the cell tughra_art and one instance of it in slot_7.
No KLayout context cell is written.  Usage: python3 -I add_art.py <slot_7.gds in> <tughra_art.gds> <slot_7.gds out>"""
import sys
import klayout.db as db
src, art, out = sys.argv[1:4]
ly = db.Layout(); ly.read(src)
assert ly.cell('tughra_art') is None, 'slot_7 already has a cell tughra_art'
top = ly.cell('slot_7'); assert top is not None and len(list(ly.top_cells())) == 1
al = db.Layout(); al.read(art)
assert al.dbu == ly.dbu and len(list(al.top_cells())) == 1 and al.cells() == 1
ac = ly.create_cell('tughra_art')
ac.copy_tree(al.top_cells()[0])
top.insert(db.CellInstArray(ac.cell_index(), db.Trans(88500, 141300)))
opt = db.SaveLayoutOptions(); opt.write_context_info = False
ly.write(out, opt)
print('wrote', out)
