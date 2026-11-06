# sg13cmos5l_cm_slot7 — Chipalooza slot 7 delivery repository

This repository holds exactly what the Chipalooza harness (`sg13cmos5l_ocd_chipalooza`) reads for **slot 7**:
the slot layout `final/gds/slot_7.gds` (top cell `slot_7`) and two **custom I/O pad cells** that replace the
analog pads `s7_an[0]` and `s7_an[1]` of slot 7. It has one branch, `main`, and no inherited history, so that a
`git submodule add` of it stays small.

**`slot_7.gds` is a plumbing stand-in.** It contains only the 13 pin shapes at the slot's right edge, so that
the harness flow can be tested end to end. The real slot circuit follows in a later commit of this repository.

The design work lives in [`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single);
the files here are copies from fixed commits of it (table below).

## Files and provenance

Source repository for every file: `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`.
`T` = branch `toplevel` @ `91a7da8b67ac56a26c605501146667a1fde28c32`,
`H` = branch `harness-test` @ `4611357166b7368be4fbf8e176b1e82b8a9a85d0`.

| file here | commit | source path | sha256 (of the source file) |
|---|---|---|---|
| `LICENSE` | T | `LICENSE` | `a7fd04ca6fa87a80afd79015999a48e6e5db4966926af0a69182cb8c2d836d9f` |
| `final/gds/slot_7.gds` | H | `final/gds/slot_7.gds` | `5624ae45efb7761fd0b405ecc785a3f2f3c3a93d93203d0aaca9feb15bedc11c` |
| `final/lef/slot_7.lef` | H | `final/lef/slot_7.lef` | `9fd8d5b1c57d7a2d26ad8e4883d8634f5dec4bfc36a9026ad9becc5401c9d8a8` |
| `final/lib/slot_7.lib` | H | `final/lib/slot_7.lib` | `6137d6230046318850c9f1fba2d8e79322ce28d9e18f0e2e64385099c419bd56` |
| `final/vh/slot_7.vh` | H | `final/vh/slot_7.vh` | `1ba0f560eb7b9e23258d2f371b1e8ab0936b4103aeb7ccaece69990c75086976` |
| `final/pads/sg13cmos5l_IOPadDiff2Single.gds` | T | `macros/sg13cmos5l_IOPadDiff2Single/layout/klayout/sg13cmos5l_IOPadDiff2Single.klay.gds` | `13e176ab106d0cb307a6ebc42acf647ce38b6abc52183a9f1d9ffead2f6c2b17` |
| `final/pads/sg13cmos5l_IOPadSingle2Diff.gds` | T | `macros/sg13cmos5l_IOPadSingle2Diff/layout/klayout/sg13cmos5l_IOPadSingle2Diff.klay.gds` | `f4b0e07320821248872780b344d71845d08bc250a4bfc9bcf8633a39bdef0182` |
| `final/pads/sg13cmos5l_IOPadDiff2Single.spice` | T | `macros/sg13cmos5l_IOPadDiff2Single/netlist/schematic/sg13cmos5l_IOPadDiff2Single_magic.spice` | `b8d9103230bd7ced5c75a0fb38d56f078ec3cbf48d0f82a3772b85ff1edc2c1c` |
| `final/pads/sg13cmos5l_IOPadSingle2Diff.spice` | T | `macros/sg13cmos5l_IOPadSingle2Diff/netlist/schematic/sg13cmos5l_IOPadSingle2Diff_magic.spice` | `5a4e67f9b12f5f9017978ad0da4305fb331c9aa3abf4657ec48f5c77a8d32810` |
| `final/pads/pads.txt` | — | written here (manifest) | — |

All files are byte copies, except that each `.spice` file starts with a 4-line `*` comment carrying its provenance;
without those 4 lines it is identical to the source. The pad GDS files are the KLayout `.klay.gds` files renamed to
`.gds`; their top cell is named like the file. Sub-cells inside the pad GDS are **not** renamed here — the harness
prefixes them on import (`scripts/custom_io_uniquify.py`). No LEF is supplied for the pads: the harness test showed
none is needed (`FIXED_BBOX 0 0 80 180` is set on import).

## Pad cells

`final/pads/pads.txt` lists, per pad cell, the `config.txt` pad it replaces and its core-side pins in order along the
core edge. Every pad cell also has the ring pins `iovdd iovss vdd vss` and the bond pad `pad`.

| cell | replaces | core-side pins |
|---|---|---|
| `sg13cmos5l_IOPadSingle2Diff` | `s7_an[0]` | vref outp outn vcm en_3v3 en_3v3_b iref |
| `sg13cmos5l_IOPadDiff2Single` | `s7_an[1]` | vinp vinn vref iref en_3v3_b en_3v3 |

The `config.txt` lines for slot 7:

```
s7_an[0]:  sg13cmos5l_IOPadSingle2Diff  s7_an_0
s7_an[1]:  sg13cmos5l_IOPadDiff2Single  s7_an_1
```

### Known LVS note (`vss` pin)

Quoted from `macros/sg13cmos5l_IOPadDiff2Single/README.md` of the design repository (commit T):

> Magic keeps one name for the joined net, so netgen ends with "Top level cell failed pin matching" on `vss`. Accepted by
> Christoph on 2026-11-03. Everything else matches.

Background in the same README: the cell's `vss` p+ tie and the `iovss` ties share the p-substrate, so `vss` and
`iovss` are one net in the extracted layout. The `sg13cmos5l_IOPadSingle2Diff` cell has the same mismatch for the same
reason; IHP's own `IOPadAnalog` shows the same merge in the harness's magic + netgen LVS.

## Slot 7 pin table

From `macros/slot/harness_test/slot7_pins.md` (commit H, sha256
`a4a2897c359e04caa45a575ad3a874eda0e30780dab9c1dc33f4dade907f7de9`). All pins Metal3 at the right edge,
x 535.050..536.450 um, slot-local coordinates (origin = lower left of the 537.15 x 273 um slot).

| signal | pad | pad pin | y0 (um) | y1 (um) |
|---|---|---|---|---|
| s7_an_0_vref | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | vref | 112.115 | 112.405 |
| s7_an_0_outp | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | outp | 123.725 | 124.015 |
| s7_an_0_outn | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | outn | 129.825 | 130.115 |
| s7_an_0_vcm | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | vcm | 135.875 | 136.165 |
| s7_an_0_en_3v3 | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | en_3v3 | 142.505 | 142.795 |
| s7_an_0_en_3v3_b | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | en_3v3_b | 153.695 | 153.985 |
| s7_an_0_iref | s7_an[0] (sg13cmos5l_IOPadSingle2Diff) | iref | 159.365 | 159.655 |
| s7_an_1_vinp | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | vinp | 222.115 | 222.405 |
| s7_an_1_vinn | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | vinn | 222.655 | 222.945 |
| s7_an_1_vref | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | vref | 223.195 | 223.485 |
| s7_an_1_iref | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | iref | 260.455 | 260.745 |
| s7_an_1_en_3v3_b | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | en_3v3_b | 260.995 | 261.285 |
| s7_an_1_en_3v3 | s7_an[1] (sg13cmos5l_IOPadDiff2Single) | en_3v3 | 261.535 | 261.825 |

## License

Solderpad Hardware License v2.1, see `LICENSE`.
