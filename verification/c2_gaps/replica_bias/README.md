<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Replica bias gaps: pad_ref_rb post-layout and mismatch, bias_dist_pd copy accuracy

IHP sg13cmos5l simulation. Gap-filling characterization (2026-11-23) of two blocks of slot 7 as taped out
(slot repository commit `158afc5afab0056bd6d216a4db3833e34a364949`, design repository
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single)
commit `9052bd35928c6d40344e8e686c9abbe736bfadb9`). Results and their reading: [results.md](results.md).

## What and why

| gap | what was there | what this adds |
|---|---|---|
| `pad_ref_rb` post-layout | schematic CACE, 8 / 8 groups (2026-11-07); layout v2 LVS-clean, used extracted in the slot tier-1 run; no PEX CACE suite | magic C-coupled PEX of the cell as taped out, CACE groups `vcm_dc_params`, `vcm_dc_3v0_params`, `vref_room/hot/cold_params`, `pd_params` on the PEX view, compared with the committed schematic CSVs (and a schematic rerun with the same tools) |
| `pad_ref_rb` mismatch | `mm_params.csv` with a header only; CACE summary only | the same `mm_params` group (schematic, tt_mismatch, 27 °C, 3.3 V, 100 iterations) with the per-run CSV and statistics |
| `bias_dist_pd` | truth-table simulation only (tt, 27 °C) | copy ratio per output over 5 corners × −40 / 27 / 125 °C at 5 µA, output 0.5 … 2.5 V; leakage of disabled outputs; a mismatch MC of the copy ratio; schematic and magic C-coupled extraction |

## Layout used

The cells `pad_ref_rb` and `bias_dist_pd` were taken (with their subcells) from `final/gds/slot_7.gds` of this
repository (blob `7fb01b9d…`, the same at `158afc5` and at the documentation commit `9d3e441`; sha256
`469f2327…69c05`) and compared by a flattened per-layer XOR plus text comparison (KLayout, `gds_cell_compare.py`)
with the macro GDS `macros/<cell>/layout/klayout/<cell>.klay.gds` at the design commit: **identical** for both
(pad_ref_rb: 39 layers, 7188 polygons, 73.8 × 76.26 µm; bias_dist_pd: 39 layers, 5291 polygons;
`results/gds_compare.log`). The extraction was run on the cell cut from **slot_7.gds**.

## Method

- Extraction as the design repository's `make magic-pex EXT_MODE=2` (macro Makefiles): `sak-pex.sh -m 2 -n <cell>_pex`
  (magic, C-coupled), pins put in the symbol's order (`sak-pin-reorder.py` on `<cell>.sym` with
  `type=primitive`), then `scripts/cace/pex_for_sim.py --tie vssh 1e12` (0 capacitor-only nodes found in either cell).
  Not applied: the S2D pad's `pex_add_port.py` (adds a substrate-joined `vss` port to the S2D pad); in `pad_ref_rb`
  and `bias_dist_pd` magic extracts the substrate as `vssh`, which is a port, so there is no separate substrate node.
- PEX CACE as `macros/sg13cmos5l_IOPadSingle2Diff/Makefile` `sim-cace CACE_SOURCE=pex` (design commit): a copy of
  the yaml with its own `runs` / `netlist` / `documentation` folders and `layout: cace/layout_pex`, the prepared netlist
  at `cace/netlist_pex/pex/pad_ref_rb.spice` (newer than the layout, so CACE logs "Skipping extraction of pex netlist.
  Up to date."), `cace -s pex -p <group> -j 1`, CSV by `scripts/cace/cace_to_csv.py`; `run_cace.sh` here.
- Netgen LVS of both extracted netlists (capacitors removed, `mm_ok=1` removed from the schematic side) against the
  source netlists of the design commit: "Circuits match uniquely" for both (`results/lvs_pex.log`; pad_ref_rb 33
  devices / 16 nets after netgen's parallel merging, bias_dist_pd 75 / 50).
- Mismatch MC: CACE `mm_params` (`collate: iterations`, `SEED = 12345 + iteration`). CACE 2.11 puts the iterations one
  level deeper (`parameters/mm_params/run_0/run_<k>/`) than `cace_to_csv.py` looks, which is why the committed
  `mm_params.csv` has a header only; `mc_collect.py` reads them recursively. The netlisted testbench carries `mm_ok=1`
  on the DUT's devices (45 instances in the sheets) and on `bias_gen_pd`'s 2 devices and the gates of `en_ctrl_3v3`;
  the harness iDAC mirror (2 devices in the template's SOURCES block) has no mismatch.
- bias_dist_pd (`bias_dist_copy.py`, plain ngspice decks, not CACE): vddh = 3.3 V, an ideal 5 µA sourced into `iin0`
  (`en_in0` = 1, the other inputs off), all four outputs held at one voltage `vc` through a 0 V ammeter each, `vc` swept
  0.5 … 2.5 V in 50 mV; ratio = I(iout<j>) / 5 µA. Cases: on (`en_3v3` = 1, all `en_out` = 1), output switch off
  (`en_3v3` = 1, `en_out` = 0, input on), block off (`en_3v3` = 0). While the input switch is open, the ideal source is
  clamped by a diode to 2.6 V. Views: the source netlist (`bias_dist_pd.spice` + `hv_logic.spice`, "schematic") and the
  magic C-coupled extraction of the slot_7.gds cell ("magic_pex_2"). Mismatch MC (`bias_dist_mc.py`): tt_mismatch,
  27 °C, `mm_ok=1` added to every MOSFET by `pex_for_sim.py --mm-ok`, 100 runs, `SEED = 12345 + iteration`.
- `JOBS` simulations at a time (default 1: CACE `-j 1`, PEX and schematic one after the other, one ngspice deck at a
  time; `JOBS=2`: PEX and schematic side by side, MC `-j 2`, 2 decks at a time). The committed results come from a
  `JOBS=1` run.

## Reproduce

```
cd verification/c2_gaps/replica_bias
JOBS=1 ./run.sh [<work_dir>]     # 8 min with JOBS=2, longer with JOBS=1; rewrites results/
```

`run.sh` fetches the design files at the commit (`git clone --depth 1 --filter=blob:none --no-checkout`,
`git fetch --depth 1 origin 9052bd35…`, `git archive FETCH_HEAD <paths> | tar x`), cuts and XORs the cells, extracts,
runs LVS, CACE (PEX and schematic), the MC, the bias_dist_pd decks, stamps SPDX headers on the generated text files and
writes `results/tables.md` and the plots (`analyze.py`). Environment: `PDK_ROOT=/foss/pdks PDK=ihp-sg13cmos5l`
(`PDKPATH` is set by run.sh; sak-pex.sh needs it).

## Tool versions

| tool | version |
|---|---|
| ngspice (`ngspice -v`) | ngspice-47, compiled with KLU; the decks and CACE templates use the default sparse solver ("Using SPARSE 1.3") |
| magic (`magic --version`) | 8.3.685 |
| CACE (`cace --version`) | 2.11.0 |
| xschem | 3.4.8RC |
| KLayout | 0.30.12 |
| Netgen | 1.5.324 |
| IHP Open PDK | `/foss/pdks/IHP-Open-PDK` commit `df4c5054ee8ca481c3eb873687274f28cdb50b1e` (2026-10-14), OSDI PSP 103 models |
| sak-pex.sh / sak-pin-reorder.py | as installed in `/usr/local/bin` (IIC-OSIC-TOOLS) |

## Files

| file | content |
|---|---|
| `run.sh` | everything, from the fetch to the tables |
| `run_cace.sh` | CACE groups on the schematic or PEX view (S2D pad's `sim-cace CACE_SOURCE=pex` scheme) |
| `gds_cell_compare.py` | KLayout: XOR of one cell between two GDS files, writes the cell as its own GDS |
| `lvs_check.sh` | netgen LVS of an extraction (capacitors removed) against the source netlists |
| `mc_collect.py` | per-iteration CSV and statistics of CACE `mm_params` |
| `bias_dist_copy.py`, `bias_dist_mc.py` | bias_dist_pd decks (copy ratio / leakage; mismatch MC) |
| `analyze.py`, `spdx_stamp.py` | tables and plots; SPDX headers on generated files |
| `results/pex/*_magic_pex_2.spice` | the two extracted netlists (C-coupled, symbol pin order; 9 kB, 14 kB) |
| `results/cace_pex/`, `results/cace_schematic/` | per-run CSV and CACE summary per group, PEX view and schematic rerun |
| `results/mc/` | `mm_params_runs.csv` (100 runs), `mm_params_stats.csv`, CACE summary |
| `results/bias_dist/` | `bias_dist_copy_<view>.csv` (all cases, corners, temperatures, vc points), `bias_dist_mc_<view>.csv` |
| `results/gds_compare.log`, `results/lvs_pex.log` | layout identity and LVS of the extractions |
| `results/tables.md` | the tables as generated (results.md quotes them) |
| `results/*.png` | MC histograms of vcm / vref; bias_dist_pd copy error vs output voltage |

CSV files start with two `#` SPDX lines; the readers here skip lines that start with `#`.

## What this does NOT show

- **No resistance.** The C-coupled extraction adds only capacitances; with the same devices (LVS match) a DC operating
  point cannot change, and every group run here is a DC operating point. The PEX-vs-schematic differences are at the
  numerical resolution (see results.md). Wiring resistance (full-RC, `EXT_MODE=3`) was not extracted; at the µA
  currents of these blocks it is not expected to matter, but that is not shown here.
- **No dynamics.** The capacitances matter for the enable time, the supply rejection and the kick-back of the pads'
  switching onto vcm / vref; none of the groups run here measures them (no AC or transient group exists in the
  pad_ref_rb yaml). `vcm_sel_params` (OA core / bandgap reference) and `mm_params` were not run on the PEX view
  (mismatch is vacuous on an extracted netlist without `mm_ok`).
- **No mismatch on the PEX view of pad_ref_rb**, and the pad_ref_rb MC is at one condition (tt 27 °C 3.3 V) with
  sel = 0 (harness iDAC, its mirror without mismatch); 100 runs estimate sigma to about ±7 % (1 sigma of the estimate; ±14 % at 95 % confidence).
- **bias_dist_pd**: an ideal input current and ideal output voltages, not the real loads (`pad_ref_rb`'s / the pads'
  `bias_tree` input diodes behind their own switches); one input enabled at a time (sums of several inputs not
  characterized); 3.3 V supply only; per-output differences come from mismatch only (the systematic ratio is the same
  for the four outputs in both views); the MC is at tt 27 °C only, does not include the source's mismatch, and does
  not include layout gradients.
- Magic reported 31 (pad_ref_rb) and 4 (bias_dist_pd) extraction warnings at default settings; they were not
  examined individually. LVS of the extracted netlists matches the source netlists.
- Not silicon: everything here is IHP sg13cmos5l simulation.
