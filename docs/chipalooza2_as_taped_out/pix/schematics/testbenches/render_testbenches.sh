#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Re-render the slot 7 test-bench pictures (SVG): the CACE templates and the stand-alone xschem test
# benches of the design repository https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
# at the two taped-out commits. Same method as ../render_schematics.sh.
#
# Usage:  render_testbenches.sh [work_dir] [out_dir]
#   work_dir  scratch folder for the sparse checkout (default: ${TMPDIR:-/tmp}/s7_testbenches)
#   out_dir   where the SVGs go (default: the folder this script is in)
# Needs: git, xschem (3.4.x), xvfb-run, the IHP open PDK (PDK_ROOT, PDK=ihp-sg13cmos5l).
# Only .sch/.sym/xschemrc files are fetched (a few MB), never the whole ~160 MB repository.
#
# CACE templates are rendered as they are in the repository, i.e. with their CACE placeholders
# ({vdd}, {corner}, {temperature}, ...) unsubstituted.
set -euo pipefail

REPO_URL=https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single
PADS_COMMIT=91a7da8b67ac56a26c605501146667a1fde28c32   # sg13cmos5l_IOPadSingle2Diff / _IOPadDiff2Single
SLOT_COMMIT=9052bd35928c6d40344e8e686c9abbe736bfadb9   # macros/slot_7 and the blocks it places

HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${1:-${TMPDIR:-/tmp}/s7_testbenches}
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

# 2. Render. macros/xschemrc of the design repo puts every macros/*/schematic/xschem and
#    macros/*/testbenches/xschem folder on the symbol search path, which covers every symbol the
#    test benches place (DUT, bias_gen_pd, en_ctrl_3v3, *_sel wrappers, hv_logic, bias_*_pd).
#    dark_colorscheme 0 gives the white background. Exported area = bounding box + 3 % margin,
#    0.75 px per xschem unit clamped to 900..2400 px wide, viewBox added afterwards.
EXPORT_TCL='
  foreach {x1 y1 x2 y2} [xschem get bbox] break
  set mx [expr {0.03*($x2-$x1)}]; set my [expr {0.03*($y2-$y1)}]
  set x1 [expr {$x1-$mx}]; set x2 [expr {$x2+$mx}]; set y1 [expr {$y1-$my}]; set y2 [expr {$y2+$my}]
  set w [expr {int(min(2400, max(900, 0.75*($x2-$x1))))}]
  set h [expr {int($w*($y2-$y1)/($x2-$x1))}]
  xschem print svg $svgfile $w $h $x1 $y1 $x2 $y2
  exit'
# Without an X server (xschem -x) text extents are unknown and "get bbox" misses the comment texts.
if command -v xvfb-run >/dev/null; then XRUN="xvfb-run -a"; else XRUN=""; echo "no xvfb-run: texts may be clipped"; fi
# The code blocks (netlist / control text) are Monospace. xschem's bounding box underestimates their width
# against a browser's DejaVu Sans Mono (0.602 em per character), so a long code line can run past the right
# edge where the code block is the widest part of the sheet. Widen the page (width and viewBox, same scale)
# until every Monospace line ends inside it with the same ~3 % margin.
widen_for_monospace() {
  python3 -I - "$1" <<'PY'
import html, math, re, sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
m = re.search(r'width="(\d+)" height="(\d+)" viewBox="0 0 (\d+) (\d+)"', s)
w = int(m.group(1))
right = 0.0
for fs, x, t in re.findall(r'<text[^>]*font-size="([\d.]+)"[^>]*font-family:Monospace;[^>]*'
                           r'translate\(([-\d.]+),[^)]*\)[^>]*>([^<]*)</text>', s):
    right = max(right, float(x) + len(html.unescape(t)) * float(fs) * 0.602)
need = math.ceil(right + 0.03 / 1.06 * w)
if need > w:
    s = s.replace(m.group(0), f'width="{need}" height="{m.group(2)}" viewBox="0 0 {need} {m.group(4)}"', 1)
    bg = f'<rect class="l0" x="0" y="0" width="{w}" height="{m.group(2)}"/>'   # white background
    s = s.replace(bg, bg.replace(f'width="{w}"', f'width="{need}"'), 1)
    open(p, 'w', encoding='utf-8').write(s)
    print(f'  widened {p.rsplit("/", 1)[-1]}: {w} -> {need} px (Monospace code lines)')
PY
}
render() {  # commit path-below-macros/ output-name
  local src="$WORK/src_${1:0:7}/macros"
  local sch="$src/$2"
  local name=$3
  local log="$WORK/$name.log"
  rm -f "$OUT/$name.svg"
  ( cd "$WORK" && timeout 120 $XRUN xschem -q --rcfile "$src/xschemrc" --tcl 'set dark_colorscheme 0' \
      --command "set svgfile {$OUT/$name.svg}; $EXPORT_TCL" "$sch" ) >"$log" 2>&1 || true
  if [ ! -s "$OUT/$name.svg" ]; then echo "FAILED  $name (see $log)"; return; fi
  sed -i '1s/<svg \(.*\) width="\([0-9]*\)" height="\([0-9]*\)"/<svg \1 width="\2" height="\3" viewBox="0 0 \2 \3"/' "$OUT/$name.svg"
  widen_for_monospace "$OUT/$name.svg"
  if grep -qi 'not found\|missing\|error' "$log"; then
    echo "WARN    $name: $(grep -i 'not found\|missing\|error' "$log" | head -3 | tr '\n' ' ')"
  fi
  printf '%-50s %8d bytes\n' "$name.svg" "$(stat -c %s "$OUT/$name.svg")"
}

# CACE templates: <cell>_<tb>.sch -> <cell>__<tb>.svg
S2D=sg13cmos5l_IOPadSingle2Diff/verification/cace/templates
D2S=sg13cmos5l_IOPadDiff2Single/verification/cace/templates
for tb in tb_ac tb_dc tb_enable tb_noise tb_pd tb_range tb_tran; do
  render $PADS_COMMIT $S2D/sg13cmos5l_IOPadSingle2Diff_$tb.sch sg13cmos5l_IOPadSingle2Diff__$tb
done
render $PADS_COMMIT $S2D/s2d_mpdda_pd_sel_tb_loop.sch s2d_mpdda_pd_sel__tb_loop
for tb in tb_ac tb_dc tb_drive tb_enable tb_noise tb_pd tb_thd tb_tran; do
  render $PADS_COMMIT $D2S/sg13cmos5l_IOPadDiff2Single_$tb.sch sg13cmos5l_IOPadDiff2Single__$tb
done
render $PADS_COMMIT $D2S/d2s_mpdda_pd_sel_tb_loop.sch d2s_mpdda_pd_sel__tb_loop

# Stand-alone D2S test benches (DUT d2s_mpdda_pd): testbenches/xschem/<tb>.sch -> d2s_mpdda_pd__<tb>.svg
for tb in tb_pd_enable tb_pd_leak tb_pd_startup_oa tb_pd_unpowered; do
  render $PADS_COMMIT sg13cmos5l_IOPadDiff2Single/testbenches/xschem/$tb.sch d2s_mpdda_pd__$tb
done

# Slot 7 blocks (commit 9052bd3). Of bg_core_pd, bias_dist_pd, en_ctrl_3v3, vcm_rb, vref_s2d_rb, slot_7
# only en_ctrl_3v3 has xschem test benches at this commit.
render $SLOT_COMMIT pad_ref_rb/verification/cace/templates/pad_ref_rb_tb_dc.sch pad_ref_rb__tb_dc
for tb in tb_dc tb_tran_en tb_tran_vddl; do
  render $SLOT_COMMIT en_ctrl_3v3/verification/cace/templates/en_ctrl_3v3_$tb.sch en_ctrl_3v3__$tb
done
