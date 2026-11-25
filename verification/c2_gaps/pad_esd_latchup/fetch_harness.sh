#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Fetch the harness padframe files this study reads (shallow, blobless; only these paths are downloaded):
# RTimothyEdwards/sg13cmos5l_ocd_chipalooza, branch tapeout_nov_2026, pinned to commit 2ef5a869 (the branch head
# on 2026-11-25). Usage: fetch_harness.sh <work_dir>  ->  <work_dir>/harness/<paths>
set -euo pipefail
WORK=$(realpath -m "$1")
URL=https://github.com/RTimothyEdwards/sg13cmos5l_ocd_chipalooza
REV=2ef5a86964b4f93a5b1e2c9bb8a46edc425cc227
mkdir -p "$WORK"
if [ ! -d "$WORK/harness_repo" ]; then
  git clone -q --depth 1 --filter=blob:none --no-checkout -b tapeout_nov_2026 "$URL" "$WORK/harness_repo"
fi
git -C "$WORK/harness_repo" fetch -q --depth 1 origin $REV
rm -rf "$WORK/harness" && mkdir -p "$WORK/harness"
git -C "$WORK/harness_repo" archive $REV magic/sg13cmos5l_padframe.mag magic/sg13cmos5l_ocd_Split2000.mag \
  verilog/rtl/sg13cmos5l_ocd_Split2000.v netlist/layout/sg13cmos5l_padframe.spice config.txt README \
  | tar x -C "$WORK/harness"
echo "fetched: $WORK/harness ($REV)"
