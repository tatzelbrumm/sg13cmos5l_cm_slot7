<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
solver aid: none
-->

# CACE Summary for sg13cmos5l_IOPadDiff2Single

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Gain                 | ngspice              | Gain                 |            0.49 |          ​ |          any |          ​ |         0.51 |          ​ |   Skip 🟧    |
| Output offset        | ngspice              | Vos_out              |           -5 mV |          ​ |          any |          ​ |         5 mV |          ​ |   Skip 🟧    |
| Integral nonlinearity | ngspice              | INL                  |             any |          ​ |          any |          ​ |        10 mV |          ​ |   Skip 🟧    |
| IO ring supply current | ngspice              | Iio                  |             any |          ​ |          any |          ​ |       400 uA |          ​ |   Skip 🟧    |
| Core ring supply current | ngspice              | Icore                |             any |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| Quiescent current OP | ngspice              | IqP                  |          150 uA |          ​ |          any |          ​ |       300 uA |          ​ |   Skip 🟧    |
| Quiescent current ON | ngspice              | IqN                  |          150 uA |          ​ |          any |          ​ |       300 uA |          ​ |   Skip 🟧    |
| Minimum output-device current | ngspice              | Imin                 |           30 uA |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain                 | ngspice              | Gain                 |            0.49 |   0.498241 |          any |   0.499951 |         0.51 |   0.500198 |   Pass ✅    |
| Output offset        | ngspice              | Vos_out              |           -5 mV |   0.032 mV |          any |   0.048 mV |         5 mV |   1.769 mV |   Pass ✅    |
| Integral nonlinearity | ngspice              | INL                  |             any |  11.101 mV |          any |  44.951 mV |          any |  88.418 mV |   Pass ✅    |
| IO ring supply current | ngspice              | Iio                  |             any | 295.799 uA |          any | 301.128 uA |       400 uA | 308.780 uA |   Pass ✅    |
| Core ring supply current | ngspice              | Icore                |             any |   0.008 nA |          any |   0.118 nA |       100 nA |  23.889 nA |   Pass ✅    |
| Quiescent current OP | ngspice              | IqP                  |          150 uA | 211.035 uA |          any | 216.067 uA |       300 uA | 223.260 uA |   Pass ✅    |
| Quiescent current ON | ngspice              | IqN                  |          150 uA | 210.630 uA |          any | 216.017 uA |       300 uA | 223.219 uA |   Pass ✅    |
| Minimum output-device current | ngspice              | Imin                 |           30 uA |  62.832 uA |          any |  82.958 uA |          any | 100.660 uA |   Pass ✅    |
| Gain                 | ngspice              | Gain                 |            0.49 |          ​ |          any |          ​ |         0.51 |          ​ |   Skip 🟧    |
| Output offset        | ngspice              | Vos_out              |           -5 mV |          ​ |          any |          ​ |         5 mV |          ​ |   Skip 🟧    |
| Integral nonlinearity | ngspice              | INL                  |             any |          ​ |          any |          ​ |        10 mV |          ​ |   Skip 🟧    |
| IO ring supply current | ngspice              | Iio                  |             any |          ​ |          any |          ​ |       500 uA |          ​ |   Skip 🟧    |
| Core ring supply current | ngspice              | Icore                |             any |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| Quiescent current OP | ngspice              | IqP                  |          100 uA |          ​ |          any |          ​ |       350 uA |          ​ |   Skip 🟧    |
| Quiescent current ON | ngspice              | IqN                  |          100 uA |          ​ |          any |          ​ |       350 uA |          ​ |   Skip 🟧    |
| Minimum output-device current | ngspice              | Imin                 |           30 uA |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain                 | ngspice              | Gain                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output offset        | ngspice              | Vos_out              |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Integral nonlinearity | ngspice              | INL                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring supply current | ngspice              | Iio                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Core ring supply current | ngspice              | Icore                |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Quiescent current OP | ngspice              | IqP                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Quiescent current ON | ngspice              | IqN                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Minimum output-device current | ngspice              | Imin                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain                 | ngspice              | Gain                 |            0.49 |          ​ |          any |          ​ |         0.51 |          ​ |   Skip 🟧    |
| Output offset        | ngspice              | Vos_out              |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Integral nonlinearity | ngspice              | INL                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring supply current | ngspice              | Iio                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Core ring supply current | ngspice              | Icore                |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Quiescent current OP | ngspice              | IqP                  |          120 uA |          ​ |          any |          ​ |       350 uA |          ​ |   Skip 🟧    |
| Quiescent current ON | ngspice              | IqN                  |          120 uA |          ​ |          any |          ​ |       350 uA |          ​ |   Skip 🟧    |
| Minimum output-device current | ngspice              | Imin                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Closed-loop gain     | ngspice              | Acl_dB               |         -6.2 dB |          ​ |          any |          ​ |     -5.85 dB |          ​ |   Skip 🟧    |
| Bandwidth            | ngspice              | f3dB                 |           1 MHz |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain peaking         | ngspice              | Peak_dB              |             any |          ​ |          any |          ​ |         1 dB |          ​ |   Skip 🟧    |
| PSRR iovdd 1 kHz     | ngspice              | PSRR_1k              |           60 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| PSRR iovdd 100 kHz   | ngspice              | PSRR_100k            |           25 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| CMRR 1 kHz           | ngspice              | CMRR_1k              |           70 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output impedance 1 kHz | ngspice              | Zout_1k              |             any |          ​ |          any |          ​ |         10 Ω |          ​ |   Skip 🟧    |
| Output impedance 1 MHz | ngspice              | Zout_1M              |             any |          ​ |          any |          ​ |        300 Ω |          ​ |   Skip 🟧    |
| Bandwidth            | ngspice              | f3dB                 |           1 MHz |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain peaking         | ngspice              | Peak_dB              |             any |          ​ |          any |          ​ |         4 dB |          ​ |   Skip 🟧    |
| Bandwidth, 1 nF      | ngspice              | f3dB                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain peaking, 1 nF   | ngspice              | Peak_dB              |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Slew rate, rising    | ngspice              | SR_rise              |          1 V/us |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Slew rate, falling   | ngspice              | SR_fall              |          1 V/us |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Overshoot            | ngspice              | Overshoot            |             any |          ​ |          any |          ​ |         15 % |          ​ |   Skip 🟧    |
| Settling time, rising | ngspice              | ts_rise              |             any |          ​ |          any |          ​ |         1 us |          ​ |   Skip 🟧    |
| Settling time, falling | ngspice              | ts_fall              |             any |          ​ |          any |          ​ |         1 us |          ​ |   Skip 🟧    |
| THD                  | ngspice              | THD                  |             any |          ​ |          any |          ​ |       -35 dB |          ​ |   Skip 🟧    |
| Output amplitude     | ngspice              | Vout_amp             |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output noise 1 kHz   | ngspice              | En_1k                |             any |          ​ |          any |          ​ | 1000 nV/rtHz |          ​ |   Skip 🟧    |
| Output noise 100 kHz | ngspice              | En_100k              |             any |          ​ |          any |          ​ |  200 nV/rtHz |          ​ |   Skip 🟧    |
| Integrated output noise | ngspice              | Vn_int               |             any |          ​ |          any |          ​ |       300 uV |          ​ |   Skip 🟧    |
| Max output           | ngspice              | Vout_max             |           3.0 V |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Min output           | ngspice              | Vout_min             |             any |          ​ |          any |          ​ |        0.9 V |          ​ |   Skip 🟧    |
| Short-circuit source current | ngspice              | Isc_src              |           20 mA |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Short-circuit sink current | ngspice              | Isc_snk              |           20 mA |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring current, off | ngspice              | Iio_pd               |             any |          ​ |          any |          ​ |      1000 nA |          ​ |   Skip 🟧    |
| Core ring current, off | ngspice              | Icore_pd             |             any |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| Pad leakage, off     | ngspice              | Ipad_pd              |         -100 nA |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| vdd1v2_sense current | ngspice              | Is12_pd              |             any |          ​ |          any |          ​ |      2000 nA |          ​ |   Skip 🟧    |
| vdd3v3_sense current | ngspice              | Is33_pd              |             any |          ​ |          any |          ​ |      2000 nA |          ​ |   Skip 🟧    |
| Internal enable      | ngspice              | Ven3                 |             any |          ​ |          any |          ​ |        0.1 V |          ​ |   Skip 🟧    |
| Turn-on time         | ngspice              | t_on                 |             any |          ​ |          any |          ​ |         5 us |          ​ |   Skip 🟧    |
| Enable glitch, positive | ngspice              | Glitch_max           |             any |          ​ |          any |          ​ |       400 mV |          ​ |   Skip 🟧    |
| Enable glitch, negative | ngspice              | Glitch_min           |         -400 mV |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring current after start-up | ngspice              | Iio_end              |          200 uA |          ​ |          any |          ​ |       400 uA |          ​ |   Skip 🟧    |
| Output offset - mismatch | ngspice              | Vos_out              |          -20 mV |          ​ |          any |          ​ |        20 mV |          ​ |   Skip 🟧    |
| Gain - mismatch      | ngspice              | Gain                 |            0.49 |          ​ |          any |          ​ |         0.51 |          ​ |   Skip 🟧    |
| Quiescent current OP - mismatch | ngspice              | IqP                  |          100 uA |          ​ |          any |          ​ |       400 uA |          ​ |   Skip 🟧    |

