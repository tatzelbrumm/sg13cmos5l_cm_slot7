#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
# Run the sim.py jobs of a job file one at a time (one ngspice process), skipping jobs whose log in <work_dir>/out
# exists (a job that was run once, also a failed one, is not repeated; delete its log to run it again).
# Usage: runjobs.sh <work_dir> <job_file>
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$(realpath -m "$1")
grep -v '^#' "$2" | while IFS= read -r j; do
  [ -z "$j" ] && continue
  IFS=: read -r view c t v ana load <<< "$j"
  tag="${view}_${c}_${t}_${v}_${ana}"
  [ "$ana" = step ] && tag="${tag}_${load:-open}"
  [ -f "$WORK/out/$tag.log" ] && continue
  python3 -I "$HERE/sim.py" "$WORK" "$j"
done
