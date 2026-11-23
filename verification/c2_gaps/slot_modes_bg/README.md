<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: mode start-up at ss / −40 °C, mode table over PVT, bg_core_pd alone

IHP sg13cmos5l simulation (ngspice, IHP OSDI models). This fills three gaps in the slot-level characterization of the
taped-out slot 7 (commit `158afc5afab0056bd6d216a4db3833e34a364949` of this repository):

1. **The ss / −40 °C mode failures** in the designer's tier-1 mode runs (`docs/slot7_hookup/tier1/modes.txt` of the
   design repository: swap, mon, feed, ext, swap+feed `FAILED` at ss −40 °C, "stall at the bandgap's start-up node").
   Question: simulator artefact or a second stable state of the bandgap (real start-up risk)?
2. **Mode table over more PVT points** than the designer's 3 (modes) / 5 (round trip).
3. **`bg_core_pd` alone**: output current over MOS × rhigh corners × T × V, start-up by supply ramp, supply
   sensitivity, and a check for a zero-current state.

Verdict and numbers: **`results.md`**. Generated tables: `results_tables.md`, CSVs, plots.

## Sources

| what | where |
|---|---|
| design repository | <https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single> commit `9052bd35928c6d40344e8e686c9abbe736bfadb9` (fetched by `run.sh`, only the paths below, no full clone) |
| tier-1 scripts | `docs/slot7_hookup/tier1/run_tier1.py`, `run_modes.py` (imported unchanged: same netlists, same port wrapping) |
| slot glue | `macros/slot_7/netlist/source/slot_7.spice` (`slot_7`, `s7_ctrl`, `s7_doutpd`) |
| views used in the slot decks | both custom pads, `pad_ref_rb`, `bias_dist_pd`: **extracted** (`netlist/layout/*_klayout.cir`, converted by the designer's `run_starve.convert()`); `bg_core_pd`: **schematic** (`netlist/schematic/bg_core_pd_magic.spice`), as in the designer's runs; `ls_up_fs`, `s7_ctrl`, `hv_logic`, `en_ctrl_3v3`: source netlists |
| views used for bg_core_pd alone | **schematic** `macros/bg_core_pd/netlist/schematic/bg_core_pd_magic.spice`; **extracted** `macros/bg_core_pd/netlist/pex/bg_core_pd_magic_pex_3.spice` (magic PEX, R + C) |
| PDK | IHP-Open-PDK `ihp-sg13cmos5l`, commit `df4c5054ee8ca481c3eb873687274f28cdb50b1e`, `.spiceinit` of the PDK (OSDI psp103, r3_cmc, ...) |

## Tools

- `ngspice -v`: `ngspice-47 : Circuit level simulation program`, compiled with KLU (the decks use the default SPARSE
  solver).
- Python 3.13.18, matplotlib 3.11.2, numpy 2.5.3 (tables / plots only). CACE 2.11 installed, not used.

## Files

| file | what |
|---|---|
| `run.sh` | reproduces everything: `./run.sh [WORKDIR] [fetch\|designer\|modes\|bg\|tables]` (default all; at most 2 ngspice in parallel, set `NPAR` in the script) |
| `slot_modes.py` | slot 7 decks: `pu` = power-up transient per mode (the method of task 1), `dcop` = the designer's DC deck with stderr kept, `dcns` = `dcop` + `.nodeset` of the bandgap nodes (diagnosis only) |
| `jobs_modes.txt` | job list for `slot_modes.py`, priority order |
| `bg_core.py` | bg_core_pd alone: DC table, supply ramps, zero-state diagnosis |
| `tables.py`, `plots.py` | CSV / markdown tables, PNG plots from the runs |
| `designer_modes_rerun_ss.txt` | the designer's `run_modes.py`, unchanged, re-run at ss −40 °C here |
| `results.md` | verdict, summary, what it does not show |
| `results_tables.md` | all generated tables |
| `slot_modes_powerup.csv`, `slot_modes_dc_diag.csv` | slot 7 per mode × PVT; DC diagnosis |
| `bg_core_dc.csv`, `bg_core_ramp.csv`, `bg_core_diag.csv` | bg_core_pd alone |
| `slot_powerup_ss_m40.png`, `bg_core_ramp.png` | waveforms |

## Method

**Slot decks (`slot_modes.py pu`).** The designer's testbench (both pads, slot_7, pad in / pad out, bus sources and
loads as in `run_modes.py`), but as a transient from all nodes at 0 V (`uic`, no `.ic` / `.nodeset`):
vdd_3v3 and iovdd ramp 0 → V in 10 µs, v12 = 1.2 V and the mode bits from t = 0 (register written before enable),
`enable` 0 → 1.2 V at 20 µs. Pad in 0.5 V to 40 µs, then 0 / 0.25 / 0.5 / 0.75 / 1.0 V for 10 µs each, sampled at each
step's end; error = pad out − expected (`run_modes.py`'s expressions: direct vcm + (in − vref), swap vcm − (in − vref),
feed vcm + (bus0 − bus1)/2, ext 1.30 + in − 0.50). Feed modes: pad in fixed 0.5 V, one sample at 90 µs. The bus
sources (feed bus0 / bus1 1.45 / 1.05 V, ext bus2 / bus3 1.30 / 0.50 V, each through 10 kΩ) switch on at 25 … 26 µs,
after enable (instrument connected to a powered slot). Pad out: 1 GΩ (as `run_modes.py`) ∥ **10 pF** (probe / board
load; variant `pu`); variant `pu0` is 1 GΩ only. Solver aids (no circuit change): `method=gear`, `cshunt=1e-15` (as
the designer's own transient in `run_tier1.py`), maximum time step 10 ns; variant `pu2` (retry of aborted runs):
enable edge 1 µs, maximum step 5 ns. Without these the transient aborts with "timestep too small" in the D2S pad's
antenna diode `X$3` (`dpantenna`, pad → iovdd): at 5.9 µs (trapezoidal, no cshunt), 21.3 µs (gear + cshunt, swap),
6.6 µs (gear + cshunt + rshunt 1 TΩ, default mode). With 1 GΩ only, or with the feed sources on from t = 0, more runs
abort at the same diode during the supply ramp or at the enable edge. All aborts are listed as `FAILED` in the tables
with the instance ngspice names. The ss −40 °C runs of section 1 of `results.md` were done in this order (pu0 first,
then pu); `slot_modes_powerup.csv` has a `cload` column.

**DC diagnosis (`dcop`, `dcns`).** The designer's DC deck, unchanged, with ngspice's stderr kept, and the same deck
with `.nodeset` of the bandgap nodes (g, vpc, vpg, ks, ibg) at their running values (from the power-up transient).

**bg_core_pd alone (`bg_core.py`).** `iout` into a 0.7 V source; enabled (`en_3v3` = vdd, `en_3v3_b` = 0). DC: `.op`,
cross-checked with the end of a 200 µs power-up transient (vdd 0 → V in 2 µs) and its value at 100 µs. MOS tt / ss /
ff / sf / fs × rhigh `res_typ` / `res_bcs` / `res_wcs` (schematic; extracted: res_typ) × −40 / 27 / 125 °C × 3.0 / 3.3
/ 3.6 V; pnpMPA typ. For the extracted view the DC runs use the PEX netlist without its capacitors (DC-equivalent):
with them, ngspice's `.op` ends in its "transient op" with capacitor currents still flowing (ss −40 °C: 6.92 µA with
pex_3, 8.29 µA with pex_2, against 4.85 µA without capacitors, pex_1 and schematic). Ramps: vdd = en_3v3 0 → V in
1 µs and in 1 ms (`method=gear`; with trapezoidal integration iout alternates point to point around its DC value,
e.g. 4.59 / 5.18 µA, the known trapezoidal ringing). Zero-state check: `.op` with `.nodeset` at the zero-current
state, and a transient with the supply up and `.ic` at the zero-current state.

## What this does NOT show

- No Monte Carlo / mismatch; pnpMPA only `typ`; rhigh corners only for bg_core_pd alone (slot runs: res_typ).
- `bg_core_pd` in the slot decks is the schematic view (as in the designer's runs); its extracted view is only
  simulated alone. `ls_up_fs` and `s7_ctrl` are source netlists (no layout netlist used).
- No package, bond wire, ESD event, harness or instrument model; pad out unloaded (1 GΩ) as in the designer's runs.
- Supply ramps for the slot: one shape (10 µs, enable at 20 µs); for bg_core_pd alone: 1 µs and 1 ms, enable tied to
  vdd. Not covered: enable toggling while powered, supply dips / brown-out, very slow (> 1 ms) ramps.
- The slot mode table covers only the PVT points that finished in the time box (see `results.md`); `run.sh` runs the
  full job list.
- Absence of a second state is shown for the PVT points simulated, by the methods above; it is not a proof for all
  conditions.
