#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Run AC / transient / noise curve groups (mkgroups.py) of one pad with CACE 2.11 on its schematic or magic PEX
# netlist, then collect the curves (collect.py). IHP sg13cmos5l simulation. Same netlist preparation as
# ../dc_curves/cace_dc.sh:
#   pex netlists: S2D = the design repository's netlist/pex/<cell>_magic_pex_2.spice (commit 91a7da8b), D2S =
#   ../d2s_pex/<cell>_magic_pex_2.spice (this repository); both prepared as the S2D Makefile's sim-cace
#   CACE_SOURCE=pex (pex_for_sim.py --tie iovss 1e12, subckt renamed to the cell name, newer than the layout).
#   D2S PEX: ngspice option rshunt=1e12 (as ../d2s_pex pass 2; the PEX operating point does not converge without
#   it). D2S schematic: without it, as the committed CACE schematic results (these analyses converge without it);
#   RSHUNT=1 adds it to the schematic too (check of its effect; results to <work_dir>/out/schematic_rshunt/).
# Usage: [JOBS=3] [RSHUNT=1] cace_at.sh <work_dir> <cell> <schematic|pex> <group> [<group> ...]
set -u
WORK=$(realpath "$1"); T=$2; SRC=$3; shift 3
HERE=$(dirname "$(realpath "$0")"); SLOT=$(cd "$HERE/../../.." && pwd)
JOBS=${JOBS:-3}
M=$WORK/design/macros/$T
SCR=$WORK/design/scripts/cace
OUT=$WORK/out/$SRC${RSHUNT:+_rshunt}
mkdir -p "$OUT"
cd "$M/verification/cace" || exit 1
python3 "$HERE/mkgroups.py" "$M" "$T" "$SRC" > /dev/null || exit 1
xschem -x -q -r --rcfile "$M/schematic/xschem/xschemrc" \
  --command "set fp [open .xschem_library_path_atg w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xschem_library_path_atg | grep '/macros/' | grep -v "^$M/" | paste -sd: -)
if [ "$SRC" = pex ]; then
  Y=_atg_${T}_pex.yaml; RUNS=_runs_atg_pex
  if [ "$T" = sg13cmos5l_IOPadSingle2Diff ]; then PEXNET=$M/netlist/pex/${T}_magic_pex_2.spice
  else PEXNET=$SLOT/verification/c2_gaps/d2s_pex/${T}_magic_pex_2.spice; fi
  mkdir -p layout_pex netlist_pex/pex
  ln -sf "$SLOT/pads/$T/$T.gds" layout_pex/$T.gds
  python3 "$SCR/pex_for_sim.py" "$PEXNET" netlist_pex/pex/$T.spice --tie iovss 1e12
  sed -i "s/\b${T}_pex\b/$T/g" netlist_pex/pex/$T.spice
  touch netlist_pex/pex/$T.spice
else
  Y=_atg_$T.yaml; RUNS=_runs_atg
fi
if [ "$T" = sg13cmos5l_IOPadDiff2Single ] && { [ "$SRC" = pex ] || [ -n "${RSHUNT:-}" ]; }; then
  for k in ac tran noise enable; do
    sed -i 's/^\.option warn=1$/.option warn=1\n.option rshunt=1e12/' templates/${T}_tb_at_$k.sch
  done
fi
status=0
for g in "$@"; do
  rm -rf $RUNS/RUN_*
  echo "=== $T $SRC $g start $(date -u +%H:%M:%S)"
  cace $Y -s $SRC -p "$g" -j "$JOBS" --no-progress-bar > "$OUT/log_$g.txt" 2>&1 || status=1
  python3 "$HERE/collect.py" $RUNS/RUN_* "$g" "$OUT/$g" || status=1
  echo "=== $T $SRC $g done $(date -u +%H:%M:%S)"
done
exit $status
