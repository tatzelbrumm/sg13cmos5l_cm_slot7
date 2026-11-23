<!-- SPDX-FileCopyrightText: 2026 Christoph Maier -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# D2S pad: post-layout (magic PEX) characterization

**IHP sg13cmos5l post-layout (magic PEX) simulation** of the taped-out pad `sg13cmos5l_IOPadDiff2Single` (D2S),
compared with its committed schematic CACE results. Results: [results.md](results.md).

## Why

The D2S pad had CACE results on its schematic only: the committed results (design repository commit
91a7da8b67ac56a26c605501146667a1fde28c32, `macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/`) predate
its layout, and no PEX view existed. The S2D pad has both views. This folder adds the PEX view of the D2S pad as
taped out (`pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds`, this repository; the cell in the chip
GDS is this cell unchanged), made the same way as the S2D pad's PEX view.

## Method (= S2D `make magic-pex EXT_MODE=2` + `make sim-cace CACE_SOURCE=pex`, design repository commit 9052bd35928c6d40344e8e686c9abbe736bfadb9)

1. `sak-pex.sh -d -m 2 -n sg13cmos5l_IOPadDiff2Single_pex` on the taped-out GDS: magic, C-coupled (EXT_MODE=2).
2. `scripts/pex_add_port.py ... vss iovss 1`: magic merges the vss band's p+ tie and the iovss ties into one
   substrate node, so the extracted cell has no vss port; vss is added and tied to iovss by 1 Ohm (the sheet's Rsub),
   as for S2D. Ports reordered to the symbol (`sak-pin-reorder.py` with `<cell>_pex.sym` = symbol with type=primitive).
   Result: [sg13cmos5l_IOPadDiff2Single_magic_pex_2.spice](sg13cmos5l_IOPadDiff2Single_magic_pex_2.spice)
   (293 devices + 482 coupling/ground capacitors; 4-line SPDX/provenance header added).
3. Device check: netgen LVS of the same extraction with the capacitors dropped against the committed schematic LVS
   netlist `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.spice`: **Circuits match uniquely**,
   76 = 76 devices after merging (hv_pmos 154 extracted fingers / hv_nmos 111 / rhigh 18 / rppd 2 / dantenna 4 /
   dpantenna 4), 36 = 36 nets; the only property errors are the schematic-only `mm_ok` (117 lines). vdd and vss are
   disconnected in both netlists (vss: the known vss/iovss substrate merge). [lvs_summary.txt](lvs_summary.txt).
4. CACE (`cace_pex.sh`): copy of the cell yaml with its own runs / netlist / docs folders and a layout path, the
   prepared netlist newer than the layout so CACE does not extract again; `scripts/cace/pex_for_sim.py --tie iovss 1e12`
   (20 capacitor-only nodes), subckt renamed to the cell name. The templates place en_ctrl_3v3 and bias_gen_pd next to
   the cell (schematic, as in the schematic runs): only the pad cell itself is the PEX view.
5. Two D2S-specific additions (not needed for S2D):
   - `pex_sense.py`: tb_dc reads IqP / IqN / Imin as `@n.x1.xfp.xop.nsg13_hv_pmos[ids]` / `...xfn.xon...`, schematic
     instance names (XOP ng=82, XON ng=68). Magic extracts each finger flat, so the source terminals of the 82 / 68
     extracted output fingers (counts checked) are moved to a node with a 0 V source, and the pex copy of tb_dc reads
     `i(v.x1.vop_sense)` / `i(v.x1.von_sense)` instead (total channel current of all fingers; bulk unchanged).
   - **rshunt**: the PEX netlist's operating point did not converge without help. dc_params (DC sweep from Vd = -1 V)
     ran in 25 of 30 runs as is; ac_params failed in all 15 runs (gmin and source stepping failed; singular nodes in
     the rhigh chains of the unit_r2 resistors, e.g. `x1.a_9918_32196#`). The same op of the schematic converges by
     true gmin stepping. With `.option rshunt=1e12` (1 TOhm from every node to ground) the PEX op at tt/27 C converged
     to v(pad) = 1.650053 V, i(vio) = -303.771 uA vs schematic 1.650042 V, -303.762 uA (diagnostic op runs in this
     task). Pass 2 therefore runs all groups with `RSHUNT=1e12` added to the templates that set none (tb_pd already
     has rshunt=1e14 and is left as is). The dc_params rerun with rshunt quantifies its effect against pass 1.
6. `compare.py`: min / median / max per quantity, schematic vs PEX, and the largest per-run change over runs with
   equal conditions. `plots.py`: per-corner plots.

Groups run (priority order): dc_params, ac_params, ac_load_params, tran_params, noise_params, drive_params,
enable_params, pd_params, thd_params. Not run: mm_params (mismatch is vacuous on an extracted netlist: magic writes no
mm_ok), dc_3v0 / dc_sel / dc_sel3 / dc_ibias / ac_1nF (not requested in this pass).

## Outcome (details and numbers: results.md)

All nine groups ran on the PEX view (pass 2, rshunt 1e12): 127 of 127 runs have results, and every quantity is
within the yaml limits (proposals). Largest PEX vs schematic shifts: bandwidth f3dB about -12 % (ac_params median
2.015 -> 1.774 MHz), slew rates about -12 ... -13 %, CMRR 1 kHz median 124 -> 109 dB, enable t_on up to +94 %
(median 0.854 -> 1.349 us), IqP / IqN about +5 %, Iio about +3.6 %, INL per run -9 ... +x % with the max 7.40 -> 7.50 mV
(ss/-40 C/3.3 V), integrated noise -4.6 %, Isc_snk +3.3 %; gain, PSRR, THD and output swing within about 2 %. Pass 1 (no rshunt): dc_params 25 of 30 runs.

## Reproduce

```
verification/c2_gaps/d2s_pex/run.sh [<work_dir>] [<group> ...]
```
from a checkout of this repository (it fetches the design repository commit itself: shallow, blobless, only the
paths it needs). Results go to `<work_dir>/out/`: `norshunt/dc_params.csv` and `rshunt1e12/<group>.csv` are
`csv/dc_params_pex_norshunt.csv` and `csv/<group>_pex_rshunt1e12.csv` here (3-line `#` header added), the
`compare_*.md` and `spec_table_pex.md` files are the tables of results.md, the PNGs are plots/.
Wall clock in this task (4 shared CPUs, 2 parallel ngspice): magic PEX < 1 min, pass 1 (dc_params) about 8 min,
pass 2 (all nine groups) about 10 min. PNG files carry no header: same copyright and license as this README.

## Tool versions

- ngspice-47 (KLU), IHP OSDI models from the PDK; magic 8.3.685; netgen 1.5.324; CACE 2.11.0; KLayout 0.30.12
  (not used by the flow); xschem (netlists the templates; IIC-OSIC-TOOLS install), sak-pex.sh / sak-pin-reorder.py
  (IIC-OSIC-TOOLS).
- PDK: /foss/pdks/ihp-sg13cmos5l -> IHP-Open-PDK commit df4c5054ee8ca481c3eb873687274f28cdb50b1e (2026-10-14).
- This repository: pad files from commit 158afc5afab0056bd6d216a4db3833e34a364949 (unchanged since commit e9a7479).
- Design repository: tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single 91a7da8b67ac56a26c605501146667a1fde28c32
  (D2S macro, yaml, templates, schematic results, scripts); method from 9052bd35928c6d40344e8e686c9abbe736bfadb9
  (S2D Makefile; scripts/pex_add_port.py, scripts/cace/pex_for_sim.py, cace_to_csv.py identical in both commits).

## What this does NOT show

- C-coupled extraction only: no wire resistance (EXT_MODE=3 full-RC not run), no substrate network beyond the
  vss-iovss 1 Ohm tie, no package / bond wire, no ESD event.
- Bias generator and enable logic (bias_gen_pd, en_ctrl_3v3) are schematic in both views: their layout is not part
  of this cell.
- Pass-2 numbers include rshunt = 1 TOhm on every node (the schematic results do not); the dc_params pass-1 vs pass-2
  comparison bounds its effect on the DC quantities only. Leakage-type quantities (pd_params) are in pA ... nA and
  tb_pd uses its own rshunt=1e14 in both views.
- No mismatch / Monte Carlo, and no silicon measurement. Limits in the yaml are proposals (see the yaml header).
- Failed runs are listed in results.md; they are not retried with other solver settings.
