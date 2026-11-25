#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Run DC-curve groups (mkgroups.py) of one pad with CACE 2.11 on its schematic or magic PEX netlist, then collect the
# sweeps (collect.py). IHP sg13cmos5l simulation.
# Usage: [JOBS=3] [NORSHUNT=1] cace_dc.sh <work_dir> <cell> <schematic|pex> <group> [<group> ...]
#   NORSHUNT=1: D2S without the rshunt option (check only; results to <work_dir>/out/<view>_norshunt/)
#   pex netlists: S2D = the design repository's netlist/pex/<cell>_magic_pex_2.spice (commit 91a7da8b, made by the
#   S2D Makefile's magic-pex EXT_MODE=2 from the taped-out GDS); D2S = ../d2s_pex/<cell>_magic_pex_2.spice (this
#   repository, made by d2s_pex/run.sh from pads/<cell>/<cell>.gds). Both prepared as the S2D Makefile's
#   sim-cace CACE_SOURCE=pex: pex_for_sim.py --tie iovss 1e12, subckt renamed to the cell name, the prepared netlist
#   newer than the layout (CACE does not extract again). D2S, both views: ngspice option rshunt=1e12 (see below).
set -u
WORK=$(realpath "$1"); T=$2; SRC=$3; shift 3
HERE=$(dirname "$(realpath "$0")"); SLOT=$(cd "$HERE/../../.." && pwd)
JOBS=${JOBS:-3}
M=$WORK/design/macros/$T
SCR=$WORK/design/scripts/cace
OUT=$WORK/out/$SRC${NORSHUNT:+_norshunt}
mkdir -p "$OUT"
cd "$M/verification/cace" || exit 1
python3 "$HERE/mkgroups.py" "$M" "$T" "$SRC" > /dev/null || exit 1
xschem -x -q -r --rcfile "$M/schematic/xschem/xschemrc" \
  --command "set fp [open .xschem_library_path_dcg w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xschem_library_path_dcg | grep '/macros/' | grep -v "^$M/" | paste -sd: -)
if [ "$SRC" = pex ]; then
  Y=_dcg_${T}_pex.yaml; RUNS=_runs_dcg_pex
  if [ "$T" = sg13cmos5l_IOPadSingle2Diff ]; then PEXNET=$M/netlist/pex/${T}_magic_pex_2.spice
  else PEXNET=$SLOT/verification/c2_gaps/d2s_pex/${T}_magic_pex_2.spice; fi
  mkdir -p layout_pex netlist_pex/pex
  ln -sf "$SLOT/pads/$T/$T.gds" layout_pex/$T.gds
  python3 "$SCR/pex_for_sim.py" "$PEXNET" netlist_pex/pex/$T.spice --tie iovss 1e12
  sed -i "s/\b${T}_pex\b/$T/g" netlist_pex/pex/$T.spice
  touch netlist_pex/pex/$T.spice
else
  Y=_dcg_$T.yaml; RUNS=_runs_dcg
fi
# D2S, both views: ngspice option rshunt=1e12 (1 TOhm from every node to ground). PEX: as d2s_pex pass 2 (the op
# does not converge without it). Schematic: without it the sweep at tt / -40 C / 3.3 V crawled (one 0 ... 3.3 V branch
# not finished after 13 min, with gmin stepping at every restart, singular nodes in the disabled bandgap core of
# bias_gen_pd); with it the same branch takes 3 s. Its effect on the DC quantities: README.md / tables/crosscheck.md.
if [ "$T" = sg13cmos5l_IOPadDiff2Single ] && [ -z "${NORSHUNT:-}" ]; then
  sed -i 's/^\.option warn=1$/.option warn=1\n.option rshunt=1e12/' templates/${T}_tb_dcsweep.sch
fi
status=0
for g in "$@"; do
  rm -rf $RUNS/RUN_*
  echo "=== $T $SRC $g start $(date -u +%H:%M:%S)"
  cace $Y -s $SRC -p "$g" -j "$JOBS" --no-progress-bar > "$OUT/log_$g.txt" 2>&1 || status=1
  python3 "$HERE/collect.py" $RUNS/RUN_* "$g" "$OUT/$g.csv.gz" || status=1
  echo "=== $T $SRC $g done $(date -u +%H:%M:%S)"
done
exit $status
