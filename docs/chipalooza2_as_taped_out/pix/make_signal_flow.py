# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Draw the signal and current flow of slot 7 as taped out (158afc5) as an SVG block diagram.

Connections follow glue_logic.md (switch matrix XT1..XT10, same-net joins, bias_dist_pd configuration) and
README.md section 2. usage: python3 make_signal_flow.py [out.svg]   (default: slot7_signal_flow.svg next to this file)
"""
import os
import sys

W, H = 1240, 830
C_CTRL, C_IREF, C_VREF, C_SIG, C_BUS, C_TXT = "#7b3fa0", "#c25e00", "#2e7d32", "#1f5fbf", "#666666", "#222222"
out = []


def box(x, y, w, h, lines, fill="#f7f7f7", stroke="#444", bold_first=True, size=13, top=20):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.4"/>')
    ty = y + top
    for i, t in enumerate(lines):
        wgt = "bold" if (i == 0 and bold_first) else "normal"
        out.append(f'<text x="{x + 10}" y="{ty}" font-size="{size + (1 if i == 0 and bold_first else 0)}" '
                   f'font-weight="{wgt}" fill="{C_TXT}">{t}</text>')
        ty += size + 5


def line(pts, color, width=2.0, dash=None, arrow=False):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#a_{color[1:]})"' if arrow else ""
    out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{extra}{mk}/>')


def dot(x, y, color):
    out.append(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{color}"/>')


def text(x, y, t, color=C_TXT, size=12, anchor="start", weight="normal", style="normal"):
    out.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" text-anchor="{anchor}" '
               f'font-weight="{weight}" font-style="{style}">{t}</text>')


def switch(x, y, color, label=None):
    """Open switch symbol between (x, y) and (x + 36, y)."""
    line([(x, y), (x + 10, y)], color)
    line([(x + 10, y), (x + 27, y - 9)], color)
    line([(x + 27, y), (x + 36, y)], color)
    dot(x + 10, y, color)
    dot(x + 27, y, color)
    if label:
        text(x + 18, y - 13, label, C_CTRL, 11, "middle")


def bondpad(x, y, label):
    out.append(f'<rect x="{x}" y="{y}" width="50" height="50" fill="#e8d9a8" stroke="#8a6d1a" stroke-width="1.5"/>')
    out.append(f'<rect x="{x + 8}" y="{y + 8}" width="34" height="34" fill="none" stroke="#8a6d1a" stroke-width="1"/>')
    text(x + 25, y + 68, label, C_TXT, 12, "middle", "bold")


# ---- top row: harness controls, s7_ctrl, legend
box(20, 45, 185, 80, ["harness", "enable, dig_in[0..5]", "1.2 V levels"])
line([(205, 85), (248, 85)], C_CTRL, arrow=True)
box(250, 25, 420, 112, ["s7_ctrl: 3.3 V glue logic (71.6 × 38.04 µm)",
                        "7 fail-safe level shifters ls_up_fs (1.2 V → 3.3 V)",
                        "key: dig_in[3] = 1 and dig_in[4] = 0, else default",
                        "mode decode → switch controls ld, lx, sb, bd, rc",
                        "en / en_b to every block (enable = 0: all off)"], fill="#f3ecf7", stroke=C_CTRL)
# legend
lx, ly = 905, 25
out.append(f'<rect x="{lx}" y="{ly}" width="315" height="135" rx="6" fill="#ffffff" stroke="#999"/>')
text(lx + 10, ly + 19, "legend", C_TXT, 13, weight="bold")
for i, (c, dash, w, t) in enumerate([(C_CTRL, "6,4", 2, "control (3.3 V enables, switch controls)"),
                                      (C_IREF, None, 2.4, "reference current (≈ 5 µA, sourced)"),
                                      (C_VREF, None, 2.4, "reference voltage (vcm, vref)"),
                                      (C_SIG, None, 2.4, "signal path"),
                                      (C_BUS, None, 4, "harness shared analog bus")]):
    yy = ly + 40 + 20 * i
    line([(lx + 12, yy - 4), (lx + 52, yy - 4)], c, w, dash)
    text(lx + 62, yy, t, C_TXT, 12)

# ---- bias row
box(20, 190, 190, 82, ["bg_core_pd", "Banba bandgap", "sources ≈ 5 µA"], fill="#fff4e8", stroke=C_IREF)
line([(210, 228), (258, 228)], C_IREF, 2.4, arrow=True)
text(234, 220, "ibg", C_IREF, 11, "middle")
box(260, 190, 190, 82, ["bias_dist_pd", "switched 1:1 copies", "bandgap in; 3 outputs used"], fill="#fff4e8", stroke=C_IREF)
line([(300, 137), (300, 188)], C_CTRL, 2, "6,4", arrow=True)
text(306, 160, "en, en_b → all blocks", C_CTRL, 11)
# out0 -> pad_ref_rb
line([(450, 210), (528, 210)], C_IREF, 2.4, arrow=True)
text(489, 202, "iprb", C_IREF, 11, "middle")
box(530, 185, 225, 100, ["pad_ref_rb: replica bias", "one bias tree from 5 µA", "vcm_rb  ≈ 1.26 V", "vref_rb ≈ 0.49 V"], fill="#eef6ee", stroke=C_VREF)
# rc switches
switch(780, 210, C_VREF)
switch(780, 250, C_VREF)
line([(755, 210), (780, 210)], C_VREF, 2.4)
line([(755, 250), (780, 250)], C_VREF, 2.4)
text(806, 176, "rc: XT9, XT10", C_CTRL, 11)
line([(670, 118), (798, 118), (798, 190)], C_CTRL, 2, "6,4", arrow=True)
# vcm net: right to bus2, tap to D2S vref, left to S2D vcm
VCM_X_BUS, VREF_X_BUS = 1190, 1215
line([(816, 210), (VCM_X_BUS, 210), (VCM_X_BUS, 728)], C_VREF, 2.4)
text(1075, 203, "vcm (S2D vcm = D2S vref = analog_bus2)", C_VREF, 11, "middle")
line([(990, 210), (990, 448)], C_VREF, 2.4, arrow=True)
dot(990, 210, C_VREF)
line([(870, 210), (870, 330), (290, 330), (290, 448)], C_VREF, 2.4, arrow=True)
dot(870, 210, C_VREF)
# vref net: right to bus3, left to S2D vref
line([(816, 250), (VREF_X_BUS, 250), (VREF_X_BUS, 758)], C_VREF, 2.4)
text(1095, 243, "vref (S2D vref = analog_bus3)", C_VREF, 11, "middle")
line([(845, 250), (845, 360), (225, 360), (225, 448)], C_VREF, 2.4, arrow=True)
dot(845, 250, C_VREF)
# irefs of the pads' own bias trees
line([(380, 272), (380, 448)], C_IREF, 2.4, arrow=True)
text(386, 410, "s7_an_0_iref", C_IREF, 11)
line([(425, 272), (425, 300), (1040, 300), (1040, 448)], C_IREF, 2.4, arrow=True)
text(1046, 320, "s7_an_1_iref", C_IREF, 11)

# ---- signal row
bondpad(35, 505, "s7_an[0]")
line([(85, 530), (158, 530)], C_SIG, 2.4, arrow=True)
text(120, 522, "pad", C_SIG, 11, "middle")
box(160, 450, 255, 140, ["S2D pad (custom cell)", "sg13cmos5l_IOPadSingle2Diff",
                         "outp − outn = 2 (pad − vref)", "(outp + outn)/2 = vcm", "input 0 … 1 V (vref ≈ 0.5 V)"],
    fill="#edf3fc", stroke=C_SIG, top=40)
text(225, 466, "vref", C_VREF, 10, "middle")
text(290, 466, "vcm", C_VREF, 10, "middle")
text(380, 466, "iref", C_IREF, 10, "middle")

# switch matrix
box(470, 440, 300, 168, ["switch matrix (10 × tg_hv)", "ld: XT1, XT2  outp→vinp, outn→vinn",
                         "lx: XT3, XT4  outp→vinn, outn→vinp", "sb: XT5, XT6  outp→bus0, outn→bus1",
                         "bd: XT7, XT8  bus0→vinp, bus1→vinn", "(rc: XT9, XT10, above)"], fill="#f5f8fd", stroke=C_SIG, size=12)
line([(415, 510), (468, 510)], C_SIG, 2.4, arrow=True)
line([(415, 555), (468, 555)], C_SIG, 2.4, arrow=True)
text(441, 503, "outp", C_SIG, 11, "middle")
text(441, 548, "outn", C_SIG, 11, "middle")
line([(770, 510), (818, 510)], C_SIG, 2.4, arrow=True)
line([(770, 555), (818, 555)], C_SIG, 2.4, arrow=True)
text(794, 503, "vinp", C_SIG, 11, "middle")
text(794, 548, "vinn", C_SIG, 11, "middle")
line([(500, 137), (500, 438)], C_CTRL, 2, "6,4", arrow=True)
text(506, 420, "ld, lx, sb, bd", C_CTRL, 11)

box(820, 450, 255, 140, ["D2S pad (custom cell)", "sg13cmos5l_IOPadDiff2Single",
                         "pad − vref = (vinp − vinn)/2", "vref = vcm ≈ 1.26 V", "class-AB output stage"],
    fill="#edf3fc", stroke=C_SIG, top=40)
text(990, 466, "vref", C_VREF, 10, "middle")
text(1040, 466, "iref", C_IREF, 10, "middle")
line([(1075, 530), (1108, 530)], C_SIG, 2.4, arrow=True)
bondpad(1110, 505, "s7_an[1]")

# ---- shared analog buses
buses = [("analog_bus0", 668), ("analog_bus1", 698), ("analog_bus2", 728), ("analog_bus3", 758)]
for name, y in buses:
    line([(560, y), (1228, y)], C_BUS, 4)
    text(552, y + 4, name, C_TXT, 12, "end", "bold")
line([(600, 608), (600, 668)], C_SIG, 2.4)
dot(600, 668, C_SIG)
line([(640, 608), (640, 698)], C_SIG, 2.4)
dot(640, 698, C_SIG)
text(606, 640, "bus0", C_SIG, 10)
text(646, 680, "bus1", C_SIG, 10)
dot(VCM_X_BUS, 728, C_VREF)
dot(VREF_X_BUS, 758, C_VREF)
text(1228, 785, "to the harness's per-slot bus switches", C_TXT, 11, "end", style="italic")

# ---- mode summary and supplies
box(20, 610, 440, 160, ["modes (dig_in, only with the key)", "default: loop direct (ld); vcm, vref on bus2 / bus3",
                        "swap  [0]: loop crossed (lx)", "mon   [1]: + S2D outputs on bus0 / bus1 (sb)",
                        "feed  [2]: bus0 / bus1 drive the D2S, loop open (bd)",
                        "ext   [5]: replica off (rc open), vcm / vref from bus2 / 3",
                        "default loop: s7_an[1] = vcm + (s7_an[0] − vref)"], fill="#ffffff", stroke="#999", size=12)
text(20, 805, "Supplies: vdd_3v3 / vss_3v3 (harness-gated) for every block; the slot works with only vdd_3v3 on. vdd_1v2 only gates s7_doutpd, "
     "which holds dig_out[11:0] low.", C_TXT, 12)
text(20, 822, "The pad buffers' output stages and ESD sit on the pad ring (iovdd / iovss). Slot 7 as taped out, commit 158afc5; "
     "Oguey–Aebischer core not in the slot.", C_TXT, 12)

defs = "".join(f'<marker id="a_{c[1:]}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
               f'<path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for c in (C_CTRL, C_IREF, C_VREF, C_SIG))
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="DejaVu Sans, Helvetica, Arial, sans-serif"><defs>{defs}</defs>'
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>' + "".join(out) + "</svg>\n")
dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "slot7_signal_flow.svg")
open(dst, "w", encoding="utf-8").write(svg)
print(dst)
