#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# IHP sg13cmos5l schematic simulation: full CACE suite of the D2S pad sg13cmos5l_IOPadDiff2Single on its current
# (taped-out) schematic, design repository commit 91a7da8b, yaml and templates unchanged; comparison with the
# committed (stale) schematic results and a regenerated data-sheet candidate.
# Usage: run.sh [<work_dir>] [fetch|netcheck|sim|csv|compare|results|datasheet|all]   (default ./_work next to this script, all)
# Environment: JOBS = parallel ngspice runs per group (default 3); RSHUNT_GROUPS = groups to run with ngspice
# rshunt=1e12 (default drive_params, the only group that did not converge without it, see README.md).
# Needs: PDK_ROOT with ihp-sg13cmos5l, ngspice-47 with the IHP OSDI models, xschem, CACE 2.11, python3 with pyyaml,
# git with network access to github.com (shallow, blobless fetch of one commit; only the needed paths are extracted).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOT=$(cd "$HERE/../../.." && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export JOBS=${JOBS:-3}
export PYTHONDONTWRITEBYTECODE=1
T=sg13cmos5l_IOPadDiff2Single
URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
C=91a7da8b67ac56a26c605501146667a1fde28c32
GROUPS_="dc_params dc_3v0_params dc_sel_params dc_sel3_params dc_ibias_params ac_params ac_load_params ac_1nF_params
 tran_params thd_params noise_params drive_params pd_params enable_params mm_params"
RSHUNT_GROUPS=${RSHUNT_GROUPS-drive_params}
M=$WORK/design/macros/$T
CY=$M/verification/cace/$T.yaml
OLD=$M/verification/cace/results/$T
DS=$SLOT/docs/chipalooza2_as_taped_out/datasheets
mkdir -p "$WORK"

fetch() {
  [ -d "$WORK/repo" ] || git clone -q --depth 1 --filter=blob:none --no-checkout "$URL" "$WORK/repo"
  git -C "$WORK/repo" fetch -q --depth 1 origin $C
  local P="scripts/cace macros/$T/schematic macros/$T/verification/cace macros/$T/netlist"
  for d in en_ctrl_3v3 bias_sel_pd bias_gen_pd ls_up_1v2_3v3 hv_logic IOPad oa_core_pd bg_core_pd bias_tree_pd \
           bias_tree_noab_pd bias_sel_noab_pd bias_in_pd bias_out_pd bias_oa_pd bias_bg_pd; do
    P="$P macros/$d/schematic/xschem"
  done
  rm -rf "$WORK/design" && mkdir -p "$WORK/design"
  git -C "$WORK/repo" archive $C $P | tar x -C "$WORK/design"
}

# Which netlist: CACE 2.11 always regenerates the schematic netlist (xschem -n -s -r -x -q --tcl "set top_is_subckt 1"
# in the schematic folder, project xschemrc). Netlist it the same way and compare it, comments (** lines) dropped,
# with the taped-out cell's LVS netlist pads/<cell>/<cell>.spice (its 4-line provenance header dropped).
netcheck() {
  mkdir -p "$WORK/netcheck"
  (cd "$M/schematic/xschem" && xschem -n -s -r -x -q --tcl "set top_is_subckt 1" -o "$WORK/netcheck" -N cace_sch.spice $T.sch > /dev/null 2>&1)
  tail -n +5 "$SLOT/pads/$T/$T.spice" > "$WORK/netcheck/pad_lvs.spice"
  {
    echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"
    echo "# SPDX-License-Identifier: Apache-2.0"
    echo "# CACE schematic netlist (xschem, design commit ${C:0:8}) vs taped-out LVS netlist pads/$T/$T.spice"
    echo "sha256 pads/$T/$T.spice without its 4-line header: $(sha256sum < "$WORK/netcheck/pad_lvs.spice" | cut -d' ' -f1)"
    echo "sha256 design $C:macros/$T/netlist/schematic/${T}_magic.spice: $(sha256sum < "$M/netlist/schematic/${T}_magic.spice" | cut -d' ' -f1)"
    echo "lines (without ** comments): CACE $(grep -vc '^\*\*' "$WORK/netcheck/cace_sch.spice"), LVS $(grep -vc '^\*\*' "$WORK/netcheck/pad_lvs.spice")"
    echo "diff LVS -> CACE (** comment lines dropped):"
    diff <(grep -v '^\*\*' "$WORK/netcheck/pad_lvs.spice") <(grep -v '^\*\*' "$WORK/netcheck/cace_sch.spice") || true
    echo "Rsub in the schematic:"
    grep -A5 'name=Rsub$' "$M/schematic/xschem/$T.sch" | tr '\n' ' '; echo
  } > "$HERE/netcheck.txt"
  cat "$HERE/netcheck.txt"
}

sim() {
  local g plain=""
  for g in $GROUPS_; do
    case " $RSHUNT_GROUPS " in *" $g "*) RSHUNT=1e12 "$HERE/cace_sch.sh" "$WORK" "$WORK/out" $g || echo "WARNING: $g failed" ;;
                                   *) plain="$plain $g" ;; esac
  done
  [ -z "$plain" ] || "$HERE/cace_sch.sh" "$WORK" "$WORK/out" $plain || echo "WARNING: a group failed (see $WORK/out/log_*.txt)"
}

# result files of this folder: CSV (2-line SPDX header added, else as cace_to_csv.py writes it), CACE summary
# (SPDX comment added), solver aid per group
csv() {
  mkdir -p "$HERE/csv"
  local g
  for g in $GROUPS_; do
    [ -f "$WORK/out/$g.csv" ] || continue
    [ -f "$WORK/out/aid_$g.txt" ] || { echo "no aid_$g.txt"; exit 1; }
    { echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "# SPDX-License-Identifier: Apache-2.0"
      cat "$WORK/out/$g.csv"; } > "$HERE/csv/$g.csv"
    { echo "<!--"; echo "SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "SPDX-License-Identifier: Apache-2.0"
      echo "solver aid: $(cat "$WORK/out/aid_$g.txt")"; echo "-->"; cat "$WORK/out/summary_$g.md"; } > "$HERE/csv/summary_$g.md"
  done
  # drive_params without the aid (3 of 10 runs without result; see README.md), kept as the evidence for the aid
  if [ -f "$WORK/out/drive_params_norshunt.csv" ]; then
    { echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "# SPDX-License-Identifier: Apache-2.0"
      echo "# drive_params WITHOUT rshunt: runs without a complete result are missing (tt -40: ngspice killed by hand after 15.6 min; sf / ff -40: first DC sweep did not converge)"
      cat "$WORK/out/drive_params_norshunt.csv"; } > "$HERE/csv/drive_params_norshunt.csv"
  fi
}

compare() {
  mkdir -p "$HERE/tables" "$WORK/pexres"
  python3 "$HERE/compare.py" "$CY" "$OLD" "$HERE/csv" "$HERE/tables/compare_committed.md" "$HERE/tables/compare_committed.csv" $GROUPS_
  # magic PEX results of ../d2s_pex (pass 2, rshunt 1e12) vs this schematic run
  local f g
  for f in "$SLOT"/verification/c2_gaps/d2s_pex/csv/*_pex_rshunt1e12.csv; do
    g=$(basename "$f" _pex_rshunt1e12.csv); cp "$f" "$WORK/pexres/$g.csv"
  done
  python3 "$HERE/compare.py" "$CY" "$HERE/csv" "$WORK/pexres" "$HERE/tables/compare_pex.md" "$HERE/tables/compare_pex.csv" \
    $(cd "$WORK/pexres" && ls *.csv | sed 's/\.csv$//')
}

# data-sheet candidate: make_datasheet.py on the new results (comment lines stripped: its CSV reader expects none),
# then: the hand-made Figures section of the current data sheet inserted before the specification (its marker says
# to keep it), and the generator's provenance lines, which describe committed results, replaced by this run's.
datasheet() {
  local R=$WORK/ds/$T g
  rm -rf "$WORK/ds" && mkdir -p "$R"
  for g in $GROUPS_; do
    [ -f "$HERE/csv/$g.csv" ] || continue
    grep -v '^#' "$HERE/csv/$g.csv" > "$R/$g.csv"
    cp "$HERE/csv/summary_$g.md" "$R/summary_$g.md"
  done
  sed '1,/^-->$/d' "$HERE/datasheet_intro.md" > "$WORK/ds/intro.md"   # SPDX comment of the source files dropped
  sed '1,/^-->$/d' "$HERE/datasheet_notes.md" > "$WORK/ds/notes.md"
  python3 "$DS/tools/make_datasheet.py" "$CY" "$WORK/ds/raw.md" \
    --title "$T (D2S pad, s7_an[1]): characterization data sheet" --repo-url "$URL" --commit $C \
    --cell-path macros/$T --view "schematic=$R" --intro "$WORK/ds/intro.md" --notes "$WORK/ds/notes.md"
  python3 "$HERE/ds_post.py" "$WORK/ds/raw.md" "$DS/$T.md" "$HERE/$T.regenerated.md"
}

# results.md = results_head.md (hand-written text) + the two generated tables
results() {
  { cat "$HERE/results_head.md"
    grep -v '^<!--' "$HERE/tables/compare_committed.md"
    printf '\n## 5. Per quantity, this schematic re-run ("old") vs magic PEX of ../d2s_pex ("new") (= tables/compare_pex.md)\n\n'
    grep -v '^<!--' "$HERE/tables/compare_pex.md"; } > "$HERE/results.md"
}

case "$STEP" in
  all) fetch; netcheck; sim; csv; compare; results; datasheet ;;
  fetch|netcheck|sim|csv|compare|results|datasheet) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
