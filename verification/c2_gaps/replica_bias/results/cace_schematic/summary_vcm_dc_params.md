
# CACE Summary for pad_ref_rb

**netlist source**: schematic

|      Parameter       |         Tool         |     Result      | Min Limit  |  Min Value   | Typ Target |  Typ Value   | Max Limit  |  Max Value   |  Status  |
| :------------------- | :------------------- | :-------------- | ---------: | -----------: | ---------: | -----------: | ---------: | -----------: | :------: |
| Vcm: output, iovdd 3.3 / 3.6 V | ngspice              | Vcm                  |         1.031 V |    1.242 V |          any |    1.295 V |       1.53 V |    1.395 V |   Pass ✅    |
| Vref                 | ngspice              | Vref                 |             any |    0.437 V |          any |    0.494 V |          any |    0.596 V |   Pass ✅    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |  18.986 uA |          any |  19.114 uA |        25 uA |  19.260 uA |   Pass ✅    |
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
| Vcm: mismatch (tt 27 C 3.3 V) | ngspice              | Vcm                  |           1.2 V |          ​ |          any |          ​ |       1.32 V |          ​ |   Skip 🟧    |
| Vref: mismatch (tt 27 C 3.3 V) | ngspice              | Vref                 |          0.47 V |          ​ |          any |          ​ |       0.52 V |          ​ |   Skip 🟧    |
| Supply current (tree + both blocks, without the reference) | ngspice              | Ib                   |             any |          ​ |          any |          ​ |        25 uA |          ​ |   Skip 🟧    |

