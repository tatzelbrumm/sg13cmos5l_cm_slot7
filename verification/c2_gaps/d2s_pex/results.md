<!-- SPDX-FileCopyrightText: 2026 Christoph Maier -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# sg13cmos5l_IOPadDiff2Single: schematic vs post-layout (magic PEX) CACE results

**IHP sg13cmos5l post-layout (magic PEX) simulation** of the taped-out cell (pads/sg13cmos5l_IOPadDiff2Single/*.gds),
magic C-coupled extraction, compared with the committed schematic results.

Sources of the numbers:
- schematic: design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single commit 91a7da8b67ac56a26c605501146667a1fde28c32,
  macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single/<group>.csv
- PEX: csv/<group>_pex.csv in this folder, from run.sh in this task (CACE 2.11.0, ngspice-47).

Values are SI (V, A, Hz, s) as cace_to_csv.py writes them, whatever the [unit] label of the column says
(e.g. INL[mV] 0.0074 = 7.4 mV, f3dB[MHz] 2.0E+06 = 2.0 MHz). min / median / max are over all runs of each view
(N differs where PEX runs failed); "max per-run change" compares runs with the same conditions only.

## Status per group

| group | status |
|---|---|
| dc_params | done: 25 of 30 runs; 5 PEX runs failed (DC sweep did not converge): sf/-40 C/3.3 V, ff/-40/3.3, sf/-40/3.6, ff/-40/3.6, ff/27/3.6 |
| ac_params | running / TBD: first attempt, every run's operating point failed to converge on the PEX netlist (see README) |
| ac_load_params, tran_params, noise_params, drive_params, enable_params, pd_params, thd_params | TBD (queued behind the op convergence fix) |

## dc_params

| group | quantity | N sch | sch min | sch median | sch max | N pex | pex min | pex median | pex max | max per-run change % |
|---|---|---|---|---|---|---|---|---|---|---|
| dc_params | Gain[] | 30 | 0.4981 | 0.5 | 0.5 | 25 | 0.4983 | 0.5 | 0.5 | +0.0544 |
| dc_params | Vos_out[mV] | 30 | 3.487e-05 | 7.344e-05 | 0.001947 | 25 | 3.202e-05 | 7.024e-05 | 0.001737 | -13 |
| dc_params | INL[mV] | 30 | 0.0001222 | 0.0004804 | 0.007404 | 25 | 0.0001209 | 0.0004867 | 0.0075 | -8.64 |
| dc_params | Iio[A] | 30 | 0.0002932 | 0.0003017 | 0.000314 | 25 | 0.0003017 | 0.0003107 | 0.0003198 | +3.54 |
| dc_params | Icore[A] | 30 | 8.253e-12 | 1.185e-10 | 2.389e-08 | 25 | 8.253e-12 | 2.435e-10 | 2.389e-08 | -0.000242 |
| dc_params | IqP[A] | 30 | 0.0002074 | 0.0002154 | 0.0002266 | 25 | 0.0002166 | 0.000225 | 0.0002335 | +5.32 |
| dc_params | IqN[A] | 30 | 0.000207 | 0.0002146 | 0.0002265 | 25 | 0.0002162 | 0.0002244 | 0.0002335 | +5.32 |
| dc_params | Imin[A] | 30 | 9.577e-05 | 0.0001051 | 0.0001119 | 25 | 0.0001047 | 0.0001125 | 0.0001184 | +9.3 |

Plots: plots/inl_per_corner.png, plots/iqp_per_corner.png (IqP = total current of the 82 extracted OP fingers,
read through a 0 V sense, see README).
