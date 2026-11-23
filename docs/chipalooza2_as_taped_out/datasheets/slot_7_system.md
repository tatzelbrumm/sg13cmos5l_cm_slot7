<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# slot_7 as a whole (taped-out circuit): tier-1 simulation data sheet

> **Scope.** This is the only characterization of the **slot circuit as a system** and not a CACE suite: the designer's tier-1 simulation
> of the slot-7 netlist with the two custom pads and the replica bias, from the design repository at `9052bd35` (v3, the version the delivery cites; the delivery states v3 has the same geometry as the v2 these runs
> were started on, with renamed bandgap cells, and the taped-out `slot_7.gds` is v3 plus the tughra art, which has no devices or pins).
> Blocks with a layout were simulated **from their extracted layout netlists** (both pads, `pad_ref_rb`, `bias_dist_pd`); `bg_core_pd` from its schematic netlist; `ls_up_fs` from its source netlist
> (it had no layout at the time of the run). The slot's `s7_ctrl` glue was simulated in the mode runs. Slot `vdd_3v3` and pad-ring `iovdd` both 3.3 V (3.0 / 3.6 V at the corners), harness enable 1.2 V, S2D input swept 0 … 1.0 V, D2S output unloaded (1 GΩ);
> expected D2S out = `vcm` + (in − `vref`). Source files: [`docs/slot7_hookup/tier1/results.txt`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/docs/slot7_hookup/tier1/results.txt), [`modes.txt`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/blob/9052bd35928c6d40344e8e686c9abbe736bfadb9/docs/slot7_hookup/tier1/modes.txt), scripts `run_tier1.py`, `run_modes.py` in the same folder.
> **No simulation was run for this page;** the two files are copied verbatim below.

## 1. Corner table (`results.txt`)

Columns: corner, temperature [°C], supply [V]; `vcm` and `vref` [V]; maximum round-trip error over pad input 0 … 1 V [mV]; `I(slot vdd_3v3)` and `I(ring iovdd)` enabled [µA]; the same two currents [nA] 150–170 µs after the enable falls (transient).

```
# slot7_tier1 with both pads (extracted), pad_ref_rb and bias_dist_pd (extracted), bg_core_pd, ls_up_fs
# corner  T  V  | vcm vref [V] | round-trip error max over pad_in 0..1 V [mV] | I slot vdd_3v3, I ring iovdd [uA] enabled | same [nA], 150-170 us after enable falls (transient)
tt   27 3.3  | 1.257 0.492 |    0.90 |  49.74 387.56 |    31.63    12.24
ss  -40 3.0  | 1.115 0.447 |    1.31 |  48.38 364.58 |    25.36     9.01
ff  125 3.6  | 1.299 0.571 |    6.49 |  49.40 395.62 |    56.20    58.22
fs  125 3.6  | 1.366 0.576 |    3.37 |  49.23 392.13 |    48.64    32.10
sf  -40 3.0  | 1.138 0.444 |    1.11 |  48.61 369.44 |    25.55     9.09
```

| quantity | value over the five corners |
|---|---|
| `vcm` | 1.115 … 1.366 V (tt 27 °C 1.257 V) |
| `vref` | 0.444 … 0.576 V (tt 27 °C 0.492 V) |
| round-trip error, max over 0 … 1 V input | 0.90 … 6.49 mV |
| slot `vdd_3v3` current, enabled | 48.4 … 49.7 µA |
| pad ring `iovdd` current, enabled | 364.6 … 395.6 µA |
| after the enable falls (150–170 µs) | slot 25 … 56 nA, ring 9 … 58 nA |

## 2. Modes (`modes.txt`)

Columns: mode, corner, temperature [°C]; maximum error [mV] against the expected output; for `mon` the differences `v(bus0) − v(outp)` and `v(bus1) − v(outn)` [mV]. `FAILED` = no DC result.

```
# mode       corner     | error max [mV] vs expected | v(bus0)-v(outp), v(bus1)-v(outn) [mV] (mon)
default     tt   27 |     0.90 |        -        -
swap        tt   27 |     0.99 |        -        -
mon         tt   27 |     0.94 |     0.01     0.01
feed        tt   27 |     0.05 |        -        -
ext         tt   27 |     0.91 |        -        -
all_high    tt   27 |     0.90 |        -        -
swap+feed   tt   27 |     0.05 |        -        -
no_key_swap tt   27 |     0.90 |        -        -
default     ss  -40 |     1.31 |        -        -
swap        ss  -40 | FAILED
mon         ss  -40 | FAILED
feed        ss  -40 | FAILED
ext         ss  -40 | FAILED
all_high    ss  -40 |     1.31 |        -        -
swap+feed   ss  -40 | FAILED
no_key_swap ss  -40 |     1.31 |        -        -
default     ff  125 |     6.50 |        -        -
swap        ff  125 |     2.88 |        -        -
mon         ff  125 |     6.55 |     0.01     0.01
feed        ff  125 |     2.22 |        -        -
ext         ff  125 |     6.39 |        -        -
all_high    ff  125 |     6.50 |        -        -
swap+feed   ff  125 |     2.22 |        -        -
no_key_swap ff  125 |     6.50 |        -        -
```

At ss −40 °C the manual modes did not converge in DC (default, all-high and no-key-swap do); the transient runs from power-up gave feed 0.24 mV and ext 0.04 mV, and swap / mon stall at the bandgap's start-up node
(design repository RUNLOG rows 121–122; see [glue_logic.md](../glue_logic.md) §7).

## 3. Not covered

Monte Carlo of the slot; PEX of the whole slot; the 3.0 / 3.6 V × all-corner mode grid (modes at tt 27 °C, ss −40 °C and ff 125 °C only); a CACE suite for the slot; silicon.
