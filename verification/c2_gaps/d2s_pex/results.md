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
(e.g. INL[mV] 0.0074 = 7.4 mV, f3dB[MHz] 2.0e+06 = 2.0 MHz, SR[V/us] 1.9e+06 = 1.9 V/us). min / median / max are over
all runs of each view (N differs where PEX runs failed); "max per-run change" is the largest |PEX - sch| / |sch| in %
(sign kept) over runs with equal conditions. Pass-2 PEX runs carry ngspice rshunt = 1e12 Ohm on every node, the
schematic runs do not (see README.md: without it the PEX operating point did not converge).

## Status per group (pass 2 = rshunt 1e12)

| group | status |
|---|---|
| dc_params | pass 1 (no rshunt) done: 25 of 30 runs, see below; pass 2 (rshunt) queued last |
| ac_params | done: 15 of 15 schematic runs have a PEX result |
| ac_load_params | running / TBD |
| tran_params | running / TBD |
| noise_params | running / TBD |
| drive_params | running / TBD |
| enable_params | running / TBD |
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

