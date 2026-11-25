<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 whole-slot PEX: results

**IHP sg13cmos5l post-layout (magic PEX) simulation.** Method, versions and limits: [README.md](README.md). Every
value in the comparison is in [tables.md](tables.md) and [csv/compare.csv](csv/compare.csv). Per-run values are in
`csv/*_summary.csv`.

## 1. LVS: the extraction is the taped-out circuit

netgen 1.5.324 compared each extraction, with capacitors dropped and parasitic resistors shorted
([lvs_summary.txt](lvs_summary.txt)):

| cell, extraction | layout devices (extracted → after merging) | reference | nets | result |
|---|---|---|---|---|
| `slot_7`, C-coupled | 497 → 371 (`sg13_hv_nmos` 179, `sg13_hv_pmos` 268, `rhigh` 41, `pnpMPA` 9) | `netlist/slot_7_netgen.spice`: 443 → 371 | 222 = 222 | **Netlists match** (11 symmetries, resolved by property / name), 0 property errors |
| `slot_7`, full-RC | the same 497 → 371 (9 427 resistors shorted) | same | 222 = 222 | Netlists match, 0 property errors |
| S2D pad, C / full-RC | 225 → 76 | `pads/…/sg13cmos5l_IOPadSingle2Diff.spice` | 37 = 37 | Circuits match uniquely; property errors only the schematic's `mm_ok` |
| D2S pad, C / full-RC | 293 → 76 | `pads/…/sg13cmos5l_IOPadDiff2Single.spice` | 36 = 36 | Circuits match uniquely; property errors only `mm_ok` |

The slot's top level still reports "failed pin matching", for the same reasons as the hierarchical check of
[`signoff/taped_out_158afc5`](../../../signoff/taped_out_158afc5/README.md):

- The reference's comma ports (`analog_bus3,s7_an_0_vref`, `s7_an_0_en_3v3,s7_an_1_en_3v3`) are single nets in the
  layout, so the names cannot pair.
- `vss_1v2_uq0` has no partner.
- In the full-RC check, shorting the resistors also merges the port names that magic keeps as separate resistive
  pieces of one net (`s7_an_0_vcm`, `s7_an_0_vref`, `s7_an_1_vref`, `s7_an_1_en_3v3*`), so those ports appear as "no
  matching pin" as well.

The unused harness pins (`dig_in[6..23]`, `clk`, `reset`, `ibias0/1`, `vbias`) are disconnected in both netlists.

**Verdict:** the whole-slot extraction from `final/gds/slot_7.gds` is the circuit of `netlist/slot_7_netgen.spice`.

## 2. Parasitics

Totals from [csv/pex_totals.csv](csv/pex_totals.csv). Ground is the substrate node: `vss_3v3` in the slot, `iovss` in
the pads. "Floating" means nodes without a device or resistor: the `tughra_art` metal and poly, and unused metal.

| cell | extraction | capacitors | C total [pF] | to ground [pF] | coupling [pF] | floating nodes [pF] | resistors |
|---|---|---|---|---|---|---|---|
| `slot_7` | `sak-pex.sh -m 2` (as the earlier pads) | 1568 | 1.889 | 0.760 | 1.128 | 0.160 (101 nodes) | – |
| `slot_7` | **C-coupled (with substrate C)** | 1636 | **2.158** | 1.029 | 1.128 | 0.160 | – |
| `slot_7` | **full-RC** | 3461 | 2.166 | 1.037 | 1.128 | 0.160 | **9 427** (169 of 388 nets) |
| S2D | `sak-pex.sh` (earlier pad PEX) | 573 | 1.447 | 0.562 | 0.886 | 0.019 | – |
| S2D | C-coupled / full-RC | 589 / 3436 | 1.889 / 1.889 | 1.003 | 0.886 | 0.019 | – / 12 048 |
| D2S | `sak-pex.sh` (earlier pad PEX) | 482 | 1.339 | 0.345 | 0.995 | 0.015 | – |
| D2S | C-coupled / full-RC | 503 / 3592 | 1.995 / 1.997 | 1.000 / 1.002 | 0.995 | 0.015 | – / 9 835 |

- The `.ext` files hold 2.162 pF (slot), 1.893 pF (S2D) and 1.999 pF (D2S). The flat output reproduces these totals
  to within the 0.01 fF threshold. **The hierarchical `sak-pex.sh` output, which all earlier pad PEX runs used, lacks
  0.27 pF in the slot, 0.44 pF in S2D and 0.66 pF in D2S.** All of that missing part is node-to-substrate
  capacitance: the bond pad's 116 fF (S2D) and 223 fF (D2S) are absent, and `enable` (33.8 fF) is absent. Some nets
  also get a value the `.ext` does not have: `s7_an_0_outp` has 11.6 fF instead of 3.5 fF.
- **Magic's own full-RC netlist double-counts capacitance.** It totals 3.90 pF for the slot, against 2.16 pF in the
  `.ext`. The resistor-node capacitances of a resistive net add up to that net's total capacitance, coupling included
  ([csv/rnode_caps_slot_7.csv](csv/rnode_caps_slot_7.csv): over the 146 resistive nets with ground capacitance,
  1.90 pF of rnode capacitance against 0.80 pF of ground capacitance). The full-RC netlist simulated here keeps
  magic's resistors and takes its capacitors from the C extraction (README, method 2).
- Selected slot nets, C total / to ground [fF] ([csv/pex_nets.csv](csv/pex_nets.csv)):

  | net | C total / to ground |
  |---|---|
  | `s7_an_0_outp` / `outn` | 10.7 / 3.5, 11.5 / 3.9 |
  | `s7_an_1_vinp` / `vinn` | 26.1 / 2.4, 23.3 / 3.4 |
  | `vcm` (`s7_an_0_vcm`) | 52.0 / 19.6 |
  | `vref` (`analog_bus3`) | 39.5 / 28.4 |
  | `iref` to S2D / D2S | 16.0 / 5.3, 17.6 / 8.8 |
  | replica outputs `vcm_rb` / `vref_rb` | 109 / 91, 174 / 147 |
  | bandgap `g` / `vpc` / `vpg` | 87 / 27, 90 / 2.8, 85 / 0.2 |
  | `vdd_3v3` | 464 / 119 |

- Resistance: the largest effective resistance from a port to any point of its net is 72 Ω (`s7_an_0_outp`), 120 Ω
  (`vinp` / `vinn`), 112 / 118 Ω (`iref` lines), 125 Ω (`analog_bus2`), 110 Ω (`vdd_3v3`) and 283 Ω (`enable`). In
  the pads it is 99 Ω (S2D `pad`) and 102 Ω (D2S `pad`). The ground networks show 7.3 kΩ (`vss_3v3`) and 13 … 14 kΩ
  (`iovss`) to their most remote resistor node. Which piece of the ground net that is was not examined. The
  substrate itself is not resistive in magic.

## 3. Simulation: change against the earlier slot runs

Views (README, method 5):

- `prev`: the earlier deck, rerun here.
- `c`: the whole slot magic C-coupled, with the earlier pad netlists.
- `cc`: as `c`, with the pads re-extracted with their substrate capacitance.
- `rc`: slot and pads full-RC.

**The `prev` rerun reproduces the committed CSVs of `../dc_curves` and `../ac_tran` (view `pex`).** Every row
agrees to the printed digits, or to 1 ns in settling, so the change columns compare like with like. "Change" is
`c` vs `prev` and `rc` vs `prev`. The tables show selected rows; [tables.md](tables.md) has all of them.

### 3.1 tt 27 °C 3.3 V

| quantity | committed (pads PEX) | prev | c | change c | cc | rc | change rc |
|---|---|---|---|---|---|---|---|
| `vcm` [V] | 1.2566 | 1.2566 | 1.2615 | +4.93 mV | 1.2615 | 1.2616 | +5.03 mV |
| `vref` (S2D) [V] | 0.4923 | 0.4923 | 0.4941 | +1.81 mV | 0.4941 | 0.4949 | +2.60 mV |
| S2D output common mode [V] | – | 1.2683 | 1.2733 | +4.93 mV | 1.2733 | 1.2650 | −3.31 mV |
| I slot `vdd_3v3` enabled [µA] | – | 49.75 | 49.63 | −0.2 % | 49.63 | 49.61 | −0.3 % |
| I ring `iovdd` enabled [µA] | – | 420.00 | 420.04 | +0.0 % | 420.04 | 419.95 | −0.0 % |
| I slot disabled (DC) [nA] | – | 7.35 | 8.73 | +18.8 % | 8.73 | 13.01 | +77 % |
| I ring disabled (DC) [nA] | – | 6.38 | 6.38 | 0 % | 6.38 | 18.72 | +193 % |
| bias current into each pad's `iref` [µA] | – | 5.0196 | 5.0198 | +0.005 % | 5.0198 | 5.0177 | −0.04 % |
| max \|error\| pad in 0 … 1 V [mV] | 0.870 | 0.870 | 0.872 | +0.00 mV | 0.872 | 0.865 | −0.01 mV |
| gain (small signal) | 0.99875 | 0.99875 | 0.99875 | −1 ppm | 0.99875 | 0.99889 | +141 ppm |
| offset [mV] | 0.064 | 0.064 | 0.064 | 0.00 mV | 0.064 | 0.119 | +0.06 mV |
| 1 mV-linear pad-in range [V] | −0.1708 … 1.2812 | −0.1708 … 1.2811 | −0.1710 … 1.2874 | −0.2 / +6.3 mV | same as c | −0.1688 … 1.2778 | +2.0 / −3.3 mV |
| f−3dB unloaded [MHz] | 1.356 | 1.356 | 1.322 | −2.5 % | 1.304 | 1.303 | −3.9 % |
| f−3dB 1 kΩ ∥ 10 pF [MHz] | 1.122 | 1.122 | 1.100 | −2.0 % | 1.082 | 1.081 | −3.7 % |
| f−3dB 1 kΩ ∥ 100 pF [MHz] | 1.325 | 1.325 | 1.294 | −2.4 % | 1.274 | 1.273 | −3.9 % |
| gain at 1 kHz, 1 kΩ load [dB] | −0.0117 | −0.0117 | −0.0117 | 0.000 | −0.0117 | −0.0148 | −0.003 |
| peaking (all loads) | none | none | none | – | none | none | – |
| step: settling 1 % rise, unloaded [ns] | 517 | 517 | 529 | +2.4 % | – | 537 | +3.9 % |
| step: settling 0.1 % rise, unloaded [ns] | 710 | 710 | 726 | +2.3 % | – | 736 | +3.7 % |
| step: settling 1 % rise, 1 kΩ ∥ 10 pF [ns] | 623 | 623 | 633 | +1.6 % | – | 643 | +3.2 % |
| step: settling 1 % rise, 1 kΩ ∥ 100 pF [ns] | 524 | 524 | 538 | +2.6 % | 546 | 546 | +4.2 % |
| step: settling 0.1 % rise, 1 kΩ ∥ 100 pF [ns] | 696 | 696 | 716 | +2.8 % | 727 | 727 | +4.5 % |
| step: settling 1 % fall, 1 kΩ ∥ 100 pF [ns] | 533 | 533 | 546 | +2.4 % | 554 | 554 | +3.9 % |
| step gain (0.5 V step), unloaded | 0.99872 | 0.99871 | 0.99871 | −2 ppm | – | 0.99885 | +139 ppm |
| enable: `vcm` at 98 % [µs after enable] | – | 1.59 | 1.68 | +5.7 % | – | 1.75 | +10.0 % |
| enable: `vref` at 98 % [µs] | – | 1.57 | 1.74 | +10.9 % | – | 1.73 | +9.9 % |
| enable: pad out within 1 mV [µs] | – | 1.86 | 2.21 | +18.3 % | – | 2.02 | +8.3 % |
| enable: peak ring current [µA] | – | 1032 | 967 | −6.3 % | – | 1033 | +0.1 % |

Overshoot in the step is ≤ 0.015 % at every point and in every view (largest: fs 125 °C, 1 kΩ ∥ 100 pF, prev 0.015 %, c 0.011 %, rc 0.009 %). The overlays are [plots/dc_error.png](plots/dc_error.png),
[plots/bode_tt27.png](plots/bode_tt27.png), [plots/step_tt27.png](plots/step_tt27.png) and
[plots/enable.png](plots/enable.png).

### 3.2 The five PVT points (c vs prev; rc vs prev)

| PVT | `vcm` change c / rc [mV] | `vref` change c / rc [mV] | max \|err\| 0 … 1 V prev → c [mV] | f−3dB unloaded change c / cc / rc | 1 % settling, 1 kΩ ∥ 100 pF, change c / rc |
|---|---|---|---|---|---|
| tt 27 °C 3.3 V | +4.93 / +5.03 | +1.81 / +2.60 | 0.870 → 0.872 (rc 0.865) | −2.5 % / −3.8 % / −3.9 % | +2.6 % / +4.2 % |
| ss −40 °C 3.0 V | +4.81 / +4.64 | +1.86 / +2.63 | 1.318 → no result | −2.9 % / −4.2 % / no result | +3.3 % / no result |
| ff 125 °C 3.6 V | **+24.29 / +24.85** | +1.77 / +2.53 | 6.11 → 6.11 (rc 6.14) | −2.5 % / −3.7 % / −3.8 % | +2.7 % / +4.4 % |
| fs 125 °C 3.6 V | **+13.18 / +13.37** | +1.82 / +2.57 | 3.11 → 3.12 (rc 3.10) | −2.5 % / −3.8 % / −4.0 % | +2.8 % / +4.6 % |
| sf −40 °C 3.0 V | +3.53 / +3.46 | +1.81 / +2.58 | 1.087 → no result (rc 0.924) | −2.6 % / – / −4.0 % | +2.9 % / +4.6 % |

- The enabled supply currents change by ≤ 0.3 % (slot) and ≤ 0.04 % (ring) at all five points. The bias currents into
  the pads (tt, ss −40 °C, ff 125 °C) change by ≤ 0.01 % (c) and 0.04 % (rc).
- The 1 mV-linear range's upper end follows `vcm`: ff 125 °C 1.3673 → 1.3998 V (+32 mV), fs 125 °C +21 mV, tt +6 mV.
  The lower end moves by ≤ 0.3 mV (c).
- Enable from the disabled operating point, with pad out within 1 mV, prev → c: tt 1.86 → 2.21 µs,
  **ss −40 °C 1.96 → 2.59 µs (+32 %)**, ff 125 °C 2.23 → 2.31 µs. The `vref` 98 % time at ss −40 °C goes from
  1.48 to 2.08 µs. The peak ring current at enable is 734 µA (c) against 932 µA (prev) at ss −40 °C.

### 3.3 Where the changes come from

- **`vcm` / `vref`: the replica-bias block `pad_ref_rb` alone.** The view `hyb` is the earlier deck with only
  `pad_ref_rb` replaced by its magic extraction (cut from `slot_7.gds`). It reproduces the whole-slot `c` values to
  0.03 mV: tt `vcm` 1.261529 V vs 1.261532 V, ff 125 °C 1.32333 vs 1.32336 V, ss −40 °C 1.11955 vs 1.11955 V, and
  `vref` within 0.02 mV. The bandgap and the distribution are not the cause: their output current into the pads is
  the same to 0.01 %. The magic values agree with the `pad_ref_rb` schematic: `../replica_bias` gives typical
  1.261 / 0.493 V at tt 27 °C, and PEX = schematic to 0.1 mV there. So the earlier slot runs, and the designer's
  tier-1 table (`vcm` 1.257, `vref` 0.492 V at tt; data sheet `slot_7_system.md`), are low by the error of the
  **KLayout-converted `pad_ref_rb` netlist** that the tier-1 deck uses (`run_tier1.wrapped()`). That error is 3.5 …
  4.9 mV at −40 / 27 °C and 13 … 24 mV at 125 °C for `vcm`, and 1.8 mV for `vref`. The cause inside that conversion
  was not found here (compare `../klayout_pad_diodes`, where the same converter drops the diode sizes).
- **Bandwidth and settling: −2.5 % / +2.5 % from the slot's wiring capacitance, −1.4 % more from the pads' substrate
  capacitance (`cc`), and next to nothing from wire resistance.** `rc` and `cc` agree to ≤ 0.15 % in f−3dB and
  to ≤ 2 ns in settling. At these impedances (≤ 125 Ω of wire, tens of fF) the resistance does not matter for the
  1.3 MHz loop.
- **Full-RC DC:** the gain moves +116 … +166 ppm toward 1 and the S2D output common mode moves −3 … −6 mV at
  −40 / 27 °C. The gain with 1 kΩ load drops by a further 0.003 dB (0.035 %, as if about 0.35 Ω were in series
  with the 1 kΩ load); where in the pad's output wiring this comes from was not isolated. The max \|error\| over 0 … 1 V changes by −0.16 … +0.03 mV.
- **Disabled currents:** these are DC operating points, in nA. The slot's DC current with `enable` = 0 rises
  +6 … +19 % (c) and +20 … +77 % (rc). The ring current is unchanged in c and rises +29 … +205 % in rc (5.4 → 16.7 nA
  at ss −40 °C). They are still in the nA range; the data sheet's 150–170 µs transient values (9 … 58 nA ring,
  25 … 56 nA slot) are of the same order.

### 3.4 Modes at tt 27 °C (task 4)

Max \|pad out − expected\| [mV], with the designer's `run_modes.py` definitions ([csv/mode_summary.csv](csv/mode_summary.csv)):

| mode | designer's `modes.txt` (KLayout pads) | prev (PEX pads) | c | change |
|---|---|---|---|---|
| swap | 0.99 | 0.980 | 0.986 | +0.006 |
| mon | 0.94 | 0.918 | 0.920 | +0.002 |
| feed | 0.05 | 0.041 | 0.037 | −0.003 |
| ext | 0.91 | 0.883 | 0.883 | +0.000 |

The full-RC `swap` run did not reach an operating point: no result after 796 s with KLU and 618 s with SPARSE, after
which it was stopped. The full-RC runs of mon, feed and ext were therefore not attempted.

### 3.5 Against the slot data sheet (`docs/chipalooza2_as_taped_out/datasheets/slot_7_system.md`, tier-1, KLayout pads)

| PVT | data sheet `vcm` / `vref` [V] | this run `c` | data sheet max err [mV] | `c` | data sheet I slot / ring [µA] | `c` |
|---|---|---|---|---|---|---|
| tt 27 °C | 1.257 / 0.492 | 1.2615 / 0.4941 | 0.90 | 0.872 | 49.74 / 387.56 | 49.63 / 420.04 |
| ss −40 °C | 1.115 / 0.447 | 1.1195 / 0.4493 | 1.31 | no result | 48.38 / 364.58 | 48.26 / 398.39 |
| ff 125 °C | 1.299 / 0.571 | 1.3234 / 0.5727 | 6.49 | 6.11 | 49.40 / 395.62 | 49.31 / 423.31 |
| fs 125 °C | 1.366 / 0.576 | 1.3786 / 0.5775 | 3.37 | 3.12 | 49.23 / 392.13 | 49.13 / 418.78 |
| sf −40 °C | 1.138 / 0.444 | 1.1412 / 0.4459 | 1.11 | no result | 48.61 / 369.44 | 48.48 / 404.97 |

The ring-current difference of about +33 µA is the pad view, not the slot extraction: KLayout pads in the data sheet,
PEX pads here, and `prev` already shows it (420.00 µA at tt). The error differences against the data sheet are
likewise mostly the pad view (`../dc_curves`).

## 4. Convergence aids and runs without a result

- Every run uses `.option gmin=1e-12 rshunt=1e12`. The transients use `method=gear`, and enable / power-up also use
  `cshunt=1e-15`. KLU is the solver. No `.nodeset` or `.ic` is used, and power-up uses `uic` from 0 V.
- On failure, `sim.py` retries automatically. The retries and their outcome are in each log and in `batch.log`:
  1. SPARSE instead of KLU. This was needed by: prev op at tt / ss / ff (the disabled operating point does not
     converge with KLU); prev enable at tt / ss / ff; c op and ac at sf −40 °C; c opi at ss −40 °C; c modes mon /
     ext; and hyb op at tt / ff.
  2. SPARSE plus `gminsteps=100 srcsteps=100 itl1=1000 itl6=1000`. It rescued no run.
  3. For DC only, the sweep split at 0.5 V. It rescued no run.
- The `cs` check (c with SPARSE instead of KLU, tt 27 °C, op and ac) agrees with c to ≤ 2·10⁻⁵ dB in gain, the
  same f−3dB to 4 digits, and the same operating point to 0.01 mV.
- **No result** (10 runs, all at −40 °C except power-up):
  - c ss −40 °C: dc and step unloaded.
  - c sf −40 °C: dc.
  - cc sf −40 °C: ac.
  - rc ss −40 °C: ac, dc and both steps (only its op converged).
  - **Power-up from 0 V** (supply ramp in 10 µs, `uic`) for c and for prev. Both stop at t = 2.78 µs (supply about
    0.92 V): prev with "timestep too small" at node `xs.en_b`, c stalled for 60 min. This is the deck with the PEX
    pads, not the slot extraction, since prev fails the same way. The enable transient from the disabled operating
    point replaces it (§3.1, §3.2).
  - Every −40 °C failure stops in the S2D pad's antenna diode `d.x2s.x43` (`dparea` / `dpcorner` instance, "timestep
    too small"). This is the same place as the cold aborts in `../slot_modes_bg` and the `darea` step in
    `../klayout_pad_diodes`. The other runs at the same PVT points converged (c ss −40 °C op, ac, 100 pF step,
    enable; c sf −40 °C ac and steps), so these are solver failures, not a different circuit state. They were not
    pursued further.

## 5. Verdicts

1. **LVS:** the whole-slot magic extraction matches `netlist/slot_7_netgen.spice`: 371 = 371 devices, 222 = 222 nets,
   0 property errors. The only pin messages are the known naming ones (comma ports, `vss_1v2_uq0`).
2. **Parasitics:** the slot has 2.16 pF (1.03 pF to substrate, 1.13 pF coupling, 0.16 pF on the floating art) and 9.4 k
   resistors on 169 nets. The analog signal and bias nets carry 10 … 52 fF and ≤ 125 Ω.
3. **Dynamic results:** the extracted slot costs 2.5 % bandwidth and adds 2.5 % settling time. With the pads'
   substrate capacitance included, the totals are 3.9 % and 4.5 %. Wire resistance adds nothing measurable. The
   round trip stays first-order: no peaking, overshoot ≤ 0.015 %.
4. **DC:** the round-trip transfer and error are unchanged (max \|err\| over 0 … 1 V within 0.003 mV with C, −0.16 …
   +0.03 mV with RC). The supply currents change by ≤ 0.3 %.
5. **The one material change is `vcm` / `vref`.** With the extracted `pad_ref_rb`, `vcm` is +3.5 … +4.9 mV at
   −40 / 27 °C and +13 / +24 mV at fs / ff 125 °C, and `vref` is +1.8 mV. This agrees with the `pad_ref_rb`
   schematic and PEX. **The earlier slot-level `vcm` / `vref` figures (tier-1 data sheet, `../dc_curves`,
   `../ac_tran`) carry the error of the KLayout-converted `pad_ref_rb` view and should be read as low by that
   amount.** The pad-in range's upper end moves up with `vcm`.
6. **Enable time** from the disabled state grows by 18 % at tt and by 32 % at ss −40 °C (1.96 → 2.59 µs to within
   1 mV) with the extracted slot. It is still below 3 µs.
7. **Earlier pad PEX:** the earlier pad PEX netlists (`sak-pex.sh`, hierarchical output) lack 0.44 pF (S2D) and
   0.66 pF (D2S) of substrate capacitance. Adding it costs a further 1.4 % of round-trip bandwidth. The `../d2s_pex`
   bandwidth and slew figures are therefore somewhat optimistic; that folder was not rerun here.
