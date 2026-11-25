<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Generated tables (analyze.py)

## Runs

| job | what | runs ok | supply [V] | solver aid |
|---|---|---|---|---|
| dc 1k | DC, enabled default mode, S2D pad swept | 32 | 3.0, 3.3, 3.6 | none, rshunt |
| dc 1kgnd | DC, enabled default mode, S2D pad swept | 32 | 3.0, 3.3, 3.6 | none |
| dc open | DC, enabled default mode, S2D pad swept | 31 | 3.0, 3.3, 3.6 | none |
| en | enable off / on edges | 10 | 3.3, 3.6 | none, step2n |
| fs | fail-safe: slot supplies 0, ring on, pads driven | 23 | 3.3, 3.6 | rshunt |
| fs0 | fail-safe: all supplies 0, pads driven | 30 | 3.3, 3.6 | rshunt |
| fst | fail-safe as fs, as a slow transient (pad ramp 0 ... supply in 50 us) | 10 | 3.3, 3.6 | none |
| mode | mode switching | 7 | 3.3, 3.6 | none, step2n |
| off | disabled (enable 0), pad ramped | 9 | 3.3, 3.6 | none |
| pu | power-up transient | 6 | 3.3, 3.6 | none, step2n |
| pu fast | power-up transient | 10 | 3.3, 3.6 | none, step2n |
| pu late | power-up transient | 2 | 3.3, 3.6 | none |
| step 100p | full-swing S2D pad steps | 10 | 3.3, 3.6 | none |
| step open | full-swing S2D pad steps | 10 | 3.3, 3.6 | none |

Failed runs (no result): 16

| run | last solver message |
|---|---|
| dc_ss_-40_3.0_open | doAnalyses: DC:  Timestep too small;  vin = -0.2: trouble with dparea-instance d.x2d.xlay.x_167.d1 |
| fs_ff_-40_3.3 | TIMEOUT after 120 s (killed) |
| fs_fs_-40_3.6 | doAnalyses: DC:  Timestep too small;  vin = 0.4: trouble with dparea-instance d.x2s.xlay.x_63.d1 |
| fs_sf_-40_3.6 | TIMEOUT after 120 s (killed) |
| fs_ss_-40_3.3 | doAnalyses: DC:  Timestep too small;  vin = 0: trouble with dparea-instance d.x2s.xlay.x_63.d1 |
| fs_ss_-40_3.6 | doAnalyses: DC:  Timestep too small;  vin = 0: trouble with dparea-instance d.x2s.xlay.x_63.d1 |
| fs_tt_-40_3.3 | TIMEOUT after 120 s (killed) |
| fs_tt_-40_3.6 | doAnalyses: DC:  Timestep too small;  vin = 0.1: trouble with dparea-instance d.x2s.xlay.x_63.d1 |
| mode_ff_-40_3.3 | TIMEOUT after 240 s (killed) |
| mode_ff_-40_3.6 | TIMEOUT after 240 s (killed) |
| mode_sf_-40_3.6 | TIMEOUT after 240 s (killed) |
| off_tt_27_3.3 | TIMEOUT after 240 s (killed) |
| pu_ff_125_3.6 | TIMEOUT after 240 s (killed) |
| pu_fs_125_3.6 | TIMEOUT after 150 s (killed) |
| pu_ss_125_3.3 | TIMEOUT after 150 s (killed) |
| pu_ss_125_3.6 | TIMEOUT after 240 s (killed) |

## Maximum per device type and gate length, all 3.3 V runs

| type | L [um] | L meets spec LG | devices | blocks | max \|VGS\| [V] | where (\|VGS\|) | max \|VGD\| [V] | max \|VDS\| [V] | where (\|VDS\|) | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | max \|VDS\| held >= 100 ns [V] | max \|VGB\| [V] | devices with \|VGS\| or \|VGD\| > 3.301 V | same, held >= 100 ns | same (peak), 27 C runs only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HV-NMOS | 0.45 | no | 134 | D2S pad, S2D pad, bg_core_pd, bias_dist_pd, pad_ref_rb, s7_ctrl logic, s7_ctrl ls_up_fs, s7_ctrl tg_hv switches, s7_doutpd | 3.875 | xs.xd.xlay.x_8.x_7 (off ff -40 C 3.3 V, t = 1.14 us) | 3.875 | 3.813 | xs.xd.xlay.x_6.x_7 (off ff -40 C 3.3 V, t = 1.14 us) | 3.714 | 3.300 | 3.485 | 86 | 5 | 85 |
| HV-NMOS | 0.6 | yes | 1 | S2D pad | 0.201 | x2s.xlay.x_43 (step open ss 125 C 3.3 V, t = 12.01 us) | 3.300 | 3.300 | x2s.xlay.x_43 (dc 1k ff -40 C 3.3 V, pad 3.30 V) | 3.300 | 3.300 | 0.089 | 0 | 0 | 0 |
| HV-NMOS | 1 | yes | 8 | D2S pad, bg_core_pd | 2.865 | x2d.xlay.x_169 (pu late tt 27 C 3.3 V, t = 20.54 us) | 3.415 | 3.307 | x2d.xlay.x_171 (en ff -40 C 3.3 V, t = 22.01 us) | 3.406 | 3.302 | 1.810 | 1 | 1 | 1 |
| HV-NMOS | 2 | yes | 1 | bg_core_pd | 1.879 | xs.xbg.xms3 (en ss 125 C 3.3 V, t = 22.48 us) | 3.242 | 3.222 | xs.xbg.xms3 (off ss 125 C 3.3 V, t = 70.00 us) | 3.221 | 3.221 | 1.879 | 0 | 0 | 0 |
| HV-NMOS | 3 | yes | 11 | D2S pad, S2D pad, pad_ref_rb | 2.675 | x2s.xlay.x_104 (pu fast ss 125 C 3.3 V, t = 1.73 us) | 3.163 | 3.308 | xs.xr.xlay.x_39 (en ss 125 C 3.3 V, t = 22.66 us) | 3.163 | 3.300 | 1.371 | 0 | 0 | 0 |
| HV-NMOS | 3.25 | yes | 1 | pad_ref_rb | 1.292 | xs.xr.xlay.x_10 (step 100p ss 125 C 3.3 V, t = 12.07 us) | 1.292 | 0.000 |  | 1.291 | 0.000 | 1.292 | 0 | 0 | 0 |
| HV-NMOS | 4 | yes | 3 | bg_core_pd | 0.968 | xs.xbg.xnb (dc 1k ss -40 C 3.3 V, pad -0.20 V) | 3.086 | 3.221 | xs.xbg.xnb (off ss 125 C 3.3 V, t = 70.00 us) | 3.086 | 3.221 | 1.773 | 0 | 0 | 0 |
| HV-NMOS | 6 | yes | 31 | D2S pad, S2D pad, bias_dist_pd, pad_ref_rb | 1.299 | xs.xd.xlay.x_10 (pu fast ff -40 C 3.3 V, t = 0.96 us) | 3.318 | 3.422 | x2d.xlay.x_209 (pu late tt 27 C 3.3 V, t = 20.48 us) | 3.300 | 3.398 | 1.299 | 2 | 0 | 2 |
| HV-NMOS | 8 | yes | 3 | D2S pad, S2D pad, pad_ref_rb | 1.371 | x2s.xlay.x_109 (step 100p ss 125 C 3.3 V, t = 12.04 us) | 0.000 | 1.371 | x2s.xlay.x_109 (step 100p ss 125 C 3.3 V, t = 12.04 us) | 1.312 | 1.312 | 1.371 | 0 | 0 | 0 |
| HV-NMOS | 12 | yes | 4 | S2D pad, pad_ref_rb | 2.912 | x2s.xlay.x_110 (dc 1k ss -40 C 3.3 V, pad 1.75 V) | 2.912 | 0.000 |  | 2.912 | 0.000 | 2.912 | 0 | 0 | 0 |
| HV-NMOS | 12.4 | yes | 1 | pad_ref_rb | 1.292 | xs.xr.xlay.x_9 (step 100p ss 125 C 3.3 V, t = 12.07 us) | 1.292 | 0.000 |  | 1.291 | 0.000 | 1.292 | 0 | 0 | 0 |
| HV-NMOS | 12.66 | yes | 1 | pad_ref_rb | 1.292 | xs.xr.xlay.x_7 (step 100p ss 125 C 3.3 V, t = 12.07 us) | 1.292 | 0.000 |  | 1.291 | 0.000 | 1.292 | 0 | 0 | 0 |
| HV-NMOS | 16.9 | yes | 1 | pad_ref_rb | 0.611 | xs.xr.xlay.x_45 (step 100p ss 125 C 3.3 V, t = 2.02 us) | 0.611 | 0.000 |  | 0.591 | 0.000 | 0.611 | 0 | 0 | 0 |
| HV-PMOS | 0.45 | no | 110 | D2S pad, S2D pad, bg_core_pd, bias_dist_pd, pad_ref_rb, s7_ctrl logic, s7_ctrl ls_up_fs, s7_ctrl tg_hv switches | 3.483 | xs.xc.xl5.xi3.xp (mode ss 125 C 3.3 V, t = 42.01 us) | 3.698 | 3.813 | xs.xd.xlay.x_6.x_8 (off ff -40 C 3.3 V, t = 1.14 us) | 3.682 | 3.300 | 3.363 | 106 | 12 | 104 |
| HV-PMOS | 0.6 | yes | 8 | D2S pad, S2D pad | 1.505 | x2d.xlay.x_234 (pu fast tt 27 C 3.3 V, t = 1.22 us) | 3.501 | 3.500 | x2s.xlay.x_3 (dc 1k ff -40 C 3.3 V, pad -0.20 V) | 3.500 | 3.500 | 2.050 | 3 | 3 | 3 |
| HV-PMOS | 1 | yes | 34 | D2S pad, S2D pad, bg_core_pd, pad_ref_rb | 3.195 | x2d.xlay.x_276 (fs fs 125 C 3.3 V, pad 3.30 V) | 3.279 | 3.113 | xs.xbg.xpac (off ss 125 C 3.3 V, t = 70.00 us) | 3.279 | 3.113 | 3.195 | 0 | 0 | 0 |
| HV-PMOS | 3 | yes | 5 | D2S pad, S2D pad | 1.192 | x2d.xlay.x_238 (step 100p ss 125 C 3.3 V, t = 12.18 us) | 2.996 | 3.265 | x2s.xlay.x_91 (en ff -40 C 3.3 V, t = 22.01 us) | 2.996 | 3.258 | 1.597 | 0 | 0 | 0 |
| HV-PMOS | 4 | yes | 15 | D2S pad, S2D pad, pad_ref_rb | 1.597 | x2d.xlay.x_242 (step 100p ss 125 C 3.3 V, t = 2.09 us) | 1.597 | 1.597 | x2d.xlay.x_243 (step 100p ss 125 C 3.3 V, t = 2.09 us) | 1.552 | 1.552 | 1.597 | 0 | 0 | 0 |
| HV-PMOS | 5 | yes | 7 | s7_ctrl ls_up_fs | 3.447 | xs.xc.xl0.xpf (mode ss 125 C 3.3 V, t = 42.00 us) | 3.343 | 3.344 | xs.xc.xl0.xpf (mode ss 125 C 3.3 V, t = 12.01 us) | 3.300 | 3.300 | 3.305 | 7 | 0 | 7 |
| HV-PMOS | 6 | yes | 40 | D2S pad, S2D pad, bias_dist_pd, pad_ref_rb | 1.417 | x2s.xlay.x_173 (pu fast ss 125 C 3.3 V, t = 2.17 us) | 3.345 | 3.845 | xs.xr.xlay.x_18 (en ss 125 C 3.3 V, t = 22.65 us) | 3.239 | 3.719 | 1.417 | 1 | 0 | 0 |
| HV-PMOS | 12.5 | yes | 8 | bg_core_pd | 3.312 | xs.xbg.xms1_0 (pu late tt 27 C 3.3 V, t = 20.07 us) | 7.278 | 10.013 | xs.xbg.xms1_0 (en ff -40 C 3.3 V, t = 22.01 us) | 3.300 | 3.955 | 3.312 | 2 | 0 | 2 |
| HV-PMOS | 20 | yes | 70 | s7_ctrl ls_up_fs | 3.300 | xs.xc.xl4.xpl1 (mode ss 125 C 3.3 V, t = 2.01 us) | 5.491 | 7.815 | xs.xc.xl0.xpl1 (pu fast ss 125 C 3.3 V, t = 0.88 us) | 3.300 | 3.272 | 3.300 | 12 | 0 | 12 |
| HV-PMOS | 32.16 | yes | 2 | D2S pad | 3.300 | x2d.xlay.x_2 (fs ff 125 C 3.3 V, pad 0.00 V) | 3.300 | 0.000 |  | 3.300 | 0.000 | 3.300 | 0 | 0 | 0 |

## Maximum per device type and gate length, all 3.6 V runs

| type | L [um] | L meets spec LG | devices | blocks | max \|VGS\| [V] | where (\|VGS\|) | max \|VGD\| [V] | max \|VDS\| [V] | where (\|VDS\|) | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | max \|VDS\| held >= 100 ns [V] | max \|VGB\| [V] | devices with \|VGS\| or \|VGD\| > 3.301 V | same, held >= 100 ns | same (peak), 27 C runs only |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HV-NMOS | 0.45 | no | 134 | D2S pad, S2D pad, bg_core_pd, bias_dist_pd, pad_ref_rb, s7_ctrl logic, s7_ctrl ls_up_fs, s7_ctrl tg_hv switches, s7_doutpd | 4.182 | xs.xd.xlay.x_8.x_7 (en ff -40 C 3.6 V, t = 2.11 us) | 4.182 | 4.346 | xs.xd.xlay.x_6.x_7 (en sf -40 C 3.6 V, t = 2.11 us) | 4.065 | 3.674 | 3.816 | 109 | 109 | 109 |
| HV-NMOS | 0.6 | yes | 1 | S2D pad | 0.201 | x2s.xlay.x_43 (step open fs 125 C 3.6 V, t = 12.01 us) | 3.600 | 3.600 | x2s.xlay.x_43 (dc 1k ff -40 C 3.6 V, pad 3.60 V) | 3.600 | 3.600 | 0.089 | 1 | 1 | 1 |
| HV-NMOS | 1 | yes | 8 | D2S pad, bg_core_pd | 3.144 | x2d.xlay.x_169 (pu late tt 27 C 3.6 V, t = 20.50 us) | 3.728 | 3.608 | x2d.xlay.x_171 (en ff -40 C 3.6 V, t = 22.01 us) | 3.719 | 3.602 | 1.816 | 3 | 3 | 3 |
| HV-NMOS | 2 | yes | 1 | bg_core_pd | 2.002 | xs.xbg.xms3 (en ss -40 C 3.6 V, t = 22.27 us) | 3.602 | 3.550 | xs.xbg.xms3 (off ff 125 C 3.6 V, t = 40.61 us) | 3.550 | 3.550 | 2.002 | 1 | 1 | 1 |
| HV-NMOS | 3 | yes | 11 | D2S pad, S2D pad, pad_ref_rb | 2.925 | x2s.xlay.x_104 (pu fast fs 125 C 3.6 V, t = 1.64 us) | 3.455 | 3.610 | xs.xr.xlay.x_39 (en ss 125 C 3.6 V, t = 22.61 us) | 3.455 | 3.600 | 1.363 | 4 | 4 | 4 |
| HV-NMOS | 3.25 | yes | 1 | pad_ref_rb | 1.390 | xs.xr.xlay.x_10 (step 100p ss 125 C 3.6 V, t = 12.07 us) | 1.390 | 0.000 |  | 1.388 | 0.000 | 1.390 | 0 | 0 | 0 |
| HV-NMOS | 4 | yes | 3 | bg_core_pd | 0.969 | xs.xbg.xnb (pu ss -40 C 3.6 V, t = 8.54 us) | 3.448 | 3.550 | xs.xbg.xnb (off ff 125 C 3.6 V, t = 40.62 us) | 3.448 | 3.550 | 1.776 | 1 | 1 | 0 |
| HV-NMOS | 6 | yes | 31 | D2S pad, S2D pad, bias_dist_pd, pad_ref_rb | 1.468 | xs.xd.xlay.x_10 (pu fast ss -40 C 3.6 V, t = 0.96 us) | 3.618 | 3.727 | x2d.xlay.x_209 (pu late tt 27 C 3.6 V, t = 20.44 us) | 3.600 | 3.706 | 1.468 | 8 | 8 | 7 |
| HV-NMOS | 8 | yes | 3 | D2S pad, S2D pad, pad_ref_rb | 1.363 | x2s.xlay.x_109 (step 100p ss 125 C 3.6 V, t = 12.04 us) | 0.000 | 1.363 | x2s.xlay.x_109 (step 100p ss 125 C 3.6 V, t = 12.04 us) | 1.309 | 1.309 | 1.363 | 0 | 0 | 0 |
| HV-NMOS | 12 | yes | 4 | S2D pad, pad_ref_rb | 2.430 | x2s.xlay.x_110 (dc 1k ss -40 C 3.6 V, pad 1.75 V) | 2.430 | 0.000 |  | 2.430 | 0.000 | 2.430 | 0 | 0 | 0 |
| HV-NMOS | 12.4 | yes | 1 | pad_ref_rb | 1.390 | xs.xr.xlay.x_9 (step 100p ss 125 C 3.6 V, t = 12.07 us) | 1.390 | 0.000 |  | 1.388 | 0.000 | 1.390 | 0 | 0 | 0 |
| HV-NMOS | 12.66 | yes | 1 | pad_ref_rb | 1.390 | xs.xr.xlay.x_7 (step 100p ss 125 C 3.6 V, t = 12.07 us) | 1.390 | 0.000 |  | 1.388 | 0.000 | 1.390 | 0 | 0 | 0 |
| HV-NMOS | 16.9 | yes | 1 | pad_ref_rb | 0.616 | xs.xr.xlay.x_45 (step 100p ss 125 C 3.6 V, t = 2.03 us) | 0.616 | 0.000 |  | 0.593 | 0.000 | 0.616 | 0 | 0 | 0 |
| HV-PMOS | 0.45 | no | 110 | D2S pad, S2D pad, bg_core_pd, bias_dist_pd, pad_ref_rb, s7_ctrl logic, s7_ctrl ls_up_fs, s7_ctrl tg_hv switches | 3.817 | xs.xc.xl5.xi3.xp (mode ss -40 C 3.6 V, t = 42.01 us) | 4.094 | 4.346 | xs.xd.xlay.x_6.x_8 (en sf -40 C 3.6 V, t = 2.11 us) | 4.082 | 3.674 | 3.710 | 109 | 106 | 109 |
| HV-PMOS | 0.6 | yes | 8 | D2S pad, S2D pad | 1.786 | x2d.xlay.x_234 (pu fast ss -40 C 3.6 V, t = 1.05 us) | 3.801 | 3.800 | x2s.xlay.x_3 (dc 1k ff -40 C 3.6 V, pad -0.20 V) | 3.800 | 3.800 | 2.068 | 4 | 4 | 4 |
| HV-PMOS | 1 | yes | 34 | D2S pad, S2D pad, bg_core_pd, pad_ref_rb | 3.490 | x2d.xlay.x_276 (fs fs 125 C 3.6 V, pad 3.60 V) | 3.578 | 3.468 | xs.xbg.xpac (off fs 125 C 3.6 V, t = 70.00 us) | 3.578 | 3.468 | 3.490 | 7 | 7 | 6 |
| HV-PMOS | 3 | yes | 5 | D2S pad, S2D pad | 1.206 | x2d.xlay.x_238 (step 100p ss -40 C 3.6 V, t = 12.16 us) | 3.283 | 3.569 | x2s.xlay.x_91 (en ss -40 C 3.6 V, t = 22.02 us) | 3.283 | 3.564 | 1.599 | 0 | 0 | 0 |
| HV-PMOS | 4 | yes | 15 | D2S pad, S2D pad, pad_ref_rb | 1.599 | x2d.xlay.x_242 (step 100p ss 125 C 3.6 V, t = 2.09 us) | 1.599 | 1.599 | x2d.xlay.x_243 (step 100p ss 125 C 3.6 V, t = 2.09 us) | 1.554 | 1.554 | 1.599 | 0 | 0 | 0 |
| HV-PMOS | 5 | yes | 7 | s7_ctrl ls_up_fs | 3.743 | xs.xc.xl0.xpf (mode ss 125 C 3.6 V, t = 42.00 us) | 3.630 | 3.630 | xs.xc.xl0.xpf (mode ss 125 C 3.6 V, t = 12.01 us) | 3.600 | 3.600 | 3.605 | 7 | 7 | 7 |
| HV-PMOS | 6 | yes | 40 | D2S pad, S2D pad, bias_dist_pd, pad_ref_rb | 1.419 | x2s.xlay.x_173 (pu fast ss 125 C 3.6 V, t = 2.08 us) | 3.777 | 4.234 | xs.xr.xlay.x_18 (en tt 27 C 3.6 V, t = 22.48 us) | 3.534 | 4.056 | 1.419 | 31 | 30 | 14 |
| HV-PMOS | 12.5 | yes | 8 | bg_core_pd | 3.618 | xs.xbg.xms1_0 (pu late tt 27 C 3.6 V, t = 20.07 us) | 7.888 | 10.745 | xs.xbg.xms1_0 (en ff 125 C 3.6 V, t = 22.01 us) | 3.600 | 4.283 | 3.618 | 4 | 4 | 4 |
| HV-PMOS | 20 | yes | 70 | s7_ctrl ls_up_fs | 3.600 | xs.xc.xl4.xpl1 (mode ff 125 C 3.6 V, t = 2.01 us) | 5.851 | 8.196 | xs.xc.xl4.xpl1 (pu fast sf -40 C 3.6 V, t = 0.82 us) | 3.600 | 3.453 | 3.600 | 70 | 70 | 70 |
| HV-PMOS | 32.16 | yes | 2 | D2S pad | 3.600 | x2d.xlay.x_2 (fs ff -40 C 3.6 V, pad 0.00 V) | 3.600 | 0.000 |  | 3.600 | 0.000 | 3.600 | 2 | 2 | 2 |

## Devices with |VGS| or |VGD| above 3.301 V, by run class and gate-length class

| runs | number of runs | gate-length class | devices | \|VGS\| > 3.301 V | \|VGS\| or \|VGD\| > 3.301 V | same, held >= 100 ns | max of \|VGS\|, \|VGD\| [V] | same, held >= 100 ns [V] | by block (\|VGS\| or \|VGD\| > 3.301 V) |
|---|---|---|---|---|---|---|---|---|---|
| all 3.0 V runs | 5 | L >= spec LG | 255 | 0 | 0 | 0 | 3.300 | 3.300 |  |
| all 3.0 V runs | 5 | L below spec LG (0.45 um) | 244 | 0 | 0 | 0 | 3.000 | 3.000 |  |
| all 3.3 V runs | 96 | L >= spec LG | 255 | 8 | 28 | 4 | 7.278 | 3.500 | D2S pad 4, S2D pad 1, bg_core_pd 2, bias_dist_pd 1, pad_ref_rb 1, s7_ctrl ls_up_fs 19 |
| all 3.3 V runs | 96 | L below spec LG (0.45 um) | 244 | 164 | 192 | 17 | 3.875 | 3.714 | D2S pad 2, S2D pad 3, bg_core_pd 1, bias_dist_pd 55, s7_ctrl logic 76, s7_ctrl ls_up_fs 42, s7_ctrl tg_hv switches 13 |
| 3.3 V runs at 27 C | 32 | L >= spec LG | 255 | 8 | 27 | 4 | 6.946 | 3.500 | D2S pad 4, S2D pad 1, bg_core_pd 2, bias_dist_pd 1, s7_ctrl ls_up_fs 19 |
| 3.3 V runs at 27 C | 32 | L below spec LG (0.45 um) | 244 | 161 | 189 | 13 | 3.848 | 3.680 | D2S pad 2, S2D pad 2, bg_core_pd 1, bias_dist_pd 54, s7_ctrl logic 76, s7_ctrl ls_up_fs 42, s7_ctrl tg_hv switches 12 |
| 3.3 V DC, enabled (dc) | 45 | L >= spec LG | 255 | 0 | 1 | 1 | 3.500 | 3.500 | S2D pad 1 |
| 3.3 V DC, enabled (dc) | 45 | L below spec LG (0.45 um) | 244 | 0 | 0 | 0 | 3.300 | 3.300 |  |
| 3.3 V fail-safe (fs, fs0, fst) | 32 | L >= spec LG | 255 | 0 | 0 | 0 | 3.300 | 3.300 |  |
| 3.3 V fail-safe (fs, fs0, fst) | 32 | L below spec LG (0.45 um) | 244 | 0 | 0 | 0 | 3.300 | 3.300 |  |
| 3.3 V transients | 19 | L >= spec LG | 255 | 8 | 28 | 4 | 7.278 | 3.500 | D2S pad 4, S2D pad 1, bg_core_pd 2, bias_dist_pd 1, pad_ref_rb 1, s7_ctrl ls_up_fs 19 |
| 3.3 V transients | 19 | L below spec LG (0.45 um) | 244 | 164 | 192 | 17 | 3.875 | 3.714 | D2S pad 2, S2D pad 3, bg_core_pd 1, bias_dist_pd 55, s7_ctrl logic 76, s7_ctrl ls_up_fs 42, s7_ctrl tg_hv switches 13 |
| all 3.6 V runs | 121 | L >= spec LG | 255 | 88 | 143 | 142 | 7.888 | 3.800 | D2S pad 24, S2D pad 24, bg_core_pd 7, bias_dist_pd 4, pad_ref_rb 7, s7_ctrl ls_up_fs 77 |
| all 3.6 V runs | 121 | L below spec LG (0.45 um) | 244 | 198 | 218 | 215 | 4.182 | 4.082 | D2S pad 7, S2D pad 7, bg_core_pd 2, bias_dist_pd 58, pad_ref_rb 5, s7_ctrl logic 76, s7_ctrl ls_up_fs 49, s7_ctrl tg_hv switches 14 |
| 3.6 V runs at 27 C | 33 | L >= spec LG | 255 | 88 | 123 | 116 | 7.196 | 3.800 | D2S pad 15, S2D pad 16, bg_core_pd 5, bias_dist_pd 4, pad_ref_rb 6, s7_ctrl ls_up_fs 77 |
| 3.6 V runs at 27 C | 33 | L below spec LG (0.45 um) | 244 | 196 | 218 | 215 | 4.156 | 3.982 | D2S pad 7, S2D pad 7, bg_core_pd 2, bias_dist_pd 58, pad_ref_rb 5, s7_ctrl logic 76, s7_ctrl ls_up_fs 49, s7_ctrl tg_hv switches 14 |
| 3.6 V DC, enabled (dc) | 45 | L >= spec LG | 255 | 69 | 74 | 74 | 3.800 | 3.800 | S2D pad 4, bg_core_pd 3, s7_ctrl ls_up_fs 67 |
| 3.6 V DC, enabled (dc) | 45 | L below spec LG (0.45 um) | 244 | 79 | 154 | 154 | 3.600 | 3.600 | S2D pad 1, bias_dist_pd 40, s7_ctrl logic 58, s7_ctrl ls_up_fs 48, s7_ctrl tg_hv switches 7 |
| 3.6 V fail-safe (fs, fs0, fst) | 31 | L >= spec LG | 255 | 6 | 46 | 46 | 3.600 | 3.600 | D2S pad 24, S2D pad 22 |
| 3.6 V fail-safe (fs, fs0, fst) | 31 | L below spec LG (0.45 um) | 244 | 2 | 2 | 2 | 3.600 | 3.600 | D2S pad 2 |
| 3.6 V transients | 45 | L >= spec LG | 255 | 82 | 121 | 120 | 7.888 | 3.800 | D2S pad 10, S2D pad 16, bg_core_pd 7, bias_dist_pd 4, pad_ref_rb 7, s7_ctrl ls_up_fs 77 |
| 3.6 V transients | 45 | L below spec LG (0.45 um) | 244 | 198 | 218 | 215 | 4.182 | 4.082 | D2S pad 7, S2D pad 7, bg_core_pd 2, bias_dist_pd 58, pad_ref_rb 5, s7_ctrl logic 76, s7_ctrl ls_up_fs 49, s7_ctrl tg_hv switches 14 |

## Number of devices per bin of their max(|VGS|, |VGD|) [V], peak and held >= 100 ns

| runs | gate-length class | value | <= 3.301 | 3.301 ... 3.35 | 3.35 ... 3.5 | 3.5 ... 3.6 | 3.6 ... 3.65 | 3.65 ... 3.8 | 3.8 ... 4.0 | 4.0 ... 5.0 | > 5.0 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all 3.3 V runs | L >= spec LG | peak | 227 | 3 | 10 | 1 | 0 | 0 | 0 | 0 | 14 |
| all 3.3 V runs | L >= spec LG | held | 251 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| all 3.3 V runs | L = 0.45 um | peak | 52 | 115 | 66 | 6 | 0 | 4 | 1 | 0 | 0 |
| all 3.3 V runs | L = 0.45 um | held | 227 | 4 | 2 | 9 | 0 | 2 | 0 | 0 | 0 |
| 3.3 V DC, enabled (dc) | L >= spec LG | peak | 254 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.3 V DC, enabled (dc) | L >= spec LG | held | 254 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.3 V DC, enabled (dc) | L = 0.45 um | peak | 244 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.3 V DC, enabled (dc) | L = 0.45 um | held | 244 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.3 V transients | L >= spec LG | peak | 227 | 3 | 10 | 1 | 0 | 0 | 0 | 0 | 14 |
| 3.3 V transients | L >= spec LG | held | 251 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3.3 V transients | L = 0.45 um | peak | 52 | 115 | 66 | 6 | 0 | 4 | 1 | 0 | 0 |
| 3.3 V transients | L = 0.45 um | held | 227 | 4 | 2 | 9 | 0 | 2 | 0 | 0 | 0 |
| all 3.6 V runs | L >= spec LG | peak | 112 | 1 | 38 | 73 | 5 | 11 | 1 | 0 | 14 |
| all 3.6 V runs | L >= spec LG | held | 113 | 1 | 39 | 98 | 0 | 4 | 0 | 0 | 0 |
| all 3.6 V runs | L = 0.45 um | peak | 26 | 0 | 2 | 11 | 93 | 89 | 18 | 5 | 0 |
| all 3.6 V runs | L = 0.45 um | held | 29 | 0 | 3 | 179 | 20 | 2 | 9 | 2 | 0 |
| 3.6 V DC, enabled (dc) | L >= spec LG | peak | 181 | 1 | 3 | 69 | 0 | 1 | 0 | 0 | 0 |
| 3.6 V DC, enabled (dc) | L >= spec LG | held | 181 | 1 | 3 | 69 | 0 | 1 | 0 | 0 | 0 |
| 3.6 V DC, enabled (dc) | L = 0.45 um | peak | 90 | 0 | 4 | 150 | 0 | 0 | 0 | 0 | 0 |
| 3.6 V DC, enabled (dc) | L = 0.45 um | held | 90 | 0 | 4 | 150 | 0 | 0 | 0 | 0 | 0 |
| 3.6 V transients | L >= spec LG | peak | 134 | 3 | 21 | 66 | 5 | 11 | 1 | 0 | 14 |
| 3.6 V transients | L >= spec LG | held | 135 | 3 | 22 | 91 | 0 | 4 | 0 | 0 | 0 |
| 3.6 V transients | L = 0.45 um | peak | 26 | 0 | 2 | 11 | 93 | 89 | 18 | 5 | 0 |
| 3.6 V transients | L = 0.45 um | held | 29 | 0 | 3 | 179 | 20 | 2 | 9 | 2 | 0 |

Bins are half-open (lower, upper]. The first bin ends at 3.301 V: a device counts as above 3.3 V when it exceeds it by more than 1 mV (at a 3.3 V supply, VGS = supply comes out a few uV above 3.3 V at some points).

### Devices with L meeting the spec LG and |VGS| or |VGD| > 3.301 V, all 3.3 V runs: 28

| device | block | type | W/L [um] | d = s (capacitor) | \|VGS\| [V] | where | \|VGD\| [V] | where | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | max \|VDS\| [V] | nodes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| xs.xbg.xms1_0 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 3.312 | pu late tt 27 C 3.3 V, t = 20.07 us | 7.278 | en ff -40 C 3.3 V, t = 22.01 us | 3.300 | 10.013 | g xs.en_b, s vdd_3v3, d xs.xbg.net1 |
| xs.xbg.xms1_1 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 3.182 | dc 1k ss -40 C 3.3 V, pad -0.20 V | 7.278 | en ff -40 C 3.3 V, t = 22.01 us | 3.182 | 8.529 | g xs.en_b, s xs.xbg.net1, d xs.xbg.net2 |
| xs.xc.xl0.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 3.30 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d0, s xs.xc.xl0.l2, d xs.xc.xl0.l1 |
| xs.xc.xl0.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 3.30 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.815 | g d0, s xs.xc.xl0.l1, d xs.xc.xl0.x |
| xs.xc.xl1.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 0.95 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d1, s xs.xc.xl1.l2, d xs.xc.xl1.l1 |
| xs.xc.xl1.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 0.95 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.815 | g d1, s xs.xc.xl1.l1, d xs.xc.xl1.x |
| xs.xc.xl2.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 2.45 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d2, s xs.xc.xl2.l2, d xs.xc.xl2.l1 |
| xs.xc.xl2.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 2.45 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.815 | g d2, s xs.xc.xl2.l1, d xs.xc.xl2.x |
| xs.xc.xl3.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 1.70 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d3, s xs.xc.xl3.l2, d xs.xc.xl3.l1 |
| xs.xc.xl3.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 1.70 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.815 | g d3, s xs.xc.xl3.l1, d xs.xc.xl3.x |
| xs.xc.xl5.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 2.15 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d5, s xs.xc.xl5.l2, d xs.xc.xl5.l1 |
| xs.xc.xl5.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 2.15 V | 5.491 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.815 | g d5, s xs.xc.xl5.l1, d xs.xc.xl5.x |
| xs.xc.xl4.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | dc 1k ff -40 C 3.3 V, pad 1.10 V | 5.490 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 6.000 | g d4, s xs.xc.xl4.l2, d xs.xc.xl4.l1 |
| xs.xc.xl4.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.300 | mode ss 125 C 3.3 V, t = 2.01 us | 5.490 | pu fast ss 125 C 3.3 V, t = 0.88 us | 3.300 | 7.814 | g d4, s xs.xc.xl4.l1, d xs.xc.xl4.x |
| x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | no | 0.812 | fs0 ss -40 C 3.3 V, pad 3.30 V | 3.501 | step open ss 125 C 3.3 V, t = 12.03 us | 3.500 | 3.500 | g x2s.xlay.n_i9, s padin, d iovdd |
| xs.xc.xl0.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.447 | mode ss 125 C 3.3 V, t = 42.00 us | 3.343 | mode ss 125 C 3.3 V, t = 12.01 us | 3.300 | 3.344 | g xs.xc.xl0.y, s vdd_3v3, d xs.xc.xl0.x |
| xs.xc.xl1.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.447 | mode ss 125 C 3.3 V, t = 42.00 us | 3.340 | mode ss 125 C 3.3 V, t = 22.01 us | 3.300 | 3.340 | g xs.xc.xl1.y, s vdd_3v3, d xs.xc.xl1.x |
| xs.xc.xl2.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.447 | mode ss 125 C 3.3 V, t = 22.00 us | 3.340 | mode ss 125 C 3.3 V, t = 32.01 us | 3.300 | 3.340 | g xs.xc.xl2.y, s vdd_3v3, d xs.xc.xl2.x |
| xs.xc.xl4.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.447 | mode ss 125 C 3.3 V, t = 42.00 us | 3.338 | mode ss 125 C 3.3 V, t = 52.01 us | 3.300 | 3.338 | g xs.xc.xl4.y, s vdd_3v3, d xs.xc.xl4.x |
| xs.xc.xl5.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.447 | mode ss 125 C 3.3 V, t = 32.00 us | 3.338 | mode ss 125 C 3.3 V, t = 52.01 us | 3.300 | 3.338 | g xs.xc.xl5.y, s vdd_3v3, d xs.xc.xl5.x |
| x2d.xlay.x_234 | D2S pad | HV-PMOS | 6.66/0.6 | no | 1.505 | pu fast tt 27 C 3.3 V, t = 1.22 us | 3.420 | pu late tt 27 C 3.3 V, t = 20.48 us | 3.396 | 3.186 | g x2d.xlay.n_i118, s x2d.xlay.n_i115, d x2d.xlay.n_i116 |
| x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | no | 1.274 | dc 1k ss -40 C 3.3 V, pad -0.20 V | 3.419 | pu late tt 27 C 3.3 V, t = 20.48 us | 3.398 | 3.307 | g x2d.xlay.n_i118, s x2d.xlay.n_i5, d x2d.xlay.n_i67 |
| xs.xc.xle.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.418 | en tt 27 C 3.3 V, t = 22.00 us | 3.338 | en ss 125 C 3.3 V, t = 2.01 us | 3.300 | 3.338 | g xs.xc.xle.y, s vdd_3v3, d xs.xc.xle.x |
| xs.xc.xl3.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.418 | mode tt 27 C 3.3 V, t = 2.00 us | 3.338 | mode ss 125 C 3.3 V, t = 52.01 us | 3.300 | 3.338 | g xs.xc.xl3.y, s vdd_3v3, d xs.xc.xl3.x |
| x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | no | 1.113 | fs sf 125 C 3.3 V, pad 3.30 V | 3.415 | pu late tt 27 C 3.3 V, t = 20.07 us | 3.406 | 3.307 | g x2d.xlay.n_i134, s x2d.xlay.n_i67, d x2d.xlay.n_i5 |
| xs.xr.xlay.x_18 | pad_ref_rb | HV-PMOS | 5/6 | no | 1.379 | en ss 125 C 3.3 V, t = 2.24 us | 3.345 | en ss 125 C 3.3 V, t = 22.64 us | 3.015 | 3.845 | g xs.xr.xlay.n_13, s xs.xr.xlay.n_25, d vdd_3v3 |
| x2d.xlay.x_209 | D2S pad | HV-NMOS | 6/6 | no | 0.988 | dc 1k ss -40 C 3.3 V, pad -0.20 V | 3.318 | en ff -40 C 3.3 V, t = 22.01 us | 3.300 | 3.422 | g x2d.xlay.n_i135, s 0, d x2d.xlay.n_i118 |
| xs.xd.xlay.x_11 | bias_dist_pd | HV-NMOS | 6/6 | no | 1.299 | pu fast ff -40 C 3.3 V, t = 0.96 us | 3.316 | en ff -40 C 3.3 V, t = 22.01 us | 3.300 | 3.303 | g xs.xd.xlay.n_9, s 0, d xs.xd.xlay.n_28 |

### Devices with L meeting the spec LG and |VGS| or |VGD| > 3.301 V, all 3.6 V runs: 143

| device | block | type | W/L [um] | d = s (capacitor) | \|VGS\| [V] | where | \|VGD\| [V] | where | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | max \|VDS\| [V] | nodes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| xs.xbg.xms1_0 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 3.618 | pu late tt 27 C 3.6 V, t = 20.07 us | 7.888 | en ff 125 C 3.6 V, t = 22.01 us | 3.600 | 10.745 | g xs.en_b, s vdd_3v3, d xs.xbg.net1 |
| xs.xbg.xms1_1 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 3.466 | mode ss -40 C 3.6 V, t = 42.01 us | 7.888 | en ff 125 C 3.6 V, t = 22.01 us | 3.466 | 9.032 | g xs.en_b, s xs.xbg.net1, d xs.xbg.net2 |
| xs.xc.xl4.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d4, s xs.xc.xl4.l2, d xs.xc.xl4.l1 |
| xs.xc.xl4.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | mode ff 125 C 3.6 V, t = 2.01 us | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d4, s xs.xc.xl4.l1, d xs.xc.xl4.x |
| xs.xc.xl0.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d0, s xs.xc.xl0.l2, d xs.xc.xl0.l1 |
| xs.xc.xl0.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d0, s xs.xc.xl0.l1, d xs.xc.xl0.x |
| xs.xc.xl1.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d1, s xs.xc.xl1.l2, d xs.xc.xl1.l1 |
| xs.xc.xl1.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d1, s xs.xc.xl1.l1, d xs.xc.xl1.x |
| xs.xc.xl2.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d2, s xs.xc.xl2.l2, d xs.xc.xl2.l1 |
| xs.xc.xl2.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d2, s xs.xc.xl2.l1, d xs.xc.xl2.x |
| xs.xc.xl3.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d3, s xs.xc.xl3.l2, d xs.xc.xl3.l1 |
| xs.xc.xl3.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d3, s xs.xc.xl3.l1, d xs.xc.xl3.x |
| xs.xc.xl5.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 6.287 | g d5, s xs.xc.xl5.l2, d xs.xc.xl5.l1 |
| xs.xc.xl5.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 8.196 | g d5, s xs.xc.xl5.l1, d xs.xc.xl5.x |
| x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | no | 0.828 | fs0 ss -40 C 3.6 V, pad 3.60 V | 3.801 | step 100p ff 125 C 3.6 V, t = 12.03 us | 3.800 | 3.800 | g x2s.xlay.n_i9, s padin, d iovdd |
| xs.xr.xlay.x_18 | pad_ref_rb | HV-PMOS | 5/6 | no | 1.381 | en ss 125 C 3.6 V, t = 2.19 us | 3.777 | en ff 125 C 3.6 V, t = 22.54 us | 3.465 | 4.234 | g xs.xr.xlay.n_13, s xs.xr.xlay.n_25, d vdd_3v3 |
| xs.xc.xl0.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.630 | mode ss 125 C 3.6 V, t = 12.01 us | 3.600 | 3.630 | g xs.xc.xl0.y, s vdd_3v3, d xs.xc.xl0.x |
| xs.xc.xl1.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.628 | mode tt 27 C 3.6 V, t = 12.01 us | 3.600 | 3.627 | g xs.xc.xl1.y, s vdd_3v3, d xs.xc.xl1.x |
| xs.xc.xl2.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.626 | mode ss 125 C 3.6 V, t = 32.01 us | 3.600 | 3.626 | g xs.xc.xl2.y, s vdd_3v3, d xs.xc.xl2.x |
| xs.xc.xl4.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.625 | mode ss 125 C 3.6 V, t = 52.01 us | 3.600 | 3.625 | g xs.xc.xl4.y, s vdd_3v3, d xs.xc.xl4.x |
| xs.xc.xl5.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.743 | mode ss 125 C 3.6 V, t = 32.00 us | 3.625 | mode ss 125 C 3.6 V, t = 52.01 us | 3.600 | 3.625 | g xs.xc.xl5.y, s vdd_3v3, d xs.xc.xl5.x |
| x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | no | 1.138 | fs sf 125 C 3.6 V, pad 3.60 V | 3.728 | pu late tt 27 C 3.6 V, t = 20.07 us | 3.719 | 3.608 | g x2d.xlay.n_i134, s x2d.xlay.n_i67, d x2d.xlay.n_i5 |
| x2d.xlay.x_234 | D2S pad | HV-PMOS | 6.66/0.6 | no | 1.786 | pu fast ss -40 C 3.6 V, t = 1.05 us | 3.725 | pu late tt 27 C 3.6 V, t = 20.44 us | 3.703 | 3.516 | g x2d.xlay.n_i118, s x2d.xlay.n_i115, d x2d.xlay.n_i116 |
| x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | no | 1.451 | en ss -40 C 3.6 V, t = 22.40 us | 3.725 | pu late tt 27 C 3.6 V, t = 20.44 us | 3.707 | 3.608 | g x2d.xlay.n_i118, s x2d.xlay.n_i5, d x2d.xlay.n_i67 |
| xs.xc.xle.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.712 | en ss 125 C 3.6 V, t = 22.00 us | 3.625 | en ss 125 C 3.6 V, t = 2.01 us | 3.600 | 3.625 | g xs.xc.xle.y, s vdd_3v3, d xs.xc.xle.x |
| xs.xc.xl3.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | no | 3.712 | mode ss 125 C 3.6 V, t = 2.00 us | 3.627 | mode tt 27 C 3.6 V, t = 2.01 us | 3.600 | 3.625 | g xs.xc.xl3.y, s vdd_3v3, d xs.xc.xl3.x |
| x2d.xlay.x_209 | D2S pad | HV-NMOS | 6/6 | no | 0.992 | pu fast ss -40 C 3.6 V, t = 1.06 us | 3.618 | en tt 27 C 3.6 V, t = 22.01 us | 3.600 | 3.727 | g x2d.xlay.n_i135, s 0, d x2d.xlay.n_i118 |
| xs.xd.xlay.x_11 | bias_dist_pd | HV-NMOS | 6/6 | no | 1.468 | pu fast ss -40 C 3.6 V, t = 0.96 us | 3.618 | en ff 125 C 3.6 V, t = 22.01 us | 3.600 | 3.603 | g xs.xd.xlay.n_9, s 0, d xs.xd.xlay.n_28 |
| xs.xbg.xms3 | bg_core_pd | HV-NMOS | 0.5/2 | no | 2.002 | en ss -40 C 3.6 V, t = 22.27 us | 3.602 | en ff 125 C 3.6 V, t = 22.01 us | 3.550 | 3.550 | g xs.xbg.ks, s 0, d xs.xbg.vpc |
| xs.xbg.xms1_7 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 2.270 | mode ss -40 C 3.6 V, t = 42.01 us | 3.602 | en ss 125 C 3.6 V, t = 22.01 us | 3.600 | 4.541 | g xs.en_b, s xs.xbg.net7, d xs.xbg.ks |
| x2s.xlay.x_43 | S2D pad | HV-NMOS | 88/0.6 | no | 0.201 | step open fs 125 C 3.6 V, t = 12.01 us | 3.600 | step 100p ff -40 C 3.6 V, t = 2.01 us | 3.600 | 3.600 | g x2s.xlay.n_i8, s padin, d 0 |
| xs.xc.xle.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 2.01 us | 3.600 | en ff -40 C 3.6 V, t = 11.21 us | 3.600 | 2.544 | g enable, s vdd_3v3, d xs.xc.xle.l9 |
| xs.xc.xle.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 11.21 us | 3.600 | en ff -40 C 3.6 V, t = 11.03 us | 3.600 | 3.119 | g enable, s xs.xc.xle.l9, d xs.xc.xle.l8 |
| xs.xc.xle.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 11.03 us | 3.600 | en ff -40 C 3.6 V, t = 11.06 us | 3.600 | 3.313 | g enable, s xs.xc.xle.l8, d xs.xc.xle.l7 |
| xs.xc.xle.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 11.06 us | 3.600 | en ff -40 C 3.6 V, t = 11.05 us | 3.600 | 3.401 | g enable, s xs.xc.xle.l7, d xs.xc.xle.l6 |
| xs.xc.xle.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 11.05 us | 3.600 | en ff -40 C 3.6 V, t = 10.90 us | 3.600 | 3.196 | g enable, s xs.xc.xle.l6, d xs.xc.xle.l5 |
| xs.xc.xle.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 10.90 us | 3.600 | en ff -40 C 3.6 V, t = 10.00 us | 3.600 | 3.017 | g enable, s xs.xc.xle.l5, d xs.xc.xle.l4 |
| xs.xc.xle.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 10.00 us | 3.600 | en ff -40 C 3.6 V, t = 9.99 us | 3.600 | 2.830 | g enable, s xs.xc.xle.l4, d xs.xc.xle.l3 |
| xs.xc.xle.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 9.99 us | 3.600 | en ff -40 C 3.6 V, t = 9.97 us | 3.600 | 2.684 | g enable, s xs.xc.xle.l3, d xs.xc.xle.l2 |
| xs.xc.xle.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 9.97 us | 3.600 | en ff -40 C 3.6 V, t = 22.00 us | 3.600 | 2.692 | g enable, s xs.xc.xle.l2, d xs.xc.xle.l1 |
| xs.xc.xle.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | en ff -40 C 3.6 V, t = 22.00 us | 3.600 | en ff -40 C 3.6 V, t = 8.25 us | 3.600 | 4.296 | g enable, s xs.xc.xle.l1, d xs.xc.xle.x |
| xs.xc.xl0.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 1.616 | g d0, s vdd_3v3, d xs.xc.xl0.l9 |
| xs.xc.xl0.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.055 | g d0, s xs.xc.xl0.l9, d xs.xc.xl0.l8 |
| xs.xc.xl0.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.231 | g d0, s xs.xc.xl0.l8, d xs.xc.xl0.l7 |
| xs.xc.xl0.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.371 | g d0, s xs.xc.xl0.l7, d xs.xc.xl0.l6 |
| xs.xc.xl0.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.468 | g d0, s xs.xc.xl0.l6, d xs.xc.xl0.l5 |
| xs.xc.xl0.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.244 | g d0, s xs.xc.xl0.l5, d xs.xc.xl0.l4 |
| xs.xc.xl0.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.487 | g d0, s xs.xc.xl0.l4, d xs.xc.xl0.l3 |
| xs.xc.xl0.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.312 | g d0, s xs.xc.xl0.l3, d xs.xc.xl0.l2 |
| xs.xc.xl1.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 1.616 | g d1, s vdd_3v3, d xs.xc.xl1.l9 |
| xs.xc.xl1.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 2.055 | g d1, s xs.xc.xl1.l9, d xs.xc.xl1.l8 |
| xs.xc.xl1.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 2.231 | g d1, s xs.xc.xl1.l8, d xs.xc.xl1.l7 |
| xs.xc.xl1.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 2.371 | g d1, s xs.xc.xl1.l7, d xs.xc.xl1.l6 |
| xs.xc.xl1.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 2.468 | g d1, s xs.xc.xl1.l6, d xs.xc.xl1.l5 |
| xs.xc.xl1.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 4.244 | g d1, s xs.xc.xl1.l5, d xs.xc.xl1.l4 |
| xs.xc.xl1.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 4.487 | g d1, s xs.xc.xl1.l4, d xs.xc.xl1.l3 |
| xs.xc.xl1.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 3.45 V | 3.600 | 4.312 | g d1, s xs.xc.xl1.l3, d xs.xc.xl1.l2 |
| xs.xc.xl2.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 1.616 | g d2, s vdd_3v3, d xs.xc.xl2.l9 |
| xs.xc.xl2.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 2.055 | g d2, s xs.xc.xl2.l9, d xs.xc.xl2.l8 |
| xs.xc.xl2.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 2.231 | g d2, s xs.xc.xl2.l8, d xs.xc.xl2.l7 |
| xs.xc.xl2.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 2.371 | g d2, s xs.xc.xl2.l7, d xs.xc.xl2.l6 |
| xs.xc.xl2.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 2.468 | g d2, s xs.xc.xl2.l6, d xs.xc.xl2.l5 |
| xs.xc.xl2.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 4.244 | g d2, s xs.xc.xl2.l5, d xs.xc.xl2.l4 |
| xs.xc.xl2.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 4.487 | g d2, s xs.xc.xl2.l4, d xs.xc.xl2.l3 |
| xs.xc.xl2.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.05 V | 3.600 | 4.312 | g d2, s xs.xc.xl2.l3, d xs.xc.xl2.l2 |
| xs.xc.xl3.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 1.616 | g d3, s vdd_3v3, d xs.xc.xl3.l9 |
| xs.xc.xl3.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.055 | g d3, s xs.xc.xl3.l9, d xs.xc.xl3.l8 |
| xs.xc.xl3.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.231 | g d3, s xs.xc.xl3.l8, d xs.xc.xl3.l7 |
| xs.xc.xl3.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.371 | g d3, s xs.xc.xl3.l7, d xs.xc.xl3.l6 |
| xs.xc.xl3.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.468 | g d3, s xs.xc.xl3.l6, d xs.xc.xl3.l5 |
| xs.xc.xl3.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.244 | g d3, s xs.xc.xl3.l5, d xs.xc.xl3.l4 |
| xs.xc.xl3.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.487 | g d3, s xs.xc.xl3.l4, d xs.xc.xl3.l3 |
| xs.xc.xl3.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.312 | g d3, s xs.xc.xl3.l3, d xs.xc.xl3.l2 |
| xs.xc.xl4.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 1.616 | g d4, s vdd_3v3, d xs.xc.xl4.l9 |
| xs.xc.xl4.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 2.055 | g d4, s xs.xc.xl4.l9, d xs.xc.xl4.l8 |
| xs.xc.xl4.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 2.231 | g d4, s xs.xc.xl4.l8, d xs.xc.xl4.l7 |
| xs.xc.xl4.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 2.371 | g d4, s xs.xc.xl4.l7, d xs.xc.xl4.l6 |
| xs.xc.xl4.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 2.468 | g d4, s xs.xc.xl4.l6, d xs.xc.xl4.l5 |
| xs.xc.xl4.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 4.244 | g d4, s xs.xc.xl4.l5, d xs.xc.xl4.l4 |
| xs.xc.xl4.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 4.487 | g d4, s xs.xc.xl4.l4, d xs.xc.xl4.l3 |
| xs.xc.xl4.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | dc 1k ff -40 C 3.6 V, pad 0.15 V | 3.600 | 4.312 | g d4, s xs.xc.xl4.l3, d xs.xc.xl4.l2 |
| xs.xc.xl5.xpl10 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 1.616 | g d5, s vdd_3v3, d xs.xc.xl5.l9 |
| xs.xc.xl5.xpl9 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.055 | g d5, s xs.xc.xl5.l9, d xs.xc.xl5.l8 |
| xs.xc.xl5.xpl8 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.231 | g d5, s xs.xc.xl5.l8, d xs.xc.xl5.l7 |
| xs.xc.xl5.xpl7 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.371 | g d5, s xs.xc.xl5.l7, d xs.xc.xl5.l6 |
| xs.xc.xl5.xpl6 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 2.468 | g d5, s xs.xc.xl5.l6, d xs.xc.xl5.l5 |
| xs.xc.xl5.xpl5 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.244 | g d5, s xs.xc.xl5.l5, d xs.xc.xl5.l4 |
| xs.xc.xl5.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.487 | g d5, s xs.xc.xl5.l4, d xs.xc.xl5.l3 |
| xs.xc.xl5.xpl3 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | no | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | dc 1k ff -40 C 3.6 V, pad -0.20 V | 3.600 | 4.312 | g d5, s xs.xc.xl5.l3, d xs.xc.xl5.l2 |
| x2d.xlay.x_2 | D2S pad | HV-PMOS | 7.96/32.16 | yes | 3.600 | fs ff -40 C 3.6 V, pad 0.00 V | 3.600 | fs ff -40 C 3.6 V, pad 0.00 V | 3.600 | 0.000 | g x2d.xlay.n_i5, s x2d.xlay.n_i113, d x2d.xlay.n_i113 |
| x2d.xlay.x_77 | D2S pad | HV-PMOS | 546.12/0.6 | no | 1.132 | dc 1kgnd ss -40 C 3.6 V, pad 1.75 V | 3.600 | fs ff -40 C 3.6 V, pad 0.00 V | 3.600 | 3.600 | g x2d.xlay.n_i5, s padout, d iovdd |
| x2d.xlay.x_169 | D2S pad | HV-NMOS | 4.4/1 | no | 3.144 | pu late tt 27 C 3.6 V, t = 20.50 us | 3.587 | pu late tt 27 C 3.6 V, t = 20.07 us | 3.578 | 3.516 | g x2d.xlay.n_i134, s x2d.xlay.n_i115, d x2d.xlay.n_i116 |
| x2s.xlay.x_202 | S2D pad | HV-PMOS | 20/1 | no | 3.489 | fs fs 125 C 3.6 V, pad 3.60 V | 3.578 | fs ff -40 C 3.6 V, pad 3.60 V | 3.578 | 3.005 | g padin, s x2s.xlay.n_i11, d x2s.xlay.n_i34 |
| x2s.xlay.x_208 | S2D pad | HV-PMOS | 20/1 | no | 3.489 | fs fs 125 C 3.6 V, pad 3.60 V | 3.578 | fs ff -40 C 3.6 V, pad 3.60 V | 3.578 | 3.005 | g padin, s x2s.xlay.n_i11, d x2s.xlay.n_i33 |
| x2d.xlay.x_276 | D2S pad | HV-PMOS | 20/1 | no | 3.490 | fs fs 125 C 3.6 V, pad 3.60 V | 3.563 | fs fs 125 C 3.6 V, pad 3.60 V | 3.563 | 2.781 | g padout, s x2d.xlay.n_i120, d x2d.xlay.n_i131 |
| x2d.xlay.x_278 | D2S pad | HV-PMOS | 20/1 | no | 3.490 | fs fs 125 C 3.6 V, pad 3.60 V | 3.563 | fs fs 125 C 3.6 V, pad 3.60 V | 3.563 | 2.781 | g padout, s x2d.xlay.n_i120, d x2d.xlay.n_i130 |
| xs.xr.xlay.x_28 | pad_ref_rb | HV-NMOS | 4.8/6 | no | 0.991 | pu fast ss -40 C 3.6 V, t = 1.59 us | 3.555 | off ff 125 C 3.6 V, t = 70.00 us | 3.555 | 3.555 | g xs.xr.xlay.n_17, s 0, d xs.xr.xlay.n_23 |
| x2s.xlay.x_191 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.535 | pu fast ss -40 C 3.6 V, t = 1.00 us | 3.534 | 3.590 | g x2s.xlay.n_i32, s x2s.xlay.n_i23, d iovdd |
| x2d.xlay.x_256 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.529 | fst fs -40 C 3.6 V, t = 2.00 us | 3.529 | 3.585 | g x2d.xlay.n_i132, s x2d.xlay.n_i133, d iovdd |
| x2s.xlay.x_179 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.519 | off ff 125 C 3.6 V, t = 68.83 us | 3.519 | 4.044 | g x2s.xlay.n_i32, s x2s.xlay.n_i34, d iovdd |
| x2s.xlay.x_182 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.519 | off ff 125 C 3.6 V, t = 68.83 us | 3.519 | 4.044 | g x2s.xlay.n_i32, s x2s.xlay.n_i33, d iovdd |
| x2s.xlay.x_187 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.517 | off ff 125 C 3.6 V, t = 68.89 us | 3.517 | 4.041 | g x2s.xlay.n_i32, s x2s.xlay.n_i26, d iovdd |
| x2s.xlay.x_190 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.517 | off ff 125 C 3.6 V, t = 68.89 us | 3.517 | 4.041 | g x2s.xlay.n_i32, s x2s.xlay.n_i29, d iovdd |
| x2d.xlay.x_236 | D2S pad | HV-PMOS | 2/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.506 | fst sf -40 C 3.6 V, t = 1.01 us | 3.506 | 3.563 | g x2d.xlay.n_i132, s x2d.xlay.n_i128, d iovdd |
| x2d.xlay.x_1 | D2S pad | HV-PMOS | 7.96/32.16 | yes | 3.489 | fs fs 125 C 3.6 V, pad 3.60 V | 3.489 | fs fs 125 C 3.6 V, pad 3.60 V | 3.489 | 0.000 | g x2d.xlay.n_i114, s x2d.xlay.n_i67, d x2d.xlay.n_i67 |
| x2d.xlay.x_7 | D2S pad | HV-NMOS | 299.2/1 | no | 1.388 | fs sf 125 C 3.6 V, pad 3.60 V | 3.489 | fs fs 125 C 3.6 V, pad 3.60 V | 3.489 | 3.600 | g x2d.xlay.n_i67, s padout, d 0 |
| xs.xd.xlay.x_8 | bias_dist_pd | HV-PMOS | 5/6 | no | 1.397 | en ss 125 C 3.6 V, t = 2.19 us | 3.488 | en ff 125 C 3.6 V, t = 22.01 us | 3.469 | 3.554 | g xs.xd.xlay.n_28, s xs.xd.xlay.n_26, d vdd_3v3 |
| x2d.xlay.x_174 | D2S pad | HV-NMOS | 2.4/6 | no | 0.992 | pu fast ss -40 C 3.6 V, t = 1.06 us | 3.474 | fst sf -40 C 3.6 V, t = 2.49 us | 3.474 | 3.571 | g x2d.xlay.n_i135, s 0, d x2d.xlay.n_i121 |
| xs.xd.xlay.x_6 | bias_dist_pd | HV-PMOS | 5/6 | no | 1.397 | en ss 125 C 3.6 V, t = 2.19 us | 3.472 | en ff 125 C 3.6 V, t = 22.01 us | 3.455 | 3.755 | g xs.xd.xlay.n_28, s xs.xd.xlay.n_29, d vdd_3v3 |
| x2s.xlay.x_148 | S2D pad | HV-NMOS | 6/6 | no | 0.996 | pu fast ss -40 C 3.6 V, t = 1.05 us | 3.472 | fst ss -40 C 3.6 V, t = 52.00 us | 3.472 | 3.551 | g x2s.xlay.n_i35, s 0, d x2s.xlay.n_i32 |
| x2d.xlay.x_208 | D2S pad | HV-NMOS | 6/6 | no | 0.992 | pu fast ss -40 C 3.6 V, t = 1.06 us | 3.471 | fs ff 125 C 3.6 V, pad 1.95 V | 3.471 | 3.549 | g x2d.xlay.n_i135, s 0, d x2d.xlay.n_i132 |
| x2s.xlay.x_218 | S2D pad | HV-PMOS | 20/1 | no | 3.470 | pu fast ss -40 C 3.6 V, t = 1.51 us | 3.470 | pu fast ss -40 C 3.6 V, t = 1.51 us | 3.443 | 1.031 | g vref_s2d, s x2s.xlay.n_i20, d x2s.xlay.n_i26 |
| x2s.xlay.x_224 | S2D pad | HV-PMOS | 20/1 | no | 3.470 | pu fast ss -40 C 3.6 V, t = 1.51 us | 3.470 | pu fast ss -40 C 3.6 V, t = 1.51 us | 3.443 | 1.031 | g vref_s2d, s x2s.xlay.n_i20, d x2s.xlay.n_i29 |
| x2s.xlay.x_138 | S2D pad | HV-NMOS | 2.4/6 | no | 0.996 | pu fast ss -40 C 3.6 V, t = 1.05 us | 3.458 | fs ff 125 C 3.6 V, pad 1.40 V | 3.458 | 3.519 | g x2s.xlay.n_i35, s 0, d x2s.xlay.n_i17 |
| x2s.xlay.x_104 | S2D pad | HV-NMOS | 30/3 | no | 2.925 | pu fast fs 125 C 3.6 V, t = 1.64 us | 3.455 | fs fs 125 C 3.6 V, pad 0.65 V | 3.455 | 3.553 | g x2s.xlay.n_i13, s x2s.xlay.n_i19, d iovdd |
| xs.xbg.xnb | bg_core_pd | HV-NMOS | 20/4 | no | 0.969 | pu ss -40 C 3.6 V, t = 8.54 us | 3.448 | off fs 125 C 3.6 V, t = 70.00 us | 3.448 | 3.550 | g xs.xbg.g, s xs.xbg.eb, d xs.xbg.vpc |
| xs.xbg.xpac | bg_core_pd | HV-PMOS | 40/1 | no | 1.305 | pu fast ss -40 C 3.6 V, t = 0.96 us | 3.448 | off fs 125 C 3.6 V, t = 70.00 us | 3.448 | 3.468 | g xs.xbg.vpc, s xs.xbg.ca, d xs.xbg.g |
| xs.xr.xlay.x_36 | pad_ref_rb | HV-NMOS | 60/3 | no | 1.027 | en ss -40 C 3.6 V, t = 2.15 us | 3.446 | pu fast ss 125 C 3.6 V, t = 1.38 us | 3.446 | 3.603 | g xs.xr.xlay.n_6, s xs.vref_rb, d vdd_3v3 |
| xs.xr.xlay.x_39 | pad_ref_rb | HV-NMOS | 15/3 | no | 2.924 | off ff 125 C 3.6 V, t = 70.00 us | 3.446 | pu fast ss 125 C 3.6 V, t = 1.38 us | 3.446 | 3.610 | g xs.xr.xlay.n_6, s xs.xr.xlay.n_8, d vdd_3v3 |
| xs.xr.xlay.x_31 | pad_ref_rb | HV-NMOS | 2.4/6 | no | 0.991 | pu fast ss -40 C 3.6 V, t = 1.59 us | 3.441 | pu fast ss 125 C 3.6 V, t = 1.18 us | 3.426 | 3.554 | g xs.xr.xlay.n_17, s 0, d xs.xr.xlay.n_13 |
| xs.xd.xlay.x_7 | bias_dist_pd | HV-PMOS | 5/6 | no | 1.397 | en ss 125 C 3.6 V, t = 2.19 us | 3.432 | en sf -40 C 3.6 V, t = 22.01 us | 3.412 | 3.878 | g xs.xd.xlay.n_28, s xs.xd.xlay.n_27, d vdd_3v3 |
| x2d.xlay.x_261 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.406 | fs ff 125 C 3.6 V, pad 3.60 V | 3.406 | 3.573 | g x2d.xlay.n_i132, s x2d.xlay.n_i126, d iovdd |
| x2d.xlay.x_266 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.406 | fs ff 125 C 3.6 V, pad 3.60 V | 3.406 | 3.573 | g x2d.xlay.n_i132, s x2d.xlay.n_i129, d iovdd |
| x2d.xlay.x_259 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.402 | fs ff 125 C 3.6 V, pad 0.00 V | 3.402 | 3.529 | g x2d.xlay.n_i132, s x2d.xlay.n_i123, d iovdd |
| x2d.xlay.x_260 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.402 | fs ff 125 C 3.6 V, pad 0.00 V | 3.402 | 3.529 | g x2d.xlay.n_i132, s x2d.xlay.n_i124, d iovdd |
| x2d.xlay.x_265 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.402 | fs ff 125 C 3.6 V, pad 0.00 V | 3.402 | 3.529 | g x2d.xlay.n_i132, s x2d.xlay.n_i130, d iovdd |
| x2d.xlay.x_269 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.402 | fs ff 125 C 3.6 V, pad 0.00 V | 3.402 | 3.529 | g x2d.xlay.n_i132, s x2d.xlay.n_i131, d iovdd |
| x2s.xlay.x_173 | S2D pad | HV-PMOS | 2/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.399 | pu fast ss 125 C 3.6 V, t = 1.00 us | 3.398 | 3.455 | g x2s.xlay.n_i32, s x2s.xlay.n_i13, d iovdd |
| xs.xr.xlay.x_13 | pad_ref_rb | HV-PMOS | 2/6 | no | 1.381 | en ss 125 C 3.6 V, t = 2.19 us | 3.397 | pu fast ss 125 C 3.6 V, t = 1.23 us | 3.397 | 3.446 | g xs.xr.xlay.n_13, s xs.xr.xlay.n_6, d vdd_3v3 |
| x2d.xlay.x_268 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.394 | fs ff 125 C 3.6 V, pad 0.00 V | 3.394 | 3.577 | g x2d.xlay.n_i132, s x2d.xlay.n_i125, d iovdd |
| x2d.xlay.x_258 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.393 | fs ff 125 C 3.6 V, pad 0.00 V | 3.393 | 3.577 | g x2d.xlay.n_i132, s x2d.xlay.n_i127, d iovdd |
| x2s.xlay.x_180 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.384 | fs ff 125 C 3.6 V, pad 0.95 V | 3.384 | 3.511 | g x2s.xlay.n_i32, s x2s.xlay.n_i22, d iovdd |
| x2s.xlay.x_189 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.384 | fs ff 125 C 3.6 V, pad 0.95 V | 3.384 | 3.511 | g x2s.xlay.n_i32, s x2s.xlay.n_i25, d iovdd |
| x2s.xlay.x_102 | S2D pad | HV-NMOS | 30/3 | no | 2.753 | pu fast fs 125 C 3.6 V, t = 1.60 us | 3.378 | fs ff 125 C 3.6 V, pad 0.00 V | 3.378 | 3.413 | g x2s.xlay.n_i13, s x2s.xlay.n_i12, d x2s.xlay.n_i14 |
| x2s.xlay.x_181 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.375 | fs ff 125 C 3.6 V, pad 0.00 V | 3.375 | 3.503 | g x2s.xlay.n_i32, s x2s.xlay.n_i21, d iovdd |
| x2s.xlay.x_188 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.375 | fs ff 125 C 3.6 V, pad 0.00 V | 3.375 | 3.503 | g x2s.xlay.n_i32, s x2s.xlay.n_i24, d iovdd |
| x2d.xlay.x_257 | D2S pad | HV-PMOS | 5/6 | no | 1.402 | en ss 125 C 3.6 V, t = 2.19 us | 3.371 | off ff 125 C 3.6 V, t = 70.00 us | 3.371 | 3.727 | g x2d.xlay.n_i132, s x2d.xlay.n_i134, d iovdd |
| xs.xr.xlay.x_19 | pad_ref_rb | HV-PMOS | 5/6 | no | 1.381 | en ss 125 C 3.6 V, t = 2.19 us | 3.366 | pu fast ff 125 C 3.6 V, t = 1.22 us | 3.124 | 3.489 | g xs.xr.xlay.n_13, s xs.xr.xlay.n_24, d vdd_3v3 |
| x2s.xlay.x_177 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.353 | fs ff 125 C 3.6 V, pad 1.20 V | 3.353 | 3.482 | g x2s.xlay.n_i32, s x2s.xlay.n_i31, d iovdd |
| x2s.xlay.x_178 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.353 | fs ff 125 C 3.6 V, pad 1.20 V | 3.353 | 3.482 | g x2s.xlay.n_i32, s x2s.xlay.n_i30, d iovdd |
| x2s.xlay.x_185 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.353 | fs ff 125 C 3.6 V, pad 1.20 V | 3.353 | 3.482 | g x2s.xlay.n_i32, s x2s.xlay.n_i27, d iovdd |
| x2s.xlay.x_186 | S2D pad | HV-PMOS | 5/6 | no | 1.419 | pu fast ss 125 C 3.6 V, t = 2.08 us | 3.353 | fs ff 125 C 3.6 V, pad 1.20 V | 3.353 | 3.482 | g x2s.xlay.n_i32, s x2s.xlay.n_i28, d iovdd |
| xs.xbg.xms1_2 | bg_core_pd | HV-PMOS | 0.5/12.5 | no | 3.322 | mode ss -40 C 3.6 V, t = 42.01 us | 3.166 | mode ss -40 C 3.6 V, t = 42.01 us | 3.322 | 3.746 | g xs.en_b, s xs.xbg.net2, d xs.xbg.net3 |

## |VDS| against the breakdown voltage

| runs | type | value | max \|VDS\| [V] | device (block, W/L um) | where | spec \|BVDSS\| min [V] | margin [V] |
|---|---|---|---|---|---|---|---|
| all 3.0 V runs | HV-NMOS | peak | 3.300 | x2s.xlay.x_43 (S2D pad, 88/0.6) | dc 1k sf -40 C 3.0 V, pad 3.30 V | 5.3 | 2.000 |
| all 3.0 V runs | HV-NMOS | held >= 100 ns | 3.300 | x2s.xlay.x_43 (S2D pad, 88/0.6) | dc 1k sf -40 C 3.0 V | 5.3 | 2.000 |
| all 3.0 V runs | HV-PMOS | peak | 3.200 | x2s.xlay.x_3 (S2D pad, 266.4/0.6) | dc 1k sf -40 C 3.0 V, pad -0.20 V | 5.3 | 2.100 |
| all 3.0 V runs | HV-PMOS | held >= 100 ns | 3.200 | x2s.xlay.x_3 (S2D pad, 266.4/0.6) | dc 1k sf -40 C 3.0 V | 5.3 | 2.100 |
| all 3.3 V runs | HV-NMOS | peak | 3.813 | xs.xd.xlay.x_6.x_7 (bias_dist_pd, 1/0.45) | off ff -40 C 3.3 V, t = 1.14 us | 5.3 | 1.487 |
| all 3.3 V runs | HV-NMOS | held >= 100 ns | 3.398 | x2d.xlay.x_209 (D2S pad, 6/6) | pu late tt 27 C 3.3 V | 5.3 | 1.902 |
| all 3.3 V runs | HV-PMOS | peak | 10.013 | xs.xbg.xms1_0 (bg_core_pd, 0.5/12.5) | en ff -40 C 3.3 V, t = 22.01 us | 5.3 | -4.713 |
| all 3.3 V runs | HV-PMOS | held >= 100 ns | 3.955 | xs.xbg.xms1_7 (bg_core_pd, 0.5/12.5) | en ff -40 C 3.3 V | 5.3 | 1.345 |
| all 3.6 V runs | HV-NMOS | peak | 4.346 | xs.xd.xlay.x_6.x_7 (bias_dist_pd, 1/0.45) | en sf -40 C 3.6 V, t = 2.11 us | 5.3 | 0.954 |
| all 3.6 V runs | HV-NMOS | held >= 100 ns | 3.706 | x2d.xlay.x_209 (D2S pad, 6/6) | pu late tt 27 C 3.6 V | 5.3 | 1.594 |
| all 3.6 V runs | HV-PMOS | peak | 10.745 | xs.xbg.xms1_0 (bg_core_pd, 0.5/12.5) | en ff 125 C 3.6 V, t = 22.01 us | 5.3 | -5.445 |
| all 3.6 V runs | HV-PMOS | held >= 100 ns | 4.283 | xs.xbg.xms1_7 (bg_core_pd, 0.5/12.5) | en ss -40 C 3.6 V | 5.3 | 1.017 |

## Top 20 devices by max of |VGS|, |VGD| held >= 100 ns, all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xc.xt10.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 4.082 | en ss -40 C 3.6 V | 4.082 | 0.591 | 3.977 | 3.682 |
| 2 | xs.xd.xlay.x_8.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.065 | en ss -40 C 3.6 V | 4.065 | 3.600 | 3.982 | 3.714 |
| 3 | xs.xd.xlay.x_5.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.974 | en ss -40 C 3.6 V | 3.974 | 2.773 | 3.856 | 3.589 |
| 4 | xs.xd.xlay.x_6.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.974 | en ss -40 C 3.6 V | 3.974 | 2.773 | 3.855 | 3.588 |
| 5 | xs.xd.xlay.x_7.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.974 | en ss -40 C 3.6 V | 3.974 | 2.773 | 3.856 | 3.588 |
| 6 | xs.xc.xt2.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.972 | en ss -40 C 3.6 V | 3.972 | 2.127 | 3.862 | 3.583 |
| 7 | xs.xc.xt3.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.972 | en ss -40 C 3.6 V | 3.972 | 3.353 | 3.862 | 3.583 |
| 8 | xs.xc.xt8.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.972 | en ss -40 C 3.6 V | 3.972 | 3.593 | 3.862 | 3.583 |
| 9 | xs.xc.xt1.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.962 | off ss -40 C 3.6 V | 3.962 | 2.430 | 3.861 | 3.565 |
| 10 | xs.xc.xt4.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.962 | off ss -40 C 3.6 V | 3.962 | 3.353 | 3.861 | 3.565 |
| 11 | xs.xc.xt7.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.962 | off ss -40 C 3.6 V | 3.962 | 3.593 | 3.861 | 3.565 |
| 12 | x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | yes | 3.800 | dc 1k ff -40 C 3.6 V | 3.800 | 3.800 | 3.800 | 3.500 |
| 13 | xs.xc.xt5.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.757 | en ss 125 C 3.6 V | 3.757 | 3.593 | 3.716 | 3.464 |
| 14 | xs.xc.xt6.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.720 | en tt 27 C 3.6 V | 3.720 | 3.593 | 3.720 | 3.434 |
| 15 | x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | yes | 3.719 | pu late tt 27 C 3.6 V | 3.719 | 1.752 | 3.719 | 3.406 |
| 16 | x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.707 | pu late tt 27 C 3.6 V | 3.707 | 1.688 | 3.707 | 3.398 |
| 17 | x2d.xlay.x_234 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.703 | pu late tt 27 C 3.6 V | 3.703 | 1.688 | 3.703 | 3.396 |
| 18 | xs.xc.xt9.xn | s7_ctrl tg_hv switches | HV-NMOS | 1/0.45 | no | 3.622 | en ff 125 C 3.6 V | 3.622 | 2.331 | 3.588 | 3.303 |
| 19 | x2s.xlay.x_192 | S2D pad | HV-PMOS | 1/0.45 | no | 3.618 | en ff 125 C 3.6 V | 3.618 | 3.030 | 3.588 | 3.302 |
| 20 | x2s.xlay.x_193 | S2D pad | HV-PMOS | 1/0.45 | no | 3.618 | en ff 125 C 3.6 V | 3.618 | 3.353 | 3.588 | 3.302 |

## Top 20 devices by |VDS| held >= 100 ns, all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | \|VDS\| held >= 100 ns [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xbg.xms1_7 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 4.283 | en ss -40 C 3.6 V | 4.283 | 2.269 | 4.198 | 3.955 |
| 2 | xs.xr.xlay.x_18 | pad_ref_rb | HV-PMOS | 5/6 | yes | 4.056 | en tt 27 C 3.6 V | 4.056 | 1.790 | 4.056 | 3.700 |
| 3 | x2s.xlay.x_179 | S2D pad | HV-PMOS | 5/6 | yes | 4.044 | off ff -40 C 3.6 V | 4.044 | 3.089 | 3.916 | 3.719 |
| 4 | x2s.xlay.x_182 | S2D pad | HV-PMOS | 5/6 | yes | 4.044 | off ff -40 C 3.6 V | 4.044 | 3.089 | 3.916 | 3.719 |
| 5 | x2s.xlay.x_187 | S2D pad | HV-PMOS | 5/6 | yes | 4.041 | off ff -40 C 3.6 V | 4.041 | 2.591 | 3.914 | 3.716 |
| 6 | x2s.xlay.x_190 | S2D pad | HV-PMOS | 5/6 | yes | 4.041 | off ff -40 C 3.6 V | 4.041 | 2.591 | 3.914 | 3.716 |
| 7 | x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | yes | 3.800 | dc 1k ff -40 C 3.6 V | 3.800 | 3.800 | 3.800 | 3.500 |
| 8 | x2d.xlay.x_257 | D2S pad | HV-PMOS | 5/6 | yes | 3.718 | pu late tt 27 C 3.6 V | 3.718 | 2.231 | 3.718 | 3.405 |
| 9 | x2d.xlay.x_209 | D2S pad | HV-NMOS | 6/6 | yes | 3.706 | pu late tt 27 C 3.6 V | 3.706 | 2.200 | 3.706 | 3.398 |
| 10 | xs.xd.xlay.x_5.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.128 | 1.931 |
| 11 | xs.xd.xlay.x_5.x_8 | bias_dist_pd | HV-PMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.128 | 1.931 |
| 12 | xs.xd.xlay.x_6.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.659 | 2.507 |
| 13 | xs.xd.xlay.x_6.x_8 | bias_dist_pd | HV-PMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.659 | 2.507 |
| 14 | xs.xd.xlay.x_7.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.403 | 2.253 |
| 15 | xs.xd.xlay.x_7.x_8 | bias_dist_pd | HV-PMOS | 1/0.45 | no | 3.674 | en ss -40 C 3.6 V | 3.674 | 0.014 | 2.403 | 2.253 |
| 16 | x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | yes | 3.602 | en ff 125 C 3.6 V | 3.602 | 2.474 | 3.602 | 3.302 |
| 17 | x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.602 | en ff 125 C 3.6 V | 3.602 | 2.474 | 3.602 | 3.302 |
| 18 | xs.xc.xild.xn | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.600 | en fs 125 C 3.6 V | 3.600 | 3.600 | 3.600 | 3.300 |
| 19 | xs.xc.xle.xi3.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.600 | en ss 125 C 3.6 V | 3.600 | 3.600 | 3.600 | 3.300 |
| 20 | xs.xc.xirc.xn | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.600 | en ff 125 C 3.6 V | 3.600 | 3.600 | 3.600 | 3.300 |

## Top 20 devices by max of |VGS|, |VGD| (peak), all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | max of \|VGS\|, \|VGD\| (peak) [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xbg.xms1_0 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 7.888 | en ff 125 C 3.6 V, t = 22.01 us | 3.600 | 3.600 | 7.196 | 7.278 |
| 2 | xs.xbg.xms1_1 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 7.888 | en ff 125 C 3.6 V, t = 22.01 us | 3.466 | 3.466 | 7.196 | 7.278 |
| 3 | xs.xc.xl4.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.490 |
| 4 | xs.xc.xl4.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.490 |
| 5 | xs.xc.xl0.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 6 | xs.xc.xl0.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 7 | xs.xc.xl1.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 8 | xs.xc.xl1.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 9 | xs.xc.xl2.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 10 | xs.xc.xl2.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 11 | xs.xc.xl3.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 12 | xs.xc.xl3.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 13 | xs.xc.xl5.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 14 | xs.xc.xl5.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 5.851 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.600 | 3.600 | 5.444 | 5.491 |
| 15 | xs.xd.xlay.x_8.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.182 | en ff -40 C 3.6 V, t = 2.11 us | 4.065 | 3.600 | 4.156 | 3.875 |
| 16 | xs.xc.xt10.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 4.094 | en ss -40 C 3.6 V, t = 2.43 us | 4.082 | 0.591 | 3.995 | 3.698 |
| 17 | xs.xd.xlay.x_5.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.085 | en ss -40 C 3.6 V, t = 2.12 us | 3.974 | 2.773 | 4.043 | 3.762 |
| 18 | xs.xd.xlay.x_6.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.085 | en ss -40 C 3.6 V, t = 2.12 us | 3.974 | 2.773 | 4.029 | 3.750 |
| 19 | xs.xd.xlay.x_7.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.085 | en ss -40 C 3.6 V, t = 2.12 us | 3.974 | 2.773 | 4.037 | 3.756 |
| 20 | xs.xc.xt4.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.974 | en ss -40 C 3.6 V, t = 22.01 us | 3.962 | 3.353 | 3.861 | 3.565 |

## Top 20 devices by |VGS| (peak), all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | \|VGS\| (peak) [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xd.xlay.x_8.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 4.182 | en ff -40 C 3.6 V, t = 2.11 us | 4.061 | 3.599 | 4.156 | 3.875 |
| 2 | xs.xc.xl5.xi3.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.817 | mode ss -40 C 3.6 V, t = 42.01 us | 3.600 | 0.000 | 3.789 | 3.483 |
| 3 | xs.xc.xl1.xi3.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.810 | mode ss -40 C 3.6 V, t = 42.01 us | 3.600 | 0.000 | 3.781 | 3.478 |
| 4 | xs.xc.xl3.xi3.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.807 | mode ss -40 C 3.6 V, t = 42.01 us | 3.600 | 0.000 | 3.735 | 3.461 |
| 5 | xs.xc.xim.xp | s7_ctrl logic | HV-PMOS | 1/0.45 | no | 3.791 | mode ss -40 C 3.6 V, t = 22.01 us | 3.600 | 0.000 | 3.750 | 3.457 |
| 6 | xs.xc.xl0.xi3.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.767 | mode ss -40 C 3.6 V, t = 42.01 us | 3.600 | 0.000 | 3.740 | 3.439 |
| 7 | xs.xc.xt7.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.757 | en ss 125 C 3.6 V, t = 4.12 us | 3.757 | 3.030 | 3.716 | 3.465 |
| 8 | xs.xc.xl0.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 9 | xs.xc.xl0.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 10 | xs.xc.xl1.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 11 | xs.xc.xl1.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 12 | xs.xc.xl2.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 13 | xs.xc.xl2.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 14 | xs.xc.xl4.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 15 | xs.xc.xl4.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 16 | xs.xc.xl5.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.743 | mode ss 125 C 3.6 V, t = 32.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 17 | xs.xc.xl5.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 32.00 us | 3.600 | 3.600 | 3.733 | 3.447 |
| 18 | xs.xc.xt8.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.720 | en tt 27 C 3.6 V, t = 7.38 us | 3.720 | 3.353 | 3.720 | 3.434 |
| 19 | xs.xc.xle.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.713 | en ss 125 C 3.6 V, t = 22.00 us | 3.600 | 0.000 | 3.708 | 3.418 |
| 20 | xs.xc.xl3.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.713 | mode ss 125 C 3.6 V, t = 2.00 us | 3.600 | 3.600 | 3.708 | 3.418 |

## Top 20 devices by |VDS| (peak), all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | \|VDS\| (peak) [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xbg.xms1_0 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 10.745 | en ff 125 C 3.6 V, t = 22.01 us | 0.683 | 0.145 | 10.186 | 10.013 |
| 2 | xs.xbg.xms1_1 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 9.032 | en ff 125 C 3.6 V, t = 22.01 us | 0.604 | 0.156 | 8.508 | 8.529 |
| 3 | xs.xc.xl4.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.452 | 0.000 | 7.759 | 7.814 |
| 4 | xs.xc.xl0.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.452 | 0.000 | 7.759 | 7.815 |
| 5 | xs.xc.xl1.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.452 | 0.000 | 7.759 | 7.815 |
| 6 | xs.xc.xl2.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.452 | 0.000 | 7.759 | 7.815 |
| 7 | xs.xc.xl3.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.451 | 0.000 | 7.759 | 7.815 |
| 8 | xs.xc.xl5.xpl1 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 8.196 | pu fast sf -40 C 3.6 V, t = 0.82 us | 3.452 | 0.000 | 7.759 | 7.815 |
| 9 | xs.xc.xl4.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 10 | xs.xc.xl0.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 11 | xs.xc.xl1.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 12 | xs.xc.xl2.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 13 | xs.xc.xl3.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 14 | xs.xc.xl5.xpl2 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 6.287 | pu fast sf -40 C 3.6 V, t = 0.82 us | 1.207 | 0.000 | 5.881 | 6.000 |
| 15 | xs.xbg.xms1_7 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 4.541 | off ff -40 C 3.6 V, t = 1.11 us | 4.283 | 2.269 | 4.471 | 4.202 |
| 16 | xs.xc.xl4.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 4.487 | pu fast tt 27 C 3.6 V, t = 0.95 us | 1.743 | 0.000 | 4.487 | 4.410 |
| 17 | xs.xc.xl0.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 4.487 | pu fast tt 27 C 3.6 V, t = 0.95 us | 1.743 | 0.000 | 4.487 | 4.410 |
| 18 | xs.xc.xl1.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 4.487 | pu fast tt 27 C 3.6 V, t = 0.95 us | 1.743 | 0.000 | 4.487 | 4.410 |
| 19 | xs.xc.xl2.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 4.487 | pu fast tt 27 C 3.6 V, t = 0.95 us | 1.743 | 0.000 | 4.487 | 4.410 |
| 20 | xs.xc.xl3.xpl4 | s7_ctrl ls_up_fs | HV-PMOS | 0.3/20 | yes | 4.487 | pu fast tt 27 C 3.6 V, t = 0.95 us | 1.743 | 0.000 | 4.487 | 4.410 |

## Top 20 devices by |VGB| (peak), all 3.6 V runs

| # | device | block | type | W/L [um] | L meets spec LG | \|VGB\| (peak) [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.3 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xc.xne.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.816 | mode ss -40 C 3.6 V, t = 42.01 us |  | 0.000 | 3.789 | 3.485 |
| 2 | xs.xc.xnm.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.810 | mode ss -40 C 3.6 V, t = 42.01 us |  | 0.000 | 3.782 | 3.480 |
| 3 | xs.xc.xnv.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.807 | mode ss -40 C 3.6 V, t = 42.01 us |  | 0.000 | 3.736 | 3.462 |
| 4 | xs.xc.xn3.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.793 | mode ss -40 C 3.6 V, t = 22.01 us |  | 0.000 | 3.751 | 3.459 |
| 5 | xs.xc.xns.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.767 | mode ss -40 C 3.6 V, t = 42.01 us |  | 0.000 | 3.741 | 3.441 |
| 6 | xs.xc.xl0.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us |  | 3.600 | 3.733 | 3.447 |
| 7 | xs.xc.xl1.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us |  | 3.600 | 3.733 | 3.447 |
| 8 | xs.xc.xl2.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us |  | 3.600 | 3.733 | 3.447 |
| 9 | xs.xc.xl4.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 42.00 us |  | 3.600 | 3.733 | 3.447 |
| 10 | xs.xc.xl5.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.743 | mode ss 125 C 3.6 V, t = 32.00 us |  | 3.600 | 3.733 | 3.447 |
| 11 | xs.xc.xle.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.713 | en ss 125 C 3.6 V, t = 22.00 us |  | 0.000 | 3.708 | 3.418 |
| 12 | xs.xc.xl3.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.713 | mode ss 125 C 3.6 V, t = 2.00 us |  | 3.600 | 3.708 | 3.418 |
| 13 | xs.xc.xi1.xp | s7_ctrl logic | HV-PMOS | 1/0.45 | no | 3.710 | mode fs 125 C 3.6 V, t = 42.01 us |  | 3.600 | 3.607 | 3.363 |
| 14 | xs.xc.xilx.xn | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode ss 125 C 3.6 V, t = 2.01 us |  | 3.600 | 3.620 | 3.386 |
| 15 | xs.xc.xnld.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |
| 16 | xs.xc.xnlx.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |
| 17 | xs.xc.xnsb.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |
| 18 | xs.xc.xnbd.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |
| 19 | xs.xc.xnrc.xna | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |
| 20 | xs.xd.xlay.x_1.x_1 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.696 | mode fs 125 C 3.6 V, t = 22.01 us |  | 3.600 | 3.694 | 3.381 |

## Top 20 devices by max of |VGS|, |VGD| held >= 100 ns, all 3.3 V runs

| # | device | block | type | W/L [um] | L meets spec LG | max of \|VGS\|, \|VGD\| held >= 100 ns [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.6 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xd.xlay.x_8.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.714 | en ff -40 C 3.3 V | 3.714 | 3.300 | 3.680 | 4.065 |
| 2 | xs.xc.xt10.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.682 | off ff -40 C 3.3 V | 3.682 | 0.589 | 3.676 | 4.082 |
| 3 | xs.xd.xlay.x_5.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.589 | off ff -40 C 3.3 V | 3.589 | 2.473 | 3.566 | 3.974 |
| 4 | xs.xd.xlay.x_7.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.588 | en ff -40 C 3.3 V | 3.588 | 2.473 | 3.565 | 3.974 |
| 5 | xs.xd.xlay.x_6.x_7 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.588 | off ff -40 C 3.3 V | 3.588 | 2.473 | 3.564 | 3.974 |
| 6 | xs.xc.xt2.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.583 | en ff -40 C 3.3 V | 3.583 | 2.028 | 3.567 | 3.972 |
| 7 | xs.xc.xt3.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.583 | en ff -40 C 3.3 V | 3.583 | 3.060 | 3.567 | 3.972 |
| 8 | xs.xc.xt8.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.583 | en ff -40 C 3.3 V | 3.583 | 3.293 | 3.567 | 3.972 |
| 9 | xs.xc.xt1.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.565 | en tt 27 C 3.3 V | 3.565 | 2.912 | 3.565 | 3.962 |
| 10 | xs.xc.xt4.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.565 | en tt 27 C 3.3 V | 3.565 | 3.060 | 3.565 | 3.962 |
| 11 | xs.xc.xt7.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.565 | en tt 27 C 3.3 V | 3.565 | 3.293 | 3.565 | 3.962 |
| 12 | x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | yes | 3.500 | dc 1k ff -40 C 3.3 V | 3.500 | 3.500 | 3.500 | 3.800 |
| 13 | xs.xc.xt5.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.464 | en ss 125 C 3.3 V | 3.464 | 3.293 | 3.429 | 3.757 |
| 14 | xs.xc.xt6.xp | s7_ctrl tg_hv switches | HV-PMOS | 1/0.45 | no | 3.434 | en tt 27 C 3.3 V | 3.434 | 3.293 | 3.434 | 3.720 |
| 15 | x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | yes | 3.406 | pu late tt 27 C 3.3 V | 3.406 | 1.455 | 3.406 | 3.719 |
| 16 | x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.398 | pu late tt 27 C 3.3 V | 3.398 | 1.392 | 3.398 | 3.707 |
| 17 | x2d.xlay.x_234 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.396 | pu late tt 27 C 3.3 V | 3.396 | 1.392 | 3.396 | 3.703 |
| 18 | xs.xc.xt9.xn | s7_ctrl tg_hv switches | HV-NMOS | 1/0.45 | no | 3.303 | en ss 125 C 3.3 V | 3.303 | 2.064 | 3.288 | 3.622 |
| 19 | x2s.xlay.x_192 | S2D pad | HV-PMOS | 1/0.45 | no | 3.302 | en ss 125 C 3.3 V | 3.302 | 2.800 | 3.288 | 3.618 |
| 20 | x2s.xlay.x_193 | S2D pad | HV-PMOS | 1/0.45 | no | 3.302 | en ss 125 C 3.3 V | 3.302 | 3.060 | 3.288 | 3.618 |

## Top 20 devices by |VDS| held >= 100 ns, all 3.3 V runs

| # | device | block | type | W/L [um] | L meets spec LG | \|VDS\| held >= 100 ns [V] | where | held >= 100 ns [V] | DC enabled only [V] | 27 C runs only [V] | all 3.6 V runs [V] |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | xs.xbg.xms1_7 | bg_core_pd | HV-PMOS | 0.5/12.5 | yes | 3.955 | en ff -40 C 3.3 V | 3.955 | 2.120 | 3.901 | 4.283 |
| 2 | x2s.xlay.x_179 | S2D pad | HV-PMOS | 5/6 | yes | 3.719 | off ff -40 C 3.3 V | 3.719 | 2.790 | 3.110 | 4.044 |
| 3 | x2s.xlay.x_182 | S2D pad | HV-PMOS | 5/6 | yes | 3.719 | off ff -40 C 3.3 V | 3.719 | 2.790 | 3.110 | 4.044 |
| 4 | x2s.xlay.x_187 | S2D pad | HV-PMOS | 5/6 | yes | 3.716 | off ff -40 C 3.3 V | 3.716 | 2.294 | 3.110 | 4.041 |
| 5 | x2s.xlay.x_190 | S2D pad | HV-PMOS | 5/6 | yes | 3.716 | off ff -40 C 3.3 V | 3.716 | 2.294 | 3.110 | 4.041 |
| 6 | xs.xr.xlay.x_18 | pad_ref_rb | HV-PMOS | 5/6 | yes | 3.700 | en ss 125 C 3.3 V | 3.700 | 1.521 | 3.686 | 4.056 |
| 7 | x2s.xlay.x_3 | S2D pad | HV-PMOS | 266.4/0.6 | yes | 3.500 | dc 1k ff -40 C 3.3 V | 3.500 | 3.500 | 3.500 | 3.800 |
| 8 | x2d.xlay.x_257 | D2S pad | HV-PMOS | 5/6 | yes | 3.405 | pu late tt 27 C 3.3 V | 3.405 | 1.933 | 3.405 | 3.718 |
| 9 | x2d.xlay.x_209 | D2S pad | HV-NMOS | 6/6 | yes | 3.398 | pu late tt 27 C 3.3 V | 3.398 | 1.901 | 3.398 | 3.706 |
| 10 | x2d.xlay.x_171 | D2S pad | HV-NMOS | 4.4/1 | yes | 3.302 | en ff -40 C 3.3 V | 3.302 | 2.178 | 3.302 | 3.602 |
| 11 | x2d.xlay.x_232 | D2S pad | HV-PMOS | 6.66/0.6 | yes | 3.302 | en ff -40 C 3.3 V | 3.302 | 2.178 | 3.302 | 3.602 |
| 12 | xs.xc.xild.xn | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.300 | en ss 125 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 13 | xs.xc.xle.xi3.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.300 | en ss 125 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 14 | xs.xc.xirc.xn | s7_ctrl logic | HV-NMOS | 1/0.45 | no | 3.300 | en ss 125 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 15 | xs.xd.xlay.x_5.x_3 | bias_dist_pd | HV-NMOS | 1/0.45 | no | 3.300 | en ss 125 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 16 | xs.xc.xle.xn1 | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.300 | en ff -40 C 3.3 V | 3.300 | 0.000 | 3.300 | 3.600 |
| 17 | xs.xc.xle.xpf | s7_ctrl ls_up_fs | HV-PMOS | 0.3/5 | yes | 3.300 | pu fast ff -40 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 18 | xs.xc.xle.xi1.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.300 | en ff -40 C 3.3 V | 3.300 | 0.000 | 3.300 | 3.600 |
| 19 | xs.xc.xle.xi1.xn | s7_ctrl ls_up_fs | HV-NMOS | 1/0.45 | no | 3.300 | dc 1k ff -40 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |
| 20 | xs.xc.xle.xi2.xp | s7_ctrl ls_up_fs | HV-PMOS | 1/0.45 | no | 3.300 | dc 1k ff -40 C 3.3 V | 3.300 | 3.300 | 3.300 | 3.600 |

## Largest |VGS|, |VGD|, |VDS| per job kind (over all devices and runs of the kind)

| job | supply [V] | runs | max \|VGS\| [V] | device, where | max \|VGD\| [V] | max \|VDS\| [V] | device, where |
|---|---|---|---|---|---|---|---|
| dc 1k | 3.0 | 2 | 3.000 | xs.xc.xle.xi2.xn 1/0.45 (dc 1k sf -40 C 3.0 V, pad 0.05 V) | 3.300 | 3.300 | x2s.xlay.x_43 88/0.6 (dc 1k sf -40 C 3.0 V, pad 3.30 V) |
| dc 1k | 3.3 | 15 | 3.300 | xs.xc.xle.xi2.xn 1/0.45 (dc 1k ff -40 C 3.3 V, pad -0.15 V) | 3.500 | 3.500 | x2s.xlay.x_3 266.4/0.6 (dc 1k ff -40 C 3.3 V, pad -0.20 V) |
| dc 1k | 3.6 | 15 | 3.600 | xs.xc.xle.xi2.xn 1/0.45 (dc 1k ff -40 C 3.6 V, pad 1.20 V) | 3.800 | 3.800 | x2s.xlay.x_3 266.4/0.6 (dc 1k ff -40 C 3.6 V, pad -0.20 V) |
| dc 1kgnd | 3.0 | 2 | 3.000 | xs.xc.xle.xi2.xn 1/0.45 (dc 1kgnd sf -40 C 3.0 V, pad 0.75 V) | 3.300 | 3.300 | x2s.xlay.x_43 88/0.6 (dc 1kgnd sf -40 C 3.0 V, pad 3.30 V) |
| dc 1kgnd | 3.3 | 15 | 3.300 | xs.xc.xle.xi2.xn 1/0.45 (dc 1kgnd ff -40 C 3.3 V, pad -0.00 V) | 3.500 | 3.500 | x2s.xlay.x_3 266.4/0.6 (dc 1kgnd ff -40 C 3.3 V, pad -0.20 V) |
| dc 1kgnd | 3.6 | 15 | 3.600 | xs.xc.xle.xi2.xn 1/0.45 (dc 1kgnd ff -40 C 3.6 V, pad -0.15 V) | 3.800 | 3.800 | x2s.xlay.x_3 266.4/0.6 (dc 1kgnd ff -40 C 3.6 V, pad -0.20 V) |
| dc open | 3.0 | 1 | 3.000 | xs.xc.xle.xi2.xn 1/0.45 (dc open sf -40 C 3.0 V, pad 0.10 V) | 3.300 | 3.300 | x2s.xlay.x_43 88/0.6 (dc open sf -40 C 3.0 V, pad 3.30 V) |
| dc open | 3.3 | 15 | 3.300 | xs.xc.xle.xi2.xn 1/0.45 (dc open ff -40 C 3.3 V, pad 0.35 V) | 3.500 | 3.500 | x2s.xlay.x_3 266.4/0.6 (dc open ff -40 C 3.3 V, pad -0.20 V) |
| dc open | 3.6 | 15 | 3.600 | xs.xc.xle.xi2.xn 1/0.45 (dc open ff -40 C 3.6 V, pad 0.45 V) | 3.800 | 3.800 | x2s.xlay.x_3 266.4/0.6 (dc open ff -40 C 3.6 V, pad -0.20 V) |
| en | 3.3 | 3 | 3.875 | xs.xd.xlay.x_8.x_7 1/0.45 (en ff -40 C 3.3 V, t = 2.14 us) | 7.278 | 10.013 | xs.xbg.xms1_0 0.5/12.5 (en ff -40 C 3.3 V, t = 22.01 us) |
| en | 3.6 | 7 | 4.182 | xs.xd.xlay.x_8.x_7 1/0.45 (en ff -40 C 3.6 V, t = 2.11 us) | 7.888 | 10.745 | xs.xbg.xms1_0 0.5/12.5 (en ff 125 C 3.6 V, t = 22.01 us) |
| fs | 3.3 | 12 | 3.300 | x2d.xlay.x_2 7.96/32.16 (fs ff 125 C 3.3 V, pad 0.00 V) | 3.300 | 3.300 | x2s.xlay.x_3 266.4/0.6 (fs ff 125 C 3.3 V, pad 0.00 V) |
| fs | 3.6 | 11 | 3.600 | x2d.xlay.x_2 7.96/32.16 (fs ff -40 C 3.6 V, pad 0.00 V) | 3.600 | 3.600 | x2s.xlay.x_3 266.4/0.6 (fs ff -40 C 3.6 V, pad 0.00 V) |
| fs0 | 3.3 | 15 | 0.812 | x2s.xlay.x_3 266.4/0.6 (fs0 ss -40 C 3.3 V, pad 3.30 V) | 0.812 | 0.812 | x2s.xlay.x_3 266.4/0.6 (fs0 ss -40 C 3.3 V, pad 3.30 V) |
| fs0 | 3.6 | 15 | 0.828 | x2s.xlay.x_3 266.4/0.6 (fs0 ss -40 C 3.6 V, pad 3.60 V) | 0.828 | 0.828 | x2s.xlay.x_3 266.4/0.6 (fs0 ss -40 C 3.6 V, pad 3.60 V) |
| fst | 3.3 | 5 | 3.300 | x2d.xlay.x_2 7.96/32.16 (fst ff -40 C 3.3 V, t = 2.00 us) | 3.300 | 3.300 | x2s.xlay.x_3 266.4/0.6 (fst ff -40 C 3.3 V, t = 1.00 us) |
| fst | 3.6 | 5 | 3.600 | x2d.xlay.x_2 7.96/32.16 (fst ff -40 C 3.6 V, t = 2.00 us) | 3.600 | 3.600 | x2s.xlay.x_3 266.4/0.6 (fst ff -40 C 3.6 V, t = 1.00 us) |
| mode | 3.3 | 2 | 3.483 | xs.xc.xl5.xi3.xp 1/0.45 (mode ss 125 C 3.3 V, t = 42.01 us) | 3.483 | 4.020 | xs.xc.xl0.xpl1 0.3/20 (mode tt 27 C 3.3 V, t = 42.01 us) |
| mode | 3.6 | 5 | 3.817 | xs.xc.xl5.xi3.xp 1/0.45 (mode ss -40 C 3.6 V, t = 42.01 us) | 3.817 | 4.306 | xs.xc.xl0.xpl1 0.3/20 (mode tt 27 C 3.6 V, t = 42.01 us) |
| off | 3.3 | 2 | 3.875 | xs.xd.xlay.x_8.x_7 1/0.45 (off ff -40 C 3.3 V, t = 1.14 us) | 3.875 | 4.201 | xs.xbg.xms1_7 0.5/12.5 (off ff -40 C 3.3 V, t = 1.14 us) |
| off | 3.6 | 7 | 4.182 | xs.xd.xlay.x_8.x_7 1/0.45 (off ff -40 C 3.6 V, t = 1.11 us) | 4.182 | 4.541 | xs.xbg.xms1_7 0.5/12.5 (off ff -40 C 3.6 V, t = 1.11 us) |
| pu | 3.3 | 2 | 3.300 | xs.xc.xle.xi2.xn 1/0.45 (pu ff -40 C 3.3 V, t = 10.00 us) | 3.300 | 3.300 | xs.xc.xle.xi1.xn 1/0.45 (pu ff -40 C 3.3 V, t = 10.00 us) |
| pu | 3.6 | 4 | 3.600 | xs.xc.xle.xi2.xn 1/0.45 (pu ff -40 C 3.6 V, t = 10.00 us) | 3.600 | 3.600 | xs.xc.xle.xi1.xn 1/0.45 (pu ff -40 C 3.6 V, t = 10.00 us) |
| pu fast | 3.3 | 3 | 3.301 | xs.xc.xle.xi2.xn 1/0.45 (pu fast tt 27 C 3.3 V, t = 1.07 us) | 5.491 | 7.815 | xs.xc.xl0.xpl1 0.3/20 (pu fast ss 125 C 3.3 V, t = 0.88 us) |
| pu fast | 3.6 | 7 | 3.601 | xs.xc.xle.xi2.xn 1/0.45 (pu fast ss 125 C 3.6 V, t = 1.16 us) | 5.851 | 8.196 | xs.xc.xl4.xpl1 0.3/20 (pu fast sf -40 C 3.6 V, t = 0.82 us) |
| pu late | 3.3 | 1 | 3.385 | xs.xc.xt7.xp 1/0.45 (pu late tt 27 C 3.3 V, t = 13.21 us) | 3.586 | 5.690 | xs.xbg.xms1_0 0.5/12.5 (pu late tt 27 C 3.3 V, t = 20.07 us) |
| pu late | 3.6 | 1 | 3.666 | xs.xc.xt7.xp 1/0.45 (pu late tt 27 C 3.6 V, t = 14.09 us) | 3.884 | 5.782 | xs.xbg.xms1_0 0.5/12.5 (pu late tt 27 C 3.6 V, t = 20.07 us) |
| step 100p | 3.3 | 3 | 3.300 | xs.xc.xild.xp 1/0.45 (step 100p ss 125 C 3.3 V, t = 12.01 us) | 3.501 | 3.500 | x2s.xlay.x_3 266.4/0.6 (step 100p ff -40 C 3.3 V, t = 12.01 us) |
| step 100p | 3.6 | 7 | 3.600 | xs.xc.xnld.xna 1/0.45 (step 100p ff 125 C 3.6 V, t = 12.01 us) | 3.801 | 3.800 | x2s.xlay.x_3 266.4/0.6 (step 100p ff -40 C 3.6 V, t = 12.01 us) |
| step open | 3.3 | 3 | 3.300 | xs.xc.xild.xp 1/0.45 (step open ss 125 C 3.3 V, t = 12.01 us) | 3.501 | 3.500 | x2s.xlay.x_3 266.4/0.6 (step open ff -40 C 3.3 V, t = 12.01 us) |
| step open | 3.6 | 7 | 3.600 | xs.xc.xnld.xna 1/0.45 (step open ff 125 C 3.6 V, t = 12.01 us) | 3.801 | 3.800 | x2s.xlay.x_3 266.4/0.6 (step open ff -40 C 3.6 V, t = 12.01 us) |

## Node extremes (transients and DC): highest node voltage and lowest node voltage per job kind

| job | supply [V] | highest node [V] | node (where) | lowest node [V] | node (where) |
|---|---|---|---|---|---|
| dc 1k | 3.0 | 3.300 | v(padin) (dc 1k sf -40 C 3.0 V, pad 3.30 V) | -0.200 | v(padin) (dc 1k sf -40 C 3.0 V, pad -0.20 V) |
| dc 1k | 3.3 | 3.300 | v(en0) (dc 1k ff -40 C 3.3 V, pad 2.70 V) | -0.200 | v(padin) (dc 1k ff -40 C 3.3 V, pad -0.20 V) |
| dc 1k | 3.6 | 3.600 | v(en0) (dc 1k ff -40 C 3.6 V, pad 1.05 V) | -0.200 | v(padin) (dc 1k ff -40 C 3.6 V, pad -0.20 V) |
| dc 1kgnd | 3.0 | 3.300 | v(padin) (dc 1kgnd sf -40 C 3.0 V, pad 3.30 V) | -0.200 | v(padin) (dc 1kgnd sf -40 C 3.0 V, pad -0.20 V) |
| dc 1kgnd | 3.3 | 3.300 | v(en0) (dc 1kgnd ff -40 C 3.3 V, pad 0.85 V) | -0.200 | v(padin) (dc 1kgnd ff -40 C 3.3 V, pad -0.20 V) |
| dc 1kgnd | 3.6 | 3.600 | v(en0) (dc 1kgnd ff -40 C 3.6 V, pad -0.15 V) | -0.200 | v(padin) (dc 1kgnd ff -40 C 3.6 V, pad -0.20 V) |
| dc open | 3.0 | 3.300 | v(padin) (dc open sf -40 C 3.0 V, pad 3.30 V) | -0.200 | v(padin) (dc open sf -40 C 3.0 V, pad -0.20 V) |
| dc open | 3.3 | 3.300 | v(en0) (dc open ff -40 C 3.3 V, pad 1.35 V) | -0.200 | v(padin) (dc open ff -40 C 3.3 V, pad -0.20 V) |
| dc open | 3.6 | 3.600 | v(en0) (dc open ff -40 C 3.6 V, pad 0.55 V) | -0.200 | v(padin) (dc open ff -40 C 3.6 V, pad -0.20 V) |
| en | 3.3 | 5.033 | v(xs.xbg.net1) (en ff -40 C 3.3 V, t = 2.13 us) | -6.713 | v(xs.xbg.net1) (en ff -40 C 3.3 V, t = 22.01 us) |
| en | 3.6 | 5.502 | v(xs.xbg.net1) (en ff -40 C 3.6 V, t = 2.10 us) | -7.145 | v(xs.xbg.net1) (en ff 125 C 3.6 V, t = 22.01 us) |
| fs | 3.3 | 3.300 | v(iovdd) (fs ff 125 C 3.3 V, pad 0.00 V) | -0.000 | v(xs.xbg.g) (fs sf 27 C 3.3 V, pad 0.00 V) |
| fs | 3.6 | 3.600 | v(iovdd) (fs ff -40 C 3.6 V, pad 0.00 V) | -0.000 | v(xs.xbg.g) (fs ss 27 C 3.6 V, pad 0.00 V) |
| fs0 | 3.3 | 0.812 | v(padin) (fs0 ss -40 C 3.3 V, pad 3.30 V) | -0.000 | v(xs.xbg.vpc) (fs0 fs 125 C 3.3 V, pad 0.00 V) |
| fs0 | 3.6 | 0.828 | v(padin) (fs0 ss -40 C 3.6 V, pad 3.60 V) | -0.000 | v(xs.xbg.vpc) (fs0 fs 125 C 3.6 V, pad 0.00 V) |
| fst | 3.3 | 3.300 | v(x2d.xlay.n_i5) (fst ss -40 C 3.3 V, t = 4.67 us) | -0.000 | v(x2d.xlay.n_i113) (fst sf -40 C 3.3 V, t = 1.05 us) |
| fst | 3.6 | 3.600 | v(x2d.xlay.n_i5) (fst ss -40 C 3.6 V, t = 4.55 us) | -0.000 | v(padin) (fst ss -40 C 3.6 V, t = 1.00 us) |
| mode | 3.3 | 4.045 | v(xs.xc.xl0.l2) (mode tt 27 C 3.3 V, t = 2.01 us) | -0.935 | v(xs.xc.xl0.l1) (mode tt 27 C 3.3 V, t = 52.18 us) |
| mode | 3.6 | 4.349 | v(xs.xc.xl0.l2) (mode ss -40 C 3.6 V, t = 2.01 us) | -0.513 | v(xs.xc.xl4.l1) (mode ff 125 C 3.6 V, t = 52.17 us) |
| off | 3.3 | 5.033 | v(xs.xbg.net1) (off ff -40 C 3.3 V, t = 1.13 us) | -1.077 | v(xs.xc.xle.l1) (off ff -40 C 3.3 V, t = 1.14 us) |
| off | 3.6 | 5.510 | v(xs.xbg.net1) (off ff -40 C 3.6 V, t = 1.10 us) | -0.635 | v(xs.xc.xle.l1) (off ff -40 C 3.6 V, t = 1.11 us) |
| pu | 3.3 | 3.300 | v(xs.xd.xlay.n_30) (pu ff -40 C 3.3 V, t = 10.05 us) | -0.961 | v(xs.xc.xl0.l1) (pu tt 27 C 3.3 V, t = 5.98 us) |
| pu | 3.6 | 3.600 | v(xs.xd.xlay.n_30) (pu ff -40 C 3.6 V, t = 10.05 us) | -1.112 | v(xs.xc.xl0.l1) (pu tt 27 C 3.6 V, t = 5.69 us) |
| pu fast | 3.3 | 3.306 | v(x2d.xlay.n_i122) (pu fast tt 27 C 3.3 V, t = 1.50 us) | -5.491 | v(xs.xc.xl0.l1) (pu fast ss 125 C 3.3 V, t = 0.88 us) |
| pu fast | 3.6 | 3.611 | v(x2d.xlay.n_i122) (pu fast ss -40 C 3.6 V, t = 1.35 us) | -5.851 | v(xs.xc.xl4.l1) (pu fast sf -40 C 3.6 V, t = 0.82 us) |
| pu late | 3.3 | 4.005 | v(xs.xc.xle.l5) (pu late tt 27 C 3.3 V, t = 20.10 us) | -2.390 | v(xs.xbg.net1) (pu late tt 27 C 3.3 V, t = 20.07 us) |
| pu late | 3.6 | 4.301 | v(xs.xc.xle.l5) (pu late tt 27 C 3.6 V, t = 20.10 us) | -2.182 | v(xs.xbg.net1) (pu late tt 27 C 3.6 V, t = 20.07 us) |
| step 100p | 3.3 | 3.401 | v(x2s.xlay.n_i9) (step 100p ff -40 C 3.3 V, t = 2.01 us) | -0.200 | v(padin) (step 100p ff -40 C 3.3 V, t = 12.01 us) |
| step 100p | 3.6 | 3.711 | v(x2s.xlay.n_i9) (step 100p ff 125 C 3.6 V, t = 2.01 us) | -0.200 | v(padin) (step 100p ff -40 C 3.6 V, t = 12.01 us) |
| step open | 3.3 | 3.401 | v(x2s.xlay.n_i9) (step open ff -40 C 3.3 V, t = 2.01 us) | -0.200 | v(padin) (step open ff -40 C 3.3 V, t = 12.01 us) |
| step open | 3.6 | 3.711 | v(x2s.xlay.n_i9) (step open ff 125 C 3.6 V, t = 2.01 us) | -0.200 | v(padin) (step open ff -40 C 3.6 V, t = 12.01 us) |
