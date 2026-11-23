#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Reproduce everything in this directory (IHP sg13cmos5l simulation, ngspice + IHP OSDI models).
# usage: ./run.sh [WORKDIR]   (default WORKDIR: ./_work, not committed; outputs written next to this script)
# Steps (each can be run alone: ./run.sh WORKDIR fetch|designer|modes|bg|tables)
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="$(mkdir -p "${1:-$HERE/_work}" && cd "${1:-$HERE/_work}" && pwd)"
STEP="${2:-all}"
REPO_URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
REPO_COMMIT=9052bd35928c6d40344e8e686c9abbe736bfadb9
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=${PDK:-ihp-sg13cmos5l}
SPICEINIT="$PDK_ROOT/$PDK/libs.tech/ngspice/.spiceinit"
[ -f "$SPICEINIT" ] || SPICEINIT=/foss/pdks/IHP-Open-PDK/ihp-sg13cmos5l/libs.tech/ngspice/.spiceinit
TREE="$WORK/tree"
NPAR=2   # at most 2 ngspice runs in parallel

fetch() {
  # only the needed paths of the design repository, at the commit (no full clone)
  if [ ! -d "$WORK/git" ]; then
    git clone -q --depth 1 --filter=blob:none --no-checkout "$REPO_URL" "$WORK/git"
  fi
  git -C "$WORK/git" fetch -q --depth 1 origin "$REPO_COMMIT"
  rm -rf "$TREE"; mkdir -p "$TREE"
  git -C "$WORK/git" archive FETCH_HEAD docs/slot7_hookup/tier1 macros/bg_core_pd/netlist macros/slot_7/netlist \
    macros/pad_ref_rb/netlist macros/bias_dist_pd/netlist macros/en_ctrl_3v3/netlist macros/hv_logic/netlist \
    macros/en_ctrl_3v3/testbenches/spice/run_starve.py macros/sg13cmos5l_IOPadSingle2Diff/netlist \
    macros/sg13cmos5l_IOPadDiff2Single/netlist | tar x -C "$TREE"
  mkdir -p "$TREE/docs/slot7_hookup/tier1/runs"
  for d in "$TREE/docs/slot7_hookup/tier1/runs" "$WORK/slot" "$WORK/bg"; do mkdir -p "$d"; cp "$SPICEINIT" "$d/.spiceinit"; done
}

designer() {
  # the designer's own run_modes.py, unchanged, at all three of its points (writes modes.txt in the fetched tree)
  (cd "$TREE/docs/slot7_hookup/tier1" && python3 -I run_modes.py)
  cp "$TREE/docs/slot7_hookup/tier1/modes.txt" "$HERE/designer_modes_rerun.txt"
}

modes() {
  rm -f "$HERE"/slot_modes_*.csv.raw
  # job list: see jobs_modes.txt (one job per line, <mode>:<mos>:<temp>:<vdd>[:variant])
  grep -v '^#' "$HERE/jobs_modes.txt" | xargs -P "$NPAR" -n 1 \
    python3 -I "$HERE/slot_modes.py" "$TREE" "$WORK/slot" "$WORK/slot_out"
}

bg() {
  python3 -I "$HERE/bg_core.py" "$TREE" "$WORK/bg" "$HERE" all
}

tables() {
  python3 -I "$HERE/tables.py" "$WORK" "$HERE"
}

case "$STEP" in
  all) fetch; designer; modes; bg; tables ;;
  *) "$STEP" ;;
esac
