# Slot 7 progress (for the harness owner)

What the harness reads from this repository: `final/gds/slot_7.gds` (top cell `slot_7`) and the custom pad cells in
`pads/<cell>/` (manifest `pads/pads.txt`). Everything else is documentation. The design work happens in
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single)
(macro `macros/slot7_testplatform/`, records `docs/slot7_testplatform/`: PLAN.md, RUNLOG.md, SUMMARY.md).
This file is updated with each step; newest entry first.

## 2026-11-06T18:48Z — stage B started (work branch `claude/c5-testplatform`)

Adds to the test platform (stage A stays as delivered on `main`):
- a bias tree `bias_tree_noab_pd` (the same tree as inside the S2D pad), its reference selectable from the OA core,
  the BG core or the harness `ibias0` (`dig_in[4]` / `[5]` / `[6]`, tree enable `dig_in[7]`);
- its four bias voltages `vbp vbn vbpc vbnc` onto `analog_bus2` through transmission gates (`dig_in[8..11]`);
- the harness `ibias1` onto `analog_bus3` (`dig_in[12]`) for comparison;
- all enables fail-safe like stage A (dig_in AND enable AND slot vdd_1v2 present).
Ports, `slot_7.lib` and `slot_7.vh` stay the same. `main` is updated only after DRC, LVS and the harness flow pass.

## 2026-11-06 — stage A delivered on `main`

`slot_7.gds` = test platform stage A: Oguey–Aebischer core and Banba bandgap core, each ~5 uA sourced, through
transmission gates onto `analog_bus0` / `analog_bus1` (enables `dig_in[0..3]`, fail-safe; read-back `dig_out[3:0]`).
Checks: KLayout DRC 0, magic + netgen LVS match (104 devices), PVT simulation (5 corners, -40 / 27 / 125 C),
harness fork `tatzelbrumm/sg13cmos5l_ocd_chipalooza` branch `custom-pad-test`: projects, projects-gds, gds-prefill
exit 0, net check of the pre-fill top: all 36 used and 27 unused slot pins OK.
Measurement procedure (SPI register writes): design repo `docs/slot7_testplatform/PLAN.md` section 5; results:
`docs/slot7_testplatform/SUMMARY.md`.
