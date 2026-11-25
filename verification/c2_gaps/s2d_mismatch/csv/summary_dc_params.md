<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
CACE 2.11 summary of this run (IHP sg13cmos5l simulation, design 91a7da8b)
-->

# CACE Summary for sg13cmos5l_IOPadSingle2Diff

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Gain                 | ngspice              | Gain                 |            1.99 |    1.99849 |            2 |    1.99898 |         2.01 |     1.9993 |   Pass ✅    |
| Input offset (systematic) | ngspice              | Vos_in               |           -1 mV |  -0.000 mV |         0 mV |  -0.000 mV |         1 mV |   0.001 mV |   Pass ✅    |
| Integral nonlinearity | ngspice              | INL                  |             any |   0.087 mV |          any |   0.163 mV |         2 mV |   1.069 mV |   Pass ✅    |
| Output common-mode error | ngspice              | Vcm_err              |          -30 mV |   5.003 mV |          any |  10.491 mV |        30 mV |  18.050 mV |   Pass ✅    |
| IO ring current      | ngspice              | Iio                  |             any | 114.640 uA |          any | 115.536 uA |       135 uA | 116.860 uA |   Pass ✅    |
| Gain vs vref and vcm | ngspice              | Gain                 |             any |          ​ |            2 |          ​ |          any |          ​ |   Skip 🟧    |
| Integral nonlinearity vs vref and vcm | ngspice              | INL                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output common-mode error vs vref and vcm | ngspice              | Vcm_err              |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Input range, low end | ngspice              | Vin_min              |             any |          ​ |          any |          ​ |        0.1 V |          ​ |   Skip 🟧    |
| Input range, high end | ngspice              | Vin_max              |           1.0 V |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain vs bias select  | ngspice              | Gain                 |            1.99 |          ​ |            2 |          ​ |         2.01 |          ​ |   Skip 🟧    |
| Input offset (systematic) vs bias select | ngspice              | Vos_in               |           -1 mV |          ​ |         0 mV |          ​ |         1 mV |          ​ |   Skip 🟧    |
| Integral nonlinearity vs bias select | ngspice              | INL                  |             any |          ​ |          any |          ​ |         2 mV |          ​ |   Skip 🟧    |
| Output common-mode error vs bias select | ngspice              | Vcm_err              |          -30 mV |          ​ |          any |          ​ |        30 mV |          ​ |   Skip 🟧    |
| IO ring current vs bias select | ngspice              | Iio                  |             any |          ​ |          any |          ​ |       220 uA |          ​ |   Skip 🟧    |
| Gain, sel 11         | ngspice              | Gain                 |             any |          ​ |            2 |          ​ |          any |          ​ |   Skip 🟧    |
| Input offset (systematic), sel 11 | ngspice              | Vos_in               |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Integral nonlinearity, sel 11 | ngspice              | INL                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output common-mode error, sel 11 | ngspice              | Vcm_err              |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring current, sel 11 | ngspice              | Iio                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Gain vs ibias        | ngspice              | Gain                 |            1.99 |          ​ |            2 |          ​ |         2.01 |          ​ |   Skip 🟧    |
| Input offset (systematic) vs ibias | ngspice              | Vos_in               |           -1 mV |          ​ |         0 mV |          ​ |         1 mV |          ​ |   Skip 🟧    |
| Integral nonlinearity vs ibias | ngspice              | INL                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output common-mode error vs ibias | ngspice              | Vcm_err              |          -30 mV |          ​ |          any |          ​ |        30 mV |          ​ |   Skip 🟧    |
| IO ring current vs ibias | ngspice              | Iio                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Closed-loop gain at 1 kHz | ngspice              | Acl_dB               |             any |          ​ |      6.02 dB |          ​ |          any |          ​ |   Skip 🟧    |
| Closed-loop -3 dB bandwidth | ngspice              | f3dB                 |           1 MHz |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output common-mode response to iovdd at 1 kHz | ngspice              | CMvdd_1k             |             any |          ​ |          any |          ​ |       -30 dB |          ​ |   Skip 🟧    |
| PSRR iovdd at 1 kHz (input-referred), mismatch | ngspice              | PSRRp_1k             |           60 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| PSRR iovdd at 100 kHz (input-referred), mismatch | ngspice              | PSRRp_100k           |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| PSRR iovss at 1 kHz (input-referred), mismatch | ngspice              | PSRRn_1k             |           60 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| PSRR iovss at 100 kHz (input-referred), mismatch | ngspice              | PSRRn_100k           |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| CMRR at 1 kHz (pad and vref together), mismatch | ngspice              | CMRR_1k              |           70 dB |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Rise time 10-90 %    | ngspice              | t_rise               |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Settling time to 1 % | ngspice              | t_settle             |             any |          ​ |          any |          ​ |      1000 ns |          ​ |   Skip 🟧    |
| Overshoot            | ngspice              | Overshoot            |             any |          ​ |          any |          ​ |          5 % |          ​ |   Skip 🟧    |
| Largest output common-mode deviation during the step | ngspice              | Vcm_dev              |             any |          ​ |          any |          ​ |        50 mV |          ​ |   Skip 🟧    |
| Input noise density at 1 kHz | ngspice              | En_1k                |             any |          ​ |          any |          ​ | 1000 nV/rtHz |          ​ |   Skip 🟧    |
| Input noise density at 100 kHz | ngspice              | En_100k              |             any |          ​ |          any |          ​ |  250 nV/rtHz |          ​ |   Skip 🟧    |
| Differential output noise, 10 Hz - 10 MHz | ngspice              | Vn_out               |             any |          ​ |          any |          ​ |      1000 uV |          ​ |   Skip 🟧    |
| IO ring current, off | ngspice              | Iio_pd               |             any |          ​ |          any |          ​ |      1000 nA |          ​ |   Skip 🟧    |
| Core ring current, off | ngspice              | Icore_pd             |             any |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| Pad input leakage, off | ngspice              | Ipad_pd              |         -100 nA |          ​ |          any |          ​ |       100 nA |          ​ |   Skip 🟧    |
| Internal enable      | ngspice              | Ven3                 |             any |          ​ |          any |          ​ |        0.1 V |          ​ |   Skip 🟧    |
| Differential output, off | ngspice              | Vod_pd               |           -1 mV |          ​ |          any |          ​ |         1 mV |          ​ |   Skip 🟧    |
| Output common mode, off | ngspice              | Voc_pd               |           -1 mV |          ​ |          any |          ​ |         1 mV |          ​ |   Skip 🟧    |
| Enable time          | ngspice              | t_on                 |             any |          ​ |          any |          ​ |         3 us |          ​ |   Skip 🟧    |
| Output CM glitch, high | ngspice              | Vc_max               |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Output CM glitch, low | ngspice              | Vc_min               |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Differential output at the end | ngspice              | Vd_end               |             any |          ​ |        0.5 V |          ​ |          any |          ​ |   Skip 🟧    |
| IO ring current, enabled | ngspice              | Iio_on               |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Input offset - Mismatch | ngspice              | Vos_in               |          -20 mV |          ​ |          any |          ​ |        20 mV |          ​ |   Skip 🟧    |
| Gain - Mismatch      | ngspice              | Gain                 |            1.93 |          ​ |          any |          ​ |         2.07 |          ​ |   Skip 🟧    |
| Output common-mode error - Mismatch | ngspice              | Vcm_err              |          -60 mV |          ​ |          any |          ​ |        60 mV |          ​ |   Skip 🟧    |
| Input offset - Process MC | ngspice              | Vos_in               |           -5 mV |          ​ |          any |          ​ |         5 mV |          ​ |   Skip 🟧    |
| Gain - Process MC    | ngspice              | Gain                 |            1.99 |          ​ |          any |          ​ |         2.01 |          ​ |   Skip 🟧    |
| Output common-mode error - Process MC | ngspice              | Vcm_err              |          -30 mV |          ​ |          any |          ​ |        30 mV |          ​ |   Skip 🟧    |

