#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# IHP sg13cmos5l simulation: the Monte Carlo groups of the S2D pad sg13cmos5l_IOPadSingle2Diff (s7_an[0]) re-run with
# the per-run data kept (mm_params, ac_mm_params, mc_params on the schematic; mm_params also on the magic C-coupled
# PEX netlist with mm_ok=1 set on the extracted devices), plus one dc_params run as a check of the committed
# (non-Monte-Carlo) schematic results. Design repository commit 91a7da8b, yaml and templates unchanged, CACE 2.11.
# Usage: run.sh [<work_dir>] [fetch|history|netcheck|sim|csv|analyze|results|all]   (default ./_work next to this script, all)
# Environment: JOBS = parallel ngspice runs per group (default 2); SIM_SCH / SIM_PEX = groups of the sim step.
# Needs: PDK_ROOT with ihp-sg13cmos5l, ngspice-47 with the IHP OSDI models, xschem, CACE 2.11, python3 with pyyaml and
# matplotlib, git with network access to github.com (blobless clones; only the needed paths are extracted).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOT=$(cd "$HERE/../../.." && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export JOBS=${JOBS:-2}
export PYTHONDONTWRITEBYTECODE=1
T=sg13cmos5l_IOPadSingle2Diff
URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
C=91a7da8b67ac56a26c605501146667a1fde28c32
SIM_SCH=${SIM_SCH-mm_params ac_mm_params mc_params dc_params}
SIM_PEX=${SIM_PEX-mm_params}
M=$WORK/design/macros/$T
DEPS="sg13cmos5l_IOPadDiff2Single en_ctrl_3v3 bias_sel_pd bias_gen_pd ls_up_1v2_3v3 hv_logic IOPad oa_core_pd bg_core_pd
 bias_tree_pd bias_tree_noab_pd bias_sel_noab_pd"     # the macros the S2D xschemrc puts on the library path
mkdir -p "$WORK"

fetch() {
  [ -d "$WORK/repo" ] || git clone -q --depth 1 --filter=blob:none --no-checkout "$URL" "$WORK/repo"
  git -C "$WORK/repo" fetch -q --depth 1 origin $C
  local P="scripts/cace macros/$T/schematic macros/$T/verification/cace macros/$T/verification/lvs macros/$T/netlist
   macros/$T/layout/klayout/$T.klay.gds" d
  for d in $DEPS; do P="$P macros/$d/schematic/xschem"; done
  rm -rf "$WORK/design" && mkdir -p "$WORK/design"
  git -C "$WORK/repo" archive $C $P | tar x -C "$WORK/design"
}

# Staleness: commit dates of the committed results vs the last change of the schematic (S2D and the macros it uses),
# from a blobless clone with full history (commits and trees only, about 2 MB).
history() {
  [ -d "$WORK/hist" ] || git clone -q --filter=blob:none --no-checkout "$URL" "$WORK/hist"
  local H="git -C $WORK/hist" R=macros/$T/verification/cace/results/$T f d
  {
    echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"
    echo "# SPDX-License-Identifier: Apache-2.0"
    echo "# last commit (at design commit ${C:0:8}) that changed each path: hash, committer date, subject"
    echo "## committed schematic results, per file"
    for f in mm_params.csv summary_mm_params.md ac_mm_params.csv summary_ac_mm_params.md mc_params.csv \
             summary_mc_params.md dc_params.csv summary_dc_params.md; do
      echo "$f: $($H log -1 --format='%h %ci %s' $C -- $R/$f)"
    done
    echo "## schematic, CACE file, templates, LVS netlist, layout, PEX netlist of the S2D pad"
    for f in schematic/xschem verification/cace/$T.yaml verification/cace/templates netlist/schematic/${T}_magic.spice \
             layout/klayout/$T.klay.gds netlist/pex; do
      echo "macros/$T/$f: $($H log -1 --format='%h %ci %s' $C -- macros/$T/$f)"
    done
    echo "## commits that changed macros/$T/schematic/xschem after the mismatch results (2026-10-26)"
    $H log --format='%h %ci %s' 6229797..$C -- macros/$T/schematic/xschem
    echo "## schematic folders of the macros on the S2D library path"
    for d in $DEPS; do echo "macros/$d: $($H log -1 --format='%h %ci %s' $C -- macros/$d/schematic/xschem)"; done
  } > "$HERE/staleness.txt"
  cat "$HERE/staleness.txt"
}

# Which netlist: CACE 2.11 regenerates the schematic netlist (xschem -n -s -r -x -q --tcl "set top_is_subckt 1" in the
# schematic folder, project xschemrc). Netlist it the same way and compare it, comments (** lines) dropped, with the
# taped-out cell's LVS netlist pads/<cell>/<cell>.spice (its 4-line provenance header dropped). Also: the pad GDS of
# this repository against the design's macro GDS (the layout the PEX netlist was extracted from), and the design's
# magic / netgen LVS report of that GDS against the LVS netlist.
netcheck() {
  mkdir -p "$WORK/netcheck"
  (cd "$M/schematic/xschem" && xschem -n -s -r -x -q --tcl "set top_is_subckt 1" -o "$WORK/netcheck" -N cace_sch.spice $T.sch > /dev/null 2>&1)
  tail -n +5 "$SLOT/pads/$T/$T.spice" > "$WORK/netcheck/pad_lvs.spice"
  local L=$M/verification/lvs/$T.magic.lvs/$T.lvs.out
  {
    echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"
    echo "# SPDX-License-Identifier: Apache-2.0"
    echo "# CACE schematic netlist (xschem, design commit ${C:0:8}) vs taped-out LVS netlist pads/$T/$T.spice"
    echo "sha256 pads/$T/$T.spice without its 4-line header: $(sha256sum < "$WORK/netcheck/pad_lvs.spice" | cut -d' ' -f1)"
    echo "sha256 design ${C:0:8}:macros/$T/netlist/schematic/${T}_magic.spice: $(sha256sum < "$M/netlist/schematic/${T}_magic.spice" | cut -d' ' -f1)"
    echo "lines (without ** comments): CACE $(grep -vc '^\*\*' "$WORK/netcheck/cace_sch.spice"), LVS $(grep -vc '^\*\*' "$WORK/netcheck/pad_lvs.spice")"
    echo "diff LVS -> CACE (** comment lines dropped):"
    diff <(grep -v '^\*\*' "$WORK/netcheck/pad_lvs.spice") <(grep -v '^\*\*' "$WORK/netcheck/cace_sch.spice") || true
    echo "Rsub in the schematic:"
    grep -A5 'name=Rsub$' "$M/schematic/xschem/$T.sch" | tr '\n' ' '; echo
    echo "mm_ok=1 instances in the CACE netlist: $(grep -c 'mm_ok=1' "$WORK/netcheck/cace_sch.spice"); MOSFET / rhigh / rppd lines without mm_ok=1: $(grep -E '^[Xx].* (sg13_hv_nmos|sg13_hv_pmos|sg13_lv_nmos|sg13_lv_pmos|rhigh|rppd|rsil)( |$)' "$WORK/netcheck/cace_sch.spice" | grep -vc 'mm_ok=1' || true)"
    echo "sha256 pads/$T/$T.gds: $(sha256sum < "$SLOT/pads/$T/$T.gds" | cut -d' ' -f1)"
    echo "sha256 design ${C:0:8}:macros/$T/layout/klayout/$T.klay.gds: $(sha256sum < "$M/layout/klayout/$T.klay.gds" | cut -d' ' -f1)"
    echo "design ${C:0:8}:macros/$T/verification/lvs/$T.magic.lvs/$T.lvs.out (magic extraction of that GDS vs the LVS netlist):"
    grep -E 'Number of devices|Number of nets|Netlists match|Final result|no matching pin' "$L" | sed 's/  */ /g'
    echo "  property errors other than mm_ok:"
    grep -v mm_ok "$L" | grep -E -B1 'delta=' | sed 's/^/  /'
    echo "PEX netlist ${C:0:8}:macros/$T/netlist/pex/${T}_magic_pex_2.spice: $(head -1 "$M/netlist/pex/${T}_magic_pex_2.spice")"
  } > "$HERE/netcheck.txt"
  cat "$HERE/netcheck.txt"
}

sim() {
  [ -z "$SIM_SCH" ] || "$HERE/cace_run.sh" "$WORK" "$WORK/out" schematic $SIM_SCH || echo "WARNING: a schematic group failed (see $WORK/out/log_*.txt)"
  [ -z "$SIM_PEX" ] || "$HERE/cace_run.sh" "$WORK" "$WORK/out" pex $SIM_PEX || echo "WARNING: a pex group failed (see $WORK/out/log_*_pex.txt)"
}

# result files of this folder: CSV with a 3-line comment header (SPDX, units), CACE summary with an SPDX comment
csv() {
  mkdir -p "$HERE/csv"
  local f b
  for f in "$WORK"/out/*.csv; do
    b=$(basename "$f")
    { echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "# SPDX-License-Identifier: Apache-2.0"
      echo "# IHP sg13cmos5l simulation, design ${C:0:8}, CACE 2.11; values as the testbench writes them (V, A, Hz, dB), whatever the [unit] label says"
      cat "$f"; } > "$HERE/csv/$b"
  done
  for f in "$WORK"/out/summary_*.md; do
    b=$(basename "$f")
    { echo "<!--"; echo "SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "SPDX-License-Identifier: Apache-2.0"
      echo "CACE 2.11 summary of this run (IHP sg13cmos5l simulation, design ${C:0:8})"; echo "-->"; cat "$f"; } > "$HERE/csv/$b"
  done
  [ ! -f "$WORK/out/pex_for_sim.log" ] || { echo "# SPDX-FileCopyrightText: 2026 Christoph Maier"; echo "# SPDX-License-Identifier: Apache-2.0"
    cat "$WORK/out/pex_for_sim.log"; } > "$HERE/csv/pex_for_sim.log"
}

# statistics (tables/stats.md, tables/stats.csv), comparison with the committed CACE summaries and dc_params.csv
# (tables/compare_committed.md), histograms (figures/*.png)
analyze() {
  python3 "$HERE/analyze.py" "$M/verification/cace/$T.yaml" "$M/verification/cace/results/$T" "$HERE/csv" "$HERE"
}

# results.md = results_head.md (hand-written text) + the generated tables
results() {
  { cat "$HERE/results_head.md"
    printf '\n## 3. Statistics per group, view and quantity (= tables/stats.md)\n\n'
    sed '1,/^-->$/d' "$HERE/tables/stats.md"
    printf '\n## 4. Comparison with the committed results (= tables/compare_committed.md)\n\n'
    sed '1,/^-->$/d' "$HERE/tables/compare_committed.md"; } > "$HERE/results.md"
}

case "$STEP" in
  all) fetch; history; netcheck; sim; csv; analyze; results ;;
  fetch|history|netcheck|sim|csv|analyze|results) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
