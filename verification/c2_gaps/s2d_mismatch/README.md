<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# S2D pad: Monte Carlo groups re-run with the per-run data kept

**IHP sg13cmos5l simulation** of `sg13cmos5l_IOPadSingle2Diff` (S2D pad, `s7_an[0]`): the CACE groups `mm_params`
(local mismatch: input offset, gain, output-CM error; 100 iterations), `ac_mm_params` (PSRR / CMRR under mismatch,
30 iterations) and `mc_params` (process MC, 30 iterations) on the taped-out schematic, `mm_params` also on the magic
C-coupled PEX netlist, and one `dc_params` run as a check of the committed results; run on 2026-11-25.
Numbers and reading: **[results.md](results.md)**.

Status: complete (2026-11-25, 03:48 … 03:58 UTC). 395 of 395 runs have a result (100 + 30 + 30 + 135 schematic,
100 PEX); no solver aid.

## Outcome (numbers: results.md)

- The simulated schematic netlist is the taped-out cell (below).
- The committed mismatch / MC summaries are **stale**: written 2026-10-26 (pre-layout design), while the S2D
  schematic changed until 2026-11-05. The other committed schematic results are not: `dc_params` re-run here
  reproduces all 135 committed runs exactly.
- σ on the taped-out schematic (100 runs): input offset **5.25 mV**, gain **0.0167** (0.83 %), output CM error
  **11.0 mV** (mean 7.9 mV); every run inside the working limits. PEX with mm_ok=1: 6.15 mV, 0.0164, 12.7 mV
  (σ confidence intervals overlap the schematic's).
- PSRR / CMRR under mismatch (30 runs): worst PSRR iovdd 83.8 dB (1 kHz) / 82.3 dB (100 kHz), iovss 83.4 / 66.0 dB,
  CMRR 90.1 dB (1 kHz); every run inside the working limits.
- Process MC: no offset (−8.6 nV systematic, σ 0.13 nV), gain σ 8.6 ppm, CM error σ 0.17 mV; as the committed
  summary.

## Why

The committed CSVs of the three Monte Carlo groups in the design repository
(tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single, `macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/sg13cmos5l_IOPadSingle2Diff/`,
commit 91a7da8b67ac56a26c605501146667a1fde28c32) have a header only: CACE (2.11 here; the design README names 2.13.0
for the 2026-10-25/26 run) nests the iterations of a collated group one level deeper (`parameters/<group>/run_0/run_<k>/`)
than `scripts/cace/cace_to_csv.py` looks. Only CACE's min / typ / max summary survived, so the data sheet
`docs/chipalooza2_as_taped_out/datasheets/sg13cmos5l_IOPadSingle2Diff.md` can show no σ and no histogram ("CACE summary
values (per-run CSV not committed)"). This folder re-runs those groups with the per-run data collected
(`mm_collect.py`, as ../d2s_schematic_rerun/mm_collect.py and ../replica_bias/mc_collect.py).

## Which netlist, and why it is the taped-out one ([netcheck.txt](netcheck.txt))

CACE 2.11 regenerates the schematic netlist on every call (xschem `-n -s -r -x -q --tcl "set top_is_subckt 1"` in
`macros/<cell>/schematic/xschem` with the project xschemrc). `run.sh netcheck` netlists the schematic of 91a7da8b
that way and compares it with `pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.spice` of this repository:

- the pad netlist is, below its 4-line provenance header, byte-identical (sha256 5a4e67f9…) to the design's
  `netlist/schematic/sg13cmos5l_IOPadSingle2Diff_magic.spice` (the LVS netlist);
- the CACE netlist equals it line by line (122 lines without the xschem `**` comments) except for **one line**,
  `Rsub iovss vss 1` in the top cell: Rsub carries `lvs_ignore=open` in the schematic (vss and iovss share the
  p-substrate), the same simulation-only tie as in the D2S pad; the PEX netlist has the same tie (`Rport_vss vss iovss 1`,
  `pex_add_port.py`);
- every MOSFET / rhigh / rppd instance of the CACE netlist carries `mm_ok=1` (75 instances, none without);
- the pad GDS `pads/…/sg13cmos5l_IOPadSingle2Diff.gds` is byte-identical (sha256 f4b0e073…) to the design's
  `layout/klayout/sg13cmos5l_IOPadSingle2Diff.klay.gds`, from which the PEX netlist was extracted (2026-11-05). The
  design's magic / netgen LVS of that GDS against the LVS netlist (`verification/lvs/…magic.lvs/…lvs.out`, not re-run
  here): 76 = 76 devices, 37 = 37 nets, "Netlists match with 7 symmetries with property errors"; the property errors
  are `mm_ok` (absent in the extraction) and w / l of the two antenna diodes swapped (27.78 × 1.26 µm, same area);
  "Top level cell failed pin matching" only because `vss` has no pin of its own in the layout (substrate).

## Staleness ([staleness.txt](staleness.txt))

From a blobless clone with full history (`run.sh history`): the committed `mm_params`, `ac_mm_params` and `mc_params`
CSV / summary files were last written by 6229797 on 2026-10-26 00:55 +0100. After that, 8 commits changed
`macros/sg13cmos5l_IOPadSingle2Diff/schematic/xschem` (last 668cf59, backannotation, 2026-11-04 17:47, and 49bd7dc,
2026-11-05 01:19, which only adds the `_pex` symbol). So the committed mismatch results describe the pre-layout
design and are stale. The other schematic groups (`dc_params` … `enable_params`) were committed 2026-11-05 01:22 …
01:48, after every change of the S2D schematic and of the macros on its library path (last 668cf59), and the
`dc_params` re-run here matches the committed `dc_params.csv` exactly in all 135 runs and 5 quantities
(results.md section 4).

## Method

- `run.sh fetch`: `git clone --depth 1 --filter=blob:none --no-checkout`, `git fetch --depth 1 origin 91a7da8b…`,
  `git archive` of only the S2D macro's schematic, CACE yaml / templates / committed results, netlists, LVS report and
  GDS, the schematic folders of the macros its xschemrc lists, and `scripts/cace`.
- `cace_run.sh <work> <out> schematic <groups>`: as ../d2s_schematic_rerun/cace_sch.sh: per group `cace <yaml copy> -s
  schematic -p <group> -j 2` (the copy differs from the committed yaml only in its runs / docs folders), templates
  **unchanged** (restored and renetlisted before every group), `XSCHEM_USER_LIBRARY_PATH` set to the other macros'
  xschem folders as in the design Makefile's `sim-cace`. Seeds as in the template: `SEED = 12345 + iteration`.
- `cace_run.sh <work> <out> pex mm_params`: as the design Makefile's `sim-cace CACE_SOURCE=pex` (yaml copy with
  `netlist: cace/netlist_pex`, `layout: cace/layout_pex`; the prepared netlist newer than the layout, so CACE logs
  "Skipping extraction of pex netlist"), with one change: the design's
  `netlist/pex/sg13cmos5l_IOPadSingle2Diff_magic_pex_2.spice` is prepared with `scripts/cace/pex_for_sim.py --mm-ok
  --tie iovss 1e12` (the Makefile uses only `--tie iovss 1e12`). `--mm-ok` appends `mm_ok=1` to the 221 extracted
  MOSFET / rhigh / rppd instances (`csv/pex_for_sim.log`); magic does not write it, and without it the PDK draws no
  local mismatch, which is why the Makefile leaves the mismatch groups out for pex ("vacuous"). The testbench parts
  outside the cell (`en_ctrl_3v3`, `bias_gen_pd`, harness iDAC) are the same schematic blocks in both views.
- `mm_collect.py`: per-run CSV of a group, iterations found recursively; also used for `dc_params` (same rows as
  `cace_to_csv.py`). Unscored (`null`) columns of `ac_mm_params` carry the template's names (`Acl_dB(unscored)`,
  `f3dB(unscored)`, `CMvdd_1k(unscored)`) instead of `cace_to_csv.py`'s `None` (which repeats one value).
- `analyze.py`: mean, σ (sample), its 95 % confidence interval (chi-square, Wilson–Hilferty), min, median, max,
  mean ± 3σ, inside the working limits; the dB rejections also as linear input-referred coupling; schematic vs PEX
  correlation per seed; the committed CACE summaries vs this run's CACE summaries and CSV; committed vs re-run
  `dc_params.csv`; histograms (150 dpi, style of ../replica_bias/results/pad_ref_rb_mc_hist.png).
- `run.sh csv` adds SPDX headers to the CSVs and summaries; `run.sh results` writes results.md from
  `results_head.md` and the two generated tables.

## Reproduce

```
verification/c2_gaps/s2d_mismatch/run.sh [<work_dir>] [fetch|history|netcheck|sim|csv|analyze|results|all]
```
from a checkout of this repository (default work_dir `./_work` next to the script, not committed); about 10 min of
simulation with `JOBS=2` (2 ngspice runs at a time). `SIM_SCH` / `SIM_PEX` choose the groups of the `sim` step
(default `mm_params ac_mm_params mc_params dc_params` / `mm_params`). The CACE run folder of every group is kept in
`<work_dir>/runs/<group>[_pex]` (not committed). This run: work_dir in the session scratch space, `run.sh <work> fetch`,
`history`, `netcheck`, `sim` with `SIM_SCH=mm_params SIM_PEX=""`, then `sim` with
`SIM_SCH="ac_mm_params mc_params dc_params"` (and the default `SIM_PEX`), then `csv`, `analyze`, `results`.

## Files

| file | what |
|---|---|
| `run.sh` | everything, in steps |
| `cace_run.sh` | CACE groups on the schematic or the PEX netlist (with mm_ok=1) |
| `mm_collect.py` | per-run CSV of a group (CACE 2.11 nesting of collated iterations) |
| `analyze.py` | statistics, comparison, histograms |
| `results_head.md` | hand-written part of results.md |
| `netcheck.txt` | CACE schematic netlist vs taped-out LVS netlist; GDS identity; design LVS summary |
| `staleness.txt` | commit dates of the committed results vs the schematic changes |
| `csv/<group>.csv`, `csv/mm_params_pex.csv` | per-run results (conditions, then the yaml variables; values in V / A / Hz / dB whatever the [unit] label says, as cace_to_csv.py; 3-line comment header) |
| `csv/summary_<group>[_pex].md` | CACE 2.11's summary of this run (working limits, min / typ = median / max, status) |
| `csv/pex_for_sim.log` | what pex_for_sim.py changed in the PEX netlist |
| `tables/stats.md`, `tables/stats.csv` | statistics per group, view, quantity |
| `tables/compare_committed.md` | committed summaries vs this run; committed vs re-run dc_params |
| `figures/s2d_mm_hist.png` | offset, gain, CM error: schematic (filled) and PEX (outline), 100 runs each |
| `figures/s2d_ac_mm_hist.png` | PSRR iovdd / iovss at 1 / 100 kHz, CMRR 1 kHz, 30 runs |
| `figures/s2d_mc_hist.png` | process MC: offset, gain, CM error, 30 runs |

## Tool versions and sources

- ngspice-47, IHP OSDI models of the PDK (templates: default sparse solver); CACE 2.11.0 (system Python 3.12);
  XSCHEM V3.4.8RC; Python 3.13.18 with PyYAML 6.0.3, matplotlib 3.11.2.
- PDK `/foss/pdks/ihp-sg13cmos5l` (IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e).
- Design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single 91a7da8b67ac56a26c605501146667a1fde28c32.
- This repository: `pads/sg13cmos5l_IOPadSingle2Diff/` (taped-out netlist and GDS), branch `chipalooza2-documentation`.
