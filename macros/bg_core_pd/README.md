<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# bg_core_pd: Banba current-mode bandgap core with power-down

The reference core of `bias_bg_pd`: a current-mode (Banba type) bandgap without op-amp, pnpMPA (Q2 = 8 x Q1) and rhigh.
Each branch carries V_BE1 / R1 + U_T ln 8 / R0 = 2.5 uA; PO / POC deliver twice that, about 5 uA, *sourced* out of
`iout` into an NMOS input diode: a `bias_tree_pd`, or an input of `bias_dist_pd`. Flat over temperature and MOS
corners, it follows the rhigh corners (about -20 % / +30 %, `bias_bg_pd/README.md`).

Ports (order): `vdd vss iout en_3v3 en_3v3_b`. Disabled as `oa_core_pd`: MS1 off, SKS and SVPG on, `iout` high-Z.

## Files

```
schematic/xschem/bg_core_pd.sch/.sym   the core, cut on 2026-10-20 from the flat sheet of bias_bg_pd (dangling wires
                                       removed 2026-10-22); moved here unchanged on 2026-10-27 from
                                       macros/d2s_bias_sel_pd/schematic/xschem
schematic/xschem/xschemrc              self-contained (copy of bias_bg_pd's)
layout/gds/bg_core_pd.gds              compact layout, 2026-10-28: 47.55 x 50.05 um (2380 um2; the library primitives
                                       take 2673 um2 in their bounding boxes, 3424 um2 placed as a block),
                                       Metal1 / Metal2 only
```

**Layout (2026-10-28), compact.** Assembled by script from compact primitives (cells inside the GDS):
- `bg_pmir_pcas_c`: PB / PA / PO with the cascodes PBC / PAC / POC, point-symmetric, no ring, 0.3 um end dummies on
  vpg and vpc;
- `bg_n4`: NA / NB interdigitated (2 x 10/4 each), MS2, MS3 and SKS at the ends, its own p+ ties at the bottom and the
  top, dummies tied to g on all terminals;
- `bg_ms1`: MS1 as 8 x 0.5/12.5 in series; `bg_svpg`;
- `bg_res_c`: the rhigh segments of `bg_res` (0.5 x 9.94 um, 0.68 um pitch, the same interleave), wired, no ring:
  R0 18, R1A 11, R1B 10 segments, plus 2 dummy segments on vss;
- `bg_pnp_c`: the 3 x 3 pnpMPA array of `bg_pnp` (Q1 in the centre, 8 x Q2 around it), now with emitter / base wiring.

All PMOS sit in one vdd NWell, with no rings and no tie between array rows. The ties are:
- under the vdd rail;
- a 13.1 um segment for bg_ms1;
- bg_n4's own;
- the pnp collector rings.

vdd rail (Metal1) on top, vss rail at the bottom. `iout`, `en_3v3` and `en_3v3_b` are Metal2 pins on the right edge, as
in `oa_core_pd`, so the two cores can abut in `bias_gen_pd`. On Metal1 / Metal2: e2 4.3 um, eb 4.6 um, ea 18 um (its
branch to Q1 included). No enable crosses the resistor, pnp or NMOS arrays.

Checked with a Python subset of IHP's DRC rules (0 of 74, latch-up and antenna included) and by LVS against the
composed reference and against this sheet (match, 30 devices after combining fingers and series segments). An
independent flat extraction found:
- every MOS on its sheet nets;
- R0 / R1A / R1B as 357.8 / 218.7 / 198.8 squares between their sheet nets;
- Q1 on ea and 8 x Q2 on e2.

Not yet checked with IHP's own decks (`make klayout-drc` / `make klayout-lvs`).

**The sheet follows the layout** (backannotated 2026-10-28):
- R0, R1A and R1B are the drawn chains of 18 / 11 / 10 rhigh segments of 0.5 x 9.94 um, as xschem vector instances
  `R0[17:0]`, `R1A[10:0]` and `R1B[9:0]`. Their bus labels name the chain nodes: `R0[17:0]` runs from `eb,n0[16:0]`
  to `n0[16:0],e2`, i.e. eb, n0[16] ... n0[0], e2. Box [C] is wider than before, so the labels fit.
  - Total length: R0 -0.32 %, R1A and R1B +0.04 %.
  - Resistance, from the xschem symbol's expression (each segment has its own heads): R0 +0.70 %, R1A +1.03 %,
    R1B +1.02 %, so R1 / R0 +0.32 %. Not simulated.
  - The library `bg_res` already had these segments.
- NA and NB: ng 1 -> 2, W and L as before.
- MS1 is drawn as the 8-device chain (8 x 0.5/12.5 in series) in box [S1].
- The dummies are in box [D]:
  - MDUM0 / MDUM1: PMOS 2.4/1 (8 x 0.3) on vpg and on vpc, with D = S = B = vdd;
  - MDUM2 / MDUM3: NMOS 2/1 and 16/4 with D = S = G = g, B = vss;
  - `RDUM[1:0]`: 2 rhigh segments with both ends on vss.

All ratios that set the circuit are unchanged: PO : PA : PB = 2 : 1 : 1, the same for the cascodes, NA : NB = 1 : 1,
Q2 : Q1 = 8 : 1. The subckt `bg_core_pd` in `bias_ref_pd.spice` has the same devices, with the sheet's names.
`bias_bg_pd`'s flat sheet still has the pre-layout devices; its source subckt instantiates this core and so has the
new ones.

Build scripts, checks, renders, A2's backannotation package and the skill drafts are in
`_sudelbuecher/sudelbuecher/design_considerations/pad_buffer_layout/bg_core_pd_2026-10-28/`; the sheet edit, the
subckt edit and their checks are in its `macro_install/`. The files replaced here (the sheet, this README in both
earlier versions, bias_ref_pd.spice) are in its `macro_before/`.

Source netlist: `../bias_tree_pd/netlist/source/bias_ref_pd.spice`, subckt `bg_core_pd`. Used by `bias_sel_pd` and `bias_gen_pd`.
No CACE suite of its own: the core is characterized in `bias_bg_pd` (with the tree) and in `bias_sel_pd` (code 10).
