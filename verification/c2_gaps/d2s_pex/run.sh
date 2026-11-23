#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# IHP sg13cmos5l post-layout (magic PEX) simulation of the taped-out pad sg13cmos5l_IOPadDiff2Single.
# Reproduces everything in this folder from a checkout of this repository plus the design repository commit
# (fetched here). Usage: run.sh [<work_dir>] [<group> ...]
#   work_dir  scratch folder (default: ./_work next to this script); results go to <work_dir>/out/
#   groups    CACE parameter groups (default: the nine below)
# Needs: PDK_ROOT with ihp-sg13cmos5l, magic, netgen, ngspice (IHP OSDI models), xschem, cace 2.11, sak-pex.sh,
# sak-pin-reorder.py (IIC-OSIC-TOOLS), python3 with pyyaml and matplotlib, git with network access to github.com.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOT=$(cd "$HERE/../../.." && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}"); shift || true
GROUPS_=${*:-dc_params ac_params ac_load_params tran_params noise_params drive_params enable_params pd_params thd_params}
JOBS=${JOBS:-2}
T=sg13cmos5l_IOPadDiff2Single
URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
DCOMMIT=91a7da8b67ac56a26c605501146667a1fde28c32
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export PDKPATH=$PDK_ROOT/$PDK
mkdir -p "$WORK/out"

# 1. design repository: the D2S macro (schematic, CACE yaml / templates / committed schematic results), the
#    schematic folders of the macros its xschemrc lists (the templates place en_ctrl_3v3 and bias_gen_pd next to the
#    cell), scripts/cace and scripts/pex_add_port.py. Shallow, blobless: only these paths are downloaded.
if [ ! -d "$WORK/repo" ]; then
  git clone -q --depth 1 --filter=blob:none --no-checkout "$URL" "$WORK/repo"
fi
git -C "$WORK/repo" fetch -q --depth 1 origin $DCOMMIT
P="macros/$T/schematic macros/$T/verification/cace scripts/cace scripts/pex_add_port.py"
for d in en_ctrl_3v3 bias_sel_pd bias_gen_pd ls_up_1v2_3v3 hv_logic IOPad bias_in_pd bias_out_pd bias_oa_pd \
         bias_bg_pd oa_core_pd bg_core_pd bias_tree_pd; do
  P="$P macros/$d/schematic/xschem"
done
rm -rf "$WORK/design" && mkdir -p "$WORK/design"
git -C "$WORK/repo" archive $DCOMMIT $P | tar x -C "$WORK/design"
M=$WORK/design/macros/$T

# 2. magic C-coupled extraction (EXT_MODE=2) of the taped-out cell, as the S2D Makefile target magic-pex
#    (design repository commit 9052bd35928c6d40344e8e686c9abbe736bfadb9): sak-pex.sh -m 2, then the substrate-joined
#    vss port (pex_add_port.py vss iovss 1 Ohm = the sheet's Rsub) and the port order of the symbol.
mkdir -p "$WORK/pex" "$M/netlist/pex"
cp "$SLOT/pads/$T/$T.gds" "$WORK/pex/"
sak-pex.sh -d -m 2 -n ${T}_pex -w "$WORK/pex" "$WORK/pex/$T.gds" > "$WORK/pex/sak-pex.log" 2>&1
N=$M/netlist/pex/${T}_magic_pex_2.spice
cp "$WORK/pex/$T.pex.spice" "$N"
python3 "$WORK/design/scripts/pex_add_port.py" "$N" ${T}_pex vss iovss 1
sed 's/type=subcircuit/type=primitive/' "$M/schematic/xschem/$T.sym" > "$M/schematic/xschem/${T}_pex.sym"
sak-pin-reorder.py "$M/schematic/xschem/${T}_pex.sym" "$N" --format spice > "$WORK/pex/pin-reorder.log"
cp "$N" "$WORK/out/"

# 3. device check: netgen LVS of the extraction (capacitors dropped, vss port without the 1 Ohm tie) against the
#    committed schematic LVS netlist pads/<cell>/<cell>.spice (its 4-line provenance header dropped).
mkdir -p "$WORK/lvs"
awk 'BEGIN{s=0} /^[Cc]/{s=1;next} /^\+/{if(s)next} {s=0;print}' "$WORK/pex/$T.pex.spice" > "$WORK/lvs/lay.spice"
python3 "$WORK/design/scripts/pex_add_port.py" "$WORK/lvs/lay.spice" ${T}_pex vss iovss 1
sed -i -e '/^Rport_vss/d' -e "s/\b${T}_pex\b/$T/" "$WORK/lvs/lay.spice"
grep -v -e '^\* PROVENANCE' -e '^\* commit' -e '^\* sha256' "$SLOT/pads/$T/$T.spice" > "$WORK/lvs/sch.spice"
(cd "$WORK/lvs" && netgen -batch lvs "lay.spice $T" "sch.spice $T" "$PDKPATH/libs.tech/netgen/${PDK}_setup.tcl" lvs.out > netgen.log 2>&1) || true
sed -n '/^Subcircuit summary:/,/^Number of nets/p' "$WORK/lvs/lvs.out" | tail -12 > "$WORK/out/lvs_summary.txt"
grep -E 'Final result|Property errors|match' "$WORK/lvs/lvs.out" | tail -4 >> "$WORK/out/lvs_summary.txt"
echo "property errors other than mm_ok: $(grep -A1 -E '^(sg13|rhigh|rppd|d.*antenna)[a-z_0-9]*:' "$WORK/lvs/lvs.out" | grep '^Property' | grep -vc mm_ok || true)" >> "$WORK/out/lvs_summary.txt"

# 4. CACE on the PEX view (see cace_pex.sh), then the comparison with the committed schematic CSVs
"$HERE/cace_pex.sh" "$M" "$N" "$WORK/pex/$T.gds" "$WORK/out" "$JOBS" $GROUPS_ || echo "WARNING: some CACE group failed or missed a limit"
R=$M/verification/cace/results/$T
python3 "$HERE/compare.py" "$R" "$WORK/out" $GROUPS_ > "$WORK/out/compare_table.md"
python3 "$HERE/plots.py" "$R" "$WORK/out" "$WORK/out"
echo "done: $WORK/out"
