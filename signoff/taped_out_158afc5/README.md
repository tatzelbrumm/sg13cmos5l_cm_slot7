<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Sign-off re-run of the taped-out slot 7 (`158afc5`), 2026-11-25

DRC and LVS of the **taped-out** `final/gds/slot_7.gds` (v3 + tughra art, top cell `slot_7`) and of the two pad cells in
`pads/`, re-run on 2026-11-25 with the PDK decks and tools listed below. Until now the results for this GDS existed only as text
in `../../README.md` (2026-11-08); `../slot_7/layout/klayout/slot_7_checks.txt` covers v3 **without** the art. Every number
below was read from the tool output in `reports/`; nothing was carried over from the designer's records.

Inputs (sha256, checked by `run_signoff.sh` against the provenance table of `../../README.md`: all three equal):

| input | sha256 |
|---|---|
| `final/gds/slot_7.gds` | `469f2327c4bc22b1d6fc1785fab2fd3830b6050e51989b361dc11b26be669c05` (= README "this file") |
| `pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.gds` | `f4b0e07320821248872780b344d71845d08bc250a4bfc9bcf8633a39bdef0182` |
| `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds` | `13e176ab106d0cb307a6ebc42acf647ce38b6abc52183a9f1d9ffead2f6c2b17` |
| `netlist/slot_7.cdl` | `af1e5f027f9f90c1d44d30faa886eb630bf789e194d9210e9ad2cf5a1b9028e8` |
| `netlist/slot_7_netgen.spice` / `netlist/netgen_check.sh` | `a1e08178…` / `6cd4e7b4…` (full values in `reports/versions.txt`) |

## Results

S2D = `sg13cmos5l_IOPadSingle2Diff`, D2S = `sg13cmos5l_IOPadDiff2Single`. "Expected" is the designer's record
(`../../README.md`, `../README.md`, `../../docs/chipalooza2_as_taped_out/README.md` §5). Files are in `reports/`.

| check | tool | result | expected | file |
|---|---|---|---|---|
| slot_7 DRC, designer's flags (`run_drc.py --no_density`: main deck + maximal deck) | KLayout 0.30.12, PDK deck | **0 violations** in 546 rule categories; 0 "exception" / "Traceback" / "ERROR" log lines | no violations, 0 exception lines | `slot_7.drc.txt`, `slot_7.drc.slot_7_slot_7_full.lyrdb` |
| slot_7 maximal deck, `-rd latchUpRules=true` | KLayout, `sg13cmos5l_maximal.drc` | **0** in 271 categories (incl. LU.a/c/c1/d/d1 and 56 OffGrid rules); 0 exception lines | 0 | `slot_7.maxlu.txt`, `slot_7.maxlu.slot_7_maximal_lu.lyrdb` |
| slot_7 density (`run_drc.py --density_only`) | KLayout, `density.drc` | **7 violations, 1 each**: AFil.g (Activ 4.01 % < 35), GFil.g (GatPoly 3.64 % < 15), M1.j (2.01 %), M2.j (0.94 %), M3.j (2.47 %), M4.j (0.98 %) < 35, TM1.c (TopMetal1 7.04 % < 25); no max-density rule violated | the same 7 min-density rules (unfilled slot, filled at chip level) | `slot_7.density.txt`, `slot_7.density.slot_7_slot_7_density.lyrdb` |
| slot_7 antenna (`run_drc.py --antenna_only`, step `antenna`, added 2026-11-25) | KLayout, `antenna.drc` | **0 violations** in 23 categories (Ant.a … Ant.i, cumulative ratios per metal and via); 0 exception lines | 0 | `slot_7.antenna.txt`, `slot_7.antenna.slot_7_slot_7_antenna.lyrdb` |
| slot_7 LVS vs `netlist/slot_7.cdl`, `--run_mode=deep --disable_tap_extraction` | KLayout, `run_lvs.py` | **"Congratulations! Netlists match."**, strict port mode; runner: layout = **497** devices; cross-reference: 6 circuits Match, 376 device pairs (after simplification), 0 not matching, 35 top pin pairs, 0 not matching | match, strict ports, 0 port errors, 497 devices | `slot_7.lvs.txt`, `slot_7.lvs.slot_7.lvsdb` |
| slot_7 magic + netgen (`netlist/netgen_check.sh`, unchanged) | magic 8.3.685, netgen 1.5.324 | **5 subcircuits "Netlists match uniquely"** (bg_core_pd 29 devices, pad_ref_rb 33, s7_ctrl 222, s7_doutpd 12, bias_dist_pd 75); top `slot_7`: "match uniquely with port errors", one pin without partner: **`vss_1v2_uq0`**; 4 pin rows flagged `**Mismatch**` are the comma-named merged ports (same net, other name); "Final result: Top level cell failed pin matching." | 5 match; top: one port error `vss_1v2_uq0` | `slot_7.netgen.txt`, `slot_7.netgen.comp_slot_7.out` |
| slot_7 magic DRC, `drc(full)` (`sak-drc.sh -m`) | magic 8.3.685 | **COUNT 48**, all "Metal1 overlap of Via1 < 0.005um (V1.c - M2.c)", at 8 places (6 markers each) in `bg_core_pd/bg_pmir_pcas_c` (x ≈ 333.55 and 376.38 µm, y 186.9–200.0 µm) | not recorded for the slot; `bg_core_pd` committed report: COUNT 0 | `slot_7.magicdrc.txt`, `slot_7.magicdrc.slot_7.magic.drc.rpt` |
| cross-check: `macros/bg_core_pd` magic DRC | magic 8.3.685 | **COUNT 48**, the same rule (see "Differences") | COUNT 0 (`../bg_core_pd/…/bg_core_pd.magic.drc.rpt`) | `bg_core_pd.magicdrc.txt` |
| S2D / D2S DRC, `run_drc.py --no_density` | KLayout | **0 / 0** violations (546 categories each), 0 exception lines | 0 (committed `.lyrdb`, T) | `S2D.drc.txt`, `D2S.drc.txt` |
| S2D / D2S maximal + latch-up | KLayout | **0 / 0** (271 categories each) | not recorded | `S2D.maxlu.txt`, `D2S.maxlu.txt` |
| S2D / D2S density | KLayout | **4 each**: M1.j, M2.j (min 35 %: S2D 17.37 / 15.41 %, D2S 24.31 / 18.74 %), M3.k, M4.k (max 60 %: 81.3 / 81.2 %) | not recorded | `S2D.density.txt`, `D2S.density.txt` |
| S2D / D2S antenna (`run_drc.py --antenna_only`, added 2026-11-25) | KLayout | **0 / 0** in 23 categories each | 0 | `S2D.antenna.txt`, `D2S.antenna.txt` and their `.lyrdb` |
| S2D / D2S KLayout LVS (deep, no tap extraction) against a CDL derived from `pads/*/*.spice` | KLayout | **match / match**, strict port mode; 76 / 77 device pairs, all Match; 10 / 9 pin pairs, all Match | Match, 76 / 77 device pairs (committed `.lvsdb`, T) | `S2D.lvs.txt`, `D2S.lvs.txt`, `*.netlist.*.cdl` |
| S2D / D2S KLayout LVS against `pads/*/*.spice` **as given** | KLayout | **no match**: schematic side has 0 devices (the X-card primitives are not read as devices) | — (diagnostic) | `S2D.lvs_spice_as_given.txt`, `D2S.lvs_spice_as_given.txt` |
| S2D / D2S magic + netgen (`sak-lvs.sh -m`) | magic, netgen | 76 devices / 37 nets and 76 / 36 on both sides, "Netlists match with 7 symmetries with property errors", "Final result: Top level cell failed pin matching", only `vss` without partner (the `vss`–`iovss` substrate merge). The `.lvs.out` files are **byte-identical** to the committed ones | only the documented vss / iovss merge | `S2D.netgen.txt`, `D2S.netgen.txt` |
| S2D / D2S magic DRC | magic | **COUNT 0 / 0**; reports byte-identical to the committed ones | COUNT 0 | `S2D.magicdrc.txt`, `D2S.magicdrc.txt` |

Run times (wall, 2 KLayout threads, other jobs on the machine): slot_7 DRC 27 s, maximal + latch-up 21 s, density 4 s,
LVS 7 s, magic DRC 2 s, `netgen_check.sh` 1 s; pads 13–26 s for each KLayout DRC, ≤ 6 s for the rest. The whole
`run_signoff.sh` took 163 s. Per run: `reports/runtimes.txt`.

## Versions

From `reports/versions.txt`: KLayout 0.30.12 (binary and Python module); magic 8.3.685 (git `bed8d4ff`); netgen 1.5.324
(git `abe6117e`); Python 3.13.18; IIC-OSIC-TOOLS 2026.10 (`68d3f07e`) for `sak-drc.sh` / `sak-lvs.sh`;
PDK `ihp-sg13cmos5l` from `iic-jku/IHP-Open-PDK` at **`df4c5054ee8ca481c3eb873687274f28cdb50b1e`** (2026-10-14, "Merge pull
request #1261 …fix/precheck-min-rules", `git describe`: `v0.3.0-1049-gdf4c5054`), sparse checkout, work tree clean; one dangling
symlink under `libs.tech/klayout` (`README.md` → `ihp-sg13g2`), none in `tech/drc` or `tech/lvs`.

## How to reproduce

```
export PDK_ROOT=/foss/pdks PDK=ihp-sg13cmos5l      # defaults of the script
signoff/taped_out_158afc5/run_signoff.sh /path/to/rundir          # all steps; THR=2 KLayout threads
signoff/taped_out_158afc5/run_signoff.sh /path/to/rundir lvs summary   # single steps: env drc maxlu density lvs magicdrc netgen summary
cp /path/to/rundir/summary/* signoff/taped_out_158afc5/reports/   # how reports/ was made
```

The script writes only into the run directory. Per cell it runs (exact command lines with paths in `reports/runtimes.txt`):

```
python3 $KLT/drc/run_drc.py --path=<gds> --topcell=<top> --run_dir=<d> --no_density --mp=1 --density_thr=2
klayout -b -r $KLT/drc/rule_decks/sg13cmos5l_maximal.drc -rd input=<gds> -rd topcell=<top> -rd run_mode=deep \
        -rd thr=2 -rd threads=2 -rd latchUpRules=true -rd report=<lyrdb> -rd log=<log>
python3 $KLT/drc/run_drc.py --path=<gds> --topcell=<top> --run_dir=<d> --density_only --density_thr=2
python3 $KLT/lvs/run_lvs.py --layout=<gds> --netlist=<cdl> --topcell=<top> --run_dir=<d> --run_mode=deep --disable_tap_extraction
sh /foss/tools/sak/sak-drc.sh -m -w <d> <gds>                                   # magic DRC, drc(full)
bash <copy of netlist/>/netgen_check.sh                                         # slot_7: slot_7.gds copied next to it
sh /foss/tools/sak/sak-lvs.sh -m -s pads/<c>/<c>.spice -l pads/<c>/<c>.gds -c <c> -w <d>   # pads
```

with `KLT=$PDK_ROOT/$PDK/libs.tech/klayout/tech`. `summarize.py` then reads every `.lyrdb` (rule categories, items per
category), `.lvsdb` (cross-reference status of every circuit, device, net and pin pair), the magic and netgen reports, and
scans all logs for "exception", "Traceback" and "ERROR", so a bare "Passed" of the runner is never the only evidence.

## What differs from the designer's records, and why

1. **PDK commit.** The designer recorded KLayout 0.30.12 and "PDK `ihp-sg13cmos5l` decks" but no PDK commit; this run used
   `df4c5054`. The KLayout results agree with the records in every number, so no deck difference shows.
2. **"497 devices"** is the runner's layout-side count per circuit definition before alignment ("Devices to compare:
   layout=497 schematic=234"); the cross-reference after netlist simplification has 376 device pairs, all Match. Both numbers
   come from the same run.
3. **Maximal deck, two ways.** Inside `run_drc.py` the maximal deck runs 230 rules; standalone, 286 rule outputs
   (271 report categories). The 56 extra are its OffGrid rules: `run_drc.py` passes `no_offgrid=false`, and
   `sg13cmos5l_maximal.drc` sets `$offGridRules = ($no_offgrid == "true")`, i.e. the switch acts inverted there, so the
   designer's `--no_density` run skips the maximal deck's own OffGrid rules (the main deck's off-grid table does run,
   "OFFGRID enabled: true"). Both runs: 0 violations.
4. **magic DRC of the slot: 48 markers** ("Metal1 overlap of Via1 < 0.005um"), not in any record (the designer recorded
   no magic DRC of the slot). They sit in `bg_pmir_pcas_c` of `bg_core_pd`, where two Via1 cuts 0.22 µm apart, each on its own
   Metal1 strip, share one Metal2 strip; the markers cover the 0.2 µm Metal1 gap between the cuts. The stand-alone
   `macros/bg_core_pd/layout/gds/bg_core_pd.gds` gives the same 48 today, although its committed report says COUNT 0, and
   `bg_pmir_pcas_c` in the slot is identical to the macro's (flat XOR 0 on Metal1, Via1, Metal2). So the difference comes
   from the magic version / tech file, not from the art or the slot. KLayout's V1.c and M2.c pass. That magic merges the two
   cuts into one contact area is a likely explanation; it was not verified. The art is far from these places (art x 88.5–246.5 µm).
5. **Pad KLayout LVS netlist.** `pads/*/*.spice` is the magic/netgen netlist; it instances the PDK devices as X cards,
   which KLayout reads as calls of undefined subcircuits, so the schematic side ends up with 0 devices and no match
   (kept as `*.lvs_spice_as_given.txt`). `spice2cdl.py` renames only the X cards of PDK primitives to M / R / D cards
   (S2D: 34 + 33 MOS, 6 rhigh, 2 rppd, 2 + 2 antenna diodes); with that CDL both pads match. The design repository's
   KLayout LVS CDL (xschem `lvs_netlist 1`) is not in this repository, so its equality to the derived CDL is not shown.
   In KLayout LVS the pad pins `vdd` and `vss` drop out: no device of the pad netlist connects to them, so the netlist
   simplification removes them, and the `vss`–`iovss` merge (seen by netgen) does not show there.
6. **Pad density** was not recorded before: M1/M2 below the minimum and M3/M4 above the 60 % maximum (81 %) as stand-alone
   cells; density is evaluated at chip level.

Not done here: chip-level DRC / LVS with the harness (antenna effects of the chip-level routing included), PEX. The antenna
rules above are checked per cell (slot and pads), added on 2026-11-25 as step `antenna` of `run_signoff.sh`.

## Files

| file | what |
|---|---|
| `run_signoff.sh` | runs every check above |
| `summarize.py` | writes the summaries from a run directory |
| `spice2cdl.py` | derives the pad CDL for KLayout LVS (see 5) |
| `reports/summary.txt` | one line per check, then all summaries |
| `reports/<cell>.<check>.txt` | summary per check (command, exit code, wall time, counts, log scan) |
| `reports/<cell>.<check>.<file>` | copies of the tool reports (all < 2 MB; the two `lvs_spice_as_given` `.lvsdb` only by sha256) |
| `reports/files.txt` | bytes and sha256 of every result file of the run, and whether it was copied |
| `reports/versions.txt`, `reports/runtimes.txt` | tool versions, PDK commit, input sha256; commands, exit codes, times |

The summaries (`*.txt` written by `summarize.py`) carry SPDX headers. The copied tool reports (`.lyrdb`, `.lvsdb`, `.rpt`,
`.out`, `.log`, derived `.cdl`) do not, so that they stay byte-identical to the tool output (sha256 in `reports/files.txt`), as
for the other reports in `../`. Exit code 1 of the density runs, of `sak-drc.sh` on slot_7 / bg_core_pd and of `sak-lvs.sh` on
the pads means "violations / mismatch found" (listed above), not a failed run.
