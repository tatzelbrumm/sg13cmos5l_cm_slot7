# Slot 7 progress (for the harness owner)

What the harness reads from this repository: `final/gds/slot_7.gds` (top cell `slot_7`) and the custom pad cells in
`pads/<cell>/` (manifest `pads/pads.txt`). Everything else is documentation. The design work happens in
[`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single)
(macro `macros/slot7_testplatform/`, records `docs/slot7_testplatform/`: PLAN.md, RUNLOG.md, SUMMARY.md).
This file is updated with each step; newest entry first.

## 2026-11-06T19:08Z — stage B through the harness flow (fork `tatzelbrumm/sg13cmos5l_ocd_chipalooza`, branch `claude/c5-testplatform-test`)

With `s7_version` = this repository's `claude/c5-testplatform` c0726799: `make projects-clean / projects / projects-gds
SLOTS=7` and `make gds-prefill` all exit 0; `slot_7` in the pre-fill top equals this `slot_7.gds` (XOR empty); net check
of the pre-fill top (`docs/custom_pads/tools/netcheck_slot7_platform.py --stage b`): all 49 used and 14 unused slot pins
OK. Stage B is ready for `main`; the merge is the slot owner's decision.

## 2026-11-06T19:03Z — stage B built and checked in the design repository (branch `claude/c5-testplatform`)

`final/gds/slot_7.gds` on branch `claude/c5-testplatform` now contains stage B (not yet on `main`):
- new cells: `tp_en_ctrl_b` (9 fail-safe enables) and `bias_tree_noab_pd` (the S2D pad's tree), both KLayout DRC 0 and
  magic + netgen LVS "match uniquely"; 8 more transmission gates (`xgate`);
- `slot_7.gds`: KLayout DRC (feol + beol) 0; LVS "netlists match uniquely", 190 devices, 120 nets (the same three known
  port notes as stage A: stand-in pad-stub joins, frame `vss_1v2` strip);
- simulation (5 corners, -40 / 27 / 125 C, 3.0 / 3.3 / 3.6 V): the tree runs from each reference; on `analog_bus2`,
  vbn 0.82 .. 0.99 V, vbp 1.49 .. 2.44 V; `ibias1` through the slot 5.000 uA, off <= 29 pA; fail-safe holds (vdd_1v2
  gated off, enable low); stage A unchanged (its tests repeated on the extracted stage-B layout);
- the stage-A state is kept on branch `claude/slot7-stage-a` of this repository (and of the design and harness repos).
Next: harness flow with this `slot_7.gds` on the fork, net check, then `main`.

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
