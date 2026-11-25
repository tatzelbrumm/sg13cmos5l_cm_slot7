#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Give the antenna diodes of a converted KLayout pad netlist their extracted size (IHP sg13cmos5l).

Usage: python3 -I fix_diodes.py <converted.spice> [<out.spice>]   (in place without <out>); prints one line per diode.
Also imported by run_fixed.py (fix_file()).

KLayout's SG13 LVS writes the antenna diodes as  D$63 pad iovdd dpantenna A=35.0028p P=58.08u m=2  (area in m^2,
perimeter in m). The designer's run_starve.convert() (design repository, macros/en_ctrl_3v3/testbenches/spice/
run_starve.py) turns that into the subckt call  X$63 pad iovdd dpantenna a=35.0028p p=58.08u m=2 . The PDK subckts
(libs.tech/ngspice/models/diodes.lib) take only l / w (defaults 780n): .params l=780n w=780n DEV_A=(l*w)/1p
DEV_P=(l+w)/0.5u DEV_C=4. ngspice ignores the unknown a= / p= without a message, so each diode is simulated at
0.78 um x 0.78 um. Here a / p are replaced by the rectangle l x w with l*w = A and 2(l + w) = P, which gives the model
exactly DEV_A = A/1um^2 and DEV_P = P/1um (real for every rectilinear outline, P >= 4 sqrt(A)); m= and everything else
on the line is kept.
"""
import math
import re
import sys
from pathlib import Path

SI = {'f': 1e-15, 'p': 1e-12, 'n': 1e-9, 'u': 1e-6, 'm': 1e-3, '': 1.0}
LINE = re.compile(r'^(X\S+\s+\S+\s+\S+\s+(?:dantenna|dpantenna))\s+(.*)$', re.I)


def num(s):
    m = re.fullmatch(r'([-+0-9.eE]+?)([fpnum]?)', s.strip(), re.I)
    return float(m.group(1)) * SI[m.group(2).lower()]


def lw(a, p):
    """Rectangle with area a [m^2] and perimeter p [m]: (l, w) [m], l >= w."""
    s = p / 2
    d = s * s - 4 * a
    if d < 0:
        raise ValueError(f'no rectangle with A={a} P={p}')
    l = (s + math.sqrt(d)) / 2
    return l, a / l


def fix_text(txt):
    out, log = [], []
    for line in txt.splitlines():
        m = LINE.match(line)
        if m:
            prm = dict(t.split('=', 1) for t in m.group(2).split() if '=' in t)
            low = {k.lower(): k for k in prm}
            if 'a' in low and 'p' in low and 'l' not in low and 'w' not in low:
                a, p = num(prm.pop(low['a'])), num(prm.pop(low['p']))
                l, w = lw(a, p)
                rest = ' '.join(f'{k}={v}' for k, v in prm.items())
                new = f'{m.group(1)} l={l * 1e6:.6g}u w={w * 1e6:.6g}u' + (f' {rest}' if rest else '')
                log.append(f'{line.strip()}  ->  {new.strip()}   (DEV_A {l * w * 1e12:.6g}, DEV_P {(l + w) / 0.5e-6:.6g})')
                line = new
        out.append(line)
    return '\n'.join(out) + '\n', log


def fix_file(src, dst=None):
    src = Path(src)
    txt, log = fix_text(src.read_text())
    Path(dst or src).write_text(txt)
    return log


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    for ln in fix_file(*sys.argv[1:]):
        print(ln)
