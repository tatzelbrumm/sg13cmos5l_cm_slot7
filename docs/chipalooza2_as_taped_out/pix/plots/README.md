<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Plots for HOW_IT_WORKS.md

Made by [`make_plots.py`](make_plots.py) from committed simulation data only (no simulation was run for them).
PNG, 150 dpi, the plot style of [`verification/c2_gaps/dc_curves/plots`](../../../../verification/c2_gaps/dc_curves/plots)
(same rcParams, same color per MOS corner). All data are IHP sg13cmos5l simulations. Used in
[HOW_IT_WORKS.md](../../HOW_IT_WORKS.md).

| plot | what it shows | data |
|---|---|---|
| [bg_core_current_vs_temp.png](bg_core_current_vs_temp.png) | `bg_core_pd` alone: output current into 0.7 V vs temperature, 5 MOS corners (color) × 3 rhigh corners (line style), 3.3 V, schematic; right: the MOS-corner effect alone, relative to tt at the same rhigh corner and temperature | [`verification/c2_gaps/slot_modes_bg/bg_core_dc.csv`](../../../../verification/c2_gaps/slot_modes_bg/bg_core_dc.csv) (view `schematic`, column `i_op_uA`) |
| [pex_vs_schematic_s2d.png](pex_vs_schematic_s2d.png) | S2D pad: magic C-coupled PEX vs schematic per CACE quantity; bar = change of the median over all runs, whisker = range of the per-run change (runs matched by their condition columns) | design repository [`91a7da8b`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/91a7da8b67ac56a26c605501146667a1fde28c32/macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results): `macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/sg13cmos5l_IOPadSingle2Diff/<group>.csv` and `…/sg13cmos5l_IOPadSingle2Diff_pex/<group>.csv`, groups dc, window, range, dc_ibias, ac, tran, noise, enable |
| [pex_vs_schematic_d2s.png](pex_vs_schematic_d2s.png) | D2S pad: the same, PEX of the taped-out cell (ngspice `rshunt` = 1e12) vs the schematic re-run of 2026-11-25 on the taped-out schematic | schematic: [`verification/c2_gaps/d2s_schematic_rerun/csv/<group>.csv`](../../../../verification/c2_gaps/d2s_schematic_rerun/csv/); PEX: [`verification/c2_gaps/d2s_pex/csv/<group>_pex_rshunt1e12.csv`](../../../../verification/c2_gaps/d2s_pex/csv/) (the numbers agree with [`d2s_pex/results.md`](../../../../verification/c2_gaps/d2s_pex/results.md)) |
| [bias_dist_mismatch_hist.png](bias_dist_mismatch_hist.png) | `bias_dist_pd`: local-mismatch Monte Carlo of the copy ratio at 1.0 V output, 100 runs per view (schematic, magic PEX); left: all four outputs pooled, right: `iout1 − iout2` (S2D − D2S) | [`verification/c2_gaps/replica_bias/results/bias_dist/bias_dist_mc_schematic.csv`, `bias_dist_mc_magic_pex_2.csv`](../../../../verification/c2_gaps/replica_bias/results/bias_dist/) |
| [pad_ref_rb_vcm_vref_pvt.png](pad_ref_rb_vcm_vref_pvt.png) | `pad_ref_rb`: `vcm` and `vref` vs temperature, 5 MOS corners (color) × iovdd 3.0 / 3.3 / 3.6 V (line style), 45 points, schematic | [`verification/c2_gaps/replica_bias/results/cace_schematic/vcm_dc_params.csv`, `vcm_dc_3v0_params.csv`](../../../../verification/c2_gaps/replica_bias/results/cace_schematic/) |

Not plotted in the PEX comparisons: quantities whose values lie near zero, where a relative change has no meaning
(offsets, pad-range low end, overshoot, glitches, core-ring and power-down currents). The quantity lists are `S2D_Q` and
`D2S_Q` in `make_plots.py`.

## Regenerating

```sh
python3 -I make_plots.py [--design-cache DIR]
```

Needs Python 3 with numpy and matplotlib, and `git` with network access for the design-repository CSVs: the script
makes a blob-less shallow clone of the design repository in `--design-cache` (default `~/.cache/slot7_make_plots`),
fetches commit `91a7da8b` and reads the CSVs with `git show` (only those blobs are downloaded). It prints the numbers it
plots (medians, per-run ranges, sigmas), so they can be compared with the text. Made on 2026-11-25 with matplotlib 3.11.2.
