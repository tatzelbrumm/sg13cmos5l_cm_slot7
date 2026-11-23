#!/bin/bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
# Run CACE groups of pad_ref_rb on the schematic or on the prepared PEX netlist, in a copy of the design repository's
# macro tree (<tree>), the same way as macros/sg13cmos5l_IOPadSingle2Diff/Makefile sim-cace CACE_SOURCE=pex does at
# design commit 9052bd35: a copy of the yaml with its own runs/netlist/docs folders, the prepared netlist placed at
# cace/netlist_pex/pex/pad_ref_rb.spice (newer than the layout, so CACE takes it as up to date).
# Usage: run_cace.sh <tree> <schematic|pex> <results_dir> <keep_runs_dir|-> <group> [<group> ...]
#   pex expects <tree>/pex/pad_ref_rb_sim.spice (pex_for_sim.py output) and <tree>/pex/pad_ref_rb.gds.
#   keep_runs_dir: if not '-', the CACE run folder of each group is moved there (for per-run data, e.g. mm_params).
set -u
TREE=$(realpath "$1"); SRC=$2; RES=$(realpath -m "$3"); KEEP=$4; shift 4
TOP=pad_ref_rb
MAC=$TREE/macros/$TOP
SCR=$TREE/scripts/cace
JOBS=${CACE_JOBS:-1}
cd $MAC/verification/cace || exit 1
mkdir -p "$RES"
xschem -x -q -r --rcfile $MAC/schematic/xschem/xschemrc \
  --command "set fp [open .xlp_$SRC w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xlp_$SRC | grep '/macros/' | grep -v "^$MAC/" | paste -sd: -)
echo "XSCHEM_USER_LIBRARY_PATH=$XSCHEM_USER_LIBRARY_PATH"
if [ "$SRC" = pex ]; then
  Y=_${TOP}_pex.yaml; RUNS=_runs_pex; NET=netlist_pex; DOCS=_docs_pex
  sed -e "s|^  runs:.*|  runs:             cace/$RUNS|" -e "s|^  documentation:.*|  documentation:    cace/$DOCS|" \
      -e "s|^  netlist:.*|  netlist:          cace/$NET\n  layout:           cace/layout_pex|" $TOP.yaml > $Y
  mkdir -p layout_pex $NET/pex
  cp $TREE/pex/$TOP.gds layout_pex/$TOP.gds
  sleep 1
  sed 's/\b'$TOP'_pex\b/'$TOP'/g' $TREE/pex/${TOP}_sim.spice > $NET/pex/$TOP.spice
else
  Y=$TOP.yaml; RUNS=_runs; NET=netlist; DOCS=_docs
fi
status=0
for g in "$@"; do
  rm -rf $RUNS/RUN_*
  cace $Y -s $SRC -p $g -j $JOBS --no-progress-bar > "$RES/cace_$g.log" 2>&1 || status=1
  cp $RUNS/RUN_*/summary.md "$RES/summary_$g.md"
  python3 $SCR/cace_to_csv.py $TOP.yaml $g $RUNS/RUN_* "$RES/$g.csv" || status=1
  if [ "$KEEP" != - ]; then mkdir -p "$KEEP"; rm -rf "$KEEP/$g"; mv $RUNS/RUN_* "$KEEP/$g"; fi
  rm -rf $RUNS/RUN_*
done
rm -rf $RUNS $DOCS $NET .xlp_$SRC
[ "$SRC" = pex ] && rm -rf $Y layout_pex
exit $status
