<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# KLayout-extracted pads: antenna diodes simulated at the wrong size

**IHP sg13cmos5l simulation**, ngspice-47 with the IHP OSDI models and the PDK's `diodes.lib`. Slot 7 tier-1 deck of
the designer (design repository commit 9052bd35), pads in the KLayout-extracted view that the designer's tier-1 /
mode scripts use. Follow-up to [../ac_tran/results.md](../ac_tran/results.md) section 1 (the 10 kHz sine through the
KLayout-extracted pads aborts), [../slot_modes_bg](../slot_modes_bg) (ss / sf −40 °C aborts in the pads' antenna
diodes) and [../dc_curves/results.md](../dc_curves/results.md) section 3 (KLayout-extracted pads shift the round-trip
range ends by up to 55 mV). Status: complete (runs of 2026-11-25).

## Question and hypothesis

The KLayout-extracted pad netlists are converted to simulator syntax by the designer's scripts before simulation.
Hypothesis: the antenna / ESD diodes come out of that conversion at the wrong size (the converted call passes `a=` /
`p=`, the PDK subcircuit reads only `l` / `w`), and that is what makes the sine abort and perhaps shifts the range ends.

## Answer

| item | result |
|---|---|
| conversion bug | **real**. Every `dantenna` / `dpantenna` of both pads is simulated at the PDK default size 0.78 × 0.78 µm. ngspice prints no message about it. |
| 10 kHz sine, tt 27 °C, KLayout pads (the open item of ../ac_tran) | **cured by the size fix**. Runs through with no solver aid. Matches the schematic pads to 0.07 mV (unloaded). |
| why the wrong size makes the sine abort | `darea` (the area part of `dantenna`) has a current step of 37 pA in ngspice at a reverse voltage of exactly 3·n·kT/q = 78.3 mV. pad_s2d = 0.0783 V is that voltage on the S2D pad diode X$65. With the default size, ngspice cannot get past the step. With the extracted size, it can. |
| round-trip DC range ends (../dc_curves) | **not explained by the diodes**. They are unchanged by the fix: every node within 2 nV at all five PVT points. The shift sits in the S2D output common mode, which is 33 mV lower in the KLayout view at tt 27 °C. The cause is not found here. |
| AC / step through the KLayout pads (../ac_tran) | almost unchanged by the fix: f−3dB +0.04 … +0.07 %, settling −0.3 ns |
| ss −40 °C mode DC (../slot_modes_bg) | **not cured**. All five failing modes still fail with the diodes fixed. |
| sf −40 °C power-up transients (../slot_modes_bg) | **not cured**. Both still abort, now earlier in the supply ramp. |
| magic PEX round trip at sf −40 °C, which stops at pad in 1.435 V (../dc_curves) | not addressed: the PEX netlist already has `l` / `w` |

## Where the bug is (for the designer)

Design repository `tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`, commit
`9052bd35928c6d40344e8e686c9abbe736bfadb9`, file `macros/en_ctrl_3v3/testbenches/spice/run_starve.py`, function
`convert()`, lines 44–45:

```python
        elif k == "D":
            out.append(f"X{t[0][1:]} {t[1]} {t[2]} {t[3]} " + " ".join(p.lower() for p in t[4:]))
```

KLayout's SG13 LVS writes `D$65 iovss pad dantenna A=35.0028p P=58.08u m=2`, with the area in m² and the perimeter in
m. `convert()` turns this into the subcircuit call `X$65 iovss pad dantenna a=35.0028p p=58.08u m=2`.

The PDK subcircuits are in `libs.tech/ngspice/models/diodes.lib`, lines 49–57 and 80–87:

```
.subckt dantenna 1 2
.params l=780n   w=780n   DEV_A=(l*w)/1p  DEV_P=(l+w)/0.5u  DEV_C=4
D1 1 2 darea area=DEV_A
D2 1 2 dperim area=DEV_P
D3 1 2 dcorner area=DEV_C
```

These subcircuits take only `l` and `w`. ngspice drops the unknown `a=` / `p=` without a message. Each diode therefore
gets DEV_A = 0.6084 and DEV_P = 3.12 instead of 35.0028 / 58.08 (S2D X$63, X$65) and 82.908 / 134.12, 85.176 / 137.72
(D2S X$3, X$5); that is 0.7 … 1.7 % of the area. The D2S's internal clamp diodes X$165 … X$168 (1.98 / 3.19 µm²) are
affected too.

`convert()` is used by:

- `docs/slot7_hookup/tier1/run_tier1.py` `wrapped()` (line 37);
- `run_modes.py` (through `run_tier1`);
- `run_starve.py` itself.

Its starvation results (`results/starve.txt`) therefore also have undersized pad diodes; the effect is not quantified
here.

Fix at the source: give the D line `l` / `w` from A / P (a rectangle with l·w = A and 2(l + w) = P, which gives the
model exactly DEV_A = A / 1 µm² and DEV_P = P / 1 µm), as [fix_diodes.py](fix_diodes.py) does. For these pads that
gives exactly the schematic sizes, e.g. 27.78 × 1.26 µm. The default branch `main` of the design repository
(60f270a, 2026-09-30) predates this file; later commits were not checked.

## Evidence

1. **Parameter handling** (`csv/diode_params.csv`, `diode_check.py`). `listing expand` of a `dpantenna` called with
   `a=35.0028p p=58.08u m=2` gives `dparea area=0.6084`, `dpperim area=3.12`, `dpcorner area=4`, the same as a call
   with no parameters. With `l=27.78u w=1.26u` the areas are 35.0028 / 58.08 / 4. ngspice gives no warning.
2. **The fix is the only change.** [run_fixed.py](run_fixed.py) imports the unchanged scripts `../ac_tran/slot.py`,
   `../dc_curves/roundtrip.py` and `../slot_modes_bg/slot_modes.py`. It wraps `run_tier1.wrapped()` so that each
   converted netlist goes through [fix_diodes.py](fix_diodes.py). A `diff` of the decks and netlists against the
   failed ../ac_tran run differs only in the eight diode lines (plus `rshunt`, which the failed run had from its retry).
3. **Sine, tt 27 °C 3.3 V** (`csv/sine_summary.csv`, `csv/sine_tt27.csv`, `plots/sine_tt27_fixed.png`).
   - **Control** (as converted, rerun here): aborts at 65.9723 µs, "timestep too small … v.xs.vsv0#branch", and again
     with rshunt, as in ../ac_tran.
   - **Fixed**: runs to 600 µs on the first try (gear, no rshunt). Measured over 200 … 600 µs:

     | pads, load | THD [dB] | gain | delay [ns] | error [mVpp] |
     |---|---|---|---|---|
     | KLayout fixed, unloaded | −78.3 | 0.9985 | 148 | 9.3 |
     | schematic, unloaded | −78.2 | 0.9986 | 146 | 9.2 |
     | magic PEX, unloaded | −77.9 | 0.9986 | 164 | 10.3 |
     | KLayout fixed, 1 kΩ ∥ 100 pF | −69.9 | 0.9984 | 175 | 11.4 |
     | schematic, 1 kΩ ∥ 100 pF | −72.5 | | | |
     | magic PEX, 1 kΩ ∥ 100 pF | −72.0 | | | |

     pad_d2s (KLayout fixed) − pad_d2s (schematic) is at most 0.072 mV (unloaded); magic PEX − schematic is 0.58 mV.
4. **Mechanism: the diode alone** (`csv/diode_iv_step.csv`, `csv/diode_tran.csv`, `plots/diode_step_27C.png`).
   - **The step.** The reverse current of `dantenna` (m = 2, as X$65) steps by 74 pA (37 pA per diode, all in `darea`)
     between 78.0 and 78.5 mV at 27 °C. That is 3·n·kT/q with n = 1.009: there ngspice's diode model switches from
     its forward to its reverse expression.
   - **Size, temperature, formula.** The step has the same size for both diode sizes, so it does not scale with area.
     It is 4.9 pA at −40 °C (at 60.8 mV) and 0.76 nA at 125 °C (at 103.8 mV). It matches the `darea` soft-breakdown
     term ibv·exp(−(bv − 3nkT/q)/(nbv·kT/q)) = 3.458e-7 · exp(−(11.64 − 0.0783)/(48.9 · 0.02587)) = 37.06 pA (nbv =
     48.9 makes this term large at small reverse voltage). `dperim`, `dcorner` and the `dpantenna` models show no step.
   - **DC sweep in 0.1 mV steps.** With the default size the sweep does not finish (60 s timeout) at 27 and 125 °C;
     with the extracted size it does.
   - **Minimal transient.** X$65 alone with the ideal sine on its cathode aborts at exactly 65.9723 µs (cathode at
     0.0783 V) with the default size, with gear and with trap. With the extracted size it runs through. This is the
     same abort time as the slot run.
   - **Diagnosis on modified model copies.** Default size with `darea` ibv → 1e-30, rs → 0 or tt → 0 runs through;
     with cj0 → 0 it stalls at 65.9727 µs. The extracted size with the default-size rs *and* cj0 aborts again; either
     one alone does not. So the abort needs the step together with the series resistance and junction capacitance
     of the default-size `darea`.
   - **The schematic and PEX views have the same step**; with the extracted size ngspice gets through it. The
     KLayout view failed only because its diodes are 57× too small.
5. **DC round trip** (`csv/rt_range.csv`).
   - **Unchanged by the fix.** At all five tier-1 PVT points the fixed and the as-converted KLayout runs agree to 2 nV
     at every saved node, so the range ends are unchanged; e.g. tt 27 °C pad in −0.172 … 1.245 V vs schematic
     −0.171 … 1.281 V.
   - **Where the difference is instead.** At pad in 0.5 V, tt 27 °C, the S2D output common mode (outp + outn)/2 is
     1.2358 V in the KLayout view vs 1.2684 V schematic and PEX, while vcm_s2d (the replica reference) is 1.2566 V in
     all three. The S2D differential output therefore reaches its swing limit earlier. The cause in the extracted S2D
     netlist is not found. A candidate, not tested: KLayout merges each of the six four-segment `rhigh` chains
     (4 × 12.65 µm, `unit_r2`, which includes the common-mode sense pair XM1 / XM2) into one 50.6 µm device
     (R$126 … R$131).
6. **AC / step, tt 27 °C** (`csv/ac_step_tt27.csv`).
   - **f−3dB:** 1.5153 / 1.2203 / 1.4879 MHz (unloaded / 10 pF / 100 pF) vs 1.5142 / 1.2197 / 1.4873 MHz in ../ac_tran.
   - **Unloaded step, settling to 1 %:** 466.3 vs 466.5 ns.
7. **Slot modes at −40 °C** (`csv/modes_fixed.csv`).
   - **ss −40 °C mode DC:** the designer's DC deck (slot_modes.py `dcop`) with the diodes fixed. swap, mon, feed, ext
     and swap+feed still fail: gmin and source stepping fail, then the "transient op" ends with "timestep too small",
     now in every mode at `d.x2s.xlay.x$63.d1`. That is `dparea` of the S2D pad diode pad → iovdd, a model with no
     step (item 4). Before the fix, swap failed at the D2S's `x$3`.
   - **sf −40 °C power-up:** mon (10 pF) and swap (1 GΩ only) abort at 6.26 µs, in the supply ramp, at `d.x2d.xlay.x$3.d1`
     / `x$167.d1`. In ../slot_modes_bg, mon aborted at 20.07 µs.
   - **Conclusion:** the size fix does not explain these aborts. The instance that ngspice names is where its
     ramp gives up, not a demonstrated cause.

## What it means for the documented results

- **../ac_tran:**
  - The KLayout sine is no longer missing. With the extracted diode size it matches the schematic pads (item 3). The
    "TBD" of results.md section 1 has its cause: the converted KLayout netlists (design repository `run_starve.convert()`)
    and the 37 pA step of `darea` in ngspice. No solver option fixes it, which matches what ../ac_tran found
    (cshunt, rshunt, step size, sine phase).
  - The KLayout AC / step rows were simulated with undersized diodes. Their numbers change by under 0.1 % (item 6).
- **../dc_curves:** the KLayout range-end shift (up to 55 mV) stands as documented and is **not** a diode effect. It is
  in the S2D output common mode of the extracted netlist (item 5), still unexplained.
- **../slot_modes_bg:** the remark on `a=` / `p=` is confirmed and located. The −40 °C DC / power-up aborts are **not**
  explained by it (item 7); they remain open.
- **Designer's own scripts:** `run_tier1.py`, `run_modes.py` and `run_starve.py` all simulate the pad diodes at 0.7 …
  1.7 % of their area. The 5 mV and 50 mV DC sweeps went through. The diode alone does not finish a 0.1 mV sweep
  at 27 °C, so a DC point can land where ngspice gets stuck. A transient that takes the S2D pad through 78 mV at
  27 °C aborts. The step is also at 61 mV (−40 °C, 4.9 pA) and 104 mV (125 °C, 0.76 nA); whether a transient aborts
  there was not tested.

## Method

- [fix_diodes.py](fix_diodes.py) rewrites `dantenna` / `dpantenna` calls with `a=` / `p=` (SI suffixes; m², m) to
  `l=` / `w=`, keeping `m=` and everything else. l = (s + √(s² − 4A))/2 and w = A/l with s = P/2, which is real for
  every rectilinear outline (P ≥ 4√A).
- [run_fixed.py](run_fixed.py) runs an existing slot script with that fix inserted. Each script's own decks, options
  and evaluation are unchanged; the decks go to separate run folders.
- [diode_check.py](diode_check.py) runs the PDK diode alone in ngspice: the parameter listing, the I–V sweeps and the
  minimal transients (item 4). The modified model copies used for the diagnosis exist only in the work folder.
- [evaluate.py](evaluate.py) writes the CSVs and plots. It takes the sine scalars from `../ac_tran/rt.py`
  (`sine_scalars`: THD from harmonics 2–7 over 4 periods) and the DC ranges from `../dc_curves/rt.py` (`metrics`).
  The schematic / PEX sine runs are ../ac_tran's (its work folder `out/slot`); the DC schematic / PEX / KLayout runs
  are rerun here and reproduce ../dc_curves' committed CSV exactly at its printed precision (all 15 runs, including
  the magic PEX sf −40 °C abort at 1.435 V).
- Solver settings as in the scripts: `.option gmin=1e-12`, transients `method=gear`, sine max step 39.0625 ns; PEX
  pads rshunt=1e12 (../ac_tran). The fixed KLayout runs needed no aid.

## Reproduce

```
verification/c2_gaps/klayout_pad_diodes/run.sh <ac_tran_work_dir> [<work_dir>] [diode|sine|dc|modes|eval|all]
```

`<ac_tran_work_dir>` is the work folder of `../ac_tran/run.sh` after its `fetch`, `s2d`, `d2s` and `slot` steps. It
provides `design/` and `tier1/` (design commits 91a7da8b / 9052bd35, fetched shallow and blob-less by
`../dc_curves/fetch.sh`) and `out/slot`. The default work dir is `./_work` (not committed).

Wall clock in this session (4 CPUs):

| step | time |
|---|---|
| diode | 3 min |
| sine | 6 min |
| dc | 11 min (10 of them the magic PEX run at sf −40 °C, which aborts at pad in 1.435 V as in ../dc_curves) |
| modes | 4 min |
| eval | under 1 min |

## Files

| file | what |
|---|---|
| `fix_diodes.py` | the netlist fix (a= / p= → l= / w=); also usable on one converted netlist from the command line |
| `run_fixed.py` | runs ../ac_tran/slot.py, ../dc_curves/roundtrip.py or ../slot_modes_bg/slot_modes.py with the fix |
| `diode_check.py` | the PDK antenna diode alone: parameters, I–V step, minimal abort |
| `evaluate.py` | CSVs and plots below |
| `run.sh` | everything, in steps |
| `csv/diode_params.csv` | area factors each component diode gets for a= / p=, l= / w=, no parameters |
| `csv/diode_iv_step.csv` | largest current step per device / temperature / sweep step, and whether the sweep finished |
| `csv/diode_iv_27C.csv` | dantenna reverse current 60 … 100 mV, 27 °C, both sizes (the plot) |
| `csv/diode_tran.csv` | X$65 alone under the sine: completed / aborted (time, voltage, instance) per case |
| `csv/sine_summary.csv` | sine scalars, tt 27 °C, three pad views × unloaded / 1 kΩ ∥ 100 pF |
| `csv/sine_tt27.csv` | sine waveforms 200 … 600 µs (1024 points): pad_s2d, pad_d2s and error per view, unloaded |
| `csv/rt_range.csv` | DC round trip per PVT: committed ../dc_curves rows, reruns, KLayout fixed; S2D output CM |
| `csv/ac_step_tt27.csv` | f−3dB and step settling, KLayout fixed vs ../ac_tran committed |
| `csv/modes_fixed.csv` | slot_modes.py runs with the fix (ss −40 °C mode DC, sf −40 °C power-up) |
| `plots/sine_tt27_fixed.png` | error vs expected for the three views and two loads (top), difference to schematic (bottom) |
| `plots/diode_step_27C.png` | the 74 pA step of dantenna (m = 2) at 78.3 mV, both sizes |

## Versions

- `ngspice -v`: `ngspice-47 : Circuit level simulation program` (compiled with KLU; the decks use the default solver).
- IHP OSDI models of the PDK, loaded by the PDK `.spiceinit`.
- Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2, Pillow 12.3.0.
- PDK `/foss/pdks/ihp-sg13cmos5l` (IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e, as ../dc_curves);
  `diodes.lib` md5 8719a4f26feeaba7c3f5466eb64b96da.
- Design repository tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single: 9052bd35928c6d40344e8e686c9abbe736bfadb9
  (tier-1 deck, `run_starve.convert()`, KLayout pad netlists) and 91a7da8b67ac56a26c605501146667a1fde28c32 (CACE
  schematic / PEX pad netlists, via ../ac_tran).
- This repository: `../ac_tran/slot.py`, `../dc_curves/roundtrip.py`, `../slot_modes_bg/slot_modes.py`, unchanged.

## Not covered

- **Other PVT points of the sine:** only tt 27 °C was run with the KLayout pads (as in ../ac_tran). At other
  temperatures the step sits at 61 mV (−40 °C) or 104 mV (125 °C), and is 0.76 nA at 125 °C.
- **The root cause of the remaining −40 °C aborts and of the range-end shift:** not found (items 5 and 7).
- **Starvation results:** run_starve.py's results with corrected diodes were not rerun.
