#!/bin/bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
# Netgen LVS of a magic C-coupled extraction (its capacitors removed) against the design repository's source netlists,
# to show that the extracted netlist used for simulation has the devices (W, L, ...) and connectivity of the schematic.
# mm_ok=1 (a simulation-only instance flag of the schematic) is removed before the comparison.
# Usage: lvs_check.sh <tree> <work_dir> <cell> <extracted.spice> <log>
set -euo pipefail
TREE=$1; W=$2; C=$3; X=$4; LOG=$5
mkdir -p "$W"
M=$TREE/macros
case $C in
  pad_ref_rb)   SRC="$M/vcm_rb/netlist/source/vcm_rb.spice $M/vref_s2d_rb/netlist/source/vref_s2d_rb.spice $M/pad_ref_rb/netlist/source/pad_ref_rb.spice" ;;
  bias_dist_pd) SRC="$M/hv_logic/netlist/source/hv_logic.spice $M/bias_dist_pd/netlist/source/bias_dist_pd.spice" ;;
esac
cat $SRC | grep -v -i '^\.include' | sed 's/ mm_ok=1//' > "$W/${C}_sch.spice"
sed "s/\b${C}_pex\b/${C}/" "$X" | grep -v '^C' > "$W/${C}_lay.spice"
(cd "$W" && netgen -batch lvs "${C}_lay.spice $C" "${C}_sch.spice $C" "$PDK_ROOT/$PDK/libs.tech/netgen/$PDK""_setup.tcl" "${C}_lvs.out" > "${C}_lvs.log" 2>&1)
{ echo "$C: magic C-coupled extraction (capacitors removed) vs source netlist"
  grep -E 'Number of devices|Number of nets|Cell pin lists|Netlists match|Property errors|Final result' "$W/${C}_lvs.out" | tail -6; } >> "$LOG"
