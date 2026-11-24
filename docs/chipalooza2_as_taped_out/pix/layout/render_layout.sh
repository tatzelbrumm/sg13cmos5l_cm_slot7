#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Re-render the slot 7 layout pictures from the taped-out GDS in this repository.
# Usage:  render_layout.sh [out_dir]      (default: the folder this script is in)
# Needs: KLayout 0.30 (klayout -zz), python3 with Pillow, the IHP sg13cmos5l layer properties.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../../../.." && pwd)
OUT=${1:-$HERE}
PDK_ROOT=${PDK_ROOT:-/foss/pdks}
LYP=$PDK_ROOT/ihp-sg13cmos5l/libs.tech/klayout/tech/sg13cmos5l.lyp
RAW=$(mktemp -d)
trap 'rm -rf "$RAW"' EXIT

klayout -zz -rd repo="$REPO" -rd out="$RAW" -rd lyp="$LYP" -r "$HERE/render_layout.py"
python3 "$HERE/annotate_layout.py" "$RAW" "$OUT"
