<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# D2S schematic re-run: results, old (committed) vs new

**IHP sg13cmos5l schematic simulation**, `sg13cmos5l_IOPadDiff2Single`, all 15 CACE groups of the design repository's
yaml at 91a7da8b (templates unchanged), CACE 2.11, ngspice-47 + OSDI, 2026-11-25. Old = the committed results
(`macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single/`, last written
2026-10-21, before the final schematic); new = this run on the taped-out schematic ([README](README.md): which netlist
and why). Method, commands and versions: README.md. Status: complete.

## 1. Runs

| group | runs (new) | runs with a result | solver aid | runs (old CSV) | wall clock |
|---|---:|---:|---|---:|---|
| dc_params | 30 | 30 | none | 30 | 32 s |
| dc_3v0_params | 15 | 15 | none | 15 | 16 s |
| dc_sel_params | 9 | 9 | none | 9 | 12 s |
| dc_sel3_params | 3 | 3 | none | 3 | 5 s |
| dc_ibias_params | 3 | 3 | none | 3 | 6 s |
| ac_params | 15 | 15 | none | 15 | 36 s |
| ac_load_params | 6 | 6 | none | 6 | 16 s |
| ac_1nF_params | 2 | 2 | none | 2 | 8 s |
| tran_params | 9 | 9 | none | 9 | 45 s |
| thd_params | 3 | 3 | none | 3 | 15 s |
| noise_params | 3 | 3 | none | 3 | 14 s |
| drive_params | 10 | 10 | **rshunt=1e12** (see below) | 10 | 21 s (with rshunt) |
| pd_params | 48 | 48 | none added (the template's own rshunt=1e14) | 48 | 45 s |
| enable_params | 3 | 3 | none | 3 | 37 s |
| mm_params | 30 | 30 | none | 0 (header only) | 30 s |

All 189 runs have results. CACE's verdicts against the yaml's working limits (proposals): 78 of 79 summary rows
inside, **1 outside: mm_params Gain − mismatch, min 0.48877 < 0.49** (iteration 28 of 30; the 30 iterations have
mean 0.50011, σ 0.0037, so that sample is 3.1 σ below the mean). The committed results had 79 of 79 inside.

**drive_params without aid** (first pass, kept as `csv/drive_params_norshunt.csv`): 7 of 10 runs. tt −40 °C: ngspice
made no progress (killed by hand after 15.6 min; the other runs take seconds); sf −40 °C and ff −40 °C: the first DC
sweep (`dc Vd -3 3 6`) did not converge ("Dynamic gmin stepping failed", singular nodes in the disabled bandgap /
enable logic next to the cell, e.g. `n.xc.xib.xp…`, `x1.xd.xc2.n3`), so Vout_max / Vout_min were missing. With
`.option rshunt=1e12` all 10 runs finished in 21 s; on the 7 runs that converge both ways the results differ by
≤ 0.0002 % (Vout_min, Isc_src, Isc_snk; Vout_max identical). The same aid was measured on the D2S schematic AC /
transient / noise scalars in ../ac_tran (≤ 0.006 %). No other group needed it. In several runs of dc / ac / tran /
enable / noise / mm ngspice reports "Dynamic gmin stepping failed" and then finds the operating point by true gmin
stepping (singular node in the disabled bandgap `xg.xbg.n0[1]`); those runs have complete results, as did the
committed runs.

Consistency: ac_params, ac_load_params, tran_params, noise_params and enable_params give exactly (all printed
digits) the `.data` values of the D2S schematic runs in ../ac_tran (same templates, same commit), e.g. tt 27 °C:
f3dB 2.00071 MHz, Zout 1 kHz 0.209436 Ω, t_on (sel 0) 0.982036 µs; so the 24 "stale ref" values of
`../ac_tran/tables/crosscheck.md` are confirmed by the full suite.

## 2. What changed vs the committed results (summary of section 4)

Changes > 2 % (`flag` in section 4; Δ in % of the old value; "per run" = the largest change between runs with equal
conditions):

- **Bias currents up, in every DC group**: quiescent output-device currents IqP / IqN +3.4 … +5.4 % per run (dc_params median
  215.4 → 225.5 µA), IO ring supply current Iio +1.8 … +3.6 % (median 301.7 → 311.3 µA), class-AB floor Imin
  +6.4 … +9.5 % (dc_params min 95.8 → 104.7 µA); the same shift in enable_params Iio_end (+2.2 … +3.3 %), mm_params
  IqP (median 214.5 → 220.5 µA) and drive_params Isc_snk (+3.2 … +3.3 %; Isc_src and the output swing within 0.65 %).
- **Systematic output offset** −8.0 … −14.5 % per run (µV level; dc_params max 1.947 → 1.737 mV at ff 125 °C 3.6 V).
- **INL**: dc_params median 0.480 → 0.450 mV, per run −9.1 … +2.6 %; the maximum 7.404 → 7.50 mV (ss −40 °C 3.3 V);
  dc_3v0 / dc_sel3 within 2 %.
- **Output impedance**: Zout 1 kHz −3.1 … −17 % (tt 27 °C 0.2176 → 0.2094 Ω; max 3.85 → 3.30 Ω at ff 125 °C);
  Zout 1 MHz −2.4 … −2.7 %.
- **Peaking with real peaking**: 300 pF ∥ 1 GΩ 2.899 → 2.749 dB, 300 pF ∥ 1 kΩ 0.776 → 0.715 dB, 100 pF ∥ 1 GΩ
  0.053 → 0.016 dB, 1 nF ∥ 1 GΩ 7.593 → 7.427 dB (1 kΩ 4.852 → 4.771 dB). The large % changes of the other peaking
  values (ac_params, 10 pF) are between numerically zero values (≤ 2e-6 dB, i.e. no peaking), not real changes.
- **Transient**: settling time falling at ss 300 pF 0.6165 → 0.4721 µs (−23 %; the ringing tail crosses the 1 %
  band at a different time), min settling +2.3 %; overshoot max 9.32 → 9.12 % (ss 300 pF); slew rates within 1.6 %.
  The overshoot "inf / +14 %" entries are between values ≤ 1e-4 % (no overshoot).
- **Enable**: turn-on time t_on 0.854 → 0.982 µs (sel 0, +14.9 %), 1.228 → 1.819 µs (sel 1, +48 %), 0.805 →
  1.228 µs (sel 2, +53 %); glitch amplitudes changed by +0.5 … +8.7 % (positive) and −3.2 … −5.8 % in size (negative; max 224.4 → 225.5 mV and −187.4 → −176.6 mV).
- **Power-down leakage** (nA level, absolute changes small): pad leakage at vpad = 3.3 V, en low, 0.95 → 1.90 nA (tt
  27 °C) and 9.71 → 14.94 nA (ff 125 °C, the maximum), at vpad = 0 / 1.65 V a few nA or less; IO ring current, off, at
  tt 27 °C (pdstate 0 / 3) +3.8 … +15.5 % on 0.04 … 0.17 nA. All other pd quantities unchanged (≤ 0.02 %).
- **Mismatch (mm_params)**: Vos −11.39 … 10.10 mV → −14.28 … 13.92 mV (now with per-run data: mean 0.31 mV, σ 6.28 mV
  over 30 iterations), gain 0.4939 … 0.5085 → 0.4888 … 0.5051 (one iteration below the 0.49 working limit, above).
  The 30 Monte Carlo samples are not the same draws as in the committed run (same seeds, but a different netlist), so
  min / max of 30 samples compare only statistically; the IqP shift (median +2.8 %) is the systematic one above.

Within 2 % (no flag): gain (DC and AC), bandwidth f3dB (except ac_load 10 pF ∥ 1 GΩ −2.1 %), PSRR, CMRR, slew rate,
THD and output amplitude, noise (1 kHz, 100 kHz, integrated), output swing, core-ring currents, the dc_3v0 / dc_sel3
INL.

## 3. Magic PEX (../d2s_pex) vs this schematic re-run

../d2s_pex compared its PEX results with the committed (stale) schematic results. Against the current schematic
(`tables/compare_pex.md`; there "old" = this schematic re-run, "new" = PEX, rshunt 1e12, groups dc / ac / ac_load /
tran / noise / drive / enable / pd / thd):

- the DC current shifts ../d2s_pex attributed to the layout vanish: IqP / IqN / Iio / Imin / Isc_snk / Isc_src
  ≤ 0.02 % (reported there: IqP / IqN about +5 %, Iio +3.6 %, Isc_snk +3.3 %), INL ≤ 0.75 % (reported −9.1 …
  +1.5 % per run), gain, THD, output swing, IO current after start-up ≤ 0.03 %; those were the stale reference, not
  the layout;
- the layout effects that remain: bandwidth −10 … −12 % (ac_params, median 2.001 → 1.774 MHz; ac_load −8.6 … −11 %), slew rates −9 … −12 %, CMRR
  1 kHz median 125.0 → 109.0 dB, Zout +7 … +10 % (except the ff 125 °C maximum of Zout 1 kHz, 3.30 Ω in both), settling +10 % (median), t_on +10 % median (sel 1 +31 %, 1.819 →
  2.387 µs; reported there up to +94 %), enable glitch negative −17 … −27 %, integrated noise −4.2 … −4.8 %, PSRR
  −0.8 … −2.2 %; the systematic offset +19 % median on µV values, core-ring current (pA) and the near-zero peaking /
  overshoot values as in section 2.

## 4. Per quantity, old (committed) vs new (generated by compare.py, = tables/compare_committed.md)

Values in the yaml's display unit (scaled as datasheets/tools/make_datasheet.py does). mm_params old: CACE's committed
summary (min / typ / max; no per-run data), so no per-run change.

| group | quantity | unit | old min | new min | Δ min | old median | new median | Δ median | old max | new max | Δ max | max per-run Δ (at) | max per-run \|Δ\| | runs old / new | flag |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| dc_params | Gain |  | 0.4981 | 0.4983 | +0.05 % | 0.5 | 0.5 | +0.00 % | 0.5 | 0.5 | +0.00 % | +0.05 % (corner_mos=ff, temp=125, vdd=3.3) | 0.000271 | 30 / 30 |  |
| dc_params | Output offset | mV | 0.03487 | 0.03202 | -8.16 % | 0.07344 | 0.06727 | -8.40 % | 1.947 | 1.737 | -10.78 % | -13.02 % (corner_mos=sf, temp=125, vdd=3.3) | 0.2106 | 30 / 30 | Δ > 2 % |
| dc_params | Integral nonlinearity | mV | 0.1222 | 0.1208 | -1.10 % | 0.4804 | 0.4504 | -6.24 % | 7.404 | 7.5 | +1.29 % | -8.64 % (corner_mos=sf, temp=125, vdd=3.6) | 0.09532 | 30 / 30 | Δ > 2 % |
| dc_params | IO ring supply current | uA | 293.2 | 301.7 | +2.91 % | 301.7 | 311.3 | +3.18 % | 314 | 325.3 | +3.58 % | +3.58 % (corner_mos=ff, temp=-40, vdd=3.6) | 11.24 | 30 / 30 | Δ > 2 % |
| dc_params | Core ring supply current | nA | 0.008253 | 0.008253 | +0.00 % | 0.1185 | 0.1185 | +0.00 % | 23.89 | 23.89 | +0.00 % | -0.00 % (corner_mos=ss, temp=-40, vdd=3.3) | 1e-08 | 30 / 30 |  |
| dc_params | Quiescent current OP | uA | 207.4 | 216.6 | +4.44 % | 215.4 | 225.5 | +4.72 % | 226.6 | 238.6 | +5.32 % | +5.35 % (corner_mos=ff, temp=-40, vdd=3.3) | 12.04 | 30 / 30 | Δ > 2 % |
| dc_params | Quiescent current ON | uA | 207 | 216.2 | +4.47 % | 214.6 | 225 | +4.84 % | 226.5 | 238.5 | +5.32 % | +5.35 % (corner_mos=ff, temp=-40, vdd=3.3) | 12.05 | 30 / 30 | Δ > 2 % |
| dc_params | Minimum output-device current | uA | 95.77 | 104.7 | +9.32 % | 105.1 | 113.3 | +7.83 % | 112 | 120.3 | +7.45 % | +9.32 % (corner_mos=ss, temp=-40, vdd=3.3) | 9.335 | 30 / 30 | Δ > 2 % |
| dc_3v0_params | Gain |  | 0.498 | 0.4982 | +0.06 % | 0.4999 | 0.5 | +0.00 % | 0.5002 | 0.5002 | +0.00 % | +0.06 % (corner_mos=ff, temp=125, vdd=3.0) | 0.000285 | 15 / 15 |  |
| dc_3v0_params | Output offset | mV | 0.03434 | 0.03151 | -8.25 % | 0.05332 | 0.04833 | -9.37 % | 1.985 | 1.769 | -10.85 % | -13.04 % (corner_mos=sf, temp=125, vdd=3.0) | 0.2154 | 15 / 15 | Δ > 2 % |
| dc_3v0_params | Integral nonlinearity | mV | 10.92 | 11.1 | +1.64 % | 44.4 | 44.95 | +1.25 % | 87.36 | 88.42 | +1.21 % | +1.85 % (corner_mos=sf, temp=125, vdd=3.0) | 1.057 | 15 / 15 |  |
| dc_3v0_params | IO ring supply current | uA | 286.9 | 295.8 | +3.09 % | 291.7 | 301.1 | +3.25 % | 298.2 | 308.8 | +3.56 % | +3.56 % (corner_mos=ff, temp=-40, vdd=3.0) | 10.6 | 15 / 15 | Δ > 2 % |
| dc_3v0_params | Core ring supply current | nA | 0.008253 | 0.008253 | +0.00 % | 0.1185 | 0.1185 | +0.00 % | 23.89 | 23.89 | +0.00 % | +0.00 % (corner_mos=ss, temp=-40, vdd=3.0) | 1e-08 | 15 / 15 |  |
| dc_3v0_params | Quiescent current OP | uA | 201.4 | 211 | +4.78 % | 206 | 216.1 | +4.91 % | 211.9 | 223.3 | +5.38 % | +5.38 % (corner_mos=ff, temp=-40, vdd=3.0) | 11.4 | 15 / 15 | Δ > 2 % |
| dc_3v0_params | Quiescent current ON | uA | 201.4 | 210.6 | +4.61 % | 205.8 | 216 | +4.96 % | 211.8 | 223.2 | +5.38 % | +5.38 % (corner_mos=ff, temp=-40, vdd=3.0) | 11.4 | 15 / 15 | Δ > 2 % |
| dc_3v0_params | Minimum output-device current | uA | 57.4 | 62.83 | +9.46 % | 76.82 | 82.96 | +7.99 % | 93.29 | 100.7 | +7.90 % | +9.46 % (corner_mos=ss, temp=-40, vdd=3.0) | 7.369 | 15 / 15 | Δ > 2 % |
| dc_sel_params | Gain |  | 0.498 | 0.4983 | +0.05 % | 0.4999 | 0.4999 | +0.00 % | 0.5 | 0.5 | +0.00 % | +0.05 % (sel=1, temp=125, corner_r=typ, corner_pnp=typ) | 0.000249 | 9 / 9 |  |
| dc_sel_params | Output offset | mV | 0.02655 | 0.02405 | -9.41 % | 0.05668 | 0.05125 | -9.59 % | 2.706 | 2.439 | -9.87 % | -14.48 % (sel=2, temp=125, corner_r=typ, corner_pnp=typ) | 0.2671 | 9 / 9 | Δ > 2 % |
| dc_sel_params | Integral nonlinearity | mV | 0.1965 | 0.1978 | +0.64 % | 1.355 | 1.343 | -0.93 % | 4.094 | 4.098 | +0.09 % | -9.07 % (sel=2, temp=125, corner_r=typ, corner_pnp=typ) | 0.1118 | 9 / 9 | Δ > 2 % |
| dc_sel_params | IO ring supply current | uA | 207.9 | 214.5 | +3.18 % | 302.9 | 311.4 | +2.82 % | 400.9 | 412.3 | +2.84 % | +3.50 % (sel=0, temp=-40, corner_r=typ, corner_pnp=typ) | 11.4 | 9 / 9 | Δ > 2 % |
| dc_sel_params | Core ring supply current | nA | 0.01551 | 0.01551 | +0.00 % | 0.1381 | 0.1381 | -0.00 % | 7.038 | 7.038 | +0.00 % | -0.00 % (sel=2, temp=27, corner_r=typ, corner_pnp=typ) | 1e-06 | 9 / 9 |  |
| dc_sel_params | Quiescent current OP | uA | 145.2 | 152.5 | +5.02 % | 212 | 220.8 | +4.13 % | 276.3 | 288.7 | +4.46 % | +5.29 % (sel=0, temp=-40, corner_r=typ, corner_pnp=typ) | 12.33 | 9 / 9 | Δ > 2 % |
| dc_sel_params | Quiescent current ON | uA | 145.2 | 152.5 | +5.02 % | 212 | 220.7 | +4.13 % | 273.6 | 286.2 | +4.60 % | +5.29 % (sel=0, temp=-40, corner_r=typ, corner_pnp=typ) | 12.59 | 9 / 9 | Δ > 2 % |
| dc_sel_params | Minimum output-device current | uA | 67 | 71.31 | +6.43 % | 102 | 110.1 | +7.98 % | 139.1 | 149.9 | +7.81 % | +8.74 % (sel=0, temp=27, corner_r=typ, corner_pnp=typ) | 10.86 | 9 / 9 | Δ > 2 % |
| dc_sel3_params | Gain |  | 0.4926 | 0.4935 | +0.20 % | 0.4998 | 0.4998 | +0.01 % | 0.5 | 0.5 | +0.00 % | +0.20 % (sel=3, temp=125) | 0.000979 | 3 / 3 |  |
| dc_sel3_params | Output offset | mV | 0.07093 | 0.06448 | -9.09 % | 0.5345 | 0.46 | -13.93 % | 13.55 | 11.99 | -11.49 % | -13.93 % (sel=3, temp=27) | 1.557 | 3 / 3 | Δ > 2 % |
| dc_sel3_params | Integral nonlinearity | mV | 34.65 | 33.98 | -1.93 % | 47.56 | 47.83 | +0.57 % | 52.27 | 51.74 | -1.01 % | -1.93 % (sel=3, temp=-40) | 0.6704 | 3 / 3 |  |
| dc_sel3_params | IO ring supply current | uA | 491.9 | 505 | +2.67 % | 591.3 | 606.8 | +2.62 % | 687.3 | 703.5 | +2.37 % | +2.67 % (sel=3, temp=-40) | 16.26 | 3 / 3 | Δ > 2 % |
| dc_sel3_params | Core ring supply current | nA | 0.003347 | 0.003347 | +0.00 % | 0.1578 | 0.1578 | +0.00 % | 9.245 | 9.245 | +0.00 % | +0.00 % (sel=3, temp=-40) | 0 | 3 / 3 |  |
| dc_sel3_params | Quiescent current OP | uA | 335.6 | 351.1 | +4.61 % | 401.9 | 420 | +4.49 % | 469.8 | 488.6 | +4.00 % | +4.61 % (sel=3, temp=-40) | 18.78 | 3 / 3 | Δ > 2 % |
| dc_sel3_params | Quiescent current ON | uA | 335.5 | 351 | +4.62 % | 401.4 | 419.5 | +4.51 % | 456.3 | 476.6 | +4.46 % | +4.62 % (sel=3, temp=-40) | 20.33 | 3 / 3 | Δ > 2 % |
| dc_sel3_params | Minimum output-device current | uA | 172 | 185.4 | +7.77 % | 212.2 | 227.6 | +7.24 % | 253.8 | 270.8 | +6.67 % | +7.77 % (sel=3, temp=-40) | 16.94 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | Gain |  | 0.4999 | 0.4999 | +0.00 % | 0.4999 | 0.4999 | +0.00 % | 0.5 | 0.5 | +0.00 % | +0.00 % (ibias=6.25e-06) | 6e-06 | 3 / 3 |  |
| dc_ibias_params | Output offset | mV | 0.03924 | 0.03564 | -9.17 % | 0.05669 | 0.05152 | -9.12 % | 0.08597 | 0.07783 | -9.47 % | -9.47 % (ibias=6.25e-06) | 0.008142 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | Integral nonlinearity | mV | 0.1953 | 0.2003 | +2.55 % | 1.356 | 1.376 | +1.46 % | 6.19 | 6.266 | +1.22 % | +2.55 % (ibias=3.75e-06) | 0.07549 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | IO ring supply current | uA | 228.2 | 235.6 | +3.25 % | 298.7 | 308.4 | +3.26 % | 368.2 | 380.2 | +3.27 % | +3.27 % (ibias=6.25e-06) | 12.05 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | Core ring supply current | nA | 0.1185 | 0.1185 | +0.00 % | 0.1185 | 0.1185 | +0.00 % | 0.1185 | 0.1185 | +0.00 % | +0.00 % (ibias=3.75e-06) | 0 | 3 / 3 |  |
| dc_ibias_params | Quiescent current OP | uA | 163.1 | 171.1 | +4.89 % | 212.4 | 222.9 | +4.94 % | 260.8 | 273.8 | +4.97 % | +4.97 % (ibias=6.25e-06) | 12.97 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | Quiescent current ON | uA | 163 | 171 | +4.90 % | 212.3 | 222.8 | +4.94 % | 260.7 | 273.7 | +4.98 % | +4.98 % (ibias=6.25e-06) | 12.98 | 3 / 3 | Δ > 2 % |
| dc_ibias_params | Minimum output-device current | uA | 76.7 | 83.45 | +8.80 % | 102.1 | 111 | +8.74 % | 129.1 | 140.1 | +8.55 % | +8.80 % (ibias=3.75e-06) | 11.04 | 3 / 3 | Δ > 2 % |
| ac_params | Closed-loop gain | dB | -6.055 | -6.05 | +0.08 % | -6.022 | -6.021 | +0.00 % | -6.021 | -6.021 | +0.00 % | +0.08 % (corner_mos=ff, temp=125) | 0.00485 | 15 / 15 |  |
| ac_params | Bandwidth | MHz | 1.778 | 1.762 | -0.88 % | 2.015 | 2.001 | -0.71 % | 2.252 | 2.245 | -0.30 % | -0.88 % (corner_mos=ff, temp=-40) | 0.01652 | 15 / 15 |  |
| ac_params | Gain peaking | dB | 3.027e-07 | 5.347e-08 | -82.34 % | 9.28e-07 | 8.238e-07 | -11.22 % | 1.532e-06 | 1.607e-06 | +4.91 % | -82.34 % (corner_mos=fs, temp=125) | 8.049e-07 | 15 / 15 | Δ > 2 % |
| ac_params | PSRR iovdd 1 kHz | dB | 70.66 | 70.64 | -0.03 % | 71.56 | 71.54 | -0.03 % | 72.53 | 72.51 | -0.03 % | +0.08 % (corner_mos=ff, temp=125) | 0.0554 | 15 / 15 |  |
| ac_params | PSRR iovdd 100 kHz | dB | 30.74 | 30.71 | -0.10 % | 31.62 | 31.6 | -0.09 % | 32.55 | 32.53 | -0.08 % | -0.10 % (corner_mos=ff, temp=-40) | 0.03 | 15 / 15 |  |
| ac_params | CMRR 1 kHz | dB | 93.79 | 95.19 | +1.50 % | 124 | 125 | +0.81 % | 127.5 | 128.4 | +0.72 % | +1.59 % (corner_mos=sf, temp=125) | 1.569 | 15 / 15 |  |
| ac_params | Output impedance 1 kHz | Ω | 0.1951 | 0.1891 | -3.07 % | 0.2176 | 0.2094 | -3.74 % | 3.85 | 3.302 | -14.22 % | -17.28 % (corner_mos=sf, temp=125) | 0.5475 | 15 / 15 | Δ > 2 % |
| ac_params | Output impedance 1 MHz | Ω | 159 | 154.7 | -2.68 % | 171.7 | 167.4 | -2.50 % | 206.1 | 200.8 | -2.56 % | -2.68 % (corner_mos=ff, temp=-40) | 5.284 | 15 / 15 | Δ > 2 % |
| ac_load_params | Bandwidth | MHz | 1.582 | 1.574 | -0.50 % | 2.162 | 2.144 | -0.82 % | 3.006 | 2.984 | -0.71 % | -2.14 % (cload=1e-11, rload=1000000000.0) | 0.04899 | 6 / 6 | Δ > 2 % |
| ac_load_params | Gain peaking | dB | 3.682e-07 | 1.257e-06 | +241.28 % | 0.0265 | 0.008028 | -69.71 % | 2.899 | 2.749 | -5.15 % | +252.84 % (cload=1e-11, rload=1000000000.0) | 0.1492 | 6 / 6 | Δ > 2 % |
| ac_1nF_params | Bandwidth, 1 nF | MHz | 1.336 | 1.35 | +1.07 % | 1.358 | 1.373 | +1.10 % | 1.381 | 1.396 | +1.12 % | +1.12 % (cload=1e-09, rload=1000000000.0) | 0.01542 | 2 / 2 |  |
| ac_1nF_params | Gain peaking, 1 nF | dB | 4.852 | 4.771 | -1.67 % | 6.222 | 6.099 | -1.98 % | 7.593 | 7.427 | -2.18 % | -2.18 % (cload=1e-09, rload=1000000000.0) | 0.1656 | 2 / 2 | Δ > 2 % |
| tran_params | Slew rate, rising | V/us | 1.76 | 1.749 | -0.65 % | 2.448 | 2.429 | -0.75 % | 3.054 | 3.058 | +0.11 % | -0.93 % (corner_mos=ff, cload=1e-10) | 0.02112 | 9 / 9 |  |
| tran_params | Slew rate, falling | V/us | 1.781 | 1.764 | -0.96 % | 2.466 | 2.429 | -1.50 % | 3.166 | 3.135 | -0.97 % | -1.61 % (corner_mos=ff, cload=1e-10) | 0.03697 | 9 / 9 |  |
| tran_params | Overshoot | % | -7e-05 | -6e-05 | +14.29 % | 0.0001 | 0.0001 | +0.00 % | 9.321 | 9.115 | -2.20 % | inf (corner_mos=ff, cload=1e-11) | 0.2957 | 9 / 9 | Δ > 2 % |
| tran_params | Settling time, rising | us | 0.2959 | 0.3027 | +2.29 % | 0.4562 | 0.4581 | +0.41 % | 0.6892 | 0.6761 | -1.90 % | +2.32 % (corner_mos=tt, cload=1e-10) | 0.01311 | 9 / 9 | Δ > 2 % |
| tran_params | Settling time, falling | us | 0.3036 | 0.3107 | +2.35 % | 0.4532 | 0.4564 | +0.69 % | 0.6165 | 0.4965 | -19.46 % | -23.42 % (corner_mos=ss, cload=3e-10) | 0.1444 | 9 / 9 | Δ > 2 % |
| thd_params | THD | dB | -73.2 | -73.33 | -0.17 % | -57.79 | -57.68 | +0.19 % | -38.87 | -38.66 | +0.53 % | +0.53 % (vdamp=1.5) | 0.205 | 3 / 3 |  |
| thd_params | Output amplitude | V | 0.25 | 0.25 | +0.00 % | 0.4999 | 0.5 | +0.00 % | 0.7503 | 0.7504 | +0.01 % | +0.01 % (vdamp=1.5) | 4e-05 | 3 / 3 |  |
| noise_params | Output noise 1 kHz | nV/rtHz | 607.6 | 605.1 | -0.40 % | 681.7 | 678.8 | -0.43 % | 718.5 | 715.4 | -0.43 % | -0.43 % (temp=-40) | 3.092 | 3 / 3 |  |
| noise_params | Output noise 100 kHz | nV/rtHz | 142.6 | 142.6 | +0.03 % | 152.5 | 152.6 | +0.02 % | 156.4 | 156.5 | +0.03 % | +0.03 % (temp=125) | 0.047 | 3 / 3 |  |
| noise_params | Integrated output noise | uV | 222.7 | 223.3 | +0.24 % | 234.2 | 234.6 | +0.18 % | 235.1 | 235.6 | +0.20 % | +0.24 % (temp=125) | 0.543 | 3 / 3 |  |
| drive_params | Max output | V | 3.266 | 3.266 | +0.00 % | 3.275 | 3.275 | +0.00 % | 3.283 | 3.283 | +0.00 % | +0.00 % (corner_mos=ff, temp=125) | 5e-05 | 10 / 10 |  |
| drive_params | Min output | V | 0.6396 | 0.6354 | -0.65 % | 0.6865 | 0.6823 | -0.62 % | 0.7386 | 0.7359 | -0.36 % | -0.65 % (corner_mos=ff, temp=-40) | 0.004274 | 10 / 10 |  |
| drive_params | Short-circuit source current | mA | 49.65 | 49.71 | +0.12 % | 66.98 | 67.05 | +0.11 % | 93.21 | 93.31 | +0.10 % | +0.13 % (corner_mos=ff, temp=125) | 0.0925 | 10 / 10 |  |
| drive_params | Short-circuit sink current | mA | 53.03 | 54.77 | +3.28 % | 80.36 | 82.97 | +3.24 % | 120.3 | 124.2 | +3.22 % | +3.28 % (corner_mos=ss, temp=125) | 3.879 | 10 / 10 | Δ > 2 % |
| pd_params | IO ring current, off | nA | 0.04144 | 0.04787 | +15.51 % | 257.6 | 257.5 | -0.04 % | 642.2 | 642.2 | +0.00 % | +15.51 % (pdstate=0, vpad=3.3, corner_mos=tt, temp=27) | 0.183 | 48 / 48 | Δ > 2 % |
| pd_params | Core ring current, off | nA | -0 | -0 | +0.00 % | 0.6509 | 0.6509 | +0.00 % | 23.89 | 23.89 | +0.00 % | +0.00 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 1e-07 | 48 / 48 |  |
| pd_params | Pad leakage, off | nA | -36.83 | -36.83 | -0.00 % | 0.0472 | 0.1758 | +272.41 % | 9.71 | 14.94 | +53.88 % | +124.69 % (pdstate=0, vpad=1.65, corner_mos=ff, temp=27) | 5.231 | 48 / 48 | Δ > 2 % |
| pd_params | vdd1v2_sense current | nA | -0 | -0 | +0.00 % | 1.271e-05 | 1.271e-05 | +0.00 % | 905.5 | 905.5 | +0.00 % | +0.00 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 0 | 48 / 48 |  |
| pd_params | vdd3v3_sense current | nA | -0 | -0 | +0.00 % | 0.0001149 | 0.0001149 | +0.01 % | 1114 | 1114 | +0.00 % | -0.02 % (pdstate=0, vpad=0, corner_mos=ff, temp=27) | 1.4e-08 | 48 / 48 |  |
| pd_params | Internal enable | V | 2.688e-10 | 2.688e-10 | +0.00 % | 1.392e-07 | 1.392e-07 | +0.00 % | 7.104e-07 | 7.104e-07 | +0.00 % | +0.00 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 0 | 48 / 48 |  |
| enable_params | Turn-on time | us | 0.8054 | 0.982 | +21.94 % | 0.8544 | 1.228 | +43.77 % | 1.228 | 1.819 | +48.12 % | +52.52 % (sel=2, tstop=6e-05) | 0.591 | 3 / 3 | Δ > 2 % |
| enable_params | Enable glitch, positive | mV | 111.9 | 121.6 | +8.68 % | 117.1 | 124.4 | +6.18 % | 224.4 | 225.5 | +0.53 % | +8.68 % (sel=0, tstop=6e-05) | 9.711 | 3 / 3 | Δ > 2 % |
| enable_params | Enable glitch, negative | mV | -187.4 | -176.6 | +5.75 % | -119.6 | -112.8 | +5.73 % | -107.8 | -104.3 | +3.22 % | +5.75 % (sel=1, tstop=6e-05) | 10.77 | 3 / 3 | Δ > 2 % |
| enable_params | IO ring current after start-up | uA | 298.7 | 308.4 | +3.26 % | 306.3 | 315.6 | +3.04 % | 309.1 | 315.8 | +2.17 % | +3.26 % (sel=0, tstop=6e-05) | 9.749 | 3 / 3 | Δ > 2 % |
| mm_params | Output offset - mismatch | mV | -11.39 | -14.28 | -25.39 % | 0.709 | 1.323 | +86.54 % | 10.1 | 13.92 | +37.77 % | — (old: summary only) | — | 0 / 30 | Δ > 2 % |
| mm_params | Gain - mismatch |  | 0.4939 | 0.4888 | -1.05 % | 0.4994 | 0.5003 | +0.18 % | 0.5085 | 0.5051 | -0.67 % | — (old: summary only) | — | 0 / 30 |  |
| mm_params | Quiescent current OP - mismatch | uA | 192.9 | 197.4 | +2.29 % | 214.5 | 220.5 | +2.77 % | 232.8 | 243.7 | +4.67 % | — (old: summary only) | — | 0 / 30 | Δ > 2 % |

## 5. Per quantity, this schematic re-run ("old") vs magic PEX of ../d2s_pex ("new") (= tables/compare_pex.md)

| group | quantity | unit | old min | new min | Δ min | old median | new median | Δ median | old max | new max | Δ max | max per-run Δ (at) | max per-run \|Δ\| | runs old / new | flag |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---|
| ac_load_params | Bandwidth | MHz | 1.574 | 1.425 | -9.49 % | 2.144 | 1.961 | -8.57 % | 2.984 | 2.713 | -9.08 % | -10.95 % (cload=1e-10, rload=1000) | 0.2711 | 6 / 6 | Δ > 2 % |
| ac_load_params | Gain peaking | dB | 1.257e-06 | 7.193e-08 | -94.28 % | 0.008028 | 1.537e-06 | -99.98 % | 2.749 | 2.466 | -10.31 % | -100.00 % (cload=1e-10, rload=1000000000.0) | 0.2835 | 6 / 6 | Δ > 2 % |
| ac_params | Closed-loop gain | dB | -6.05 | -6.05 | +0.00 % | -6.021 | -6.021 | +0.00 % | -6.021 | -6.021 | +0.00 % | +0.00 % (corner_mos=ss, temp=-40) | 0 | 15 / 15 |  |
| ac_params | Bandwidth | MHz | 1.762 | 1.569 | -10.99 % | 2.001 | 1.774 | -11.31 % | 2.245 | 2.016 | -10.22 % | -12.35 % (corner_mos=ss, temp=-40) | 0.2501 | 15 / 15 | Δ > 2 % |
| ac_params | Gain peaking | dB | 5.347e-08 | 4.475e-07 | +736.95 % | 8.238e-07 | 1.224e-06 | +48.56 % | 1.607e-06 | 1.815e-06 | +12.95 % | +852.31 % (corner_mos=fs, temp=125) | 7.796e-07 | 15 / 15 | Δ > 2 % |
| ac_params | PSRR iovdd 1 kHz | dB | 70.64 | 70.04 | -0.85 % | 71.54 | 70.93 | -0.85 % | 72.51 | 71.91 | -0.83 % | -0.96 % (corner_mos=ss, temp=-40) | 0.6923 | 15 / 15 |  |
| ac_params | PSRR iovdd 100 kHz | dB | 30.71 | 30.1 | -1.98 % | 31.6 | 31.06 | -1.71 % | 32.53 | 31.93 | -1.84 % | -2.17 % (corner_mos=ss, temp=-40) | 0.6902 | 15 / 15 | Δ > 2 % |
| ac_params | CMRR 1 kHz | dB | 95.19 | 95.13 | -0.07 % | 125 | 109 | -12.78 % | 128.4 | 110.3 | -14.10 % | -15.12 % (corner_mos=sf, temp=-40) | 19.42 | 15 / 15 | Δ > 2 % |
| ac_params | Output impedance 1 kHz | Ω | 0.1891 | 0.2083 | +10.11 % | 0.2094 | 0.2278 | +8.78 % | 3.302 | 3.304 | +0.05 % | +10.11 % (corner_mos=ss, temp=-40) | 0.01938 | 15 / 15 | Δ > 2 % |
| ac_params | Output impedance 1 MHz | Ω | 154.7 | 166 | +7.31 % | 167.4 | 181.3 | +8.30 % | 200.8 | 216.9 | +8.03 % | +9.26 % (corner_mos=ss, temp=125) | 17.85 | 15 / 15 | Δ > 2 % |
| dc_params | Gain |  | 0.4983 | 0.4983 | -0.00 % | 0.5 | 0.5 | -0.00 % | 0.5 | 0.5 | +0.00 % | -0.00 % (corner_mos=ff, temp=125, vdd=3.3) | 1e-06 | 30 / 30 |  |
| dc_params | Output offset | mV | 0.03202 | 0.04414 | +37.86 % | 0.06727 | 0.07998 | +18.90 % | 1.737 | 1.748 | +0.62 % | +37.86 % (corner_mos=ss, temp=-40, vdd=3.3) | 0.01341 | 30 / 30 | Δ > 2 % |
| dc_params | Integral nonlinearity | mV | 0.1208 | 0.1199 | -0.75 % | 0.4504 | 0.4495 | -0.21 % | 7.5 | 7.5 | -0.00 % | -0.75 % (corner_mos=ss, temp=125, vdd=3.6) | 0.000978 | 30 / 30 |  |
| dc_params | IO ring supply current | uA | 301.7 | 301.8 | +0.00 % | 311.3 | 311.3 | +0.00 % | 325.3 | 325.3 | +0.00 % | +0.00 % (corner_mos=ss, temp=125, vdd=3.6) | 0.011 | 30 / 30 |  |
| dc_params | Core ring supply current | nA | 0.008253 | 0.01425 | +72.70 % | 0.1185 | 0.1245 | +5.06 % | 23.89 | 23.9 | +0.03 % | +72.70 % (corner_mos=ss, temp=-40, vdd=3.6) | 0.00601 | 30 / 30 | Δ > 2 % |
| dc_params | Quiescent current OP | uA | 216.6 | 216.6 | +0.00 % | 225.5 | 225.5 | +0.00 % | 238.6 | 238.6 | +0.00 % | +0.00 % (corner_mos=ss, temp=27, vdd=3.6) | 0.007 | 30 / 30 |  |
| dc_params | Quiescent current ON | uA | 216.2 | 216.2 | -0.00 % | 225 | 225 | -0.00 % | 238.5 | 238.5 | -0.00 % | -0.00 % (corner_mos=ss, temp=-40, vdd=3.6) | 0.007 | 30 / 30 |  |
| dc_params | Minimum output-device current | uA | 104.7 | 104.7 | -0.02 % | 113.3 | 113.3 | -0.01 % | 120.3 | 120.3 | +0.00 % | -0.02 % (corner_mos=ss, temp=-40, vdd=3.3) | 0.017 | 30 / 30 |  |
| drive_params | Max output | V | 3.266 | 3.266 | +0.00 % | 3.275 | 3.275 | +0.00 % | 3.283 | 3.283 | +0.00 % | +0.00 % (corner_mos=ss, temp=-40) | 0 | 10 / 10 |  |
| drive_params | Min output | V | 0.6354 | 0.6354 | +0.00 % | 0.6823 | 0.6823 | +0.01 % | 0.7359 | 0.736 | +0.00 % | +0.01 % (corner_mos=ff, temp=125) | 5.3e-05 | 10 / 10 |  |
| drive_params | Short-circuit source current | mA | 49.71 | 49.71 | +0.00 % | 67.05 | 67.05 | +0.00 % | 93.31 | 93.31 | +0.00 % | +0.00 % (corner_mos=ss, temp=-40) | 0 | 10 / 10 |  |
| drive_params | Short-circuit sink current | mA | 54.77 | 54.77 | -0.00 % | 82.97 | 82.97 | -0.00 % | 124.2 | 124.2 | +0.00 % | -0.00 % (corner_mos=sf, temp=-40) | 0.001 | 10 / 10 |  |
| enable_params | Turn-on time | us | 0.982 | 1.109 | +12.92 % | 1.228 | 1.349 | +9.80 % | 1.819 | 2.387 | +31.23 % | +31.23 % (sel=1, tstop=6e-05) | 0.5681 | 3 / 3 | Δ > 2 % |
| enable_params | Enable glitch, positive | mV | 121.6 | 127.8 | +5.04 % | 124.4 | 128.7 | +3.44 % | 225.5 | 228.1 | +1.15 % | +5.04 % (sel=0, tstop=6e-05) | 6.127 | 3 / 3 | Δ > 2 % |
| enable_params | Enable glitch, negative | mV | -176.6 | -224.8 | -27.29 % | -112.8 | -132.5 | -17.49 % | -104.3 | -128.3 | -22.92 % | -27.29 % (sel=1, tstop=6e-05) | 48.19 | 3 / 3 | Δ > 2 % |
| enable_params | IO ring current after start-up | uA | 308.4 | 308.4 | +0.00 % | 315.6 | 315.7 | +0.03 % | 315.8 | 315.8 | +0.01 % | +0.03 % (sel=1, tstop=6e-05) | 0.106 | 3 / 3 |  |
| noise_params | Output noise 1 kHz | nV/rtHz | 605.1 | 605 | -0.02 % | 678.8 | 678.7 | -0.02 % | 715.4 | 715.3 | -0.02 % | -0.02 % (temp=-40) | 0.159 | 3 / 3 |  |
| noise_params | Output noise 100 kHz | nV/rtHz | 142.6 | 142.1 | -0.41 % | 152.6 | 151.9 | -0.46 % | 156.5 | 155.7 | -0.50 % | -0.50 % (temp=-40) | 0.788 | 3 / 3 |  |
| noise_params | Integrated output noise | uV | 223.3 | 214 | -4.16 % | 234.6 | 223.9 | -4.55 % | 235.6 | 224.2 | -4.84 % | -4.84 % (temp=-40) | 11.39 | 3 / 3 | Δ > 2 % |
| pd_params | IO ring current, off | nA | 0.04787 | 0.06358 | +32.80 % | 257.5 | 257.6 | +0.01 % | 642.2 | 642.2 | +0.00 % | +32.80 % (pdstate=0, vpad=3.3, corner_mos=tt, temp=27) | 0.0295 | 48 / 48 | Δ > 2 % |
| pd_params | Core ring current, off | nA | -0 | -0 | +0.00 % | 0.6509 | 0.6509 | +0.00 % | 23.89 | 23.89 | +0.00 % | +0.00 % (pdstate=0, vpad=1.65, corner_mos=tt, temp=27) | 1e-07 | 48 / 48 |  |
| pd_params | Pad leakage, off | nA | -36.83 | -36.85 | -0.04 % | 0.1758 | 0.1756 | -0.08 % | 14.94 | 14.95 | +0.09 % | -0.27 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 0.0167 | 48 / 48 |  |
| pd_params | vdd1v2_sense current | nA | -0 | -0 | +0.00 % | 1.271e-05 | 1.271e-05 | +0.00 % | 905.5 | 905.5 | +0.00 % | +0.00 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 0 | 48 / 48 |  |
| pd_params | vdd3v3_sense current | nA | -0 | -0 | +0.00 % | 0.0001149 | 0.0001149 | +0.00 % | 1114 | 1114 | +0.00 % | +0.02 % (pdstate=0, vpad=1.65, corner_mos=ff, temp=27) | 1.39e-08 | 48 / 48 |  |
| pd_params | Internal enable | V | 2.688e-10 | 2.688e-10 | +0.00 % | 1.392e-07 | 1.392e-07 | +0.00 % | 7.104e-07 | 7.104e-07 | +0.00 % | +0.00 % (pdstate=0, vpad=0, corner_mos=tt, temp=27) | 0 | 48 / 48 |  |
| thd_params | THD | dB | -73.33 | -73.15 | +0.24 % | -57.68 | -57.66 | +0.04 % | -38.66 | -38.66 | -0.00 % | +0.24 % (vdamp=0.5) | 0.1735 | 3 / 3 |  |
| thd_params | Output amplitude | V | 0.25 | 0.25 | -0.00 % | 0.5 | 0.4999 | -0.00 % | 0.7504 | 0.7504 | -0.00 % | -0.00 % (vdamp=1.5) | 5e-06 | 3 / 3 |  |
| tran_params | Slew rate, rising | V/us | 1.749 | 1.591 | -9.03 % | 2.429 | 2.151 | -11.44 % | 3.058 | 2.732 | -10.66 % | -12.02 % (corner_mos=ss, cload=1e-10) | 0.326 | 9 / 9 | Δ > 2 % |
| tran_params | Slew rate, falling | V/us | 1.764 | 1.603 | -9.09 % | 2.429 | 2.15 | -11.50 % | 3.135 | 2.794 | -10.89 % | -12.10 % (corner_mos=ss, cload=1e-10) | 0.3416 | 9 / 9 | Δ > 2 % |
| tran_params | Overshoot | % | -6e-05 | -9e-05 | -50.00 % | 0.0001 | 0 | -100.00 % | 9.115 | 7.986 | -12.39 % | -400.00 % (corner_mos=ss, cload=1e-11) | 1.129 | 9 / 9 | Δ > 2 % |
| tran_params | Settling time, rising | us | 0.3027 | 0.3549 | +17.27 % | 0.4581 | 0.5057 | +10.39 % | 0.6761 | 0.5478 | -18.97 % | -22.01 % (corner_mos=ss, cload=3e-10) | 0.1488 | 9 / 9 | Δ > 2 % |
| tran_params | Settling time, falling | us | 0.3107 | 0.3624 | +16.63 % | 0.4564 | 0.5038 | +10.41 % | 0.4965 | 0.5336 | +7.47 % | +16.63 % (corner_mos=ss, cload=1e-10) | 0.05167 | 9 / 9 | Δ > 2 % |
