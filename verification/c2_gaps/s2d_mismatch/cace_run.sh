#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Run CACE parameter groups of sg13cmos5l_IOPadSingle2Diff (S2D pad, s7_an[0]) on its schematic or on the magic
# C-coupled PEX netlist (IHP sg13cmos5l simulation), design repository commit 91a7da8b, yaml and templates unchanged,
# CACE 2.11, ngspice-47 + OSDI. Scheme of ../d2s_schematic_rerun/cace_sch.sh (schematic) and of the design's
# macros/sg13cmos5l_IOPadSingle2Diff/Makefile sim-cace CACE_SOURCE=pex (pex), with one change for pex: the extracted
# netlist is prepared with pex_for_sim.py --mm-ok (mm_ok=1 on every MOSFET / rhigh / rppd instance, as xschem writes it
# on every such instance of the schematic), so that local mismatch is drawn for the extracted devices too; without
# it a mismatch group on the extraction is vacuous (the reason the Makefile leaves mm groups out for pex).
# Per group: <out>/<group>[_pex].csv (mm_collect.py: CACE 2.11 nests the iterations of a collated group one level
# deeper than cace_to_csv.py looks; for a group without iterations it gives the same rows), <out>/summary_<group>[_pex].md
# (CACE's summary.md), <out>/log_<group>[_pex].txt; the CACE run folder is kept as <work>/runs/<group>[_pex].
# Templates are restored from a pristine copy and their netlists deleted before every group.
# Usage: [JOBS=2] cace_run.sh <work_dir> <out_dir> <schematic|pex> <group> [<group> ...]
set -u
WORK=$(realpath "$1"); OUT=$(realpath -m "$2"); SRC=$3; shift 3
HERE=$(dirname "$(realpath "$0")")
JOBS=${JOBS:-2}
T=sg13cmos5l_IOPadSingle2Diff
M=$WORK/design/macros/$T
SCR=$WORK/design/scripts/cace
mkdir -p "$OUT" "$WORK/runs"
cd "$M/verification/cace" || exit 1
xschem -x -q -r --rcfile "$M/schematic/xschem/xschemrc" \
  --command "set fp [open .xschem_library_path_$SRC w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xschem_library_path_$SRC | grep '/macros/' | grep -v "^$M/" | paste -sd: -)
[ -n "$XSCHEM_USER_LIBRARY_PATH" ] || { echo "no macro library path"; exit 1; }
if [ "$SRC" = pex ]; then
  Y=_pex_$T.yaml; RUNS=_runs_pex; SUF=_pex
  sed -e 's|^  runs:.*|  runs:             cace/_runs_pex|' -e 's|^  documentation:.*|  documentation:    cace/_docs_pex|' \
      -e 's|^  netlist:.*|  netlist:          cace/netlist_pex\n  layout:           cace/layout_pex|' $T.yaml > $Y
  rm -rf layout_pex netlist_pex && mkdir -p layout_pex netlist_pex/pex
  cp "$M/layout/klayout/$T.klay.gds" layout_pex/$T.gds
  sleep 1   # the prepared netlist must be newer than the layout: CACE then skips the extraction ("Up to date")
  python3 "$SCR/pex_for_sim.py" "$M/netlist/pex/${T}_magic_pex_2.spice" netlist_pex/pex/$T.spice --mm-ok --tie iovss 1e12 \
    > "$OUT/pex_for_sim.log" 2>&1 || exit 1
  sed -i "s/\b${T}_pex\b/$T/g" netlist_pex/pex/$T.spice
  cp netlist_pex/pex/$T.spice "$WORK/${T}_pex_mm.spice"
else
  Y=_sch_$T.yaml; RUNS=_runs_sch; SUF=
  sed -e 's|^  runs:.*|  runs:             cace/_runs_sch|' -e 's|^  documentation:.*|  documentation:    cace/_docs_sch|' \
      $T.yaml > $Y
fi
[ -d _templates_orig ] || cp -r templates _templates_orig
status=0
for g in "$@"; do
  rm -rf $RUNS/RUN_* templates
  cp -r _templates_orig templates           # fresh mtimes: CACE renetlists every template
  rm -f templates/*.spice
  echo "=== $g$SUF start $(date -u +%FT%H:%M:%SZ) jobs=$JOBS"
  cace $Y -s $SRC -p "$g" -j "$JOBS" --no-progress-bar > "$OUT/log_$g$SUF.txt" 2>&1 || status=1
  cp $RUNS/RUN_*/summary.md "$OUT/summary_$g$SUF.md" 2>/dev/null || status=1
  python3 "$HERE/mm_collect.py" $T.yaml "$g" $RUNS/RUN_* "$OUT/$g$SUF.csv" templates || status=1
  [ "$SRC" = schematic ] && cp netlist/schematic/$T.spice "$OUT/netlist_$g.spice" 2>/dev/null
  rm -rf "$WORK/runs/$g$SUF"; mv $RUNS/RUN_* "$WORK/runs/$g$SUF" 2>/dev/null
  echo "=== $g$SUF done $(date -u +%FT%H:%M:%SZ) rows=$(($(grep -vc '^#' "$OUT/$g$SUF.csv" 2>/dev/null || echo 1)-1))"
done
rm -rf templates && cp -r _templates_orig templates
exit $status
