<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# D2S pad: full CACE suite re-run on the taped-out schematic

**IHP sg13cmos5l schematic simulation** of `sg13cmos5l_IOPadDiff2Single` (D2S pad, `s7_an[1]`), all 15 parameter
groups of its CACE file, run on 2026-11-25. Old vs new: **[results.md](results.md)**.

Status: complete (2026-11-25, 02:52 … 03:24 UTC). All 189 runs of the 15 groups have results; drive_params needed the
solver aid rshunt=1e12, every other group ran as the templates are.

## Outcome (numbers: results.md)

- The simulated netlist is the taped-out cell (below). Changes vs the committed results > 2 %: bias currents up in
  every DC group (IqP / IqN +3.4 … +5.4 %, Iio +1.8 … +3.6 %, Imin +6.4 … +9.5 %; the same in Iio_end, mm IqP,
  Isc_snk +3.2 %), systematic offset −8 … −14.5 % (µV level), INL per run −9 … +2.6 %, Zout 1 kHz −3 … −17 %,
  Zout 1 MHz −2.5 %, peaking at 300 pF / 1 nF −1.7 … −8 %, settling (fall, ss 300 pF −23 %), turn-on time +15 / +48 /
  +53 % (sel 0 / 1 / 2), glitches, nA-level power-down leakage; gain, bandwidth, PSRR, CMRR, slew rate, THD, noise
  and output swing within 2 % (one bandwidth −2.1 %).
- Working limits: 78 of 79 CACE summary rows inside (committed: 79 of 79); outside: **mm_params Gain − mismatch,
  min 0.48877 < 0.49** (one of 30 Monte Carlo iterations, 3.1 σ below the mean).
- mm_params has per-iteration data for the first time (Vos σ 6.28 mV over 30 iterations).
- Against this run, the magic PEX results of ../d2s_pex show no DC current / INL / drive shift (≤ 0.75 %): the
  +3 … +5 % current shifts reported there were the stale schematic reference. The layout effects that remain:
  bandwidth and slew rate about −11 %, CMRR 1 kHz median 125 → 109 dB, Zout +8 %, settling and t_on about +10 % (median),
  integrated noise −4.5 %.
- The regenerated data sheet (candidate) drops the hand-added "Warning (found 2026-11-25)" block of the current
  sheet (it described the stale results) and keeps its Figures section; the index in
  `docs/chipalooza2_as_taped_out/datasheets/README.md` still says "79 of 79" and "results predate the layout" for this
  sheet (not changed here).

## Why

The committed schematic CACE results of the D2S pad (design repository
tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single, `macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/`,
present at commit 91a7da8b67ac56a26c605501146667a1fde28c32) were last written on 2026-10-21, while the D2S schematic
changed until 2026-11-03 (layout backannotation, bias-tree dummies, vss / iovss tie). The cross-check in
[../ac_tran](../ac_tran/results.md) (section 4, `tables/crosscheck.md`) re-ran the unchanged templates on the
schematic at 91a7da8b and found 24 values more than 2 % off the committed ones (Zout at 1 kHz down to −14 %, t_on up
to +53 %), while the same method reproduced the S2D results and the D2S PEX results exactly. The data sheet
`docs/chipalooza2_as_taped_out/datasheets/sg13cmos5l_IOPadDiff2Single.md` was generated from those stale results.
This folder re-runs every group on the current schematic and regenerates the data sheet from the new results.

## Which netlist, and why it is the taped-out one

CACE 2.11 always regenerates the schematic netlist (`cace_regenerate.py`, `regenerate_schematic_netlist`: xschem
`-n -s -r -x -q --tcl "set top_is_subckt 1"` in `macros/<cell>/schematic/xschem` with the project xschemrc). The
`netcheck` step of `run.sh` netlists the schematic of commit 91a7da8b exactly that way and compares it with the
taped-out cell's netlist `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.spice` of this repository (the
LVS netlist that the taped-out GDS matches: `../d2s_pex/lvs_summary.txt`, netgen "Circuits match uniquely", 76 = 76
devices, 36 = 36 nets). Result ([netcheck.txt](netcheck.txt)):

- the pad netlist is, below its 4-line provenance header, byte-identical (same sha256) to the design repository's
  `macros/sg13cmos5l_IOPadDiff2Single/netlist/schematic/sg13cmos5l_IOPadDiff2Single_magic.spice` at 91a7da8b;
- the CACE netlist and the pad netlist are identical line by line (all subcircuits: bias_tree_pd, d2s_mpdda_pd,
  d2s_out_p / d2s_out_n, d2s_sp2k, unit_r2, …, every device with its parameters), apart from the xschem `**`
  path comments and **one line**: `Rsub iovss vss 1` in the top cell of the CACE netlist. Rsub carries
  `lvs_ignore=open` in the schematic (the vss band and the iovss ties share the p-substrate; LVS sees one net), so
  it is absent from the LVS netlist by construction; the PEX view of `../d2s_pex` adds the same 1 Ω tie
  (`pex_add_port.py … vss iovss 1`).

So the schematic simulated by CACE at 91a7da8b is the taped-out cell (plus the simulation-only substrate tie), and the
suite is run on it. The CACE file and templates are those of 91a7da8b too (since 2026-11-03 they place en_ctrl_3v3
and bias_gen_pd next to the cell, schematic, as in ../ac_tran and ../d2s_pex).

## Method

- `run.sh` `fetch`: shallow, blobless clone of the design repository, `git fetch --depth 1` of 91a7da8b, `git
  archive` of only the D2S macro (schematic, CACE yaml / templates / committed results, netlist), the schematic
  folders of the macros its xschemrc lists, and `scripts/cace`.
- `cace_sch.sh`: per group `cace <yaml copy> -s schematic -p <group> -j 3` (the copy differs from the committed yaml
  only in its runs / docs folders), templates **unchanged** (restored from a pristine copy and renetlisted before
  every group, so a solver aid can never carry over), `XSCHEM_USER_LIBRARY_PATH` set to the other macros' xschem
  folders as in ../d2s_pex. CSV per group with the design repository's `scripts/cace/cace_to_csv.py`; for
  `mm_params` with `mm_collect.py` (the same CSV format; CACE 2.11 nests the iterations one level deeper,
  `parameters/mm_params/run_0/run_<k>/`, which cace_to_csv.py does not find: that is why the committed
  mm_params.csv has a header only; as ../replica_bias/mc_collect.py). CACE's `summary.md` of the group is kept as
  `summary_<group>.md`.
- Solver aid: ngspice `.option rshunt=1e12` (1 TΩ from every node to ground) only for a group that does not converge
  without it: `RSHUNT_GROUPS` in run.sh, default `drive_params`, the only such group (first pass without it: 3 of
  10 runs without result, results.md section 1; its effect on the 7 runs that converge both ways ≤ 0.0002 %). tb_pd
  sets its own `rshunt=1e14` in the committed template (left as is). Per group: results.md section 1 and the comment
  header of `csv/summary_<group>.md`. The first drive_params pass (no aid) was run with `cace_sch.sh` alone (= `run.sh sim`
  with `RSHUNT_GROUPS=""`); its hung run (tt −40 °C) was stopped by hand (`kill` of that ngspice process after 15.6 min), so
  this pass is not part of `run.sh all`.
- `compare.py`: old (committed) vs new per group and quantity: min / median / max and the largest per-run change
  over runs with equal conditions; flag > 2 % (`tables/compare_committed.md`). Also the magic PEX results of
  ../d2s_pex against this re-run (`tables/compare_pex.md`): ../d2s_pex compared PEX with the stale schematic results.
- `datasheet`: `docs/chipalooza2_as_taped_out/datasheets/tools/make_datasheet.py` on the new CSVs (the `#` lines
  stripped into a work folder: its CSV reader expects none) with `datasheet_intro.md` / `datasheet_notes.md`;
  `ds_post.py` then inserts the hand-made Figures section of the current sheet (its marker asks to keep it) and
  replaces the generator's provenance lines ("from the committed CACE files; no simulation was run") by this run's.
  No number is edited. Result: [sg13cmos5l_IOPadDiff2Single.regenerated.md](sg13cmos5l_IOPadDiff2Single.regenerated.md);
  its links are written for `docs/chipalooza2_as_taped_out/datasheets/`, where it is meant to replace the current
  sheet.

## Groups

Groups, runs, solver aid and wall clock: results.md section 1 (15 groups, 189 runs, about 6 min of simulation in
total with 3 parallel ngspice runs, plus 15.6 min of the drive_params run without aid that made no progress).

## Reproduce

```
verification/c2_gaps/d2s_schematic_rerun/run.sh [<work_dir>] [fetch|netcheck|sim|csv|compare|results|datasheet|all]
```
from a checkout of this repository (default work_dir `./_work` next to the script, not committed). The CACE run folder of
every group is kept in `<work_dir>/runs/<group>` (not committed). `JOBS` (default 3) = parallel ngspice runs per group.

## Files

| file | what |
|---|---|
| `run.sh` | everything, in steps |
| `cace_sch.sh` | runs CACE groups on the schematic (templates unchanged; optional rshunt) |
| `mm_collect.py` | CSV of a group collated over Monte Carlo iterations (CACE 2.11 nesting) |
| `compare.py` | old vs new per quantity (`tables/compare_committed.*`: committed vs this run; `tables/compare_pex.*`: this run vs ../d2s_pex) |
| `results_head.md` | hand-written part of results.md (`run.sh results` appends the two tables) |
| `ds_post.py` | Figures section and provenance lines of the regenerated data sheet |
| `datasheet_intro.md`, `datasheet_notes.md` | intro / notes passed to make_datasheet.py |
| `netcheck.txt` | CACE schematic netlist vs taped-out LVS netlist |
| `csv/<group>.csv` | per-run results (cace_to_csv.py format: conditions, then the yaml variables in SI units whatever the [unit] label says; 2-line SPDX header) |
| `csv/summary_<group>.md` | CACE's summary of the group (working limits, min / typ / max, status) |
| `csv/drive_params_norshunt.csv` | drive_params without the solver aid (7 of 10 runs) |
| `sg13cmos5l_IOPadDiff2Single.regenerated.md` | data-sheet candidate |

## Tool versions and sources

- ngspice-47 (KLU), IHP OSDI models of the PDK; CACE 2.11.0; XSCHEM V3.4.8RC; Python 3.13.18, PyYAML 6.0.3 (CACE
  itself runs on the system Python 3.12).
- PDK `/foss/pdks/ihp-sg13cmos5l` (IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e).
- Design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single 91a7da8b67ac56a26c605501146667a1fde28c32.
- This repository: `pads/sg13cmos5l_IOPadDiff2Single/` (taped-out netlist), `../d2s_pex/csv` (PEX results), data
  sheet generator, as of commit 321ba06.
