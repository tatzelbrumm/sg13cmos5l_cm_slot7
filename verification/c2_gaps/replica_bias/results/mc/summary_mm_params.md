
# CACE Summary for pad_ref_rb

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Vcm: output, iovdd 3.3 / 3.6 V | ngspice              | Vcm                  |         1.031 V |          ​ |          any |          ​ |       1.53 V |          ​ |   Skip 🟧    |
| Vref                 | ngspice              | Vref                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |
| Vcm: output, iovdd 3.0 V | ngspice              | Vcm                  |         1.031 V |          ​ |          any |          ​ |      1.262 V |          ​ |   Skip 🟧    |
| Vref                 | ngspice              | Vref                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |
| Vcm: output, OA core / bandgap core, 3.0 V | ngspice              | Vcm                  |         1.031 V |          ​ |          any |          ​ |      1.244 V |          ​ |   Skip 🟧    |
| Vref                 | ngspice              | Vref                 |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        35 uA |          ​ |   Skip 🟧    |
| Vcm                  | ngspice              | Vcm                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Vref: output at 27 C (pad range from 0 V) | ngspice              | Vref                 |          0.47 V |          ​ |          any |          ​ |       0.51 V |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |
| Vcm                  | ngspice              | Vcm                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Vref: output at 125 C (above the S2D input INL edge, <= 0.542 V) | ngspice              | Vref                 |          0.55 V |          ​ |          any |          ​ |        0.7 V |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |
| Vcm                  | ngspice              | Vcm                  |             any |          ​ |          any |          ​ |          any |          ​ |   Skip 🟧    |
| Vref: output at -40 C (pad range from 0 V) | ngspice              | Vref                 |          0.35 V |          ​ |          any |          ​ |        0.5 V |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |
| Vcm: disabled        | ngspice              | Vcm                  |             any |          ​ |          any |          ​ |      0.001 V |          ​ |   Skip 🟧    |
| Vref: disabled       | ngspice              | Vref                 |             any |          ​ |          any |          ​ |      0.001 V |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |       0.1 uA |          ​ |   Skip 🟧    |
| Vcm: mismatch (tt 27 C 3.3 V) | ngspice              | Vcm                  |           1.2 V |    1.247 V |          any |    1.261 V |       1.32 V |    1.274 V |   Pass ✅    |
| Vref: mismatch (tt 27 C 3.3 V) | ngspice              | Vref                 |          0.47 V |    0.481 V |          any |    0.493 V |       0.52 V |    0.502 V |   Pass ✅    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |  18.762 uA |          any |  19.051 uA |        25 uA |  19.419 uA |   Pass ✅    |

