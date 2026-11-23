#!/bin/bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Reproduce verification/c2_gaps/replica_bias/ (IHP sg13cmos5l simulation):
#   1. pad_ref_rb: cell from final/gds/slot_7.gds, XOR against the design repository's macro GDS, magic C-coupled PEX
#      (sak-pex.sh -m 2, as the design repo's magic-pex EXT_MODE=2), pin order of the symbol (sak-pin-reorder.py),
#      pex_for_sim.py --tie vssh 1e12, CACE groups vcm_dc / vcm_dc_3v0 / vref_room / vref_hot / vref_cold / pd on the PEX
#      view and (for reference) on the schematic.
#   2. pad_ref_rb: CACE mm_params (100 iterations, tt_mismatch 27 C 3.3 V, schematic), per-run CSV kept.
#   3. bias_dist_pd: copy ratio and leakage (5 corners x -40/27/125 C, vc 0.5 ... 2.5 V), schematic and magic C-coupled
#      PEX of the slot_7.gds cell; local-mismatch MC of the copy ratio (100 runs, tt 27 C).
#   (and netgen LVS of both extracted netlists, capacitors removed, against the source netlists: results/lvs_pex.log)
#   4. Tables (results.md body: results/tables.md) and plots.
# Usage: [JOBS=2] ./run.sh [<work_dir>]      (default: a new folder under ${TMPDIR:-/tmp}); results are written next to this
#        script into results/ (overwritten). Needs: PDK_ROOT/PDK (ihp-sg13cmos5l), ngspice (IHP OSDI models via the PDK
#        .spiceinit), cace 2.11, xschem, magic, klayout, sak-pex.sh / sak-pin-reorder.py (IIC-OSIC-TOOLS), git, python3
#        with pyyaml and matplotlib. JOBS=<1|2> simulations at a time (default 1).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOT=$(cd "$HERE/../../.." && pwd)                   # the slot repository (sg13cmos5l_cm_slot7)
WORK=${1:-$(mktemp -d "${TMPDIR:-/tmp}/replica_bias.XXXXXX")}
mkdir -p "$WORK"; WORK=$(cd "$WORK" && pwd)
OUT=$HERE/results
DESIGN_URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
DESIGN_COMMIT=9052bd35928c6d40344e8e686c9abbe736bfadb9
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=${PDK:-ihp-sg13cmos5l}
export PDKPATH=${PDKPATH:-$PDK_ROOT/$PDK}
JOBS=${JOBS:-1}                                     # simulations at a time (1 or 2)
echo "work: $WORK   results: $OUT"

# ---- design repository files at the commit (partial clone, no full checkout)
if [ ! -d "$WORK/dr" ]; then
  git clone -q --depth 1 --filter=blob:none --no-checkout "$DESIGN_URL" "$WORK/dr"
fi
git -C "$WORK/dr" fetch -q --depth 1 origin $DESIGN_COMMIT
rm -rf "$WORK/tree"; mkdir -p "$WORK/tree/pex"
P="scripts/cace schematic/xschem macros/pad_ref_rb macros/bias_dist_pd macros/hv_logic/netlist/source"
for d in en_ctrl_3v3 bias_gen_pd ls_up_1v2_3v3 hv_logic oa_core_pd bg_core_pd bias_tree_pd vcm_rb vref_s2d_rb; do
  P="$P macros/$d/schematic/xschem"
done
P="$P macros/vcm_rb/netlist/source macros/vref_s2d_rb/netlist/source"
git -C "$WORK/dr" archive FETCH_HEAD $P | tar x -C "$WORK/tree"
TREE=$WORK/tree
REF=$TREE/macros/pad_ref_rb/verification/cace/results/pad_ref_rb    # committed schematic CSVs (2026-11-07)
cp -r "$REF" "$WORK/committed_schematic"
rm -rf "$TREE/macros/pad_ref_rb/verification/cace/results"

# ---- layout as taped out: cells of slot_7.gds, XOR against the macro GDS of the design commit
mkdir -p "$OUT" "$WORK/lay"
: > "$OUT/gds_compare.log"
echo "slot repository: $(git -C "$SLOT" rev-parse HEAD); slot_7.gds blob $(git -C "$SLOT" rev-parse HEAD:final/gds/slot_7.gds)" \
  "(at 158afc5: $(git -C "$SLOT" rev-parse 158afc5afab0056bd6d216a4db3833e34a364949:final/gds/slot_7.gds))" >> "$OUT/gds_compare.log"
echo "sha256 $(sha256sum "$SLOT/final/gds/slot_7.gds" | cut -d' ' -f1)  final/gds/slot_7.gds" >> "$OUT/gds_compare.log"
for c in pad_ref_rb bias_dist_pd; do
  klayout -b -r "$HERE/gds_cell_compare.py" -rd a="$SLOT/final/gds/slot_7.gds" \
    -rd b="$TREE/macros/$c/layout/klayout/$c.klay.gds" -rd cell=$c -rd out="$WORK/lay/$c.gds" 2>&1 \
    | sed "s|$WORK|<work>|g; s|$SLOT|<slot>|g" >> "$OUT/gds_compare.log"
done
grep XOR_RESULT "$OUT/gds_compare.log"

# ---- magic C-coupled PEX (as make magic-pex EXT_MODE=2 in the design repository), pins in the symbol's order
mkdir -p "$OUT/pex"
for c in pad_ref_rb bias_dist_pd; do
  rm -rf "$WORK/pex_$c"; mkdir -p "$WORK/pex_$c"
  (cd "$WORK/pex_$c" && sak-pex.sh -m 2 -n ${c}_pex -w "$WORK/pex_$c" "$WORK/lay/$c.gds" > pex.out 2>&1)
  mv "$WORK/pex_$c/$c.pex.spice" "$WORK/pex_$c/${c}_magic_pex_2.spice"
  sed 's/type=subcircuit/type=primitive/' "$TREE/macros/$c/schematic/xschem/$c.sym" > "$WORK/pex_$c/${c}_pex.sym"
  sak-pin-reorder.py "$WORK/pex_$c/${c}_pex.sym" "$WORK/pex_$c/${c}_magic_pex_2.spice" --format spice > /dev/null
  grep -E 'warning' "$WORK/pex_$c/$c.pex.log" | sed "s/^/$c: /" || true
  # the netlist for simulation: capacitor-only nodes tied to vssh by 1 TOhm (none were found), subckt renamed to the cell
  python3 -I "$TREE/scripts/cace/pex_for_sim.py" "$WORK/pex_$c/${c}_magic_pex_2.spice" "$WORK/pex_$c/${c}_sim.spice" --tie vssh 1e12
  sed "s|^\* PEX produced on .* using|* PEX produced using|; s|$WORK|<work>|g" "$WORK/pex_$c/${c}_magic_pex_2.spice" > "$OUT/pex/${c}_magic_pex_2.spice"
done
cp "$WORK/pex_pad_ref_rb/pad_ref_rb_sim.spice" "$WORK/lay/pad_ref_rb.gds" "$TREE/pex/"
# LVS of the extracted netlists (capacitors removed) against the source netlists of the design commit
: > "$OUT/lvs_pex.log"
for c in pad_ref_rb bias_dist_pd; do
  "$HERE/lvs_check.sh" "$TREE" "$WORK/lvs" $c "$WORK/pex_$c/${c}_magic_pex_2.spice" "$OUT/lvs_pex.log"
done
cat "$OUT/lvs_pex.log"
sed -i 's/\bbias_dist_pd_pex\b/bias_dist_pd/g' "$WORK/pex_bias_dist_pd/bias_dist_pd_sim.spice"

# ---- 1. CACE on the PEX view and on the schematic (JOBS=2: side by side, one job each; JOBS=1: one after the other)
G="vcm_dc_params vcm_dc_3v0_params vref_room_params vref_hot_params vref_cold_params pd_params"
cp -r "$TREE" "$WORK/tree_sch"
if [ "$JOBS" -ge 2 ]; then
  CACE_JOBS=1 "$HERE/run_cace.sh" "$TREE" pex "$OUT/cace_pex" - $G > "$WORK/cace_pex.log" 2>&1 & PID=$!
else
  CACE_JOBS=1 "$HERE/run_cace.sh" "$TREE" pex "$OUT/cace_pex" - $G > "$WORK/cace_pex.log" 2>&1 || echo "PEX CACE: a spec missed or a run failed"
  PID=
fi
CACE_JOBS=1 "$HERE/run_cace.sh" "$WORK/tree_sch" schematic "$OUT/cace_schematic" - $G > "$WORK/cace_sch.log" 2>&1 || echo "schematic CACE: a spec missed or a run failed"
[ -n "$PID" ] && { wait $PID || echo "PEX CACE: a spec missed or a run failed"; }
grep -h ' runs -> ' "$WORK/cace_pex.log" "$WORK/cace_sch.log" | sed "s|$OUT/||"

# ---- 2. mismatch MC (CACE mm_params, 100 iterations, schematic), per-run CSV from the kept run folder
CACE_JOBS=$JOBS "$HERE/run_cace.sh" "$TREE" schematic "$WORK/mc" "$WORK/mc_runs" mm_params > "$WORK/mc.log" 2>&1 || echo "mm_params: a spec missed"
mkdir -p "$OUT/mc"
cp "$WORK/mc/summary_mm_params.md" "$OUT/mc/"
python3 -I "$HERE/mc_collect.py" "$WORK/mc_runs/mm_params" "$OUT/mc/mm_params_runs.csv" "$OUT/mc/mm_params_stats.csv"

# ---- 3. bias_dist_pd
mkdir -p "$OUT/bias_dist"
python3 -I "$HERE/bias_dist_copy.py" "$TREE" "$WORK/bd_sch" "$OUT/bias_dist" -j $JOBS
python3 -I "$HERE/bias_dist_copy.py" "$TREE" "$WORK/bd_pex" "$OUT/bias_dist" --dut "$WORK/pex_bias_dist_pd/bias_dist_pd_sim.spice" -j $JOBS
cat "$TREE/macros/hv_logic/netlist/source/hv_logic.spice" "$TREE/macros/bias_dist_pd/netlist/source/bias_dist_pd.spice" > "$WORK/bdp_src.spice"
python3 -I "$TREE/scripts/cace/pex_for_sim.py" "$WORK/bdp_src.spice" "$WORK/bdp_sch_mm.spice" --mm-ok
python3 -I "$TREE/scripts/cace/pex_for_sim.py" "$WORK/pex_bias_dist_pd/bias_dist_pd_sim.spice" "$WORK/bdp_pex_mm.spice" --mm-ok
python3 -I "$HERE/bias_dist_mc.py" "$WORK/bdp_sch_mm.spice" "$WORK/bdmc_sch" "$OUT/bias_dist/bias_dist_mc_schematic.csv" -n 100 -j $JOBS
python3 -I "$HERE/bias_dist_mc.py" "$WORK/bdp_pex_mm.spice" "$WORK/bdmc_pex" "$OUT/bias_dist/bias_dist_mc_magic_pex_2.csv" -n 100 -j $JOBS

# ---- 4. SPDX headers on the generated text files, tables and plots
rm -f "$OUT"/cace_*/cace_*.log
python3 -I "$HERE/spdx_stamp.py" $(find "$OUT" -name '*.csv' -o -name '*.md' -o -name '*.spice' -o -name '*.log')
python3 -I "$HERE/analyze.py" "$OUT" "$WORK/committed_schematic" > "$OUT/tables.md"
python3 -I "$HERE/spdx_stamp.py" "$OUT/tables.md"
echo "done: $OUT (work folder $WORK can be deleted)"
