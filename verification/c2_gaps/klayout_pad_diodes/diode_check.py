#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""The pad antenna diode alone in ngspice (IHP sg13cmos5l simulation): parameter handling, I-V step, minimal abort.

Usage: python3 -I diode_check.py <work_dir> <dest_dir>   -> <dest_dir>/csv/diode_*.csv; decks / logs in <work_dir>/diode
Needs PDK_ROOT (ihp-sg13cmos5l) and ngspice on PATH; each ngspice run has a 60 s timeout (a stuck DC sweep is a
result here, see 2.).

1. params:  dpantenna called with a= p= (as the converted KLayout netlists), with l= w= (as the schematic / PEX
            netlists) and with nothing; `listing expand` shows the area= that each component diode gets.
2. iv:      dantenna (KLayout default size / extracted size l=27.78u w=1.26u, m=2 as X$65 of the S2D pad) and its
            component models darea / dperim / dcorner (area 1), anode 0, cathode swept 0 ... 0.2 V in 0.5 mV, at -40 /
            27 / 125 C, .option gmin=1e-12 as the slot decks. Reported: the largest current step between neighbouring
            points, where it is, and the median step (the smooth part). The same sweep in 0.1 mV steps for the two
            dantenna sizes: whether ngspice finishes it within the timeout (a point inside the step can have no DC
            solution).
3. tran:    X$65 alone, cathode = the slot sine 0.5 + 0.5 sin(2 pi 10 kHz t), tran 0 ... 100 us, max step 39.0625 ns,
            method=gear gmin=1e-12 (the options of ../ac_tran/slot.py): default size vs extracted size, and (diagnosis,
            modified copies of diodes.lib in the work dir) default size with one darea parameter removed (ibv -> 1e-30,
            rs -> 0, tt -> 0, cj0 -> 0), extracted size with trap integration, with the darea rs and cj0 of the default
            size, and with both.
"""
import csv
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

WORK, DEST = Path(sys.argv[1]).resolve() / 'diode', Path(sys.argv[2]).resolve()
LIB = Path(os.environ.get('PDK_ROOT', '/foss/pdks')) / 'ihp-sg13cmos5l' / 'libs.tech' / 'ngspice' / 'models' \
    / 'diodes.lib'
SIZED = 'l=27.78u w=1.26u'   # = KLayout A=35.0028p P=58.08u (S2D pad X$65), = the schematic XDN1 / XDN2
HDR = ('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
       '# IHP sg13cmos5l simulation (ngspice, PDK diodes.lib): %s\n')


def ng(name, deck, lib=None):
    f = WORK / f'{name}.sp'
    f.write_text(deck.replace('@LIB@', str(lib or LIB)))
    try:
        p = subprocess.run(['ngspice', '-b', f.name], cwd=WORK, capture_output=True, text=True, timeout=60)
        out = p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b'').decode(errors='replace') + '\nTIMEOUT 60 s'
    (WORK / f'{name}.log').write_text(out)
    return out


def params():
    out = ng('params', """* dpantenna: a= p= vs l= w= vs default
.include @LIB@
V1 a 0 0
Xap a 0 dpantenna a=35.0028p p=58.08u m=2
Xlw a 0 dpantenna l=27.78u w=1.26u m=2
Xdef a 0 dpantenna
.control
op
listing expand
.endc
.end
""")
    rows = []
    for inst, how in (('xap', 'a=35.0028p p=58.08u m=2 (converted KLayout netlist)'),
                      ('xlw', 'l=27.78u w=1.26u m=2 (schematic / PEX netlist)'), ('xdef', '(no parameters)')):
        for comp in ('d1', 'd2', 'd3'):
            m = re.search(rf'd\.{inst}\.{comp}\s+\S+\s+\S+\s+(\S+)\s+area=\s*(\S+)', out)
            mm = re.search(rf'd\.{inst}\.{comp}\s.*?\bm=\s*(\S+)', out)
            rows.append([inst, how, comp, m.group(1) if m else '?', float(m.group(2)) if m else '',
                         float(mm.group(1)) if mm else 1.0])
    warn = 'warning' in out.lower() and re.search(r'(?i)warn.*\b(a|p)\b', out)
    with open(DEST / 'csv' / 'diode_params.csv', 'w', newline='') as f:
        f.write(HDR % ('area factor each component diode of dpantenna gets (listing expand); ngspice message about '
                       'a= / p=: ' + ('yes' if warn else 'none')))
        w = csv.writer(f)
        w.writerow(['instance', 'call', 'component', 'model', 'area', 'm'])
        w.writerows(rows)


def iv():
    rows, curves = [], {}
    devs = [('dantenna_default', 'X1 0 c dantenna m=2'), ('dantenna_extracted', f'X1 0 c dantenna {SIZED} m=2'),
            ('darea_area1', 'D1 0 c darea area=1'), ('dperim_area1', 'D1 0 c dperim area=1'),
            ('dcorner_area1', 'D1 0 c dcorner area=1')]
    jobs = [(t, name, line, 0.0005) for t in (-40, 27, 125) for name, line in devs]
    jobs += [(t, name, line, 0.0001) for t in (-40, 27, 125) for name, line in devs[:2]]
    for t, name, line, dv in jobs:
        tag = f'iv_{name}_{t}_{dv * 1e3:g}mV'
        ng(tag, f"""* {name}: anode 0, cathode swept, {t} C
.include @LIB@
.temp {t}
.option gmin=1e-12
V1 c 0 0
{line}
.control
dc V1 0 0.2 {dv}
set wr_singlescale
set wr_vecnames
option numdgt=9
wrdata {tag}.txt i(v1)
.endc
.end
""")
        p = WORK / f'{tag}.txt'
        if not p.exists():
            rows.append([name, t, dv * 1e3, 'not finished in 60 s (ngspice batch, DC sweep)', '', '', '', ''])
            continue
        a = np.loadtxt(p, skiprows=1, ndmin=2)
        v, i = a[:, 0], -a[:, 1]     # reverse current into the cathode, positive
        d = np.diff(i)
        k = int(np.argmax(np.abs(d)))
        rows.append([name, t, dv * 1e3, f'completed, {len(v)} points', f'{d[k]:.4e}', f'{v[k]:.4f}', f'{v[k + 1]:.4f}',
                     f'{np.median(np.abs(d)):.3e}'])
        if t == 27 and name.startswith('dantenna') and dv == 0.0005:
            curves[name] = (v, i)
    with open(DEST / 'csv' / 'diode_iv_step.csv', 'w', newline='') as f:
        f.write(HDR % 'reverse current I (into the cathode) vs cathode voltage V, anode 0, sweep 0 ... 0.2 V; '
                'largest step dI between neighbouring points [A] and where; median |dI| = the smooth part')
        w = csv.writer(f)
        w.writerow(['device', 'temp_C', 'sweep_step_mV', 'sweep', 'max_step_A', 'between_V', 'and_V',
                    'median_abs_step_A'])
        w.writerows(rows)
    if curves:
        v = curves['dantenna_default'][0]
        sel = (v >= 0.06) & (v <= 0.10)
        with open(DEST / 'csv' / 'diode_iv_27C.csv', 'w', newline='') as f:
            f.write(HDR % 'dantenna m=2 (S2D pad X$65), 27 C: reverse current [A] vs cathode voltage [V], '
                    '60 ... 100 mV')
            w = csv.writer(f)
            w.writerow(['v_cathode', 'i_default_size', 'i_extracted_size'])
            for j in np.nonzero(sel)[0]:
                w.writerow([f'{v[j]:.4f}', f'{curves["dantenna_default"][1][j]:.6e}',
                            f'{np.interp(v[j], *curves["dantenna_extracted"]):.6e}'])


def tran():
    src = LIB.read_text()
    mods = {'ibv=1e-30': ('ibv=3.458E-007', 'ibv=1E-030'), 'rs=0': ('rs=2.193E+005', 'rs=0'),
            'tt=0': ('tt=7.009E-007', 'tt=0'), 'cj0=0': ('cj0=9.371E-016', 'cj0=0'),
            'rs as default size': ('rs=2.193E+005', 'rs=1.2614E+007'),
            'cj0 as default size': ('cj0=9.371E-016', 'cj0=1.6268E-017')}
    # 'as default size': darea rs x (35.0028 / 0.6084), cj0 / (35.0028 / 0.6084), so that the extracted-size darea has
    # the series resistance / junction capacitance of the default-size one
    cases = [('default size', '', [], 'gear'), ('extracted size', SIZED, [], 'gear'),
             ('extracted size, trap', SIZED, [], 'trap'), ('default size, trap', '', [], 'trap')]
    cases += [(f'default size, darea {k}', '', [k], 'gear') for k in ('ibv=1e-30', 'rs=0', 'tt=0', 'cj0=0')]
    cases += [('extracted size, darea rs as default size', SIZED, ['rs as default size'], 'gear'),
              ('extracted size, darea cj0 as default size', SIZED, ['cj0 as default size'], 'gear'),
              ('extracted size, darea rs and cj0 as default size', SIZED, ['rs as default size', 'cj0 as default size'],
               'gear')]
    rows = []
    for n, (name, size, mk, meth) in enumerate(cases):
        lib = None
        if mk:
            txt = src
            for k in mk:
                old, new = mods[k]
                line = re.search(r'^\.MODEL darea .*$', txt, re.M).group(0)
                assert old in line, (k, line)
                txt = txt.replace(line, line.replace(old, new))
            lib = WORK / f'diodes_mod{n}.lib'
            lib.write_text(txt)
        out = ng(f'tran{n}', f"""* S2D pad diode X$65 alone, {name}; cathode = the slot sine, anode 0, 27 C
.include @LIB@
.temp 27
.option gmin=1e-12 method={meth}
V1 c 0 dc 0.5 sin(0.5 0.5 10k)
X65 0 c dantenna {size} m=2
.control
tran 39.0625n 100u 0 39.0625n
echo "TRDONE"
.endc
.end
""", lib)
        m = re.search(r'Timestep too small; time = (\S+), timestep = (\S+): trouble with (.*)', out)
        if m:
            t = float(m.group(1).rstrip(','))
            vin = 0.5 + 0.5 * np.sin(2 * np.pi * 1e4 * t)
            rows.append([name, meth, 'ABORTED', f'{t:.6e}', f'{vin:.4f}', m.group(3).strip()])
        elif 'TIMEOUT' in out:
            ref = re.findall(r'Reference value :\s*(\S+)', out)
            t = float(ref[-1]) if ref else float('nan')
            vin = 0.5 + 0.5 * np.sin(2 * np.pi * 1e4 * t)
            rows.append([name, meth, 'STUCK (no end within the 60 s timeout; last time point given)', f'{t:.6e}',
                         f'{vin:.4f}', ''])
        else:
            rows.append([name, meth, 'completed' if 'TRDONE' in out and 'aborted' not in out else 'no result', '', '',
                         ''])
    with open(DEST / 'csv' / 'diode_tran.csv', 'w', newline='') as f:
        f.write(HDR % 'S2D pad antenna diode X$65 (dantenna m=2) alone, cathode driven by the slot sine 0 ... 1 V '
                '10 kHz, '
                'tran 0 ... 100 us; modified darea parameters = diagnosis only')
        w = csv.writer(f)
        w.writerow(['case', 'method', 'result', 'abort_time_s', 'v_cathode_at_abort', 'ngspice_trouble'])
        w.writerows(rows)
    for r in rows:
        print('diode tran:', ' | '.join(r))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    WORK.mkdir(parents=True, exist_ok=True)
    (DEST / 'csv').mkdir(parents=True, exist_ok=True)
    params()
    iv()
    tran()
