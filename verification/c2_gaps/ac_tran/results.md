<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# AC / transient / noise curves: key numbers and cross-check

**IHP sg13cmos5l simulation (schematic | magic PEX)**. Figures, method, conditions and limits: [README.md](README.md).
Every number here is evaluated by the scripts of this folder from the plotted curves (`csv/*_summary.csv`, one row per
run) with the CACE template definitions; ranges are over the runs named. Units SI-prefixed as stated.

## 1. Slot round trip (tier-1 slot deck, default mode, replica bias, pad_s2d at 0.5 V DC)

Five tier-1 PVT points (corner, temperature, iovdd = vdd_3v3). Loads: unloaded = only the deck's 1 GΩ; 1 kΩ to an
ideal copy of vref_d2s with 10 or 100 pF. `csv/rt_*_summary.csv`; `*` = schematic run that needed the rshunt retry.

Round-trip −3 dB bandwidth [MHz] (relative to the gain at 1 kHz; `rt_bode_tt27`, `rt_bode_pvt`, `rt_f3db`):

| PVT | unloaded: sch / PEX / KLayout | 1 kΩ ∥ 10 pF | 1 kΩ ∥ 100 pF |
|---|---|---|---|
| tt 27 °C 3.3 V | 1.532 / 1.356 / 1.514 | 1.265 / 1.122 / 1.220 | 1.523 / 1.325 / 1.487 |
| ss -40 °C 3.0 V | 1.536* / 1.332 / 1.514 | 1.283* / 1.117 / 1.229 | 1.553* / 1.318 / 1.509 |
| ff 125 °C 3.6 V | 1.627 / 1.466 / 1.607 | 1.292 / 1.166 / 1.254 | 1.588 / 1.408 / 1.548 |
| fs 125 °C 3.6 V | 1.694 / 1.519 / 1.673 | 1.348 / 1.210 / 1.308 | 1.677 / 1.478 / 1.637 |
| sf -40 °C 3.0 V | 1.470 / 1.283 / 1.451 | 1.235 / 1.082 / 1.185 | 1.473 / 1.262 / 1.434 |

- Gain at 1 kHz −0.011 … −0.048 dB (0.9945 … 0.9988); no peaking above the 1 kHz gain in any of the 45 runs; phase at
  f−3dB −70 … −97°. The magic PEX pads cost 11 … 15 % bandwidth against the schematic; the KLayout-extracted pads (no
  parasitic capacitance, the designer's tier-1 view) 1 … 4 %. 1 kΩ ∥ 10 pF has the lowest bandwidth: the D2S alone
  shows the same order (`d2s_bode_loads`: 1.57 MHz at 1 kΩ + 10 pF vs 2.00 MHz at 1 kΩ + 100 pF).
- Step 0.25 → 0.75 V (10 ns edges), settling of pad_d2s to 1 % / 0.1 % of the step after the input edge, rise / fall
  (`rt_step_tt27`, `rt_step_pvt`):

| pads, tt 27 °C | unloaded | 1 kΩ ∥ 10 pF | 1 kΩ ∥ 100 pF |
|---|---|---|---|
| schematic | 460 / 461 ns; 633 / 634 ns | 557 / 552 ns; 778 / 768 ns | 453 / 465 ns; 593 / 619 ns |
| magic PEX | 517 / 518 ns; 710 / 711 ns | 623 / 617 ns; 867 / 856 ns | 524 / 533 ns; 696 / 714 ns |
| KLayout-extracted | 467 / 466 ns; 643 / 642 ns | 577 / 566 ns; 807 / 787 ns | 462 / 473 ns; 603 / 630 ns |

  Over the five PVT points (schematic, unloaded and 1 kΩ ∥ 100 pF): 1 % in 399 … 499 ns, 0.1 % in 470 … 679 ns;
  magic PEX (tt, ss −40 °C, ff 125 °C): 474 … 551 ns / 608 … 747 ns. Overshoot ≤ 0.05 % (fs 125 °C, 100 pF), none
  at −40 / 27 °C. Output step 497.99 … 499.36 mV for the 500 mV input step (gain 0.9960 … 0.9987).
- 10 kHz sine 0 … 1 V (`rt_sine_tt27`), tt 27 °C: THD (harmonics 2–7) −78.2 dB schematic unloaded, −72.5 dB with
  1 kΩ ∥ 100 pF, −77.9 / −72.0 dB with the PEX pads; gain at 10 kHz 0.9985 … 0.9986, delay 146 ns (schematic,
  unloaded) … 192 ns (PEX, 100 pF); pad_d2s − expected 9.2 … 12.4 mVpp, which is the delay (2π · 10 kHz · 0.5 V ·
  146 ns = 4.6 mV amplitude), not distortion. Other PVT points (schematic, unloaded): sf −40 °C −70.6 dB, ss −40 °C
  −67.9 dB, fs 125 °C −61.7 dB, ff 125 °C −53.4 dB (H2 dominant): at 125 °C the input's low end 0 V lies below the
  1 mV-linear S2D input range (`../dc_curves`: ff 125 °C from +0.096 V, fs 125 °C from +0.028 V), so the bottom of the
  sine is distorted there.
- Not obtained: the sine through the KLayout-extracted pads (tt 27 °C) aborts with "timestep too small" at 66 µs
  (pad_s2d ≈ 0.078 V on the falling slope; the same input level when the sine phase is shifted, also with cshunt
  1 fF / 10 fF and rshunt; no node moves faster there in the saved waveforms: a numerical problem of that netlist
  combination, not found). The schematic and PEX pads run through. TBD.
  **Resolved 2026-11-25** (see the Follow-up at the end and [../klayout_pad_diodes](../klayout_pad_diodes/README.md)):
  the converted KLayout netlists simulate the pad diodes at the PDK default size; with the extracted size the sine
  runs through and matches the schematic pads within 0.07 mV.
- Solver aids: PEX pads always rshunt=1e12; schematic pads only in the runs marked `*` / `aid=rshunt` in the CSVs
  (ss −40 °C AC / step / sine, sf −40 °C step: operating point not found without it). Its effect, measured on the tt
  27 °C schematic AC run forced with it: f−3dB +0.0005 %, gain −4e-6 dB (`tables/rt_consistency.md`).

## 2. S2D alone (CACE conditions: iovdd 3.3 V, vref 1.2 V, vcm 1.2 V, rsrc 50 Ω, 0.5 pF per output)

| quantity | schematic | magic PEX | runs |
|---|---|---|---|
| closed-loop gain at 1 kHz | 6.015 … 6.017 dB | 6.015 … 6.017 dB | 5 corners × −40 / 27 / 125 °C |
| −3 dB bandwidth | 1.351 … 1.811 MHz (tt 27 °C 1.538) | 1.236 … 1.664 MHz (tt 27 °C 1.409) | same; set by temperature (−40 °C low, 125 °C high), corners within ±1 % |
| phase at f−3dB (tt 27 °C) | −47° | −47° | single-pole-like roll-off to about −45 dB, then a feed-through floor (s2d_bode) |
| output CM per volt iovdd at 1 kHz (CMvdd) | −58.3 … −53.9 dB | −58.3 … −53.9 dB | 15; rises to about −26 dB (schematic) / −20 dB (PEX) near 3 MHz |
| 10–90 % rise, 0.001 pF | 104 … 146 ns (tt 27 °C 126) | 121 … 171 ns (tt 27 °C 147) | ss / tt / ff × 3 temperatures |
| 10–90 % rise, 0.5 pF | 194 … 259 ns (tt 228) | 211 … 283 ns (tt 249) | same |
| settling to 1 %, 0.001 pF | 222 … 310 ns (tt 267) | 259 … 360 ns (tt 311) | same |
| settling to 1 %, 0.5 pF | 412 … 546 ns (tt 481) | 448 … 596 ns (tt 525) | same |
| overshoot | 0.00002 % max | 0.00001 % max | none (first-order settling) |
| output CM deviation during the step | 7.4 … 15.7 mV | 7.7 … 16.0 mV | same |
| input-referred noise at 1 kHz | 596 … 727 nV/√Hz (tt 27 °C 680) | 596 … 726 nV/√Hz (tt 679) | 15 |
| input-referred noise at 100 kHz | 142 … 157 nV/√Hz (tt 153) | 142 … 156 nV/√Hz (tt 152) | 15 |
| output noise 10 Hz … 10 MHz (CACE Vn_out) | 428 … 441 µVrms (tt 439) | 411 … 423 µVrms (tt 421) | 15 |
| input-referred noise 10 Hz … 1 MHz | 146 … 162 µVrms (tt 157) | 146 … 161 µVrms (tt 156) | 15 |
| enable time (vd within 1 mV) | 1.36 … 1.43 µs (tt 1.40) | 1.46 … 1.52 µs (tt 1.50) | ss / tt / ff × 3 temperatures |
| output CM excursion after enable | +0.211 … +0.271 V / −11 … −3 mV | +0.220 … +0.287 V / −4 … −3 mV | same |
| iovdd current enabled (testbench ring) | 115.2 … 116.1 µA | 115.2 … 116.1 µA | same |

Disable (s2d_enable): outp − outn collapses to 0 within about 20 ns of the en_1v2 falling edge, the iovdd current
decays from about 116 µA to a few µA within about 2 µs after a 0.6 mA spike at the edge (tt 27 °C; the enable edge has a 1.0 mA spike).

## 3. D2S alone (CACE conditions: vicm = vref = vterm = 1.65 V, 1 kΩ to vterm + 100 pF, iovdd 3.3 V)

| quantity | schematic | magic PEX | runs |
|---|---|---|---|
| −3 dB bandwidth, 1 kΩ + 100 pF | 1.76 … 2.25 MHz | 1.57 … 2.02 MHz | 5 corners × 3 temperatures |
| PSRR (iovdd, output-referred) 1 kHz / 100 kHz | 70.6 … 72.5 / 30.7 … 32.5 dB | 70.0 … 71.9 / 30.1 … 31.9 dB | same; minimum about 8 dB near 3 MHz (d2s_psrr) |
| \|Zout\| incl. load at 1 kHz / 1 MHz | 0.19 … 3.30 / 155 … 201 Ω | 0.21 … 3.30 / 166 … 217 Ω | same; at 1 kHz 0.6 … 3.3 Ω at 125 °C, 0.19 … 0.22 Ω at −40 / 27 °C (about 0.1 Ω below 100 Hz) |
| CMRR at 1 kHz (systematic) | 95 … 128 dB | 95 … 110 dB | same |

Bandwidth and peaking vs load (tt 27 °C, `d2s_bode_loads`; f−3dB from the 1 kHz gain, peaking = maximum above it):

| load | schematic f−3dB / peaking | magic PEX f−3dB / peaking |
|---|---|---|
| 1 kΩ + 10 pF | 1.574 MHz / none | 1.425 MHz / none |
| 1 GΩ + 10 pF | 2.243 MHz / none | 2.036 MHz / none |
| 1 kΩ + 100 pF | 2.001 MHz / none | 1.781 MHz / none |
| 1 GΩ + 100 pF | 2.984 MHz / 0.016 dB | 2.713 MHz / none |
| 1 kΩ + 300 pF | 2.044 MHz / 0.72 dB at 1.05 MHz | 1.885 MHz / 0.51 dB at 0.91 MHz |
| 1 GΩ + 300 pF | 2.329 MHz / 2.75 dB at 1.38 MHz | 2.180 MHz / 2.47 dB at 1.32 MHz |
| 1 kΩ + 1 nF | 1.350 MHz / 4.77 dB at 0.83 MHz | 1.270 MHz / 4.43 dB at 0.79 MHz |
| 1 GΩ + 1 nF | 1.396 MHz / 7.43 dB at 0.87 MHz | 1.318 MHz / 7.11 dB at 0.83 MHz |

Large-signal step (pad 1.40 ↔ 1.90 V, 1 kΩ to vterm; ss / tt / ff, 27 °C; slew 10–90 %, rise / fall):

| load | schematic SR [V/µs] | settling 1 % [ns] | overshoot | magic PEX SR [V/µs] | settling 1 % [ns] |
|---|---|---|---|---|---|
| 10 pF | 1.75 … 1.95 (tt 1.84 / 1.86) | 435 … 481 (tt 458 / 456) | 0 | 1.59 … 1.75 (tt 1.67 / 1.68) | 483 … 528 (tt 506 / 504) |
| 100 pF | 2.26 … 2.60 (tt 2.43 / 2.43) | 303 … 374 (tt 335 / 341) | 0 | 2.01 … 2.29 (tt 2.15 / 2.15) | 355 … 422 (tt 385 / 392) |
| 300 pF | 2.77 … 3.14 (tt 2.92 / 2.98) | 472 … 676 (tt 496 / 484) | 6.5 … 9.1 % | 2.50 … 2.79 (tt 2.62 / 2.67) | 512 … 548 (tt 537 / 523) |

The slew "rate" rises with the load: with 1 kΩ to vterm the 0.5 V step is a small signal for this driver, and the
10–90 % time follows the closed-loop bandwidth / peaking (above), not a current limit.

At the slot operating point vicm = vref = vterm = 1.26 V (`d2s_slot_vs_cace`, schematic, tt 27 °C unless noted):
bandwidth over the 15 PVT runs 1.73 … 2.29 MHz (1.65 V: 1.76 … 2.25), peaking at 1 kΩ + 1 nF 4.80 dB (4.77), PSRR
1 kHz 68.6 … 71.2 dB (2 dB lower than at 1.65 V), \|Zout\| unchanged within 2 %, step slew within 5 % (300 pF rising
edge tt 2.81 vs 2.92 V/µs), settling within 10 % except the 300 pF rising edge (tt 691 vs 496 ns: the ring after the 9 % overshoot crosses the 1 % band
once more). PEX at 1.26 V: the same differences as schematic (`csv/d2s_*_summary.csv`, groups `*_slot`).

Noise (tt 27 °C; output density at the pad, includes the 1 kΩ): schematic 679 nV/√Hz at 1 kHz, 153 nV/√Hz at 100 kHz,
235 µVrms integrated 10 Hz … 10 MHz; PEX 679 / 152 nV/√Hz, 224 µVrms. Over 15 PVT: 593 … 726 nV/√Hz at 1 kHz,
217 … 240 µVrms (schematic).

Enable (tt 27 °C, sel 0): pad − vref within 1 mV after 0.98 µs (schematic) / 1.11 µs (PEX), excursion −104 … +122 mV
(schematic) / −128 … +128 mV (PEX) during the start-up, iovdd 308 µA enabled with a start-up hump to about 1.1 mA;
sel 1 / 2: 1.82 / 1.23 µs (schematic), 2.39 / 1.35 µs (PEX). Disable: pad − vref stays within −2 … +1 mV (the 1 kΩ
holds the pad at vterm), the iovdd current falls to the µA level within about 0.5 µs.

## 4. Cross-check with the committed CACE results

`crosscheck.py` → `csv/crosscheck.csv`, `tables/crosscheck.md` (244 comparisons). For each quantity: the committed CACE
value, the value this run's unchanged CACE `.control` block printed (`.data`), and the value from the curves.

- **S2D, schematic and magic PEX** (design 91a7da8b results, committed 2026-11-05: ac, tran, noise, enable;
  f−3dB, Acl, CMvdd, En 1 k / 100 k, Vn_out, rise, settle, Vcm_dev, t_on, Iio at tt 27, ss −40, ff 125 °C, both
  loads): `.data` identical to the committed values (0.000 %); from the curves within 0.10 % (f−3dB: the dec 40 grid
  here vs dec 20 in CACE, interpolation) and 0.05 % (Vn_out: trapezoid on dec 40 vs ngspice's integral on dec 20).
- **D2S, magic PEX** (this repository's `../d2s_pex/csv`, 2026-11-24): `.data` identical (≤ 0.0007 %), curves within
  0.1 % for f−3dB, PSRR 1 k / 100 k, Zout 1 k / 1 M, SR, settling, noise, t_on, Iio. The only flags are peaking values
  of 1e-8 … 2e-6 dB (numerically zero; no peaking at those loads).
- **D2S, schematic**: 24 values differ by more than 2 % from the committed CSVs, **in `.data` as much as in the
  curves**, so not from the curve evaluation: Zout 1 kHz −3.1 … −14 %, Zout 1 MHz −2.5 %, peaking at 300 pF / 1 nF
  −2 … −8 % (0.06 … 0.17 dB), settling 100 pF +2.2 … +2.4 %, settling fall ss 300 pF −23 % (a ringing tail crossing the
  1 % band), t_on +15 … +53 %, Iio +2.2 … +3.3 %; f−3dB, PSRR, SR and noise agree within 2.2 %. Cause: the committed
  D2S schematic CSVs are older than the schematic they are compared with. In the design repository's history
  (fetched for this check) every D2S CSV last changed on 2026-10-21 (commit f3fdcf6, the move into the macro
  hierarchy), while the D2S schematic changed until 2026-11-03 (commits bd392f3 … 2abcca1: layout backannotation,
  bias tree dummies, vss / iovss tie); the S2D CSVs were rerun on 2026-11-05 after its last schematic change and are
  reproduced exactly. That the setup is not the cause: the same unchanged templates reproduce the S2D CSVs and the
  D2S PEX CSVs to 0.000 %, and the solver aid rshunt has no effect on the D2S schematic (below). These rows are marked
  `stale ref` in `tables/crosscheck.md`.
- **Solver aid rshunt=1e12** on the D2S schematic (`tables/rshunt.md`, the same groups with and without it): every
  scalar within 0.006 % (Zout 1 kHz), the rest ≤ 0.003 %. So it does not explain any schematic-vs-PEX difference.
- **Round trip** (no committed CACE values; `tables/rt_consistency.md`): \|gain\| at 10 Hz and the 0.5 V step gain
  agree with the DC small-signal slope of `../dc_curves` within 0.02 % (0.99852 … 0.99876 vs 0.99848 … 0.99882), and
  the replica operating point (vref_s2d / vcm) is identical (4 digits) for every view and PVT point; the designer's
  committed tier-1 results (9052bd35, `results.txt`: tt 1.257 / 0.492 V, ss 1.115 / 0.447 V, …) agree to their
  3 digits.

Remarks found on the way (no change made): the CACE yaml labels S2D `Vcm_dev` and D2S `Glitch_max` / `Glitch_min` as
mV, but the templates compute them in V (S2D Vcm_dev = 0.012 means 12 mV; its 50 "mV" limit is therefore compared
with a value in V, i.e. effectively 50 V). Several other CSV unit labels (f3dB "MHz", En "nV/rtHz", SR "V/µs") are
likewise SI values; this folder converts them.

## Follow-up 2026-11-25: the KLayout sine abort

Cause found; details, scripts and data in [../klayout_pad_diodes](../klayout_pad_diodes/README.md).

- **The conversion bug.** The designer's converter `run_starve.convert()` (design repository 9052bd35,
  `macros/en_ctrl_3v3/testbenches/spice/run_starve.py` lines 44–45; used by `run_tier1.wrapped()`) passes KLayout's
  diode `A=` / `P=` to the PDK subcircuits `dantenna` / `dpantenna` as `a=` / `p=`. Those subcircuits read only
  `l` / `w`. ngspice drops the unknown parameters without a message, so all pad antenna diodes are simulated at
  0.78 × 0.78 µm, 0.7 … 1.7 % of their area.
- **Why the run aborts.** ngspice's `darea` model has a 37 pA current step at a reverse voltage of 3·n·kT/q
  = 78.3 mV (27 °C). The step is the soft-breakdown term (ibv, nbv = 48.9), added when the model switches to its
  reverse-region expression. pad_s2d = 0.0783 V is that point on the S2D pad diode X$65. With the default size
  ngspice cannot pass the step: X$65 alone under the same sine aborts at the same 65.9723 µs. With the extracted size
  it passes.
- **The sine with the fix.** The diodes get l / w from A / P (the schematic sizes). The run then goes through with no
  solver aid. Unloaded: THD −78.3 dB, gain 0.9985, delay 148 ns, error 9.3 mVpp; pad_d2s is within 0.07 mV of the
  schematic pads. With 1 kΩ ∥ 100 pF: THD −69.9 dB, delay 175 ns.
- **Other KLayout results.** The KLayout AC / step results of section 1 change by under 0.1 % with the fix. The
  KLayout DC range-end shift in ../dc_curves is **not** caused by the diodes: it is unchanged within 2 nV. It sits in
  the S2D output common mode, 33 mV lower than schematic at tt 27 °C, cause not found.
- **Still open.** The −40 °C aborts in ../slot_modes_bg are not cured by the fix.
