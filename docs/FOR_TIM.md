<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 with the custom S2D / D2S pads: notes for the harness (2026-11-08)

Slot 7 (`slot_7.gds`, 537.15 × 273 µm) drives the two custom pads `sg13cmos5l_IOPadSingle2Diff` (s7_an_0) and
`sg13cmos5l_IOPadDiff2Single` (s7_an_1) through the 13 core-side nets of the custom-io route (s7_an_0_vref, _outp,
_outn, _vcm, _en_3v3, _en_3v3_b, _iref; s7_an_1_vinp, _vinn, _vref, _iref, _en_3v3_b, _en_3v3). The pad cells are
unchanged from the earlier hand-over (`pads/`).

## What is in the slot

- On-slot bandgap reference → bias distribution → replica bias (vcm for both pads, vref for the S2D) and the pads'
  5 µA reference currents.
- A switch matrix: S2D → D2S loop (direct or swapped), S2D outputs onto analog_bus0/1, or the D2S fed from
  analog_bus0/1; vcm / vref on analog_bus2/3 (monitor, or fed from outside with the replica bias disconnected).
- Fail-safe enables without a 1.2 V supply: the slot works with only its `vdd_3v3` switched on; disabled, it draws
  leakage only, and the pads draw leakage only from the pad ring (≤ 67 nA at 125 °C) while the slot's supplies are off.
- `dig_out[11:0]` held low by NMOS (gate `vdd_1v2`), as in the earlier slot 7.

## Harness settings

| what | setting |
|---|---|
| select slot 7 | proj_sel = 7 |
| supplies | power_3v3_ena on (power_1v2_ena only for the dig_out pull-downs) |
| enable | proj_ena on → default mode |
| dig_in | route all dig_in registers to constant 0 first (0x0D); then set bits through 0x0D / 0x0E as needed |
| buses | analog_ena[k] for the buses you measure |

## Modes (dig_in bits act only with the key dig_in[3] = 1, dig_in[4] = 0; otherwise the default)

| dig_in | effect |
|---|---|
| none / no key (default) | loop S2D → D2S direct; analog_bus0/1 disconnected; vcm on analog_bus2, vref on analog_bus3 |
| [0] swap | loop crossed (polarity flip) |
| [1] mon | S2D outp / outn → analog_bus0 / 1 (loop stays on; slows the loop while the bus switches are closed) |
| [2] feed | analog_bus0 / 1 → D2S vinp / vinn, loop off (wins over swap and mon); drive around vcm |
| [5] ext | replica bias disconnected; drive vcm on analog_bus2 and the S2D vref on analog_bus3 |

## What to expect (simulation, extracted pads, tt 27 °C unless noted)

- vcm ≈ 1.26 V (1.12–1.37 V over corners), vref ≈ 0.49 V (0.44–0.58 V); read them with a high-impedance voltmeter.
- Default loop: D2S pad out = vcm + (S2D pad in − vref), error ≤ 1.3 mV (−40 / 27 °C), ≤ 6.5 mV (125 °C) for pad in
  0 … 1 V. Swap: vcm − (in − vref).
- Current, enabled: slot vdd_3v3 ≈ 49 µA, pad ring ≈ 365–396 µA (mostly the D2S output stage).

## Verification

DRC clean (`run_drc.py --no_density`; maximal deck with latch-up rules). LVS `run_lvs.py --run_mode=deep
--disable_tap_extraction` against `slot_7.cdl`: match, 497 devices, 0 port mismatches (pins that share one net are one
port named with KLayout's comma list, e.g. `analog_bus2,s7_an_0_vcm,s7_an_1_vref`; flat LVS needs
`--ignore_top_ports_mismatch` because the blocks' own labels join the net names). magic + netgen: `netlist/slot_7_netgen.spice`
(X cards, unused harness pins as ports; `netlist/netgen_check.sh`): all blocks match uniquely; the only top-level pin
error is `vss_1v2_uq0`, the frame's second vss_1v2 strip, unconnected inside the slot. Use `slot_7.cdl` /
`slot_7_netgen.spice` for LVS (`slot_7.spice` holds only the slot's own levels). Not done: PEX of the whole slot, fill.

Contact: Christoph Maier. Design sources: `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`, branch
`claude/c4-replica-bias`, `macros/slot_7/`.
