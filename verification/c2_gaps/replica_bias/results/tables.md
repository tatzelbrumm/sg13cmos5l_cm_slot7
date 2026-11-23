<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
### pad_ref_rb: schematic vs magic C-coupled PEX (IHP sg13cmos5l simulation, CACE 2.11, ngspice-47)

Min .. max over the runs of each group; "max |PEX - sch|" = the largest difference of one run between the views
(runs matched by their conditions); "rerun vs committed" = the same for this schematic rerun against the CSV committed
in the design repository (2026-11-07).

| group | runs | quantity | committed schematic min .. max | PEX min .. max | max \|PEX - sch\| | rerun vs committed max \|diff\| |
|---|---|---|---|---|---|---|
| vcm_dc_params | 30 / 30 | Vcm [V] | 1.242 .. 1.395 | 1.242 .. 1.395 | 0.0001 V | 7e-05 V |
| vcm_dc_params | 30 / 30 | Vref [V] | 0.4374 .. 0.5964 | 0.4374 .. 0.5964 | 0 V | 0 V |
| vcm_dc_params | 30 / 30 | Ib [uA] | 18.99 .. 19.26 | 18.99 .. 19.26 | 0 uA | 0 uA |
| vcm_dc_3v0_params | 15 / 15 | Vcm [V] | 1.12 .. 1.193 | 1.12 .. 1.193 | 0 V | 0 V |
| vcm_dc_3v0_params | 15 / 15 | Vref [V] | 0.4363 .. 0.5941 | 0.4363 .. 0.5941 | 0 V | 0 V |
| vcm_dc_3v0_params | 15 / 15 | Ib [uA] | 18.93 .. 19.16 | 18.93 .. 19.16 | 0 uA | 0 uA |
| vref_room_params | 15 / 15 | Vcm [V] | 1.14 .. 1.365 | 1.14 .. 1.365 | 0 V | 0 V |
| vref_room_params | 15 / 15 | Vref [V] | 0.4832 .. 0.5038 | 0.4832 .. 0.5038 | 0 V | 0 V |
| vref_room_params | 15 / 15 | Ib [uA] | 19.01 .. 19.16 | 19.01 .. 19.16 | 0 uA | 0 uA |
| vref_hot_params | 15 / 15 | Vcm [V] | 1.178 .. 1.395 | 1.178 .. 1.395 | 0 V | 0 V |
| vref_hot_params | 15 / 15 | Vref [V] | 0.5724 .. 0.5964 | 0.5724 .. 0.5964 | 0 V | 0 V |
| vref_hot_params | 15 / 15 | Ib [uA] | 19.12 .. 19.26 | 19.12 .. 19.26 | 0 uA | 0 uA |
| vref_cold_params | 15 / 15 | Vcm [V] | 1.12 .. 1.352 | 1.12 .. 1.352 | 0.0001 V | 7e-05 V |
| vref_cold_params | 15 / 15 | Vref [V] | 0.4363 .. 0.4553 | 0.4363 .. 0.4553 | 0 V | 0 V |
| vref_cold_params | 15 / 15 | Ib [uA] | 18.93 .. 19.08 | 18.93 .. 19.08 | 0 uA | 0 uA |
| pd_params | 4 / 4 | Vcm [V] | 1.897e-09 .. 3.051e-07 | 1.897e-09 .. 3.051e-07 | 2.5e-12 V | 7e-13 V |
| pd_params | 4 / 4 | Vref [V] | 9.403e-08 .. 1.651e-05 | 9.401e-08 .. 1.651e-05 | 1.2e-10 V | 4e-11 V |
| pd_params | 4 / 4 | Ib [uA] | 7.060e-05 .. 9.877e-03 | 7.059e-05 .. 9.877e-03 | 9.9e-08 uA | 2.8e-08 uA |

### pad_ref_rb: local-mismatch Monte Carlo (IHP sg13cmos5l simulation, schematic, tt_mismatch, 27 C, 3.3 V, 100 runs)

| quantity | n | mean | sigma | min | max | mean - 3 sigma .. mean + 3 sigma |
|---|---|---|---|---|---|---|
| Vcm | 100 | 1260.86 mV | 5.415 mV | 1246.91 mV | 1273.95 mV | 1244.61 .. 1277.10 mV |
| Vref | 100 | 493.05 mV | 3.788 mV | 481.36 mV | 501.81 mV | 481.69 .. 504.42 mV |
| Ib | 100 | 19.06 uA | 0.148 uA | 18.76 uA | 19.42 uA | 18.61 .. 19.50 uA |

### bias_dist_pd: copy ratio I(iout<j>) / I(iin0) at 5 uA, all four outputs on, 3.3 V (IHP sg13cmos5l simulation)

View **schematic** (netlist/source/bias_dist_pd.spice + hv_logic.spice). Ratio min .. max over vc = 0.5 ... 2.5 V (41 points), all four outputs; spread = largest
|ratio(out j) - ratio(out k)| at one vc.

| corner | T [C] | ratio @ 0.5 V | ratio @ 1.0 V | ratio @ 2.5 V | min .. max (all outputs, 0.5 ... 2.5 V) | output spread |
|---|---|---|---|---|---|---|
| tt | -40 | 1.0138 | 1.0132 | 1.0093 | 1.0093 .. 1.0138 | 0.0e+00 |
| tt | 27 | 1.0129 | 1.0123 | 1.0082 | 1.0082 .. 1.0129 | 0.0e+00 |
| tt | 125 | 1.0118 | 1.0111 | 1.0066 | 1.0066 .. 1.0118 | 0.0e+00 |
| ss | -40 | 1.0121 | 1.0115 | 1.0076 | 1.0076 .. 1.0121 | 0.0e+00 |
| ss | 27 | 1.0113 | 1.0107 | 1.0066 | 1.0066 .. 1.0113 | 0.0e+00 |
| ss | 125 | 1.0104 | 1.0097 | 1.0050 | 1.0050 .. 1.0104 | 0.0e+00 |
| ff | -40 | 1.0156 | 1.0150 | 1.0112 | 1.0112 .. 1.0156 | 0.0e+00 |
| ff | 27 | 1.0146 | 1.0140 | 1.0100 | 1.0100 .. 1.0146 | 0.0e+00 |
| ff | 125 | 1.0133 | 1.0126 | 1.0082 | 1.0082 .. 1.0133 | 0.0e+00 |
| sf | -40 | 1.0136 | 1.0130 | 1.0092 | 1.0092 .. 1.0136 | 0.0e+00 |
| sf | 27 | 1.0127 | 1.0121 | 1.0081 | 1.0081 .. 1.0127 | 0.0e+00 |
| sf | 125 | 1.0116 | 1.0110 | 1.0065 | 1.0065 .. 1.0116 | 0.0e+00 |
| fs | -40 | 1.0140 | 1.0134 | 1.0095 | 1.0095 .. 1.0140 | 0.0e+00 |
| fs | 27 | 1.0130 | 1.0124 | 1.0083 | 1.0083 .. 1.0130 | 0.0e+00 |
| fs | 125 | 1.0119 | 1.0113 | 1.0066 | 1.0066 .. 1.0119 | 0.0e+00 |

All corners and temperatures (schematic): ratio 1.0050 .. 1.0156, i.e. copy error +0.50 % .. +1.56 %.

View **magic_pex_2** (magic C-coupled extraction of the bias_dist_pd cell of slot_7.gds). Ratio min .. max over vc = 0.5 ... 2.5 V (41 points), all four outputs; spread = largest
|ratio(out j) - ratio(out k)| at one vc.

| corner | T [C] | ratio @ 0.5 V | ratio @ 1.0 V | ratio @ 2.5 V | min .. max (all outputs, 0.5 ... 2.5 V) | output spread |
|---|---|---|---|---|---|---|
| tt | -40 | 1.0138 | 1.0132 | 1.0093 | 1.0093 .. 1.0138 | 0.0e+00 |
| tt | 27 | 1.0128 | 1.0123 | 1.0082 | 1.0082 .. 1.0128 | 0.0e+00 |
| tt | 125 | 1.0118 | 1.0112 | 1.0066 | 1.0066 .. 1.0118 | 0.0e+00 |
| ss | -40 | 1.0121 | 1.0115 | 1.0076 | 1.0076 .. 1.0121 | 0.0e+00 |
| ss | 27 | 1.0114 | 1.0107 | 1.0065 | 1.0065 .. 1.0114 | 0.0e+00 |
| ss | 125 | 1.0103 | 1.0098 | 1.0049 | 1.0049 .. 1.0103 | 0.0e+00 |
| ff | -40 | 1.0156 | 1.0150 | 1.0112 | 1.0112 .. 1.0156 | 0.0e+00 |
| ff | 27 | 1.0146 | 1.0140 | 1.0100 | 1.0100 .. 1.0146 | 0.0e+00 |
| ff | 125 | 1.0132 | 1.0126 | 1.0082 | 1.0082 .. 1.0132 | 0.0e+00 |
| sf | -40 | 1.0136 | 1.0130 | 1.0092 | 1.0092 .. 1.0136 | 0.0e+00 |
| sf | 27 | 1.0127 | 1.0120 | 1.0081 | 1.0081 .. 1.0127 | 0.0e+00 |
| sf | 125 | 1.0116 | 1.0110 | 1.0065 | 1.0065 .. 1.0116 | 0.0e+00 |
| fs | -40 | 1.0140 | 1.0134 | 1.0095 | 1.0095 .. 1.0140 | 0.0e+00 |
| fs | 27 | 1.0130 | 1.0123 | 1.0084 | 1.0084 .. 1.0130 | 0.0e+00 |
| fs | 125 | 1.0119 | 1.0113 | 1.0066 | 1.0066 .. 1.0119 | 0.0e+00 |

All corners and temperatures (magic_pex_2): ratio 1.0049 .. 1.0156, i.e. copy error +0.49 % .. +1.56 %.

### bias_dist_pd: leakage of the outputs (IHP sg13cmos5l simulation; |I(iout<j>)| max over the 4 outputs and vc = 0.5 ... 2.5 V)

| view | case | corner / T of the maximum | max \|I\| per output | at tt 27 C |
|---|---|---|---|---|
| schematic | en_3v3 = 0 (block off) | ff / 125 C | 25.9 pA | 0.0412 pA |
| schematic | en_3v3 = 1, en_out = 0, input on | ff / 125 C | 145 pA | 0.115 pA |
| magic_pex_2 | en_3v3 = 0 (block off) | ff / 125 C | 25.9 pA | 0.0412 pA |
| magic_pex_2 | en_3v3 = 1, en_out = 0, input on | ff / 125 C | 145 pA | 0.115 pA |

### bias_dist_pd: local-mismatch Monte Carlo of the copy ratio (IHP sg13cmos5l simulation, tt_mismatch, 27 C, 3.3 V, 100 runs)

mm_ok=1 added to every MOSFET (pex_for_sim.py --mm-ok); the source netlist of bias_dist_pd has no mm_ok, so this
MC is new. Ratio at vc = 1.0 V.

| view | output | mean | sigma | min | max |
|---|---|---|---|---|---|
| schematic | iout0 | 1.0131 | 0.0119 | 0.9829 | 1.0476 |
| schematic | iout1 | 1.0129 | 0.0115 | 0.9795 | 1.0458 |
| schematic | iout2 | 1.0127 | 0.0118 | 0.9831 | 1.0470 |
| schematic | iout3 | 1.0131 | 0.0120 | 0.9747 | 1.0453 |
| schematic | iout1 - iout2 (the pads' pair) | 0.0002 | 0.0036 | -0.0096 | 0.0099 |
| magic_pex_2 | iout0 | 1.0132 | 0.0102 | 0.9905 | 1.0349 |
| magic_pex_2 | iout1 | 1.0129 | 0.0104 | 0.9900 | 1.0363 |
| magic_pex_2 | iout2 | 1.0127 | 0.0106 | 0.9859 | 1.0402 |
| magic_pex_2 | iout3 | 1.0127 | 0.0103 | 0.9871 | 1.0392 |
| magic_pex_2 | iout1 - iout2 (the pads' pair) | 0.0002 | 0.0041 | -0.0094 | 0.0086 |

(n = 100 iterations per view)

