<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
### Slot 7 modes from power-up: max |D2S pad out - expected| [mV]

IHP sg13cmos5l simulation; bg_core_pd schematic, both pads / pad_ref_rb / bias_dist_pd extracted, ls_up_fs / s7_ctrl source. Pad in 0 / 0.25 / 0.5 / 0.75 / 1.0 V (feed modes: 0.5 V). `FAILED` = simulator gave no result; empty = not run in the time box.

| MOS | T [C] | V | default | swap | mon | feed | ext | all_high | swap+feed | no_key_swap | vcm / vref [V] | bandgap g [V] | t(g 90 %) after enable [us] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ss | -40 | 3.0 | 1.37 |  |  |  |  |  |  |  | 1.115 / 0.447 | 1.773 | 0.81 ... 0.81 |

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

