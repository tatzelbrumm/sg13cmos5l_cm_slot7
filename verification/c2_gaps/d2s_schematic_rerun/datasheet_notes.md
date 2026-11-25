<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
- **Re-run, not the committed results.** Every table of this sheet comes from the CACE re-run of 2026-11-25 on the taped-out schematic (CACE 2.11, ngspice-47 with the IHP OSDI models, IHP-Open-PDK `df4c5054`); the working limits and verdicts are those of the unchanged CACE file at `91a7da8b`. Differences to the earlier, committed results: [old vs new](../../../verification/c2_gaps/d2s_schematic_rerun/results.md).
- **Solver aid:** drive_params ran with ngspice `.option rshunt=1e12` (1 TΩ from every node to ground): without it 3 of its 10 runs (tt, sf, ff at −40 °C) gave no result (DC sweep not converging, or no progress after 15 min); on the 7 runs that converge both ways it changes the results by ≤ 0.0002 %. All other groups ran exactly as the templates are (pd_params with the template's own rshunt=1e14).
- **mm_params** now has its per-iteration data (the committed CSV had a header only, because CACE 2.11 nests the iterations one level deeper than the design repository's `cace_to_csv.py` expects), so its specification rows are min / median / max over the iterations of the CSV, not CACE's summary.
- **Units:** the CSV column labels are those of the design repository's `cace_to_csv.py` and are not reliable (several hold SI values under a display-unit label, e.g. `Vos_out[mV]` and `t_on[us]` hold V and s); the generator rescales each column to the unit of CACE's own summary.
