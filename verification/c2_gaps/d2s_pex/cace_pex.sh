#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Run CACE parameter groups of sg13cmos5l_IOPadDiff2Single on the magic C-coupled PEX netlist, the same way as
# macros/sg13cmos5l_IOPadSingle2Diff/Makefile target sim-cace CACE_SOURCE=pex (design repository commit
# 9052bd35928c6d40344e8e686c9abbe736bfadb9): copy of the yaml with own runs / netlist / docs folders and a layout path,
# the prepared netlist (pex_for_sim.py --tie iovss 1e12, subckt renamed to the cell name) newer than the layout, so
# that CACE takes it as up to date and does not extract again.
# Usage: cace_pex.sh <macro_dir> <pex_netlist> <layout.gds> <out_dir> <jobs> <group> [<group> ...]
set -u
M=$(realpath "$1"); HERE=$(dirname "$(realpath "$0")"); PEXNET=$(realpath "$2"); GDS=$(realpath "$3"); OUT=$(realpath -m "$4"); JOBS=$5; shift 5
T=sg13cmos5l_IOPadDiff2Single
SCR=$M/../../scripts/cace
mkdir -p "$OUT"
cd "$M/verification/cace" || exit 1
xschem -x -q -r --rcfile "$M/schematic/xschem/xschemrc" \
  --command "set fp [open .xschem_library_path_pex w]; puts \$fp \$XSCHEM_LIBRARY_PATH; close \$fp" > /dev/null 2>&1
export XSCHEM_USER_LIBRARY_PATH=$(tr ':' '\n' < .xschem_library_path_pex | grep '/macros/' | grep -v "^$M/" | paste -sd: -)
echo "XSCHEM_USER_LIBRARY_PATH=$XSCHEM_USER_LIBRARY_PATH"
sed -e 's|^  runs:.*|  runs:             cace/_runs_pex|' -e 's|^  documentation:.*|  documentation:    cace/_docs_pex|' \
    -e 's|^  netlist:.*|  netlist:          cace/netlist_pex\n  layout:           cace/layout_pex|' $T.yaml > _${T}_pex.yaml
mkdir -p layout_pex netlist_pex/pex
ln -sf "$GDS" layout_pex/$T.gds
python3 "$SCR/pex_for_sim.py" "$PEXNET" netlist_pex/pex/$T.spice --tie iovss 1e12
sed -i "s/\b${T}_pex\b/$T/g" netlist_pex/pex/$T.spice
python3 "$HERE/pex_sense.py" netlist_pex/pex/$T.spice
# the tb_dc template reads the output-device currents by schematic instance name: read the 0 V senses instead
sed -i -e 's/@n\.x1\.xfp\.xop\.nsg13_hv_pmos\[ids\]/i(v.x1.vop_sense)/g' \
       -e 's/@n\.x1\.xfn\.xon\.nsg13_hv_nmos\[ids\]/i(v.x1.von_sense)/g' templates/${T}_tb_dc.sch
touch netlist_pex/pex/$T.spice
status=0
for g in "$@"; do
  rm -rf _runs_pex/RUN_*
  echo "=== $g start $(date -u +%H:%M:%S)"
  cace _${T}_pex.yaml -s pex -p "$g" -j "$JOBS" --no-progress-bar > "$OUT/log_$g.txt" 2>&1 || status=1
  cp _runs_pex/RUN_*/summary.md "$OUT/summary_$g.md" 2>/dev/null
  for p in _runs_pex/RUN_*/parameters/$g/*.png; do [ -f "$p" ] && cp "$p" "$OUT/"; done
  python3 "$SCR/cace_to_csv.py" $T.yaml "$g" _runs_pex/RUN_* "$OUT/$g.csv" || status=1
  echo "=== $g done $(date -u +%H:%M:%S) rows=$(($(wc -l < "$OUT/$g.csv" 2>/dev/null || echo 1)-1))"
done
exit $status
