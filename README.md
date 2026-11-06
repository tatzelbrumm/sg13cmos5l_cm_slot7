# sg13cmos5l_cm_slot7 — Chipalooza slot 7 delivery repository

This repository holds what the Chipalooza harness (`sg13cmos5l_ocd_chipalooza`) reads for **slot 7**:
the slot layout `final/gds/slot_7.gds` (top cell `slot_7`) and two **custom I/O pad cells** (`pads/`) that
replace the analog pads `s7_an[0]` and `s7_an[1]` of slot 7. `macros/` holds building blocks of the slot's inner
circuit (the two bias cores); the harness does not read them. It has one branch, `main`, and no inherited history,
so that a `git submodule add` of it stays small.

**`slot_7.gds` is the slot-7 test platform for the two bias references (stage A, branch `claude/c5-testplatform`).**
It needs no custom pad: the Oguey–Aebischer core `oa_core_pd` and the Banba bandgap core `bg_core_pd`, each with a
fail-safe 3.3 V enable (`dig_in[0]` / `dig_in[1]`, AND `enable`, AND the slot's `vdd_1v2` present), drive their output
current (~5 uA, sourced) through a bare hv transmission gate (`xgate`, enabled by `dig_in[2]` / `dig_in[3]`, also
fail-safe) onto `analog_bus0` / `analog_bus1`. An SMU on the chip pin `analog[0]` / `analog[1]` measures them;
`dig_out[3:0]` read the four enables back (SPI reg 0x38). Procedure, pin map, results: design repository
`docs/slot7_testplatform/` (PLAN.md, SUMMARY.md). The frame, the 13 custom-pad pins at the right edge and their
stand-in stubs and wiring are unchanged from the previous `slot_7.gds` (sha256 5624ae45...), so it fits the
custom-pad wrapper as before; the platform stays at x < 145 um. Ports, `slot_7.lib` and `slot_7.vh` are unchanged.

The design work lives in [`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single);
the files here are copies from fixed commits of it (table below).

## Files and provenance

Source repository for every file: `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`.
`T` = branch `toplevel` @ `91a7da8b67ac56a26c605501146667a1fde28c32`,
`H` = branch `harness-test` @ `4611357166b7368be4fbf8e176b1e82b8a9a85d0`,
`P` = branch `claude/c5-slot7-testplatform` @ `a665f66336e842abefbefaee35e6df1c91510f19`.

| file here | commit | source path | sha256 (of the source file) |
|---|---|---|---|
| `LICENSE` | T | `LICENSE` | `a7fd04ca6fa87a80afd79015999a48e6e5db4966926af0a69182cb8c2d836d9f` |
| `final/gds/slot_7.gds` | H | `final/gds/slot_7.gds` | `5624ae45efb7761fd0b405ecc785a3f2f3c3a93d93203d0aaca9feb15bedc11c` |
| `final/lef/slot_7.lef` | H | `final/lef/slot_7.lef` | `9fd8d5b1c57d7a2d26ad8e4883d8634f5dec4bfc36a9026ad9becc5401c9d8a8` |
| `final/lib/slot_7.lib` | H | `final/lib/slot_7.lib` | `6137d6230046318850c9f1fba2d8e79322ce28d9e18f0e2e64385099c419bd56` |
| `final/vh/slot_7.vh` | H | `final/vh/slot_7.vh` | `1ba0f560eb7b9e23258d2f371b1e8ab0936b4103aeb7ccaece69990c75086976` |
| `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds` | T | `macros/sg13cmos5l_IOPadDiff2Single/layout/klayout/sg13cmos5l_IOPadDiff2Single.klay.gds` | `13e176ab106d0cb307a6ebc42acf647ce38b6abc52183a9f1d9ffead2f6c2b17` |
| `pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.gds` | T | `macros/sg13cmos5l_IOPadSingle2Diff/layout/klayout/sg13cmos5l_IOPadSingle2Diff.klay.gds` | `f4b0e07320821248872780b344d71845d08bc250a4bfc9bcf8633a39bdef0182` |
| `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.spice` | T | `macros/sg13cmos5l_IOPadDiff2Single/netlist/schematic/sg13cmos5l_IOPadDiff2Single_magic.spice` | `b8d9103230bd7ced5c75a0fb38d56f078ec3cbf48d0f82a3772b85ff1edc2c1c` |
| `pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.spice` | T | `macros/sg13cmos5l_IOPadSingle2Diff/netlist/schematic/sg13cmos5l_IOPadSingle2Diff_magic.spice` | `5a4e67f9b12f5f9017978ad0da4305fb331c9aa3abf4657ec48f5c77a8d32810` |
| `pads/pads.txt` | — | written here (manifest) | — |
| `macros/bg_core_pd/`, `macros/oa_core_pd/` | `toplevel` @ cf88683 | `macros/<cell>/...` | see "Bias cores" below |

All files are byte copies, except that each `.spice` file starts with a 4-line `*` comment carrying its provenance;
without those 4 lines it is identical to the source. The pad GDS files are the KLayout `.klay.gds` files renamed to
`.gds`; their top cell is named like the file. Sub-cells inside the pad GDS are **not** renamed here — the harness
prefixes them on import (`scripts/custom_io_uniquify.py`). No LEF is supplied for the pads: the harness test showed
none is needed (`FIXED_BBOX 0 0 80 180` is set on import).

## Pad cells

`pads/pads.txt` lists, per pad cell, the `config.txt` pad it replaces and its core-side pins in order along the
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

## Bias cores for the slot's inner circuit

`macros/bg_core_pd/` and `macros/oa_core_pd/` are the two reference-current cores that will feed the pads' `iref`
pins from inside slot 7. They are building blocks for `slot_7.gds`: no harness script reads them. Since branch
`claude/c5-testplatform` both are placed in `slot_7.gds` (sub-cells `slot7_oa_core_pd`, `slot7_bg_core_pd`; every
sub-cell of `slot_7.gds` has the prefix `slot7_`).

| cell | what | size (um) | ports |
|---|---|---|---|
| `bg_core_pd` | Banba current-mode bandgap (pnpMPA, rhigh), no op-amp | 47.55 x 50.05 | vdd vss iout en_3v3 en_3v3_b |
| `oa_core_pd` | Oguey–Aebischer, MOS only (weak inversion) | 40.51 x 58.135 | vdd vss iout en_3v3 en_3v3_b |

Both *source* about 5 uA out of `iout`, into an NMOS input diode. That is what each pad's `iref` pin is: the input of the
pad's own `bias_tree_pd`. Disabled (`en_3v3` = 0), `iout` is high-Z, so disabled cores may share one output node. They
run on 3.3 V (`vdd` = the slot's gated `vdd_3v3`); their enables are 3.3 V signals. The selector `bias_gen_pd` of the design
repository (harness `ibias` / OA / BG / both, by `sel1 sel0`) has a schematic but no layout yet.
Layout: Metal1/Metal2 only; `vdd` rail (Metal1) on top, `vss` at the bottom, `iout en_3v3 en_3v3_b` as Metal2 pins on the
right edge, so the two cores can abut.

Each directory keeps the design repository's paths, so its README's relative links still work. Copied from
`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single` branch `toplevel` @ `cf88683b74ce1284ddc7cd327c4effeb771606a3`
(content identical at `4611357`): README, layout GDS, LVS netlist (`netlist/schematic/*_magic.spice`), extracted netlist,
xschem `.sch` / `.sym` / `xschemrc`, and the committed magic DRC and LVS reports. Not copied: the Makefile (it needs the
template repository around it) and the PEX netlists.

Checked here (2026-11-06): KLayout DRC with the PDK deck (FEOL+BEOL), 0 violations for both; magic + netgen LVS
(`sak-lvs.sh`, as the macros' `make magic-lvs`), "Circuits match uniquely" for both (bg 29 devices / 21 nets, oa 28 / 22).

| file | sha256 |
|---|---|
| `macros/bg_core_pd/README.md` | `1323e7217dd3eddba48c1683a8d341404ba3fb788070bce3ee9d747cd218fc0d` |
| `macros/bg_core_pd/layout/gds/bg_core_pd.gds` | `c799ffb5464610edb334b764305cbbb305ec3f31863f8990cb7f606ab08be10c` |
| `macros/bg_core_pd/netlist/schematic/bg_core_pd_magic.spice` | `a2f6d9d8385f0de4073eefe74219bf57dc49bc8694b284508bf1cc06ec392a9f` |
| `macros/bg_core_pd/netlist/layout/bg_core_pd_magic.ext.spc` | `8650e4ab046df41f366890da79ec7053855b93e2cc03afdef55c34f901488c6d` |
| `macros/bg_core_pd/schematic/xschem/bg_core_pd.sch` | `bd3e1864c9cc6444b6ce42dd4152ae3b6bfc767c910580a39adfae5b6b074a0b` |
| `macros/bg_core_pd/schematic/xschem/bg_core_pd.sym` | `ba65ec364875a3cb4d70f4cee9fbb417cd65314087ab379bf3001327526ca137` |
| `macros/bg_core_pd/schematic/xschem/xschemrc` | `02ebdf0b026bba540dbe5963947261d1c1166ae470913ace15b2297c03b53471` |
| `macros/bg_core_pd/verification/drc/bg_core_pd.magic.drc/bg_core_pd.magic.drc.rpt` | `1603b8cbf81c51020bf43734988113e68a6ad9034db4e092fd1b54acac2ad9d9` |
| `macros/bg_core_pd/verification/lvs/bg_core_pd.magic.lvs/bg_core_pd.lvs.out` | `1a94d96d1f008811b75310728e656059a00bb70f9b58b9dfb26b58674c38bb7d` |
| `macros/oa_core_pd/README.md` | `fbf6b04836ed49c40d104c361086565c9c5d3360b07b57346669b9f142312cf5` |
| `macros/oa_core_pd/layout/gds/oa_core_pd.gds` | `22ad9f9552e4d5807310f8277f0db17de9e7ddb7e77bda91a0cc740c9bc2039f` |
| `macros/oa_core_pd/netlist/schematic/oa_core_pd_magic.spice` | `2bead4323fb461c08e081f514583fa554eac5c298fd8c549cad472d1e3be3d0d` |
| `macros/oa_core_pd/netlist/layout/oa_core_pd_magic.ext.spc` | `55b1bcc7339c25ab95e58ca37a46ed605dece1a25f9354f4e24251607872bc8d` |
| `macros/oa_core_pd/schematic/xschem/oa_core_pd.sch` | `2963b25ec6e351c7638bc818e1b731f144ac7bcda5d6808e808205b41a3ab11c` |
| `macros/oa_core_pd/schematic/xschem/oa_core_pd.sym` | `47028f93b57be1c2ac6df64a3d325cb43a1273536d4454ed0c9f483fd5881b6b` |
| `macros/oa_core_pd/schematic/xschem/xschemrc` | `02ebdf0b026bba540dbe5963947261d1c1166ae470913ace15b2297c03b53471` |
| `macros/oa_core_pd/verification/drc/oa_core_pd.magic.drc/oa_core_pd.magic.drc.rpt` | `7a45eb866cb7d88e11053dc8b95494cceeccdab203ffb9f2cba5985fbeaaa35b` |
| `macros/oa_core_pd/verification/lvs/oa_core_pd.magic.lvs/oa_core_pd.lvs.out` | `3e372812cd1d3eccb5df91a31707444bdf728151b9e429f867e37e10ffd225ed` |

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

## Test platform checks (branch `claude/c5-testplatform`, 2026-11-06)

In the design repository (commit P): PDK KLayout DRC (feol + beol) of `slot_7.gds`: 0; magic + netgen LVS against the
platform netlist: "Netlists match uniquely" (104 devices, 72 nets), with the known port errors of the unchanged stubs
(`s7_an_0_outp` / `_outn` joined to `s7_an_1_vinp` / `_vinn`) and of the frame's Metal2 `vss_1v2` strip (not connected
inside the slot, as before). Harness flow on the fork branch `claude/c5-testplatform-test`: see that branch's
`docs/custom_pads/RUNLOG.md`.
