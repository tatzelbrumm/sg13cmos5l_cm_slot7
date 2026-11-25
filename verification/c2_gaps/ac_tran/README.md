<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# AC, transient and noise curves of the two custom pads and the slot-7 round trip

**IHP sg13cmos5l simulation (schematic | magic PEX)**, ngspice-47 with the IHP OSDI models; the pad curves are run
through CACE 2.11 on the pads' own committed CACE testbenches. Pads: `sg13cmos5l_IOPadSingle2Diff` (S2D, `s7_an[0]`)
and `sg13cmos5l_IOPadDiff2Single` (D2S, `s7_an[1]`) as taped out. Until now these quantities existed only as CACE
scalar tables; here are the Bode plots, waveforms and spectra behind them, plus the slot round trip
pad_s2d → S2D → slot 7 → D2S → pad_d2s. Numbers, cross-check against the committed CACE CSVs: **[results.md](results.md)**.
DC transfer curves: [../dc_curves](../dc_curves).

Status: complete (all figures, tables and checks below from the runs of 2026-11-25), except the 10 kHz sine
through the KLayout-extracted pads (aborts, see results.md section 1).

## Figures (plots/, PNG 150 dpi; SVG too where it stays below 60 kB; PNGs re-encoded with a 256-color palette)

Common conventions (as ../dc_curves): one color per MOS corner (tt blue, ss orange, ff green, sf yellow, fs pink),
line style per temperature (−40 °C dotted, 27 °C solid, 125 °C dashed); where both pad views are in one panel without
a temperature family, schematic is solid and magic PEX dash-dot (slot figures: PEX dashed, KLayout-extracted dotted).
Each title states the simulation view(s) and the conditions.

### 1. Slot round trip (tier-1 slot deck, default mode, replica bias)

| file | what it shows / how to read it |
|---|---|
| `rt_bode_tt27` | small-signal gain pad_d2s / pad_s2d, magnitude and phase, 1 kHz … 100 MHz, at pad_s2d = 0.5 V DC, tt 27 °C 3.3 V; three loads (color: unloaded = 1 GΩ only as the designer's deck, 1 kΩ ∥ 10 pF, 1 kΩ ∥ 100 pF), three pad views (line style). Ideal: 0 dB (S2D gain 2 × D2S gain ½). The text box lists f−3dB and peaking per curve. |
| `rt_bode_pvt` | the same at the five tier-1 PVT points (color = corner; the temperature / supply of each point in the legend), unloaded and 1 kΩ ∥ 100 pF, pads schematic and magic PEX |
| `rt_f3db` | round-trip −3 dB bandwidth (relative to the gain at 1 kHz) per PVT point × pad view × load, as points |
| `rt_step_tt27` | step 0.25 → 0.75 V at pad_s2d (10 ns edges, up at 2 µs, down at 7 µs): top pad_s2d (the ideal source) and pad_d2s, bottom pad_d2s − final value in mV with the ±1 % band (±5 mV) grey; the 1 % settling time of each curve is the vertical line / triangle; tt 27 °C, three loads, schematic and PEX pads |
| `rt_step_pvt` | settling after the rising edge, pad_d2s − final in mV, five PVT points × pad views, unloaded and 1 kΩ ∥ 100 pF; grey bands ±1 % and ±0.1 % |
| `rt_sine_tt27` | 10 kHz sine 0 … 1 V at pad_s2d, 4 periods after 2 settling periods: input, expected output vcm + pad_s2d − vref (the replica's actual vcm / vref, as the designer's run_tier1.py) and pad_d2s (top); pad_d2s − expected (bottom). That error is mostly the round-trip delay (≈ 2π f A τ, a 90°-shifted sine), not distortion; the black curve (×10) is pad_d2s minus its own fitted dc + 10 kHz fundamental, i.e. the distortion; THD (harmonics 2–7), H2, H3, gain and delay in the text box |

### 2. S2D alone (CACE tb_ac / tb_tran / tb_noise / tb_enable conditions: iovdd 3.3 V, vref 1.2 V, vcm 1.2 V, rsrc 50 Ω, 0.5 pF per output, harness iDAC 5 µA)

| file | what it shows |
|---|---|
| `s2d_bode` | closed-loop (outp − outn)/(pad source − vref), magnitude (full and zoomed around −3 dB) and phase, 10 Hz … 1 GHz, 5 corners × 3 temperatures, schematic (left) and magic PEX (right). Temperature, not the corner, sets the bandwidth. |
| `s2d_cm_response` | output common mode (outp + outn)/2 per volt on iovdd (the CACE CMvdd) and per volt of signal, vs frequency, systematic (no mismatch) |
| `s2d_step` | step u = −0.25 → +0.25 V (CACE tb_tran): outp, outn (top) and outp − outn (bottom) at the two CACE loads 0.001 pF and 0.5 pF per output, tt 27 °C, schematic and PEX; 1 % band and settling times marked |
| `s2d_settling` | (outp − outn) − final in % of the step vs time, ss / tt / ff × 3 temperatures, both loads and views |

### 3. D2S alone (CACE conditions vicm = vref = vterm = 1.65 V, 1 kΩ to vterm + 100 pF unless stated; iovdd 3.3 V)

| file | what it shows |
|---|---|
| `d2s_bode_loads` | pad / (vinp − vinn), magnitude and phase, at the CACE loads 10 pF, 100 pF, 300 pF, 1 nF, each with 1 kΩ to vterm (solid) and unloaded 1 GΩ (dashed), tt 27 °C, schematic and PEX; peaking per load in the text box (the 1 nF peaking) |
| `d2s_bode_corners` | the same at the default load over 5 corners × 3 temperatures |
| `d2s_zout` | output impedance \|v(pad)/i_test\| vs frequency as CACE Zout (it includes the 1 kΩ ∥ 100 pF load), corners × temperatures |
| `d2s_psrr` | iovdd rejection −20 log\|pad / v(iovdd)\| vs frequency (output-referred, the CACE PSRR definition), corners × temperatures |
| `d2s_step` | large-signal step vinp − vinn −0.5 → +0.5 V and back (pad 1.40 ↔ 1.90 V) at 10 / 100 / 300 pF (1 kΩ to vterm), tt 27 °C, both views; slew rates and 1 % settling in the text box |
| `d2s_slot_vs_cace` | the D2S at the slot operating point vicm = vref = vterm = 1.26 V (dashed) vs 1.65 V (solid): gain at the four 1 kΩ loads, \|Zout\| at 27 °C over corners, rising step at 10 / 100 / 300 pF; schematic |

### 4. Noise

| file | what it shows |
|---|---|
| `s2d_noise` | S2D input-referred noise density (referred to the pad source − vref, includes rsrc 50 Ω), 10 Hz … 10 MHz, corners × temperatures, schematic, plus magic PEX; values at 1 kHz / 100 kHz, integrated output noise 10 Hz … 10 MHz (the CACE Vn_out) and integrated input-referred noise 10 Hz … 1 MHz in the text box |
| `d2s_noise` | D2S output noise density at the pad (1 kΩ to vterm + 100 pF; includes the 1 kΩ's own noise), 10 Hz … 10 MHz, corners × temperatures, both views; values at 1 kHz / 100 kHz and integrated 10 Hz … 10 MHz (the CACE Vn_int) |

### 5. Enable / disable

| file | what it shows |
|---|---|
| `s2d_enable` | S2D with u = +0.25 V: outp − outn (→ 0.5 V) and the output common mode, and the iovdd current of the testbench (pad + bias_gen_pd + en_ctrl_3v3), at en_1v2 0 → 1.2 V (1 µs) and 1.2 → 0 V (11 µs); tt 27 °C, ss −40 °C, ff 125 °C; both views; the current spike at the edges is clipped and its peak printed |
| `d2s_enable` | D2S with vinp = vinn: pad − vref and the iovdd / vdd-core currents at enable (1 µs) and disable (31 µs), tt 27 °C, sel 0, both views |

## Method

### Pads (CACE testbenches reused)

`mkgroups.py` copies each pad's committed CACE templates `tb_ac`, `tb_tran`, `tb_noise`, `tb_enable` (design commit
91a7da8b) to `<cell>_tb_at_<kind>.sch` and only **adds** lines inside the `.control` block; sources, models, options
and the original analyses and `meas` lines are unchanged, so each run's `.data` line (the CACE scalars) is computed
exactly as for the committed results (results.md shows it reproduces the committed CSVs). Added:

- `wrdata` of the waveforms the original analyses computed (tb_tran, tb_enable, D2S tb_ac after each of its four
  `ac dec 50 1 1G` analyses: signal, iovdd, common mode, output test current);
- after the original `echo … > .data`: S2D tb_ac: the signal and iovdd AC analyses again on a finer, wider grid
  (dec 40, 10 Hz … 1 GHz; the original is dec 20, 10 Hz … 100 MHz); both tb_noise: the noise analysis on dec 40,
  10 Hz … 10 MHz; both tb_enable: a second transient with the enable switched on at 1 µs and off again (S2D at 11 µs,
  D2S at 31 µs) by `alter @Ven[pwl]`.

The groups (`mkgroups.py`, each reusing the spec / variables of the original group) and their conditions:

| group | template | conditions (others = yaml defaults) | = committed CACE group |
|---|---|---|---|
| `s2d_ac` | tb_ac | 5 corners × −40 / 27 / 125 °C | ac_params |
| `s2d_tran` | tb_tran | cload 0.001 / 0.5 pF × ss / tt / ff × 3 temperatures | tran_params |
| `s2d_noise` | tb_noise | 5 corners × 3 temperatures | noise_params |
| `s2d_enable` | tb_enable | ss / tt / ff × 3 temperatures | enable_params |
| `d2s_ac` | tb_ac | 5 corners × 3 temperatures | ac_params |
| `d2s_ac_load` | tb_ac | cload 10 / 100 / 300 pF / 1 nF × rload 1 kΩ / 1 GΩ, tt 27 °C | ac_load_params + ac_1nF_params |
| `d2s_tran` | tb_tran | ss / tt / ff × cload 10 / 100 / 300 pF, 27 °C | tran_params |
| `d2s_noise` | tb_noise | 5 corners × 3 temperatures | noise_params (tt × 3 temperatures) |
| `d2s_enable` | tb_enable | sel 0 / 1 / 2, tt 27 °C | enable_params |
| `d2s_ac_slot`, `d2s_ac_load_slot`, `d2s_tran_slot` | tb_ac, tb_tran | as d2s_ac / d2s_ac_load / d2s_tran with vref = vicm = vterm = 1.26 V | — (slot operating point) |

`cace_at.sh` runs the groups on the schematic or the magic PEX view, prepared exactly as `../dc_curves/cace_dc.sh`
(S2D PEX: the design repository's `netlist/pex/<cell>_magic_pex_2.spice`; D2S PEX: `../d2s_pex/<cell>_magic_pex_2.spice`;
`pex_for_sim.py --tie iovss 1e12`, `vss` tied to `iovss` by 1 Ω inside the netlist as the sheet's Rsub). Only the pad
cell is extracted; bias_gen_pd and en_ctrl_3v3 next to it are schematic in both views. `collect.py` gathers the
`wrdata` files into gzipped CSVs in the work folder (not committed).

Solver aid: the D2S magic PEX view runs with ngspice `.option rshunt=1e12` (1 TΩ from every node to ground), as
`../d2s_pex` pass 2 (its operating point does not converge without it). The D2S schematic runs here **without** it,
as the committed schematic CACE results (these analyses converge without it). Its effect on the schematic was measured
(the same groups run with it, `rshunt.py`, `tables/rshunt.md`; summary in results.md). The S2D needs no aid.

### Slot round trip

`slot.py` builds the designer's tier-1 slot deck (commit 9052bd35, `docs/slot7_hookup/tier1/run_tier1.py`, imported)
exactly as `../dc_curves/roundtrip.py`: slot_7 source netlist in its default mode (mode bits 0, enable 1.2 V),
pad_ref_rb and bias_dist_pd KLayout-extracted, bg_core_pd schematic, S2D vref / vcm and D2S vref from the replica
pad_ref_rb, iref from the slot bandgap through bias_dist_pd, vdd_3v3 = iovdd; `.option gmin=1e-12`; the two pads as
schematic (CACE netlists), magic PEX (+ rshunt=1e12, as above) or KLayout-extracted (the designer's tier-1 view).
Added: the load, RL from pad_d2s to vterm and CL from pad_d2s to ground, vterm = an ideal copy (VCVS) of the D2S
reference v(vref_d2s) (so the 1 kΩ carries no DC current, as CACE's vterm = vref); "unloaded" = only the deck's 1 GΩ
to ground. Analyses: `ac` (pad_s2d 0.5 V DC + 1 V AC, dec 40, 10 Hz … 1 GHz, the three loads in one deck), `step`
(tran to 12 µs, max step 2 ns), `sine` (tran 0 … 600 µs, written from 200 µs, max step 39 ns = 4 periods / 1024).
Transients use `method=gear` (the designer's own tier-1 transient uses gear). If a run fails (operating point not
found), `slot.py` reruns it once with `rshunt=1e12` and records that in `<tag>.aid` and in the `aid` column of
`csv/rt_*_summary.csv`. Jobs: `jobs_slot.txt` (the five PVT points of run_tier1.py).

Scalar definitions: everything in results.md is evaluated by the scripts here from the plotted curves with the CACE
template definitions (f−3dB where the gain falls 3 dB below its 1 kHz value; 10–90 % rise; settling = last time
outside ±1 % of the step around the final value, measured from the input edge; slew = 0.8 × step / t(10 → 90 %);
noise integrals = trapezoid over the density squared). Round trip: the same definitions; THD from harmonics 2–7 over 4
periods resampled to 1024 points (the D2S tb_thd method).

## Reproduce

```
verification/c2_gaps/ac_tran/run.sh [<work_dir>] [fetch|s2d|d2s|slot|plots|all]
```
from a checkout of this repository (default work_dir `./_work` next to the script, not committed). `fetch` uses
`../dc_curves/fetch.sh` (shallow, blobless clone of the design repository; `git archive` of commits
91a7da8b67ac56a26c605501146667a1fde28c32 and 9052bd35928c6d40344e8e686c9abbe736bfadb9, only the paths needed). Order:
s2d and d2s before slot (slot uses the pad netlists their CACE runs prepare). Parallel ngspice runs: `JOBS` (default 3).
Wall clock in this session (4 CPUs, 2 … 3 parallel ngspice; ngspice also uses several threads): S2D groups 5 min
(schematic) + 9 min (PEX); D2S groups 6 min + 10 min; slot jobs about 75 min in total (most 15 s … 2 min; the cold
schematic runs that fail and are retried with rshunt take 8 … 10 min, the PEX transients 2 … 4 min); plots and tables
under 1 min. Partial reruns: `run.sh <work_dir> plots` regenerates everything committed from the work folder.

## Files

| file | what |
|---|---|
| `run.sh` | everything, in steps |
| `mkgroups.py` | writes the curve templates (`<cell>_tb_at_<kind>.sch`) and the CACE yaml of the groups next to a pad's own yaml |
| `cace_at.sh` | runs groups with CACE on the schematic or PEX view, then `collect.py` |
| `collect.py` | gathers each group's `wrdata` curves and `.data` scalars (work folder) |
| `slot.py`, `jobs_slot.txt` | round-trip decks (tier-1 slot deck with the chosen pad view) and the job list |
| `common.py` | loading, scalar helpers, plot style (imports the style / colors of `../dc_curves/common.py`) |
| `s2d.py`, `d2s.py`, `rt.py` | scalars, plots and `csv/*_summary.csv` |
| `crosscheck.py` | committed CACE value vs this run's `.data` vs the value from the curves (`csv/crosscheck.csv`, `tables/crosscheck.md`) |
| `tables/rt_consistency.md` | round trip vs ../dc_curves (low-frequency gain, step gain, replica operating point) and the slot rshunt check (written by `rt.py`) |
| `rshunt.py` | effect of rshunt=1e12 on the D2S schematic scalars (`tables/rshunt.md`) |
| `csv/*_summary.csv` | one row per run: the scalars evaluated from the curves (units in the header comment) |

## Tool versions and sources

- `ngspice -v`: `ngspice-47 : Circuit level simulation program`, `Compiled with KLU Direct Linear Solver`; IHP OSDI
  models of the PDK (`.spiceinit` of the PDK).
- CACE 2.11.0, XSCHEM V3.4.8RC (netlisting), Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2, PyYAML 6.0.3.
- PDK `/foss/pdks/ihp-sg13cmos5l` (IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e, as ../dc_curves).
- Design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single: 91a7da8b67ac56a26c605501146667a1fde28c32 (pad
  macros, CACE yaml / templates / committed results, S2D PEX netlist), 9052bd35928c6d40344e8e686c9abbe736bfadb9 (slot
  tier-1 decks). This repository: `pads/`, `../d2s_pex/` (D2S PEX netlist and its committed PEX CACE CSVs),
  `../dc_curves/` (fetch.sh, plot style) as of commit 57372f0.

## What this does NOT show

- No mismatch / Monte Carlo: all curves are systematic (corner) behaviour. In particular the S2D PSRR / CMRR (CACE
  `ac_mm_params`) need mismatch and are not plotted; the S2D common-mode curves are the systematic part only.
- Resistor / capacitor corners: typical only.
- No package, bond wire, ESD event, board or probe; sources ideal except the CACE testbench's rsrc (S2D) and load.
- C-coupled PEX only (no wire resistance); in the pad runs only the pad cell is extracted (bias_gen_pd and en_ctrl_3v3
  schematic); in the round trip the other slot blocks are the designer's views (KLayout-extracted pad_ref_rb /
  bias_dist_pd without parasitic capacitance, schematic bg_core_pd, source slot_7).
- Pad runs use the harness iDAC bias (5 µA, sel 0) and fixed vref / vcm, not the slot's bandgap / replica; only the
  round trip has the slot's own bias, and only in its default mode at five PVT points.
- Noise only for the pads alone (not the round trip); no 1/f-noise corner model beyond the PDK's.
- Enable transients of the pads alone (the slot power-up / mode transients are in ../slot_modes_bg).
- Large-signal behaviour only for the steps / sine listed (no slew-limited sine sweep, no overload recovery).
- Round trip with KLayout-extracted pads: AC at all five PVT points, step only at tt 27 °C, no sine (the run aborts,
  results.md); magic PEX pads: step at tt / ss −40 °C / ff 125 °C, sine at tt only.
- The D2S schematic values cannot be confirmed against its committed CACE CSVs, which are older than the schematic
  (results.md section 4); they are confirmed by the method (S2D and D2S PEX reproduced exactly).
