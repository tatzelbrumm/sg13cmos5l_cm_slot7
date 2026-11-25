#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# DC curves of the S2D / D2S pads (IHP sg13cmos5l simulation, schematic | magic PEX): reproduces plots/, csv/, tables/
# of this folder from a checkout of this repository plus the design-repository commits (fetched by fetch.sh).
# Usage: run.sh [<work_dir>] [fetch|s2d|d2s|rt|vrefvcm|check|plots|all]   (default ./_work, all)
# Environment: JOBS = parallel ngspice runs (default 3). Needs PDK_ROOT with ihp-sg13cmos5l, ngspice with the IHP OSDI
# models, xschem, CACE 2.11, python3 with numpy / matplotlib / pyyaml, git with network access to github.com.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export JOBS=${JOBS:-3}
export PYTHONDONTWRITEBYTECODE=1
S2D=sg13cmos5l_IOPadSingle2Diff
D2S=sg13cmos5l_IOPadDiff2Single
mkdir -p "$WORK" "$HERE/plots" "$HERE/csv" "$HERE/tables"

fetch() { "$HERE/fetch.sh" "$WORK"; }

s2d() {
  "$HERE/cace_dc.sh" "$WORK" $S2D schematic s2d_grid || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  "$HERE/cace_dc.sh" "$WORK" $S2D pex s2d_grid || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  python3 "$HERE/s2d.py" "$WORK/out" "$HERE" s2d_grid
}

d2s() {
  "$HERE/cace_dc.sh" "$WORK" $D2S schematic d2s_grid d2s_noload d2s_slot || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  "$HERE/cace_dc.sh" "$WORK" $D2S pex d2s_grid d2s_noload d2s_slot || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  python3 "$HERE/d2s.py" "$WORK/out" "$HERE"
}

rt() {
  # needs the pad netlists that the s2d / d2s steps prepared (schematic and PEX views)
  grep -v '^#' "$HERE/jobs_rt.txt" | xargs -P "$JOBS" -n 1 python3 -I "$HERE/roundtrip.py" "$WORK" "$WORK/out/rt"
  python3 "$HERE/rt.py" "$WORK/out/rt" "$HERE"
}

vrefvcm() {
  "$HERE/cace_dc.sh" "$WORK" $S2D schematic s2d_vrefvcm s2d_slot || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  python3 "$HERE/s2d.py" "$WORK/out" "$HERE" s2d_slot
  python3 "$HERE/vrefvcm.py" "$WORK/out" "$HERE"
}

check() {
  # effect of the D2S solver aid rshunt=1e12: the same +-1 V sweeps with and without it (schematic)
  "$HERE/cace_dc.sh" "$WORK" $D2S schematic d2s_rshunt_chk || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
  NORSHUNT=1 "$HERE/cace_dc.sh" "$WORK" $D2S schematic d2s_rshunt_chk || echo "WARNING: cace_dc.sh reported a failure (see <work_dir>/out/<view>/log_*.txt, *.failed.txt)"
}

plots() {
  python3 "$HERE/s2d.py" "$WORK/out" "$HERE" s2d_grid
  python3 "$HERE/s2d.py" "$WORK/out" "$HERE" s2d_slot
  python3 "$HERE/d2s.py" "$WORK/out" "$HERE"
  python3 "$HERE/rt.py" "$WORK/out/rt" "$HERE"
  python3 "$HERE/vrefvcm.py" "$WORK/out" "$HERE"
  python3 "$HERE/crosscheck.py" "$WORK/design" "$HERE" "$WORK/out"
}

case "$STEP" in
  all) fetch; s2d; d2s; rt; vrefvcm; check; plots ;;
  fetch|s2d|d2s|rt|vrefvcm|check|plots) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
