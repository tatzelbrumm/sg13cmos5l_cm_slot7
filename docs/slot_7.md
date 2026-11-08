<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# slot_7: slot 7 with the custom pads (tier 1, 2026-11-08, in progress)

The slot-7 circuit for the hand-over: harness enable and dig_in0..5 -> `s7_ctrl` (master enable, mode decode, switch
matrix) -> bandgap core -> `bias_dist_pd` -> `pad_ref_rb` and both custom pads; S2D -> D2S loop direct or swapped, the
S2D outputs on analog_bus0/1 or the D2S fed from them, vcm / vref on analog_bus2/3 (monitored, or fed with pad_ref_rb
disconnected). Concept and simulation: `docs/slot7_hookup/` (CONCEPT.md, tier1/).

| dig_in | function (only with the key dig_in3 = 1, dig_in4 = 0; otherwise the default) |
|---|---|
| 0 swap | loop S2D -> D2S crossed (polarity flip) |
| 1 mon | S2D outp / outn -> analog_bus0 / 1 (loop stays on) |
| 2 feed | analog_bus0 / 1 -> D2S vinp / vinn, loop off (wins over swap and mon) |
| 5 ext | pad_ref_rb disconnected; the pads take vcm / vref from analog_bus2 / 3 |

Default (enable = 1, any dig_in without the key): bandgap reference, replica bias on, loop direct, analog_bus0/1
disconnected, vcm / vref on analog_bus2 / 3 (close the harness's bus switches, reg 0x51 bits 6 / 7, to read them).

Files: `netlist/source/slot_7.spice` (s7_ctrl, slot_7; source of truth); sheets `schematic/xschem/{s7_ctrl,slot_7}.sch`;
layout `layout/klayout/slot_7.klay.gds` (v3 = agent A's v2 of 17:42 UTC with the bandgap's cell `pnpMPA` renamed `bgc_pnpMPA`
and written without KLayout's context cell, both for magic / netgen; geometry XOR 0 against v2: bg_core_pd (330, 152.7), bias_dist_pd
(385, 183.1), pad_ref_rb (450, 150), s7_ctrl (452, 60), s7_doutpd (8, 60) µm; M1 / M2 stubs, M3 horizontal, M4
vertical, TopMetal1 straps for vdd_3v3 / vss_3v3; DRC clean incl. the maximal deck with latch-up rules; LVS
`--run_mode=deep` match with 0 port mismatches, 497 devices; pins that share one net are one CDL port named with the
comma list of their labels, as KLayout names such a net) and `layout/klayout/s7_ctrl.klay.gds` (DRC / LVS clean).
dig_out[11:0] are held low by `s7_doutpd` (as the fallback did; back-annotated into the source netlist and the sheets,
`s7_doutpd.sch/.sym`). Routes over the analog blocks (from agent A's build log, `layout/klayout/slot_7_routes.png`): only `en`, `en_b` and
`s7_an_0_iref` cross pad_ref_rb (Metal3, all DC), only the supply straps cross bias_dist_pd; the long dig_in / enable /
analog_bus lines end at s7_ctrl. No shield needed. S2D enable kick through the ext switches (tt, 27 °C): vcm +118 / −63 mV,
vref +85 / −62 mV (shorted: +107 / −58, +81 / −54 mV), so pad_ref_rb's bypass capacitors still work through them. Check summary: `layout/klayout/slot_7_checks.txt`.

## LVS netlists

- `layout/klayout/slot_7.cdl`: complete (slot_7 and all subcircuits), KLayout `run_lvs.py --run_mode=deep` → match, 497
  devices, 0 port mismatches (pins on one net are one port named with KLayout's comma list).
- `layout/klayout/slot_7_netgen.spice`: the same with X cards for magic + netgen, and the unused harness pins as ports;
  `layout/klayout/netgen_check.sh` extracts with magic and runs netgen: 5 subcircuits match uniquely, the top matches
  with one port error, `vss_1v2_uq0` (the frame's second vss_1v2 strip, unconnected inside the slot, joined by the harness).
- `netlist/source/slot_7.spice` is the source of the slot's own levels (s7_ctrl, s7_doutpd, slot_7); its blocks are
  defined in their macros, so use the two files above for LVS.
