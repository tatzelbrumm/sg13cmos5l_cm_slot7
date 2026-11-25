<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 test plan: measuring the fabricated chip through the Chipalooza #2 harness

Designer: Christoph Maier. Scope: the slot 7 circuit **as taped out** (this repository at `158afc5`; see [README.md](README.md)
section 1) on the Chipalooza #2 harness chip (`MPC9639`, harness branch `tapeout_nov_2026`). No chip has been measured yet.
Every expected value below is a **simulated interval** (a corner table, a CACE result range or a single simulated point), copied
with its source; none of them is a guaranteed limit, and the design's only specification is the ad hoc one of the CACE working limits (see
[ACHIEVED_VS_LIMITS.md](ACHIEVED_VS_LIMITS.md)). The verdict for a measurement is therefore "inside the simulated interval" or
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
| DS | [datasheets/sg13cmos5l_IOPadDiff2Single.md](datasheets/sg13cmos5l_IOPadDiff2Single.md) (CACE, schematic, re-run on 2026-11-25 on the taped-out schematic; replaces the committed results of 2026-10-21, which predated the final schematic) | yaml: design repository @ `91a7da8b`; results: [d2s_schematic_rerun](../../verification/c2_gaps/d2s_schematic_rerun/results.md) |
| DP | [verification/c2_gaps/d2s_pex/results.md](../../verification/c2_gaps/d2s_pex/results.md) (D2S, CACE on the magic PEX of the taped-out cell) | this repository |
| DC | [verification/c2_gaps/dc_curves/results.md](../../verification/c2_gaps/dc_curves/results.md) (DC curves of both pads and of the round trip) | this repository |
| AT | [verification/c2_gaps/ac_tran/results.md](../../verification/c2_gaps/ac_tran/results.md) (AC, transient, noise of both pads and of the round trip) | this repository |
| RP | [verification/c2_gaps/replica_bias/results.md](../../verification/c2_gaps/replica_bias/results.md) (`pad_ref_rb` PEX and mismatch) | this repository |
| SM | [verification/c2_gaps/slot_modes_bg/results.md](../../verification/c2_gaps/slot_modes_bg/results.md) (modes at ss −40 °C from power-up, `bg_core_pd` alone) | this repository |
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
The bus switch's series resistance was modeled as 10 kΩ ("harness switch and instrument") in the mode simulations (MO, `run_modes.py`).

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

Bench (minimum capabilities: §8; acceptance intervals per step: §9): SMU or precision source on `s7_an[0]`; high-impedance voltmeter (or SMU in voltage-measure mode) on `s7_an[1]`; high-impedance
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
high end 1.057 … 1.299 V (SD, `window_params`); D2S output swing, minimum output 0.6354 … 0.7359 V, maximum 3.266 … 3.283 V (DS,
`drive_params`, at the CACE input common mode 1.65 V). With `vcm` ≈ 1.26 V and `vref` ≈ 0.49 V an input of 0 V maps to about 0.77 V at
the D2S output; at the slot's own operating point (D2S `vicm` = `vref` = 1.26 V) the D2S is linear (10 mV) over 0.211 … 2.317 V at
tt 27 °C 3.3 V, worst 0.328 … 2.258 V (DC §2b, 1 kΩ to 1.26 V), so 0.77 V is well inside it.

### 3.3 Manual modes (key valid)

Write the mode bits with `dig_ena` cleared and set it afterwards, so that all bits reach the slot together (HK latch; recommended,
not part of FT): `0x51` bit 3 = 0, route writes, `0x51` bit 3 = 1. Return to the default between modes (`0x20 … 0x25 = 0x0D`).

| step | route writes | `0x51` | stimulus (as simulated, MO) | measure | simulated interval (MO unless stated) |
|---|---|---|---|---|---|
| M1 swap | `0x23 = 0x0E`, `0x20 = 0x0E` | `0x0F` | `s7_an[0]` 0 … 1.0 V | `s7_an[1]` | D2S out = `vcm` − (in − `vref`) (FT). Max deviation: tt 27 °C 0.99 mV, ff 125 °C 2.88 mV; ss −40 °C 3.0 V: no DC result; power-up transient from 0 V 1.12 mV (SM §1, pad out 1 GΩ ∥ 10 pF; the stall reported in RL rows 121–122 is traced there to the solver at the pads' antenna diodes, not to the bandgap) |
| M2 mon | `0x23 = 0x0E`, `0x21 = 0x0E` | `0x3F` (bus switches 0, 1) | `s7_an[0]` 0 … 1.0 V; `analog[0]` / `[1]` high-impedance | `analog[0]` = `outp`, `analog[1]` = `outn`; `s7_an[1]` | loop unchanged: max deviation tt 27 °C 0.94 mV, ff 125 °C 6.55 mV; `v(bus0) − v(outp)` = `v(bus1) − v(outn)` = 0.01 mV (into 1 GΩ). Pad relation `outp − outn` = 2 (in − `vref`), (`outp` + `outn`)/2 = `vcm` (README §2.3); S2D gain 1.998 … 1.999, output common-mode error 5.003 … 18.05 mV (SD, `dc_params`, both views). The loop is slower while the bus switches are closed (FT); "stable, 10–30× slower" (this repository's `README.md`). ss −40 °C 3.0 V: no DC result; power-up transient 1.43 mV (SM §1) |
| M3 feed | `0x23 = 0x0E`, `0x22 = 0x0E` | `0x3F` | `analog[0]` = `vcm` + 0.2 V, `analog[1]` = `vcm` − 0.2 V (MO: sources at `vcm` ± 0.2 V through 10 kΩ); `s7_an[0]` fixed 0.5 V | `s7_an[1]` | D2S out = `vcm` + (`v(bus0)` − `v(bus1)`)/2 = `vcm` + 0.2 V (MO). Max deviation: tt 27 °C 0.05 mV, ff 125 °C 2.22 mV; ss −40 °C: no DC result, power-up transient 0.24 mV (RL row 122; SM §1 the same). D2S alone: gain 0.4983 … 0.5000, output offset 0.032 … 1.737 mV (DS, `dc_params`, 3.3 / 3.6 V) |
| M4 ext | `0x23 = 0x0E`, `0x25 = 0x0E` | `0xCF` (bus switches 2, 3) | `analog[2]` = 1.30 V, `analog[3]` = 0.50 V (MO: "driven at 1.30 / 0.50 V through 10 kohm"); `s7_an[0]` 0 … 1.0 V | `s7_an[1]` | D2S out = `vcm` + (in − `vref`) with the external values (MO). Max deviation: tt 27 °C 0.91 mV, ff 125 °C 6.39 mV; ss −40 °C: no DC result, power-up transient 0.04 mV (RL row 122); SM §1: 4.92 mV, there taken against the source values 1.30 / 0.50 V behind their 10 kΩ. `pad_ref_rb` stays enabled and keeps drawing its current (GL §3) |
| M5 swap + feed | `0x23 = 0x0E`, `0x20 = 0x0E`, `0x22 = 0x0E` | `0x3F` | as M3 | `s7_an[1]` | feed wins over swap (GL §3): as M3; tt 27 °C 0.05 mV, ff 125 °C 2.22 mV; ss −40 °C: no DC result, power-up transient 0.24 mV (SM §1) |
| M6 all high | `0x20 … 0x37 = 0x0E` | `0x0F` | as D2 | `s7_an[1]` | key invalid (`dig_in[4]` = 1) → default: 0.90 mV (tt 27 °C), 1.31 mV (ss −40 °C), 6.50 mV (ff 125 °C) |
| M7 no key, swap | `0x20 = 0x0E` only | `0x0F` | as D2 | `s7_an[1]` | default (not crossed): 0.90 / 1.31 / 6.50 mV at tt 27 / ss −40 / ff 125 °C |

M6 and M7 test the key: a crossed or opened loop there is outside the simulated behavior. GL §3 lists all 16 combinations of the four mode bits.

### 3.4 Disable, fail-safe and leakage

| step | SPI writes | measure | simulated interval / expectation |
|---|---|---|---|
| F1 disable | `0x51` bit 0 = 0 (e.g. `0x0E`) | supply currents; `s7_an[1]` | slot `vdd_3v3` 25.36 … 56.20 nA, ring 9.01 … 58.22 nA, 150–170 µs after the enable falls (T1). Every switch opens, bandgap and distribution off, pad enables inactive (GL §2) |
| F2 enable with `vdd_1v2` off | `0x51 = 0x0B` | as D1, D2 | same as D1, D2 (P3'–P5'); the level shifters run from `vdd_3v3` only (GL §2) |
| F3 slot supplies off | `0x51` bits 1, 2 = 0 | pad-ring current | ≤ 67 nA at 125 °C (FT); per pad as P1 (EC) |
| F4 slot not selected | `0x50` = another slot | pad-ring current | the power gates follow `select` (HK), so as F3; `dig_in` latches reset to 0 (HK) |
| F5 pad leakage, disabled pads | F3 state, `s7_an[0]` and `s7_an[1]` each at 0 and 3.3 V | pad current | S2D pad input leakage −7.64 … 5.876 nA (SD, `pd_params`, schematic; PEX −7.647 … 5.869 nA); D2S pad leakage −36.83 … 14.94 nA (DS, `pd_params`; PEX −36.85 … 14.95 nA, DP); both over the CACE power-down states, 27 / 125 °C |
| F6 enable timing (optional, oscilloscope on `s7_an[1]`, `s7_an[0]` at a fixed level) | toggle `0x51` bit 0 | settling after enable | S2D pad enable time 1.359 … 1.43 µs (SD schematic), 1.463 … 1.524 µs (SD PEX); D2S turn-on 0.982 … 1.819 µs (DS), 1.109 … 2.387 µs (DP); `pad_ref_rb` enable: `vcm` 0.79 … 1.81 µs, `vref` 1.03 … 2.02 µs (README §2.3). S2D enable kick through the ext switches (tt 27 °C): `vcm` +118 / −63 mV, `vref` +85 / −62 mV (S7) |

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
  swap + feed at ss −40 °C in DC (MO, RL rows 121–122; power-up transients exist for all 8 modes there, SM §1); the 3.0 / 3.6 V supplies for the modes (MO runs tt 27 °C 3.3 V, ss −40 °C 3.0 V, ff 125 °C 3.6 V only);
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

## 8. Equipment needed

Instrument *types* and the minimum capability each step needs (no availability, no persons). Adapted from the equipment list
of the sky130 proposal repository `sky130_cm_ip__single2diff2single` (`docs/EQUIPMENT_NEEDED.md`); the capabilities here are derived from this chip's simulated values (column 4), so
they are working estimates for a bench, not requirements of a specification.

| instrument | used in steps | minimum capability | derived from |
|---|---|---|---|
| harness test board with its SPI / control host | all | writes of `0x50`, `0x51`, `0x20 … 0x37`; reads of `0x38`, `0x39`, `0x01 … 0x07` | §2, §7 (HK) |
| chip supplies (3.3 V slot supply, pad ring) | all | as the harness board provides; 3.0 / 3.6 V settable if the 3.0 / 3.6 V corner intervals are to be compared at their own supply | T1 simulates −40 °C at 3.0 V and 125 °C at 3.6 V |
| current meters on the chip's 3.3 V supply and on the pad-ring supply (SMU or ammeter in series) | P1, P3, P5, F1, F3, F4 | µA range with ≤ 0.1 µA resolution for the enabled step; ≤ 1 nA resolution for the disabled and unpowered states; stable over the minutes of a state change, because the slot is seen only as a difference on supplies shared with the rest of the chip (§1) | enabled 48.38 … 49.74 µA (slot), 364.58 … 395.62 µA (ring); disabled 25.36 … 56.20 nA / 9.01 … 58.22 nA (T1); unpowered ≤ 67 nA (FT) |
| source-measure unit on `s7_an[0]` | D2, M1, M2, M4, M6, M7 (sweep 0 … 1.0 V, optionally to 1.5 V for the range ends, §9), M3 (fixed 0.5 V), F5 (0 / 3.3 V), D3–D5 (DC level) | 0 … 3.3 V; low source impedance (the S2D was characterized from 50 Ω, SD); current resolution ≤ 0.1 nA for F5 | S2D pad leakage −7.640 … 5.876 nA (SD) |
| DC voltmeters, high input impedance, at least 3 (`s7_an[1]`; `analog[2]` and `analog[3]`, or `analog[0]` and `analog[1]` in mon; and the applied `s7_an[0]` level) | D1, D2, M1–M7, F2 | 6½ digits, 10 µV resolution or better over 0 … 3.3 V, input impedance ≥ 1 GΩ | smallest simulated deviation 0.05 mV (M3, MO); bus vs pad difference 0.01 mV into 1 GΩ (MO); FT: "read them with a high-impedance voltmeter" |
| DC voltage sources, 2 channels, each behind a 10 kΩ series resistor | M3 (`analog[0]` / `[1]` at `vcm` ± 0.2 V), M4 (`analog[2]` / `[3]` at 1.30 / 0.50 V) | 0 … 3.3 V; set to 0 V before power-down (§3.4) | the mode simulations drive the buses through 10 kΩ (MO) |
| oscilloscope | F6; D4 (optional) | 2 channels plus a trigger from the SPI write (F6); ≥ 20 MHz bandwidth (≥ 10× the highest round-trip bandwidth; derived here); able to resolve 5 mV on a 0.5 V step (the 1 % band) and excursions of 0.1 … 0.3 V | round trip 1.08 … 1.69 MHz, 1 % settling 399 … 623 ns (AT §1); D2S enable excursion +228.1 / −224.8 mV (DP) |
| function generator | D3–D5 (optional) | sine 1 kHz … 10 MHz with DC offset; step 0.25 ↔ 0.75 V with edges ≤ 10 ns; sine distortion at 10 kHz below the −78.2 dB to be measured | AT §1 (10 ns edges as simulated, THD −78.2 dB at tt 27 °C) |
| frequency-response analyzer, or the generator with the oscilloscope / a lock-in amplifier | D3 (optional) | magnitude and phase from 1 kHz to ≥ 5 MHz | round trip 1.08 … 1.69 MHz, gain at 1 kHz −0.011 … −0.048 dB (AT §1) |
| FFT analyzer, audio analyzer or ≥ 24-bit ADC with FFT | D5 (optional) | > 80 dB dynamic range at 10 kHz … 70 kHz (harmonics 2–7) | THD −78.2 … −53.4 dB (AT §1) |
| loads for `s7_an[1]` | D2 (open), D3, D4 | open (≥ 1 GΩ); 1 kΩ to a source set to the measured `vcm`, with 10 pF and 100 pF; the board's and probe's own capacitance counted in the load | AT §1: "1 kΩ to an ideal copy of vref_d2s with 10 or 100 pF"; T1: 1 GΩ |
| SMU with pA resolution on a shared pin (only for bus-current measurements) | §4 leak subtraction | pA resolution | PL §5 |
| temperature chamber or thermal forcer, with a die or board temperature reading | §4 | −40, 27, 125 °C | the simulated temperatures (§4) |

## 9. Acceptance table

One row per measurement step: the quantity, the conditions, the **simulated** interval with its source, and how to classify
the reading. The intervals are the current ones (DC curves of 2026-11-24, AC / transient, the D2S re-run of 2026-11-25, the
ss −40 °C power-up runs); none is a guaranteed limit (the specification is the ad hoc one of [ACHIEVED_VS_LIMITS.md](ACHIEVED_VS_LIMITS.md)). "Inside" / "outside" always means
**inside / outside the simulated interval** of §5, not pass / fail. A die sits at one process point, so compare with the
interval over all simulated corners at the measured temperature; where only one corner was simulated at a temperature (27 °C:
tt only), a reading outside it says little by itself. Mismatch is in none of the slot-level intervals (§5; D2S output offset
σ 6.28 mV, DR §2; S2D input offset −10.2 … 16.0 mV over 100 samples, σ 5.25 mV, [S2D mismatch](../../verification/c2_gaps/s2d_mismatch/results.md)), so a loop deviation above its corner interval is
recorded as outside and then checked against the mismatch spread before the circuit is suspected. DR = the D2S re-run
([d2s_schematic_rerun](../../verification/c2_gaps/d2s_schematic_rerun/results.md)); other keys: §0.

| step | quantity | conditions | simulated interval (source) | classify |
|---|---|---|---|---|
| P1, F3, F4 | pad-ring current, slot supplies off | `0x51` = 0 (F4: another slot selected), bench sources at 0 V | ≤ 67 nA at 125 °C (FT); per pad S2D ≤ 0.4 nA (−40 / 27 °C), ≤ 25 nA (125 °C), D2S ≤ 4.3 nA / ≤ 67 nA (EC) | inside if ≤ the value at the nearest simulated temperature; the ring also supplies the other pads of the chip, so only the part attributable to slot 7's pads can be compared |
| P3, F1 | slot `vdd_3v3` and ring current, `enable` = 0 | 150–170 µs or later after the enable falls | −40 °C (ss, sf, 3.0 V): 25.36 … 25.55 nA / 9.01 … 9.09 nA; 27 °C (tt, 3.3 V): 31.63 / 12.24 nA; 125 °C (ff, fs, 3.6 V): 48.64 … 56.20 nA / 32.10 … 58.22 nA (T1) | inside / outside the interval at that temperature |
| P4 | `0x38`, `0x39` low nibble | `dig_ena` = 1, all `dig_in` = 0, `vdd_1v2` on | `0x00` / 0 (logic expectation, GL §6; no simulation of `s7_doutpd`) | equal / not equal |
| P5 | enabled current step from P4 | `s7_an[1]` open, `s7_an[0]` at 0 V | −40 °C (3.0 V): slot 48.38 … 48.61 µA, ring 364.58 … 369.44 µA; 27 °C (tt): 49.74 / 387.56 µA; 125 °C (3.6 V): 49.23 … 49.40 / 392.13 … 395.62 µA (T1, D2S at 1 GΩ) | inside / outside; a load on `s7_an[1]` adds its own current to the ring |
| D1 | `vcm` on `analog[2]`, `vref` on `analog[3]` | default mode, high-impedance meters | slot (T1): `vcm` −40 °C 1.115 … 1.138 V, 27 °C 1.257 V, 125 °C 1.299 … 1.366 V; `vref` 0.444 … 0.447 / 0.492 / 0.571 … 0.576 V. `pad_ref_rb` alone, 5 corners × 3.0 / 3.3 / 3.6 V (RP §1, schematic = PEX): `vcm` 1.242 … 1.395 V (3.3 / 3.6 V), 1.120 … 1.193 V (3.0 V); `vref` 0.4363 … 0.4553 V (−40 °C), 0.4832 … 0.5038 V (27 °C), 0.5724 … 0.5964 V (125 °C). Mismatch, tt 27 °C 3.3 V, 100 samples: `vcm` 1246.91 … 1273.95 mV (σ 5.415 mV), `vref` 481.36 … 501.81 mV (σ 3.788 mV) (RP §2) | inside the corner interval at that temperature and supply; outside it but within the mismatch spread: record as "outside the corner interval, within the mismatch range" (corners and mismatch were not simulated together) |
| D2 | max \|`s7_an[1]` − (`vcm` + `s7_an[0]` − `vref`)\| over `s7_an[0]` = 0 … 1 V, with the `vcm` / `vref` measured in D1 | default mode, `s7_an[1]` open | per PVT point, envelope of the schematic / magic PEX pads (DC §3), the KLayout-extracted pads (DC §3) and T1: tt 27 °C 3.3 V 0.86 … 0.90 mV; ss −40 °C 3.0 V 1.31 … 1.37 mV; sf −40 °C 3.0 V 1.10 … 1.13 mV; fs 125 °C 3.6 V 3.10 … 3.37 mV; ff 125 °C 3.6 V 6.10 … 6.49 mV | inside if ≤ the largest value at that temperature (−40 °C 1.37 mV, 27 °C 0.90 mV, 125 °C 6.49 mV) |
| D2 | round-trip gain (slope of `s7_an[1]` vs `s7_an[0]` near `s7_an[0]` = `vref`) | as above | 0.99848 … 0.99882 over the five PVT points (DC §3) | inside / outside (insensitive to offsets) |
| D2 | 1 mV-linear input range (contiguous around `s7_an[0]` = `vref`, error from the straight line < 1 mV), sweep extended to 1.5 V | as above | high end: −40 °C 1.055 … 1.114 V, 27 °C 1.281 V, 125 °C 1.367 … 1.440 V; low end above 0 V only at 125 °C: 0.028 … 0.096 V (DC §3, schematic pads; the KLayout-extracted pads give high ends up to 55.2 mV lower) | inside / outside |
| D3 (optional) | round-trip −3 dB bandwidth (relative to 1 kHz), peaking | `s7_an[0]` 0.5 V DC plus a small sine; loads open, 1 kΩ ∥ 10 pF, 1 kΩ ∥ 100 pF (1 kΩ to `vcm`) | tt 27 °C: 1.122 … 1.532 MHz; −40 °C (ss, sf, 3.0 V): 1.082 … 1.553 MHz; 125 °C (ff, fs, 3.6 V): 1.166 … 1.694 MHz; no peaking above the 1 kHz gain in any run (AT §1; three pad views, three loads) | inside / outside the interval at that temperature; state the actual load (board + probe) |
| D4 (optional) | settling of `s7_an[1]` to 1 % after a 0.25 → 0.75 V step (10 ns edges), overshoot, output step | loads as D3 | 1 %: tt 27 °C 453 … 623 ns (three views, three loads); over the five PVT points 399 … 499 ns (schematic, open and 1 kΩ ∥ 100 pF), 474 … 551 ns (PEX, tt / ss −40 °C / ff 125 °C); overshoot ≤ 0.05 %; output step 497.99 … 499.36 mV (AT §1) | inside / outside |
| D5 (optional) | THD (harmonics 2–7) of a 10 kHz sine 0 … 1 V | open or 1 kΩ ∥ 100 pF | tt 27 °C: −78.2 … −72.0 dB; open, schematic: −40 °C −70.6 … −67.9 dB, 125 °C −61.7 … −53.4 dB (AT §1; at 125 °C the bottom of the sine lies below the linear input range) | inside if not worse than the worst value at that temperature |
| M1 swap | max \|`s7_an[1]` − (`vcm` − (`s7_an[0]` − `vref`))\| | as D2 | tt 27 °C 0.99 mV, ff 125 °C 2.88 mV (MO); ss −40 °C 1.12 mV (SM §1, power-up transient) | inside if ≤ the value at that temperature; a non-inverted output is a logic fault, not a deviation |
| M2 mon | deviation as D2; `v(analog[0])` − `v(analog[1])` against 2 (`s7_an[0]` − `vref`), (`v(analog[0])` + `v(analog[1])`)/2 against `vcm` | bus switches 0, 1 closed, high-impedance meters | loop: tt 27 °C 0.94 mV, ff 125 °C 6.55 mV (MO), ss −40 °C 1.43 mV (SM §1); S2D gain 1.99849 … 1.99930, output CM error 5.003 … 18.050 mV (SD, `dc_params`); bus − pin 0.01 mV into 1 GΩ (MO) | inside / outside; the loop is 10–30× slower while the bus switches are closed (this repository's `README.md`), so let readings settle |
| M3 feed | `s7_an[1]` − (`vcm` + (`v(analog[0])` − `v(analog[1])`)/2) | sources at `vcm` ± 0.2 V through 10 kΩ, `s7_an[0]` 0.5 V | tt 27 °C 0.05 mV, ff 125 °C 2.22 mV (MO); ss −40 °C 0.24 mV (RL row 122, SM §1); D2S alone at `vicm` 1.65 V: gain 0.4983 … 0.5000, offset 0.032 … 1.737 mV (DS) | inside / outside |
| M4 ext | deviation as D2 with the measured `v(analog[2])` / `v(analog[3])` | sources 1.30 / 0.50 V through 10 kΩ | tt 27 °C 0.91 mV, ff 125 °C 6.39 mV (MO); ss −40 °C 0.04 mV (RL row 122) or 4.92 mV when taken against the source values behind the 10 kΩ (SM §1) | inside / outside; state which reference voltages were used |
| M5 swap + feed | as M3 | as M3 | as M3: tt 27 °C 0.05 mV, ff 125 °C 2.22 mV (MO), ss −40 °C 0.24 mV (SM §1) | inside / outside; a crossed output means feed did not win (GL §3) |
| M6, M7 | as D2 (key invalid → default) | as D2 | tt 27 °C 0.90 mV, ff 125 °C 6.50 mV, ss −40 °C 1.31 mV (MO; SM §1 1.37 mV) | inside / outside; a crossed or opened loop is a logic fault |
| F2 | D1 and D2 with `vdd_1v2` off | `0x51 = 0x0B` | as D1, D2 (FT: the slot works with only `vdd_3v3`; not simulated separately) | inside / outside the D1, D2 intervals |
| F5 | pad current, pads disabled | F3 state; each pad at 0 V and 3.3 V | S2D −7.640 … 5.876 nA (SD schematic; PEX −7.647 … 5.869 nA); D2S −36.83 … 14.94 nA (DS; PEX −36.85 … 14.95 nA, DP); CACE power-down states at 27 / 125 °C | inside / outside at 27 / 125 °C; at −40 °C only EC (P1 row) |
| F6 | time from the enable write to `s7_an[1]` within 1 mV / 1 % of its final value; excursion of `s7_an[1]` | `s7_an[0]` fixed, `s7_an[1]` open or 1 kΩ | no slot-level interval except ss −40 °C (`vcm` at 98 % 1.6 µs after enable, bandgap at 90 % after 0.80 … 0.83 µs, SM §1). Block values: `pad_ref_rb` `vcm` 0.79 … 1.81 µs, `vref` 1.03 … 2.02 µs (README §2.3); S2D 1.359 … 1.524 µs (SD, schematic … PEX); D2S 0.982 … 2.387 µs, excursion +121.6 … +228.1 / −104.3 … −224.8 mV with 1 kΩ (DS … DP) | no slot-level interval at 27 / 125 °C ("not covered", §5): record and compare with the block values; at −40 °C compare with SM |
| F6 (ext) | kick on `analog[2]` / `analog[3]` at the S2D enable | ext mode, tt 27 °C | `vcm` +118 / −63 mV, `vref` +85 / −62 mV (S7) | inside / outside at 27 °C; no value at other temperatures |
