<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: whole-slot parasitic extraction and simulation

**IHP sg13cmos5l post-layout (magic PEX) simulation** of the taped-out slot 7 as one extracted netlist, with the two
custom pads. Results and comparison: [results.md](results.md); generated table: [tables.md](tables.md).

## Question

Until now the slot-level simulations used the slot's source netlist (design repository commit 9052bd35) with
`pad_ref_rb` and `bias_dist_pd` KLayout-extracted, `bg_core_pd`, `s7_ctrl`, `ls_up_fs` and `s7_doutpd` from schematic
or source netlists, and the routing between the blocks not at all. The two pads were simulated as schematic, as magic
C-coupled PEX or KLayout-extracted. Nobody had extracted the whole slot, and nobody had extracted wire resistance.
This folder asks three questions:

1. Is the magic extraction of the whole `final/gds/slot_7.gds` the same circuit as `netlist/slot_7_netgen.spice`?
2. How large are its parasitics, with and without wire resistance?
3. How do the slot's DC, AC, step, power-up, `vcm` / `vref` and supply-current results change when the extracted slot
   replaces the source netlist, and when the slot and pads are full-RC?

## Method

1. **Extraction** ([extract.sh](extract.sh)), magic 8.3.685 with the PDK's magicrc. The slot is read from
   `final/gds/slot_7.gds` (sha256 `469f2327…`) and the pads from `pads/<cell>/<cell>.gds`. Each cell is flattened
   with the commands of `sak-pex.sh`. Three extractions are made per cell:
   - `sak`: `sak-pex.sh -m 2`, as the earlier pad PEX netlists (`../d2s_pex`, the S2D netlist of the design
     repository). It is kept for comparison only.
   - `c` (C-coupled): the same magic commands (`extract all`, `ext2spice lvs`, `cthresh 0.01` fF). The netlist is
     written flat (`ext2spice hierarchy off`) and given the port order of the hierarchical output
     ([pexfix.py](pexfix.py) `c`).
   - `rc` (full-RC): the commands of `sak-pex.sh -m 3`, with `extresist threshold 0`, `minres 100` mΩ and
     `mindelay 0`. With these settings magic extracts resistance on every net it finds resistance for: 169 of 388
     slot nets and 32 nets of each pad. The other nets have no resistor network in magic's output. The netlist keeps
     magic's devices and resistors and takes its capacitors from `c` ([pexfix.py](pexfix.py) `rc`, see below).
2. **Two corrections of the magic output, both found here:**
   - **Substrate capacitance.** Written hierarchically (`ext2spice lvs`, which `sak-pex.sh` uses), this magic
     version leaves out most of the node-to-substrate capacitance that the `.ext` file holds. Some nets also get a
     different value. The `.ext` totals are 2.162 pF for the slot, 1.893 pF for S2D and 1.999 pF for D2S. The flat
     output matches them: 2.158, 1.889 and 1.995 pF; the 4 fF difference is the 0.01 fF threshold. The hierarchical
     output gives 1.889, 1.447 and 1.339 pF. Examples: the slot net `enable` has 33.77 fF to substrate in the `.ext`
     and none in the hierarchical netlist; `s7_an_0_outp` has 3.47 fF in the `.ext` and 11.62 fF in the hierarchical
     netlist. **The pad PEX netlists of the earlier runs (`../d2s_pex`, `../dc_curves`, `../ac_tran`) are
     `sak-pex.sh` output, so they lack this capacitance:** 0.44 pF for S2D and 0.66 pF for D2S. The coupling
     capacitors are the same in both outputs. The devices are identical (checked card by card).
   - **Full-RC capacitance.** `extresist` places capacitors to ground on the resistor nodes of each resistive net,
     and their sum is the net's *total* capacitance, coupling included. `ext2spice` then writes the coupling
     capacitors as well. As a result magic's full-RC netlist has 3.90 pF for the slot instead of 2.16 pF. Example:
     `dig_in[1]` has 3.66 fF to substrate and 127.9 fF in all, and its rnode capacitances add up to 124.2 fF
     ([csv/rnode_caps_slot_7.csv](csv/rnode_caps_slot_7.csv)). The full-RC netlist used here keeps magic's devices
     and resistors. Its capacitors are those of `c`. The ground capacitance of each resistive net is split over its
     resistor nodes in the proportion magic computed, and coupling capacitors stay at the nets' main nodes, as in
     magic's own output. For nets whose main node magic removed (`killnode`), the rnode with the largest
     capacitance takes its place. Totals: slot 2.166 pF, pads 1.889 / 1.997 pF.
3. **LVS** (netgen 1.5.324, [lvs_collapse.py](lvs_collapse.py): capacitors dropped, parasitic resistors shorted).
   The slot is compared with `netlist/slot_7_netgen.spice` in the same way as `netlist/netgen_check.sh`, and each
   pad with `pads/<cell>/<cell>.spice` (vss port added as in `../d2s_pex`). See
   [lvs_summary.txt](lvs_summary.txt).
4. **Simulation netlists** ([prep.py](prep.py)). The extracted `slot_7` is wrapped into a subckt with the port order
   of the source netlist that the earlier decks instantiate. Ports that the layout makes one net are joined by 0 V
   sources, as the source netlist does. The unused harness pins carry no device; they are tied to `vss_3v3`, and
   `vss_1v2_uq0` to `vss_1v2`. Nodes that only capacitors touch get 1 TΩ to ground (`pex_for_sim.py --tie`): these
   are the floating poly and metal of `tughra_art`, 101 nodes with 0.16 pF. The pads are prepared as in
   `../dc_curves/cace_dc.sh`.
5. **Decks** ([sim.py](sim.py)). The deck is the earlier tier-1 round-trip deck: S2D pad → slot 7 default mode →
   D2S pad, with replica `vcm` / `vref` and `iref` from the slot's bandgap through `bias_dist_pd`, `vdd_3v3` = `iovdd`,
   enable 1.2 V, mode bits 0. The analyses and loads are those of `../dc_curves/roundtrip.py` and
   `../ac_tran/slot.py`. Power-up follows `../slot_modes_bg` 'pu', and the modes follow the designer's
   `run_modes.py`. Views:

   | view | slot | pads |
   |---|---|---|
   | `prev` | earlier deck: source netlist with KLayout-extracted `pad_ref_rb` / `bias_dist_pd`, schematic `bg_core_pd` | earlier magic PEX (`sak-pex.sh`, no substrate C) |
   | `c` | magic C-coupled, whole slot | as `prev` |
   | `cc` | magic C-coupled, whole slot | magic C-coupled with substrate C |
   | `rc` | magic full-RC, whole slot | magic full-RC |
   | `cs` | as `c`, solver SPARSE (check) | as `prev` |
   | `hyb` | as `prev`, but `pad_ref_rb` = its magic C-coupled extraction (cut from `slot_7.gds`) | as `prev` |

   `c` vs `prev` isolates the slot's layout. `cc` vs `c` isolates the pads' missing substrate capacitance. `rc` adds
   wire resistance everywhere. `hyb` locates the `vcm` / `vref` shift.

   Analyses ([jobs.txt](jobs.txt)): operating point enabled and disabled, bias currents into the pads, DC round trip,
   AC with three loads, and the 0.25 → 0.75 V step with three loads at tt and two (unloaded, 1 kΩ ∥ 100 pF) at the
   other four points. The enable transient starts from the disabled operating point. Power-up from 0 V was tried at
   tt and stalls (results.md §4). The modes swap / mon / feed / ext were run at tt 27 °C.
6. **Solver options and convergence aids.** Every run uses `.option gmin=1e-12 rshunt=1e12`. rshunt is 1 TΩ from every
   node to ground; the PEX pads need it (`../d2s_pex`), and the earlier PEX-pad runs had it too. The transients add
   `method=gear` (as `../ac_tran`), and power-up also adds `cshunt=1e-15` with a 10 ns maximum step (as
   `../slot_modes_bg`). The solver is KLU (`.option klu`). The earlier runs used ngspice's default SPARSE 1.3, which
   took 282 s for one full-RC operating point (63 s with KLU). The `cs` view checks the solver's effect on the `c`
   results. The operating points of the extracted netlists need gmin stepping ("dynamic gmin stepping failed, true
   gmin stepping completed"), as the earlier PEX-pad decks did. No `.nodeset` and no `.ic` are used anywhere. After a
   failed run, `sim.py` retries with SPARSE, then with more gmin / source steps and iterations, then (DC only) with
   the sweep split at 0.5 V. Each retry is recorded in the run's log, in `<tag>.aid` and in results.md §4.
7. **Evaluation** ([evaluate.py](evaluate.py)): the definitions of `../dc_curves/rt.py` and `../ac_tran/rt.py`,
   restated in the script. The comparison takes the committed CSVs of those folders (view `pex`) and the `prev`
   rerun of the same deck.

## Reproduce

```
verification/c2_gaps/slot_pex/run.sh [<work_dir>] [fetch|extract|prep|stats|sim|eval|all]
```

Run it from a checkout of this repository. It fetches the design-repository paths itself (shallow, blobless, through
`../dc_curves/fetch.sh`). Bulky data goes to `<work_dir>` (default `_work/`, ignored by git): extractions `x_*/`,
netlists `nets/`, decks `runs/` and waveforms `out/`. The `sim` step runs [jobs.txt](jobs.txt) one ngspice process at a
time. Wall clock in this task, on 4 CPUs shared with other jobs, was about 4 h. Most runs take 10 s … 3 min. The
failing −40 °C retries take up to 20 min each, and the power-up attempt was stopped after 60 min (`SIM_TIMEOUT` now
limits each attempt to 15 min, or 40 min for transients). Extraction and LVS take about 15 s.

Reproducibility: magic's full-RC resistor count changes from run to run, from 9.8 k to 10.6 k resistors for the slot
on identical input (three runs). The device cards and the capacitors of `c` do not change. The `rc` results therefore
carry a small run-to-run spread, which was not quantified.

## Versions

- ngspice-47 (KLU compiled in), IHP OSDI models of the PDK (`psp103.osdi`, `r3_cmc.osdi`, …) through the PDK's
  `.spiceinit`; magic 8.3.685; netgen 1.5.324; `sak-pex.sh` (IIC-OSIC-TOOLS, sha256 `fc9f6dbf…`); python3 with
  numpy 2.5.3 and matplotlib 3.11.2.
- PDK `/foss/pdks/ihp-sg13cmos5l` → IHP-Open-PDK `df4c5054ee8ca481c3eb873687274f28cdb50b1e` (2026-10-14).
- This repository, branch `chipalooza2-documentation`, HEAD `8c58c8c` at the time of the run. Layout sha256:
  `final/gds/slot_7.gds` `469f2327…`, `pads/sg13cmos5l_IOPadSingle2Diff/*.gds` `13e176ab…`,
  `pads/sg13cmos5l_IOPadDiff2Single/*.gds` `f4b0e073…`.
- Design repository `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`: `9052bd35` (tier-1 deck, slot source
  netlist, block netlists) and `91a7da8b` (S2D PEX netlist, `pex_for_sim.py`, `pex_add_port.py`).

## What this does NOT show

- **No substrate network.** The substrate is one node (`vss_3v3` in the slot, `iovss` in each pad). There is no
  substrate resistance and no coupling through the substrate. The pads' `vss` is tied to `iovss` by 1 Ω as before.
- **No package, bond wire, padframe or harness.** The slot's pins connect to ideal sources and to the pads directly.
  The harness's analog-bus switches and the wiring from the slot edge to the pad cells are not included.
- **Full-RC is magic's resistor network** on the nets magic extracts, with the capacitance correction described
  above. That correction is mine, not magic's. Contact and via resistance are included only as magic models them.
  Nets without a resistor network (219 of 388 in the slot) stay ideal wires.
- Only the five tier-1 PVT points are covered, with `res_typ`, `cap_typ` and pnp `typ`. There is no Monte Carlo or
  mismatch: magic writes no `mm_ok`. There is no noise, no sine/THD on the extracted slot, and no silicon.
- The disabled currents are DC operating points with `enable` = 0 V. They are not the 150–170 µs transient window of
  the designer's data sheet.
- rshunt (1 TΩ on every node) is in every run. Its effect on the schematic deck was ≤ 0.006 % (`../ac_tran`). It was
  not re-measured on the extracted netlists.
- The runs that did not finish are listed in results.md. They were not retried with other solver settings.

PNG files carry no SPDX header: same copyright and license as this README.
