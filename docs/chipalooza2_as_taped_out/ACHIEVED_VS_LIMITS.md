<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Achieved vs working limits: S2D pad, D2S pad, `pad_ref_rb`

Back to [README.md](README.md). **The limits below are the designer's working limits, not a specification.** The design is a
proof of concept and had no specification before it was characterized; the CACE files carry the designer's working limits,
"partly derived from earlier measured bands" ([datasheets/README.md](datasheets/README.md)), not pass / fail criteria. A
specification, if one is wanted, would be set ex post facto from the observed intervals. "Inside" therefore means "inside the
designer's working limit in simulation", not "meets a specification" and not a guarantee; nothing here was measured on silicon.

**How to read the tables.** *Working limit*: as the data sheet shows it from the CACE yaml ("no limit" where both sides are
`any`). *Schematic* / *post-layout*: min … max over the runs of the group, copied from the sources named under each table
(post-layout = magic C-coupled extraction). *Margin*: distance from the worse of the two views to the nearest working limit, in
the limit's unit, computed here from the values shown; negative = outside. *Verdict*: inside / outside / no limit. "—" = no
run in that view. Groups that exercise the CACE fixtures' bias selection (`dc_sel*`, `vcm_sel` at the S2D / D2S;
it can pick the Oguey–Aebischer core, which is not in the slot) are left out except where noted; they are in the data sheets.

(*) The CACE yaml labels S2D `Vcm_dev` and D2S `Glitch_max` / `Glitch_min` as mV, but the templates compute them in V, so
CACE compared a value in V with 50 / 400 as if both were in V (effectively 50 V / 400 V)
([AC / transient results](../../verification/c2_gaps/ac_tran/results.md) §4). The data sheets show the values in mV; the margin
and verdict here are those of the physical value against the limit read as mV.

## S2D pad (`sg13cmos5l_IOPadSingle2Diff`, `s7_an[0]`)

Sources: [S2D data sheet](datasheets/sg13cmos5l_IOPadSingle2Diff.md), sections "CACE run summaries" (schematic and
post-layout; committed CACE results of design commit `91a7da8b`, 2026-11-05; the ac / tran / noise / enable groups are
reproduced to 0.000 % in [AC / transient](../../verification/c2_gaps/ac_tran/results.md) §4, window_params within 0.62 mV in
[DC curves](../../verification/c2_gaps/dc_curves/results.md) §1). CACE conditions: `vref` = `vcm` = 1.2 V (window:
`vref` 0.5 V), 50 Ω source, 0.5 pF per output.

| group (runs) | quantity | working limit | schematic | post-layout | margin | verdict |
|---|---|---|---|---|---|---|
| dc_params (135) | gain | 1.99 … 2.01 | 1.99849 … 1.99930 | 1.99849 … 1.99930 | 0.0085 | inside |
| dc_params | input offset (systematic) | −1 … 1 mV | −0.000 … 0.001 mV | −0.000 … 0.001 mV | 0.999 mV | inside |
| dc_params | INL | ≤ 2 mV | 0.087 … 1.069 mV | 0.087 … 1.069 mV | 0.931 mV | inside |
| dc_params | output common-mode error | −30 … 30 mV | 5.003 … 18.050 mV | 5.003 … 18.050 mV | 11.95 mV | inside |
| dc_params | IO ring current | ≤ 135 µA | 114.64 … 116.86 µA | 114.64 … 116.86 µA | 18.14 µA | inside |
| range_params (96) | gain / INL vs `vref`, `vcm` | no limit | 1.94975 … 2.03771 / 0.189 … 172.31 mV | 1.94975 … 2.03771 / 0.189 … 172.31 mV | — | no limit |
| window_params (27) | input range, low end | ≤ 0.1 V | 0.000 … 0.087 V | 0.000 … 0.087 V | 0.013 V | inside |
| window_params | input range, high end | ≥ 1.0 V | 1.057 … 1.299 V | 1.058 … 1.299 V | 0.057 V | inside |
| *not CACE:* high end at the slot's `vref` 0.49 V / `vcm` 1.26 V (45 runs, [DC curves](../../verification/c2_gaps/dc_curves/results.md) §1b) | input range, high end | 1.0 V, the window_params limit applied for comparison | 0.980 … 1.351 V | — | −0.020 V | outside at ss −40 °C 3.0 V only (comparison; with the replica's own `vcm` there, 1.115 V, the round trip keeps −0.243 … 1.055 V, same source) |
| dc_ibias_params (15; 3 … 7 µA) | gain | 1.99 … 2.01 | 1.99871 … 1.99924 | 1.99871 … 1.99924 | 0.0087 | inside |
| dc_ibias_params | output common-mode error | −30 … 30 mV | 8.667 … 11.682 mV | 8.667 … 11.682 mV | 18.32 mV | inside |
| ac_params (15) | closed-loop gain at 1 kHz | no limit | 6.015 … 6.017 dB | 6.015 … 6.017 dB | — | no limit |
| ac_params | −3 dB bandwidth | ≥ 1 MHz | 1.353 … 1.812 MHz | 1.237 … 1.666 MHz | 0.237 MHz | inside |
| ac_params | output CM response to `iovdd`, 1 kHz | ≤ −30 dB | −58.31 … −53.85 dB | −58.31 … −53.85 dB | 23.85 dB | inside |
| ac_mm_params (30 MC, re-run 2026-11-25) | PSRR `iovdd` / `iovss` 1 kHz; CMRR 1 kHz | ≥ 60 / ≥ 60 / ≥ 70 dB | 83.83 … 131.6 / 83.42 … 120.4 / 90.08 … 117.9 dB | — | 20.08 dB (CMRR) | inside |
| tran_params (18) | rise time 10–90 % | no limit | 104.1 … 259.0 ns | 121.2 … 283.0 ns | — | no limit |
| tran_params | settling to 1 % | ≤ 1000 ns | 222.3 … 546.0 ns | 258.6 … 596.1 ns | 403.9 ns | inside |
| tran_params | overshoot | ≤ 5 % | 0.000 … 0.002 % | 0.000 … 0.001 % | 4.998 % | inside |
| tran_params | CM deviation during the step (`Vcm_dev`) (*) | ≤ 50 mV | 7.418 … 15.646 mV | 7.666 … 15.981 mV | 34.0 mV | inside (*) |
| noise_params (15) | input noise 1 kHz / 100 kHz | ≤ 1000 / ≤ 250 nV/√Hz | 596.0 … 726.5 / 142.5 … 157.1 | 595.9 … 726.4 / 142.0 … 156.4 | 273.5 / 92.9 nV/√Hz | inside |
| noise_params | differential output noise 10 Hz … 10 MHz | ≤ 1000 µV | 427.5 … 440.7 µV | 410.5 … 423.1 µV | 559.3 µV | inside |
| pd_params (24) | IO ring current, off | ≤ 1000 nA | 0.059 … 597.1 nA | 0.069 … 597.1 nA | 402.9 nA | inside |
| pd_params | core ring current, off | ≤ 100 nA | −0.000 … 4.831 nA | −0.000 … 4.831 nA | 95.17 nA | inside |
| pd_params | pad input leakage, off | −100 … 100 nA | −7.640 … 5.876 nA | −7.647 … 5.869 nA | 92.35 nA | inside |
| pd_params | differential output / output CM, off | −1 … 1 mV each | −0.001 … 0.000 / −0.000 … 0.000 mV | the same | 0.999 mV | inside |
| enable_params (9) | enable time | ≤ 3 µs | 1.359 … 1.430 µs | 1.463 … 1.524 µs | 1.476 µs | inside |
| enable_params | output CM glitch, high / low | no limit | 0.211 … 0.270 / −0.011 … −0.003 V | 0.220 … 0.287 / −0.004 … −0.003 V | — | no limit |
| mm_params (100 MC, re-run 2026-11-25) | input offset | −20 … 20 mV | −10.22 … 15.97 mV | −13.17 … 19.63 mV | 0.37 mV (PEX) | inside |
| mm_params | gain | 1.93 … 2.07 | 1.9577 … 2.0497 | 1.9590 … 2.0336 | 0.020 | inside |
| mm_params | output common-mode error | −60 … 60 mV | −27.29 … 47.04 mV | −17.87 … 41.95 mV | 12.96 mV | inside |
| mc_params (30 process MC; summary only) | gain; output CM error | 1.99 … 2.01; −30 … 30 mV | 1.99895 … 1.99898; 10.141 … 10.854 mV | — | 0.0090; 19.15 mV | inside |

S2D mismatch with per-run data: re-run of 2026-11-25 on the taped-out netlist, rows mm_params above ([`verification/c2_gaps/s2d_mismatch/`](../../verification/c2_gaps/s2d_mismatch/results.md)).

## D2S pad (`sg13cmos5l_IOPadDiff2Single`, `s7_an[1]`)

Sources: schematic = the CACE re-run of 2026-11-25 on the taped-out schematic, as tabulated in the
[D2S data sheet](datasheets/sg13cmos5l_IOPadDiff2Single.md) ("CACE run summaries"; [re-run results](../../verification/c2_gaps/d2s_schematic_rerun/results.md));
post-layout = [D2S post-layout](../../verification/c2_gaps/d2s_pex/results.md) (tables "Schematic vs PEX", PEX columns, and
"PEX (pass 2) against the yaml limits"; ngspice `rshunt` = 1e12 as a convergence aid), except ac_1nF, which is from
[AC / transient](../../verification/c2_gaps/ac_tran/results.md) §3 (PEX, tt 27 °C only). The committed D2S results of 2026-10-21
predate the final schematic and are not used. CACE conditions: `vicm` = `vref` = `vterm` = 1.65 V, 1 kΩ to `vterm` + 100 pF
(the slot runs the D2S at 1.26 V: [DC curves](../../verification/c2_gaps/dc_curves/results.md) §2b).

| group (runs) | quantity | working limit | schematic | post-layout | margin | verdict |
|---|---|---|---|---|---|---|
| dc_params (30; 3.3 / 3.6 V) | gain | 0.49 … 0.51 | 0.4983 … 0.5000 | 0.4983 … 0.5000 | 0.0083 | inside |
| dc_params | output offset | −5 … 5 mV | 0.032 … 1.737 mV | 0.044 … 1.748 mV | 3.25 mV | inside |
| dc_params | INL (±1 V) | ≤ 10 mV | 0.121 … 7.500 mV | 0.120 … 7.500 mV | 2.50 mV | inside |
| dc_params | IO ring current | ≤ 400 µA | 301.7 … 325.3 µA | 301.8 … 325.3 µA | 74.7 µA | inside |
| dc_params | core ring current | ≤ 100 nA | 0.008 … 23.89 nA | 0.014 … 23.90 nA | 76.1 nA | inside |
| dc_params | quiescent current OP / ON | 150 … 300 µA | 216.6 … 238.6 / 216.2 … 238.5 µA | the same | 61.4 µA | inside |
| dc_params | minimum output-device current | ≥ 30 µA | 104.7 … 120.3 µA | 104.7 … 120.3 µA | 74.7 µA | inside |
| dc_3v0_params (15; 3.0 V) | gain | 0.49 … 0.51 | 0.4982 … 0.5002 | — | 0.0082 | inside |
| dc_3v0_params | output offset | −5 … 5 mV | 0.032 … 1.769 mV | — | 3.23 mV | inside |
| dc_3v0_params | INL (±1 V) | no limit | 11.10 … 88.42 mV | — | — | no limit (at `vicm` 1.26 V: ≤ 1.38 mV, DC curves §2b) |
| dc_ibias_params (3; 3.75 / 5 / 6.25 µA) | gain | 0.49 … 0.51 | 0.4999 … 0.5000 | — | 0.0099 | inside |
| dc_ibias_params | quiescent current OP | 120 … 350 µA | 171.1 … 273.8 µA | — | 51.1 µA | inside |
| ac_params (15) | closed-loop gain | −6.2 … −5.85 dB | −6.050 … −6.021 dB | −6.050 … −6.021 dB | 0.150 dB | inside |
| ac_params | bandwidth | ≥ 1 MHz | 1.762 … 2.245 MHz | 1.569 … 2.016 MHz | 0.569 MHz | inside |
| ac_params | gain peaking | ≤ 1 dB | ≤ 0.000002 dB | ≤ 0.000002 dB | 1.00 dB | inside |
| ac_params | PSRR `iovdd` 1 kHz / 100 kHz | ≥ 60 / ≥ 25 dB | 70.64 … 72.51 / 30.71 … 32.53 dB | 70.04 … 71.91 / 30.10 … 31.93 dB | 10.04 / 5.10 dB | inside |
| ac_params | CMRR 1 kHz | ≥ 70 dB | 95.19 … 128.4 dB | 95.13 … 110.3 dB | 25.13 dB | inside |
| ac_params | output impedance 1 kHz / 1 MHz | ≤ 10 / ≤ 300 Ω | 0.189 … 3.302 / 154.7 … 200.8 Ω | 0.208 … 3.304 / 166.0 … 216.9 Ω | 6.70 / 83.1 Ω | inside |
| ac_load_params (6; 10 / 100 / 300 pF, 1 kΩ / 1 GΩ) | bandwidth | ≥ 1 MHz | 1.574 … 2.985 MHz | 1.425 … 2.713 MHz | 0.425 MHz | inside |
| ac_load_params | gain peaking | ≤ 4 dB | 0.000 … 2.749 dB | 0.000 … 2.466 dB | 1.251 dB | inside |
| ac_1nF_params (2; 1 nF, 1 kΩ / 1 GΩ) | bandwidth; gain peaking | no limit | 1.350 … 1.396 MHz; 4.771 … 7.427 dB | 1.270 … 1.318 MHz; 4.43 … 7.11 dB | — | no limit |
| tran_params (9; 10 / 100 / 300 pF) | slew rate rising / falling | ≥ 1 V/µs | 1.749 … 3.058 / 1.764 … 3.135 V/µs | 1.591 … 2.732 / 1.603 … 2.794 V/µs | 0.591 V/µs | inside |
| tran_params | overshoot | ≤ 15 % | 0.000 … 9.115 % | 0.000 … 7.986 % | 5.89 % | inside |
| tran_params | settling rising / falling | ≤ 1 µs | 0.303 … 0.676 / 0.311 … 0.497 µs | 0.355 … 0.548 / 0.362 … 0.534 µs | 0.324 µs | inside |
| thd_params (3; 0.5 / 1 / 1.5 V) | THD | ≤ −35 dB | −73.33 … −38.66 dB | −73.15 … −38.66 dB | 3.66 dB | inside |
| noise_params (3) | output noise 1 kHz / 100 kHz | ≤ 1000 / ≤ 200 nV/√Hz | 605.1 … 715.4 / 142.6 … 156.5 | 605.0 … 715.3 / 142.1 … 155.7 | 284.6 / 43.5 nV/√Hz | inside |
| noise_params | integrated output noise | ≤ 300 µV | 223.3 … 235.6 µV | 214.0 … 224.2 µV | 64.4 µV | inside |
| drive_params (10) | max / min output | ≥ 3.0 V / ≤ 0.9 V | 3.266 … 3.283 / 0.635 … 0.736 V | 3.266 … 3.283 / 0.635 … 0.736 V | 0.266 / 0.164 V | inside |
| drive_params | short-circuit source / sink current | ≥ 20 mA | 49.71 … 93.31 / 54.77 … 124.2 mA | the same | 29.71 mA | inside |
| pd_params (48) | IO ring current, off | ≤ 1000 nA | 0.048 … 642.2 nA | 0.064 … 642.2 nA | 357.8 nA | inside |
| pd_params | core ring current, off | ≤ 100 nA | −0.000 … 23.89 nA | −0.000 … 23.89 nA | 76.1 nA | inside |
| pd_params | pad leakage, off | −100 … 100 nA | −36.83 … 14.94 nA | −36.85 … 14.95 nA | 63.15 nA | inside |
| pd_params | `vdd1v2_sense` / `vdd3v3_sense` current | ≤ 2000 nA | 0 … 905.5 / 0 … 1114 nA | the same | 886 nA | inside |
| enable_params (3; sel 0 / 1 / 2) | turn-on time | ≤ 5 µs | 0.982 … 1.819 µs | 1.109 … 2.387 µs | 2.61 µs | inside |
| enable_params | enable glitch, positive (*) | ≤ 400 mV | 121.6 … 225.5 mV | 127.8 … 228.1 mV | 171.9 mV | inside (*) |
| enable_params | enable glitch, negative (*) | ≥ −400 mV | −176.6 … −104.3 mV | −224.8 … −128.3 mV | 175.2 mV | inside (*) |
| enable_params | IO ring current after start-up | 200 … 400 µA | 308.4 … 315.8 µA | 308.4 … 315.8 µA | 84.2 µA | inside |
| mm_params (30 MC, tt 27 °C) | output offset | −20 … 20 mV | −14.28 … 13.92 mV (σ 6.28 mV) | — | 5.72 mV | inside |
| mm_params | gain | 0.49 … 0.51 | **0.48877** … 0.50508 | — | **−0.00123** | **outside** (1 of 30 samples, 3.1 σ below the mean 0.50011, σ 0.0037; [re-run](../../verification/c2_gaps/d2s_schematic_rerun/results.md) §1) |
| mm_params | quiescent current OP | 100 … 400 µA | 197.4 … 243.7 µA | — | 97.4 µA | inside |

Not run post-layout ([D2S post-layout](../../verification/c2_gaps/d2s_pex/results.md), README "Not done"): dc_3v0, dc_sel,
dc_sel3, dc_ibias, ac_1nF as a CACE group, mismatch. Over all groups of the schematic re-run 78 of 79 summary rows are inside,
the one outside is the mismatch gain above ([data sheet](datasheets/sg13cmos5l_IOPadDiff2Single.md)). For comparison with
dc_ibias: the slot's bandgap gives 3.829 … 6.369 µA ([bandgap](../../verification/c2_gaps/slot_modes_bg/results.md) §3) and
`bias_dist_pd` copies it with +0.49 … +1.56 % ([replica bias](../../verification/c2_gaps/replica_bias/results.md) §3), so the
top of the slot's `iref` lies slightly above the 6.25 µA of that grid.

## `pad_ref_rb` (replica bias: `vcm`, `vref`)

Sources: [replica data sheet](datasheets/pad_ref_rb.md) (working limits; schematic CACE committed at design commit `9052bd35`,
2026-11-07) and [replica bias results](../../verification/c2_gaps/replica_bias/results.md) §1 (PEX = schematic to 0.1 mV; the
4-digit values below are from its tables) and §2 (mismatch, 100 runs with per-run data).

| group (runs) | quantity | working limit | schematic | post-layout | margin | verdict |
|---|---|---|---|---|---|---|
| vcm_dc_params (30; 3.3 / 3.6 V, 5 corners, −40 / 27 / 125 °C) | `vcm` | 1.031 … 1.53 V | 1.242 … 1.395 V | 1.242 … 1.395 V | 0.135 V | inside |
| vcm_dc_3v0_params (15; 3.0 V) | `vcm` | 1.031 … 1.262 V | 1.120 … 1.193 V | 1.120 … 1.193 V | 0.069 V | inside |
| vcm_sel_params (18; fixture's OA / bandgap selection, 3.0 V) | `vcm` | 1.031 … 1.244 V | 1.117 … 1.204 V | — | 0.040 V | inside |
| vref_room_params (15; 27 °C) | `vref` | 0.47 … 0.51 V | 0.4832 … 0.5038 V | 0.4832 … 0.5038 V | 6.2 mV | inside |
| vref_hot_params (15; 125 °C) | `vref` | 0.55 … 0.7 V | 0.5724 … 0.5964 V | 0.5724 … 0.5964 V | 22.4 mV | inside |
| vref_cold_params (15; −40 °C) | `vref` | 0.35 … 0.5 V | 0.4363 … 0.4553 V | 0.4363 … 0.4553 V | 44.7 mV | inside |
| the DC groups above except vcm_sel | supply current (without the 5 µA reference) | ≤ 25 µA | 18.93 … 19.26 µA | 18.93 … 19.26 µA | 5.74 µA | inside |
| vcm_sel_params | supply current | ≤ 35 µA | 11.504 … 27.966 µA | — | 7.03 µA | inside |
| pd_params (4; disabled, 3.6 V) | `vcm` / `vref` disabled | ≤ 1 mV each | ≤ 0.31 µV / ≤ 16.5 µV | ≤ 0.31 µV / ≤ 16.5 µV | 0.98 mV | inside |
| pd_params | supply current, disabled | ≤ 0.1 µA | ≤ 9.9 nA | ≤ 9.9 nA | 90.1 nA | inside |
| mm_params (100 MC, tt 27 °C 3.3 V) | `vcm` | 1.2 … 1.32 V | 1246.91 … 1273.95 mV (σ 5.415 mV) | — (not run; mismatch on an extracted netlist is vacuous per the yaml header, [data sheet](datasheets/pad_ref_rb.md)) | 46.05 mV | inside |
| mm_params | `vref` | 0.47 … 0.52 V | 481.36 … 501.81 mV (σ 3.788 mV) | — | 11.4 mV | inside |
| mm_params | supply current | ≤ 25 µA | 18.76 … 19.42 µA | — | 5.58 µA | inside |

No working limit exists for the enable time (`vcm` 0.79 … 1.81 µs, `vref` 1.03 … 2.02 µs, [README §2.3](README.md#23-the-blocks))
or for dynamic behaviour on the PEX view, which was not simulated ([replica bias results](../../verification/c2_gaps/replica_bias/results.md), "Not resolved here").
