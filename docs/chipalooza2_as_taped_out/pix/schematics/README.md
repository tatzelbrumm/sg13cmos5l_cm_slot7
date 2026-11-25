<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 schematics (xschem renders)

SVG exports of the xschem sheets of the design repository
[tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single)
at the two taped-out commits:

- **P** = [`91a7da8`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/91a7da8b67ac56a26c605501146667a1fde28c32) (`91a7da8b67ac56a26c605501146667a1fde28c32`): the custom pads
- **S** = [`9052bd3`](https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single/tree/9052bd35928c6d40344e8e686c9abbe736bfadb9) (`9052bd35928c6d40344e8e686c9abbe736bfadb9`): `slot_7` and the blocks it places

All pictures: xschem 3.4.8RC, IHP open PDK `ihp-sg13cmos5l` symbols, the design repo's `macros/xschemrc`
(every `macros/*/schematic/xschem` on the symbol path), light colour scheme, exported area = drawing
bounding box + 3 % margin. Every sheet was checked as a PNG (Playwright Chromium): all symbols resolve.
Source paths are relative to `macros/` of the design repository.

**Test benches:** the CACE templates and stand-alone xschem test benches of these cells, rendered the same way, are in [`testbenches/`](testbenches/README.md).

## Hierarchy

```
slot_7 ─┬─ s7_ctrl ── ls_up_fs (efs_ls_core in the layout) ×7, nand2_hv ×13, inv_hv ×12, tg_hv ×10
        ├─ s7_doutpd
        ├─ bg_core_pd
        ├─ bias_dist_pd ── bdp_slice ×8 (nand2_hv, inv_hv, tg_hv)
        └─ pad_ref_rb ─┬─ bias_tree_rb, vcm_rb, vref_s2d_rb, bypass_rb
en_ctrl_3v3 ── ls_up_fs ×3          (stand-alone enable macro; its shifter is the one s7_ctrl uses)
sg13cmos5l_IOPadSingle2Diff ─┬─ s2d_pad_esd, bias_tree_noab_pd
                             └─ s2d_mpdda_pd ── s2d_mpdda ── unit_r2 ×6
sg13cmos5l_IOPadDiff2Single ─┬─ d2s_sp2k ×2, d2s_out_p, d2s_out_n, bias_tree_pd
                             └─ d2s_mpdda_pd ── unit_r2 ×4
```

## Pictures

| file | cell | source (commit) |
|---|---|---|
| [slot_7.svg](slot_7.svg) | slot 7 top: s7_ctrl, s7_doutpd, bg_core_pd, bias_dist_pd, pad_ref_rb | `slot_7/schematic/xschem/slot_7.sch` (S) |
| [s7_ctrl.svg](s7_ctrl.svg) | master enable, mode decode, switch matrix | `slot_7/schematic/xschem/s7_ctrl.sch` (S) |
| [s7_doutpd.svg](s7_doutpd.svg) | 12 pull-downs for the unused dig_out | `slot_7/schematic/xschem/s7_doutpd.sch` (S) |
| [bg_core_pd.svg](bg_core_pd.svg) | bandgap-referenced 5 µA current reference | `bg_core_pd/schematic/xschem/bg_core_pd.sch` (S) |
| [bias_dist_pd.svg](bias_dist_pd.svg) | switchable bias distribution mirror (4 in, 4 out) | `bias_dist_pd/schematic/xschem/bias_dist_pd.sch` (S) |
| [bdp_slice.svg](bdp_slice.svg) | one switched leg of bias_dist_pd | `bias_dist_pd/schematic/xschem/bdp_slice.sch` (S) |
| [pad_ref_rb.svg](pad_ref_rb.svg) | replica bias of the pads' vcm / vref | `pad_ref_rb/schematic/xschem/pad_ref_rb.sch` (S) |
| [bias_tree_rb.svg](bias_tree_rb.svg) | shared bias tree of pad_ref_rb | `pad_ref_rb/schematic/xschem/bias_tree_rb.sch` (S) |
| [vcm_rb.svg](vcm_rb.svg) | vcm replica (S2D vcm = D2S vref) | `vcm_rb/schematic/xschem/vcm_rb.sch` (S) |
| [vref_s2d_rb.svg](vref_s2d_rb.svg) | vref replica of the S2D pad | `vref_s2d_rb/schematic/xschem/vref_s2d_rb.sch` (S) |
| [bypass_rb.svg](bypass_rb.svg) | vcm / vref bypass capacitors | `pad_ref_rb/schematic/xschem/bypass_rb.sch` (S) |
| [en_ctrl_3v3.svg](en_ctrl_3v3.svg) | fail-safe enable / select macro | `en_ctrl_3v3/schematic/xschem/en_ctrl_3v3.sch` (S) |
| [ls_up_fs.svg](ls_up_fs.svg) | fail-safe 1.2 V → 3.3 V level shifter (layout cell `efs_ls_core`) | `en_ctrl_3v3/schematic/xschem/ls_up_fs.sch` (S) |
| [inv_hv.svg](inv_hv.svg) | 3.3 V inverter | `hv_logic/schematic/xschem/inv_hv.sch` (S) |
| [nand2_hv.svg](nand2_hv.svg) | 3.3 V NAND2 | `hv_logic/schematic/xschem/nand2_hv.sch` (S) |
| [tg_hv.svg](tg_hv.svg) | 3.3 V transmission gate | `hv_logic/schematic/xschem/tg_hv.sch` (S) |
| [sg13cmos5l_IOPadSingle2Diff.svg](sg13cmos5l_IOPadSingle2Diff.svg) | S2D pad top | `sg13cmos5l_IOPadSingle2Diff/schematic/xschem/sg13cmos5l_IOPadSingle2Diff.sch` (P) |
| [s2d_mpdda_pd.svg](s2d_mpdda_pd.svg) | S2D input buffer with enable | `sg13cmos5l_IOPadSingle2Diff/schematic/xschem/s2d_mpdda_pd.sch` (P) |
| [s2d_mpdda.svg](s2d_mpdda.svg) | S2D core amplifier (matched-pair DDA) | `sg13cmos5l_IOPadSingle2Diff/schematic/xschem/s2d_mpdda.sch` (P) |
| [s2d_pad_esd.svg](s2d_pad_esd.svg) | S2D primary ESD protection | `sg13cmos5l_IOPadSingle2Diff/schematic/xschem/s2d_pad_esd.sch` (P) |
| [bias_tree_noab_pd.svg](bias_tree_noab_pd.svg) | S2D bias tree | `bias_tree_noab_pd/schematic/xschem/bias_tree_noab_pd.sch` (P) |
| [sg13cmos5l_IOPadDiff2Single.svg](sg13cmos5l_IOPadDiff2Single.svg) | D2S pad top | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/sg13cmos5l_IOPadDiff2Single.sch` (P) |
| [d2s_mpdda_pd.svg](d2s_mpdda_pd.svg) | D2S core amplifier (DDA, class-AB drive) | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/d2s_mpdda_pd.sch` (P) |
| [d2s_out_p.svg](d2s_out_p.svg) | D2S P output / clamp frame | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/d2s_out_p.sch` (P) |
| [d2s_out_n.svg](d2s_out_n.svg) | D2S N output / clamp frames | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/d2s_out_n.sch` (P) |
| [d2s_sp2k.svg](d2s_sp2k.svg) | D2S 2 kΩ secondary protection | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/d2s_sp2k.sch` (P) |
| [unit_r2.svg](unit_r2.svg) | split-tail PMOS pair unit of both DDAs | `sg13cmos5l_IOPadDiff2Single/schematic/xschem/unit_r2.sch` (P) |
| [bias_tree_pd.svg](bias_tree_pd.svg) | D2S bias tree | `bias_tree_pd/schematic/xschem/bias_tree_pd.sch` (P) |

## Regenerating

```sh
PDK_ROOT=/foss/pdks PDK=ihp-sg13cmos5l ./render_schematics.sh [work_dir] [out_dir]
```

[`render_schematics.sh`](render_schematics.sh) fetches only the `.sch` / `.sym` / `xschemrc` files of the two
commits (blob-less shallow clone, `git archive`), then for each sheet runs, under `xvfb-run` (without an X
server xschem does not know text extents and the comment texts fall outside the exported area):

```sh
xvfb-run -a xschem -q --rcfile <commit>/macros/xschemrc --tcl 'set dark_colorscheme 0' \
  --command 'set svgfile out.svg; <bbox + 3 % margin>; xschem print svg $svgfile $w $h $x1 $y1 $x2 $y2; exit' cell.sch
```

with a page width of 0.75 px per xschem unit (900 to 2400 px), and adds a `viewBox` so the SVG scales.
