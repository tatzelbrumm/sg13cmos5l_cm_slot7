<!-- SPDX-FileCopyrightText: 2026 Christoph Maier -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# sg13cmos5l_IOPadDiff2Single: schematic vs post-layout (magic PEX) CACE results

**IHP sg13cmos5l post-layout (magic PEX) simulation** of the taped-out cell
(`pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds`), magic C-coupled extraction, compared with the
committed schematic results. Method and caveats: [README.md](README.md).

Sources of the numbers:
- schematic: design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single commit
  91a7da8b67ac56a26c605501146667a1fde28c32,
  `macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single/<group>.csv`
- PEX: `csv/<group>_pex_rshunt1e12.csv` (pass 2) and `csv/dc_params_pex_norshunt.csv` (pass 1) in this folder,
  from run.sh in this task (CACE 2.11.0, ngspice-47).

Values are SI (V, A, Hz, s, V/s, Ohm, dB) as cace_to_csv.py writes them, whatever the [unit] label of the column says
(e.g. INL[mV] 0.0074 = 7.4 mV, f3dB[MHz] 2.0e+06 = 2.0 MHz, SR[V/us] 1.9e+06 = 1.9 V/us, Overshoot[%] 0.08 = 8 %). min / median / max are over
all runs of each view (N differs where PEX runs failed); "max per-run change" is the largest |PEX - sch| / |sch| in %
(sign kept) over runs with equal conditions. Pass-2 PEX runs carry ngspice rshunt = 1e12 Ohm on every node, the
schematic runs do not (see README.md: without it the PEX operating point did not converge).

## Status per group (pass 2 = rshunt 1e12)

| group | status |
|---|---|
| dc_params | pass 1 (no rshunt) done: 25 of 30 runs, see below; pass 2 (rshunt) queued last |
| ac_params | done: 15 of 15 schematic runs have a PEX result |
| ac_load_params | done: 6 of 6 schematic runs have a PEX result |
| tran_params | done: 9 of 9 schematic runs have a PEX result |
| noise_params | done: 3 of 3 schematic runs have a PEX result |
| drive_params | done: 10 of 10 schematic runs have a PEX result |
| enable_params | done: 3 of 3 schematic runs have a PEX result |
| pd_params | running / TBD |
| thd_params | running / TBD |

## Schematic vs PEX (pass 2, rshunt 1e12)

| group | quantity | N sch | sch min | sch median | sch max | N pex | pex min | pex median | pex max | max per-run change % |
|---|---|---|---|---|---|---|---|---|---|---|
| ac_params | Acl_dB[dB] | 15 | -6.055 | -6.022 | -6.021 | 15 | -6.05 | -6.021 | -6.021 | +0.0801 |
| ac_params | f3dB[MHz] | 15 | 1.778e+06 | 2.015e+06 | 2.252e+06 | 15 | 1.569e+06 | 1.774e+06 | 2.016e+06 | -12.9 |
| ac_params | Peak_dB[dB] | 15 | 3.027e-07 | 9.28e-07 | 1.532e-06 | 15 | 4.475e-07 | 1.224e-06 | 1.815e-06 | +107 |
| ac_params | PSRR_1k[dB] | 15 | 70.66 | 71.56 | 72.53 | 15 | 70.04 | 70.93 | 71.91 | -1 |
| ac_params | PSRR_100k[dB] | 15 | 30.74 | 31.62 | 32.55 | 15 | 30.1 | 31.06 | 31.93 | -2.26 |
| ac_params | CMRR_1k[dB] | 15 | 93.79 | 124 | 127.5 | 15 | 95.13 | 109 | 110.3 | -14.5 |
| ac_params | Zout_1k[Ω] | 15 | 0.1951 | 0.2176 | 3.85 | 15 | 0.2083 | 0.2278 | 3.304 | -17.1 |
| ac_params | Zout_1M[Ω] | 15 | 159 | 171.7 | 206.1 | 15 | 166 | 181.3 | 216.9 | +6.64 |
| ac_load_params | Acl_dB[] | 6 | -6.022 | -6.021 | -6.021 | 6 | -6.021 | -6.021 | -6.021 | +0.00133 |
| ac_load_params | f3dB[MHz] | 6 | 1.582e+06 | 2.162e+06 | 3.006e+06 | 6 | 1.425e+06 | 1.961e+06 | 2.713e+06 | -11.6 |
| ac_load_params | Peak_dB[dB] | 6 | 3.682e-07 | 0.0265 | 2.899 | 6 | 7.193e-08 | 1.537e-06 | 2.466 | +188 |
| ac_load_params | PSRR_1k[] | 6 | 71.56 | 71.56 | 71.56 | 6 | 70.93 | 70.93 | 70.93 | -0.877 |
| ac_load_params | PSRR_100k[] | 6 | 31.59 | 31.62 | 31.63 | 6 | 30.95 | 30.98 | 31 | -2.03 |
| ac_load_params | CMRR_1k[] | 6 | 124 | 124 | 124 | 6 | 110.2 | 110.2 | 110.2 | -11.1 |
| ac_load_params | Zout_1k[] | 6 | 0.2176 | 0.2176 | 0.2176 | 6 | 0.2278 | 0.2278 | 0.2278 | +4.72 |
| ac_load_params | Zout_1M[] | 6 | 159 | 180.8 | 237 | 6 | 167.7 | 193.2 | 255.7 | +7.91 |
| tran_params | SR_rise[V/us] | 9 | 1.76e+06 | 2.448e+06 | 3.054e+06 | 9 | 1.591e+06 | 2.151e+06 | 2.732e+06 | -12.5 |
| tran_params | SR_fall[V/us] | 9 | 1.781e+06 | 2.466e+06 | 3.166e+06 | 9 | 1.603e+06 | 2.15e+06 | 2.794e+06 | -13.3 |
| tran_params | Overshoot[%] | 9 | -7e-07 | 1e-06 | 0.09321 | 9 | -9e-07 | 0 | 0.07986 | -100 |
| tran_params | ts_rise[us] | 9 | 2.959e-07 | 4.562e-07 | 6.892e-07 | 9 | 3.549e-07 | 5.057e-07 | 5.478e-07 | -23.5 |
| tran_params | ts_fall[us] | 9 | 3.036e-07 | 4.532e-07 | 6.165e-07 | 9 | 3.624e-07 | 5.038e-07 | 5.336e-07 | +19.4 |
| noise_params | En_1k[nV/rtHz] | 3 | 6.076e-07 | 6.817e-07 | 7.185e-07 | 3 | 6.05e-07 | 6.787e-07 | 7.153e-07 | -0.452 |
| noise_params | En_100k[nV/rtHz] | 3 | 1.426e-07 | 1.525e-07 | 1.564e-07 | 3 | 1.421e-07 | 1.519e-07 | 1.557e-07 | -0.474 |
| noise_params | Vn_int[uV] | 3 | 0.0002227 | 0.0002342 | 0.0002351 | 3 | 0.000214 | 0.0002239 | 0.0002242 | -4.64 |
| drive_params | Vout_max[V] | 10 | 3.266 | 3.275 | 3.283 | 10 | 3.266 | 3.275 | 3.283 | +0.00153 |
| drive_params | Vout_min[V] | 10 | 0.6396 | 0.6865 | 0.7386 | 10 | 0.6354 | 0.6823 | 0.736 | -0.646 |
| drive_params | Isc_src[mA] | 10 | 0.04965 | 0.06698 | 0.09321 | 10 | 0.04971 | 0.06705 | 0.09331 | +0.133 |
| drive_params | Isc_snk[mA] | 10 | 0.05303 | 0.08036 | 0.1203 | 10 | 0.05477 | 0.08297 | 0.1242 | +3.28 |
| enable_params | t_on[us] | 3 | 8.054e-07 | 8.544e-07 | 1.228e-06 | 3 | 1.109e-06 | 1.349e-06 | 2.387e-06 | +94.4 |
| enable_params | Glitch_max[mV] | 3 | 0.1119 | 0.1171 | 0.2244 | 3 | 0.1278 | 0.1287 | 0.2281 | +14.1 |
| enable_params | Glitch_min[mV] | 3 | -0.1874 | -0.1196 | -0.1078 | 3 | -0.2248 | -0.1325 | -0.1283 | -20 |
| enable_params | Iio_end[A] | 3 | 0.0002987 | 0.0003063 | 0.0003091 | 3 | 0.0003084 | 0.0003157 | 0.0003158 | +3.27 |

## PEX (pass 2) against the yaml limits (proposals, see the yaml header)

scripts/cace/spec_table.py of the design repository commit 91a7da8b on csv/*_pex_rshunt1e12.csv; worst case in display units.

| group | quantity | unit | limit | worst | runs | verdict |
|---|---|---|---:|---:|---:|---|
| ac_params | Closed-loop gain | dB | >= -6.2 | -6.05 | 15 | pass |
| ac_params | Closed-loop gain | dB | <= -5.85 | -6.021 | 15 | pass |
| ac_params | Bandwidth | MHz | >= 1 | 1.569 | 15 | pass |
| ac_params | Gain peaking | dB | <= 1 | 1.815e-06 | 15 | pass |
| ac_params | PSRR iovdd 1 kHz | dB | >= 60 | 70.04 | 15 | pass |
| ac_params | PSRR iovdd 100 kHz | dB | >= 25 | 30.1 | 15 | pass |
| ac_params | CMRR 1 kHz | dB | >= 70 | 95.13 | 15 | pass |
| ac_params | Output impedance 1 kHz | Ω | <= 10 | 3.304 | 15 | pass |
| ac_params | Output impedance 1 MHz | Ω | <= 300 | 216.9 | 15 | pass |
| ac_load_params | Bandwidth | MHz | >= 1 | 1.425 | 6 | pass |
| ac_load_params | Gain peaking | dB | <= 4 | 2.466 | 6 | pass |
| tran_params | Slew rate, rising | V/us | >= 1 | 1.591 | 9 | pass |
| tran_params | Slew rate, falling | V/us | >= 1 | 1.603 | 9 | pass |
| tran_params | Overshoot | % | <= 15 | 7.986 | 9 | pass |
| tran_params | Settling time, rising | us | <= 1 | 0.5478 | 9 | pass |
| tran_params | Settling time, falling | us | <= 1 | 0.5336 | 9 | pass |
| noise_params | Output noise 1 kHz | nV/rtHz | <= 1000 | 715.3 | 3 | pass |
| noise_params | Output noise 100 kHz | nV/rtHz | <= 200 | 155.7 | 3 | pass |
| noise_params | Integrated output noise | uV | <= 300 | 224.2 | 3 | pass |
| drive_params | Max output | V | >= 3.0 | 3.266 | 10 | pass |
| drive_params | Min output | V | <= 0.9 | 0.736 | 10 | pass |
| drive_params | Short-circuit source current | mA | >= 20 | 49.71 | 10 | pass |
| drive_params | Short-circuit sink current | mA | >= 20 | 54.77 | 10 | pass |
| enable_params | Turn-on time | us | <= 5 | 2.387 | 3 | pass |
| enable_params | Enable glitch, positive | mV | <= 400 | 228.1 | 3 | pass |
| enable_params | Enable glitch, negative | mV | >= -400 | -224.8 | 3 | pass |
| enable_params | IO ring current after start-up | uA | >= 200 | 308.4 | 3 | pass |
| enable_params | IO ring current after start-up | uA | <= 400 | 315.8 | 3 | pass |


## dc_params pass 1 (templates unchanged, no rshunt)

25 of 30 runs; 5 PEX runs failed (DC sweep did not converge, measurements empty): corner_mos/temp/vdd =
sf/-40/3.3, ff/-40/3.3, sf/-40/3.6, ff/-40/3.6, ff/27/3.6. Schematic: all 30 runs.

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

## Plots

- plots/f3dB_per_corner.png: closed-loop -3 dB bandwidth per corner_mos/temp (ac_params, pass 2)
- plots/inl_per_corner.png: INL per corner_mos/temp/vdd (dc_params; pass 2 once it has run, else pass 1)
- plots/iqp_per_corner.png: quiescent current of the output PMOS (dc_params; PEX = sum over the 82 extracted fingers)

