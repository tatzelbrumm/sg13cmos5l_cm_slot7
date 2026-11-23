<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: characterization data sheets (first step)

**No specification existed:** the design is a proof of concept, so the CACE files carry the designer's *working limits* (partly derived from earlier measured bands), not pass / fail criteria. Each data sheet therefore leads with an **ex post facto specification**: for every characterized quantity the minimum and maximum over the characterization grid, the value at typical conditions, the median, the number of runs and the corner where each extreme occurs. These intervals describe what was simulated; they are not guaranteed limits. If a range should be *defined* (rather than observed), it should be chosen from these tables.

Data sheets of the circuits in the **taped-out** `slot_7` ([../README.md](../README.md)), built from characterization data that already exist in the design repository. **No simulation was run for any of them**;
they are generated or copied from committed files, and each states which taped-out cell it covers and where the data differ from the taped-out circuit. Below the specification, every CACE sheet reproduces, per parameter group, the rows of CACE's own `summary_<group>.md` (working limits, measured min / typ / max, CACE's status against those limits) with the group's run count and swept conditions.
Generator: [tools/make_datasheet.py](tools/make_datasheet.py) (reads `<cell>.yaml` and the `results/` directory; the extracted CACE trees were read from the design repository at the commits below).

| data sheet | covers (taped-out cell) | data | views | CACE summary rows inside the working limits | commit |
|---|---|---|---|---|---|
| [pad_ref_rb.md](pad_ref_rb.md) | `pad_ref_rb`: replica bias `vcm` / `vref` | CACE, 8 groups | schematic | 24 of 24 | design repo `9052bd35` |
| [sg13cmos5l_IOPadSingle2Diff.md](sg13cmos5l_IOPadSingle2Diff.md) | S2D pad, `s7_an[0]` | CACE, 12 groups + mismatch / MC | schematic and post-layout (magic PEX) | 57 of 57 and 46 of 46 | design repo `91a7da8b` |
| [sg13cmos5l_IOPadDiff2Single.md](sg13cmos5l_IOPadDiff2Single.md) | D2S pad, `s7_an[1]` | CACE, 14 groups | schematic only (results predate the layout) | 79 of 79 | design repo `91a7da8b` |
| [en_ctrl_3v3_level_shifter.md](en_ctrl_3v3_level_shifter.md) | `ls_up_fs` shifter of the glue (via the whole `en_ctrl_3v3` v2 cell, which `slot_7` does not instantiate) | CACE, 7 groups | schematic | 33 of 33 | design repo `9052bd35` |
| [slot_7_system.md](slot_7_system.md) | the slot as a whole, five corners and the modes | tier-1 simulation (not CACE) | extracted blocks | n/a | design repo `9052bd35` |
| [../test_platforms.md](../test_platforms.md) | test platforms (stage A / B), **not taped out** | ngspice testbench summaries | schematic and extracted | n/a | design repo `efb80141` |

The counts are rows of CACE group summaries (one row per quantity and group), not simulation runs and not specification checks; run counts are in each sheet. Typical conditions are the CACE files' defaults (tt, 27 °C, 3.3 V; typical resistor and PNP corners); a group that sweeps only other supplies has no typical row (shown as —).

## Taped-out circuits without a data sheet, and why

| circuit | what exists | gap |
|---|---|---|
| `bg_core_pd` | no CACE suite of its own; characterized only inside `bias_bg_pd` / `bias_sel_pd` (the bias of the class-AB driver, which are not in the slot), and as the BG branch of the test platform (`../test_platforms.md`: output current over corners and temperature, enable time, fail-safe) | no data sheet from a suite on the taped-out cell |
| `bias_dist_pd` | a truth-table simulation (`tb_truth`) only | no CACE suite |
| `s7_ctrl` (glue logic) | slot-level mode runs (`slot_7_system.md`); its shifter via `en_ctrl_3v3_level_shifter.md` | no suite on the cell itself |
| `s7_doutpd` | none | none |

## Data that are explicitly not used here

`bias_sel_pd`, `bias_bg_pd`, `bias_in_pd`, `bias_out_pd`, `bias_oa_pd`, `OgueyAebischerBias`, `vcm_rb` / `vref_s2d_rb` baselines of the old per-block trees and the test-platform results other than as the separate test-platform document: they characterize
circuits (or earlier versions) that are not in the taped-out slot.
