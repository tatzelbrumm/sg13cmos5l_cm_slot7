#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Re-render the slot 7 schematic pictures (SVG) from the xschem sources of the design repository
# https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single at the two taped-out commits.
#
# Usage:  render_schematics.sh [work_dir] [out_dir]
#   work_dir  scratch folder for the sparse checkout (default: ${TMPDIR:-/tmp}/s7_schematics)
#   out_dir   where the SVGs go (default: the folder this script is in)
# Needs: git, xschem (3.4.x), the IHP open PDK (PDK_ROOT, PDK=ihp-sg13cmos5l).
# Only .sch/.sym/xschemrc files are fetched (a few MB), never the whole ~160 MB repository.
set -euo pipefail

REPO_URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
PADS_COMMIT=91a7da8b67ac56a26c605501146667a1fde28c32   # sg13cmos5l_IOPadSingle2Diff / _IOPadDiff2Single
SLOT_COMMIT=9052bd35928c6d40344e8e686c9abbe736bfadb9   # macros/slot_7 and the blocks it places

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:-${TMPDIR:-/tmp}/s7_schematics}
OUT=${2:-$HERE}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export PDK=${PDK:-ihp-sg13cmos5l}

mkdir -p "$WORK" "$OUT"
WORK=$(cd "$WORK" && pwd); OUT=$(cd "$OUT" && pwd)

# 1. Blob-less, shallow, no-checkout clone; then extract only the xschem sources of each commit.
if [ ! -d "$WORK/repo/.git" ]; then
  git clone --quiet --depth 1 --filter=blob:none --no-checkout "$REPO_URL" "$WORK/repo"
fi
for c in $PADS_COMMIT $SLOT_COMMIT; do
  d="$WORK/src_${c:0:7}"
  if [ ! -d "$d" ]; then
    git -C "$WORK/repo" fetch --quiet --depth 1 origin "$c"
    mkdir -p "$d"
    git -C "$WORK/repo" ls-tree -r --name-only "$c" | grep '\.sch$\|\.sym$\|xschemrc$' > "$d.files"
    git -C "$WORK/repo" archive "$c" $(cat "$d.files") | tar x -C "$d"
  fi
done

# 2. Render. macros/xschemrc of the design repo puts every macros/*/schematic/xschem folder on the
#    symbol search path (symbol basenames are unique across macros at both commits).
#    dark_colorscheme 0 gives the white background. The exported area is the drawing's bounding box
#    (xschem get bbox) plus a 3 % margin; the page is 0.75 px per xschem unit, clamped to 900..2400 px
#    wide, and a viewBox is added afterwards so the SVG scales cleanly in a browser or Markdown viewer.
EXPORT_TCL='
  foreach {x1 y1 x2 y2} [xschem get bbox] break
  set mx [expr {0.03*($x2-$x1)}]; set my [expr {0.03*($y2-$y1)}]
  set x1 [expr {$x1-$mx}]; set x2 [expr {$x2+$mx}]; set y1 [expr {$y1-$my}]; set y2 [expr {$y2+$my}]
  set w [expr {int(min(2400, max(900, 0.75*($x2-$x1))))}]
  set h [expr {int($w*($y2-$y1)/($x2-$x1))}]
  xschem print svg $svgfile $w $h $x1 $y1 $x2 $y2
  exit'
# Run under a virtual X server: without X (xschem -x) text extents are unknown, so "get bbox" misses the
# comment texts and they would be cut off.
if command -v xvfb-run >/dev/null; then XRUN="xvfb-run -a"; else XRUN=""; echo "no xvfb-run: texts may be clipped"; fi
render() {  # commit macro cell
  local src="$WORK/src_${1:0:7}/macros"
  local sch="$src/$2/schematic/xschem/$3.sch"
  local log="$WORK/$3.log"
  rm -f "$OUT/$3.svg"
  ( cd "$WORK" && timeout 120 $XRUN xschem -q --rcfile "$src/xschemrc" --tcl 'set dark_colorscheme 0' \
      --command "set svgfile {$OUT/$3.svg}; $EXPORT_TCL" "$sch" ) >"$log" 2>&1 || true
  if [ ! -s "$OUT/$3.svg" ]; then echo "FAILED  $3 (see $log)"; return; fi
  sed -i '1s/<svg \(.*\) width="\([0-9]*\)" height="\([0-9]*\)"/<svg \1 width="\2" height="\3" viewBox="0 0 \2 \3"/' "$OUT/$3.svg"
  if grep -qi 'not found\|missing\|error' "$log"; then
    echo "WARN    $3: $(grep -i 'not found\|missing\|error' "$log" | head -3 | tr '\n' ' ')"
  fi
  printf '%-30s %8d bytes\n' "$3.svg" "$(stat -c %s "$OUT/$3.svg")"
}

# Pads (commit 91a7da8)
render $PADS_COMMIT sg13cmos5l_IOPadSingle2Diff sg13cmos5l_IOPadSingle2Diff
render $PADS_COMMIT sg13cmos5l_IOPadSingle2Diff s2d_mpdda_pd
render $PADS_COMMIT sg13cmos5l_IOPadSingle2Diff s2d_mpdda
render $PADS_COMMIT sg13cmos5l_IOPadSingle2Diff s2d_pad_esd
render $PADS_COMMIT bias_tree_noab_pd           bias_tree_noab_pd
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single sg13cmos5l_IOPadDiff2Single
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single d2s_mpdda_pd
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single d2s_out_p
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single d2s_out_n
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single d2s_sp2k
render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single unit_r2
render $PADS_COMMIT bias_tree_pd                bias_tree_pd

# Slot 7 and its blocks (commit 9052bd3)
render $SLOT_COMMIT slot_7       slot_7
render $SLOT_COMMIT slot_7       s7_ctrl
render $SLOT_COMMIT slot_7       s7_doutpd
render $SLOT_COMMIT pad_ref_rb   pad_ref_rb
render $SLOT_COMMIT pad_ref_rb   bias_tree_rb
render $SLOT_COMMIT pad_ref_rb   bypass_rb
render $SLOT_COMMIT vcm_rb       vcm_rb
render $SLOT_COMMIT vref_s2d_rb  vref_s2d_rb
render $SLOT_COMMIT bg_core_pd   bg_core_pd
render $SLOT_COMMIT bias_dist_pd bias_dist_pd
render $SLOT_COMMIT bias_dist_pd bdp_slice
render $SLOT_COMMIT en_ctrl_3v3  en_ctrl_3v3
render $SLOT_COMMIT en_ctrl_3v3  ls_up_fs
render $SLOT_COMMIT hv_logic     inv_hv
render $SLOT_COMMIT hv_logic     nand2_hv
render $SLOT_COMMIT hv_logic     tg_hv
