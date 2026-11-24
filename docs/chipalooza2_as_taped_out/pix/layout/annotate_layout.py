# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
#
# Second step of render_layout.sh: add a caption strip (cell, size in um, view) and a scale bar
# below each raw KLayout render, and store it as a 123-colour palette PNG (keeps each file well under 400 kB).
# Usage: python3 annotate_layout.py <raw dir> <out dir>
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

raw_dir, out_dir = sys.argv[1], sys.argv[2]
os.makedirs(out_dir, exist_ok=True)


def font(size):
    for name in ("DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def nice_length(target_um):
    """Largest 1/2/5 x 10^n length not above target_um."""
    best = 0.1
    for exp in range(-1, 4):
        for m in (1, 2, 5):
            v = m * 10 ** exp
            if v <= target_um:
                best = v
    return best


for png in sorted(glob.glob(os.path.join(raw_dir, "*.png"))):
    name = os.path.splitext(os.path.basename(png))[0]
    cell, gds, w_um, h_um, um_per_px, view = open(os.path.join(raw_dir, name + ".txt")).read().split("\t")
    w_um, h_um, um_per_px, view = float(w_um), float(h_um), float(um_per_px), view.strip()
    im = Image.open(png).convert("RGB")
    W, H = im.size
    fs = max(14, min(24, W // 45))
    fsmall = int(fs * 0.8)
    strip = int(fs * 1.3 + 2 * fsmall * 1.3 + 12)
    # Quantize the layout itself to 120 colours, then add pure black / grey / white for the caption.
    q = im.quantize(colors=120, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()[:120 * 3] + [0, 0, 0, 80, 80, 80, 255, 255, 255]
    canvas = Image.new("RGB", (W, H + strip), "white")
    canvas.paste(q.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(canvas)
    f, f2 = font(fs), font(fsmall)
    # line 1: cell and size (left), scale bar of about 20 % of the width (right)
    d.text((10, H + 4), "%s   %.2f \u00d7 %.2f \u00b5m" % (cell, w_um, h_um), fill="black", font=f)
    bar_um = nice_length(0.2 * W * um_per_px)
    bar_px = int(round(bar_um / um_per_px))
    label = ("%g um" % bar_um).replace("um", "\u00b5m")
    tw = d.textlength(label, font=f2)
    x2 = W - 12
    yb = H + 4 + fs // 2
    d.rectangle([x2 - tw - 8 - bar_px, yb - 2, x2 - tw - 8, yb + 2], fill="black")
    d.text((x2 - tw, H + 4 + (fs - fsmall) // 2), label, fill="black", font=f2)
    # lines 2 and 3: source file, view
    vtxt = "all layers" if view == "all" else "Metal2 and below (Metal3 ... TopMetal2, Passiv hidden)"
    d.text((10, H + 8 + int(fs * 1.3)), gds, fill=(80, 80, 80), font=f2)
    d.text((10, H + 8 + int(fs * 1.3 + fsmall * 1.3)), vtxt, fill=(80, 80, 80), font=f2)
    palimg = Image.new("P", (1, 1))
    palimg.putpalette(pal + [255, 255, 255] * (256 - len(pal) // 3))
    out = os.path.join(out_dir, name + ".png")
    canvas.quantize(palette=palimg, dither=Image.Dither.NONE).save(out, optimize=True)
    print("%-30s %5d x %-5d %7d bytes" % (name + ".png", W, H + strip, os.path.getsize(out)))
