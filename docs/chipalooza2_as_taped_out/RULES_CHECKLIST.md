<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: Chipalooza #2 rules checklist

| | |
|---|---|
| project | custom S2D / D2S analog pad pair with bandgap-referenced replica bias |
| challenge, slot | Chipalooza Challenge #2 (IHP SG13CMOS5L), slot 7 |
| designer | Christoph Maier |
| repository | [tatzelbrumm/sg13cmos5l_cm_slot7](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7); taped-out commit `158afc5`; documentation on branch `chipalooza2-documentation` |
| rules | [opencircuitdesign.com/chipalooza/rules-2.html](https://opencircuitdesign.com/chipalooza/rules-2.html), read 2026-11-25 (no change notice on the page); numbering as on the page |
| details | one row per item with full evidence: [RULES_COMPLIANCE_chipalooza2.md](../RULES_COMPLIANCE_chipalooza2.md); everything else: [data book](pdf/slot7_databook.pdf) |

Status: **met** · **partly** (what is missing is stated) · **not met** · **open** (decision or record not in the repository) ·
**n/a**. Count over the 39 rows (sub-items listed separately; item 13 split into its three requirements): met 16, partly 7, not met 3, open 3, n/a 10.

| # | rule | status | evidence / what is missing |
|---|---|---|---|
| P | conform to all IHP SG13CMOS5L requirements: DRC, voltage limits | partly | DRC 0 and LVS match on the taped-out GDS, see the sign-off table below; all devices 3.3 V class on 3.3 V. Missing: antenna check not run |
| 1 | start date 2026-07-13 | n/a | |
| 2 | 17 weeks to tapeout | n/a | taped out 2026-11-09 |
| 3 | individuals or teams | n/a | individual |
| 4 | proposal due 2026-07-27 | open | the Chipalooza #2 proposal is not in the repository |
| 5 | personal details kept out of the main proposal | met | documentation names the designer only |
| 5.1 | type of IP block | met | [description](README.md) |
| 5.2 | list of I/O, including test ports | met | [description §4](README.md#4-physical-interface-and-layout-hierarchy), [glue logic](glue_logic.md) |
| 5.3 | functional description | met | [description §2](README.md#2-electrical-function), [how it works](HOW_IT_WORKS.md) |
| 5.4 | target specification: average, minimum, maximum, absolute limits | not met | no specification before the design; characterized values against the designer's working limits: [achieved vs limits](ACHIEVED_VS_LIMITS.md) |
| 5.5 | outline of a test plan | met | [test plan](TEST_PLAN.md) |
| 5.6 | equipment (sent separately) | n/a | equipment needed: [test plan §8](TEST_PLAN.md#8-equipment-needed) |
| 5.7 | CVs (sent separately) | n/a | |
| 6 | useful within an SoC | met | [description: use in a system](README.md#known-limitations-and-use-in-a-system) |
| 6.1 | supplies 1.2 V / 3.3 V | met | 3.3 V; 1.2 V for pull-downs only |
| 6.2–6.4 | bandgap 1.2 V, 1 bias voltage, 2 bias currents | met | not used: own bandgap on the slot |
| 6.5 | 4 shared analog signals | met | `analog_bus0..3` |
| 6.6 | 24 digital inputs | met | 6 used |
| 6.7 | 12 digital outputs | met | held low |
| 6.8 | 0 to 4 dedicated analog pads; exceptions approved | partly | 2 pads, replaced by custom pad cells, carried in the harness configuration (`s7_an[0]`, `s7_an[1]`). Missing: written approval record in the repository |
| 7 | target specification met in post-layout verification | not met | as 5.4 |
| 8 | up to 18 designs per chip | n/a | on the taped-out chip |
| 9 | public repository with all files to reproduce, verify and use the block | partly | GDS, LEF, lib, Verilog stub, netlists, sign-off scripts and reports here. Missing: schematic sources, CACE decks and layout scripts are in the design repository only |
| 10 | verifiable with open-source EDA tools; AI not required | met | [tools and versions](../AI_ASSISTANCE.md) |
| 11 | all source files for all views in the repository | not met | as 9 |
| 12 | full behavioural description documented; plain-text files for integration | met | [description](README.md), [data book](pdf/slot7_databook.pdf); `final/lef`, `final/lib`, `final/vh`, `pads/pads.txt` |
| 13 | sign-off data required (final DRC and LVS) | met | [sign-off reports of the taped-out GDS](../../signoff/taped_out_158afc5/README.md) |
| 13 | simulation results as plots, not raw data | met | 7 figures on the front page, 54 in [`verification/c2_gaps/`](../../verification/c2_gaps/), all in the data book |
| 13 | raw data reproducible from the design sources in the repository | partly | each simulation folder has `run.sh`. Missing: it fetches the sources from the design repository (as 9) |
| 14 | standard open-source licence, preferably Apache 2.0 | open | `LICENSE`: Solderpad Hardware License 2.1 (wraps Apache 2.0); documentation files Apache-2.0. Acceptance of SHL 2.1 not recorded |
| 15 | follow the repository template; sign-off scripts runnable by anyone | partly | [run_signoff.sh](../../signoff/taped_out_158afc5/run_signoff.sh) re-runs DRC / LVS from a clone. Missing: template structure (the design repository has it) |
| 16 | post-layout PVT verification, commercial range (≤ 110 °C acceptable) | partly | both pads: extracted layout, 5 corners, −40 … 125 °C, 3.0 … 3.6 V ([S2D](datasheets/sg13cmos5l_IOPadSingle2Diff.md), [D2S](../../verification/c2_gaps/d2s_pex/results.md)). Missing: extraction of the whole slot |
| 17 | layout within the slot; designer wires the wrapper | met | 537.15 × 273 µm, frame pins unchanged |
| 18 | shared analog pins through multiplexers; note any resistance limit | partly | bus effect stated, switch simulated as 10 kΩ ([test plan §1](TEST_PLAN.md#1-what-can-be-observed-where)). Missing: an allowed series resistance |
| 19 | harness chip documented | n/a | harness repository |
| 20 | reviews: proposal, schematic, layout, final | open | no review records in the repository |
| 21 | not ready at the final review → no tapeout | n/a | taped out |
| 22 | awards | n/a | |
| 23 | updates announced in the forum | n/a | the rules page shows no change notice; the forum was not checked |

## Sign-off of the taped-out GDS (re-run 2026-11-25)

| check | `slot_7` | S2D pad | D2S pad |
|---|---|---|---|
| KLayout DRC, full deck without density | 0 | 0 | 0 |
| KLayout DRC, maximal deck with latch-up rules | 0 | 0 | 0 |
| KLayout density (fill is added at chip level) | 7 minimum-density rules | 4 | 4 |
| KLayout LVS | match (strict ports, 497 devices) | match (76 devices; reference: CDL derived from `pads/*/*.spice`) | match (77 devices; same) |
| magic DRC | 48 markers in `bg_core_pd`, all "Metal1 overlap of Via1" (KLayout passes the same rules) | 0 | 0 |
| magic + netgen LVS | 5 subcircuits match; top cell: "failed pin matching", one pin without partner (`vss_1v2_uq0`); same as the designer's pre-tapeout run | "failed pin matching": only `vss` without partner (`vss` / `iovss` substrate merge, accepted 2026-11-03); report identical to the committed one | same as S2D |
| antenna | not run | not run | not run |

Reports and the script: [`signoff/taped_out_158afc5/`](../../signoff/taped_out_158afc5/README.md).
