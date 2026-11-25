#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# ESD (HBM) and latch-up simulation of the slot-7 pads on a model of the harness pad ring (IHP sg13cmos5l simulation,
# PDK compact models, not ESD-calibrated). Reproduces csv/ and plots/ of this folder.
# Usage: run.sh [fetch|ring|iv|hbm|latchup|geometry|scr|post|all]   (default all; work dir ./_work)
# ngspice runs strictly one at a time. Needs PDK_ROOT with ihp-sg13cmos5l, ngspice-47 with the IHP OSDI models,
# KLayout's python module, python3 with numpy / matplotlib, git with network access to github.com.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=$HERE/_work
STEP=${1:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$WORK" "$HERE/csv" "$HERE/plots"
cd "$HERE"

fetch()    { ./fetch_harness.sh "$WORK"; }
ring()     { python3 ring.py "$WORK" "$HERE"; }
iv()       { python3 iv.py "$WORK"; }
hbm()      { python3 esd.py "$WORK" wave; python3 esd.py "$WORK" run; python3 esd.py "$WORK" post; }
latchup()  { python3 latchup.py "$WORK" itest; python3 latchup.py "$WORK" ovt; python3 latchup.py "$WORK" post; }
geometry() { python3 lu_geometry.py "$HERE"; }
scr()      { python3 scr.py "$WORK"; python3 scr_plot.py; }
post()     { python3 esd.py "$WORK" post; python3 latchup.py "$WORK" post; python3 scr_plot.py; python3 tables.py > "$WORK/tables.md"; }

case "$STEP" in
  all) fetch; ring; iv; hbm; latchup; geometry; scr; post ;;
  fetch|ring|iv|hbm|latchup|geometry|scr|post) "$STEP" ;;
  *) echo "unknown step $STEP"; exit 2 ;;
esac
