#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Run CACE parameter groups of sg13cmos5l_IOPadDiff2Single on its schematic (IHP sg13cmos5l schematic simulation),
# with the design repository's yaml and templates unchanged (commit 91a7da8b), CACE 2.11, ngspice-47 + OSDI.
# CACE regenerates the schematic netlist from macros/<cell>/schematic/xschem/<cell>.sch on every call.
# Per group: <out>/<group>.csv (design repository's cace_to_csv.py; mm_params: mm_collect.py, because CACE 2.11
# nests the iterations one level deeper), <out>/summary_<group>.md (CACE's summary.md), <out>/log_<group>.txt;
# the CACE run folder of each group is kept as <work>/runs/<group> (per-run data).
# RSHUNT=<ohm> (environment): ngspice .option rshunt=<ohm> added to every template that sets no rshunt (solver aid;
# only used for a group that does not converge without it). Templates are restored from a pristine copy before
# every group, and their netlists deleted, so an aid never carries over to the next group.
# Usage: [JOBS=3] [RSHUNT=1e12] cace_sch.sh <work_dir> <out_dir> <group> [<group> ...]
set -u
WORK=$(realpath "$1"); OUT=$(realpath -m "$2"); shift 2
HERE=$(dirname "$(realpath "$0")")
JOBS=${JOBS:-3}
T=sg13cmos5l_IOPadDiff2Single
M=$WORK/design/macros/$T
SCR=$WORK/design/scripts/cace
mkdir -p "$OUT" "$WORK/runs"
cd "$M/verification/cace" || exit 1
xschem -x -q -r --rcfile "$M/schematic/xschem/xschemrc" \
  --command "set fp [open .xschem_library_path_sch w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xschem_library_path_sch | grep '/macros/' | grep -v "^$M/" | paste -sd: -)
sed -e 's|^  runs:.*|  runs:             cace/_runs_sch|' -e 's|^  documentation:.*|  documentation:    cace/_docs_sch|' \
    $T.yaml > _sch_$T.yaml
[ -d _templates_orig ] || cp -r templates _templates_orig
status=0
for g in "$@"; do
  rm -rf _runs_sch/RUN_* templates
  cp -r _templates_orig templates           # fresh mtimes: CACE renetlists every template
  rm -f templates/*.spice
  aid=none
  if [ -n "${RSHUNT:-}" ]; then
    for t in templates/*.sch; do
      grep -q 'rshunt' "$t" || sed -i "s/^\.option warn=1\$/.option warn=1\n.option rshunt=$RSHUNT/" "$t"
    done
    aid="rshunt=$RSHUNT"
  fi
  echo "=== $g start $(date -u +%FT%H:%M:%SZ) aid=$aid"
  cace _sch_$T.yaml -s schematic -p "$g" -j "$JOBS" --no-progress-bar > "$OUT/log_$g.txt" 2>&1 || status=1
  cp _runs_sch/RUN_*/summary.md "$OUT/summary_$g.md" 2>/dev/null || status=1
  if [ "$g" = mm_params ]; then
    python3 "$HERE/mm_collect.py" $T.yaml "$g" _runs_sch/RUN_* "$OUT/$g.csv" || status=1
  else
    python3 "$SCR/cace_to_csv.py" $T.yaml "$g" _runs_sch/RUN_* "$OUT/$g.csv" || status=1
  fi
  echo "$aid" > "$OUT/aid_$g.txt"
  cp netlist/schematic/$T.spice "$OUT/netlist_$g.spice" 2>/dev/null
  rm -rf "$WORK/runs/$g"; mv _runs_sch/RUN_* "$WORK/runs/$g" 2>/dev/null
  echo "=== $g done $(date -u +%FT%H:%M:%SZ) rows=$(($(wc -l < "$OUT/$g.csv" 2>/dev/null || echo 1)-1))"
done
rm -rf templates && cp -r _templates_orig templates
exit $status
