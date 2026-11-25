#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Terminal voltages of every MOS device of slot 7 and its two custom pads (IHP sg13cmos5l simulation, ngspice-47 with
# the IHP OSDI models): reproduces csv/, plots/ and tables.md of this folder from a checkout of this repository plus
# the design-repository commits 91a7da8b / 9052bd35 (fetched by ../dc_curves/fetch.sh, shallow and blobless).
# Usage: run.sh [<work_dir>] [fetch|sim|check|analyze|all]   (default ./_work, all)
#   sim runs the jobs of jobs.txt one after the other (one ngspice process at a time); a job whose result exists in
#   <work_dir>/dev is skipped (FORCE=1 reruns everything), and so is one that failed before (RETRY=1 retries those).
#   Raw files are deleted after evaluation (KEEP_RAW=1 keeps them).
# Needs PDK_ROOT with ihp-sg13cmos5l, ngspice-47 with the IHP OSDI models, python3 with numpy / matplotlib,
# git with network access to github.com.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(realpath -m "${1:-$HERE/_work}")
STEP=${2:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$WORK"

fetch() { "$HERE/../dc_curves/fetch.sh" "$WORK"; }

tagof() {  # job -> run tag (as vs.py)
  local IFS=:; set -- $1
  echo "$1_$2_$3_$4${5:+_$5}"
}

sim() {
  local j
  grep -v '^#' "$HERE/jobs.txt" | while read -r j; do
    [ -n "$j" ] || continue
    if [ "${FORCE:-0}" != 1 ] && [ -f "$WORK/dev/$(tagof "$j").csv.gz" ]; then continue; fi
    # a job that was tried and failed (log, no result) is retried only with RETRY=1
    if [ "${FORCE:-0}" != 1 ] && [ "${RETRY:-0}" != 1 ] && [ -f "$WORK/log/$(tagof "$j").log" ]; then continue; fi
    python3 -I "$HERE/vs.py" "$WORK" "$j"
  done
}

check() {  # solver / model check of the enable-edge transient (tt 27 C 3.6 V): stress-run setting, 2 / 0.5 ns step,
           # trapezoidal integration, NQS model (rfmode=1) on bg_core_pd + ls_up_fs and on bg_core_pd only
  python3 -I "$HERE/edges.py" "$WORK" "$HERE" en:tt:27:3.6 '' step2n step05n trap nqs nqsbg
}

analyze() {
  python3 -I "$HERE/analyze.py" "$WORK" "$HERE"
}

case "$STEP" in
  all) fetch; sim; check; analyze ;;
  fetch|sim|check|analyze) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
