<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Results: DC curves of the S2D and D2S pads

IHP sg13cmos5l simulation (schematic | magic PEX), ngspice-47, CACE 2.11, 2026-11-24. Method, criteria, conditions and
limits: [README.md](README.md). Every number here is from the runs of `run.sh` in this folder (tables generated into
`tables/`, per-run values in `csv/`).

Status: complete.

> **Note added 2026-11-25 (whole-slot extraction):** the slot-level runs here use the designer's tier-1 deck, whose `pad_ref_rb` is the
> KLayout-converted netlist. Its `vcm` is 3.5 … 4.9 mV low at −40 / 27 °C and 13 … 24 mV low at 125 °C, `vref` 1.8 mV low, against the
> `pad_ref_rb` schematic, its PEX and the extracted whole slot; the round-trip error is unchanged (≤ 0.003 mV), the 1 mV-linear range's
> high end moves up with `vcm` (+6 mV at tt 27 °C, +32 mV at ff 125 °C). The pad PEX netlists lack the pads' substrate capacitance
> (no effect on DC). Details: [../slot_pex/results.md](../slot_pex/results.md) §3.

## Key numbers

| quantity | conditions | result |
|---|---|---|
| S2D linear input range (1 mV, input-referred) | vref 0.5 V, vcm 1.2 V, 5 corners × 3 T × 3.0 / 3.3 / 3.6 V | high end 1.057 (ss −40 °C 3.0 V) … 1.299 V; low end ≤ 0 V except 125 °C (≤ 0.087 V); tt 27 °C 3.3 V: −0.149 … 1.245 V |
| S2D at the slot's vref 0.49 V / vcm 1.26 V | same grid | high end 0.980 (ss −40 °C 3.0 V) … 1.351 V; tt 27 °C 3.3 V: −0.157 … 1.296 V |
| D2S linear output range (10 mV, output-referred) | vicm = vref 1.65 V (CACE), 1 kΩ | 3.3 V: worst 1.121 … 2.180 V (ss −40 °C), tt 27 °C 0.985 … 2.314 V; 3.0 V: worst 1.449 … 1.851 V; 3.6 V: worst 0.737 … 2.558 V |
| D2S at the slot's vicm = vref 1.26 V | 1 kΩ to 1.26 V | 3.3 V: worst ends 0.328 / 2.258 V (ff 125 °C), tt 27 °C 0.211 … 2.317 V; 3.0 V: worst 0.627 … 1.894 V (ss −40 °C) |
| D2S INL (±1 V, CACE definition) | vicm 1.65 V / 1.26 V | 3.0 V: ≤ 88.4 / ≤ 1.38 mV; 3.3 V: ≤ 7.50 / ≤ 0.56 mV; 3.6 V: ≤ 0.49 / ≤ 0.50 mV |
| D2S swing at vinp − vinn = ∓3 V | vicm 1.65 V, 1 kΩ, 3.3 V | 0.635 … 0.736 V / 3.266 … 3.283 V (unloaded: up to 3.300 V) |
| Round trip, 1 mV range (pads schematic) | slot deck, replica bias, tt 27 °C 3.3 V | pad in −0.171 … 1.281 V → pad out 0.595 … 2.044 V; max \|err\| over 0 … 1 V 0.86 mV (6.10 mV at ff 125 °C 3.6 V) |
| schematic vs magic PEX | all of the above | range ends within 0.7 mV, INL / error curves within 0.03 mV |

## 1. S2D pad (sg13cmos5l_IOPadSingle2Diff): input range and linearity

Conditions: CACE `tb_dc` sources, vref 0.5 V, vcm 1.2 V, harness iref 5 µA, 50 Ω source, 0.5 pF per output; pad
swept −0.3 … 3.3 V in 2 mV steps; 5 MOS corners × −40 / 27 / 125 °C × iovdd 3.0 / 3.3 / 3.6 V = 45 runs per view,
45 / 45 completed in both views.

**Linear input range (|error from the small-signal line| < 1 mV, input-referred; the CACE `window_params`
criterion).** High end 1.057 V (ss −40 °C 3.0 V) … 1.299 V (ff −40 °C 3.6 V) over all 45 runs; at iovdd ≥ 3.3 V
1.153 … 1.299 V (lowest at ss 125 °C 3.6 V). Low end: below 0 V (down to −0.252 V) at −40 and 27 °C; above 0 V at 125 °C,
at most 0.087 V (ff 125 °C 3.6 V). The range at tt 27 °C 3.3 V is −0.149 … 1.245 V. So the documented range
"0 … about 1 V at vref = 0.5 V" holds in every run for the upper end (≥ 1.057 V) and is met at 0 V except at 125 °C,
where the error from the small-signal line reaches 1 mV between pad 0.013 V and 0.087 V depending on the corner.

- Gain (small-signal, from u = ±0.1 V) 1.99676 … 1.99783 (ideal 2; −0.16 … −0.11 %), systematic offset < 1 µV.
- Error vs the ideal 2 (pad − vref), referred to the input, over pad 0 … 1 V: at most 4.34 mV (ff 125 °C, at pad
  = 0 V); at −40 / 27 °C at most 0.98 mV with iovdd ≥ 3.3 V and 1.47 mV at 3.0 V (ss −40 °C). Inside the range it is
  mostly the gain error (−0.12 % ≈ 0.6 mV at pad = vref ± 0.5 V).
- Schematic vs magic PEX: identical within 0.03 mV in the range ends and 0.029 mV in the error curves (C-coupled
  extraction, DC).
- Above the range the outputs saturate: at tt 27 °C 3.3 V, outp − outn rises to about 2.7 V with a step near pad
  1.53 V (`s2d_transfer_tt27_*`), the common mode leaves vcm there.

Cross-check with the committed CACE `window_params` (design 91a7da8b, ss / tt / ff × 3 T × 3 V, 27 runs per view):
Vin_max agrees within 0.62 mV (schematic and PEX; CACE sweeps in 10 mV steps, here 2 mV), Vin_min (clipped at 0 V
as CACE) within 0.25 mV; committed Vin_max 1.0575 … 1.2993 V, here 1.0571 … 1.2994 V (`tables/crosscheck.md`).

Range table per corner (schematic; PEX in `tables/s2d_grid.md`, equal to ±0.03 mV):

| corner | T [°C] | 3.0 V | 3.3 V | 3.6 V |
|---|---|---|---|---|
| tt | -40 | -0.090 ... 1.126 | -0.233 ... 1.289 | -0.240 ... 1.291 |
| tt | 27 | -0.098 ... 1.172 | -0.149 ... 1.245 | -0.151 ... 1.245 |
| tt | 125 | 0.050 ... 1.161 | 0.049 ... 1.164 | 0.050 ... 1.163 |
| ss | -40 | -0.032 ... 1.057 | -0.236 ... 1.278 | -0.246 ... 1.283 |
| ss | 27 | -0.059 ... 1.101 | -0.171 ... 1.236 | -0.174 ... 1.236 |
| ss | 125 | 0.018 ... 1.142 | 0.013 ... 1.154 | 0.014 ... 1.153 |
| ff | -40 | -0.136 ... 1.193 | -0.216 ... 1.299 | -0.221 ... 1.299 |
| ff | 27 | -0.099 ... 1.223 | -0.115 ... 1.254 | -0.116 ... 1.254 |
| ff | 125 | 0.086 ... 1.175 | 0.086 ... 1.175 | 0.087 ... 1.174 |
| sf | -40 | -0.114 ... 1.160 | -0.220 ... 1.287 | -0.226 ... 1.288 |
| sf | 27 | -0.099 ... 1.197 | -0.125 ... 1.242 | -0.127 ... 1.241 |
| sf | 125 | 0.077 ... 1.159 | 0.077 ... 1.161 | 0.077 ... 1.160 |
| fs | -40 | -0.062 ... 1.091 | -0.243 ... 1.291 | -0.252 ... 1.295 |
| fs | 27 | -0.084 ... 1.138 | -0.170 ... 1.248 | -0.172 ... 1.249 |
| fs | 125 | 0.025 ... 1.161 | 0.022 ... 1.168 | 0.023 ... 1.167 |

(Vin_min … Vin_max in V, pad voltage; vref 0.5 V.)

### 1b. S2D at the slot's nominal replica values (vref 0.49 V, vcm 1.26 V)

Same sweep with vref 0.49 V and vcm 1.26 V fixed (the replica's tt 27 °C values; schematic, 45 / 45 runs; table in
`tables/s2d_slot.md`, figure `s2d_range_slot`). High end 0.980 V (ss −40 °C 3.0 V) … 1.351 V (ff −40 °C 3.6 V); at
iovdd ≥ 3.3 V at least 1.205 V; tt 27 °C 3.3 V −0.157 … 1.296 V. Low end above 0 V only at 125 °C (at most 0.086 V)
and at ss −40 °C 3.0 V (0.018 V). So with vcm held at 1.26 V, the 1 V high end is missed only at ss −40 °C 3.0 V
(0.980 V); in the slot the replica lowers vcm there (1.115 V at ss −40 °C 3.0 V, section 3), and the round trip at that
point keeps −0.243 … 1.055 V. Max |error vs ideal| over pad 0 … 1 V 4.37 mV, gain 1.99642 … 1.99777.

## 2. D2S pad (sg13cmos5l_IOPadDiff2Single): output range and linearity

Conditions: CACE `tb_dc` sources and load (vref = vicm = vterm 1.65 V, 1 kΩ from pad to vterm + 100 pF; "unloaded"
= 1 TΩ instead of 1 kΩ), harness iref 5 µA; vinp − vinn swept from 0 to +3.3 V and from 0 to −3.3 V in 5 mV steps;
5 MOS corners × −40 / 27 / 125 °C × iovdd 3.0 / 3.3 / 3.6 V = 45 runs per view and load, 45 / 45 completed in all
four sets. ngspice option rshunt = 1e12 in both views (see README.md, "Solver aids").

**Linear output range (|error from the small-signal line| < 10 mV, output-referred; 10 mV = the CACE `dc_params`
INL limit).** At iovdd 3.3 V: 0.985 … 2.314 V at tt 27 °C; worst corner ss −40 °C 1.121 … 2.180 V; best ends
0.792 V / 2.519 V (ff 125 °C). At 3.6 V: 0.580 … 2.723 V at best, worst ss −40 °C 0.737 … 2.558 V. At **3.0 V the range
collapses**: worst ss −40 °C 1.449 … 1.851 V (±0.2 V around vref = 1.65 V), best ff 125 °C 1.162 … 2.152 V.

- The range is not set by the output stage: loaded (1 kΩ) and unloaded give the same range ends (both views, same
  table in `tables/d2s.md`). At −40 / 27 °C (iovdd 3.3 V) the error from the small-signal line exceeds 10 mV near
  pad 0.9 … 1.1 V and 2.2 … 2.4 V and has a local maximum near pad 2.4 V (11.7 … 56.0 mV) before the output saturates;
  at 125 °C it stays below 10 mV up to the saturation knees (`d2s_linearity_criterion`). Above vinp − vinn ≈ +1.75 V
  (vinp = 2.51 … 2.58 V at 3.3 V) the pad jumps to the upper rail (`d2s_transfer_tt27_*`, `d2s_corners_*`).
- Saturation (pad at vinp − vinn = −3 / +3 V, as CACE `drive_params`): 1 kΩ to 1.65 V, iovdd 3.3 V: 0.635 … 0.736 V /
  3.266 … 3.283 V; unloaded: 0.635 … 0.735 V / 3.300 V (the rail). 3.0 V: 0.717 … 0.840 / 2.971 … 2.985 V (1 kΩ);
  3.6 V: 0.539 … 0.618 / 3.561 … 3.581 V (1 kΩ).
- INL (CACE definition, max over vinp − vinn = ±1 V): 3.3 V 0.41 … 7.50 mV (ss −40 °C), 3.6 V ≤ 0.49 mV, 3.0 V
  11.1 … 88.4 mV (ss −40 °C) — the known headroom limit at 3.0 V with vicm = 1.65 V.
- Gain (from ±0.2 V) 0.4982 … 0.5002 (ideal 0.5), systematic output offset ≤ 1.78 mV (125 °C; ≤ 0.11 mV at −40 /
  27 °C).
- Schematic vs magic PEX: range ends within 0.45 mV, INL within 0.001 mV, pad at ±3 V within 0.32 mV.

Cross-check with the committed CACE results (design 91a7da8b, schematic; `tables/crosscheck.md`): gain within 0.00028;
INL within 0.09 mV at 3.3 / 3.6 V and within 1.07 mV at 3.0 V (88.43 here vs 87.36 mV committed at ss −40 °C: about
+1.2 % in every 3.0 V run; output offsets 8 … 13 % lower here, at the 0.03 … 2 mV level); `drive_params` Vout_max within
0.08 mV, Vout_min within 4.2 mV. The solver aid rshunt does not cause the INL difference: the same ±1 V sweeps without
it give the same INL within 0.002 mV (check step). Its cause was not found here (the S2D CACE results are reproduced
within 0.04 mV by the same method; the committed D2S CACE results predate the D2S layout, `../d2s_pex/README.md`, and
whether they were made from the same schematic netlist was not checked).

Output range per corner, schematic, 1 kΩ load (pad-voltage span [V] with |error from small-signal line| < 10 mV; PEX
and unloaded in `tables/d2s.md`):

| corner | T [°C] | 3.0 V | 3.3 V | 3.6 V | INL ±1 V at 3.0 / 3.3 / 3.6 V [mV] |
|---|---|---|---|---|---|
| tt | -40 | 1.387 ... 1.914 | 1.054 ... 2.247 | 0.604 ... 2.698 | 75.73 / 2.38 / 0.20 |
| tt | 27 | 1.349 ... 1.952 | 0.986 ... 2.314 | 0.638 ... 2.667 | 44.95 / 1.38 / 0.15 |
| tt | 125 | 1.238 ... 2.065 | 0.810 ... 2.496 | 0.697 ... 2.640 | 16.43 / 0.60 / 0.22 |
| ss | -40 | 1.449 ... 1.851 | 1.121 ... 2.180 | 0.737 ... 2.558 | 88.43 / 7.50 / 0.24 |
| ss | 27 | 1.413 ... 1.887 | 1.062 ... 2.238 | 0.664 ... 2.639 | 55.20 / 3.83 / 0.17 |
| ss | 125 | 1.310 ... 1.990 | 0.830 ... 2.473 | 0.692 ... 2.628 | 21.96 / 1.03 / 0.12 |
| ff | -40 | 1.324 ... 1.977 | 0.987 ... 2.314 | 0.580 ... 2.723 | 57.76 / 0.88 / 0.18 |
| ff | 27 | 1.284 ... 2.017 | 0.897 ... 2.400 | 0.614 ... 2.693 | 32.92 / 0.59 / 0.15 |
| ff | 125 | 1.162 ... 2.152 | 0.792 ... 2.519 | 0.720 ... 2.638 | 11.10 / 0.70 / 0.49 |
| sf | -40 | 1.355 ... 1.946 | 1.020 ... 2.281 | 0.593 ... 2.710 | 66.95 / 1.38 / 0.18 |
| sf | 27 | 1.316 ... 1.985 | 0.943 ... 2.356 | 0.626 ... 2.680 | 38.91 / 0.86 / 0.14 |
| sf | 125 | 1.197 ... 2.107 | 0.798 ... 2.509 | 0.696 ... 2.643 | 13.49 / 0.41 / 0.16 |
| fs | -40 | 1.419 ... 1.882 | 1.088 ... 2.213 | 0.615 ... 2.687 | 83.24 / 4.30 / 0.22 |
| fs | 27 | 1.382 ... 1.919 | 1.025 ... 2.275 | 0.651 ... 2.653 | 50.58 / 2.30 / 0.16 |
| fs | 125 | 1.277 ... 2.026 | 0.821 ... 2.484 | 0.703 ... 2.634 | 19.44 / 0.93 / 0.33 |

### 2b. D2S at the slot's operating point (vref = vicm = 1.26 V)

Same testbench with vref = vicm = vterm = 1.26 V (the slot's vcm, D2S vref = vcm), 1 kΩ to 1.26 V + 100 pF, vinp − vinn
swept 0 … ±2.52 V (inputs stay in 0 … 2.52 V); 45 runs per view, 45 / 45 complete in both views.

**Here the D2S is far more linear than at the CACE vicm = 1.65 V, also at iovdd 3.0 V**: INL (±1 V) at most 1.38 mV at
3.0 V (ss −40 °C; 88.4 mV at vicm 1.65 V), 0.56 mV at 3.3 V, 0.50 mV at 3.6 V. Output range (10 mV criterion) at
3.3 V: 0.152 … 2.373 V at best, worst ends 0.328 V / 2.258 V (ff 125 °C); tt 27 °C 0.211 … 2.317 V. At 3.0 V: worst
ss −40 °C 0.627 … 1.894 V. The low saturation level moves with vicm: pad at vinp − vinn = −2.52 V is 0.115 … 0.230 V
(3.3 V), whereas at vicm 1.65 V the pad stops at 0.64 … 0.74 V. The jump to the upper rail (first point with pad more
than 100 mV above ideal) comes at vinp = 2.33 … 2.40 V at 3.3 V (3.0 V: 2.17 … 2.26 V; 3.6 V: 2.36 … 2.45 V), against
2.51 … 2.58 V at vicm 1.65 V (3.0 V: 2.37 … 2.44 V; 3.6 V: 2.67 … 2.74 V). Schematic vs PEX: range ends within 0.69 mV, INL within 0.001 mV.
Gain 0.4983 … 0.5000, output offset ≤ 1.79 mV (125 °C).

| corner | T [°C] | 3.0 V | 3.3 V | 3.6 V | INL ±1 V at 3.0 / 3.3 / 3.6 V [mV] |
|---|---|---|---|---|---|
| tt | -40 | 0.557 ... 1.963 | 0.176 ... 2.348 | 0.107 ... 2.424 | 0.61 / 0.17 / 0.10 |
| tt | 27 | 0.344 ... 2.178 | 0.211 ... 2.317 | 0.176 ... 2.357 | 0.43 / 0.13 / 0.09 |
| tt | 125 | 0.377 ... 2.153 | 0.301 ... 2.264 | 0.289 ... 2.285 | 0.39 / 0.26 / 0.22 |
| ss | -40 | 0.627 ... 1.894 | 0.200 ... 2.322 | 0.108 ... 2.422 | 1.38 / 0.19 / 0.10 |
| ss | 27 | 0.546 ... 1.973 | 0.232 ... 2.294 | 0.175 ... 2.356 | 0.86 / 0.14 / 0.09 |
| ss | 125 | 0.400 ... 2.126 | 0.285 ... 2.262 | 0.266 ... 2.290 | 0.38 / 0.14 / 0.11 |
| ff | -40 | 0.486 ... 2.034 | 0.152 ... 2.373 | 0.106 ... 2.425 | 0.38 / 0.15 / 0.11 |
| ff | 27 | 0.321 ... 2.201 | 0.200 ... 2.331 | 0.177 ... 2.356 | 0.28 / 0.12 / 0.11 |
| ff | 125 | 0.365 ... 2.179 | 0.328 ... 2.258 | 0.320 ... 2.275 | 0.67 / 0.56 / 0.50 |
| sf | -40 | 0.522 ... 1.999 | 0.164 ... 2.360 | 0.107 ... 2.423 | 0.47 / 0.16 / 0.10 |
| sf | 27 | 0.333 ... 2.189 | 0.205 ... 2.325 | 0.177 ... 2.356 | 0.34 / 0.12 / 0.09 |
| sf | 125 | 0.365 ... 2.168 | 0.301 ... 2.264 | 0.290 ... 2.284 | 0.30 / 0.21 / 0.17 |
| fs | -40 | 0.593 ... 1.928 | 0.187 ... 2.336 | 0.106 ... 2.424 | 0.88 / 0.18 / 0.10 |
| fs | 27 | 0.497 ... 2.021 | 0.220 ... 2.307 | 0.175 ... 2.357 | 0.59 / 0.13 / 0.09 |
| fs | 125 | 0.391 ... 2.139 | 0.305 ... 2.262 | 0.292 ... 2.286 | 0.55 / 0.37 / 0.33 |

(schematic, pad-voltage span [V] with |error from small-signal line| < 10 mV; PEX in `tables/d2s.md`.)

## 3. Round trip S2D → slot 7 (default mode) → D2S

Conditions: the designer's tier-1 slot deck (design 9052bd35, `run_tier1.py`, imported): slot_7 default mode, replica
bias `pad_ref_rb` and `bias_dist_pd` KLayout-extracted, `bg_core_pd` schematic, iref from the slot's bandgap, pad out
unloaded (1 GΩ); **vref / vcm are the replica values as simulated** (not set by sources). Pad in swept −0.3 … 3.3 V in
5 mV steps; the two custom pads in three views (both pads the same view): schematic, magic PEX, and the KLayout-extracted
netlists that the designer's deck uses. PVT: the designer's five tier-1 points. 15 runs: 14 complete, 1 partial (PEX,
sf −40 °C 3.0 V: ngspice aborted the sweep at pad in 1.435 V, "timestep too small" at the S2D pad's diode
`d.x2s.x43.d1`; data up to 1.43 V are used, which covers the linear range there).

| pads | PVT | replica vref / vcm [V] | max \|err\| pad in 0 … 1 V [mV] | pad in range, 1 mV [V] | pad out range, 1 mV [V] |
|---|---|---|---|---|---|
| schematic | tt 27 °C 3.3 V | 0.4923 / 1.2566 | 0.86 | -0.171 … 1.281 | 0.595 … 2.044 |
| schematic | ss −40 °C 3.0 V | 0.4475 / 1.1148 | 1.33 | -0.243 … 1.055 | 0.427 … 1.721 |
| schematic | ff 125 °C 3.6 V | 0.5709 / 1.2991 | 6.10 | 0.096 … 1.367 | 0.828 … 2.095 |
| schematic | fs 125 °C 3.6 V | 0.5757 / 1.3655 | 3.10 | 0.028 … 1.440 | 0.821 … 2.229 |
| schematic | sf −40 °C 3.0 V | 0.4441 / 1.1377 | 1.10 | -0.247 … 1.114 | 0.449 … 1.806 |

err = pad out − (vcm + pad in − vref) with the replica's vcm / vref (the `run_tier1.py` definition); range = contiguous
around pad in = vref with |error from the small-signal line| < 1 mV (round-trip gain 1, so input- and output-referred
are the same). All views and the 10 mV ranges: `tables/rt.md`.

- Round-trip gain 0.99848 … 0.99882; the error inside the range is mostly this gain error (−0.12 … −0.15 %) plus, at
  125 °C, an offset of 1.1 … 2.4 mV (pad out − vcm at pad in = vref), which is why ff / fs 125 °C have the largest
  max |err| (6.10 / 3.10 mV, schematic pads).
- Above the range pad out saturates at about 2.25 V (tt 27 °C, `rt_transfer_tt27`), i.e. the S2D → D2S chain limits
  at pad in ≈ 1.4 … 1.5 V.
- Views: magic PEX = schematic within 0.3 mV (range ends) and 0.01 mV (max |err|). The KLayout-extracted pads (the
  designer's tier-1 view) give the same error inside the range (+0.03 … +0.38 mV) but range ends that differ by up to
  55 mV (high end lower by 7.7 … 55.2 mV, low end up to 32.9 mV higher at −40 °C); the reason was not investigated here.
  **Update 2026-11-25** ([../klayout_pad_diodes](../klayout_pad_diodes/README.md) item 5): not the undersized pad
  diodes (fixing them changes no node by more than 2 nV); the S2D output common mode of the KLayout-extracted netlist is
  33 mV lower than schematic / PEX at tt 27 °C. Cause still not found.
- Cross-check: with the KLayout-extracted pads, max |err| over pad in 0 … 1 V = 0.90 / 1.37 / 6.48 / 3.37 / 1.13 mV at
  tt / ss / ff / fs / sf; the designer's `results.txt` (same deck, 50 mV steps) has 0.90 / 1.31 / 6.49 / 3.37 / 1.11 mV.

## 4. S2D input range vs vref and vcm

Conditions: as section 1 (schematic), vref 0.5 / 0.8 / 1.2 / 1.65 V × vcm 1.0 / 1.2 / 1.4 / 1.65 V (the CACE
`range_params` grid) × iovdd 3.0 / 3.3 V × ss / tt / ff × −40 / 27 / 125 °C = 288 runs, 288 / 288 complete
(`range_params` itself: 3.0 V, −40 / 125 °C). Entry = the pad range met at all nine corner / temperature runs (highest
low end … lowest high end), 1 mV criterion; figure `s2d_vrefvcm_range` (also tt 27 °C ends).

iovdd 3.0 V:

| vref \ vcm | 1.00 V | 1.20 V | 1.40 V | 1.65 V |
|---|---|---|---|---|
| 0.50 V | 0.104 … 0.951 | 0.086 … 1.057 | 0.171 … 0.837 | 0.371 … 0.630 |
| 0.80 V | 0.365 … 1.246 | 0.264 … 1.360 | 0.470 … 1.138 | 0.671 … 0.930 |
| 1.20 V | 0.764 … 1.647 | 0.672 … 1.756 | 0.872 … 1.546 | 1.071 … 1.331 |
| 1.65 V | 1.573 … 1.743 | 1.573 … 1.743 | 1.573 … 1.743 | 1.563 … 1.737 |

iovdd 3.3 V:

| vref \ vcm | 1.00 V | 1.20 V | 1.40 V | 1.65 V |
|---|---|---|---|---|
| 0.50 V | 0.105 … 0.950 | 0.086 … 1.154 | 0.086 … 1.172 | 0.120 … 0.889 |
| 0.80 V | 0.365 … 1.246 | 0.179 … 1.445 | 0.154 … 1.473 | 0.419 … 1.189 |
| 1.20 V | 0.763 … 1.643 | 0.570 … 1.837 | 0.556 … 1.885 | 0.819 … 1.592 |
| 1.65 V | 1.218 … 2.000 | 1.031 … 1.999 | 1.041 … 2.000 | 1.277 … 2.041 |

- vcm 1.2 … 1.4 V gives the widest range at both supplies; vcm 1.0 V cuts the high end (about vref + 0.45 V), vcm
  1.65 V cuts both ends, most at iovdd 3.0 V (vref 0.5 V: 0.371 … 0.630 V).
- At 3.3 V with vcm 1.2 … 1.4 V the high end follows vref (vref + 0.64 … 0.69 V) up to vref 1.2 V; at vref 1.65 V it
  stops at about 2.0 V. At 3.0 V, vref 1.65 V leaves only 1.57 … 1.74 V.
- Cross-check with the committed `range_params` (96 runs): gain within 0.00006, INL (u = ±0.5 V) within 0.038 mV
  (`tables/crosscheck.md`).
