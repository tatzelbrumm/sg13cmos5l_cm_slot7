<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: candidate data for characterizing the building blocks that were taped out

Step 2 of the slot 7 documentation ([README.md](README.md)). **This is an inventory of candidates, not a result.** For each block of the
taped-out `slot_7` it lists where in the design repository
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single) simulation, CACE and check data can be found,
at the two commits the slot 7 delivery cites: **V3** = `claude/c4-replica-bias` @ `9052bd35` (slot_7 v3, replica bias, slot circuit) and
**T** = `toplevel` @ `91a7da8b` (the pad cells, as the delivery's provenance table gives). Not done here, and needed before any of it is quoted as a
specification of the taped-out blocks:

1. Confirm for each suite that the netlist it simulated is the netlist of the block as it is in `slot_7.gds` of `158afc5` (the macros kept changing
   after some of the CACE runs; several READMEs say so themselves).
2. Re-run, or at least read the result CSVs, instead of trusting a README's summary.

Files were listed with `git ls-tree` on the clone; their contents were read only where stated.

## 1. By block

| block of `slot_7` | source macro (design repo) | candidate data | state |
|---|---|---|---|
| `bg_core_pd` (bandgap, ~5 µA) | `macros/bg_core_pd` | [`macros/bg_core_pd/README.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bg_core_pd/README.md); Magic DRC and LVS reports in `verification/` (also copied into the slot 7 delivery with sha256). **Electrical characterization:** the same Banba cell is the reference of `macros/bias_bg_pd`; its CACE suite [`macros/bias_bg_pd/verification/cace/bias_bg_pd.yaml`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bias_bg_pd/verification/cace/bias_bg_pd.yaml) has groups `dc`, `dc_rp`, `mm`, `pd`, `psrr`, `startup` with results in `verification/cace/results/bias_bg_pd/` ([`macros/bias_bg_pd/verification/cace/results/bias_bg_pd`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bias_bg_pd/verification/cace/results/bias_bg_pd)); and the shared-selector suite `macros/bias_sel_pd` (groups `iref`, `mm`, `pd`, `psrr`, `pvt`, `rpnp`, `sel`, `startup`) | candidate: `bias_bg_pd` is the bandgap-referenced bias of the class-AB driver, a different cell than `bg_core_pd`; whether its bandgap is the same circuit as `bg_core_pd` must be checked in the netlists |
| `bias_dist_pd` (distribution mirror) | `macros/bias_dist_pd` | [`macros/bias_dist_pd/README.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bias_dist_pd/README.md); [`macros/bias_dist_pd/testbenches/spice/tb_truth.spice`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bias_dist_pd/testbenches/spice/tb_truth.spice) with output [`macros/bias_dist_pd/testbenches/spice/tb_truth.out`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/bias_dist_pd/testbenches/spice/tb_truth.out) (enable truth table). The tier-1 slot run uses it extracted | no CACE suite found; truth-table test only |
| `pad_ref_rb` (replica bias: `vcm`, `vref`) | `macros/pad_ref_rb` (+ `macros/vcm_rb`, `macros/vref_s2d_rb`) | CACE suite [`macros/pad_ref_rb/verification/cace/pad_ref_rb.yaml`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/pad_ref_rb/verification/cace/pad_ref_rb.yaml); results `verification/cace/results/pad_ref_rb/` ([`macros/pad_ref_rb/verification/cace/results/pad_ref_rb`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/pad_ref_rb/verification/cace/results/pad_ref_rb)): `vcm_dc`, `vcm_dc_3v0`, `vcm_sel`, `vref_cold` / `vref_room` / `vref_hot`, `mm`, `pd` with `summary_*_params.md` per group; baselines `macros/vcm_rb/verification/baseline` and `macros/vref_s2d_rb/verification/baseline`; `macros/vcm_rb/testbenches/{rb_char,pad_char,spice}` | most complete suite among the slot blocks |
| `s7_ctrl` (enable, mode decode, switch matrix; [glue logic](glue_logic.md)) | `macros/slot_7` (the sheet and layout live there); its cells `efs_ls_core`, `bdp_nand2_hv`, `bdp_inv_hv`, `bdp_tg_hv` come from `macros/en_ctrl_3v3` (fail-safe level shifter `ls_up_fs`, `efs_ls_core`) and `macros/hv_logic` / `macros/bias_dist_pd` | [`macros/en_ctrl_3v3/verification/cace/en_ctrl_3v3.yaml`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/en_ctrl_3v3/verification/cace/en_ctrl_3v3.yaml) with results `verification/cace/results/en_ctrl_3v3/` (`float`, `pvt`, `tran_en`, `tran_pg` groups) and [`macros/en_ctrl_3v3/testbenches/spice/results`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/en_ctrl_3v3/testbenches/spice/results) (`starve.txt`, `states.txt`); [`macros/hv_logic/README.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/hv_logic/README.md); slot level: [`macros/slot_7/layout/klayout/slot_7_checks.txt`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/macros/slot_7/layout/klayout/slot_7_checks.txt) (DRC / LVS / netgen summary), `docs/slot7_hookup/tier1/` | `en_ctrl_3v3` v2 is the delivered enable; the slot's `s7_ctrl` is a larger cell that reuses its level shifter — confirm which `en_ctrl_3v3` revision the cell instances |
| `s7_doutpd` (12 NMOS pull-downs) | `macros/slot_7` | no suite found; the devices are `nmosHV` 0.5 µm / 0.45 µm; leakage / pull-down function is covered by the slot-level tier-1 and the harness checks | gap |
| pad `sg13cmos5l_IOPadSingle2Diff` (S2D) | `macros/sg13cmos5l_IOPadSingle2Diff` (T) | CACE results [`macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/sg13cmos5l_IOPadSingle2Diff`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/91a7da8b67ac56a26c605501146667a1fde28c32/macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/sg13cmos5l_IOPadSingle2Diff): `ac`, `ac_mm`, `dc`, `dc_ibias`, `dc_sel`, `dc_sel3`, `enable`, `mc`, `mm`, `noise`, `pd`, `range`, `tran`, `window`; plus `results/s2d_mpdda_pd_sel/` (loop); Magic DRC report, KLayout and Magic LVS in `verification/` | 63 files under `verification/cace` |
| pad `sg13cmos5l_IOPadDiff2Single` (D2S) | `macros/sg13cmos5l_IOPadDiff2Single` (T) | CACE suite [`macros/sg13cmos5l_IOPadDiff2Single/verification/cace/sg13cmos5l_IOPadDiff2Single.yaml`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/91a7da8b67ac56a26c605501146667a1fde28c32/macros/sg13cmos5l_IOPadDiff2Single/verification/cace/sg13cmos5l_IOPadDiff2Single.yaml) and [`macros/sg13cmos5l_IOPadDiff2Single/verification/cace/d2s_mpdda_pd_sel.yaml`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/91a7da8b67ac56a26c605501146667a1fde28c32/macros/sg13cmos5l_IOPadDiff2Single/verification/cace/d2s_mpdda_pd_sel.yaml); results [`macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/91a7da8b67ac56a26c605501146667a1fde28c32/macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single): `ac`, `ac_1nF`, `ac_load`, `dc`, `dc_3v0`, `dc_ibias`, `dc_sel`, `dc_sel3`, `drive`, `enable`, `mm`, `noise`, `pd`, `thd`, `tran`; loop results `d2s_mpdda_pd_sel/`; DRC / LVS in `verification/` | 50 files under `verification/cace` |
| whole slot | `macros/slot_7`, `docs/slot7_hookup/` | [`docs/slot7_hookup/tier1/results.txt`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/docs/slot7_hookup/tier1/results.txt) (5 corners: `vcm`, `vref`, round-trip error, currents), `tier1/modes.txt`, `kick_short.spice`, `kick_switch.spice`, scripts `run_tier1.py`, `run_modes.py`; [`docs/slot7_hookup/CONCEPT.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/docs/slot7_hookup/CONCEPT.md) | the numbers quoted in the README's section 2.5 |

The Oguey–Aebischer core (`macros/oa_core_pd`, `macros/OgueyAebischerBias`, `macros/bias_oa_pd`) has CACE data too, but **its block is not in the taped-out slot** (see the README, section 4).

## 2. Script base and result formats (the "internal" characterization tooling)

All in the design repository, branch `claude/c4-replica-bias` / `toplevel`:

| item | what it does / format |
|---|---|
| `verification/cace/<cell>.yaml` | CACE datasheet: parameters with conditions, limits, and testbench templates (`templates/`); `make sim-cace` leaves `verification/cace/results/<cell>/<group>_params.csv` and `summary_<group>_params.md` |
| [`scripts/cace/cace_to_csv.py`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/scripts/cace/cace_to_csv.py) | collects the per-run results of one parameter group into a CSV |
| [`scripts/cace/spec_table.py`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/scripts/cace/spec_table.py) | specification table (limit, worst case, verdict per quantity) as markdown from the yaml and the CSVs |
| [`scripts/cace/mc_stats.py`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/scripts/cace/mc_stats.py) | statistics of Monte Carlo groups against the limits of another group |
| [`scripts/cace/compare_views.py`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/scripts/cace/compare_views.py) | compares CACE results between netlist views (schematic against extracted `_cores_<view>`) |
| [`scripts/cace/pex_for_sim.py`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/scripts/cace/pex_for_sim.py) | prepares an extracted (PEX) netlist for simulation (mismatch devices, capacitor-only nodes) |
| `<macro>/testbenches/spice/run_*.py` | stand-alone ngspice drivers with `results/*.txt` (for example `en_ctrl_3v3`: `run_states.py`, `run_starve.py`) |
| `docs/slot7_hookup/tier1/run_tier1.py`, `run_modes.py` | the slot-level run: extracted pads, `pad_ref_rb`, `bias_dist_pd`, `bg_core_pd`, `ls_up_fs`; five corners; all eight modes |
| `docs/slot7_testplatform/`, `macros/slot7_testplatform/testbenches/ngspice` | the earlier test platform (stage A / B): PVT runs of the bias cores and the bias tree; not the taped-out circuit |
| `sudelbuecher/chatlog/`, per-session `ref/` (branch `sudel_buecher`) | the chat logs and run logs where the numbers were produced; the delivery's README points there |

## 3. Gap against the example documentation

[`documentation_examples.md`](https://github.com/tatzelbrumm/sg13cmos5l_ocd_chipalooza/blob/da4557a5b2ac84c6e05c5a683a019df4895b67e9/sudelbuecher/slots/documentation_examples.md) lists the examples to follow (biasgen `doc/` bandgap, slot 15 tinyBGR README, slot 2 `sbcs` README, slot 5 class-AB README).
Their common structure: description, **key specifications** (table with limits), architecture, pins, default conditions, schematic, layout, simulation results (pre-layout, post-layout /
PEX, Monte Carlo mismatch). What [README.md](README.md) has and lacks against it:

| example section | in the slot 7 README | missing |
|---|---|---|
| description, architecture | sections 2.1, 2.3 | per-block schematic pictures (the design repository has `schematic/*.svg` for `slot_7`, `s7_ctrl`, `s7_doutpd`) |
| key specifications | quoted figures in 2.3 and 2.5 | a spec table per block with min / typ / max over PVT: needs the result CSVs of section 1 |
| pins | section 4.2 (pad pins), glue_logic.md (`s7_ctrl` ports) | pin tables of `bg_core_pd`, `bias_dist_pd`, `pad_ref_rb` (ports are in the macro READMEs) |
| default conditions | 2.4 (default mode) | the PVT grid of the characterization (tier-1: tt / ss / ff / fs / sf × −40 / 27 / 125 °C × 3.0 / 3.3 / 3.6 V) stated per block |
| layout | 4.3 (hierarchy, sizes, positions) | per-block layout pictures |
| simulation results | 2.5, glue_logic.md §7 | post-layout (PEX) and Monte Carlo results per block: they exist for the pads (S2D: 414 / 414 runs, schematic and extracted) and `bg_core_pd` (C1), not for `bias_dist_pd`, `s7_ctrl` |

## 4. Suggested next step

Pick the blocks in this order of value for a datasheet of slot 7: (1) the modes and the default operating point (tier-1 results, needs the
extracted `158afc5` netlist re-run), (2) `pad_ref_rb` (`vcm`, `vref` over PVT), (3) `bg_core_pd` (start-up, which is also where the open ss / −40 °C swap and
mon stall sits), (4) the two pads (CACE already broad), (5) `s7_ctrl` / `bias_dist_pd` (functional truth tables). Say which, and I will read the
result CSVs for that block and write the numbers into this folder with their source commit.
