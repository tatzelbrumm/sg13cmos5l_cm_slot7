<!--
SPDX-FileCopyrightText: 2026 Christoph Maier
SPDX-License-Identifier: Apache-2.0
-->
# Slot 7 layout renders (KLayout)

PNG renders of the taped-out GDS in this repository, made with KLayout 0.30.12 in batch mode
(`pya.LayoutView`, `save_image_with_options`, 2× oversampling, white background, texts hidden) and the IHP
layer properties `ihp-sg13cmos5l/libs.tech/klayout/tech/sg13cmos5l.lyp`. Each picture has a caption strip
with the cell name, its size and a scale bar (added with Pillow, then stored as a 123-color palette PNG).
"Front end" views hide Passiv, Via2 … TopVia2 and Metal3 … TopMetal2, so the devices, Metal1 and Metal2
under the pad's top-metal plates show.

| file | cell | size (µm) | source | view |
|---|---|---|---|---|
| [slot_7.png](slot_7.png) | `slot_7` (whole slot, 2000 px wide) | 537.15 × 273.00 | `final/gds/slot_7.gds` | all layers |
| [slot_7_bg_core_pd.png](slot_7_bg_core_pd.png) | `bg_core_pd` | 47.55 × 50.05 | `final/gds/slot_7.gds` | all layers |
| [slot_7_bias_dist_pd.png](slot_7_bias_dist_pd.png) | `bias_dist_pd` | 60.49 × 16.44 | `final/gds/slot_7.gds` | all layers |
| [slot_7_pad_ref_rb.png](slot_7_pad_ref_rb.png) | `pad_ref_rb` | 73.80 × 76.26 | `final/gds/slot_7.gds` | all layers |
| [slot_7_s7_ctrl.png](slot_7_s7_ctrl.png) | `s7_ctrl` | 71.60 × 38.04 | `final/gds/slot_7.gds` | all layers |
| [slot_7_s7_doutpd.png](slot_7_s7_doutpd.png) | `s7_doutpd` | 24.67 × 3.85 | `final/gds/slot_7.gds` | all layers |
| [slot_7_tughra_art.png](slot_7_tughra_art.png) | `tughra_art` | 158.05 × 90.00 | `final/gds/slot_7.gds` | all layers |
| [IOPadSingle2Diff.png](IOPadSingle2Diff.png) | `sg13cmos5l_IOPadSingle2Diff` | 81.24 × 180.00 | `pads/sg13cmos5l_IOPadSingle2Diff/sg13cmos5l_IOPadSingle2Diff.gds` | all layers |
| [IOPadSingle2Diff_frontend.png](IOPadSingle2Diff_frontend.png) | `sg13cmos5l_IOPadSingle2Diff` | 81.24 × 180.00 | same | Metal2 and below |
| [IOPadDiff2Single.png](IOPadDiff2Single.png) | `sg13cmos5l_IOPadDiff2Single` | 81.24 × 180.00 | `pads/sg13cmos5l_IOPadDiff2Single/sg13cmos5l_IOPadDiff2Single.gds` | all layers |
| [IOPadDiff2Single_frontend.png](IOPadDiff2Single_frontend.png) | `sg13cmos5l_IOPadDiff2Single` | 81.24 × 180.00 | same | Metal2 and below |

Sizes are the cell bounding boxes (the pads' 81.24 µm includes the 0.62 µm edge stubs on each side of the 80 µm frame).

## Regenerating

```sh
./render_layout.sh [out_dir]      # default: this folder
```

which runs

```sh
klayout -zz -rd repo=<repo root> -rd out=<tmp> -rd lyp=$PDK_ROOT/ihp-sg13cmos5l/libs.tech/klayout/tech/sg13cmos5l.lyp -r render_layout.py
python3 annotate_layout.py <tmp> <out_dir>
```

- [`render_layout.py`](render_layout.py): KLayout script, the list of pictures (cell, long side in px, view); writes the raw PNGs and the bounding box / µm per pixel of each.
- [`annotate_layout.py`](annotate_layout.py): adds the caption and the scale bar, quantizes.
- [`render_layout.sh`](render_layout.sh): runs both.
