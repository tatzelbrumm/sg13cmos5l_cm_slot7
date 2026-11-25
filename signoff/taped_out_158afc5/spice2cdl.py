#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Derive a KLayout-LVS CDL from a magic/netgen-flavour SPICE netlist (pads/*/*.spice).

The netgen netlists instance the PDK primitives as subcircuit calls (X cards):
    XM1 d g s b sg13_hv_nmos w=.. l=..   ->  MXM1 d g s b sg13_hv_nmos w=.. l=..
    XR1 a b sub rhigh w=.. l=..          ->  RXR1 a b sub rhigh w=.. l=..
    XD1 a c dantenna l=.. w=..           ->  DXD1 a c dantenna l=.. w=..
Only lines whose model is one of the primitives below are changed; subcircuit calls of
the design's own cells, .subckt / .ends and comments are copied unchanged. The new
element name is the old one with the element letter in front, so names stay unique.
"""
import re
import sys

PRIMS = {
    "sg13_lv_nmos": "M", "sg13_lv_pmos": "M", "sg13_hv_nmos": "M", "sg13_hv_pmos": "M",
    "rhigh": "R", "rppd": "R", "rsil": "R",
    "dantenna": "D", "dpantenna": "D",
}


def convert(lines):
    out, n = [], {}
    for line in lines:
        s = line.rstrip("\n")
        if s[:1] in ("x", "X"):
            toks = s.split()
            # model = last token before the first key=value parameter
            idx = next((i for i, t in enumerate(toks) if "=" in t), len(toks))
            model = toks[idx - 1].lower()
            if model in PRIMS:
                letter = PRIMS[model]
                toks[0] = letter + toks[0]
                n[model] = n.get(model, 0) + 1
                s = " ".join(toks)
        out.append(s + "\n")
    return out, n


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src) as f:
        out, n = convert(f.readlines())
    with open(dst, "w") as f:
        f.write("* derived by spice2cdl.py from %s (X cards of PDK primitives -> M/R/D)\n" % src)
        f.writelines(out)
    sys.stderr.write("spice2cdl: %s -> %s: %s\n" % (src, dst, ", ".join("%s %d" % kv for kv in sorted(n.items()))))
