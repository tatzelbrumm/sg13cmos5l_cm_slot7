<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 test benches (xschem renders)

SVG exports of the xschem test benches of the design repository
[tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single)
that characterize the taped-out slot 7 cells: the CACE templates (`verification/cace/templates/`) and the stand-alone
xschem benches (`testbenches/xschem/`). Rendered exactly like the circuit sheets in [`..`](../README.md).

- **P** = [`91a7da8`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/91a7da8b67ac56a26c605501146667a1fde28c32) (`91a7da8b67ac56a26c605501146667a1fde28c32`): the custom pads
- **S** = [`9052bd3`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/9052bd35928c6d40344e8e686c9abbe736bfadb9) (`9052bd35928c6d40344e8e686c9abbe736bfadb9`): `slot_7` and the blocks it places

File names are `<cell>__<bench>.svg`, `<cell>` being the cell under test. Source paths are relative to `macros/`.

**CACE templates are shown as they are in the repository, placeholders included.** Every `CACE{vdd}`,
`CACE{corner_mos}`, `CACE{temp}`, `CACE{DUT_path}`, `CACE{filename}_CACE{N}.data`, `CACE[<expression>]` … is
what CACE substitutes per run from the conditions of the parameter group (CACE 5.2 syntax: `CACE{name=default}`
carries the value used when the group does not sweep it). They are not netlists that run in ngspice as drawn; the
pictures show the sheets one would open and edit. In every template the circuit is the drawn DUT symbol, the sources
and loads are in the `SOURCES` / `MODEL` code blocks, and the analysis and measurements are in the `NGSPICE` block.
Since 2026-11-04 the pad templates also place `en_ctrl_3v3` (xc) and `bias_gen_pd` (xg) next to the pad, as on the slot.

Every picture was checked as a PNG (Playwright Chromium): all symbols resolve, no empty boxes or "?".
Text that overlaps in a picture (e.g. the "run directory" note over the `MODEL` header of the S2D templates, one long
`SOURCES` line of `sg13cmos5l_IOPadSingle2Diff_tb_pd` over the pad symbol's name) overlaps the same way in the sheet.

## What exists at the taped-out commits

| macro | test benches | commit |
|---|---|---|
| `sg13cmos5l_IOPadSingle2Diff` | 7 CACE templates of the pad + 1 of the loop-gain fixture `s2d_mpdda_pd_sel` | P |
| `sg13cmos5l_IOPadDiff2Single` | 8 CACE templates of the pad + 1 of the loop-gain fixture `d2s_mpdda_pd_sel`; 4 stand-alone `tb_pd_*` | P |
| `pad_ref_rb` | 1 CACE template (`pad_ref_rb_tb_dc`, used by all 8 groups) | S |
| `en_ctrl_3v3` | 3 CACE templates (`tb_dc`, `tb_tran_en`, `tb_tran_vddl`) | S |
| `bg_core_pd`, `bias_dist_pd`, `vcm_rb`, `vref_s2d_rb`, `slot_7` | **none in xschem** (`bias_dist_pd`, `vcm_rb`, `vref_s2d_rb` have SPICE decks / Python scripts under `testbenches/`; `vcm_rb`, `vref_s2d_rb` old per-block CACE baselines under `verification/baseline/`, not of the taped-out cells) | S |

## Pictures

Conditions not listed are the CACE file's defaults (tt, 27 °C, iovdd 3.3 V, vdd 1.2 V, typical R / C / PNP,
sel 0 = harness 5 µA; S2D: vref = vcm = 1.2 V, rsrc 50 Ω, cload 0.5 pF per output; D2S: vref = vicm = 1.65 V,
100 pF ∥ 1 kΩ to vterm = 1.65 V). "5 corners" = ss, sf, tt, fs, ff;
"3 temps" = −40, 27, 125 °C. Data-sheet groups link to [`../../../datasheets/`](../../../datasheets/README.md).

### S2D pad (`sg13cmos5l_IOPadSingle2Diff`, P; CACE file `sg13cmos5l_IOPadSingle2Diff/verification/cace/sg13cmos5l_IOPadSingle2Diff.yaml`)

S2D templates: `sg13cmos5l_IOPadSingle2Diff/verification/cace/templates/`. Data sheet: [S2D](../../../datasheets/sg13cmos5l_IOPadSingle2Diff.md) (groups marked † also in its post-layout view).

| picture | source (commit) | what the bench measures (CACE group: parameters; conditions) | data-sheet group |
|---|---|---|---|
| [sg13cmos5l_IOPadSingle2Diff__tb_dc.svg](sg13cmos5l_IOPadSingle2Diff__tb_dc.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_dc.sch` (P) | DC sweep of u = pad − vref ± 0.5 V. **dc**: Gain, Vos_in, INL, Vcm_err, Iio; iovdd 3.0 / 3.3 / 3.6 V × 5 corners × R bcs / typ / wcs × 3 temps. **range**: Gain, INL, Vcm_err; iovdd 3.0 V, vref 0.5 / 0.8 / 1.2 / 1.65 V × vcm 1.0 / 1.2 / 1.4 / 1.65 V, ss / tt / ff, −40 / 125 °C. **dc_sel**: as dc, sel 0 / 1 / 2 × 5 corners × 3 temps; **dc_sel3**: sel 3; **dc_ibias**: harness ibias 3 … 7 µA × ss / tt / ff. **mm**: Vos_in, Gain, Vcm_err, 100 mismatch runs (tt); **mc**: same, 30 process + mismatch runs | dc_params †, range_params †, dc_sel_params †, dc_sel3_params †, dc_ibias_params †, mm_params, mc_params |
| [sg13cmos5l_IOPadSingle2Diff__tb_range.svg](sg13cmos5l_IOPadSingle2Diff__tb_range.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_range.sch` (P) | **window**: Vin_min, Vin_max (pad range in which the input-referred error stays below 1 mV, pad swept 0 … iovdd); vref 0.5 V, iovdd 3.0 / 3.3 / 3.6 V × ss / tt / ff × 3 temps | window_params † |
| [sg13cmos5l_IOPadSingle2Diff__tb_ac.svg](sg13cmos5l_IOPadSingle2Diff__tb_ac.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_ac.sch` (P) | Closed-loop AC, one source at a time (signal, iovdd, iovss, vref + vcm). **ac**: Acl_dB, f3dB, CMvdd_1k; 5 corners × 3 temps. **ac_mm**: PSRRp / PSRRn at 1 kHz and 100 kHz, CMRR_1k; 30 mismatch runs (tt, 27 °C) | ac_params †, ac_mm_params |
| [sg13cmos5l_IOPadSingle2Diff__tb_tran.svg](sg13cmos5l_IOPadSingle2Diff__tb_tran.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_tran.sch` (P) | **tran**: t_rise, t_settle, Overshoot, Vcm_dev for a u step −vstep/2 → +vstep/2 at 1 µs; cload 1 fF / 0.5 pF × ss / tt / ff × 3 temps | tran_params † |
| [sg13cmos5l_IOPadSingle2Diff__tb_noise.svg](sg13cmos5l_IOPadSingle2Diff__tb_noise.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_noise.sch` (P) | **noise**: En_1k, En_100k (input-referred density), Vn_out (integrated); 5 corners × 3 temps | noise_params † |
| [sg13cmos5l_IOPadSingle2Diff__tb_pd.svg](sg13cmos5l_IOPadSingle2Diff__tb_pd.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_pd.sch` (P) | **pd**: Iio_pd, Icore_pd, Ipad_pd, Ven3, Vod_pd, Voc_pd (supply and pad leakage, internal enable, outputs) in the power-down states pdstate 0 (en_1v2 low) / 1 (slot vdd_1v2 off) / 2 (slot vdd_3v3 off) / 3 (core 1.2 V off) × vpad 0 / 1.65 / 3.3 V × 27 / 125 °C | pd_params † |
| [sg13cmos5l_IOPadSingle2Diff__tb_enable.svg](sg13cmos5l_IOPadSingle2Diff__tb_enable.svg) | `…/sg13cmos5l_IOPadSingle2Diff_tb_enable.sch` (P) | **enable**: t_on, Vc_max, Vc_min, Vd_end, Iio_on for en_1v2 0 → 1.2 V at 1 µs with u = +0.25 V; ss / tt / ff × 3 temps | enable_params † |
| [s2d_mpdda_pd_sel__tb_loop.svg](s2d_mpdda_pd_sel__tb_loop.svg) | `…/s2d_mpdda_pd_sel_tb_loop.sch` (P), CACE file `s2d_mpdda_pd_sel.yaml` | **loop** on the fixture `s2d_mpdda_pd_sel` (input buffer + selectable bias, feedback broken at vfbp / vfbn): T0, fc, PM, GM, differential (dm) and common mode (cm); cload 1 fF / 0.5 / 2 / 10 pF × 5 corners × 3 temps | none (results exist in the design repo, `results/s2d_mpdda_pd_sel/`, but no data sheet reproduces them) |

### D2S pad (`sg13cmos5l_IOPadDiff2Single`, P; CACE file `sg13cmos5l_IOPadDiff2Single/verification/cace/sg13cmos5l_IOPadDiff2Single.yaml`)

D2S templates: `sg13cmos5l_IOPadDiff2Single/verification/cace/templates/`. Data sheet: [D2S](../../../datasheets/sg13cmos5l_IOPadDiff2Single.md) (schematic view only).

| picture | source (commit) | what the bench measures (CACE group: parameters; conditions) | data-sheet group |
|---|---|---|---|
| [sg13cmos5l_IOPadDiff2Single__tb_dc.svg](sg13cmos5l_IOPadDiff2Single__tb_dc.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_dc.sch` (P) | DC sweep of vd = vinp − vinn. **dc**: Gain, Vos_out, INL, Iio, Icore, IqP, IqN, Imin (output-device quiescent and minimum currents); 5 corners × 3 temps × iovdd 3.3 / 3.6 V. **dc_3v0**: same at 3.0 V. **dc_sel**: sel 0 / 1 / 2 × 3 temps; **dc_sel3**: sel 3 × 3 temps; **dc_ibias**: ibias 3.75 / 5 / 6.25 µA. **mm**: Vos_out, Gain, IqP, 30 mismatch runs | dc_params, dc_3v0_params, dc_sel_params, dc_sel3_params, dc_ibias_params, mm_params |
| [sg13cmos5l_IOPadDiff2Single__tb_ac.svg](sg13cmos5l_IOPadDiff2Single__tb_ac.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_ac.sch` (P) | **ac**: Acl_dB, f3dB, Peak_dB, PSRR_1k / 100k (iovdd), CMRR_1k, Zout_1k / 1M; 5 corners × 3 temps. **ac_load**: f3dB, Peak_dB; cload 10 / 100 / 300 pF × rload 1 kΩ / 1 GΩ. **ac_1nF**: same with 1 nF | ac_params, ac_load_params, ac_1nF_params |
| [sg13cmos5l_IOPadDiff2Single__tb_tran.svg](sg13cmos5l_IOPadDiff2Single__tb_tran.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_tran.sch` (P) | **tran**: SR_rise, SR_fall, Overshoot, ts_rise, ts_fall (large-signal step); ss / tt / ff × cload 10 / 100 / 300 pF | tran_params |
| [sg13cmos5l_IOPadDiff2Single__tb_thd.svg](sg13cmos5l_IOPadDiff2Single__tb_thd.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_thd.sch` (P) | **thd**: THD, Vout_amp (10 kHz sine, harmonics from 1024 resampled points); vdamp 0.5 / 1 / 1.5 V | thd_params |
| [sg13cmos5l_IOPadDiff2Single__tb_noise.svg](sg13cmos5l_IOPadDiff2Single__tb_noise.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_noise.sch` (P) | **noise**: En_1k, En_100k, Vn_int (output noise); 3 temps | noise_params |
| [sg13cmos5l_IOPadDiff2Single__tb_drive.svg](sg13cmos5l_IOPadDiff2Single__tb_drive.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_drive.sch` (P) | **drive**: Vout_max, Vout_min (swing into the load), Isc_src, Isc_snk (short-circuit current); 5 corners × −40 / 125 °C | drive_params |
| [sg13cmos5l_IOPadDiff2Single__tb_pd.svg](sg13cmos5l_IOPadDiff2Single__tb_pd.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_pd.sch` (P) | **pd**: Iio_pd, Icore_pd, Ipad_pd, Is12_pd, Is33_pd, Ven3 in pdstate 0 / 1 / 2 / 3 (as S2D) × vpad 0 / 1.65 / 3.3 V × tt / ff × 27 / 125 °C | pd_params |
| [sg13cmos5l_IOPadDiff2Single__tb_enable.svg](sg13cmos5l_IOPadDiff2Single__tb_enable.svg) | `…/sg13cmos5l_IOPadDiff2Single_tb_enable.sch` (P) | **enable**: t_on, Glitch_max, Glitch_min, Iio_end (start-up and output glitch after en_1v2 rises); sel 0 / 1 / 2, tstop 60 µs | enable_params |
| [d2s_mpdda_pd_sel__tb_loop.svg](d2s_mpdda_pd_sel__tb_loop.svg) | `…/d2s_mpdda_pd_sel_tb_loop.sch` (P), CACE file `d2s_mpdda_pd_sel.yaml` | Loop gain of the pad driver on the fixture `d2s_mpdda_pd_sel` (driver + selectable bias, loop opened at vfb): T0, fc, PM, GM. **loop**: 5 corners × 3 temps; **loop_load**: cload 10 / 100 / 300 pF × rload 1 kΩ / 1 GΩ; **loop_1nF**: 1 nF; **loop_sel**: sel 0 … 3 × −40 / 125 °C | none (results in the design repo, `results/d2s_mpdda_pd_sel/`, not in a data sheet) |

Stand-alone D2S benches (`sg13cmos5l_IOPadDiff2Single/testbenches/xschem/`, P). These are ordinary ngspice benches
with fixed values (no placeholders) on the driver `d2s_mpdda_pd` + output stage (`d2s_out_p` / `d2s_out_n`), but with
the **older bias blocks `bias_in_pd` / `bias_oa_pd`**, not the taped-out `bias_tree_pd` + `bias_gen_pd`. Their
reference numbers (in the sheets' notes) come from `results_power_down.txt`, which is not in the repository at P.
None of them feeds a data sheet.

| picture | source (commit) | what the bench measures | data-sheet group |
|---|---|---|---|
| [d2s_mpdda_pd__tb_pd_enable.svg](d2s_mpdda_pd__tb_pd_enable.svg) | `sg13cmos5l_IOPadDiff2Single/testbenches/xschem/tb_pd_enable.sch` (P) | vout (1 kΩ ∥ 100 pF, vinp = vinn = vref = 1.65 V) while en_3v3 rises at 10 µs and falls at 60 µs: excursion after each edge and settling to 1 mV; tt, 27 °C | none |
| [d2s_mpdda_pd__tb_pd_leak.svg](d2s_mpdda_pd__tb_pd_leak.svg) | `…/tb_pd_leak.sch` (P) | disabled (en_3v3 = 0), vout held at 1.65 V: bias, driver and vddo supply currents, output-device V_SG / V_GS; tt, 27 °C (notes quote ff 125 °C too) | none |
| [d2s_mpdda_pd__tb_pd_startup_oa.svg](d2s_mpdda_pd__tb_pd_startup_oa.svg) | `…/tb_pd_startup_oa.sch` (P) | with the self-contained `bias_oa_pd`: en_3v3 0 → 3.3 V at 1 µs from the disabled operating point; output-stage quiescent current and the time it stays within ±10 % of its final value | none |
| [d2s_mpdda_pd__tb_pd_unpowered.svg](d2s_mpdda_pd__tb_pd_unpowered.svg) | `…/tb_pd_unpowered.sch` (P) | unpowered (vdd = vddo one floating rail, 1 GΩ ∥ 1 nF), pad driven 0 → 5 V in 10 ns through 1.5 kΩ: output-device V_SG / V_GS, peak currents, how far vddo is pulled up; not an ESD simulation | none |

### Slot 7 blocks (S)

| picture | source (commit) | what the bench measures (CACE group: parameters; conditions) | data-sheet group |
|---|---|---|---|
| [pad_ref_rb__tb_dc.svg](pad_ref_rb__tb_dc.svg) | `pad_ref_rb/verification/cace/templates/pad_ref_rb_tb_dc.sch` (S), CACE file `pad_ref_rb.yaml` (generated by `pad_ref_rb/verification/gen_cace.py`) | DC operating point of the replica bias, with `en_ctrl_3v3` and `bias_gen_pd` next to it: Vcm, Vref, Ib (supply current) in every group. **vcm_dc**: iovdd 3.3 / 3.6 V × 5 corners × 3 temps; **vcm_dc_3v0**: 3.0 V; **vcm_sel**: 3.0 V, sel 1 / 2 × ss / tt / ff × 3 temps; **vref_room / vref_hot / vref_cold**: iovdd 3.0 / 3.3 / 3.6 V × 5 corners at 27 / 125 / −40 °C; **pd**: en = 0, 3.6 V, tt / ff × 27 / 125 °C; **mm**: 100 mismatch runs | [pad_ref_rb](../../../datasheets/pad_ref_rb.md): vcm_dc_params, vcm_dc_3v0_params, vcm_sel_params, vref_room_params, vref_hot_params, vref_cold_params, pd_params, mm_params |
| [en_ctrl_3v3__tb_dc.svg](en_ctrl_3v3__tb_dc.svg) | `en_ctrl_3v3/verification/cace/templates/en_ctrl_3v3_tb_dc.sch` (S), CACE file `en_ctrl_3v3.yaml` | DC truth table of `en_ctrl_3v3` v2 (shifter `ls_up_fs`): Verr_en, Verr_sel (output error against the expected level), I_vddh, I_vddl, I_s12, I_s33, I_en. sup = 0 / 0.5 / 1 picks (vddl, vddh) = (1.08, 3.0) / (1.2, 3.3) / (1.32, 3.6) V; cload 50 fF. **truth**: case 0 … 7 (all on, en off, vddl off, vddl floating, sel swapped …), tt 27 °C nominal; **pvt**: case 0 × 5 corners × −40 / 125 °C × sup 0 / 1; **vddl_off**: case 2 / 3, same grid; **float**: case 4 / 5 (vddl floating at 0.62 V through 1 TΩ), sup 0 | [en_ctrl_3v3](../../../datasheets/en_ctrl_3v3_level_shifter.md): truth_params, pvt_params, vddl_off_params, float_params |
| [en_ctrl_3v3__tb_tran_en.svg](en_ctrl_3v3__tb_tran_en.svg) | `en_ctrl_3v3/verification/cace/templates/en_ctrl_3v3_tb_tran_en.sch` (S) | **tran_en**: td_on, td_off (en_1v2 → en_3v3 delay, enable at 20 ns, disable at 520 ns, 100 ps edges); 5 corners × −40 / 125 °C × sup 0 / 1, cload 50 fF | tran_en_params |
| [en_ctrl_3v3__tb_tran_vddl.svg](en_ctrl_3v3__tb_tran_vddl.svg) | `en_ctrl_3v3/verification/cace/templates/en_ctrl_3v3_tb_tran_vddl.sch` (S) | **tran_vddl**: td_on, td_off, Ven_end with vddl off (scenario 1) or floating at 0.62 V (scenario 2), senses on; 5 corners × −40 / 125 °C, sup 0, cload 50 fF | tran_vddl_params |

The design repo's `en_ctrl_3v3` results directory at S also holds `tran_pg_params` results (not in the data sheet); their
template `en_ctrl_3v3_tb_tran_pg.sch` exists at P but no longer at S (`tran_vddl` took its place) and is not rendered here.

## Regenerating

```sh
PDK_ROOT=/foss/pdks PDK=ihp-sg13cmos5l ./render_testbenches.sh [work_dir] [out_dir]
```

[`render_testbenches.sh`](render_testbenches.sh) does what [`../render_schematics.sh`](../render_schematics.sh) does
(blob-less shallow clone, only `.sch` / `.sym` / `xschemrc` of the two commits via `git archive`; xschem 3.4.8RC under
`xvfb-run` with the design repo's `macros/xschemrc`, which puts every `macros/*/schematic/xschem` and
`macros/*/testbenches/xschem` on the symbol path; `dark_colorscheme 0`; bounding box + 3 % margin; 0.75 px per
xschem unit, 900 … 2400 px wide; `viewBox` added). One addition: xschem's bounding box underestimates the width of the
Monospace code blocks against a browser's DejaVu Sans Mono, so the last characters of the longest code line were cut
off where a code block is the right-most item. The script estimates each Monospace line's width (0.602 em per
character) and, where needed, widens the page and its white background on the right (same scale) to keep the 3 %
margin; it prints the sheets it widened.
