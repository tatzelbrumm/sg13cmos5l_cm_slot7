#!/bin/bash
# magic extraction of slot_7.gds (v3: no cell rename needed) and netgen LVS against slot_7_netgen.spice
set -e
export PDK_ROOT=${PDK_ROOT:-/foss/pdks} PDK=ihp-sg13cmos5l
cd "$(dirname "$0")"; mkdir -p mag
cd mag
magic -dnull -noconsole -rcfile ${PDK_ROOT}/${PDK}/libs.tech/magic/${PDK}.magicrc > ../magic.log 2>&1 << MEOF
drc off
crashbackups stop
locking disable
units microns
snap internal
gds read ../slot_7.gds
load slot_7
select top cell
extract path extfiles
extract no all
extract do unique
extract all
ext2spice lvs
ext2spice -p extfiles -o ../slot_7_layout.spice
quit -noprompt
MEOF
cd ..
netgen -batch lvs "slot_7_layout.spice slot_7" "slot_7_netgen.spice slot_7" ${PDK_ROOT}/${PDK}/libs.tech/netgen/${PDK}_setup.tcl comp_slot_7.out < /dev/null > netgen.log 2>&1 || true
grep -n "Final result" comp_slot_7.out || true
grep -E "Circuits match uniquely|Netlists match uniquely|Netlists do not match|instanced inside" comp_slot_7.out | sort | uniq -c
grep -iE "unknown layer|context" magic.log | head -3
