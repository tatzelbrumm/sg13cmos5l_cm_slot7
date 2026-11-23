<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 test plan: measuring the fabricated chip through the Chipalooza #2 harness

Designer: Christoph Maier. Scope: the slot 7 circuit **as taped out** (this repository at `158afc5`; see [README.md](README.md)
section 1) on the Chipalooza #2 harness chip (`MPC9639`, harness branch `tapeout_nov_2026`). No chip has been measured yet.
Every expected value below is a **simulated interval** (a corner table, a CACE result range or a single simulated point), copied
with its source; none of them is a guaranteed limit, and the design had no specification (proof of concept; see
[datasheets/README.md](datasheets/README.md)). The verdict for a measurement is therefore "inside the simulated interval" or
"outside the simulated interval", never "pass / fail against a specification".

## 0. Sources

| key | file | repository @ commit |
|---|---|---|
| FT | [`docs/FOR_TIM.md`](../FOR_TIM.md) (harness settings, modes, expected values) | this repository @ `158afc5` |
| S7 | [`docs/slot_7.md`](../slot_7.md) (modes, registers) | this repository @ `158afc5` |
| GL | [glue_logic.md](glue_logic.md) (logic equations and truth table, derived from `netlist/slot_7.spice`) | this set |
| T1 | `docs/slot7_hookup/tier1/results.txt` (five corners), copied verbatim in [datasheets/slot_7_system.md](datasheets/slot_7_system.md) §1 | design repository `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single` @ `9052bd35` |
| MO | `docs/slot7_hookup/tier1/modes.txt` (modes), copied verbatim in [datasheets/slot_7_system.md](datasheets/slot_7_system.md) §2; stimulus from the docstring of `run_modes.py` in the same folder | design repository @ `9052bd35` |
| RL | `docs/replica_bias/RUNLOG.md` rows 121, 122, 129 | design repository @ `9052bd35` |
| RB | [datasheets/pad_ref_rb.md](datasheets/pad_ref_rb.md) (CACE, schematic) | design repository @ `9052bd35` |
| SD | [datasheets/sg13cmos5l_IOPadSingle2Diff.md](datasheets/sg13cmos5l_IOPadSingle2Diff.md) (CACE, schematic and magic PEX) | design repository @ `91a7da8b` |
| DS | [datasheets/sg13cmos5l_IOPadDiff2Single.md](datasheets/sg13cmos5l_IOPadDiff2Single.md) (CACE, schematic; results predate the layout) | design repository @ `91a7da8b` |
| EC | `macros/en_ctrl_3v3/README.md`, "starvation" row (pad leakage with the enables at any level) | design repository @ `9052bd35` |
| PL | `docs/slot7_testplatform/PLAN.md` §5 (verified stage A / B measurement procedure) | design repository @ `efb80141` |
| HK | `verilog/rtl/housekeeping.v` (register map), `verilog/rtl/router.v` (route codes), `verilog/rtl/user_project_control.v` and `user_project_control_base.v` (per-slot gating) | harness `tatzelbrumm/sg13cmos5l_ocd_chipalooza` @ `7eeb3cb` (tapeout commit; the four files are unchanged at the branch tip `055993f`) |

## 1. What can be observed where

| chip-level access | slot net | what it carries | mode |
|---|---|---|---|
| dedicated pad `s7_an[0]` | S2D pad input (`sg13cmos5l_IOPadSingle2Diff`) | the single-ended input, driven by the bench; range 0 … 1 V with `vref` ≈ 0.5 V (README §2.3) | all |
| dedicated pad `s7_an[1]` | D2S pad output (`sg13cmos5l_IOPadDiff2Single`) | the single-ended output, measured | all |
| shared pin `analog[0]` / `analog[1]`, through the harness's per-slot bus switch (0x51 bit 4 / 5) | `analog_bus0` / `analog_bus1` | S2D `outp` / `outn` (mon) or D2S `vinp` / `vinn` driven from outside (feed); disconnected otherwise (FT, GL §4) | mon, feed |
| shared pin `analog[2]`, bus switch 0x51 bit 6 | `analog_bus2` = `s7_an_0_vcm` = `s7_an_1_vref` (one net, GL §5) | `vcm` of the replica bias (default), or `vcm` driven from outside (ext) | default, ext |
| shared pin `analog[3]`, bus switch 0x51 bit 7 | `analog_bus3` = `s7_an_0_vref` (GL §5) | S2D `vref` (default), or driven from outside (ext) | default, ext |
| SPI read of 0x38 / 0x39 (HK: `dbus_in[7:0]` / `[11:8]`, the selected slot's `dig_out` while `dig_ena` = 1) | `dig_out[11:0]` | held low by `s7_doutpd` while `vdd_1v2` is on (GL §6) | all |
| chip supply currents (differences between states) | slot `vdd_3v3`; pad ring `iovdd` | enabled / disabled / unpowered currents (§4) | all |

The path from a shared pin to the slot is the one PL §5 describes for stage A: chip pin `analog[k]` → shared net → slot 7's harness bus
switch → `analog_bus<k>`. The shared net also carries the open switches of the other 17 slots, so a bus-current measurement needs the
leak subtraction of PL §5; a bus-voltage measurement needs a high-impedance voltmeter (FT: "read them with a high-impedance voltmeter").
The bus switch's series resistance was modelled as 10 kΩ ("harness switch and instrument") in the mode simulations (MO, `run_modes.py`).

## 2. Harness registers used (HK, quoted from the RTL)

| register | field | used as |
|---|---|---|
| `0x50` | `proj_sel[4:0]` | `0x07` selects slot 7 |
| `0x51` | bit 0 `proj_ena` (slot `enable`), bit 1 `proj_3v3_ena`, bit 2 `proj_1v2_ena`, bit 3 `proj_dig_ena`, bits 7:4 `analog_bus_ena[3:0]` | supplies, enable, `dig_in` latch, bus switches |
| `0x20` + k, k = 0 … 23 | `user_in_route[k]` (4 bits): code `0x0`…`0xB` = pad `io[0..11]`, `0xD` = constant 0, `0xE` = constant 1, `0xF` = sequencer | source of the slot's `dig_in[k]` |
| `0x38`, `0x39` | `dbus_in[7:0]`, `dbus_in[11:8]` | read-back of `dig_out` |

Facts from the same RTL that matter here: the route registers reset to `0x0` (`user_in_route <= 96'd0`), i.e. every `dig_in` follows pad `io[0]`
until it is re-routed (PL §5 step 2 says the same); the per-slot `dig_in` latch is transparent while `dig_ena` = 1 and holds its value when
`dig_ena` = 0 ("allows the user to set up the digital input signal routing in advance, and then release the latch to present all signals
to the user project at the same time", `user_project_control.v`); the latch is reset (all `dig_in` = 0) while slot 7 is not selected; the
power gates and bus switches act only for the selected slot (`proj_3v3_ena = select & power_3v3_ena`, `user_project_control_base.v`).

FT states the settings as: "proj_sel = 7"; "power_3v3_ena on (power_1v2_ena only for the dig_out pull-downs)"; "proj_ena on → default
mode"; "route all dig_in registers to constant 0 first (0x0D); then set bits through 0x0D / 0x0E as needed"; "analog_ena[k] for the
buses you measure". S7: "close the harness's bus switches, reg 0x51 bits 6 / 7, to read them". `0x0D` / `0x0E` are route **codes**
written into `0x20 … 0x37` (HK, `router.v`), not register addresses (`0x0E` as an address is `seq_prescaler`).

Mode bits (GL §3; FT): the bits act only with the **key `dig_in[3]` = 1 and `dig_in[4]` = 0**; otherwise the default applies.
`dig_in[0]` swap → `0x20`; `dig_in[1]` mon → `0x21`; `dig_in[2]` feed → `0x22`; `dig_in[3]` key → `0x23` = `0x0E`; `dig_in[4]` → `0x24`
stays `0x0D`; `dig_in[5]` ext → `0x25`. (Register numbers derived from HK: `0x20` + k routes `dig_in[k]`; PL §5 uses the same
mapping, e.g. "`0x22 = 0x0E` (`dig_in[2]` = 1)".) `dig_in[6..23]` are unused (GL §3).

The `0x51` values below are composed from the bit map above; values marked PL are those of PL §5 verbatim.

## 3. Sequence

Bench: SMU or precision source on `s7_an[0]`; high-impedance voltmeter (or SMU in voltage-measure mode) on `s7_an[1]`; high-impedance
voltmeters or sources on `analog[0..3]` as the step says; ammeters on the chip's 3.3 V supply and pad-ring supply for current differences.
Set every bench source on `s7_an[0]` and `analog[0..3]` to 0 V before power-up.

### 3.1 Power-up into the default mode (PL §5 steps 1–5 apply unchanged)

| step | SPI writes | state | measure / expect |
|---|---|---|---|
| P1 | `0x50 = 0x07` (PL) | slot 7 selected; `0x51` = 0: slot supplies off | baseline: pad-ring current with the slot's supplies off; the pads draw leakage only, **≤ 67 nA at 125 °C** (FT); per pad S2D ≤ 0.4 nA (−40 / 27 °C), ≤ 25 nA (125 °C), D2S ≤ 4.3 nA / ≤ 67 nA (EC; pad at 0 / 1.8 / 3.6 V, enables anywhere in 0 … 3.6 V) |
| P2 | `0x20 … 0x37 = 0x0D` (PL) | all 24 `dig_in` routed to constant 0 | — |
| P3 | `0x51 = 0x06` (PL) | `vdd_3v3` and `vdd_1v2` gated on; `enable` = 0, `dig_ena` = 0 | disabled slot: leakage only (FT). Simulated, 150–170 µs after the enable falls: slot `vdd_3v3` 25.36 … 56.20 nA, ring 9.01 … 58.22 nA over the five corners (T1) |
| P4 | `0x51 = 0x0E` (PL) | `dig_ena` = 1: latches transparent, all `dig_in` = 0 | read `0x38` = `0x00`, `0x39` low nibble = 0 (`dig_out[11:0]` held low; GL §6; no stand-alone simulation of `s7_doutpd`) |
| P5 | `0x51 = 0x0F` (PL) | `enable` = 1 → **default mode** (no key) | current step from P4: slot `vdd_3v3` 48.38 … 49.74 µA, ring 364.58 … 395.62 µA over the five corners (T1; FT: "≈ 49 µA", "≈ 365–396 µA") |

Variant P3'–P5' **without `vdd_1v2`** (FT: "the slot works with only its `vdd_3v3` switched on"): `0x51 = 0x02`, `0x0A`, `0x0B`. Expect the same
analog results as with `vdd_1v2`; `dig_out` is then not held low by the slot (GL §6), so 0x38 / 0x39 carry no expectation.

### 3.2 Default mode: references and loop

| step | SPI writes | stimulus | measure | simulated interval (source) |
|---|---|---|---|---|
| D1 | `0x51 = 0xCF` (bus switches 2 and 3 closed) | none on `analog[2]` / `[3]` | `vcm` on `analog[2]`, `vref` on `analog[3]`, high-impedance | slot, extracted blocks: `vcm` 1.115 … 1.366 V (tt 27 °C: 1.257 V), `vref` 0.444 … 0.576 V (tt 27 °C: 0.492 V), five corners (T1; FT: 1.12–1.37 V, 0.44–0.58 V). `pad_ref_rb` alone (RB): `vcm` 1.242 … 1.395 V at 3.3 / 3.6 V, 1.12 … 1.193 V at 3.0 V; `vref` 0.4363 … 0.4553 V at −40 °C, 0.4832 … 0.5038 V at 27 °C, 0.5724 … 0.5964 V at 125 °C; Monte Carlo at tt 27 °C 3.3 V: `vcm` 1.247 … 1.274 V, `vref` 0.481 … 0.502 V |
| D2 | as D1 (or `0x51 = 0x0F` to keep the buses off the references) | `s7_an[0]` swept 0 … 1.0 V (T1, MO: "Pad in swept 0 ... 1.0 V") | `s7_an[1]` | D2S out = `vcm` + (in − `vref`) with the `vcm` / `vref` of D1 (FT; README §2.1). Maximum deviation from that line over 0 … 1 V: tt 27 °C 0.90 mV, ss −40 °C 1.31 mV, sf −40 °C 1.11 mV, fs 125 °C 3.37 mV, ff 125 °C 6.49 mV (T1); FT: "≤ 1.3 mV (−40 / 27 °C), ≤ 6.5 mV (125 °C)". D2S load in simulation: 1 GΩ (datasheets/slot_7_system.md) |

Context for D2 from the pad sheets (each pad simulated alone, not in the slot): S2D input range with `vref` = 0.5 V, low end 0 … 0.087 V,
high end 1.057 … 1.299 V (SD, `window_params`); D2S output swing, minimum output 0.6396 … 0.7386 V, maximum 3.266 … 3.283 V (DS,
`drive_params`). With `vcm` ≈ 1.26 V and `vref` ≈ 0.49 V an input of 0 V maps to about 0.77 V at the D2S output, close to that minimum.

### 3.3 Manual modes (key valid)

Write the mode bits with `dig_ena` cleared and set it afterwards, so that all bits reach the slot together (HK latch; recommended,
not part of FT): `0x51` bit 3 = 0, route writes, `0x51` bit 3 = 1. Return to the default between modes (`0x20 … 0x25 = 0x0D`).

| step | route writes | `0x51` | stimulus (as simulated, MO) | measure | simulated interval (MO unless stated) |
|---|---|---|---|---|---|
| M1 swap | `0x23 = 0x0E`, `0x20 = 0x0E` | `0x0F` | `s7_an[0]` 0 … 1.0 V | `s7_an[1]` | D2S out = `vcm` − (in − `vref`) (FT). Max deviation: tt 27 °C 0.99 mV, ff 125 °C 2.88 mV; **ss −40 °C: no simulated value** (no DC result; in the power-up transient swap stalls at the bandgap's start-up node, RL rows 121–122) |
| M2 mon | `0x23 = 0x0E`, `0x21 = 0x0E` | `0x3F` (bus switches 0, 1) | `s7_an[0]` 0 … 1.0 V; `analog[0]` / `[1]` high-impedance | `analog[0]` = `outp`, `analog[1]` = `outn`; `s7_an[1]` | loop unchanged: max deviation tt 27 °C 0.94 mV, ff 125 °C 6.55 mV; `v(bus0) − v(outp)` = `v(bus1) − v(outn)` = 0.01 mV (into 1 GΩ). Pad relation `outp − outn` = 2 (in − `vref`), (`outp` + `outn`)/2 = `vcm` (README §2.3); S2D gain 1.998 … 1.999, output common-mode error 5.003 … 18.05 mV (SD, `dc_params`, both views). The loop is slower while the bus switches are closed (FT); "stable, 10–30× slower" (this repository's `README.md`). ss −40 °C: no simulated value (as swap) |
| M3 feed | `0x23 = 0x0E`, `0x22 = 0x0E` | `0x3F` | `analog[0]` = `vcm` + 0.2 V, `analog[1]` = `vcm` − 0.2 V (MO: sources at `vcm` ± 0.2 V through 10 kΩ); `s7_an[0]` fixed 0.5 V | `s7_an[1]` | D2S out = `vcm` + (`v(bus0)` − `v(bus1)`)/2 = `vcm` + 0.2 V (MO). Max deviation: tt 27 °C 0.05 mV, ff 125 °C 2.22 mV; ss −40 °C: no DC result, power-up transient 0.24 mV (RL row 122). D2S alone: gain 0.4981 … 0.5, output offset 0.03487 … 1.947 mV (DS, `dc_params`, 3.3 / 3.6 V) |
| M4 ext | `0x23 = 0x0E`, `0x25 = 0x0E` | `0xCF` (bus switches 2, 3) | `analog[2]` = 1.30 V, `analog[3]` = 0.50 V (MO: "driven at 1.30 / 0.50 V through 10 kohm"); `s7_an[0]` 0 … 1.0 V | `s7_an[1]` | D2S out = `vcm` + (in − `vref`) with the external values (MO). Max deviation: tt 27 °C 0.91 mV, ff 125 °C 6.39 mV; ss −40 °C: no DC result, power-up transient 0.04 mV (RL row 122). `pad_ref_rb` stays enabled and keeps drawing its current (GL §3) |
| M5 swap + feed | `0x23 = 0x0E`, `0x20 = 0x0E`, `0x22 = 0x0E` | `0x3F` | as M3 | `s7_an[1]` | feed wins over swap (GL §3): as M3; tt 27 °C 0.05 mV, ff 125 °C 2.22 mV; ss −40 °C: no simulated value |
| M6 all high | `0x20 … 0x37 = 0x0E` | `0x0F` | as D2 | `s7_an[1]` | key invalid (`dig_in[4]` = 1) → default: 0.90 mV (tt 27 °C), 1.31 mV (ss −40 °C), 6.50 mV (ff 125 °C) |
| M7 no key, swap | `0x20 = 0x0E` only | `0x0F` | as D2 | `s7_an[1]` | default (not crossed): 0.90 / 1.31 / 6.50 mV at tt 27 / ss −40 / ff 125 °C |

M6 and M7 test the key: a crossed or opened loop there is outside the simulated behaviour. GL §3 lists all 16 combinations of the four mode bits.

### 3.4 Disable, fail-safe and leakage

| step | SPI writes | measure | simulated interval / expectation |
|---|---|---|---|
| F1 disable | `0x51` bit 0 = 0 (e.g. `0x0E`) | supply currents; `s7_an[1]` | slot `vdd_3v3` 25.36 … 56.20 nA, ring 9.01 … 58.22 nA, 150–170 µs after the enable falls (T1). Every switch opens, bandgap and distribution off, pad enables inactive (GL §2) |
| F2 enable with `vdd_1v2` off | `0x51 = 0x0B` | as D1, D2 | same as D1, D2 (P3'–P5'); the level shifters run from `vdd_3v3` only (GL §2) |
| F3 slot supplies off | `0x51` bits 1, 2 = 0 | pad-ring current | ≤ 67 nA at 125 °C (FT); per pad as P1 (EC) |
| F4 slot not selected | `0x50` = another slot | pad-ring current | the power gates follow `select` (HK), so as F3; `dig_in` latches reset to 0 (HK) |
| F5 pad leakage, disabled pads | F3 state, `s7_an[0]` and `s7_an[1]` each at 0 and 3.3 V | pad current | S2D pad input leakage −7.64 … 5.876 nA (SD, `pd_params`, schematic; PEX −7.647 … 5.869 nA); D2S pad leakage −36.83 … 9.71 nA (DS, `pd_params`); both over the CACE power-down states, 27 / 125 °C |
| F6 enable timing (optional, oscilloscope on `s7_an[1]`, `s7_an[0]` at a fixed level) | toggle `0x51` bit 0 | settling after enable | S2D pad enable time 1.359 … 1.43 µs (SD schematic), 1.463 … 1.524 µs (SD PEX); D2S turn-on 0.8054 … 1.228 µs (DS); `pad_ref_rb` enable: `vcm` 0.79 … 1.81 µs, `vref` 1.03 … 2.02 µs (README §2.3). S2D enable kick through the ext switches (tt 27 °C): `vcm` +118 / −63 mV, `vref` +85 / −62 mV (S7) |

Power-down order (carried over from PL §5 as a precaution): open the bus switches (`0x51` bits 7:4 = 0) and set every bench source on
`analog[0..3]` and `s7_an[0]` to 0 V **before** gating `vdd_3v3` off. In stage A a voltage on a bus drove the transmission gate's PMOS into
the floating `vdd_3v3` ("up to 87 nA at 0.7 V", PL §5). The taped-out slot uses other transmission gates (`tg_hv`, bulks on `vss` /
`vddh`, GL §4); this back-feeding was **not simulated** for them.

## 4. Temperature points

−40, 27 and 125 °C: the temperatures of the simulations above (T1: tt 27, ss −40, sf −40, fs 125, ff 125 °C; MO: tt 27, ss −40, ff 125 °C;
CACE suites −40 / 27 / 125 °C). At each point repeat D1, D2, M1–M4, F1 and F3; subtract the bus leakage measured with the slot disabled at
the same temperature (PL §5: "I_leak grows with temperature ... hence the subtraction at every point"). A single die sits at one process
point, so compare each value with the whole interval over corners at that temperature, not with the tt value.

## 5. Inside / outside the simulated interval

- **Inside:** the measured value lies within the interval stated for its step (for D2, M1–M7: the deviation from the stated straight line
  is at most the stated maximum for the nearest simulated temperature).
- **Outside:** record it with temperature, supply readings and the setup. Before attributing it to the circuit, check the setup: bus-switch
  resistance and the leakage of the 17 other slots on the shared pins (PL §5), meter loading of `vcm` / `vref` (FT), source impedance on
  `analog[0..3]` (simulated as 10 kΩ, MO).
- **Not covered by any simulation** (classify as "no simulated interval", not as outside): mismatch at slot level (only `pad_ref_rb` has a
  Monte Carlo result, RB; deviations of the loop that come from offsets can exceed the corner intervals); swap, mon, feed, ext and
  swap + feed at ss −40 °C in DC (MO, RL rows 121–122); the 3.0 / 3.6 V supplies for the modes (MO runs tt 27 °C 3.3 V, ss −40 °C 3.0 V, ff 125 °C 3.6 V only);
  whole-slot PEX (README §5); `s7_doutpd` on its own (GL §6).

## 6. What from the stage A / B procedure applies

The stage A / B test platforms ([test_platforms.md](test_platforms.md)) were **not taped out**; their procedure (PL §5) was written for them.

| PL §5 item | applies to the taped-out slot? |
|---|---|
| steps 1–5 (select, route all `dig_in` to 0, gates on, `dig_ena`, `enable`) | **yes, unchanged** (§3.1) |
| leak subtraction on a shared pin at every temperature | yes, for any bus-current measurement (§4) |
| power-down order (buses open, SMU at 0 V before `vdd_3v3` off) | yes, as a precaution (§3.4); the back-feed numbers belong to stage A |
| steps 6–10: OA / BG output currents on `analog[0]` / `[1]`, `I_OA = I_on − I_leak`, TG enables `dig_in[0..3]`, read-back bits on `0x38` | **no**: the taped-out slot has no OA core, does not route the bandgap current to a bus, and uses `dig_in[0..5]` as mode bits with the key; `dig_out` is held low |
| stage B: bias voltages on `analog_bus2` (`dig_in[8..11]`), `ibias1` on `analog_bus3` (`dig_in[12]`) | **no**: not in the taped-out slot; `analog_bus2/3` carry `vcm` / `vref` |
| the fail-safe idea (enable AND `dig_in` AND `vdd_1v2` present, `tp_en_ctrl`) | **no**: the taped-out enables are `ls_up_fs` level shifters that need no `vdd_1v2` (GL §2; test_platforms.md §4) |

The bandgap core's output current cannot be measured directly on the taped-out slot; it appears only through `vcm`, `vref` (D1) and the
supply currents (P5). The stage A simulation of the same macro (BG 3.83 … 6.37 µA, test_platforms.md §2.3) is background, not an expected value
for this chip.

## 7. Record per measurement

Chip identity (SPI reads of `0x01 … 0x07`, HK), die / board, temperature, supply readings, the `0x51` value and route writes, the bench
settings (source values and impedances), raw readings, and the step key of this plan. Keep raw data in a plain-text or CSV file next to the
summary.
