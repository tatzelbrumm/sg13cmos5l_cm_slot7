#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# AC / transient / noise curves of the S2D / D2S pads and the slot-7 round trip (IHP sg13cmos5l simulation,
# schematic | magic PEX): reproduces plots/, csv/, tables/ of this folder from a checkout of this repository plus the
# design-repository commits (fetched by ../dc_curves/fetch.sh, shallow and blobless).
# Usage: run.sh [<work_dir>] [fetch|s2d|d2s|slot|plots|all]   (default ./_work, all)
# Environment: JOBS = parallel ngspice runs (default 3). Needs PDK_ROOT with ihp-sg13cmos5l, ngspice with the IHP OSDI
# models, xschem, CACE 2.11, python3 with numpy / matplotlib / pyyaml, git with network access to github.com.
# Order: s2d and d2s before slot (slot uses the pad netlists that their CACE runs prepare).
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SLOTROOT=$(cd "$HERE/../../.." && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export JOBS=${JOBS:-3}
export PYTHONDONTWRITEBYTECODE=1
S2D=sg13cmos5l_IOPadSingle2Diff
D2S=sg13cmos5l_IOPadDiff2Single
DG="d2s_ac d2s_ac_load d2s_tran d2s_noise d2s_enable d2s_ac_slot d2s_ac_load_slot d2s_tran_slot"
W="WARNING: cace_at.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
mkdir -p "$WORK" "$HERE/plots" "$HERE/csv" "$HERE/tables"

fetch() { "$HERE/../dc_curves/fetch.sh" "$WORK"; }

s2d() {
  "$HERE/cace_at.sh" "$WORK" $S2D schematic s2d_ac s2d_tran s2d_noise s2d_enable || echo "$W"
  "$HERE/cace_at.sh" "$WORK" $S2D pex s2d_ac s2d_tran s2d_noise s2d_enable || echo "$W"
}

d2s() {
  "$HERE/cace_at.sh" "$WORK" $D2S schematic $DG || echo "$W"
  "$HERE/cace_at.sh" "$WORK" $D2S pex $DG || echo "$W"
  # check: effect of the solver aid rshunt=1e12 on the D2S schematic (results to <work_dir>/out/schematic_rshunt)
  RSHUNT=1 "$HERE/cace_at.sh" "$WORK" $D2S schematic d2s_ac d2s_tran d2s_noise || echo "$W"
}

slot() {
  grep -v '^#' "$HERE/jobs_slot.txt" | xargs -P "$JOBS" -n 1 python3 -I "$HERE/slot.py" "$WORK" "$WORK/out/slot"
}

plots() {
  cd "$HERE"
  python3 s2d.py "$WORK/out" "$HERE" "$WORK/design"
  python3 d2s.py "$WORK/out" "$HERE" "$WORK/design"
  python3 rt.py "$WORK/out/slot" "$HERE"
  python3 crosscheck.py "$WORK/out" "$HERE" "$WORK/design" "$SLOTROOT"
  python3 rshunt.py "$WORK/out" "$HERE"
}

case "$STEP" in
  all) fetch; s2d; d2s; slot; plots ;;
  fetch|s2d|d2s|slot|plots) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
