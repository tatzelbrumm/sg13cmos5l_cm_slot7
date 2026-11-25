#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Re-runs the sign-off checks of the taped-out slot 7 (this repository at 158afc5):
# final/gds/slot_7.gds (v3 + tughra art, top cell slot_7) and the two pad cells in pads/.
#
#   usage: run_signoff.sh [OUT_DIR] [STEP ...]
#     OUT_DIR  run directory (default: ./signoff_run); everything is written there, nothing in the repository
#     STEP     any of: env drc maxlu density lvs magicdrc netgen summary  (default: all, in this order)
#   environment: PDK_ROOT (default /foss/pdks), PDK (default ihp-sg13cmos5l), THR (KLayout threads, default 2),
#                SAK (directory of sak-drc.sh / sak-lvs.sh, default /foss/tools/sak)
#
# Per check and cell, the exact command, its exit code and its wall time are appended to OUT_DIR/runtimes.txt;
# its stdout/stderr go to OUT_DIR/logs/<cell>.<step>.log. summarize.py then writes OUT_DIR/summary/*.txt.
# The summaries committed in reports/ next to this script are copies of OUT_DIR/summary/ of the run of 2026-11-25.

set -u -o pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
OUT=$(realpath -m "${1:-$PWD/signoff_run}")
[ $# -gt 0 ] && shift
STEPS=${*:-env drc maxlu density lvs magicdrc netgen summary}

export PDK_ROOT=${PDK_ROOT:-/foss/pdks}
export PDK=${PDK:-ihp-sg13cmos5l}
export PDKPATH=$PDK_ROOT/$PDK
export STD_CELL_LIBRARY=${STD_CELL_LIBRARY:-sg13cmos5l_stdcell}
THR=${THR:-2}
SAK=${SAK:-/foss/tools/sak}
KLT=$PDKPATH/libs.tech/klayout/tech

# cell | layout | netlist for KLayout LVS | netlist for magic + netgen
CELLS="slot_7 S2D D2S"
declare -A GDS TOP KNET MNET
GDS[slot_7]=$REPO/final/gds/slot_7.gds
TOP[slot_7]=slot_7
KNET[slot_7]=$REPO/netlist/slot_7.cdl
MNET[slot_7]=$REPO/netlist/slot_7_netgen.spice
for p in S2D D2S; do
	case $p in
		S2D) c=sg13cmos5l_IOPadSingle2Diff ;;
		D2S) c=sg13cmos5l_IOPadDiff2Single ;;
	esac
	GDS[$p]=$REPO/pads/$c/$c.gds
	TOP[$p]=$c
	KNET[$p]=$OUT/$p/netlist/$c.cdl        # derived from MNET by spice2cdl.py (see README)
	MNET[$p]=$REPO/pads/$c/$c.spice
done

mkdir -p "$OUT/logs"
RT=$OUT/runtimes.txt
SPDX_HDR='# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0'
[ -f "$RT" ] || printf '%s\n# cell\tstep\texit code\twall time\tcommand\n' "$SPDX_HDR" > "$RT"

# run <cell> <step> <command...>: log, exit code and wall time
run() {
	local cell=$1 step=$2
	shift 2
	local log=$OUT/logs/$cell.$step.log t0 t1 rc
	t0=$(date +%s)
	echo "[$(date -u +%FT%TZ)] $cell $step: $*"
	"$@" > "$log" 2>&1
	rc=$?
	t1=$(date +%s)
	printf '%s\t%s\trc=%d\t%ds\t%s\n' "$cell" "$step" "$rc" "$((t1 - t0))" "$*" >> "$RT"
	echo "    rc=$rc, $((t1 - t0)) s, log $log"
	return 0
}

step_env() {
	local f=$OUT/versions.txt
	{
		echo "$SPDX_HDR"
		echo "date (UTC): $(date -u +%FT%TZ)"
		echo "host: $(uname -srm), $(nproc) CPUs, KLayout threads used: $THR"
		echo "klayout: $(klayout -b -v 2>&1)"
		echo "python3: $(python3 --version 2>&1), klayout python module: $(python3 -c 'import klayout.db as d; print(d.__version__)' 2>&1)"
		echo "magic: $(magic --version 2>&1 | head -1)"
		echo "netgen: $(netgen -batch quit < /dev/null 2>&1 | grep -m1 -i '^netgen')"
		echo "PDK: PDK_ROOT=$PDK_ROOT PDK=$PDK -> $(realpath "$PDKPATH")"
		echo "PDK git: $(git -C "$PDKPATH" rev-parse HEAD 2>&1) ($(git -C "$PDKPATH" log -1 --format='%cd: %s' 2>&1))"
		echo "PDK git describe: $(git -C "$PDKPATH" describe --always --tags 2>&1)"
		echo "PDK work tree: $(git -C "$PDKPATH" status --porcelain 2>&1 | wc -l) modified/untracked entries (git status --porcelain)"
		echo "PDK broken symlinks under libs.tech/klayout: $(find "$PDKPATH/libs.tech/klayout" -xtype l 2>/dev/null | wc -l) $(find "$PDKPATH/libs.tech/klayout" -xtype l 2>/dev/null | tr '\n' ' ')"
		[ -f /foss/tools/BUILDINFO ] && grep -E '^(magic|netgen|iic|ihp-open-pdk) ' /foss/tools/BUILDINFO | sed 's/^/tool build: /'
		echo "sak scripts: $SAK (sha256 sak-drc.sh $(sha256sum "$SAK/sak-drc.sh" | cut -c1-16), sak-lvs.sh $(sha256sum "$SAK/sak-lvs.sh" | cut -c1-16))"
		echo "repository: $REPO, HEAD $(git -C "$REPO" rev-parse HEAD 2>&1)"
		echo
		echo "input sha256:"
		for c in $CELLS; do
			sha256sum "${GDS[$c]}"
			sha256sum "${MNET[$c]}"
		done
		sha256sum "$REPO/netlist/slot_7.cdl" "$REPO/netlist/netgen_check.sh"
		echo
		# slot_7.gds against the provenance table of README.md (the row of final/gds/slot_7.gds, last sha256 = "this file")
		local want got
		want=$(grep '^| `final/gds/slot_7.gds`' "$REPO/README.md" | grep -oE '[0-9a-f]{64}' | tail -1)
		got=$(sha256sum "${GDS[slot_7]}" | cut -d' ' -f1)
		if [ "$want" = "$got" ]; then echo "slot_7.gds sha256 = README.md provenance table: OK ($got)"
		else echo "slot_7.gds sha256 MISMATCH: README.md $want, file $got"; fi
		for c in S2D D2S; do
			want=$(grep "^| \`pads/${TOP[$c]}/${TOP[$c]}.gds\`" "$REPO/README.md" | grep -oE '[0-9a-f]{64}' | tail -1)
			got=$(sha256sum "${GDS[$c]}" | cut -d' ' -f1)
			if [ "$want" = "$got" ]; then echo "${TOP[$c]}.gds sha256 = README.md provenance table: OK"
			else echo "${TOP[$c]}.gds sha256 MISMATCH: README.md $want, file $got"; fi
		done
	} > "$f" 2>&1
	cat "$f"
}

# 1a. the PDK runner as the designer ran it: main deck + maximal deck (its default switches), no density
step_drc() {
	for c in $CELLS; do
		run "$c" drc python3 "$KLT/drc/run_drc.py" --path="${GDS[$c]}" --topcell="${TOP[$c]}" \
			--run_dir="$OUT/$c/klayout_drc" --no_density --mp=1 --density_thr="$THR"
	done
}

# 1b. the maximal deck alone, latch-up rules switched on explicitly
step_maxlu() {
	for c in $CELLS; do
		mkdir -p "$OUT/$c/klayout_maximal_lu"
		run "$c" maxlu klayout -b -r "$KLT/drc/rule_decks/sg13cmos5l_maximal.drc" \
			-rd input="${GDS[$c]}" -rd topcell="${TOP[$c]}" -rd run_mode=deep \
			-rd thr="$THR" -rd threads="$THR" -rd latchUpRules=true \
			-rd report="$OUT/$c/klayout_maximal_lu/${TOP[$c]}_maximal_lu.lyrdb" \
			-rd log="$OUT/$c/klayout_maximal_lu/${TOP[$c]}_maximal_lu.log"
	done
}

# 1c. density only (the slot and the pads are not filled; fill is done at chip level)
step_density() {
	for c in $CELLS; do
		run "$c" density python3 "$KLT/drc/run_drc.py" --path="${GDS[$c]}" --topcell="${TOP[$c]}" \
			--run_dir="$OUT/$c/klayout_density" --density_only --density_thr="$THR"
	done
}

# 2. KLayout LVS, deep, taps not extracted
step_lvs() {
	for c in $CELLS; do
		if [ "$c" != slot_7 ]; then
			mkdir -p "$OUT/$c/netlist"
			python3 "$HERE/spice2cdl.py" "${MNET[$c]}" "${KNET[$c]}"
			# the netgen-flavour netlist as given, for the record (its X-card devices are not read as devices)
			run "$c" lvs_spice_as_given python3 "$KLT/lvs/run_lvs.py" --layout="${GDS[$c]}" --netlist="${MNET[$c]}" \
				--topcell="${TOP[$c]}" --run_dir="$OUT/$c/klayout_lvs_spice_as_given" --run_mode=deep --disable_tap_extraction
		fi
		run "$c" lvs python3 "$KLT/lvs/run_lvs.py" --layout="${GDS[$c]}" --netlist="${KNET[$c]}" \
			--topcell="${TOP[$c]}" --run_dir="$OUT/$c/klayout_lvs" --run_mode=deep --disable_tap_extraction
	done
}

# 3a. magic DRC, drc(full), with the IIC-OSIC-TOOLS script that wrote the committed pad / bg_core_pd reports
step_magicdrc() {
	for c in $CELLS; do
		mkdir -p "$OUT/$c/magic_drc"
		run "$c" magicdrc sh "$SAK/sak-drc.sh" -m -w "$OUT/$c/magic_drc" "${GDS[$c]}"
	done
	# cross-check: the stand-alone bg_core_pd macro (macros/), whose committed magic report (signoff/bg_core_pd/) says COUNT 0
	mkdir -p "$OUT/bg_core_pd/magic_drc"
	run bg_core_pd magicdrc sh "$SAK/sak-drc.sh" -m -w "$OUT/bg_core_pd/magic_drc" "$REPO/macros/bg_core_pd/layout/gds/bg_core_pd.gds"
}

# 3b. magic extraction + netgen
#     slot_7: the designer's netlist/netgen_check.sh, unchanged, in a copy of netlist/ with slot_7.gds next to it
#     pads:   sak-lvs.sh -m (flatten, extract, netgen), as the design repository's `make magic-lvs`
step_netgen() {
	local d=$OUT/slot_7/netgen
	rm -rf "$d"
	mkdir -p "$d"
	cp "$REPO/netlist/netgen_check.sh" "$REPO/netlist/slot_7_netgen.spice" "$d/"
	cp "${GDS[slot_7]}" "$d/slot_7.gds"
	run slot_7 netgen bash "$d/netgen_check.sh"
	for c in S2D D2S; do
		mkdir -p "$OUT/$c/magic_lvs"
		run "$c" netgen sh "$SAK/sak-lvs.sh" -m -s "${MNET[$c]}" -l "${GDS[$c]}" -c "${TOP[$c]}" -w "$OUT/$c/magic_lvs"
	done
}

step_summary() {
	python3 "$HERE/summarize.py" "$OUT"
}

for s in $STEPS; do
	case $s in
		env|drc|maxlu|density|lvs|magicdrc|netgen|summary) "step_$s" ;;
		*) echo "unknown step $s"; exit 2 ;;
	esac
done
