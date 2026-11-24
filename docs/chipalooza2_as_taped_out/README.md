<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7: custom S2D / D2S pad pair with a bandgap-referenced replica bias (as taped out, November 2026)

> **Where this set comes from.** Copied on 2026-11-23 from
> [`tatzelbrumm/sg13cmos5l_ocd_chipalooza`](https://github.com/tatzelbrumm/sg13cmos5l_ocd_chipalooza/tree/da4557a5b2ac84c6e05c5a683a019df4895b67e9/sudelbuecher/slots/slot_7),
> branch `sudel_buecher` (commit `da4557a5b2ac84c6e05c5a683a019df4895b67e9`), directory `sudelbuecher/slots/slot_7/`
> (README.md, glue_logic.md, test_platforms.md, characterization_candidates.md, log.md, datasheets/ with tools/, pix/).
> It describes slot 7 **as taped out**, i.e. this repository at commit `158afc5afab0056bd6d216a4db3833e34a364949`
> (`s7_version` in `config.txt` of the harness branch `tapeout_nov_2026`).
>
> **The Oguey–Aebischer core `oa_core_pd` is not in the taped-out slot 7.** It was built and verified (cloud sessions C0 and
> C1: DRC, LVS, PEX; section 3) and used in the stage A / B test platforms ([test_platforms.md](test_platforms.md)), but the
> taped-out `final/gds/slot_7.gds` contains only the bandgap core `bg_core_pd` (section 4.3; re-checked on 2026-11-23 with
> KLayout 0.30.12: none of the 88 cells of `final/gds/slot_7.gds` is `oa_core_pd` or one of its own sub-cells `oa_svpg`, `oa_pcas_c`, `oa_pmir_c`,
> `oa_mcs_c`, `oa_ms1`, `oa_n10`, as listed in `macros/oa_core_pd/layout/gds/oa_core_pd.gds`). `macros/oa_core_pd/`
> in this repository is a copy of the macro that no harness script reads; the statement in this repository's top-level
> README that both cores are placed in `slot_7.gds` describes the test platform, not `158afc5`.
>
> Adaptations made while copying (nothing else was changed): links to files of this repository that are unchanged since `158afc5`
> are relative (`../FOR_TIM.md`, `../slot_7.md`, `../PROGRESS.md`, `../slot_7.png`, `../../netlist/slot_7.spice`,
> `../../art/tughra_art.gds`); links to other repositories stay absolute with commits (the harness's `magic/custom_io/` now
> points to the tapeout commit `7eeb3cb`); "in this session" / "checked in this session" became "on 2026-11-22" / "checked on
> 2026-11-22" (the date of that work); the link from `datasheets/slot_7_system.md` to `glue_logic.md` was corrected to
> `../glue_logic.md`; the chat-log link in `log.md` was replaced by a path citation (chat logs are not copied); in
> `characterization_candidates.md` the cross-reference "README's section 6" was corrected to section 2.5. The measurement plan for
> the fabricated chip is [TEST_PLAN.md](TEST_PLAN.md); sign-off reports are in [`../../signoff/`](../../signoff/README.md).

Designer: Christoph Maier. Slot 7 turns a single-ended pad signal into a differential pair and back: two custom analog pads, a bandgap, a
bias distribution and replica-bias block that give the pads their reference currents and common-mode / reference voltages, and a small
3.3 V control block with fail-safe enables. Sections 2 and 3 are the electrical documentation and the state of readiness of each block (the glue logic, which is as important as the circuits, has its own page: [glue_logic.md](glue_logic.md));
the pins, layout hierarchy and verification follow; the tughra art is an aside at the end. Running log of how this page was assembled:
[log.md](log.md). Data for characterizing the blocks: [characterization_candidates.md](characterization_candidates.md); first data sheets built from the existing characterization: [datasheets/](datasheets/README.md); the earlier test platforms (not taped out): [test_platforms.md](test_platforms.md).

## 1. Which version was taped out

| source | slot 7 commit |
|---|---|
| `config.txt` `s7_version` on `tapeout_nov_2026` | `158afc5afab0056bd6d216a4db3833e34a364949` |
| submodule gitlink at the tapeout commit `7eeb3cb` ("as taped out to IHP on November 9, 2026") | `158afc5` |
| submodule gitlink at the branch tip (commit `055993f`, after the tapeout commit, 2026-11-09 18:04 +0100) | `c072679`, an older state (the stage B test platform) |

**Taped out is `158afc5`** ([`tatzelbrumm/sg13cmos5l_cm_slot7`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/tree/158afc5afab0056bd6d216a4db3833e34a364949):
"slot_7 v3 + tughra art"). The gitlink at the tip of `tapeout_nov_2026` points to a different, older commit; a
`git submodule update` there checks out the stage B test platform, not the taped-out slot.

*Checked on 2026-11-22, from the chip GDS `gds/MPC9639.gds.gz` on `tapeout_nov_2026`, KLayout 0.30:*

- the cell `slot_7` of the chip has the bounding box 0,0 to 537.15 × 273 µm and, flattened and merged per layer, **is identical
  (XOR 0 on every layer) to `final/gds/slot_7.gds` of `158afc5`**; against `final/gds/slot_7.gds` of `c072679` it differs on 34 layers;
- its children are the six blocks of section 4, named with a `YX_` prefix in the chip (the harness prefixes cells on import);
- the cells `sg13cmos5l_IOPadSingle2Diff` and `sg13cmos5l_IOPadDiff2Single` of the chip equal the pad GDS of `158afc5`
  (XOR 0 on every layer, same bounding box -0.62,0 to 80.62 × 180 µm).

## 2. Electrical function

### 2.1 Signal and current flow

![Slot 7 signal and current flow: harness controls into s7_ctrl; bg_core_pd, bias_dist_pd and pad_ref_rb supply the pads' reference currents and vcm / vref; S2D pad, switch matrix and D2S pad form the signal path; analog_bus0..3 taps](pix/slot7_signal_flow.svg)

*Figure: signal and current flow of slot 7 as taped out (`158afc5`). Connections from the netlist as described in [glue_logic.md](glue_logic.md) (switch matrix §4, same-net joins and `bias_dist_pd` configuration §5). Generated by [`pix/make_signal_flow.py`](pix/make_signal_flow.py) (SVG; [PNG](pix/slot7_signal_flow.png)).*

<details><summary>The same as plain text</summary>

```
harness: enable, dig_in[0..5]            vdd_3v3 / vss_3v3 (gated)        vdd_1v2 (only dig_out pull-downs)
              |                                   |
          s7_ctrl  --- fail-safe enables, mode decode, switch matrix (3.3 V logic) ---------------+
              |                                                                                     |
        bg_core_pd (Banba bandgap, ~5 uA sourced) --> bias_dist_pd (1:1 copies, switched) --+--> pad_ref_rb: one bias tree -> vcm_rb, vref_s2d_rb
                                                                                            |         vcm  (S2D vcm = D2S vref)    ~1.26 V
                                                                                            |         vref (S2D vref)              ~0.49 V
                                                                                            +--> iref of each pad's own bias tree (s7_an_0_iref, s7_an_1_iref)
 pad s7_an[0] --> S2D pad: outp - outn = 2 (pad - vref), (outp+outn)/2 = vcm ----+ loop direct or crossed
                                                                                  v
 pad s7_an[1] <-- D2S pad: pad - vref = (vinp - vinn)/2  <------------------------+  (or fed from analog_bus0/1)
```

</details>

Default function (enable = 1): the pad signal at `s7_an[0]` is reproduced at `s7_an[1]`, shifted from the S2D `vref` (~0.49 V) to the D2S `vref`
(= `vcm`, ~1.26 V): D2S out = `vcm` + (S2D in − `vref`), for an input of 0 … 1 V. Swap crosses the differential pair (inverts about `vcm`).
The point of the slot is to show the two pad buffers working together with on-slot references and fail-safe enables.

### 2.2 Supplies, enable and fail-safe

- **Supplies:** `vdd_3v3` / `vss_3v3` for everything; `vdd_1v2` only gates the 12 pull-downs of `dig_out[11:0]` (`s7_doutpd`, NMOS 0.5 µm / 0.45 µm hv, held low).
  The slot works with only `vdd_3v3` switched on: the enables do not need a 1.2 V presence.
- **Enable:** harness `enable` = 1 turns the slot on in the default mode. Inside, `s7_ctrl` makes the 3.3 V enables (`en_3v3`, `en_3v3_b`) with fail-safe level
  shifters (`efs_ls_core`, 7 instances) and 3.3 V static logic (`nand2_hv` ×13, `inv_hv` ×12, `tg_hv` transmission gates ×10); all devices are 1 µm / 0.45 µm hv
  (`macros/hv_logic`: the IO and standard-cell libraries have only 1.2 V logic).
- **Disabled:** every reference output is high-Z, every distribution transmission gate open, tree nodes pulled to the rails; the slot draws leakage only, and the
  pads draw ≤ 67 nA at 125 °C from the pad ring while the slot's supplies are off (designer's simulation, `en_ctrl_3v3` starvation test: S2D ≤ 0.4 nA at −40 / 27 °C,
  ≤ 25 nA at 125 °C; D2S ≤ 4.3 nA / ≤ 67 nA; mostly output and ESD-device leakage, nearly independent of the enable levels).
- **Enabled current (tt 27 °C, simulation):** slot `vdd_3v3` ≈ 49 µA; pad ring ≈ 365–396 µA, mostly the D2S output stage.

### 2.3 The blocks

| block | electrical function | key design facts (from the delivery repository and the design repository's READMEs) |
|---|---|---|
| `bg_core_pd` | reference-current source for everything: Banba current-mode bandgap, no op amp | pnpMPA and `rhigh`; **sources about 5 µA** out of `iout` into an NMOS input diode; high-Z when `en_3v3` = 0 (so disabled cores may share one node); 47.55 × 50.05 µm; flat over temperature and MOS corners, but follows the `rhigh` corners (about −20 % / +30 %). Power-down transistors `en_3v3` / `en_3v3_b`. Characterized in the `bias_bg_pd` and `bias_sel_pd` suites; the bg extraction has 41 nodes only capacitors touch |
| `bias_dist_pd` | switchable distribution mirror: reference currents in, one 1:1 sourced copy per pad bias tree out | input NMOS diode NI 6 µm / 6 µm → NM → PMOS diode PD 5 µm / 6 µm → outputs PO 5 µm / 6 µm; every input and output behind a transmission gate (`bdp_slice` ×8: nand2_hv + inv_hv + tg_hv); `en_3v3` = 0 opens every gate, TDN pulls `ni` to vss, SVPD pulls `vpd` to vdd; 60.49 × 16.44 µm **Added 2026-11-23:** copy accuracy and mismatch, schematic and extracted ([§5a](#5a-gap-simulations-of-2026-11-23)) |
| `pad_ref_rb` | **replica bias** of the pads' reference voltages: gives `vcm` (S2D `vcm` = D2S `vref`, centre of the linear band) and `vref` (S2D `vref`, about 0.5 V) from one 5 µA reference, one bias tree, one enable, with bypass capacitors | `bias_tree_rb` (TG switch, NI 6/6, NBP 2.4/6 → BP 2/6 → `vbp`, PBNC 2/6 → BNC 1/8 → `vbnc`), `vcm_rb` (top-edge detector, fold-node replica, average, unit-device OTA buffer) and `vref_s2d_rb`; `bypass_rb` capacitors (hv NMOS to vss: vref ≈ 1297 µm²); replica devices track the pads' operating windows over process, temperature and `iovdd` at a current far below a resistive divider's. CACE results 8/8 groups; enable time vcm 0.79–1.81 µs, vref 1.03–2.02 µs, no overshoot; S2D enable kick vcm ≤ 0.112 V, vref ≤ 0.088 V; closed-loop INL S2D ≤ 1.73 mV, D2S ≤ 1.72 mV, round trip ≤ 0.75 mV (schematic, 2026-11-07) |
| `s7_ctrl` (glue logic) | master enable, key and mode decode, switch matrix (10 transmission gates), 3.3 V fail-safe level shifting of `enable` and `dig_in[0..5]` | full description, logic equations and truth table in [glue_logic.md](glue_logic.md); mode controls act only with the key `dig_in[3]` = 1, `dig_in[4]` = 0; `rc` / `ld` / `lx` / `sb` / `bd` select replica-bias connection, loop direct, crossed, S2D → buses, buses → D2S; 71.6 × 38.04 µm |
| `sg13cmos5l_IOPadSingle2Diff` (S2D pad) | buffered single-ended-in, differential-out pad: `outp − outn = 2 (pad − vref)`, `(outp + outn)/2 = vcm` | matched-pair DDA `s2d_mpdda`: four signal units on (`vin`, `vref`), (`vcm`, `vfbp`), (`vfbn`, `vcm`), a folded cascode with the outputs as the only high-impedance nodes, two units as CMFB into a cascoded PMOS diode, two 12 × 12 µm hv NMOS capacitors as load; the gain comes from how the matched units are connected, not from a resistor ratio. Own bias tree fed by `iref`; enable gates `en_3v3` / `en_3v3_b`, outputs tied to `vcm` while disabled; primary ESD: gate-tied clamps with rppd ties, diodes DP1/2, DN1/2; no secondary protection (the buffer input is the pad). Input window: unit gates ≲ `iovdd` − 1.3 V; with `vref` = 0.5 V the pad range is 0 … 1 V |
| `sg13cmos5l_IOPadDiff2Single` (D2S pad) | buffered differential-in, single-ended-out class-AB pad: `pad − vref = (vinp − vinn)/2` | Miller-compensated class-AB driver `d2s_mpdda_pd` (MP-DDA front end, folded cascode, class-AB control) driving the output stage that **is** the pad's clamp frames (OP with replica RP1 and dummy RPD in the P frame; ON with replica RN1 in the N frames); Miller capacitors CMA / CMB (hv PMOS in accumulation, 7.96 × 32.16 µm); own bias tree fed by `iref` (six bias lines), fail-safe enable, primary ESD diodes `DCNDiode` / `DCPDiode`. Headroom limits are at `iovdd` = 3.0 V **Added 2026-11-23:** magic PEX of the taped-out cell and post-layout CACE, 9 groups ([§5a](#5a-gap-simulations-of-2026-11-23)); ESD and latch-up simulation still not done |
| `s7_doutpd` (glue logic) | holds `dig_out[11:0]` low while `vdd_1v2` is on | 12 hv NMOS 0.5 / 0.45 µm, gate on `vdd_1v2`; see [glue_logic.md](glue_logic.md) |

The two pads replace the harness's analog pads `s7_an[0]` and `s7_an[1]`, so their ring pins (`iovdd iovss vdd vss`) and bond pad come from the harness
frame; the slot supplies their core-side pins (section 4).

### 2.4 Modes

`dig_in[0..5]` act only with the key `dig_in[3]` = 1 and `dig_in[4]` = 0; otherwise the default applies.

| `dig_in` | name | effect |
|---|---|---|
| none / no key | default | loop S2D → D2S direct; `analog_bus0/1` disconnected; `vcm` on `analog_bus2`, `vref` on `analog_bus3` |
| `[0]` | swap | loop crossed (polarity flip) |
| `[1]` | mon | S2D `outp` / `outn` → `analog_bus0` / `analog_bus1` (loop stays on; it is 10–30× slower while the bus switches are closed) |
| `[2]` | feed | `analog_bus0/1` → D2S `vinp` / `vinn`, loop off (wins over swap and mon); drive around `vcm` |
| `[5]` | ext | replica bias disconnected; drive `vcm` on `analog_bus2` and the S2D `vref` on `analog_bus3` |

Harness settings (delivery's `docs/FOR_TIM.md`): `proj_sel` = 7; `power_3v3_ena` on (`power_1v2_ena` only for the `dig_out`
pull-downs); `proj_ena` on; first route all `dig_in` registers to constant 0 (0x0D), then set bits through 0x0D / 0x0E;
`analog_ena[k]` (reg 0x51 bits 4…7) for the buses in use.


### 2.5 Expected values

- `vcm` ≈ 1.26 V (1.12–1.37 V over corners), `vref` ≈ 0.49 V (0.44–0.58 V); read with a high-impedance voltmeter.
- Default loop: D2S pad out = `vcm` + (S2D pad in − `vref`); error ≤ 1.3 mV (−40 / 27 °C), ≤ 6.5 mV (125 °C) for pad in 0 … 1 V. Swap: `vcm` − (in − `vref`).
- Current, enabled: slot `vdd_3v3` ≈ 49 µA, pad ring ≈ 365–396 µA (mostly the D2S output stage).
- S2D enable kick through the ext switches (tt, 27 °C): `vcm` +118 / −63 mV, `vref` +85 / −62 mV.

## 3. Readiness of the blocks that were kicked off

How each block was started, and how far it got by the tapeout. ("Pass" in the CACE results quoted below means inside the designer's *working limits*; the design is a proof of concept and had no specification. The observed intervals are in [datasheets/](datasheets/README.md).) "Kicked off" means a launch brief or cloud session recorded in the design repository (`docs/launch/`
on `harness-test`; the `sudelbuecher/cloud_sessions/` briefs and reports and the chat logs on `sudel_buecher`). Readiness is as the blocks' own reports and READMEs state it;
where a README is older than a later report, the later one is used and the stale statement is named. "In the slot" = present in the taped-out `slot_7` (section 4).

| block | kicked off by | readiness at the tapeout | open or stale |
|---|---|---|---|
| `bg_core_pd` | compact layout 2026-10-28; cloud session **C1** (30–31 Oct: DRC, LVS, PEX, mismatch in the bias verification) | in the slot. Layout, DRC clean, LVS match (29 devices / 21 nets), PEX 1/2/3 and KLayout-PEX with all ports connected (C1); no CACE suite of its own (characterized inside `bias_bg_pd` / `bias_sel_pd`). PEX does not move dc bias currents (≤ 0.02 %), but raises supply sensitivity at 100 kHz – 1 MHz (up to ×2.6) and slows settling by 40–57 % | its README still says "not yet checked with IHP's own decks" (older than C1). No mismatch model for pnpMPA. At ss / −40 °C the slot's swap and mon mode simulations stall at the bandgap's start-up node in the solver |
| `oa_core_pd` (Oguey–Aebischer) | cloud sessions **C0** (30 Oct: DRC, LVS, PEX) and **C1** | built and verified (DRC clean, LVS 28 devices / 22 nets, PEX) but **not in the taped-out slot**; used only in the test platform | the delivery repository still carries the macro and a README that says both cores are placed |
| `bias_dist_pd` | session **C4** (layout agent D, round 2, 2026-11-08) | in the slot. Layout 60.49 × 16.44 µm, KLayout DRC clean (maximal deck with latch-up 0), LVS against the flat CDL OK; schematic back-annotated from the layout; truth-table simulation only (2026-11-07) | no CACE suite; number of inputs was still "to be decided" in its README **Added 2026-11-23:** copy accuracy and mismatch ([§5a](#5a-gap-simulations-of-2026-11-23)) |
| `pad_ref_rb` (with `vcm_rb`, `vref_s2d_rb`, `bias_tree_rb`, `bypass_rb`) | session **C4** (brief `docs/launch/replica_bias_TASK.md`; 6–8 Nov; layout agents P, P3, N, F) | in the slot. Schematic CACE 8/8 groups pass (2026-11-07); layout v2 73.8 × 76.26 µm (M1/M2 only), LVS OK; used extracted in the slot's tier-1 simulation | `vcm_rb` / `vref_s2d_rb` READMEs say "Layout: not started" — superseded by `pad_ref_rb`'s layout. Monte Carlo and a PEX CACE suite not confirmed **Added 2026-11-23:** PEX (C-coupled) CACE and a 100-run mismatch Monte Carlo with per-run data ([§5a](#5a-gap-simulations-of-2026-11-23)) |
| `en_ctrl_3v3` (fail-safe enable; `efs_ls_core`) | session **C4**, v2 of 2026-11-08 (agent E) | its level-shifter core is in `s7_ctrl`; CACE 128/128 runs pass, layout DRC clean, LVS match | Monte Carlo and PEX not done |
| `s7_ctrl`, `s7_doutpd`, static ties (the glue; [glue_logic.md](glue_logic.md)) | session **C4** (slot hook-up on 2026-11-08, from the designer's mode specification; layout agent C) | in the slot. `s7_ctrl` layout DRC / LVS clean; whole slot DRC, LVS deep match (497 devices), magic + netgen match with one expected port error; modes simulated with extracted pads: all pass at tt 27 °C and ff 125 °C | built and verified within one day; `s7_doutpd` has no stand-alone verification; no PEX or fill of the whole slot; at ss −40 °C the manual modes did not converge in DC and swap / mon stall in transient (see glue_logic.md §7); no glue-level Monte Carlo |
| `sg13cmos5l_IOPadDiff2Single` (D2S pad) | cloud session **C2** (31 Oct – 3 Nov; bottom-up by agents: capacitors K, primitives P / N rebuilt as P2 / N2, floorplan F2, assembly) | taped out. Layout, backannotation, KLayout DRC clean, KLayout LVS pass, magic LVS fails only on the `vss` pin (substrate merge, accepted 2026-11-03); tier-1 simulation uses the extracted pad | the pad README lists PEX and post-layout CACE as not done and says the committed CACE results predate the layout; ESD and latch-up simulation not done **Added 2026-11-23:** PEX and post-layout CACE now done ([§5a](#5a-gap-simulations-of-2026-11-23)) |
| `sg13cmos5l_IOPadSingle2Diff` (S2D pad) | cloud session **C3** (3 Nov) | taped out. Layout, DRC clean, KLayout LVS pass, magic LVS fails only on `vss` (as D2S); magic PEX and post-layout CACE: 414/414 runs pass on both schematic and extracted views (2026-11-05) | its `FILL_IN.md` has open points |
| test platform stage A / B ([test_platforms.md](test_platforms.md); OA and BG cores, bias tree, transmission gates to `analog_bus0..3`) | cloud session **C5** (6–7 Nov; brief `docs/launch/slot7_testplatform_TASK.md`) | finished and delivered (DRC 0, LVS match, PVT simulation, harness flow on the fork), then replaced by the slot circuit on 8 Nov; **not in the taped-out slot** | the tip of `tapeout_nov_2026` still points its slot 7 gitlink at stage B (section 1) |
| delivery repository and harness test | tasks `docs/launch/slot7_delivery_repo_TASK.md`, `custom_pad_harness_test_TASK.md` | `tatzelbrumm/sg13cmos5l_cm_slot7` created; harness test of the custom-pad flow on the fork | the harness flow with the final v3 slot circuit on the delivery's branch is stated as not yet run; harness README: slot 7 wrapper rebuilt by hand ("automation ... not yet completely automated") |

Sources: the briefs and reports named above; `macros/*/README.md` of the design repository at `9052bd35` and `91a7da8b`; the slot 7 delivery repository at `158afc5`. I read
the C0 / C1 reports and the READMEs listed; I did **not** read the C2 / C3 / C4 chat logs in full, so their entries (agents, dates) are taken from the chatlog index of the design repository.

## 4. Physical interface and layout hierarchy

### 4.1 Top level

`slot_7` (537.15 × 273 µm) sits in the chip as `slot7_wrapper` in `chipalooza_frame` at (1363.85, 2153.95) µm; the origin of `slot_7` itself is at (1379.95, 2170.05) µm in chip coordinates (checked on 2026-11-22). The harness reads
`final/gds/slot_7.gds` (top cell `slot_7`) and the two custom pad cells in `pads/`. Frame and all 63 pin names, layers and
positions are the harness's; the stand-in's Metal4 stub pins were removed. LEF, `.lib` and `.vh` were not changed (`.lib` is a
pin-less stub).

- **Supplies:** `vdd_3v3` / `vss_3v3`; `vdd_1v2` only for the `dig_out` pull-downs. The slot works with only `vdd_3v3`
  switched on.
- **Enable:** `enable` = 1 selects the default mode: bandgap reference, replica bias on, loop S2D → D2S direct, `vcm` on
  `analog_bus2` and `vref` on `analog_bus3`.
- **Fail-safe:** disabled, the slot draws leakage only; with the slot's supplies off, the pads draw leakage only (≤ 67 nA at
  125 °C, simulation by the designer).
- **`dig_out[11:0]`:** held low by 12 NMOS pull-downs (`s7_doutpd`, gate on `vdd_1v2`).

Block diagram, from `docs/slot_7.md` of the delivery repository: harness `enable` and `dig_in[0..5]` → `s7_ctrl` (master enable,
mode decode, switch matrix) → bandgap core `bg_core_pd` → `bias_dist_pd` → `pad_ref_rb` (replica bias) and both custom pads;
S2D pad → D2S pad loop direct or swapped; S2D outputs on `analog_bus0/1` or D2S fed from them; `vcm` / `vref` on
`analog_bus2/3`. Picture: [`docs/slot_7.png`](../slot_7.png).

### 4.2 Pads

Two of slot 7's analog pads are replaced by custom I/O pad cells (`config.txt`):

```
s7_an[0]:  sg13cmos5l_IOPadSingle2Diff  s7_an_0
s7_an[1]:  sg13cmos5l_IOPadDiff2Single  s7_an_1
```

The remaining dedicated pins of slot 7 follow the harness defaults (slot table: 2 dedicated pins). Both cells are standalone cells
80 µm wide and 180 µm high with ring pins `iovdd iovss vdd vss` and the bond pad `pad`. In the chip they are instances in
`sg13cmos5l_padframe` (at (2080, 2260) µm for `IOPadSingle2Diff` and (2080, 2370) µm for `IOPadDiff2Single`, as KLayout reports them).
The harness imports them through `scripts/setup_custom.sh` (views looked for in `pads/<name>/`); the magic views are in
[`magic/custom_io/`](https://github.com/tatzelbrumm/sg13cmos5l_ocd_chipalooza/tree/7eeb3cb41108c5de7348050f6f69d839310f27e4/magic/custom_io) on the tapeout branch.

| cell | replaces | core-side pins, in order along the core edge | role |
|---|---|---|---|
| `sg13cmos5l_IOPadSingle2Diff` (S2D) | `s7_an[0]` | `vref outp outn vcm en_3v3 en_3v3_b iref` | pad input → differential `outp` / `outn` around `vcm` |
| `sg13cmos5l_IOPadDiff2Single` (D2S) | `s7_an[1]` | `vinp vinn vref iref en_3v3_b en_3v3` | differential `vinp` / `vinn` → pad output |

Pad-side nets on the slot, all Metal3 at the right edge of the slot (x = 535.050 … 536.450 µm, slot-local; origin lower left):

| net | pin | y0 (µm) | y1 (µm) | | net | pin | y0 (µm) | y1 (µm) |
|---|---|---|---|---|---|---|---|---|
| `s7_an_0_vref` | S2D `vref` | 112.115 | 112.405 | | `s7_an_1_vinp` | D2S `vinp` | 222.115 | 222.405 |
| `s7_an_0_outp` | S2D `outp` | 123.725 | 124.015 | | `s7_an_1_vinn` | D2S `vinn` | 222.655 | 222.945 |
| `s7_an_0_outn` | S2D `outn` | 129.825 | 130.115 | | `s7_an_1_vref` | D2S `vref` | 223.195 | 223.485 |
| `s7_an_0_vcm` | S2D `vcm` | 135.875 | 136.165 | | `s7_an_1_iref` | D2S `iref` | 260.455 | 260.745 |
| `s7_an_0_en_3v3` | S2D `en_3v3` | 142.505 | 142.795 | | `s7_an_1_en_3v3_b` | D2S `en_3v3_b` | 260.995 | 261.285 |
| `s7_an_0_en_3v3_b` | S2D `en_3v3_b` | 153.695 | 153.985 | | `s7_an_1_en_3v3` | D2S `en_3v3` | 261.535 | 261.825 |
| `s7_an_0_iref` | S2D `iref` | 159.365 | 159.655 | | | | | |

(The table is the delivery repository's pin table, copied from its README; I did not re-measure it. The harness side: in the slot the
nets `s7_an_0_vcm`, `s7_an_1_vref` and `analog_bus2` are one net, as the CDL port name `analog_bus2,s7_an_0_vcm,s7_an_1_vref` shows.)

**Known LVS note on the pads (quoted from the delivery repository):** the cell's `vss` p+ tie and the `iovss` ties share the
p-substrate, so `vss` and `iovss` are one net in the extracted layout, and magic + netgen end with "Top level cell failed pin
matching" on `vss`; accepted by the designer on 2026-11-03, everything else matches. IHP's own `IOPadAnalog` shows the same merge.

**Caveat from the harness README (tapeout branch, "Caveats"):** "Slot 7: The original analog pin in metal3 needed to be removed.
Automation rebuilding the slot wrapper with the custom pad pins has not yet been completely automated." The slot wrapper
`magic/slot7_wrapper.mag` was hand-preserved for the build; LVS is never run on the populated chip.

### 4.3 Hierarchy of `slot_7` (from `final/gds/slot_7.gds` of `158afc5`, read on 2026-11-22)

88 cells in all. Direct children of `slot_7`, each instantiated once; placement from `docs/slot_7.md`:

| block | size (µm) | placement (µm) | function | sub-cells (instances) |
|---|---|---|---|---|
| `bg_core_pd` | 47.55 × 50.05 | (330, 152.7) | Banba current-mode bandgap (pnpMPA, rhigh, no op amp); sources about 5 µA; high-Z when disabled | `bg_svpg bg_pmir_pcas_c bg_res_c bg_pnp_c bg_ms1 bg_n4` (1 each) |
| `bias_dist_pd` | 60.49 × 16.44 | (385, 183.1) | switchable distribution mirror: reference current in, one 1:1 sourced copy per pad bias tree out; each input and output switchable | `bdp_slice` ×8, `bdp_tdn bdp_svpd bdp_mirror_n bdp_mirror_p`, seven `bdp_fill*` |
| `pad_ref_rb` | 73.8 × 76.26 | (450, 150) | replica bias: one bias tree from one 5 µA reference gives `vcm` (S2D `vcm` = D2S `vref`) and `vref` (S2D `vref`) | `prb_frame_f prb_capr prb_capm prb_capt prb_capv rb_casc rb_tree_n rb_tree_p rb_tails rb_tubs rb_avg rb_mirror rb_cload` |
| `s7_ctrl` | 71.6 × 38.04 | (452, 60) | master enable, mode decode, switch matrix, fail-safe level shifting (3.3 V only) | `efs_ls_core` ×7, `bdp_nand2_hv` ×13, `bdp_inv_hv` ×12, `bdp_tg_hv` ×10 |
| `s7_doutpd` | 24.67 × 3.85 | (8, 60) | pull-downs holding `dig_out[11:0]` low | `dop_nmosHV_w0p5_l0p45` ×12 |
| `tughra_art` | 158.05 × 90.0 | (88.5, 141.3) | decorative art: floating GatPoly and Metal1–4 with no-fill markers; no device, no pin | — |

Notes:

- The art was added after v3 by `art/add_art.py`; see the aside at the end.
- **The Oguey–Aebischer core `oa_core_pd` is not in the taped-out slot.** The delivery repository still carries `macros/oa_core_pd/` (and its README
  says both cores are placed in `slot_7.gds`, which was true of the test platform); the hierarchy of the taped-out `slot_7.gds` has
  the bandgap core only. `macros/bg_core_pd/` and `macros/oa_core_pd/` in the delivery are copies of the macros, not read by the harness.
- Routing: M1/M2 stubs, M3 horizontal, M4 vertical, TopMetal1 straps for `vdd_3v3` / `vss_3v3`. Over the analog blocks only `en`,
  `en_b` and `s7_an_0_iref` cross `pad_ref_rb` (Metal3, DC), only the supply straps cross `bias_dist_pd` (designer's build log).

## 5. Verification state

By the designer, for `158afc5` (KLayout 0.30.12, PDK `ihp-sg13cmos5l`; from the delivery's `README.md` and `docs/`):

| check | result |
|---|---|
| `run_drc.py --no_density` | no violations |
| maximal deck with `-rd latchUpRules=true` | 0 |
| density | the same 7 minimum-density rules as without the art (AFil.g, GFil.g, M1–M4.j, TM1.c): unfilled slot, filled at chip level |
| LVS `run_lvs.py --run_mode=deep --disable_tap_extraction` against `netlist/slot_7.cdl` | netlists match, strict ports, 0 port errors, 497 devices |
| magic + netgen (`netlist/netgen_check.sh`) | 5 subcircuits match uniquely; top: one port error, `vss_1v2_uq0` (the frame's second `vss_1v2` strip, unconnected inside the slot, joined by the harness) |
| mode simulations | tt and ff pass all 8 modes; at ss / −40 °C default, feed and ext pass; **swap and mon stall at the bandgap's start-up node in the solver** (open item) |

Not done, as stated by the designer: PEX of the whole slot; fill; the harness flow with these pads and this `slot_7.gds` on the delivery's branch
(the stage B flow, with other geometry, was run on the fork). Chip level: the harness README states LVS is never run on the populated chip.
Whether the whole-chip DRC of `MPC9639` (run directories in `validate/`) is clean for slot 7 was **not** checked here.

## 5a. Gap simulations of 2026-11-23

Simulations made after the tapeout to close gaps of the characterization (IHP sg13cmos5l, ngspice-47 with the IHP OSDI models,
CACE 2.11.0, magic / netgen; reproducible with the `run.sh` of each folder from this repository plus the design-repository commits it names).
Each folder's `README.md` and `results.md` give conditions, versions and what the run does **not** show.

| folder | block | result |
|---|---|---|
| [`../../verification/c2_gaps/d2s_pex/`](../../verification/c2_gaps/d2s_pex/) | D2S pad, magic C-coupled PEX of `pads/sg13cmos5l_IOPadDiff2Single` (taped-out GDS) | netgen: circuits match uniquely (76 / 76 devices, 36 / 36 nets; `vss` tied to `iovss` as for S2D). 9 CACE groups, 127 of 127 runs, all inside the CACE working limits. Against the schematic: bandwidth −12.9 % worst (median 2.015 → 1.774 MHz), slew rate −13 %, enable time up to +94 % (median 0.854 → 1.349 µs), quiescent current +5 %, INL max 7.40 → 7.50 mV; gain, PSRR, THD, swing within about 2 %. The extracted netlist needs the ngspice option `rshunt` = 1e12 to converge (documented there). Not done: full-RC extraction, mismatch, groups dc_3v0 / dc_sel / dc_sel3 / dc_ibias / ac_1nF |
| [`../../verification/c2_gaps/replica_bias/`](../../verification/c2_gaps/replica_bias/) | `pad_ref_rb`, `bias_dist_pd` | cells cut from `final/gds/slot_7.gds` equal the design-commit macros (XOR); netgen match. `pad_ref_rb` PEX equals schematic in DC to 0.1 mV (`vcm` 1.242 … 1.395 V, `vref` 0.436 … 0.596 V over −40 … 125 °C). Mismatch (100 runs, tt 27 °C): `vcm` σ 5.4 mV, `vref` σ 3.8 mV. `bias_dist_pd`: copy error +0.49 … +1.56 % (5 corners × 3 temperatures, 0.5 … 2.5 V), mismatch σ 1.0 … 1.2 % per output, off leakage ≤ 145 pA. Not done: AC / transient on PEX, full-RC extraction |
| [`../../verification/c2_gaps/slot_modes_bg/`](../../verification/c2_gaps/slot_modes_bg/) | slot modes at ss / −40 °C, `bg_core_pd` alone | **The ss / −40 °C failures of swap, mon, feed, ext are a simulator artefact, not a start-up problem:** the designer's run reproduces them; ngspice fails in the pads' antenna diodes, not at a bandgap node (a `.nodeset` of the bandgap fixes only mon); a power-up transient from 0 V settles in all 8 modes at ss / −40 °C / 3.0 V (bandgap node at 90 % 0.80 … 0.83 µs after enable; `vcm` 1.115 V, `vref` 0.447 V; errors 0.24 … 1.43 mV, ext 4.92 mV). `bg_core_pd` alone: no second stable state found; 1 µs and 1 ms supply ramps start at all corners; current into 0.7 V 3.829 … 6.369 µA over 135 points (typical 4.958 µA), set by the resistor corner (−21 % / +28 %), MOS corners ≤ 0.31 %, supply ≤ 0.73 %/V. Still open: several other mode × corner points abort in the simulator during the supply ramp or enable edge (tt / sf −40 °C, ss 125 °C swap), not run to a result; the converted pad netlists pass `a=` / `p=` to `dpantenna`, which expects `l` / `w`, so those diodes are simulated at default size (for the designer) |

## 6. Files

Delivery repository [`tatzelbrumm/sg13cmos5l_cm_slot7`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/tree/158afc5afab0056bd6d216a4db3833e34a364949) at the taped-out commit:

- [`README.md`](https://github.com/tatzelbrumm/sg13cmos5l_cm_slot7/blob/158afc5afab0056bd6d216a4db3833e34a364949/README.md): provenance table with sha256 of every file
- [`docs/FOR_TIM.md`](../FOR_TIM.md): notes for the harness owner
- [`docs/slot_7.md`](../slot_7.md): modes, files, LVS netlists
- [`docs/PROGRESS.md`](../PROGRESS.md): dated progress log
- `final/gds/slot_7.gds`, `final/lef/slot_7.lef`, `final/lib/slot_7.lib`, `final/vh/slot_7.vh`, `pads/pads.txt`, `pads/<cell>/<cell>.{gds,spice}`
- `netlist/slot_7.cdl`, `netlist/slot_7.spice`, `netlist/slot_7_netgen.spice`, `netlist/netgen_check.sh`; `art/`

Design repository [`tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single), the delivery cites
branch `claude/c4-replica-bias` at `9052bd35` (v3), `toplevel` at `91a7da8b` (pads) and `a45cbb55` (art): macro `macros/slot_7/`, concept and
tier-1 simulation in `docs/slot7_hookup/` (`CONCEPT.md`, `tier1/results.txt`).

*Sources of this page: the delivery repository at `158afc5`; `config.txt`, `README`, `.gitmodules` and `gds/MPC9639.gds.gz` of `tapeout_nov_2026`;
design repository file lists at the commits above. Statements marked "checked on 2026-11-22" were produced by the commands recorded in
[log.md](log.md).*
## 7. Aside: the tughra

The cell `tughra_art` is a calligraphic tughra drawn in metal and polysilicon on the otherwise empty band between the TopMetal1 straps
of the slot: a deliberate piece of die art, not a circuit. It has no device and no pin, and is not connected to anything.

![tughra_art as it is in the taped-out chip](pix/tughra_art_in_MPC9639.png)

*Figure: the polygons of `tughra_art` read from the chip GDS `MPC9639.gds.gz` (cell `YX_tughra_art` inside `slot_7`), drawn per layer in slot-local
coordinates. Made on 2026-11-22 with KLayout and matplotlib from the chip data, not taken from the design repository's preview.*

| item | value |
|---|---|
| cell | `tughra_art`, 158.05 × 90.0 µm; in the chip `YX_tughra_art`, once, inside `slot_7` |
| placement | (88.5, 141.3) µm in the slot; in the chip the slot origin is at (1379.95, 2170.05) µm (no rotation, no mirror), so the art is at about (1468.45, 2311.35) µm |
| layers (art) | GatPoly 2 polygons 74.2 µm²; Metal1 18 / 544.5 µm²; Metal2 7 / 272.1 µm²; Metal3 12 / 484.1 µm²; Metal4 13 / 478.4 µm² (areas read from the chip on 2026-11-22; they equal the design repository's `verify_report.md`) |
| no-fill markers | the seven `.nofill` layers (Activ, GatPoly, Metal1–4, TopMetal1; datatype 23) carry one identical box each, 85.5, 141.0 to 243.55, 231.0 µm in slot coordinates (chip: 1465.45, 2311.05 to 1623.5, 2401.05 µm) |
| filler | *checked on 2026-11-22:* inside that box the chip has **0 µm² of filler** (datatype 22) on GatPoly and Metal1–4, and the drawn areas inside the box equal the art's own areas: the art reached the tape-out unchanged and unfilled |
| source | the design repository's `art/` (`toplevel` at `a45cbb55`, "art rev 4"): `art/source/tughra_source.webp` (the picture), `build_art.py`, `verify_art.py`, `verify_report.md`, `fill_test.md`; the cell as delivered: [`art/tughra_art.gds`](../../art/tughra_art.gds) in the slot 7 repository |
| design-side checks (quoted) | XOR of slot_7 with the art removed against the original: 0 on all 39 layer/datatypes; LVS deep before and after: match, extracted netlists identical; no rule newly violated by the art in DRC with density and antenna on (the 7 density rules AFil.g, GFil.g, M1–M4.j, TM1.c are violated with and without it: unfilled slot); closest approach to existing shapes on its own layer: 36.6 µm on Metal3, more than 60 µm on the others; the PDK filler script keeps out of the marker box (filler test) |
| layers not used | no TopMetal1 art. *Checked on 2026-11-22:* the slot's TopMetal1 (4 merged polygons, the supply straps) has 0 µm² inside the marker box, so the box is a clear area of the TopMetal1 straps |

The art is why `slot_7.gds` differs from v3 (`7394d092…`) by one instance; `art/check_art_only.py` in the delivery proves it (86 sub-cells and slot_7's own shapes
and labels identical; flat XOR of the result against v3 + art = 0 on every layer, and 0 against the design repository's `art/slot7_with_art.gds`).

