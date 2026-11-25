<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 test platforms (stage A and stage B): what was built and what the simulations gave

Back to [README.md](README.md). **These platforms are not in the taped-out slot.** They are the earlier contents of `slot_7.gds`, built in the cloud session C5 on
2026-11-06/07 to measure the two bias references on the chip, and replaced on 2026-11-08 by the slot circuit for the custom pads. They matter because (1) the
reference cores, the transmission gates, the fail-safe enable idea and the measurement procedure carried into the taped-out design, (2) the bandgap core `bg_core_pd` of the taped-out
slot is the one measured here (same macro; the taped-out `slot_7.gds` was **not** XOR-compared with the platform's cell on 2026-11-22), and (3) the tip of `tapeout_nov_2026`
still points its slot 7 submodule at stage B ([README.md](README.md) section 1). All numbers below are simulation results read from committed files of the design repository
at commit `efb80141` (branch `claude/c5-slot7-testplatform`); nothing was re-run, and no silicon measurement exists.

## 1. Which platform is which

| platform | what is on the slot | where it lives | state |
|---|---|---|---|
| **stage A** | `oa_core_pd` and `bg_core_pd` (cores, ~5 µA sourced each), a hv transmission gate `xgate` per core onto `analog_bus0` (OA) / `analog_bus1` (BG), four fail-safe enables `tp_en_ctrl` (`dig_in[0..3]`), read-back on `dig_out[3:0]`, `dig_out[11:4]` held low | design repository branch `claude/c5-slot7-testplatform` (macro `macros/slot7_testplatform/`, records `docs/slot7_testplatform/`); delivery repository `sg13cmos5l_cm_slot7` `main` from 2026-11-06 (`f2c8501`), kept as branch `claude/slot7-stage-a` | delivered, checked through the harness flow on the fork; superseded 2026-11-08 |
| **stage B** | stage A plus the bias tree `bias_tree_noab_pd` (the S2D pad's tree) with its reference selectable from the OA core, the BG core or the harness `ibias0` (`dig_in[4..6]`, tree enable `dig_in[7]`); the four bias voltages `vbp vbn vbpc vbnc` onto `analog_bus2` (`dig_in[8..11]`); the harness `ibias1` onto `analog_bus3` (`dig_in[12]`); 9 more fail-safe enables `tp_en_ctrl_b` and 8 more transmission gates; everything at x < 285 µm | the same branches; delivery repository `main` at `c072679` (README and PROGRESS dated 2026-11-06) | built, DRC / LVS clean, harness flow exit 0 on the fork; **this is the commit the tapeout branch tip points at**, but not what was taped out |

Platform size: stage A occupies x < 143 µm, y < 197 µm of the 537 × 273 µm slot; stage B x < 285 µm. Frame, pin names and the 13 custom-pad pins with their stand-in
stubs are unchanged from the earlier `slot_7.gds` (the platform needs no custom pad; fallback to foundry pads is documented in SUMMARY.md).

## 2. Stage A

### 2.1 Circuit and control

- Each core's output current is sourced through its `xgate` onto a harness bus; an SMU on chip pin `analog[0]` / `analog[1]` measures it through the harness's per-slot bus switch.
- `tp_en_ctrl` (43 hv devices): `en_k = dig_in[k] AND enable AND (slot vdd_1v2 present)`, a ratioed design (weak hv PMOS against an hv NMOS stack, no latch, no 1.2 V supply needed
  to read). Pins: `dig_in[0]` OA core, `dig_in[1]` BG core, `dig_in[2]` OA → bus0, `dig_in[3]` BG → bus1; unused: `dig_in[23:4]`, `clk`, `reset`, `ibias0/1`, `vbias`, `analog_bus2/3`, the `s7_an[*]` pins.
- **Design change on the way:** with the harness `analog_switch_small` as bus switch, its `antennanp` diode let the harness charge a gated-off `vdd_1v2` from `dig_in`, and the cores turned on at ff / fs 125 °C.
  It was replaced by `xgate` plus two more fail-safe channels.

### 2.2 Measurement procedure (SPI register writes; from `docs/slot7_testplatform/PLAN.md` §5)

1. `0x50 = 0x07` (select slot 7; `0x51` = 0 keeps everything off). 2. `0x20..0x37 = 0x0D` (route all 24 `dig_in` to constant 0: the reset value 0x0 follows pad `io[0]`).
3. `0x51 = 0x06` (3.3 V and 1.2 V gates), then `0x0E` (`dig_ena`), then `0x0F` (`enable`).
4. OA: `0x22 = 0x0E` (TG0), `0x51 = 0x1F` (bus-0 switch); SMU on `analog[0]` at 0.7 V (sweep 0 … 2 V for compliance); read `I_leak` with the core off; `0x20 = 0x0E`; read `I_on`; `I_OA = I_on − I_leak`; read-back `0x38` bits 2, 0 = 1.
   BG: the same with `0x23`, `0x21`, `0x51` bit 5, `analog[1]`, bits 3, 1.
5. Fail-safe: `0x51` bit 2 (1.2 V) or bit 0 (`enable`) to 0 returns the current to `I_leak`. Repeat at −40 / 27 / 125 °C (the subtraction is needed at every point because `I_leak` grows with temperature).
6. Before gating `vdd_3v3` off: bus switches open, SMU at 0 V (a voltage on the bus drives the TG PMOS into the floating `vdd_3v3`: up to 87 nA at 0.7 V, `vdd_3v3` floats at 0.5 … 0.67 V).

### 2.3 Simulation results, schematic netlist (ngspice; 5 process corners × −40 / 27 / 125 °C × supplies 3.0 / 1.08, 3.3 / 1.2, 3.6 / 1.32 V)

Output currents at the bus (0.7 V), per corner, at low / nominal / high supply; `logic-level failures` over all points: 0.

| corner | T (C) | I_OA (uA) low / nom / high supply | I_BG (uA) low / nom / high |
|---|---|---|---|
| tt | -40 | 3.253 / 3.255 / 3.257 | 4.862 / 4.871 / 4.878 |
| tt | 27 | 4.990 / 4.992 / 4.994 | 4.950 / 4.958 / 4.965 |
| tt | 125 | 6.659 / 6.661 / 6.663 | 4.875 / 4.883 / 4.891 |
| ss | -40 | 3.043 / 3.045 / 3.046 | 3.853 / 3.861 / 3.867 |
| ss | 27 | 4.699 / 4.701 / 4.703 | 3.912 / 3.919 / 3.925 |
| ss | 125 | 6.315 / 6.317 / 6.318 | 3.829 / 3.836 / 3.842 |
| ff | -40 | 3.494 / 3.496 / 3.498 | 6.220 / 6.231 / 6.240 |
| ff | 27 | 5.321 / 5.323 / 5.326 | 6.350 / 6.360 / 6.369 |
| ff | 125 | 7.051 / 7.053 / 7.055 | 6.294 / 6.304 / 6.315 |
| sf | -40 | 3.146 / 3.148 / 3.150 | 4.864 / 4.873 / 4.879 |
| sf | 27 | 4.843 / 4.845 / 4.846 | 4.951 / 4.959 / 4.965 |
| sf | 125 | 6.482 / 6.484 / 6.485 | 4.876 / 4.884 / 4.891 |
| fs | -40 | 3.370 / 3.372 / 3.373 | 4.860 / 4.870 / 4.878 |
| fs | 27 | 5.151 / 5.153 / 5.156 | 4.948 / 4.957 / 4.964 |
| fs | 125 | 6.855 / 6.857 / 6.859 | 4.874 / 4.882 / 4.890 |

Headline (SUMMARY.md): OA 3.04 … 7.05 µA over everything (tt: 3.26 / 4.99 / 6.66 at −40 / 27 / 125 °C, i.e. proportional to absolute temperature); BG 3.83 … 6.37 µA (tt: 4.87 / 4.96 / 4.88, flat over temperature); supply dependence 3.0 → 3.6 V at most 0.11 % (OA) and 0.37 % (BG);
compliance (change over bus 0 … 2.0 V / at 2.5 V): < 0.002 % / −0.08 % (OA), 0.014 % / −0.03 % (BG); enable to 1 % in 0.38 … 0.69 µs (OA) and 0.43 … 0.93 µs (BG), disable 71 … 100 ns.

Static states (bus current min … max over all corners, temperatures and supplies; 495 points, all with the expected read-back):

| state | I(bus0) min .. max | I(bus1) min .. max | en_oa / en_bg / read-back as expected | worst point |
|---|---|---|---|---|
| all_off (dig_in 0000, en 1, 3v3 1, 1v2 1) | 1.6e-12 .. 8.31e-11 A | 1.6e-12 .. 1.7e-10 A | yes | ff 125 C high |
| tg_on_cores_off (dig_in 0011, en 1, 3v3 1, 1v2 1) | 5.73e-12 .. 2.44e-10 A | 5.67e-12 .. 2.24e-09 A | yes | ff 125 C high |
| oa_on (dig_in 1010, en 1, 3v3 1, 1v2 1) | 3.04e-06 .. 7.05e-06 A | 1.6e-12 .. 1.7e-10 A | yes | ff 125 C high |
| bg_on (dig_in 0101, en 1, 3v3 1, 1v2 1) | 1.6e-12 .. 8.31e-11 A | 3.83e-06 .. 6.37e-06 A | yes | ff 27 C high |
| both_on (dig_in 1111, en 1, 3v3 1, 1v2 1) | 3.04e-06 .. 7.05e-06 A | 3.83e-06 .. 6.37e-06 A | yes | ff 125 C high |
| cores_on_tg_off (dig_in 1100, en 1, 3v3 1, 1v2 1) | 1.6e-12 .. 1.9e-10 A | 1.6e-12 .. 1.9e-10 A | yes | ff 125 C high |
| enable_low (dig_in 1111, en 0, 3v3 1, 1v2 1) | 1.6e-12 .. 8.31e-11 A | 1.6e-12 .. 1.7e-10 A | yes | ff 125 C high |
| vdd1v2_off (dig_in 1111, en 1, 3v3 1, 1v2 0) | 1.6e-12 .. 8.31e-11 A | 1.6e-12 .. 1.7e-10 A | yes | ff 125 C high |
| vdd1v2_off_1uA (dig_in 1111, en 1, 3v3 1, 1v2 0) | 1.6e-12 .. 8.31e-11 A | 1.6e-12 .. 1.7e-10 A | yes | ff 125 C high |
| vdd3v3_off (dig_in 1111, en 1, 3v3 0, 1v2 1) | -1.07e-08 .. -2.03e-12 A | -8.7e-08 .. -1.1e-11 A | yes | ff 125 C low |
| both_supplies_off (dig_in 1111, en 1, 3v3 0, 1v2 0) | -6.15e-10 .. -2.47e-12 A | -1.53e-09 .. -8.24e-12 A | yes | ff 125 C nom |

tie-lows dig_out[4] / dig_out[11], vdd_1v2 on: max 0 / 0 V (into 1 Tohm)
supply currents, all_off: I(vdd_3v3) 7.26e-11 .. 6.84e-09 A, I(vdd_1v2) 2.2e-06 .. 7.25e-06 A
supply currents, both_on: I(vdd_3v3) 1.89e-05 .. 3.03e-05 A, I(vdd_1v2) 2.2e-06 .. 7.25e-06 A
floating vdd_1v2 when gated off: 0 .. 0 V
floating vdd_3v3, vdd3v3_off: 0.5 .. 0.665 V
floating vdd_3v3, both_supplies_off: 0.464 .. 0.613 V

Switching times (transient, per corner):

| corner | T | I_OA on (uA) | t_on OA (us) | t_off OA | I_BG on (uA) | t_on BG (us) | t_off BG | I after off (OA / BG) |
|---|---|---|---|---|---|---|---|---|
| tt | -40 | 3.255 | 0.41 | 74 ns | 4.871 | 0.82 | 69 ns | 6.9e-12 / 1.1e-11 A |
| tt | 27 | 4.991 | 0.50 | 80 ns | 4.957 | 0.70 | 80 ns | 7e-12 / 1.2e-11 A |
| tt | 125 | 6.662 | 0.64 | 92 ns | 4.883 | 0.85 | 98 ns | 1.1e-10 / 1.1e-09 A |
| ss | -40 | 3.045 | 0.44 | 71 ns | 3.861 | 0.88 | 68 ns | 6.9e-12 / 1e-11 A |
| ss | 27 | 4.705 | 0.54 | 83 ns | 3.917 | 0.43 | 84 ns | 6.9e-12 / 1.1e-11 A |
| ss | 125 | 6.317 | 0.69 | 88 ns | 3.836 | 0.54 | 99 ns | 7.9e-11 / 7.4e-10 A |
| ff | -40 | 3.505 | 0.38 | 100 ns | 6.238 | 0.74 | 76 ns | 8e-12 / 1.8e-11 A |
| ff | 27 | 5.323 | 0.47 | 76 ns | 6.360 | 0.89 | 79 ns | 9.3e-12 / 4.1e-11 A |
| ff | 125 | 7.054 | 0.60 | 96 ns | 6.303 | 0.93 | 99 ns | 2.2e-10 / 1.9e-09 A |
| sf | -40 | 3.151 | 0.40 | 100 ns | 4.872 | 0.73 | 71 ns | 6.5e-12 / 5.4e-12 A |
| sf | 27 | 4.844 | 0.49 | 78 ns | 4.959 | 0.80 | 77 ns | 7.8e-12 / 1.7e-11 A |
| sf | 125 | 6.484 | 0.63 | 88 ns | 4.883 | 0.90 | 94 ns | 1.6e-10 / 1.4e-09 A |
| fs | -40 | 3.372 | 0.42 | 82 ns | 4.868 | 0.66 | 78 ns | 4.1e-12 / 1.8e-11 A |
| fs | 27 | 5.147 | 0.51 | 83 ns | 4.962 | 0.68 | 85 ns | 4.9e-12 / 1.4e-11 A |
| fs | 125 | 6.857 | 0.65 | 94 ns | 4.883 | 0.73 | 102 ns | 9e-11 / 8.6e-10 A |

Open-switch leakage over the bus 0 … 3.3 V: ≤ 0.16 nA (SUMMARY.md). The extracted layout netlist gives the same currents to 4 digits (tt / ff, 27 / 125 °C):

| corner | T (C) | I_OA (uA) low / nom / high supply | I_BG (uA) low / nom / high |
|---|---|---|---|
| tt | 27 | - / 4.992 / 4.994 | - / 4.958 / 4.965 |
| tt | 125 | - / 6.662 / 6.664 | - / 4.883 / 4.891 |
| ff | 27 | - / 5.324 / 5.326 | - / 6.360 / 6.369 |
| ff | 125 | - / 7.054 / 7.056 | - / 6.305 / 6.315 |

### 2.4 Checks

`tp_en_ctrl`: PDK KLayout DRC 0, magic + netgen LVS match (43 devices). `slot_7.gds` of stage A: KLayout DRC (feol + beol) 0, also for the foundry-pad variant; LVS "netlists match uniquely" (104 devices, 72 nets) with known
port errors only (the stand-in joins of the pad stubs `outp`/`vinp`, `outn`/`vinn`; the frame's `vss_1v2` strip). Harness fork `claude/c5-testplatform-test` (`9981b94`): `projects-clean`, `projects`, `projects-gds`, `gds-prefill` exit 0; `slot_7` in the pre-fill GDS equals the delivered GDS (XOR empty); net check of the pre-fill top: all 36 used and 27 unused slot pins OK.

## 3. Stage B

### 3.1 Additions

The bias tree `bias_tree_noab_pd` (the tree of the S2D pad) takes its reference from the OA core, the BG core or the harness `ibias0` (`dig_in[4..6]`; tree enable `dig_in[7]`); the four bias voltages go to `analog_bus2` through transmission gates (`dig_in[8..11]`: `vbp`, `vbn`, `vbpc`, `vbnc`); `ibias1` goes to `analog_bus3` (`dig_in[12]`) for comparison. All enables fail-safe as in stage A. New cells `tp_en_ctrl_b` (9 enables) and `bias_tree_noab_pd` (DRC 0, LVS match), plus 8 more `xgate`.

### 3.2 Simulation results (same 5 corners × 3 temperatures × 3 supplies; schematic netlist)

Bias voltages on `analog_bus2`, min … max over everything (V), for each reference (the last column: tree off, `vbp` selected):

| reference | vbp | vbn | vbpc | vbnc | tree off, vbp selected |
|---|---|---|---|---|---|
| oa | 1.494 .. 2.444 | 0.834 .. 0.980 | 1.395 .. 2.410 | 1.058 .. 1.381 | 2.313 .. 3.285 |
| bg | 1.636 .. 2.326 | 0.841 .. 0.962 | 1.545 .. 2.283 | 1.164 .. 1.249 | 2.313 .. 3.285 |
| ib0 | 1.601 .. 2.350 | 0.818 .. 0.992 | 1.515 .. 2.308 | 1.141 .. 1.288 | 2.313 .. 3.285 |

At nominal supply, per corner and temperature:

| corner | T | supply | vbn with OA / BG / ibias0 (V) | vbp with OA / BG / ibias0 (V) |
|---|---|---|---|---|
| tt | -40 | nom | 0.879 / 0.935 / 0.939 | 2.101 / 1.995 / 1.987 |
| tt | 27 | nom | 0.913 / 0.912 / 0.913 | 1.973 / 1.976 / 1.973 |
| tt | 125 | nom | 0.937 / 0.869 / 0.874 | 1.842 / 1.976 / 1.967 |
| ss | -40 | nom | 0.921 / 0.953 / 0.992 | 2.055 / 1.996 / 1.923 |
| ss | 27 | nom | 0.955 / 0.925 / 0.966 | 1.929 / 1.987 / 1.908 |
| ss | 125 | nom | 0.979 / 0.874 / 0.927 | 1.798 / 2.004 / 1.901 |
| ff | -40 | nom | 0.834 / 0.918 / 0.884 | 2.145 / 1.983 / 2.050 |
| ff | 27 | nom | 0.869 / 0.900 / 0.858 | 2.015 / 1.952 / 2.037 |
| ff | 125 | nom | 0.893 / 0.868 / 0.819 | 1.883 / 1.934 / 2.032 |
| sf | -40 | nom | 0.900 / 0.961 / 0.965 | 2.139 / 2.027 / 2.019 |
| sf | 27 | nom | 0.934 / 0.938 / 0.940 | 2.015 / 2.008 / 2.005 |
| sf | 125 | nom | 0.958 / 0.896 / 0.901 | 1.888 / 2.009 / 2.000 |
| fs | -40 | nom | 0.856 / 0.907 / 0.911 | 2.061 / 1.963 / 1.955 |
| fs | 27 | nom | 0.891 / 0.884 / 0.886 | 1.930 / 1.943 / 1.940 |
| fs | 125 | nom | 0.915 / 0.842 / 0.846 | 1.793 / 1.943 / 1.933 |

## ibias1 -> analog_bus3 (bus at 0.7 V, harness source 5 uA)

on: 5.0000 .. 5.0009 uA; off: max 2.9e-11 A

## Fail-safe (every dig_in = 1)

| case | max V(bus2) into 1 Gohm | max \|I(bus0)\| | max \|I(bus1)\| | max \|I(bus3)\| |
|---|---|---|---|---|
| vdd1v2_off | 200.9 mV | 6.32e-11 A | 1.57e-10 A | 2.9e-11 A |
| vdd1v2_off_1uA | 200.9 mV | 6.32e-11 A | 1.57e-10 A | 2.9e-11 A |
| enable_low | 200.9 mV | 6.32e-11 A | 1.57e-10 A | 2.9e-11 A |

Same quantities from the extracted layout netlist (fewer points: tt / ff at 27 / 125 °C):

| reference | vbp | vbn | vbpc | vbnc | tree off, vbp selected |
|---|---|---|---|---|---|
| oa | 1.842 .. 2.015 | 0.869 .. 0.937 | 1.745 .. 1.956 | 1.163 .. 1.336 | 2.763 .. 2.990 |
| bg | 1.934 .. 1.976 | 0.868 .. 0.912 | 1.843 .. 1.916 | 1.205 .. 1.246 | 2.763 .. 2.990 |
| ib0 | 1.967 .. 2.037 | 0.819 .. 0.913 | 1.883 .. 1.979 | 1.145 .. 1.225 | 2.763 .. 2.990 |

## ibias1 -> analog_bus3 (bus at 0.7 V, harness source 5 uA)

on: 5.0000 .. 5.0009 uA; off: max 2.2e-11 A

## Fail-safe (every dig_in = 1)

| case | max V(bus2) into 1 Gohm | max \|I(bus0)\| | max \|I(bus1)\| | max \|I(bus3)\| |
|---|---|---|---|---|
| vdd1v2_off | 161.8 mV | 5.7e-11 A | 1.47e-10 A | 2.2e-11 A |
| vdd1v2_off_1uA | 161.8 mV | 5.7e-11 A | 1.47e-10 A | 2.2e-11 A |
| enable_low | 161.8 mV | 5.7e-11 A | 1.47e-10 A | 2.2e-11 A |

Reading: with the bandgap as reference `vbn` varies 0.841 … 0.962 V and `vbp` 1.636 … 2.326 V over all points (OA: `vbn` 0.834 … 0.980, `vbp` 1.494 … 2.444); the bandgap-driven tree is the flatter of the two over temperature at nominal supply (vbp 1.995 / 1.976 / 1.976 V at tt −40 / 27 / 125 °C against 2.101 / 1.973 / 1.842 V with the OA core).

### 3.3 Checks (stated in the delivery repository's PROGRESS, 2026-11-06)

`slot_7.gds` with stage B: KLayout DRC (feol + beol) 0; LVS "netlists match uniquely", 190 devices, 120 nets (the same three known port notes as stage A); stage A's tests repeated on the extracted stage-B layout; harness flow on the fork exit 0 with `slot_7` in the pre-fill top equal to this `slot_7.gds`; net check of the pre-fill top: all 49 used and 14 unused slot pins OK.

## 4. What this says about the taped-out slot

| question | answer from the platforms | caveat |
|---|---|---|
| reference current of the bandgap core | BG: 3.83 … 6.37 µA over corners / temperature / supply, 4.96 µA tt 27 °C; 0.37 % supply dependence 3.0 → 3.6 V; flat over temperature in tt (4.87 / 4.96 / 4.88 µA); extracted layout same to 4 digits | `bg_core_pd` as in the platforms; not geometry-compared with the taped-out cell here; the taped-out slot feeds it into `bias_dist_pd`, not a bus switch (a compliance of 0 … 2.5 V on the bus is therefore not directly the operating condition) |
| enable behavior | enable to 1 %: 0.43 … 0.93 µs (BG); disable ≈ 70 … 100 ns; fail-safe against `vdd_1v2` off / enable low: bus currents ≤ 0.17 nA | the taped-out enable is a different circuit (`ls_up_fs`, [glue_logic.md](glue_logic.md)); the platform's `tp_en_ctrl` was ratioed and needed `vdd_1v2` present |
| tree bias voltages | `vbn` ≈ 0.84 … 0.98 V, `vbp` ≈ 1.5 … 2.4 V on the S2D pad's tree with each reference | the taped-out pads use their own trees fed by `iref` from the slot; the tree of stage B is the same tree design (`bias_tree_noab_pd`), not the same instance |
| OA core | characterized here; **not in the taped-out slot** | for the record of the design only |

## 5. Stale or open in the platform records

- `docs/slot7_testplatform/SUMMARY.md` at `efb80141` still reads "Stage reached: A complete … Stage B not started"; stage B was built and checked later the same day (PROGRESS entries 2026-11-06T18:48Z and 19:03Z / 19:08Z). The stage B results are in `results_b/` and `results_b_layout/`.
- Open as stated in SUMMARY: back-feeding with `vdd_3v3` off (a procedure, or an NMOS-only switch); draft-style sheets; no slot-level PEX; chip-level DRC / LVS not run.
- Everything is simulation; the platforms were delivered but the chip was taped out with the replacement slot circuit, so there is no measured chip data from them.

## 6. Sources (commit `efb80141` of the design repository unless stated)

- [`docs/slot7_testplatform/PLAN.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/efb8014101ba0afad1235859016592bf511b2117/docs/slot7_testplatform/PLAN.md), [`RUNLOG.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/efb8014101ba0afad1235859016592bf511b2117/docs/slot7_testplatform/RUNLOG.md), [`SUMMARY.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/efb8014101ba0afad1235859016592bf511b2117/docs/slot7_testplatform/SUMMARY.md)
- [`macros/slot7_testplatform/`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/efb8014101ba0afad1235859016592bf511b2117/macros/slot7_testplatform): netlists (`slot7_testplatform.spice`, `slot7_stage_b.spice`), sheets, layout scripts (`make_slot_7.py`), testbenches
  [`testbenches/ngspice/`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/efb8014101ba0afad1235859016592bf511b2117/macros/slot7_testplatform/testbenches/ngspice) with `results/` (stage A, schematic), `results_layout/` (stage A, extracted), `results_b/`, `results_b_layout/` (summaries and CSVs, scripts `run_tb.py`, `run_tb_b.py`)
- Delivery repository: [`README.md` at `c072679`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/blob/c0726799dcf90d068d7ffaf6ab0e6565e1941db3/README.md) and [`docs/PROGRESS.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/blob/c0726799dcf90d068d7ffaf6ab0e6565e1941db3/docs/PROGRESS.md) (stage A and B entries)
- Harness fork `tatzelbrumm/sg13cmos5l_ocd_chipalooza`, branch `claude/c5-testplatform-test`: `docs/custom_pads/RUNLOG.md` (not read on 2026-11-22)
