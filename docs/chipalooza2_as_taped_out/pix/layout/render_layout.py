# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# KLayout batch script: raw PNG renders of the taped-out slot 7 GDS and the two custom pads.
# Run through render_layout.sh, which then adds the caption and scale bar (annotate_layout.py):
#   klayout -zz -rd repo=<repo root> -rd out=<raw png dir> -rd lyp=<sg13cmos5l.lyp> -r render_layout.py
# Writes <out>/<name>.png plus <out>/<name>.txt (cell, gds, bbox in um, um per pixel, view) per picture.
import os
import pya

REPO = globals().get("repo", ".")
OUT = globals().get("out", "raw")
LYP = globals().get("lyp", "/foss/pdks/ihp-sg13cmos5l/libs.tech/klayout/tech/sg13cmos5l.lyp")

SLOT = "final/gds/slot_7.gds"
S2D = "pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.gds"
D2S = "pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds"

# GDS layer numbers hidden in the "frontend" view: Passiv, Via2..TopVia2, Metal3..TopMetal2,
# so the devices, Metal1 and Metal2 under the pad's top-metal plates become visible.
UPPER = {9, 29, 30, 49, 50, 66, 67, 125, 126, 133, 134}

# (picture name, gds, cell, long side in px, view)
JOBS = [
    ("slot_7", SLOT, "slot_7", 2000, "all"),
    ("slot_7_bg_core_pd", SLOT, "bg_core_pd", 1200, "all"),
    ("slot_7_bias_dist_pd", SLOT, "bias_dist_pd", 1400, "all"),
    ("slot_7_pad_ref_rb", SLOT, "pad_ref_rb", 1200, "all"),
    ("slot_7_s7_ctrl", SLOT, "s7_ctrl", 1400, "all"),
    ("slot_7_s7_doutpd", SLOT, "s7_doutpd", 1400, "all"),
    ("slot_7_tughra_art", SLOT, "tughra_art", 1400, "all"),
    ("IOPadSingle2Diff", S2D, "sg13cmos5l_IOPadSingle2Diff", 1400, "all"),
    ("IOPadSingle2Diff_frontend", S2D, "sg13cmos5l_IOPadSingle2Diff", 1400, "frontend"),
    ("IOPadDiff2Single", D2S, "sg13cmos5l_IOPadDiff2Single", 1400, "all"),
    ("IOPadDiff2Single_frontend", D2S, "sg13cmos5l_IOPadDiff2Single", 1400, "frontend"),
]

os.makedirs(OUT, exist_ok=True)

for name, gds, cellname, longside, view in JOBS:
    lv = pya.LayoutView()
    lv.set_config("background-color", "#ffffff")
    lv.set_config("grid-visible", "false")
    lv.set_config("text-visible", "false")       # pin labels would clutter the overview
    lv.set_config("cell-box-visible", "false")
    cv_index = lv.load_layout(os.path.join(REPO, gds), True)
    lv.load_layer_props(LYP)
    ly = lv.cellview(cv_index).layout()
    cell = ly.cell(cellname)
    lv.select_cell(cell.cell_index(), cv_index)
    lv.max_hier()
    if view == "frontend":
        it = lv.begin_layers()
        while not it.at_end():
            lp = it.current()
            if lp.source_layer in UPPER:
                lp.visible = False
            it.next()
    bb = cell.dbbox()
    m = 0.02 * max(bb.width(), bb.height())
    box = bb.enlarged(m, m)
    if box.width() >= box.height():
        w = longside
        h = int(round(longside * box.height() / box.width()))
    else:
        h = longside
        w = int(round(longside * box.width() / box.height()))
    png = os.path.join(OUT, name + ".png")
    # path, width, height, linewidth, oversampling, resolution, target box, monochrome
    lv.save_image_with_options(png, w, h, 1, 2, 0, box, False)
    with open(os.path.join(OUT, name + ".txt"), "w") as f:
        f.write("%s\t%s\t%.3f\t%.3f\t%.6f\t%s\n" % (cellname, gds, bb.width(), bb.height(), box.width() / w, view))
    print("%-28s %5d x %-5d  %s %.2f x %.2f um  (%s)" % (name, w, h, cellname, bb.width(), bb.height(), view))
    lv.destroy()
