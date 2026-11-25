<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# ESD (HBM) and latch-up of the slot-7 pads: simulation with the PDK's compact models

**IHP sg13cmos5l simulation** (ngspice-47 with the IHP OSDI models, PDK `ihp-sg13cmos5l` at `/foss/pdks`, tt, 27 °C).
The two custom pad cells `pads/sg13cmos5l_IOPadSingle2Diff` (S2D, input) and `pads/sg13cmos5l_IOPadDiff2Single`
(D2S, output) on a model of the harness pad ring. Results and verdicts: [results.md](results.md). Status: complete
for what is listed under "Method"; what could not be done is listed at the end of results.md.

> **Read this first: the compact models are not ESD models.** The PDK's diode and MOS models were fitted for normal
> operation. They have no snapback (no parasitic NPN in the NMOS, no parasitic PNP in the PMOS), no high-injection or
> self-heating physics fitted at ampere currents, no thermal failure, and no parasitic thyristor. The PDK's antenna
> diodes are fitted "for the reverse direction" (`diodes.lib` header) and give 405 V at 0.1 A forward (table in
> results.md §1). Everything below is **indicative**: it shows where the current goes and which oxides see the pad
> voltage, not whether the pads pass 2 kV HBM.

## Question

The README of the slot (`docs/chipalooza2_as_taped_out/README.md`, "Not verified") lists ESD and latch-up of the pads
as never simulated. Questions:

1. HBM (JS-001 style, 100 pF / 1.5 kΩ, ±500 V, ±1 kV, ±2 kV) into each pad with (a) iovss grounded, (b) iovdd grounded,
   (c) the other slot-7 pad grounded: peak pad voltage, peak voltage across every gate oxide on the pad path, peak
   diode currents and current densities, energy in the diodes.
2. CDM: optional (not done, see results.md §6).
3. Latch-up (JESD78 style): (a) I-test ±100 mA into each pad with the chip powered at 3.6 V, and the current at which the
   pad reaches 1.5 × 3.6 V = 5.4 V; (b) supply overvoltage 5.4 V; (c) an estimate of the trigger current of the parasitic
   thyristor from a lumped model with assumed parameters; the KLayout latch-up DRC result.

## Method

| step | script | what it does |
|---|---|---|
| ring model inputs | `fetch_harness.sh`, `ring.py` | fetches the harness padframe (`RTimothyEdwards/sg13cmos5l_ocd_chipalooza`, branch `tapeout_nov_2026`, commit `2ef5a869`); reads the positions of all supply pads along the ring from `magic/sg13cmos5l_padframe.mag`, and the ring metal from the PDK IO cell `sg13cmos5l_Filler2000` → `csv/ring_cells.csv`, `csv/ring_metal.csv` |
| model check | `iv.py` | forward I–V of the pad diodes and of the clamp / output-device drain paths (junction and channel, gate tied as in the pad) in the compact models → `csv/model_iv.csv`, `plots/model_iv.png` |
| HBM | `esd.py` | 60 transient runs (1 µs each; 44 with the ESD-diode proxy, 16 with the PDK antenna-diode model, 240 s wall-time limit each); per run the raw file is analyzed and deleted → `csv/hbm_*.csv`, `plots/hbm_*.png`; network check → `csv/hbm_network_check.csv` |
| I-test, overvoltage | `latchup.py` | DC sweeps of a current forced into each pad (0 → ±1 A), powered ring at 3.6 V, pads enabled; supply swept 0 … 5.4 V → `csv/itest.csv`, `csv/overvoltage.csv`, `plots/itest_vpad.png`, `plots/overvoltage_isupply.png` |
| latch-up geometry | `lu_geometry.py` | guard rings and distances of the ESD sub-cells in the pad GDS → `csv/lu_geometry.csv`, `plots/lu_layout_*.png` |
| lumped thyristor | `scr.py`, `scr_plot.py` | PNPN with assumed β, well / substrate resistances and collection fraction; trigger current by bisection → `csv/scr_trigger.csv`, `plots/scr_trigger.png` |
| tables | `tables.py` | the Markdown tables of results.md from `csv/` → `_work/tables.md` |
| common | `common.py` | netlist preparation, ring netlist, pad instances, ngspice runner (one process at a time), raw-file reader, netlist flattener |

### Pad netlists

`pads/<cell>/<cell>.spice` (the schematic / magic-LVS netlists of design commit `91a7da8b`, as taped out) are used
unchanged except for 0 V ammeters inserted into a copy (`_work/net/`, `common.py: AMMETERS`) in series with each
pad diode, the S2D clamps MCP / MCN, the D2S output devices OP / ON and the parts of the two `d2s_sp2k` stages. These
netlists give `dantenna` / `dpantenna` their `l` / `w` (the KLayout-converted netlists do not, see
[../klayout_pad_diodes](../klayout_pad_diodes/README.md)). Diode sizes (l × w, µm): S2D 2 × `dpantenna` 27.78 × 1.26
and 2 × `dantenna` 27.78 × 1.26 (35.0 µm² each); D2S 2 × `dpantenna` 65.8 × 1.26 (82.9 µm²), 2 × `dantenna`
67.6 × 1.26 (85.2 µm²), and in each `d2s_sp2k` a `dpantenna` 4.98 × 0.64 and a `dantenna` 3.1 × 0.64 behind 1.99 kΩ
rppd.

Core-side pins: **unpowered** (all HBM runs) = `vref`, `vcm`, `vinp`, `vinn`, `en_3v3` tied to the pad's own iovss,
`en_3v3_b` to its iovdd (the disabled state that the fail-safe enables present), `iref` and the S2D outputs open
(1 TΩ). **Enabled** (latch-up runs) = S2D `vref` 0.49 V, `vcm` 1.26 V; D2S `vinp` = `vinn` = `vref` = 1.26 V (the slot
operating point of HOW_IT_WORKS §2.2 / §3.1), `iref` 5 µA from iovdd, enables on, no load.

### Antenna-diode models: two variants

| variant | what | used for |
|---|---|---|
| `pdk` | `diodes.lib` as shipped: `dantenna` / `dpantenna` = area + perimeter + corner diodes with series resistance `rs` = 2.193e5 / 1.728e5 Ω (per µm² of area; 1.688e6 / 1.577e6 Ω per µm of perimeter / 0.5) and high-injection knee `ik` 0.14 / 0.30 µA/µm². "Model is designed for the reverse direction of the diodes" (file header). | HBM ±500 V … ±2 kV where it converges; I-test |
| `esdproxy` | the same subcircuit names re-modeled with the PDK's **ESD-diode** models `diodevss_mod` (n+/p-sub) and `diodevdd_mod` (p+/n-well) from `sg13g2_esd.lib` (shipped in the `ihp-sg13cmos5l` model directory, "COMMON ESD MODELS"), area = l × w: series resistance 200 / 289.6 Ω·µm² / area, i.e. 5.7 / 8.3 Ω for a 35 µm² stripe. Those models belong to the sg13g2 ESD diodes `diodevss_2kv` / `diodevdd_2kv`, whose area parameter is 35 µm² (the S2D stripes are 35.0 µm² as well); they are a **proxy** for an ESD-capable forward characteristic, **not** a calibrated model of these antenna diodes. | all HBM tables and plots; I-test |

The MOS devices keep the PDK PSP models in both variants. Their drain junctions (JUNCAP2) are linearized above
`imax` = 2.0 / 2.5 mA (hv NMOS / PMOS parameter files), which makes them resistive at ESD currents (results.md §1).

### Pad ring (harness `tapeout_nov_2026`, `2ef5a869`)

| item | value | source |
|---|---|---|
| supply clamp between iovdd and iovss | **present**: every `sg13cmos5l_IOPadIOVdd` holds an RC-triggered clamp — NMOS `Clamp_N43N43D4R` (172 fingers × 4.4 / 0.6 µm = 756.8 µm), gate driven by `RCClampInverter` (PMOS 350 / 0.5, NMOS 2 × 54 / 0.5, MOS capacitors 2 × 63 / 9.5) from `RCClampResistor` (26 × rppd 1 / 20 µm, 26 × 5.239 kΩ) | PDK `libs.ref/sg13cmos5l_io/spice/sg13cmos5l_io.spice`; simulated with the 172 fingers as one instance with m = 172 |
| number and position of the clamps | 5 `IOPadIOVdd` (`pad_vdd3v3_0` … `_4`): one on the right edge at y = 280 µm, four on the top edge at x = 360 … 690 µm; along the ring 2.09 … 2.53 mm from the slot-7 pads (which sit at y = 2260 / 2370 µm on the right edge) | `magic/sg13cmos5l_padframe.mag` → `csv/ring_cells.csv` |
| iovss pads | 6 `IOPadIOVss` (DCNDiode / DCPDiode, i.e. a dpantenna pair iovss → iovdd), the nearest 220 µm from the D2S pad | same |
| ring splits | the two `sg13cmos5l_ocd_Split2000` cut only the 1.2 V `vdd` ring; iovdd / iovss run through ("the ground domain cannot be split", cell comment) | `verilog/rtl/sg13cmos5l_ocd_Split2000.v`, `.mag` labels |
| ring resistance | iovdd 0.2505 mΩ/µm (2 × 25.5 µm on Metal3, Metal4, TopMetal1), iovss 0.2165 mΩ/µm (25.5 + 25.5 + 8 µm); Metal1 left out (upper bound) | `sg13cmos5l_Filler2000` GDS + typical sheet resistances of the process spec (Metal3/4 88 mΩ/sq, TopMetal1 18 mΩ/sq) |
| how the ring is simulated | iovdd and iovss as two resistor loops through the 13 nodes (5 IOVdd, 6 IOVss, 2 slot-7 pads), each supply cell as its PDK netlist, the substrate node of each supply cell local to it (tied to its iovss by the library's ptap1 resistors) | `common.py: ring_netlist` |
| HBM grounding | (a) the 6 IOVss bond pads at 0 V, iovdd floating; (b) the 5 IOVdd bond pads at 0 V, iovss floating; (c) the other slot-7 pad at 0 V, both rings floating | |
| not modeled | the 32 `IOPadAnalog` and the GPIO / 1.2 V supply cells on the same ring (their junction capacitance and clamps would add parallel paths), any on-chip decoupling between iovdd and iovss (unknown), the package, the 1.2 V domain and the core `vss` ring (taken as iovss) | |

### HBM network

100 pF charged to V0, a switch closing at 1 ns, 1.5 kΩ, and a series inductance L. Without L the solver stops at the
first nanosecond (the current step); L is set from the ends of the JS-001 rise-time window (2 … 10 ns into a short,
taking the 10–90 % rise of an RL step, 2.197 L / 1.5 kΩ): L = 1.365 µH (all runs) and 6.83 µH (sensitivity runs
`hbmls_*` at ±2 kV). Measured into a short: 1.85 ns and 7.96 ns (the capacitor already discharges during the rise). The network
into a short and into 500 Ω is checked in `csv/hbm_network_check.csv`. No tester parasitics (stray capacitances) beyond
that.

## How to reproduce

```
cd verification/c2_gaps/pad_esd_latchup
./run.sh            # all steps, about 2 h on one CPU; ngspice runs one at a time
./run.sh hbm        # or one step: fetch | ring | iv | hbm | latchup | geometry | scr | post
```

Needs PDK_ROOT with `ihp-sg13cmos5l`, ngspice-47 with the IHP OSDI models, KLayout's Python module (`klayout.db`),
python3 with numpy / matplotlib, git with access to github.com (harness padframe only). Bulky output (netlists, logs,
per-run JSON) goes to `_work/` (git-ignored); raw files are deleted after analysis.

## Files

| file | content |
|---|---|
| [results.md](results.md) | tables, plots, verdicts, what could not be done |
| `csv/ring_metal.csv`, `csv/ring_cells.csv` | ring metal bands and resistance per µm; supply-pad positions |
| `csv/model_iv.csv` | forward voltage of the pad devices at 1 mA … 2 A in the compact models |
| `csv/hbm_network_check.csv` | HBM network into a short and 500 Ω |
| `csv/hbm_summary.csv`, `csv/hbm_diodes.csv`, `csv/hbm_mos.csv` | per HBM run: peaks; per diode: current, density, energy; per pad-path MOS: peak oxide voltages |
| `csv/itest.csv`, `csv/overvoltage.csv` | I-test at ±100 mA; MOS terminal voltages at 3.6 and 5.4 V |
| `csv/lu_geometry.csv`, `csv/scr_trigger.csv` | latch-up geometry; lumped-thyristor trigger currents |
| `plots/*.png` | figures referenced in results.md |
