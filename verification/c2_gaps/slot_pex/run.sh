#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Whole-slot magic PEX of the taped-out slot 7 (final/gds/slot_7.gds) and the two custom pads, netgen LVS, and the
# slot round-trip simulations with the extracted netlists (IHP sg13cmos5l; ngspice-47 with the IHP OSDI models,
# magic 8.3.685, netgen 1.5.324). Reproduces csv/, plots/ and tables.md of this folder.
# Usage: run.sh [<work_dir>] [fetch|extract|prep|stats|sim|eval|all]   (default ./_work, all)
#   fetch    design repository paths (../dc_curves/fetch.sh: commits 91a7da8b and 9052bd35, shallow, blobless)
#   extract  extract.sh: magic extraction (sak-pex.sh as before, C-coupled with substrate capacitance, full-RC) of
#            slot_7 and both pads, netgen LVS of each
#   prep     prep.py: simulation netlists (slot wrapper with the source port order, floating nodes tied)
#   stats    pexstats.py: parasitic totals -> csv/pex_totals.csv, csv/pex_nets.csv; rnode evidence -> csv/rnode_caps_*.csv
#   sim      runjobs.sh: the sim.py jobs of jobs.txt, one ngspice process at a time (about 4 h on 4 shared CPUs)
#   eval     evaluate.py -> csv/*_summary.csv, csv/compare.csv, tables.md, plots/*.png
# Needs: PDK_ROOT with ihp-sg13cmos5l, magic, netgen, ngspice with the OSDI models, sak-pex.sh (IIC-OSIC-TOOLS),
# python3 with numpy / matplotlib, git with network access to github.com.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$WORK" "$HERE/csv" "$HERE/plots"

fetch() { "$HERE/../dc_curves/fetch.sh" "$WORK"; }
extract() { "$HERE/extract.sh" "$WORK" | tee "$WORK/extract.log"; }
prep() { python3 -I "$HERE/prep.py" "$WORK"; }
stats() {
  python3 -I "$HERE/pexstats.py" "$WORK" "$HERE"
  for c in slot_7 sg13cmos5l_IOPadSingle2Diff sg13cmos5l_IOPadDiff2Single; do
    cp "$WORK/x_$c/rc/rnode_caps.csv" "$HERE/csv/rnode_caps_$c.csv"
  done
  # netgen summaries (subcircuit summary, result, pin mismatches) of every extraction -> lvs_summary.txt
  { printf '# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
    echo "# netgen 1.5.324 LVS of the magic extractions (extract.sh; lvs_collapse.py: C dropped, parasitic R shorted)"
    for c in slot_7 sg13cmos5l_IOPadSingle2Diff sg13cmos5l_IOPadDiff2Single; do
      for v in c rc; do
        echo; echo "== $c, extraction $v"
        sed -n '/^Subcircuit summary:/,/^Number of nets/p' "$WORK/x_$c/lvs_$v/lvs.out" | tail -12
        grep -E 'Netlists match|match uniquely|do not match|Mismatch|no matching pin|Final result' "$WORK/x_$c/lvs_$v/lvs.out" | sort -u
        echo "property errors: $(grep -c '^Property' "$WORK/x_$c/lvs_$v/lvs.out" || true)"
      done
    done; } > "$HERE/lvs_summary.txt"
}
sim() { "$HERE/runjobs.sh" "$WORK" "$HERE/jobs.txt" | tee -a "$WORK/batch.log"; }
evaluate() { python3 -I "$HERE/evaluate.py" "$WORK" "$HERE"; }

case "$STEP" in
  all) fetch; extract; prep; stats; sim; evaluate ;;
  fetch|extract|prep|stats|sim) $STEP ;;
  eval) evaluate ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
