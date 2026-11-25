#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Fetch the design-repository paths the DC-curve runs need (shallow, blobless; only these paths are downloaded).
# Usage: fetch.sh <work_dir>   -> <work_dir>/design (commit 91a7da8b...: both pad macros, their CACE yaml / templates /
# committed results, schematics of the macros the templates place next to the pads, scripts/cace, the S2D PEX netlist)
# and <work_dir>/tier1 (commit 9052bd35...: docs/slot7_hookup/tier1 and the netlists the slot decks include).
set -euo pipefail
WORK=$(realpath -m "$1")
URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
C91=91a7da8b67ac56a26c605501146667a1fde28c32
C90=9052bd35928c6d40344e8e686c9abbe736bfadb9
mkdir -p "$WORK"
if [ ! -d "$WORK/repo" ]; then
  git clone -q --depth 1 --filter=blob:none --no-checkout "$URL" "$WORK/repo"
fi
git -C "$WORK/repo" fetch -q --depth 1 origin $C91
P="scripts/cace scripts/pex_add_port.py"
for t in sg13cmos5l_IOPadSingle2Diff sg13cmos5l_IOPadDiff2Single; do
  P="$P macros/$t/schematic macros/$t/verification/cace macros/$t/netlist"
done
for d in en_ctrl_3v3 bias_sel_pd bias_gen_pd ls_up_1v2_3v3 hv_logic IOPad oa_core_pd bg_core_pd bias_tree_pd \
         bias_tree_noab_pd bias_sel_noab_pd bias_in_pd bias_out_pd bias_oa_pd bias_bg_pd; do
  P="$P macros/$d/schematic/xschem"
done
rm -rf "$WORK/design" && mkdir -p "$WORK/design"
git -C "$WORK/repo" archive $C91 $P | tar x -C "$WORK/design"
git -C "$WORK/repo" fetch -q --depth 1 origin $C90
rm -rf "$WORK/tier1" && mkdir -p "$WORK/tier1"
git -C "$WORK/repo" archive $C90 docs/slot7_hookup/tier1 macros/slot_7/netlist macros/pad_ref_rb/netlist \
  macros/bias_dist_pd/netlist macros/bg_core_pd/netlist macros/en_ctrl_3v3/netlist macros/hv_logic/netlist \
  macros/en_ctrl_3v3/testbenches/spice/run_starve.py macros/sg13cmos5l_IOPadSingle2Diff/netlist \
  macros/sg13cmos5l_IOPadDiff2Single/netlist | tar x -C "$WORK/tier1"
echo "fetched: $WORK/design ($C91), $WORK/tier1 ($C90)"
