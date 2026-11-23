<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Sign-off reports of slot 7 and its blocks

Designer: Christoph Maier. This directory collects the DRC and LVS reports that are **committed in the design repository**
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single) for the
taped-out slot 7 (this repository at `158afc5`), its blocks and the two custom pads. The files are byte copies, collected on
2026-11-23; each keeps its path below the macro directory, so `signoff/<macro>/<path>` comes from `macros/<macro>/<path>` of the
commit named in the table. Nothing was re-run to produce them.

Commits: **V** = branch `claude/c4-replica-bias` @ `9052bd35928c6d40344e8e686c9abbe736bfadb9` (slot_7 v3 and its blocks),
**T** = branch `toplevel` @ `91a7da8b67ac56a26c605501146667a1fde28c32` (the pad cells; the pad GDS files in `../pads/` are byte
copies from T, see `../README.md`; the S2D GDS at T has sha256 `f4b0e073…`, equal to `../pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.gds`).

Summaries were read from the files on 2026-11-23: magic / netgen text as written; KLayout `.lyrdb` by counting the `<item>`
entries (violations); KLayout `.lvsdb` with `klayout.db.LayoutVsSchematic` (KLayout 0.30.12), cross-reference status of the circuit
and of each device pair.

## Files

| file here | commit | source path | bytes | sha256 | result (one line) |
|---|---|---|---:|---|---|
| `slot_7/layout/klayout/slot_7_checks.txt` | V | `macros/slot_7/layout/klayout/slot_7_checks.txt` | 736 | `8411bd3c39e9df1316e241ce6a65d055471dc7b1f924a8b936f1d509153ef42a` | slot_7 v3 (GDS sha256 prefix `7394d0923c511631`, i.e. **without** the tughra art): `run_drc.py` no violations, 0 "exception" lines, maximal + latch-up 0; LVS deep: match, 0 port mismatches, 497 devices; flat: 32 port mismatches, match with `--ignore_top_ports_mismatch`; `deep_negative`: no match (an intended negative test: RUNLOG row 130 "negative no match"); netgen: 5 subcircuits match uniquely, top port error `vss_1v2_uq0` only |
| `slot_7/verification/drc/s7_ctrl.klayout.drc/s7_ctrl.klay_s7_ctrl_main.lyrdb` | V | `macros/slot_7/verification/drc/s7_ctrl.klayout.drc/s7_ctrl.klay_s7_ctrl_main.lyrdb` | 66773 | `e41cef55a6a02fc2c0ab060e758e4cf80ffc4f05f33e42939979a24ada98f0e5` | KLayout DRC, PDK deck `ihp-sg13cmos5l.drc`, top cell `s7_ctrl`: 332 rule categories, 0 violations |
| `en_ctrl_3v3/verification/drc/en_ctrl_3v3.klayout.drc/en_ctrl_3v3.klay_en_ctrl_3v3_main.lyrdb` | V | `macros/en_ctrl_3v3/verification/drc/en_ctrl_3v3.klayout.drc/en_ctrl_3v3.klay_en_ctrl_3v3_main.lyrdb` | 66781 | `128d29e40eca6658880ced94305a7dcf00c5fc25737517e060fc73477c849d3d` | KLayout DRC, top cell `en_ctrl_3v3`: 0 violations (the slot instantiates only its level-shifter core, not this cell) |
| `en_ctrl_3v3/verification/drc/ls_up_fs.klayout.drc/ls_up_fs.klay_ls_up_fs_main.lyrdb` | V | `macros/en_ctrl_3v3/verification/drc/ls_up_fs.klayout.drc/ls_up_fs.klay_ls_up_fs_main.lyrdb` | 66775 | `4949e97f2fec7618929df6e6d1b4129f28b9881f3106112553ec1f16c02151b1` | KLayout DRC, top cell `ls_up_fs` (the shifter used 7× in `s7_ctrl` as `efs_ls_core`): 0 violations |
| `bg_core_pd/verification/drc/bg_core_pd.magic.drc/bg_core_pd.magic.drc.rpt` | V | `macros/bg_core_pd/verification/drc/bg_core_pd.magic.drc/bg_core_pd.magic.drc.rpt` | 104 | `1603b8cbf81c51020bf43734988113e68a6ad9034db4e092fd1b54acac2ad9d9` | magic DRC: `COUNT: 0`. Identical to `../macros/bg_core_pd/verification/drc/...` (same sha256) |
| `bg_core_pd/verification/lvs/bg_core_pd.magic.lvs/bg_core_pd.lvs.out` | V | `macros/bg_core_pd/verification/lvs/bg_core_pd.magic.lvs/bg_core_pd.lvs.out` | 10062 | `1a94d96d1f008811b75310728e656059a00bb70f9b58b9dfb26b58674c38bb7d` | netgen: 29 devices / 21 nets on both sides, "Final result: Circuits match uniquely." and "Property errors were found." (every listed property error is the property `mm_ok`, present in the schematic netlist only). Identical to `../macros/bg_core_pd/verification/lvs/...` |
| `sg13cmos5l_IOPadSingle2Diff/verification/drc/sg13cmos5l_IOPadSingle2Diff.magic.drc/sg13cmos5l_IOPadSingle2Diff.magic.drc.rpt` | T | `macros/sg13cmos5l_IOPadSingle2Diff/verification/drc/sg13cmos5l_IOPadSingle2Diff.magic.drc/sg13cmos5l_IOPadSingle2Diff.magic.drc.rpt` | 121 | `9457a642de7c1eab61e36b3332c3d32f60fca7ad6cadded3e12d2364a7ad1a56` | magic DRC: `COUNT: 0` |
| `sg13cmos5l_IOPadSingle2Diff/verification/drc/sg13cmos5l_IOPadSingle2Diff.klayout.drc/sg13cmos5l_IOPadSingle2Diff.klay_sg13cmos5l_IOPadSingle2Diff_main.lyrdb` | T | same path under `macros/sg13cmos5l_IOPadSingle2Diff/` | 66813 | `8ac24220695e2f2dda1819fac0712f924c7942a3afab6eea69f70aff2ae89eae` | KLayout DRC, top cell `sg13cmos5l_IOPadSingle2Diff`: 0 violations |
| `sg13cmos5l_IOPadSingle2Diff/verification/lvs/sg13cmos5l_IOPadSingle2Diff.magic.lvs/sg13cmos5l_IOPadSingle2Diff.lvs.out` | T | same path under `macros/sg13cmos5l_IOPadSingle2Diff/` | 24383 | `9dba30fd5393051185f2c35039f5152262486e9200d208e14f7429b469db473e` | netgen: 76 devices / 37 nets on both sides, "Netlists match with 7 symmetries with property errors" (`mm_ok`; W / L exchanged on the antenna diodes DN1 / DP1); "Final result: Top level cell failed pin matching" on `vss` (the known substrate merge of `vss` and `iovss`, accepted by the designer on 2026-11-03, `../README.md`) |
| `sg13cmos5l_IOPadSingle2Diff/verification/lvs/sg13cmos5l_IOPadSingle2Diff.klayout.lvs/sg13cmos5l_IOPadSingle2Diff.lvsdb` | T | same path under `macros/sg13cmos5l_IOPadSingle2Diff/` | 849629 | `c7f359c893e17f38c764ca213774a038d2d9d87e88f894fa7a2e017313b8612e` | KLayout LVS: circuit `sg13cmos5l_IOPadSingle2Diff` status Match; 76 device pairs, all Match |
| `sg13cmos5l_IOPadDiff2Single/verification/drc/sg13cmos5l_IOPadDiff2Single.magic.drc/sg13cmos5l_IOPadDiff2Single.magic.drc.rpt` | T | `macros/sg13cmos5l_IOPadDiff2Single/verification/drc/sg13cmos5l_IOPadDiff2Single.magic.drc/sg13cmos5l_IOPadDiff2Single.magic.drc.rpt` | 121 | `363dec4a0fe3dcc8a7fe2ce2daa622164b8e5dbeeb612620cf6c921d26f32dda` | magic DRC: `COUNT: 0` |
| `sg13cmos5l_IOPadDiff2Single/verification/drc/sg13cmos5l_IOPadDiff2Single.klayout.drc/sg13cmos5l_IOPadDiff2Single.klay_sg13cmos5l_IOPadDiff2Single_main.lyrdb` | T | same path under `macros/sg13cmos5l_IOPadDiff2Single/` | 66813 | `275929e0e67c25745cc5b3149ed05fa11210b6163d7c425255dce0f837d8109c` | KLayout DRC, top cell `sg13cmos5l_IOPadDiff2Single`: 0 violations |
| `sg13cmos5l_IOPadDiff2Single/verification/lvs/sg13cmos5l_IOPadDiff2Single.magic.lvs/sg13cmos5l_IOPadDiff2Single.lvs.out` | T | same path under `macros/sg13cmos5l_IOPadDiff2Single/` | 23574 | `18751b8576f8babbb6933517a3920b3af1401287f0e0af263aa3710b61ba21dc` | netgen: 76 devices / 36 nets on both sides, "Netlists match with 7 symmetries with property errors" (`mm_ok`; W / L exchanged on antenna diodes); "Final result: Top level cell failed pin matching" on `vss` (same known merge) |
| `sg13cmos5l_IOPadDiff2Single/verification/lvs/sg13cmos5l_IOPadDiff2Single.klayout.lvs/sg13cmos5l_IOPadDiff2Single.lvsdb` | T | same path under `macros/sg13cmos5l_IOPadDiff2Single/` | 1215986 | `ae628fa81bd8b2627e5cf75b979d8e90a673070d8ceb0ef8bce141bbf8a1d780` | KLayout LVS: circuit `sg13cmos5l_IOPadDiff2Single` status Match; 77 device pairs, all Match |

No file was over 2 MB, so nothing was skipped for size. The copied reports carry no SPDX header, so that they stay byte-identical
to their sources (sha256 above); they are tool output and have no licence header of their own (repository licence: `../LICENSE`).

## Not collected, and why

| item | why |
|---|---|
| `macros/<pad>/verification/lvs/<pad>.magic.lvs/<pad>.ext.spc` (T; 26584 and 33097 bytes) | the extracted netlist used by the magic LVS, not a report |
| `pad_ref_rb`, `bias_dist_pd`, `hv_logic` | no DRC or LVS report is committed at V (`verification/lvs/` holds only a `.gitignore`). Their READMEs state the results: `pad_ref_rb` "KLayout DRC (`--no_density`) clean, maximal deck with latch-up 0 (F), `make klayout-lvs` OK"; `bias_dist_pd` "KLayout DRC (`--no_density`) clean, maximal deck with latch-up 0, flat LVS against D's CDL (a negative test fails), `make klayout-lvs` OK"; `hv_logic` "No layout yet" (its gates were laid out as `bdp_*` cells inside `bias_dist_pd`) |
| LVS reports of `s7_ctrl`, `en_ctrl_3v3`, `ls_up_fs` | not committed at V (only the DRC `.lyrdb` files) |
| reports for the **taped-out** `final/gds/slot_7.gds` (v3 + tughra art, sha256 `469f2327…`) | none committed anywhere read here; `slot_7_checks.txt` above is for v3 without the art. The checks of the final GDS (DRC clean, maximal + latch-up 0, density: the same 7 minimum-density rules as without the art, LVS deep match 497 devices, `netgen_check.sh` as v3) are stated in `../README.md` (2026-11-08) as text only |
| `oa_core_pd` reports (in `../macros/oa_core_pd/verification/`) | `oa_core_pd` is not in the taped-out slot (`../docs/chipalooza2_as_taped_out/README.md`) |

To complete the sign-off set of the taped-out slot, the KLayout DRC report (`.lyrdb`) and LVS database (`.lvsdb`) of
`final/gds/slot_7.gds` against `netlist/slot_7.cdl`, and the `netgen_check.sh` output, would have to be generated and added; this was not done here.
