<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 glue logic: enables, mode decode, switch matrix, bias configuration, `dig_out` pull-downs

The glue is everything in `slot_7` that is not a signal or reference circuit: it makes the slot's enables, decodes six `dig_in` bits into modes, steers the
differential signal between the two pads and the harness buses, switches the replica-bias outputs onto the pads, configures the bias distribution, and keeps the unused
`dig_out` low. It was written in the replica-bias / slot hook-up session on 2026-11-08 on the day before the tapeout commit (2026-11-09), from the designer's mode specification, in the netlist
[`netlist/slot_7.spice`](../../netlist/slot_7.spice)
(subcircuits `s7_ctrl`, `s7_doutpd`, `slot_7`); every statement below about its logic is derived from that netlist, from which the CDL used for the layout check was derived
(KLayout LVS deep match, 497 devices). Back to [README.md](README.md).

## 1. Cells

| cell | what | where it comes from |
|---|---|---|
| `ls_up_fs` (core `efs_ls_core`) ×7 | fail-safe level shifter, one per input bit: 1.2 V harness level → 3.3 V (`out`, `out_b`) | `macros/en_ctrl_3v3` v2 |
| `nand2_hv` ×13, `inv_hv` ×12, `tg_hv` ×10 | 3.3 V static CMOS gates and transmission gates, all 1 µm / 0.45 µm sg13_hv (NOR stacks wider) | `macros/hv_logic`, layouts as `bdp_*` cells in `macros/bias_dist_pd` |
| `s7_ctrl` | enable, key and mode decode, five switch controls, ten transmission gates | `macros/slot_7`; layout 71.6 × 38.04 µm |
| `s7_doutpd` | 12 × hv NMOS 0.5 µm / 0.45 µm, gate `vdd_1v2`, source `vss_1v2`, bulk `vss_3v3`, drain on `dig_out[k]` | `macros/slot_7`; 24.67 × 3.85 µm |
| static ties in `slot_7` | bias-distribution configuration, same-net joins (section 5) | the `slot_7` subcircuit |

## 2. Inputs and fail-safe level shifting

`s7_ctrl` ports: supply `vddh` = `vdd_3v3`, `vss`; inputs `enable`, `d0 … d5` = `dig_in[0..5]`; enable outputs `en`, `en_b`; switched nets `outp outn vinp vinn bus0 bus1
vcm_rb vref_rb vcm_pad vref_pad`. Every input bit passes through its own `ls_up_fs`:

- The harness drives `enable` and `dig_in` from its always-on 1.2 V rail, so they are valid 0 / 1.2 V levels even while the slot's own `vdd_1v2` is off and 0 while slot 7 is
  not selected. No 1.2 V supply is needed to read them: `ls_up_fs` runs from the slot's switched `vdd_3v3` only.
- Circuit (from `en_ctrl_3v3` README): hv NMOS XN1 (1/0.45 µm), gate = the 1.2 V input, pulls node x low; a **leaker** (10 hv PMOS 0.3/20 µm in series, gates on the input)
  pulls x high when the input is 0 and is 2–5× weaker when it is 1.2 V; XPF (0.3/5 µm, gate y) latches x high once disabled (hysteresis, holds x against XN1's leakage);
  three `inv_hv` give y, out, out_b. The leaker is the only static current, and it flows only while the input is high (~50 nA per bit that is 1, as the netlist comment says;
  26–92 nA for the enable bit, 49–184 nA with one more bit high, measured over 11 PVT points in simulation).
- The input must be a harness level: XN1 conducts 0.6–8 µA at a 0.67 V gate, so a floating input at half a rail would read as 1.
- Unpowered (slot `vdd_3v3` off), the cell draws nothing; with the slot's 3.3 V floating at 0.6 V and `enable` high the outputs follow the floating rail (0.62–0.71 V) and draw 2 nA.
- Delay (50 fF load): enable 9.5–31 ns, disable 94–315 ns (simulation, schematic).

`en` / `en_b` (from `enable`) go to everything: `bg_core_pd`, `bias_dist_pd`, `pad_ref_rb`, the pads' `en_3v3` / `en_3v3_b` pins (same nets, joined in the layout) and the five
switch controls below. **`enable` = 0 opens every switch, switches the bandgap and the distribution off and makes all pad enables inactive.**

## 3. Mode decode (derived from the netlist)

Key and qualified bits (all in the 3.3 V domain, after the level shifters):

```
valid = d3 AND NOT d4                      (the key: dig_in[3] = 1, dig_in[4] = 0)
s = d0 AND valid     (swap)    m = d1 AND valid     (mon)    f = d2 AND valid     (feed)
ld = en AND NOT f AND NOT s                loop direct
lx = en AND NOT f AND s                    loop crossed
sb = en AND m AND NOT f                    S2D outputs to bus0/1
bd = en AND f                              bus0/1 to the D2S inputs
rc = en AND NOT (d5 AND valid)             replica bias connected to the pads
```

Without the key (`valid` = 0: `dig_in[3]` = 0, or `dig_in[4]` = 1) the three qualified bits and `ext` are 0, so any value of `dig_in[0..2]`, `dig_in[5]` gives the
**default**: `ld` = 1, `lx` = `sb` = `bd` = 0, `rc` = 1. Because the key is "3 high and 4 low", every all-equal `dig_in` pattern (the harness's reset state, where all 24
registers follow one pad, or all forced to constant 0) cannot match it. Every mode listed below needs `enable` = 1.

Truth table with the key valid and `enable` = 1 (columns: input bits swap = `dig_in[0]`, mon = `dig_in[1]`, feed = `dig_in[2]`, ext = `dig_in[5]`; outputs = the five switch controls):

| swap | mon | feed | ext | ld | lx | sb | bd | rc | resulting connection |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | loop direct; replica bias on pads |
| 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | loop direct; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | bus0/1 → D2S; loop open; replica bias on pads |
| 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | bus0/1 → D2S; loop open; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | loop direct; S2D → bus0/1; replica bias on pads |
| 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | loop direct; S2D → bus0/1; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | bus0/1 → D2S; loop open; replica bias on pads |
| 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | bus0/1 → D2S; loop open; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | loop crossed; replica bias on pads |
| 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | loop crossed; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | bus0/1 → D2S; loop open; replica bias on pads |
| 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | bus0/1 → D2S; loop open; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | loop crossed; S2D → bus0/1; replica bias on pads |
| 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | loop crossed; S2D → bus0/1; replica bias disconnected (pads take vcm / vref from bus2 / 3) |
| 1 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 1 | bus0/1 → D2S; loop open; replica bias on pads |
| 1 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | bus0/1 → D2S; loop open; replica bias disconnected (pads take vcm / vref from bus2 / 3) |

Notes:

- **feed wins** over swap and mon (`f` removes `ld`, `lx` and `sb`); feed opens the loop, connects `analog_bus0/1` to the D2S inputs and leaves the S2D outputs unconnected.
- **swap + mon** gives the crossed loop with the S2D outputs also on the buses.
- **ext** (`dig_in[5]`) disconnects `pad_ref_rb`'s `vcm_rb` / `vref_rb` from the pad nets (`rc` = 0). `pad_ref_rb` itself stays enabled and keeps drawing its current;
  the pad nets `vcm` / `vref` are the same nets as `analog_bus2` / `analog_bus3`, so the harness drives them from outside (through its own per-slot bus switches).
- The two bits `dig_in[3]` / `dig_in[4]` have no function other than the key; `dig_in[6..23]`, `clk`, `reset`, `ibias0/1`, `vbias` are unused.

## 4. Switch matrix: ten transmission gates

Each is a `tg_hv` (NMOS + PMOS, 1 µm / 0.45 µm hv, bulks on `vss` / `vddh`), closed when its control is 1 and its complement is 0:

| gate | control | connects | purpose |
|---|---|---|---|
| XT1, XT2 | `ld` | S2D `outp`–D2S `vinp`, `outn`–`vinn` | loop direct |
| XT3, XT4 | `lx` | `outp`–`vinn`, `outn`–`vinp` | loop crossed |
| XT5, XT6 | `sb` | `outp`–`bus0`, `outn`–`bus1` | monitor / drive the S2D outputs |
| XT7, XT8 | `bd` | `bus0`–`vinp`, `bus1`–`vinn` | feed the D2S from outside |
| XT9, XT10 | `rc` | `vcm_rb`–`vcm_pad`, `vref_rb`–`vref_pad` | replica bias onto the pads |

Each control is an inverted NAND output (`ld` = inverter of `ld_b`, and so on); the complement pin of each gate is the NAND output `ld_b`, `lx_b`, `sb_b`, `bd_b`, `rc_b`. All gates are in the 3.3 V domain.

## 5. Static ties and same-net joins in `slot_7`

- **`bias_dist_pd` configuration:** input 0 (`ibg`, the bandgap's ~5 µA) on, inputs 1…3 tied to `vss_3v3` and their enables low; outputs 0…2 on (to `pad_ref_rb`'s `iprb`,
  `s7_an_0_iref`, `s7_an_1_iref`), output 3 off (`isp`, spare), its enable tied low. The three distribution outputs are therefore a bandgap-referenced 5 µA each, 1:1.
- **Same-net joins** (written as 0 V sources in the simulation netlist, one net each in the layout): `en` = `s7_an_0_en_3v3` = `s7_an_1_en_3v3`; `en_b` = the two `_en_3v3_b`;
  `vcm` = `s7_an_0_vcm` = `s7_an_1_vref` = `analog_bus2`; `vref` = `s7_an_0_vref` = `analog_bus3`. The harness's own per-slot bus switches (reg 0x51 bits 4…7) isolate the buses.
- **`pad_ref_rb` supply:** the slot's `vdd_3v3`; the pad ring is not reachable inside the slot.

## 6. `dig_out` pull-downs (`s7_doutpd`)

Twelve identical hv NMOS (W 0.5 µm, L 0.45 µm), gate on `vdd_1v2`, source `vss_1v2`, bulk `vss_3v3`, drain on `dig_out[k]`: while the slot's `vdd_1v2` is on, `dig_out[11:0]` are held
low (as the fallback slot did); with it off the pull-downs are off, and the slot does not drive the outputs. This is the only use of `vdd_1v2` in the slot. No stand-alone verification beyond the slot's DRC / LVS.

## 7. What was verified, and what was not

| item | result | source |
|---|---|---|
| layout of `s7_ctrl` | KLayout DRC clean, LVS clean | design repository, `macros/slot_7` (agent C), RUNLOG |
| whole slot | DRC clean; LVS deep match, 497 devices, 0 port errors; netgen: 5 subcircuits match, one expected port error | `slot_7_checks.txt` |
| mode simulations, extracted pads, tt 27 °C | all 8 listed modes pass: round-trip error ≤ 0.99 mV (default 0.90, swap 0.99, mon 0.94, feed 0.05, ext 0.91, all-high and no-key-swap = default 0.90, swap + feed 0.05); with mon, `v(bus0) − v(outp)` = `v(bus1) − v(outn)` = 0.01 mV | `docs/slot7_hookup/tier1/modes.txt` |
| ff 125 °C | all modes pass; default 6.50 mV, swap 2.88, mon 6.55, feed 2.22, ext 6.39, swap + feed 2.22 | same |
| **ss −40 °C, DC** | default, all-high and no-key converge (1.31 mV); **swap, mon, feed, ext and swap + feed give no DC result** (convergence, even with more iterations and `rshunt` 1e12) | same; RUNLOG row 121 |
| ss −40 °C, transient from power-up (supplies, enable and bits ramped) | feed 0.24 mV and ext 0.04 mV pass; **swap and mon stall at the bandgap's start-up node `xbg.ks` at the enable edge**; swap + feed not stated as rerun | RUNLOG row 122 |
| enable cell | 128 / 128 CACE rows inside the designer's working limits (the ad hoc specification) (output error ≤ 1.3 µV, delays ≤ 2.4 / 81 ns with 100 ps edges); Monte Carlo and PEX not done | `en_ctrl_3v3` README |
| S2D enable kick through the ext switches (tt 27 °C) | `vcm` +118 / −63 mV, `vref` +85 / −62 mV (shorted: +107 / −58, +81 / −54 mV) | `slot_7` README |
| mon / bus load | with the bus switches closed the S2D → D2S loop is 10–30× slower, stable; the bus taps add a shared chip pad on `outp` / `outn` | `slot_7` README, RUNLOG |

Not verified (as far as the sources say): glue-level Monte Carlo; PEX of the whole slot; the hv-TG on-resistance and its effect on the loop at the corners other than those
listed; silicon.

## 8. Discrepancies to be aware of

- **Key bits.** An earlier concept, `docs/slot7_hookup/CONCEPT.md` (design repository), proposes the key `dig_in[23]` = 1, `dig_in[22]` = 0 with the pad-side bits in `dig_in[13..23]` and
  extra reference-select and bus-tap bits. The taped-out netlist implements the key on **`dig_in[3]` / `dig_in[4]`** with mode bits in `dig_in[0, 1, 2, 5]`, as the delivery's
  `docs/slot_7.md` and `FOR_TIM.md` state. This page follows the netlist.
- **Fallback diagnostics.** The test-platform fallback allocated `dig_in[0..12]` differently (enables of the two bias cores and transmission gates). Those functions are gone from
  the taped-out slot; only the default mode and the modes above exist.
- The delivery README says the harness flow with these pads and this `slot_7.gds` was not run on its branch; the glue was therefore verified at slot level, not through the harness.
