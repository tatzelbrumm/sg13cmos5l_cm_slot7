<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Terminal voltages of every MOS device in slot 7 and its two custom pads, compared with the PDK's HV limits

**IHP sg13cmos5l simulation**, ngspice-47 with the IHP OSDI models (PSP 103). The slot-level deck (bandgap, bias
distribution, replica bias, glue logic, both custom pads) of the designer's tier-1 testbench, with every MOS instance
of slot 7 and of both pads present: 499 MOS devices, all HV (`sg13_hv_nmos` 200, `sg13_hv_pmos` 299; no LV device and
no iNMOS). Numbers, tables and verdicts: **[results.md](results.md)**; all generated tables: [tables.md](tables.md).

## Question

The PDK process specification (`/foss/pdks/ihp-sg13cmos5l/libs.doc/doc/SG13CMOS5L_os_process_spec.pdf`, Rev. 0.2,
md5 `b0275fe63f332765fe1527a2d050c0fe`) states:

| section | device | statement (quoted) | breakdown (table row, min / max, measured at W x L) |
|---|---|---|---|
| 2.1.4 | HV-NMOS | "VGS ≤ 3.3 V (Maximum) @ 27°C for LG ≥ 0.6 µm" | BVDSSNHV013: min 5.3 V, target 6.1 V (10 x 0.45 µm²) |
| 2.1.5 | HV-PMOS | "VGS ≤ 3.3 V (Maximum) @ 27°C for LG ≥ 0.5 µm" | BVDSSPHV04: target −6.3 V, max −5.3 V (10 x 0.4 µm²) |
| 2.1.6 | HV-iNMOS | "VGS ≤ 3.3 V (Maximum) @ 27°C for LG ≥ 0.6 µm" | BVDSSNIHV045: min 5.2 V, target 6.1 V (10 x 0.45 µm²) |

each with the footnote "1 FIT in 10 years for HCI: for details see SG13G2 Qualification Report". Slot 7 runs from
3.3 V nominal; its characterization went to 3.6 V as a supply-tolerance corner; its switches and 3.3 V logic are HV
devices of W/L 1/0.45 µm ([HOW_IT_WORKS.md](../../../docs/chipalooza2_as_taped_out/HOW_IT_WORKS.md) sizing tables,
[README §2.2](../../../docs/chipalooza2_as_taped_out/README.md#22-supplies-enable-and-fail-safe) "Voltage limits
(PDK)"). Which terminal voltages does every MOS device actually see, and how do they compare with these statements?

## Method

### Deck (`vs.py`)

The designer's tier-1 slot deck (design repository `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`, commit
`9052bd35928c6d40344e8e686c9abbe736bfadb9`, `docs/slot7_hookup/tier1/run_tier1.py`, imported unchanged), built as
[../ac_tran/slot.py](../ac_tran/slot.py) builds it for the KLayout pad view:

- `slot_7` source netlist (`macros/slot_7/netlist/source/slot_7.spice`: `s7_ctrl` glue logic with 7 `ls_up_fs`,
  13 `nand2_hv`, 12 `inv_hv`, 10 `tg_hv`; `s7_doutpd`), `hv_logic` and `en_ctrl_3v3` source netlists;
- `bg_core_pd` schematic netlist (`netlist/schematic/bg_core_pd_magic.spice`), as in the designer's runs;
- `pad_ref_rb`, `bias_dist_pd` and both custom pads (`sg13cmos5l_IOPadSingle2Diff` = S2D, `sg13cmos5l_IOPadDiff2Single`
  = D2S) **KLayout-extracted** from the layout (`netlist/layout/*_klayout.cir`, converted and port-wrapped by
  `run_tier1.wrapped()`), with the antenna-diode fix of [../klayout_pad_diodes/fix_diodes.py](../klayout_pad_diodes/fix_diodes.py)
  applied (imported, unchanged) and the KLayout instance names `X$<n>` written `X_<n>` (a `$` would be expanded as a
  variable in ngspice's `.control` section). The extracted views merge parallel fingers into one device of the summed
  width, so the device count of the pads is that of the extracted netlist (S2D 65, D2S 64 MOS).
- `vdd_3v3` = `iovdd` = the supply under test; the pads' `vdd` / `vss` pins on `iovdd` / ground as in `run_tier1.py`
  (the extracted pads have no separate core-supply pins); `vdd_1v2` 1.2 V (only the `s7_doutpd` gates); harness
  `enable` 1.2 V; mode bits through the key as `../slot_modes_bg/slot_modes.py`; analog buses 1 GΩ to ground unless
  driven; D2S pad 1 GΩ to ground plus the load of the job; MOS corner on hv and lv, `res_typ`, `cap_typ`, pnp `typ`.
- `.option gmin=1e-12` (as the designer). Solver aids, recorded per run in `csv/runs.csv`: DC sweeps that fail are
  rerun with `rshunt=1e12`; the fail-safe DC sweeps (unpowered nodes held by leakage only) always run with it.
  Transients use `method=gear cshunt=1e-15` (as `run_tier1.py`'s own transient) and a 10 ns maximum step (as
  `../slot_modes_bg`); a failed transient is rerun with a 2 ns maximum step, then with a 0.5 ns maximum step. (The
  first pass retried with trapezoidal integration instead; its two results were discarded, results.md section 8.)

### Conditions (`jobs.txt`)

| job | what |
|---|---|
| `dc:<pvt>:open \| 1k \| 1kgnd` | enabled, default mode; DC sweep of the S2D pad source −0.2 V … max(3.3 V, supply) in 50 mV steps (contains 0, 0.5, 1.0 V and the range ends); D2S pad unloaded (1 GΩ), 1 kΩ to vterm = v(vref_d2s) (as `../ac_tran`; the 100 pF does not act at DC), or 1 kΩ to ground |
| `fs:<pvt>` | fail-safe: slot `vdd_3v3` = `vdd_1v2` = 0, enable 0, pad ring `iovdd` at the supply; both pads driven from one source swept 0 … supply, each through 1 kΩ |
| `fs0:<pvt>` | fail-safe: all supplies 0 V, both pads driven 0 … the supply level through 1 kΩ |
| `fst:<pvt>` | `fs` as a slow transient, for the −40 °C points where the `fs` DC sweep aborts in the S2D pad diode: from all nodes at 0 V, `iovdd` 0 → supply in 1 µs, pad source 0 V until 2 µs, then 0 → supply at 52 µs |
| `off:<pvt>` | disabled state, quasi-static: from the enabled operating point, enable 1.2 → 0 V at 1 µs (10 ns edge); S2D pad source 0.5 → −0.2 V (20 … 30 µs) → max(3.3 V, supply) (60 µs) → 0.5 V (70 µs). (A DC sweep of the disabled state does not converge: gmin and source stepping and the transient op fail at pad −0.2 V in the S2D pad diode.) |
| `en:<pvt>` | enable edges at the supply: 1.2 → 0 V at 2 µs, 0 → 1.2 V at 22 µs (10 ns edges), end 42 µs |
| `step:<pvt>:open \| 100p` | full-swing S2D pad steps from the enabled operating point at pad 0 V: 0 → supply at 2 µs, → −0.2 V at 12 µs, → 0.5 V at 22 µs (10 ns edges), end 32 µs; D2S pad unloaded or 1 kΩ to vterm + 100 pF |
| `mode:<pvt>` | mode switching (10 ns bit edges, through the key): default, swap at 2 µs, mon 12 µs, feed 22 µs, ext 32 µs, all_high 42 µs, default 52 µs, end 62 µs; bus0/1 driven (10 kΩ to 1.45 / 1.05 V) during feed, bus2/3 (10 kΩ to 1.30 / 0.50 V) during ext, through voltage-controlled switches |
| `pu:<pvt>` | power-up from all nodes at 0 V (`uic`): `vdd_3v3`, `iovdd` (and `vdd_1v2` to 1.2 V) 0 → supply in 10 µs, enable 1.2 V from t = 0, end 30 µs. Two slopes (0 → 0.3 V in 0.4 µs, then linear to 10 µs): with one linear slope ngspice's time step collapses at about 0.15 V (tt 27 °C 3.6 V: no progress past 409.5 ns in 500 s, also with `rshunt`) |
| `pu:<pvt>:fast` | the same with a 1 µs ramp, end 20 µs |
| `pu:<pvt>:late` | 10 µs ramp with enable 0, enable 0 → 1.2 V at 20 µs (100 ns edge), end 40 µs (the sequence of `../slot_modes_bg`) |

PVT points: DC jobs at the 5 MOS corners (tt, ss, ff, sf, fs) × −40 / 27 / 125 °C at 3.3 V and at 3.6 V, plus the
designer's two 3.0 V tier-1 points (ss / sf −40 °C); fail-safe jobs at the 30 points of 3.3 and 3.6 V (`fst` at the
ten −40 °C points); transients at tt 27 °C (3.3 and 3.6 V), at ff −40, ss 125, ff 125, ss −40, sf −40, fs 125 °C
(3.6 V) and at ff −40, ss 125 °C (3.3 V); `pu late` at tt 27 °C only. Which runs completed: `csv/runs.csv`.
The designer's five tier-1 PVT points (tt 27 °C 3.3 V, ss −40 °C 3.0 V, ff / fs 125 °C 3.6 V, sf −40 °C 3.0 V) are
all in the DC grid.

### Evaluation

- **Topology.** One run with ngspice `listing e` (the flattened, parameter-expanded netlist) gives every MOS instance
  (the `N…` OSDI device inside each PDK `sg13_hv_*` subcircuit, whose four nodes are the subcircuit's d / g / s / b
  directly, `rfmode=0`) with its four flattened terminal nodes, W, L, nf: `_work/topo.csv`. All later runs `save` exactly
  these nodes (284) and write a binary raw file.
- **Terminal voltages** per device and point: the *electrical* source is the lower of the two diffusion terminals for
  an NMOS and the higher for a PMOS (the layout netlists name drain and source arbitrarily); VGS = Vg − Vs, VGD = Vg − Vd,
  VDS = |Vd − Vs|, VGB, VSB, VDB. Per device and run: the largest |value| of each and where (sweep value or time), the
  largest |value| **held for at least 100 ns** (transients: sliding minimum over 11 points of a 10 ns grid; DC points
  count as held), and the time (points) with |VGS| or |VGD| above 3.3 V: `_work/dev/<run>.csv.gz`. Node maxima / minima
  per run: `_work/nodes/<run>.csv.gz`. Raw files are deleted after evaluation.
- **Classes.** A device "meets the spec LG" when L ≥ 0.6 µm (HV-NMOS) or L ≥ 0.5 µm (HV-PMOS); the others all have
  L = 0.45 µm. "Gate stress" in the tables = max(|VGS|, |VGD|), since a device conducts in either direction.
- `analyze.py` collects all runs into the tables of `tables.md`, `csv/` and the plots.
- **Solver and model check** (`edges.py`): the enable-edge transient at tt 27 °C 3.6 V again with a 2 ns and 0.5 ns
  maximum step, with trapezoidal integration, and with the PDK's non-quasi-static model card (`rfmode=1`, PSP NQS with
  `swnqs = 5`) on the devices of `bg_core_pd` and `ls_up_fs` (the two netlists with long-channel series stacks), and on
  `bg_core_pd` only; waveforms of the nodes with the largest excursions. Both NQS runs abort before the disable edge
  (results.md section 4); with `rfmode=1` on every MOS of the deck the transient does not start at all.

## Reproduce

```
verification/c2_gaps/voltage_stress/run.sh [<work_dir>] [fetch|sim|check|analyze|all]
```

from a checkout of this repository (default work dir `./_work` next to the script, not committed). `fetch` uses
`../dc_curves/fetch.sh` (shallow, blob-less clone of the design repository, `git archive` of commits 91a7da8b… and
9052bd35…; only 9052bd35 is used here). `sim` runs `jobs.txt` in order, one ngspice process at a time, and skips jobs
whose result exists (`FORCE=1` reruns them) and jobs that failed before (`RETRY=1` retries them). Environment:
`VS_TMO_DC` / `VS_TMO_TRAN` / `VS_TMO_PU` = ngspice time limit per try in s (defaults 240 / 1800 / 150; the 10 µs
power-up ramps use the smaller of `VS_TMO_TRAN` and `VS_TMO_PU`). The runs here: first pass with `VS_TMO_TRAN=600`,
the later passes with `VS_TMO_TRAN=240 VS_TMO_DC=120`, `check` with `VS_TMO_TRAN=1500` (the NQS variants with 500).
Wall clock in this session (4 shared CPUs, other jobs running): DC sweep 5 … 15 s (cold fail-safe sweeps up to the
time limit), transient 20 … 60 s per try, the 0.5 ns-step check run about 15 min; all passes together about 4 h.

## Files

| file | what |
|---|---|
| `run.sh` | everything, in steps |
| `vs.py` | deck builder, ngspice runner, per-device evaluation of one run |
| `rawread.py` | reader of ngspice binary raw files |
| `jobs.txt` | the job list (priority order) |
| `analyze.py` | tables (`tables.md`), CSVs, plots |
| `edges.py` | solver check of the edge transients |
| `results.md` | verdicts and the main tables |
| `tables.md` | all generated tables |
| `csv/runs.csv` | every run: conditions, status, solver aid, number of points |
| `csv/device_max.csv` | per MOS device (499 rows): block, W/L, nodes, max \|VGS\|, \|VGD\|, \|VDS\|, \|VGB\| over the 3.3 V and the 3.6 V runs with the run and point, held values |
| `csv/type_length_max.csv` | per device type × gate length × supply: maxima, where, number of devices above 3.3 V |
| `csv/flags_over_3v3.csv` | every device × run class with \|VGS\| or \|VGD\| > 3.3 V |
| `csv/top20_*_3v6.csv`, `csv/top20_*_3v3.csv` | top-20 devices over the 3.6 V runs (held and peak gate stress, held and peak \|VDS\|, peak \|VGS\|, \|VGB\|) and over the 3.3 V runs (held gate stress and \|VDS\|) |
| `csv/gate_stress_bins.csv` | number of devices per bin of their gate stress, per run class, gate-length class, peak / held |
| `csv/node_extremes.csv` | highest / lowest node voltage per job kind and supply |
| `csv/solver_check_*.csv` | `edges.py` results (per setting: node extremes, largest \|VGS\| and \|VDS\|) |
| `plots/ranked_vgs_vds_3v6.png` | per-device max(\|VGS\|, \|VGD\|) and \|VDS\| over the 3.6 V runs, ranked, colored by gate-length class; held values and the 3.3 V values of the same device as markers |
| `plots/hist_vgs_vds_3v6.png` | histograms of the same per-device maxima |
| `plots/solver_check_*.png` | node waveforms at the enable edges under different solver settings |

## Versions

- `ngspice -v`: `ngspice-47 : Circuit level simulation program`, compiled with KLU (the decks use the default SPARSE
  solver); IHP OSDI models loaded by the PDK `.spiceinit` (psp103, r3_cmc, …).
- PDK `/foss/pdks/ihp-sg13cmos5l` (IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e, as ../dc_curves).
- Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2. KLayout 0.30.12 and magic 8.3.685 are installed but not run here (the
  extracted netlists are the design repository's).
- Design repository commit 9052bd35928c6d40344e8e686c9abbe736bfadb9 (tier-1 deck, netlists). This repository:
  `../klayout_pad_diodes/fix_diodes.py`, `../dc_curves/fetch.sh` (unchanged; read at commit aa6b526).

## What this does NOT show

- **The spec's VGS limit is a reliability limit, not a breakdown limit.** "VGS ≤ 3.3 V (Maximum) @ 27°C" with the
  footnote "1 FIT in 10 years for HCI" is a hot-carrier lifetime statement for a gate length condition, at 27 °C. It
  does not say that a device fails above 3.3 V, and it says nothing for L = 0.45 µm (the specification states no
  maximum there, neither higher nor lower). Lifetime depends on how long and with what drain current and VDS the
  stress is applied (HCI needs channel current at high VDS); this study reports voltages, not lifetime, duty cycle or
  current. Gate-oxide (TDDB) limits for the HV oxide are not in the cited sections and are not assessed.
- BVDSS is a DC breakdown of a 10 × 0.4 / 0.45 µm² test device; it is compared here with the largest simulated |VDS|
  only. No avalanche, snapback or ESD event is simulated; the PSP models are not calibrated near breakdown.
- Only the conditions listed. No ESD, no latch-up, no supply above 3.6 V, no negative supply transients, no bond-wire
  inductance or ring noise, no supply sequencing other than the listed power-up shapes and the fail-safe DC states.
  Transients only at the PVT points of `jobs.txt` that completed (`csv/runs.csv`).
- Views: pads, `pad_ref_rb` and `bias_dist_pd` KLayout-extracted without parasitic capacitance; `bg_core_pd`
  schematic; glue logic and `s7_doutpd` source netlists (the taped-out `s7_ctrl` layout netlist is not used). Device
  sizes are those of these netlists. No magic-PEX or schematic pad view here.
- No Monte Carlo / mismatch; resistor, capacitor and pnp typical.
- Quasi-static MOS models: the multi-volt excursions of the internal nodes of the long-channel series stacks at fast
  gate edges (results.md section 4) exceed what capacitive coupling allows and are most likely the quasi-static
  channel-charge partition; the NQS runs that would show it aborted, so how far these nodes really go is not shown.
- Floating nodes of the disabled slot are held beyond the rails until the end of each run (tens of µs); how long they
  stay there in silicon (junction leakage over ms … s) is not simulated.
- Fail-safe DC states use `rshunt=1e12` (1 TΩ from every node to ground), which pulls otherwise floating nodes toward
  ground; their true leakage-determined voltages may differ.
