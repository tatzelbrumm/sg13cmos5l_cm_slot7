<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# DC curves of the two custom pads: input / output range and linearity

**IHP sg13cmos5l simulation (schematic | magic PEX)**, ngspice-47 with the IHP OSDI models, run through CACE 2.11 on
the pads' own committed CACE testbenches. Pads: `sg13cmos5l_IOPadSingle2Diff` (S2D, `s7_an[0]`) and
`sg13cmos5l_IOPadDiff2Single` (D2S, `s7_an[1]`) as taped out (`pads/<cell>/<cell>.gds` of this repository; the GDS
files are byte-identical to the design repository's `layout/klayout/<cell>.klay.gds` at commit 91a7da8b, git blob
`c871a046…` / `d09ed053…`). Numbers and range tables: **[results.md](results.md)**.

Status: complete (all figures, tables and checks below were produced by the runs of 2026-11-24).

## Figures (plots/, PNG 150 dpi; SVG too where it stays below 60 kB)

PEX figures are given for the main cases; for the variants (D2S at 3.0 V, unloaded, at the slot's vicm) only the
schematic figure is kept (size budget of this folder): the PEX curves there agree with the schematic ones within
0.7 mV (range ends) and 0.001 mV (INL), see `tables/d2s.md`.

| file | status | what it shows |
|---|---|---|
| `s2d_transfer_tt27_schematic`, `s2d_transfer_tt27_pex` | done | S2D: outp, outn, outp − outn, (outp + outn)/2 and the ideal 2 (pad − vref) vs the pad voltage −0.3 … 3.3 V; tt, 27 °C, iovdd 3.3 V, vref 0.5 V, vcm 1.2 V; the linear input range (1 mV criterion) shaded |
| `s2d_corners_schematic`, `s2d_corners_pex` | done | S2D: top, outp − outn vs pad 0 … 1.3 V; bottom, error vs the ideal transfer, vd/2 − (pad − vref), input-referred, symlog mV axis (linear inside ±1 mV, shaded); 5 MOS corners (color) × −40 / 27 / 125 °C (line style), iovdd 3.3 V |
| `s2d_linearity_criterion` | done | S2D: \|error from the small-signal line\| (the range criterion), input-referred, log axis, schematic and PEX side by side; where a curve crosses 1 mV is the range end; iovdd 3.3 V |
| `s2d_range` | done | S2D: linear input range (1 mV criterion) as a bar per MOS corner × temperature × iovdd 3.0 / 3.3 / 3.6 V, schematic and PEX |
| `s2d_range_slot` | done | the same at the slot's nominal replica values vref 0.49 V, vcm 1.26 V (schematic) |
| `s2d_vrefvcm_range` | done | S2D input range vs vref (0.5 / 0.8 / 1.2 / 1.65 V) and vcm (1.0 / 1.2 / 1.4 / 1.65 V), iovdd 3.0 and 3.3 V: bar = range met at all of ss / tt / ff × −40 / 27 / 125 °C, marks = tt 27 °C (schematic) |
| `d2s_transfer_tt27_schematic`, `d2s_transfer_tt27_pex` | done | D2S: pad vs vinp − vinn, −3.3 … 3.3 V around vicm = vref = 1.65 V, with 1 kΩ to 1.65 V + 100 pF (the CACE load) and unloaded (1 TΩ); ideal vref + (vinp − vinn)/2; output range (10 mV criterion, 1 kΩ) shaded; pad at ±3 V printed; tt, 27 °C, iovdd 3.3 V |
| `d2s_corners_schematic`, `d2s_corners_pex` | done | D2S, 1 kΩ, iovdd 3.3 V: top, pad vs vinp − vinn; bottom, error vs ideal pad − vref − (vinp − vinn)/2, output-referred, symlog mV (±10 mV shaded); corners (color) × temperatures (line style) |
| `d2s_corners_3v0_schematic` | done | the same at iovdd 3.0 V (the headroom limit at vicm 1.65 V) |
| `d2s_corners_noload_schematic` | done | the same unloaded, iovdd 3.3 V |
| `d2s_linearity_criterion` | done | D2S, 1 kΩ: \|error from the small-signal line\| vs pad output voltage, log axis, schematic and PEX; 10 mV (range criterion) and 1 mV lines; iovdd 3.3 V |
| `d2s_range`, `d2s_range_noload` | done | D2S: output range (10 mV criterion) as a bar per corner × temperature × iovdd 3.0 / 3.3 / 3.6 V, schematic and PEX; 1 kΩ and unloaded |
| `d2s_corners_slot_schematic`, `d2s_corners_slot_3v0_schematic` | done | D2S at the slot's operating point vref = vicm = 1.26 V, 1 kΩ to 1.26 V + 100 pF, vinp − vinn ±2.52 V: output and error vs ideal over corners, iovdd 3.3 V and 3.0 V |
| `d2s_range_slot` | done | D2S output range (10 mV criterion) per corner × temperature × supply at vref = vicm = 1.26 V, schematic and PEX |
| `rt_transfer_tt27` | done | round trip in the slot-7 tier-1 deck (default mode, replica vref / vcm): pad out vs pad in −0.3 … 3.3 V, pads schematic / magic PEX / KLayout-extracted, expected vcm + (pad in − vref), 1 mV range shaded; tt 27 °C 3.3 V |
| `rt_error_corners` | done | round trip: pad out − (vcm + pad in − vref) vs pad in, symlog mV, the designer's five tier-1 PVT points (color) × the three pad views (line style) |

How to read the error plots: "error vs ideal" includes the systematic gain error (S2D gain 1.9968 … 1.9978 instead of
2, i.e. −0.11 … −0.16 %) and offset, so it is a straight sloped line inside the linear range (0 at pad = vref) and bends
away at the range ends; "error from the small-signal line" removes gain and offset (the CACE definition of INL) and
shows only the nonlinearity, which is what limits the range.

## Range criteria

- **S2D input range** = the contiguous pad-voltage range around pad = vref in which |vd − vd0 − G·u| / G < 1 mV,
  with u = pad source − vref, vd = outp − outn, G = (vd(u = +0.1 V) − vd(u = −0.1 V)) / 0.2 V and vd0 = vd(u = 0).
  This is exactly the CACE `window_params` criterion of the S2D yaml (template `tb_range`) and the CACE `INL`
  definition of `tb_dc`, so the table reproduces the committed `window_params` results (cross-check in results.md:
  within 0.62 mV on Vin_max, the difference being the 10 mV vs 2 mV sweep steps). Differences: the sweep here starts at
  −0.3 V (CACE: 0 V), so Vin_min < 0 V is reported where the criterion still holds below ground; and it runs at
  iovdd 3.0 / 3.3 / 3.6 V over all five MOS corners (CACE window: ss / tt / ff).
- **D2S output range** = the pad-voltage span over the contiguous vinp − vinn range around 0 in which
  |vo − vo0 − G·vd| < 10 mV (output-referred), with vo = pad − vref, vd = vinp − vinn, G from vd = ±0.2 V and
  vo0 = vo(vd = 0): the CACE `tb_dc` small-signal line, and 10 mV = the CACE `dc_params` INL limit. The 1 mV span is
  given in brackets in `tables/d2s.md`. The rail-limited swing is given separately as the pad voltage at
  vd = ±3 V (the CACE `drive_params` points). INL in the tables = the CACE definition (max over |vd| ≤ 1 V).
- **Round trip**: the contiguous pad-in range around pad in = vref (replica) with |error from the small-signal line|
  < 1 mV (also 10 mV in `tables/rt.md`), slope from pad in = vref ± 0.1 V; error vs expected = pad out − (vcm + pad in
  − vref) as `run_tier1.py`.

## Conditions (= the committed CACE testbench `tb_dc` of each pad, only the analysis changed)

`mkgroups.py` copies the pad's `verification/cace/templates/<cell>_tb_dc.sch` (design commit 91a7da8b) to
`<cell>_tb_dcsweep.sch` and replaces only its `.control` block (wide `dc` sweep(s), `wrdata`); sources, models and
options are unchanged (D2S: plus `.option rshunt=1e12`, see "Solver aids"). The sweep groups (conditions) are in
`mkgroups.py`; CACE fills in the conditions and netlists each run as for the committed results:

- MOS corner on `cornerMOShv` and `cornerMOSlv`, `res_typ`, `cap_typ`, pnp `typ`, `dio_tt`, IHP IO library
  `sg13cmos5l_io.spice`; `.options method=gear reltol=1e-4 abstol=1e-15 gmin=1e-15` (+ `klu` in the D2S template).
- Bias: harness iDAC (PMOS mirror) 5 µA into `bias_gen_pd` with sel = 0 (harness current passed to `iref`),
  `en_ctrl_3v3` next to the pad (both schematic in both views: they are not part of the pad cell), vdd core 1.2 V.
- S2D: pad driven by vref + u through 50 Ω, 0.5 pF per output on top of the built-in capacitors; vref 0.5 V (the
  `window_params` value), vcm 1.2 V (yaml default). u swept so that the pad source runs −0.3 … 3.3 V in 2 mV steps.
- D2S: vinp = vicm + vd/2, vinn = vicm − vd/2, vref = vicm = 1.65 V (yaml defaults), pad loaded with 1 kΩ to vterm
  = 1.65 V and 100 pF (yaml defaults) or unloaded (rload 1 TΩ); vd swept from 0 to +3.3 V and from 0 to −3.3 V in 5 mV
  steps (two branches from the operating point at vd = 0, merged). Group `d2s_slot`: vref = vicm = vterm = 1.26 V
  (the slot's vcm), vd ±2.52 V.
- Round trip: see `roundtrip.py` (the designer's tier-1 slot deck, not a CACE testbench).

### Solver aids (no circuit change)

- D2S, both views: ngspice `.option rshunt=1e12` (1 TΩ from every node to ground). The PEX view needs it to converge
  (`../d2s_pex`). On the schematic view, without it the run at tt −40 °C 3.3 V did not finish: a single sweep from
  vd = −3.3 V stalled for > 13 min (also tt −40 °C 3.3 V and ff −40 °C 3.6 V), and even a sweep from vd = 0 advanced
  only 0.25 V per minute with gmin stepping at each restart (singular nodes in the disabled bandgap core of
  `bias_gen_pd`, `xg.xbg.n0[1]`); with rshunt the branch 0 … +3.3 V takes 3 s. Effect, measured by the `check` step
  (the same 0 … ±1 V sweeps with and without rshunt at ss / tt × −40 / 27 °C × 3.0 / 3.3 V, 8 + 8 runs): INL equal
  within 0.002 mV, gain within 1e-5, offset within 0.001 mV (`tables/crosscheck.md`), i.e. none at the precision
  reported here.
- D2S sweep in two branches from vd = 0 instead of one sweep from −3.3 V: the single sweep stalled at two cold PVT
  points (above).
- Round trip: `.option gmin=1e-12` as the designer's deck; `rshunt=1e12` added for the PEX pads only.

## Views

- **schematic**: CACE's xschem netlist of the pad schematic (design commit 91a7da8b), as in the committed CACE runs.
- **KLayout-extracted** (round trip only): the pads' `netlist/layout/<cell>_klayout.cir` at 9052bd35, as the designer's
  tier-1 deck uses them (converted by its `run_tier1.wrapped()`).
- **magic PEX**: magic C-coupled extraction (EXT_MODE 2) of the taped-out layout, prepared as the S2D Makefile's
  `sim-cace CACE_SOURCE=pex` (capacitor-only nodes tied to iovss by 1 TΩ, `vss` tied to `iovss` by 1 Ω as the
  sheet's Rsub). S2D: `netlist/pex/sg13cmos5l_IOPadSingle2Diff_magic_pex_2.spice` of the design repository at
  91a7da8b (2026-11-05, extracted from the same GDS). D2S: `../d2s_pex/sg13cmos5l_IOPadDiff2Single_magic_pex_2.spice`
  of this repository (LVS-checked there), with ngspice option `rshunt=1e12` as in `../d2s_pex` pass 2 (without it the
  D2S PEX operating point does not converge). Only the pad cell is extracted; bias_gen_pd and en_ctrl_3v3 stay
  schematic. At DC a C-coupled extraction adds only capacitors, so schematic and PEX curves are expected to agree
  closely; they do (results.md).

## Reproduce

```
verification/c2_gaps/dc_curves/run.sh [<work_dir>] [fetch|s2d|d2s|rt|vrefvcm|check|plots|all]
```
from a checkout of this repository (default work_dir `./_work` next to the script, not committed; default `all`).
`fetch.sh` downloads only the needed paths of the design repository (shallow, blobless clone; `git archive` of commit
91a7da8b67ac56a26c605501146667a1fde28c32 for the pads / CACE / schematics, 9052bd35928c6d40344e8e686c9abbe736bfadb9
for the slot tier-1 decks). Parallel ngspice runs: `JOBS` (default 3). Raw sweeps stay in `<work_dir>/out/`
(gzipped CSV per group, not committed); `plots/`, `csv/`, `tables/` here are regenerated from them.
Wall clock in this session (4 CPUs, 3 parallel ngspice): S2D 45-run grid 2 min (schematic), 3 min (PEX); D2S 45-run
grid about 1.5 / 2.5 min (schematic / PEX) per group; round trip 15 runs 6 min; `s2d_vrefvcm` (288 runs) 15 min; all
steps together about 42 min.

Reproduction check (2026-11-24/25): `run.sh` run from scratch in a fresh work folder, from a copy of the scripts
(fetch … rt in one go; vrefvcm, check, plots resumed after a container restart): every file in `csv/` and `tables/`
came out byte-identical to the ones here, and the same 36 plot files were written.

## Files

| file | what |
|---|---|
| `run.sh` | everything, in steps |
| `fetch.sh` | design-repository paths at the two commits |
| `mkgroups.py` | writes the DC-sweep template and the CACE yaml of the sweep groups next to a pad's own yaml |
| `cace_dc.sh` | runs sweep groups with CACE on the schematic or PEX view, then `collect.py` |
| `collect.py` | collects the per-run `wrdata` sweeps of a group into one gzipped CSV (work folder) |
| `common.py`, `s2d.py`, `d2s.py`, `rt.py`, `vrefvcm.py` | analysis, tables, plots (S2D, D2S, round trip, S2D vs vref / vcm) |
| `roundtrip.py`, `jobs_rt.txt` | round-trip decks (the designer's tier-1 slot deck with the chosen pad view) and the job list |
| `crosscheck.py` | compares with the committed CACE CSVs (`tables/crosscheck.md`) |
| `csv/*_summary.csv` | one row per run: gain, offset, INL, range ends, … |
| `tables/*.md` | generated tables (copied into results.md) |

## Tool versions

- `ngspice -v`: `ngspice-47 : Circuit level simulation program` (KLU compiled in), IHP OSDI models of the PDK
  (`.spiceinit` of the PDK, written by CACE into each run folder).
- CACE 2.11.0, XSCHEM 3.4.8RC (netlisting), magic 8.3.685 (not run here: the PEX netlists are the existing ones),
  Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2, PyYAML 6.0.3.
- PDK `/foss/pdks/ihp-sg13cmos5l` → IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e (2026-10-14).
- Design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single: 91a7da8b67ac56a26c605501146667a1fde28c32
  (pad macros, CACE yaml / templates / committed results, S2D PEX netlist), 9052bd35928c6d40344e8e686c9abbe736bfadb9
  (slot tier-1 decks). This repository: `pads/`, `../d2s_pex/` as of commit 50a7eff.

## What this does NOT show

- No mismatch / Monte Carlo: systematic (corner) behaviour only; offsets here are systematic offsets. Mismatch is
  covered by the committed CACE `mm_params` groups of both pads (not repeated here) and is not in these curves.
- Resistor corners: `res_typ` only (the S2D gain depends on resistor ratios, not on the sheet value; CACE
  `dc_params` covers `res_bcs` / `res_wcs`).
- No package, bond wire, ESD event, or source / load other than the CACE testbench's.
- C-coupled PEX only (no wire resistance), and DC only: the PEX capacitors do not act at DC.
- Bias from the harness iDAC (5 µA, sel 0) in the pad sweeps, as in the CACE runs, not the slot's bandgap; the
  pad sweeps use fixed vref / vcm (S2D 0.5 / 1.2 V and 0.49 / 1.26 V; D2S 1.65 V and 1.26 V), not the replica's PVT
  dependence. Only the round trip has the slot's own bias and replica (and there the other blocks are the designer's
  KLayout-extracted / schematic views, not magic PEX).
- Round trip: default mode only, pad out unloaded (1 GΩ) as the designer's deck, five PVT points.
- The S2D range vs vref / vcm (section 4 of results.md) is schematic only and covers ss / tt / ff.
- No transient, AC or noise behaviour: DC transfer only.
