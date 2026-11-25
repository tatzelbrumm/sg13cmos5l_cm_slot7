#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# KLayout-extracted pads: antenna diodes at their extracted size (IHP sg13cmos5l simulation). Reproduces csv/ and
# plots/ of this folder.
# Usage: run.sh <ac_tran_work_dir> [<work_dir>] [diode|sine|dc|modes|eval|all]   (default ./_work, all)
#   <ac_tran_work_dir>  the work dir of ../ac_tran/run.sh after its fetch, s2d, d2s and slot steps: design/ and tier1/
#                       (design-repository commits 91a7da8b / 9052bd35) and out/slot (the schematic / PEX sine runs)
# Environment: JOBS = parallel ngspice runs in the modes step (default 3). Needs PDK_ROOT with ihp-sg13cmos5l,
# ngspice-47 with the IHP OSDI models, python3 with numpy / matplotlib / Pillow.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
AT=$(realpath "$1")
WORK=$(realpath -m "${2:-$HERE/_work}")
STEP=${3:-all}
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
export PYTHONDONTWRITEBYTECODE=1
JOBS=${JOBS:-3}
SPICEINIT=$PDK_ROOT/$PDK/libs.tech/ngspice/.spiceinit
mkdir -p "$WORK" "$HERE/csv" "$HERE/plots"
# the decks read <work>/tier1 and <work>/design (slot.py, roundtrip.py): the ac_tran work dir's copies
ln -sfn "$AT/tier1" "$WORK/tier1"
ln -sfn "$AT/design" "$WORK/design"
FIX="python3 -I $HERE/run_fixed.py"

diode() {   # the PDK antenna diode alone: a= / p= handling, the I-V step, the minimal abort (about 3 min)
  python3 -I "$HERE/diode_check.py" "$WORK" "$HERE"
}

sine() {    # 10 kHz sine, tt 27 C, KLayout pads with the diodes fixed (unloaded, 1 kOhm || 100 pF; about 2 min each),
            # AC and unloaded step (under 1 min), and the control: the sine as converted (aborts at 66 us; slot.py then
            # retries with rshunt, which aborts too)
  $FIX "$HERE/../ac_tran/slot.py" "$WORK/fixed_slot_runs" "$WORK" "$WORK/out_fixed/slot" \
    klayout:tt:27:3.3:sine klayout:tt:27:3.3:sine:100p klayout:tt:27:3.3:ac klayout:tt:27:3.3:step
  python3 -I "$HERE/../ac_tran/slot.py" "$WORK" "$WORK/out_orig/slot" klayout:tt:27:3.3:sine
}

dc() {      # DC round trip at the five tier-1 PVT points: KLayout pads fixed, and all three pad views as before
            # (about 10 s per KLayout run, 10 ... 40 s per schematic / PEX run)
  local PTS="tt:27:3.3 ss:-40:3.0 ff:125:3.6 fs:125:3.6 sf:-40:3.0" P="" Q="" p
  for p in $PTS; do P="$P klayout:$p"; Q="$Q klayout:$p schematic:$p pex:$p"; done
  $FIX "$HERE/../dc_curves/roundtrip.py" "$WORK/fixed_rt_runs" "$WORK" "$WORK/out_fixed/rt" $P
  python3 -I "$HERE/../dc_curves/roundtrip.py" "$WORK" "$WORK/out_orig/rt" $Q
}

modes() {   # ../slot_modes_bg/slot_modes.py with the fixed diodes: the designer's mode DC deck at ss -40 C 3.0 V
            # (variant dcop) for the five modes that failed there (about 2 min each), and two power-up transients that aborted
            # at the D2S pad diode in ../slot_modes_bg (sf -40 C: mon with 10 pF, swap with 1 Gohm only; ~10 s each)
  local n=0 j d
  for j in swap:ss:-40:3.0:dcop mon:ss:-40:3.0:dcop feed:ss:-40:3.0:dcop ext:ss:-40:3.0:dcop \
           swap+feed:ss:-40:3.0:dcop mon:sf:-40:3.0:pu swap:sf:-40:3.0:pu0; do
    d=${j//:/_}
    mkdir -p "$WORK/modes_fixed/$d"
    cp "$SPICEINIT" "$WORK/modes_fixed/$d/.spiceinit"
    rm -rf "$WORK/modes_out_fixed/$d"   # slot_modes.py appends to its CSVs
    $FIX "$HERE/../slot_modes_bg/slot_modes.py" "$WORK/modes_fixed" "$WORK/tier1" "$WORK/modes_fixed/$d" \
      "$WORK/modes_out_fixed/$d" "$j" > "$WORK/modes_fixed/$d.out" 2>&1 &
    n=$((n + 1))
    if [ $((n % JOBS)) -eq 0 ]; then wait; fi
  done
  wait
}

eval_() {
  python3 -I "$HERE/evaluate.py" "$WORK" "$AT/out/slot" "$HERE"
}

case "$STEP" in
  all) diode; sine; dc; modes; eval_ ;;
  eval) eval_ ;;
  diode|sine|dc|modes) $STEP ;;
  *) echo "unknown step $STEP"; exit 1 ;;
esac
