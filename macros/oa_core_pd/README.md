<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# oa_core_pd: Oguey–Aebischer reference-current core with power-down

The reference core of `bias_oa_pd`: no resistor, no BJT (M10 / M11 in weak inversion, vres = U_T ln 16). Its output
`iout` (the POC drain) *sources* about 5 uA into an NMOS input diode: a `bias_tree_pd`, or an input of `bias_dist_pd`.
The current is proportional to mu T^2, about -35 % / +35 % over -40 ... 125 C (`bias_oa_pd/README.md`).

Ports (order): `vdd vss iout en_3v3 en_3v3_b`. Disabled (en_3v3 = 0): MS1 off (gate en_3v3_b), SKS pulls ks to vss,
SVPG pulls vpg to vdd, so PO / POC are off and `iout` is high-Z; disabled cores can share one output node.

## Files

```
schematic/xschem/oa_core_pd.sch/.sym   the core, cut on 2026-10-20 from the flat sheet of bias_oa_pd; moved here
                                       unchanged on 2026-10-27 from macros/d2s_bias_sel_pd/schematic/xschem
schematic/xschem/xschemrc              self-contained (copy of bias_bg_pd's)
layout/gds/oa_core_pd.gds              compact layout v2, 2026-10-28: 40.51 x 58.135 um (2355 um2; v1 76.00 x 50.74 um),
                                       Metal1 / Metal2 only
```

**Layout v2 (2026-10-28), compact.** Assembled by script from compact primitives (cells inside the GDS):
- `oa_n10`: M10, M11, MC10, MS2, MS3, SKS as rotated 10/1 rows, interdigitated `A B A A B A A B A`, so M10 / M11
  share a centroid, with narrow end dummies;
- `oa_mcs_c`: MCS / MCL, sharing oa_n10's single p+ tie;
- `oa_pmir_c`: the point-symmetric mirror PO / P8 / P2 / P0 with 0.3 um end dummies;
- `oa_pcas_c`: oa_pcas without its ring;
- `oa_ms1`: MS1 as 8 x 0.5/12.5 in series;
- `oa_svpg`.

All PMOS sit in one vdd NWell, with no rings and no tie between array rows; the ties are in the rails plus two segments
in oa_pmir_c's margins (latch-up: every diffusion within 20 um of a tie). vdd rail (Metal1) on top, vss rail at the
bottom, `iout`, `en_3v3` and `en_3v3_b` as Metal2 pins on the right edge.

Checked with a Python subset of IHP's DRC rules (0 violations, latch-up included) and by extraction against this
sheet (match, 28 devices after combining fingers), plus an independent flat extraction (every device on its sheet
nets). Not yet checked with IHP's own decks (`make klayout-drc` / `make klayout-lvs`).

**The sheet follows the layout** (backannotated 2026-10-28):
- M10 ng 8 -> 18 and M11 ng 4 -> 9, W and L as before;
- MS1 drawn as the 8-device chain in box [S1];
- the dummies MDUM0 (PMOS 4.4/8, gate vpg), MDUM1 (NMOS 36/1, gate vnc) and MDUM2 (NMOS 4/1, gate vbr), with
  D = S = bulk, in box [D].

All ratios that set the circuit are unchanged (M10 : M11 = 2 : 1, PO : P8 : P2 : P0 = 20 : 8 : 2 : 1, MCS : MCL = 1 : 1).
The subckt in `bias_ref_pd.spice` has the same devices. Not re-simulated: the dummies only add gate capacitance on
vpg / vnc / vbr.

Build scripts, checks, renders, the process adapter and the skill drafts:
`_sudelbuecher/sudelbuecher/design_considerations/pad_buffer_layout/oa_core_pd_v2_2026-10-28/`; the files replaced here
(v1 GDS, the sheet, this README, bias_ref_pd.spice) are in its `macro_before/`. `bias_oa_pd`'s flat sheet still has
the pre-layout devices; its source subckt instantiates this core and so has the new ones.

Source netlist: `../bias_tree_pd/netlist/source/bias_ref_pd.spice`, subckt `oa_core_pd`. Used by `bias_sel_pd` and `bias_gen_pd`.
No CACE suite of its own: the core is characterized in `bias_oa_pd` (with the tree) and in `bias_sel_pd` (code 01).
