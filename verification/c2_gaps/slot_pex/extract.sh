#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Magic parasitic extraction of the whole taped-out slot (final/gds/slot_7.gds, top cell slot_7) and of the two custom
# pad cells (pads/<cell>/<cell>.gds), and netgen LVS of each extraction (IHP sg13cmos5l; magic 8.3.685, netgen 1.5.324).
# Usage: extract.sh <work_dir>
# Per cell, in <work_dir>/<cell dir>/:
#   sak/        sak-pex.sh -m 2 exactly as the earlier pad PEX (../d2s_pex): C-coupled, flattened, 'ext2spice lvs'
#               -> <cell>.pex.spice. This output has NO node-to-substrate capacitance (see pexfix.py, README.md).
#   c/          the same magic commands (gds read, flatten, extract all, ext2spice lvs, cthresh 0.01 fF), written twice:
#               hierarchical (as sak-pex.sh, for the port order) and flat ('ext2spice hierarchy off', which writes the
#               substrate capacitances) -> pexfix.py c -> <cell>.pex.spice
#   rc/         full-RC: the commands of sak-pex.sh -m 3 with extresist threshold 0, minres 100 mOhm, mindelay 0
#               (resistance of every net magic finds resistance for, no delay gating) -> magic's netlist rc_magic.spice
#               -> pexfix.py rc (capacitors from c/, see there) -> <cell>.pex.spice
#   lvs_c, lvs_rc   lvs_collapse.py (capacitors dropped, parasitic resistors shorted) + netgen against
#               netlist/slot_7_netgen.spice (as netlist/netgen_check.sh) or pads/<cell>/<cell>.spice (vss port added
#               as ../d2s_pex/run.sh)
# Magic runs single-threaded, one at a time. Needs <work_dir>/design (fetch, for pex_add_port.py).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOT=$(cd "$HERE/../../.." && pwd)
WORK=$(realpath -m "$1")
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=${PDK:-ihp-sg13cmos5l}
export PDKPATH=$PDK_ROOT/$PDK
RCFILE=$PDKPATH/libs.tech/magic/$PDK.magicrc
SETUP=$PDKPATH/libs.tech/netgen/${PDK}_setup.tcl
S2D=sg13cmos5l_IOPadSingle2Diff
D2S=sg13cmos5l_IOPadDiff2Single

head_tcl() {  # head_tcl <gds> <top cell> <subckt name> <ext dir>
  cat << EOF
crashbackups stop
drc off
gds read $1
load $2
select top cell
flatten ${2}_flat
load ${2}_flat
cellname delete $2
cellname rename ${2}_flat $3
select top cell
extract path $4
ext2spice lvs
EOF
}

extract_cell() {  # extract_cell <dir> <gds> <top> <subckt name>
  local d=$1 g=$2 top=$3 n=$4 t0
  rm -rf "$d"; mkdir -p "$d/sak" "$d/c" "$d/rc"
  t0=$(date +%s)
  cp "$g" "$d/sak/"
  sak-pex.sh -d -m 2 -n "$n" -w "$d/sak" "$d/sak/$(basename "$g")" > "$d/sak/run.log" 2>&1
  { head_tcl "$g" "$top" "$n" "$d/c"
    echo "extract all"
    echo "ext2spice cthresh 0.01"
    echo "ext2spice -p $d/c -o $d/c/hier.spice"
    echo "ext2spice hierarchy off"
    echo "ext2spice -p $d/c -o $d/c/flat.spice"
    echo "quit -noprompt"; } > "$d/c/pex.tcl"
  magic -dnull -noconsole -rcfile "$RCFILE" "$d/c/pex.tcl" > "$d/c/magic.log" 2>&1
  python3 -I "$HERE/pexfix.py" c "$d/c/hier.spice" "$d/c/flat.spice" "$d/c/$top.pex.spice"
  { head_tcl "$g" "$top" "$n" "$d/rc"
    echo "extresist threshold 0"
    echo "extresist mindelay 0"
    echo "extresist minres 100"
    echo "extract do resistance"
    echo "extract do unique"
    echo "extract all"
    echo "ext2spice extresist on"
    echo "ext2spice cthresh 0.01"
    echo "ext2spice -p $d/rc -o $d/rc/rc_magic.spice"
    echo "quit -noprompt"; } > "$d/rc/pex.tcl"
  magic -dnull -noconsole -rcfile "$RCFILE" "$d/rc/pex.tcl" > "$d/rc/magic.log" 2>&1
  python3 -I "$HERE/pexfix.py" rc "$d/rc/rc_magic.spice" "$d/c/$top.pex.spice" "$d/rc/$n.res.ext" \
    "$d/rc/$top.pex.spice" "$d/rc/rnode_caps.csv"
  echo "  $top: $(( $(date +%s) - t0 )) s; $(grep -E 'Nets extracted' "$d/rc/magic.log")"
}

lvs() {  # lvs <dir> <pex netlist> <top> <subckt name in pex> <reference> <netgen cell>
  local d=$1
  rm -rf "$d"; mkdir -p "$d"
  python3 -I "$HERE/lvs_collapse.py" "$2" "$d/lay.spice"
  if [ "$3" != slot_7 ]; then
    python3 -I "$WORK/design/scripts/pex_add_port.py" "$d/lay.spice" "$4" vss iovss 1 > /dev/null
    sed -i -e '/^Rport_vss/d' -e "s/\b$4\b/$3/" "$d/lay.spice"
    grep -v -e '^\* PROVENANCE' -e '^\* commit' -e '^\* sha256' "$5" > "$d/sch.spice"
  else
    cp "$5" "$d/sch.spice"
  fi
  (cd "$d" && netgen -batch lvs "lay.spice $3" "sch.spice $3" "$SETUP" lvs.out < /dev/null > netgen.log 2>&1) || true
  echo "  $(basename "$d"): $(grep -E 'match uniquely|Netlists match|do not match' "$d/lvs.out" | tail -1) $(grep 'Final result' "$d/lvs.out")"
}

echo "magic extraction"
extract_cell "$WORK/x_slot_7" "$SLOT/final/gds/slot_7.gds" slot_7 slot_7
for T in $S2D $D2S; do
  extract_cell "$WORK/x_$T" "$SLOT/pads/$T/$T.gds" $T ${T}_pex
done
# pad_ref_rb alone, cut from slot_7.gds, C-coupled (for the hybrid view 'hyb' of sim.py: the earlier deck with only
# this block replaced by its magic extraction)
d=$WORK/x_pad_ref_rb; rm -rf "$d"; mkdir -p "$d"
{ head_tcl "$SLOT/final/gds/slot_7.gds" pad_ref_rb pad_ref_rb "$d"
  echo "extract all"; echo "ext2spice cthresh 0.01"; echo "ext2spice -p $d -o $d/hier.spice"
  echo "ext2spice hierarchy off"; echo "ext2spice -p $d -o $d/flat.spice"; echo "quit -noprompt"; } > "$d/pex.tcl"
magic -dnull -noconsole -rcfile "$RCFILE" "$d/pex.tcl" > "$d/magic.log" 2>&1
python3 -I "$HERE/pexfix.py" c "$d/hier.spice" "$d/flat.spice" "$d/pad_ref_rb.pex.spice"

echo "netgen LVS"
for v in c rc; do
  lvs "$WORK/x_slot_7/lvs_$v" "$WORK/x_slot_7/$v/slot_7.pex.spice" slot_7 slot_7 "$SLOT/netlist/slot_7_netgen.spice"
  for T in $S2D $D2S; do
    lvs "$WORK/x_$T/lvs_$v" "$WORK/x_$T/$v/$T.pex.spice" $T ${T}_pex "$SLOT/pads/$T/$T.spice"
  done
done
