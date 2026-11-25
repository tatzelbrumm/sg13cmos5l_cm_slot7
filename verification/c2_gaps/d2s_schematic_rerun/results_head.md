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

