<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Results: slot 7 modes at ss / −40 °C, mode table, bg_core_pd alone

IHP sg13cmos5l simulation, ngspice-47. Views: in the slot decks `bg_core_pd` **schematic**, both custom pads,
`pad_ref_rb`, `bias_dist_pd` **extracted** (layout netlists), `ls_up_fs` / `s7_ctrl` / `hv_logic` / `en_ctrl_3v3`
source; `bg_core_pd` alone: **schematic** and **extracted** (magic PEX R + C). Design repository commit `9052bd3`,
slot commit `158afc5`. Method and limits: `README.md`.

## 1. ss / −40 °C mode failures: simulator artifact, not a second state of the bandgap

**Verdict: simulator (DC solver / time-step) artifact.** In every run where the circuit was simulated from power-up,
the bandgap started and the slot settled to the expected output; no zero-current (second) state of `bg_core_pd` was
found by any method. Evidence:

1. **Reproduced.** The designer's `run_modes.py`, unchanged, at ss −40 °C 3.0 V: default and all_high pass (1.31 mV),
   swap, mon, feed, ext, swap+feed `FAILED` (`designer_modes_rerun_ss.txt`), as in the design repository.
2. **Where the solver fails.** ngspice's stderr for the same DC deck (`slot_modes_dc_diag.csv`): gmin stepping, source
   stepping and the "transient op" fallback all fail, the last with *timestep too small, trouble with
   dparea-instance* **`d.x2d.xlay.x$3.d1`** (swap; the D2S pad's antenna diode `dpantenna` pad → iovdd) or
   **`d.x2s.xlay.x$63.d1`** (feed, ext, swap+feed; the S2D pad's). Not a bandgap node.
3. **`.nodeset` of the bandgap at its running point does not cure it** (diagnosis only): mon then converges
   (1.37 mV, g = 1.7726 V), swap / feed / ext / swap+feed still fail at the same pad diodes. A DC failure caused by the
   bandgap sitting in a wrong state would be cured by placing it in the right one.
4. **Power-up transient from 0 V, all 8 modes at ss −40 °C 3.0 V** (supplies 0 → 3.0 V in 10 µs, mode bits set,
   enable at 20 µs; pad out 1 GΩ ∥ 10 pF): the bandgap's `g` node reaches 90 % **0.80 … 0.83 µs after enable** in
   every mode, vcm reaches 98 % 1.6 µs after enable (ext: vcm follows its external source, switched on at 25 … 26 µs); settled values
   g = 1.7726 V, ibg node 0.995 V, vcm 1.1148 V, vref 0.4475 V, I(vdd_3v3) 48.38 … 48.59 µA — the same as the
   designer's DC at ss −40 °C (vcm 1.115, vref 0.447 V, 48.38 µA). Max |pad out − expected| over pad in 0 … 1 V:
   default / all_high / no_key_swap 1.37, swap 1.12, mon 1.43, feed 0.24, swap+feed 0.24, ext 4.92 mV (ext: against
   the source values 1.30 / 0.50 V through 10 kΩ). Plot: `slot_powerup_ss_m40.png`. With 1 GΩ only (as the designer)
   default / swap / mon / feed / ext / all_high / no_key_swap also start and settle (same errors; ext there with
   its sources on from t = 0); one swap+feed run aborted
   during the supply ramp (6.6 µs, before enable) at the D2S antenna diode (section 2).
5. **The aborts that remain are at edges, at the same pad diodes or a 0 V branch, and before or at enable:**
   1 GΩ only: 5.9 / 6.6 / 21.3 µs at `x2d … x$3` depending on options; with 10 pF, sf −40 °C mon at 20.07 µs (the
   enable edge, `x2d … x$3`), feed and swap+feed at 3.95 µs (supply ramp, `v.xs.vsb3#branch`), the bandgap not yet
   enabled in either case. Retried with a 1 µs enable edge and a 5 ns maximum step (column "retry").
6. **bg_core_pd alone** (schematic and extracted, all five MOS corners, −40 °C / 3.0 V and 125 °C / 3.6 V):
   `.op` started from a `.nodeset` at the zero-current state (g = 0, vpg = vpc = ks = vdd) converges to the running
   state (same current as the plain `.op`); a transient with the supply up and `.ic` at the zero-current state
   recovers within 0.02 µs (extracted ss −40 °C: 0.51 µs); 1 µs supply ramps reach 90 % of the final current
   1.4 … 2.4 µs after t = 0 and 1 ms ramps follow the supply with no hang (`bg_core_ramp.png`). The start-up
   transistor MS3 is off once running (ks ≈ 0 V in the slot at ss −40 °C).

## 2. Mode table (power-up transient, pad out 1 GΩ ∥ 10 pF)

Full table below. Summary of what finished in the time box (max |pad out − expected| over pad in 0 … 1 V):

| PVT | passed (error [mV]) | aborted by the simulator (time of abort) |
|---|---|---|
| ss −40 °C 3.0 V | all 8: default 1.37, swap 1.12, mon 1.43, feed 0.24, ext 4.92, all_high 1.37, swap+feed 0.24, no_key_swap 1.37 | — |
| sf −40 °C 3.0 V | default 1.13, swap 1.04, ext 1.67, all_high 1.13, no_key_swap 1.13 | mon (20.07 µs, enable edge), feed, swap+feed (3.95 µs, supply ramp); retries abort at 3.95 µs |
| ff −40 °C 3.0 V | swap 0.99, mon 1.18 | feed (6.13 µs, supply ramp) |
| tt −40 °C 3.0 V | — | swap, mon, feed (2.94 µs, supply ramp, at the 0 V sources `Vsb2` / `Vsb3` that tie vcm / vref to bus2 / bus3) |
| ss 125 °C 3.6 V | — | swap: no result after 17 min, stopped (time box) |

Every abort is before the bandgap is enabled (supply ramp) or at the enable edge, so these runs say nothing about the
bandgap's start-up either way; in every run that got past the enable edge the bandgap started within 0.73 … 0.86 µs
and the output settled. **Not run here (TBD):** the rest of `jobs_modes.txt` (all 5 corners × −40 / 125 °C × 3.0 /
3.6 V × 8 modes; tt 27 °C; fs / ff 125 °C); the designer's DC runs cover tt 27 °C and ff 125 °C for all 8 modes
(pass). The 1 GΩ-only table is exploratory (runs made while the method was being set up; one pu0 swap+feed ss −40 °C
run aborted at 6.6 µs, a later one completed with 0.24 mV, and the later deck was not kept, so whether the two decks
were identical is not known).

## 3. bg_core_pd alone

iout into 0.7 V, `.op` (equal to the end of a 200 µs power-up transient within 0.00 %):

| view | points | min | typ (tt, res_typ, 27 °C, 3.3 V) | max |
|---|---|---|---|---|
| schematic, rhigh res_typ / bcs / wcs | 135 | 3.829 µA (ss, res_wcs, 125 °C, 3.0 V) | 4.958 µA | 6.369 µA (ff, res_bcs, 27 °C, 3.6 V) |
| schematic, res_typ only | 45 | 4.855 µA | 4.958 µA | 4.969 µA |
| extracted (PEX R, DC-equivalent), res_typ | 45 | 4.854 µA (ss, −40 °C, 3.0 V) | 4.958 µA | 4.969 µA (ff, 27 °C, 3.6 V) |

- Supply sensitivity (I(3.6 V) − I(3.0 V)) / 0.6 V / I(3.3 V): median 0.54 %/V, largest 0.73 %/V (schematic, all
  corners); extracted 0.54 / 0.66 %/V.
- Over −40 … 125 °C: (max − min) / I(27 °C) 1.7 … 2.1 % (the current peaks near 27 °C).
- MOS corners move it by ≤ 0.31 % at any rhigh corner, T and V; the rhigh corner sets it (res_wcs −21 %, res_bcs +28 % at 27 °C, from the table),
  as the block README says (about −20 % / +30 %).
- Extracted vs schematic (res_typ): equal to within 0.001 µA at every point.

## Failures / TBD

- Slot transients abort with "timestep too small" at the pads' antenna diodes (or `v.xs.vsb3#branch`) in some runs;
  aborted runs are listed as `FAILED` and, where retried, with the retry result. A solver issue of the extracted pad
  netlists in ngspice; not investigated further. The converted pad netlists call `dpantenna` with `a=` / `p=`, which
  the PDK subckt does not take (it takes `l` / `w`; defaults 0.78 × 0.78 µm), so these diodes are simulated at the
  default size: a netlist-conversion detail of the designer's `run_starve.convert()`, unchanged here (TBD for the
  designer). **Checked 2026-11-25** in [../klayout_pad_diodes](../klayout_pad_diodes/README.md): the size bug is
  confirmed and located, but fixing it does **not** cure the ss / sf −40 °C aborts listed here; they remain open.
- ngspice's `.op` of the full bg_core_pd PEX (with capacitors) is wrong at ss −40 °C (6.92 µA pex_3, 8.29 µA pex_2:
  "transient op" ends with capacitor currents flowing); the DC table uses the PEX without capacitors.
- Mode table: PVT points not reached in the time box, and the cold-corner runs that aborted before enable (section 2).
  A fix to try: slower supply ramp, or the vcm / vref bus nodes and the pad out with their board capacitance; not
  tried. No rhigh corners in the slot runs.

## Generated tables

### Slot 7 modes from power-up, pad out 1 Gohm || 10 pF: max |D2S pad out - expected| [mV]

IHP sg13cmos5l simulation; bg_core_pd schematic, both pads / pad_ref_rb / bias_dist_pd extracted, ls_up_fs / s7_ctrl source. Pad in 0 / 0.25 / 0.5 / 0.75 / 1.0 V (feed modes: 0.5 V). `FAILED @t` = the transient aborted at t ("timestep too small"; enable is at 20 us, so t < 20 us is during the supply ramp, before the bandgap is enabled); `retry` = the same run with a 1 us enable edge and a 5 ns maximum step (variant pu2); empty = not run in the time box.

| MOS | T [C] | V | default | swap | mon | feed | ext | all_high | swap+feed | no_key_swap | vcm / vref [V] | bandgap g [V] | t(g 90 %) after enable [us] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ff | -40 | 3.0 |  | 0.99 | 1.18 | FAILED @6.13 us |  |  |  |  | 1.136 / 0.432 | 1.665 | 0.73 ... 0.74 |
| sf | -40 | 3.0 | 1.13 | 1.04 | FAILED @20.07 us; retry FAILED @3.95 us | FAILED @3.95 us; retry FAILED @3.95 us | 1.67 | 1.13 | FAILED @3.95 us; retry FAILED @3.95 us | 1.13 | 1.138 / 0.444 | 1.746 | 0.79 ... 0.79 |
| ss | -40 | 3.0 | 1.37 | 1.12 | 1.43 | 0.24 | 4.92 | 1.37 | 0.24 | 1.37 | 1.115 / 0.447 | 1.773 | 0.80 ... 0.83 |
| tt | -40 | 3.0 |  | FAILED @2.94 us | FAILED @2.94 us | FAILED @2.94 us |  |  |  |  |  |  |  |

### Slot 7 modes from power-up, pad out 1 Gohm only (as run_modes.py): max |D2S pad out - expected| [mV]

IHP sg13cmos5l simulation; bg_core_pd schematic, both pads / pad_ref_rb / bias_dist_pd extracted, ls_up_fs / s7_ctrl source. Pad in 0 / 0.25 / 0.5 / 0.75 / 1.0 V (feed modes: 0.5 V). `FAILED @t` = the transient aborted at t ("timestep too small"; enable is at 20 us, so t < 20 us is during the supply ramp, before the bandgap is enabled); `retry` = the same run with a 1 us enable edge and a 5 ns maximum step (variant pu2); empty = not run in the time box.

| MOS | T [C] | V | default | swap | mon | feed | ext | all_high | swap+feed | no_key_swap | vcm / vref [V] | bandgap g [V] | t(g 90 %) after enable [us] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sf | -40 | 3.0 | 1.13 | FAILED | FAILED | FAILED |  |  |  |  | 1.138 / 0.444 | 1.746 | 0.79 ... 0.79 |
| ss | -40 | 3.0 | 1.37 | 1.12 | 1.43 | 0.24 | 4.92 | 1.37 | 0.24 | 1.37 | 1.115 / 0.447 | 1.773 | 0.80 ... 0.86 |

### DC solver diagnosis at ss / -40 C / 3.0 V (designer's DC deck)

| mode | variant | max error [mV] | ngspice (first failing instance, if any) |
|---|---|---|---|
| swap | dcop | FAILED | Timestep too small;  vin = 0: trouble with dparea-instance d.x2d.xlay.x$3.d1 |
| swap | dcns | FAILED | Timestep too small;  vin = 0: trouble with dparea-instance d.x2d.xlay.x$3.d1 |
| mon | dcns | 1.37 |  |
| feed | dcns | FAILED | Timestep too small; trouble with dparea-instance d.x2s.xlay.x$63.d1 |
| ext | dcns | FAILED | Timestep too small;  vin = 0: trouble with dparea-instance d.x2s.xlay.x$63.d1 |
| swap+feed | dcns | FAILED | Timestep too small; trouble with dparea-instance d.x2s.xlay.x$63.d1 |

### bg_core_pd alone: iout into 0.7 V [uA] (.op; cross-checked against the end of a 200 us power-up transient)

**schematic** (135 points): min 3.829 (ss res_wcs 125 C 3.0 V), typ 4.9578 (tt res_typ 27 C 3.3 V), max 6.369 (ff res_bcs 27 C 3.6 V).
res_typ only: 4.855 ... 4.969 uA.
|.op - transient end| max 0.00 %; |value at 100 us - at 199 us| max 0.00 %.
Supply sensitivity (I(3.6) - I(3.0)) / 0.6 V / I(3.3): median 0.539 %/V, largest 0.732 %/V (ss res_bcs -40 C).
Spread over -40 ... 125 C (max - min) / I(27 C): 1.74 ... 2.13 %.

schematic, 3.3 V: rows MOS x rhigh corner, columns T

| MOS | res | -40 C | 27 C | 125 C |
|---|---|---|---|---|
| tt | res_typ | 4.8714 | 4.9578 | 4.8829 |
| tt | res_bcs | 6.2247 | 6.3536 | 6.2974 |
| tt | res_wcs | 3.8652 | 3.9228 | 3.8398 |
| ss | res_typ | 4.8663 | 4.9529 | 4.8776 |
| ss | res_bcs | 6.2178 | 6.3469 | 6.2902 |
| ss | res_wcs | 3.8613 | 3.9192 | 3.8358 |
| ff | res_typ | 4.8761 | 4.9625 | 4.8881 |
| ff | res_bcs | 6.2311 | 6.3599 | 6.3045 |
| ff | res_wcs | 3.8687 | 3.9264 | 3.8437 |
| sf | res_typ | 4.8725 | 4.9588 | 4.8836 |
| sf | res_bcs | 6.2263 | 6.3548 | 6.2984 |
| sf | res_wcs | 3.866 | 3.9235 | 3.8404 |
| fs | res_typ | 4.8702 | 4.9569 | 4.8822 |
| fs | res_bcs | 6.223 | 6.3522 | 6.2965 |
| fs | res_wcs | 3.8643 | 3.9222 | 3.8393 |

**extracted** (45 points): min 4.854 (ss res_typ -40 C 3.0 V), typ 4.9575 (tt res_typ 27 C 3.3 V), max 4.969 (ff res_typ 27 C 3.6 V).
res_typ only: 4.854 ... 4.969 uA.
|.op - transient end| max 0.00 %; |value at 100 us - at 199 us| max 0.00 %.
Supply sensitivity (I(3.6) - I(3.0)) / 0.6 V / I(3.3): median 0.539 %/V, largest 0.664 %/V (ss res_typ -40 C).
Spread over -40 ... 125 C (max - min) / I(27 C): 1.74 ... 1.80 %.

extracted, 3.3 V: rows MOS x rhigh corner, columns T

| MOS | res | -40 C | 27 C | 125 C |
|---|---|---|---|---|
| tt | res_typ | 4.8711 | 4.9575 | 4.8826 |
| ss | res_typ | 4.866 | 4.9526 | 4.8772 |
| ff | res_typ | 4.8758 | 4.9623 | 4.8877 |
| sf | res_typ | 4.8722 | 4.9585 | 4.8833 |
| fs | res_typ | 4.8699 | 4.9566 | 4.8818 |

### bg_core_pd start-up by supply ramp (vdd = en_3v3 0 -> V; iout into 0.7 V)

| view | MOS | T [C] | V | ramp | t(90 % of final) [us] | I 20 us after ramp end [uA] | I at end [uA] |
|---|---|---|---|---|---|---|---|
| schematic | tt | -40 | 3.0 | 1u | 1.552 | 4.862 | 4.862 |
| schematic | tt | -40 | 3.0 | 1m | 836.96 | 4.862 | 4.862 |
| schematic | tt | 125 | 3.6 | 1u | 1.417 | 4.8906 | 4.8906 |
| schematic | tt | 125 | 3.6 | 1m | 502.467 | 4.8906 | 4.8906 |
| schematic | ss | -40 | 3.0 | 1u | 1.607 | 4.8548 | 4.8548 |
| schematic | ss | -40 | 3.0 | 1m | 882.473 | 4.8548 | 4.8548 |
| schematic | ss | 125 | 3.6 | 1u | 1.395 | 4.8854 | 4.8854 |
| schematic | ss | 125 | 3.6 | 1m | 539.038 | 4.8854 | 4.8854 |
| schematic | ff | -40 | 3.0 | 1u | 1.628 | 4.868 | 4.868 |
| schematic | ff | -40 | 3.0 | 1m | 791.742 | 4.868 | 4.868 |
| schematic | ff | 125 | 3.6 | 1u | 1.441 | 4.8958 | 4.8958 |
| schematic | ff | 125 | 3.6 | 1m | 466.179 | 4.8958 | 4.8958 |
| schematic | sf | -40 | 3.0 | 1u | 1.572 | 4.8638 | 4.8638 |
| schematic | sf | -40 | 3.0 | 1m | 814.528 | 4.8638 | 4.8638 |
| schematic | sf | 125 | 3.6 | 1u | 1.433 | 4.8913 | 4.8913 |
| schematic | sf | 125 | 3.6 | 1m | 484.611 | 4.8913 | 4.8913 |
| schematic | fs | -40 | 3.0 | 1u | 1.575 | 4.8599 | 4.8599 |
| schematic | fs | -40 | 3.0 | 1m | 859.389 | 4.8599 | 4.8599 |
| schematic | fs | 125 | 3.6 | 1u | 1.406 | 4.8899 | 4.8899 |
| schematic | fs | 125 | 3.6 | 1m | 520.345 | 4.8899 | 4.8899 |
| extracted | ss | -40 | 3.0 | 1u | 2.361 | 4.8545 | 4.8545 |
| extracted | ss | -40 | 3.0 | 1m | 882.453 | 4.8545 | 4.8545 |
| extracted | ss | 125 | 3.6 | 1u | 1.655 | 4.8851 | 4.8851 |
| extracted | ss | 125 | 3.6 | 1m | 539.023 | 4.8851 | 4.8851 |
| extracted | ff | -40 | 3.0 | 1u | 2.112 | 4.8677 | 4.8677 |
| extracted | ff | -40 | 3.0 | 1m | 791.722 | 4.8677 | 4.8677 |
| extracted | ff | 125 | 3.6 | 1u | 1.881 | 4.8955 | 4.8955 |
| extracted | ff | 125 | 3.6 | 1m | 466.164 | 4.8955 | 4.8955 |

### bg_core_pd: is there a zero-current state? (diagnosis)

| view | MOS | T [C] | V | .op from .nodeset at zero current: I [uA], g [V] | transient from .ic at zero current, supply up: I at 49 us [uA], t(90 %) [us] |
|---|---|---|---|---|---|
| schematic | tt | -40 | 3.0 | 4.862, 1.7197 | 4.862, 0.013 |
| schematic | tt | 125 | 3.6 | 4.8906, 1.2463 | 4.8906, 0.014 |
| schematic | ss | -40 | 3.0 | 4.8548, 1.7726 | 4.8548, 0.015 |
| schematic | ss | 125 | 3.6 | 4.8854, 1.2959 | 4.8854, 0.017 |
| schematic | ff | -40 | 3.0 | 4.868, 1.6646 | 4.868, 0.011 |
| schematic | ff | 125 | 3.6 | 4.8958, 1.1944 | 4.8958, 0.011 |
| schematic | sf | -40 | 3.0 | 4.8638, 1.7464 | 4.8638, 0.013 |
| schematic | sf | 125 | 3.6 | 4.8913, 1.2712 | 4.8913, 0.014 |
| schematic | fs | -40 | 3.0 | 4.8599, 1.6919 | 4.8599, 0.013 |
| schematic | fs | 125 | 3.6 | 4.8899, 1.2201 | 4.8899, 0.014 |
| extracted | ss | -40 | 3.0 | 4.8545, 1.7726 | 4.8545, 0.511 |
| extracted | ss | 125 | 3.6 | 4.8851, 1.2959 | 4.8851, 0.019 |
| extracted | ff | -40 | 3.0 | 4.8677, 1.6646 | 4.8677, 0.012 |
| extracted | ff | 125 | 3.6 | 4.8955, 1.1944 | 4.8955, 0.013 |

