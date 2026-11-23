<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Running log: slot 7 documentation (cloud session, 2026-11-22)

One row per step: what was asked or found, the command or source, the result. Times are not recorded; the order is the order of work.
The session's verbatim chat log stays in the source repository (`sudelbuecher/chatlog/2026-11-22_sonnet_submodule_urls_slot_docs_and_log_rules.md` on branch `sudel_buecher` of `tatzelbrumm/sg13cmos5l_ocd_chipalooza`) and is not copied into this repository; this file is the action log only.

| # | step | how | result |
|---|---|---|---|
| 1 | request: document slot 7 as taped out in November, from what the colleague's handover actually put on the tapeout; then collect the characterization data; keep chat log and running logs current | user message | scope: README for the circuits; candidates file for step 2 |
| 2 | read the examples file | `sudelbuecher/slots/documentation_examples.txt` (the user wrote `.md`; at that time the file was `.txt`; converted to `.md` later, row 15) | bandgap docs (biasgen `doc/`, tinyBGR README, slot 2 `sbcs` README) and a class-AB reference (slot 5 repo) as style examples |
| 3 | which slot 7 commit was taped out | `config.txt` `s7_version`; `git ls-tree` of `dependencies/slot_7` at tapeout commit `7eeb3cb` and at the tip | **taped out: `158afc5`** (v3 + tughra art). The gitlink at the tip (`055993f`, later the same day) is `c072679` (stage B test platform). Only slot 7 differs among the 21 pins |
| 4 | what is in the delivery repository at `158afc5` | shallow clone of `tatzelbrumm/sg13cmos5l_cm_slot7`, `git archive 158afc5` | README, `docs/{FOR_TIM,slot_7,PROGRESS}.md`, `final/{gds,lef,lib,vh}`, `pads/`, `netlist/`, `art/`, copies of `bg_core_pd` and `oa_core_pd` |
| 5 | is that what is in the chip | KLayout 0.30: load `gds/MPC9639.gds.gz`; take cell `slot_7`; flatten and merge per layer; XOR against `final/gds/slot_7.gds` of `158afc5` and of `c072679` | `158afc5`: XOR 0 on every layer; `c072679`: differs on 34 layers. Children are the six blocks (`YX_` prefix). Chip origin of `slot_7`: (1379.95, 2170.05) µm |
| 6 | the two pads in the chip | same method, pad cells vs `pads/*/*.gds` | both equal (XOR 0, bbox -0.62,0 to 80.62 × 180 µm); instances in `sg13cmos5l_padframe` |
| 7 | module hierarchy of `slot_7` | `klayout.db`, children of the top cell | `bg_core_pd`, `bias_dist_pd`, `pad_ref_rb`, `s7_ctrl`, `s7_doutpd`, `tughra_art`; **no `oa_core_pd`** (the macro is only a copy in the delivery repository) |
| 8 | README written | [README.md](README.md) first version | version, top level, pads, modules, modes, expected values, verification, files |
| 9 | user: "don't forget the tughra" | design repository `art/` (`verify_report.md`, `fill_test.md`, `build_stats.json`), chip data | tughra section: placement, layers, no-fill markers, **0 µm² filler inside the marker box in the chip**, TopMetal1 has 0 µm² in the box; picture rendered from the chip data into `pix/`; removed my unsourced "Ottoman sultan's monogram" line; corrected a wrongly worded TopMetal1 row after checking |
| 10 | step 2 inventory | `git ls-tree` on the design repository at `9052bd35` (v3) and `91a7da8b` (pads); READMEs of `bias_bg_pd`, `pad_ref_rb`, `en_ctrl_3v3`, `hv_logic`; `scripts/cace/*.py` headers; `tier1/results.txt` | [characterization_candidates.md](characterization_candidates.md): candidates per block, script base, caveats (none of the suites was checked against the taped-out netlist) |
| 11 | user: the tughra is an aside; the main task is the circuits with an electrical function; as an aside, which blocks were kicked off and in what state of readiness | C0 / C1 reports, `replica_bias_TASK.md`, macro READMEs, the chatlog index | README restructured: electrical function (section 2), readiness ledger (section 3), physical (4), verification (5), files (6), tughra (7, aside) |
| 12 | user: the glue logic built on short notice is as important | `netlist/slot_7.spice` at `158afc5` (`s7_ctrl`, `s7_doutpd`, `slot_7`), `en_ctrl_3v3` README, `tier1/modes.txt`, `CONCEPT.md`, RUNLOG rows 121–123 | [glue_logic.md](glue_logic.md): equations and truth table derived from the netlist by script (16 rows, asserts on the default and the no-enable case), switch matrix, static ties, `dig_out` pull-downs, verification table |
| 13 | consistency check on the ss −40 °C claim | `modes.txt` (FAILED lines) against the delivery README ("feed and ext pass") | not a conflict: DC does not converge for the manual modes; the power-up transients give feed 0.24 mV and ext 0.04 mV, and swap / mon stall at the bandgap start-up node (RUNLOG rows 121, 122). Both are stated in glue_logic.md §7 |
| 14 | index and pin correction | `slots/slot_7.md`, `slots/README.md` | taped-out vs tip gitlink stated; links point at `158afc5`; pin-check line added |
| 15 | user converted the examples file to `documentation_examples.md`; compared the example documents' headings (`slot_15`, `slot_5`, `slot_2` `sbcs`, biasgen `bandgap_v3.md`) with this README | headings of the shallow clones | the gap table in characterization_candidates.md §3: no per-block spec table, pin tables or pictures yet |
| 16 | user: first step is the existing characterizations as data sheets resembling the examples, emphasis on characterized quantities and CACE run summaries | extracted `macros/<cell>/verification/cace` and `scripts/cace` from the design repository with `git archive` into the scratchpad; looked at `spec_table.py` and the summary format | the per-group summaries repeat all parameters with *Skip* rows; `datasheets/tools/make_datasheet.py` reproduces the non-skipped rows per group with run counts and swept conditions from the yaml and CSV |
| 17 | user: "do not start additional runs for now" | none started: nothing on 2026-11-22 simulated; the generator only reads committed files | stated in every sheet |
| 18 | user: the data sheets pertain only to the circuit that was taped out | selection of cells (pads, `pad_ref_rb`, the shifter) with scope banners; excluded `bias_*`, `OgueyAebischerBias`, test-platform results from the sheets | gaps listed in `datasheets/README.md` (`bg_core_pd`, `bias_dist_pd`, `s7_ctrl`, `s7_doutpd`) |
| 19 | check: `pad_ref_rb` `mm_params` showed 0 runs | the committed `mm_params.csv` is header only | the generator now says so; the summary's min / typ / max are shown as CACE wrote them |
| 20 | slot-level sheet | `docs/slot7_hookup/tier1/results.txt`, `modes.txt` copied verbatim | `datasheets/slot_7_system.md` |
| 21 | user: the test platforms eventually matter; document the test platforms and their results | `docs/slot7_testplatform/{PLAN,SUMMARY}.md`, `macros/slot7_testplatform/testbenches/ngspice/results*/summary.md` at `efb80141`, delivery PROGRESS; tables embedded by script from the summary files | [test_platforms.md](test_platforms.md); found SUMMARY.md stale (says stage B not started) |
| 22 | user: no pass/fail criteria were specified (proof of concept); define parameters and min/typ/max ex post where no ranges exist | read-only look at CACE's *typ* (it is the **median** of the group: `Vcm` 1.295 V = median of 30 runs, mean 1.306 V) and at the CSV columns (unit labels such as `f3dB[MHz]` hold SI values) | generator extended: `## Specification (ex post facto, as characterized)` per view with min, typ at typical conditions, median, max, runs, corner of min / max; units inferred by matching the CSV to the summary; CACE limits renamed "designer's working limits" and statuses "vs working limit" |
| 23 | regenerate the four CACE sheets; consistency edits | `make_datasheet.py` on the committed files (no simulation) | `datasheets/*.md`; index, README and glue_logic wording changed from "pass" to "inside the working limits" |

## Findings to hand to the owner

1. **The gitlink of `dependencies/slot_7` at the tip of `tapeout_nov_2026` (`c072679`) is not the taped-out slot (`158afc5`).** A `git submodule update` on the tip gets the stage B test platform.
   Not changed here: the branch belongs to the harness owner.
2. The delivery README still describes `oa_core_pd` as placed in `slot_7.gds`; the taped-out hierarchy has the bandgap core only.
3. CONCEPT.md (design repository) proposes a different key and bit map than the netlist implements (`dig_in[3]` / `[4]` in the netlist).
4. Open in the design: swap and mon at ss −40 °C (bandgap start-up in the solver); whole-slot PEX; fill (the unfilled slot violates 7 density rules, filled at chip level).

## Not done

- No result CSV of any CACE suite was read for numbers; the numbers in README sections 2.3 and 2.5 are quoted from the READMEs and `tier1/results.txt`.
- The whole-chip DRC of `MPC9639` (`validate/`) was not read for slot 7.
- C2 / C3 / C4 chat logs were not read in full; their dates and agent letters are from the chatlog index and the macro READMEs.
- No simulation was run on 2026-11-22 (explicitly requested: no additional runs).
