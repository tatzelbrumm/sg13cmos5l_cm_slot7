#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Write the AC / transient / noise curve groups next to a pad's own CACE file (IHP sg13cmos5l simulation).

Usage: mkgroups.py <macro_dir> <cell> <source: schematic|pex>

Each group reuses one of the pad's committed CACE testbenches (design repository commit 91a7da8b...: tb_ac, tb_tran,
tb_noise, tb_enable) UNCHANGED, sources, models, options and the whole original .control block included, so the
.data line (the CACE scalars) is computed exactly as for the committed results. Only lines are ADDED inside the
.control block:
  - wrdata of the waveforms / spectra the original analyses computed (tb_tran, tb_enable, D2S tb_ac: right after the
    analysis line, before the original meas lines change nothing);
  - after the original echo line: extra analyses for the plots (S2D tb_ac: the same AC sources on a finer and wider
    grid, dec 40 10 Hz ... 1 GHz; tb_noise: noise dec 40 10 Hz ... 10 MHz; tb_enable: a second transient with the
    enable switched on at 1 us and off again (alter of the Ven pwl)).
Files written per run: CACE{filename}_CACE{N}.<suffix> (collect.py reads them), the .data file as the original.

Writes <cace_dir>/_atg_<cell>[_pex].yaml (copy of the cell yaml: same pins / default_conditions / paths; parameters
replaced by the groups below, each with the spec / variables of the original group it reuses; pex: own runs /
netlist / docs folders and a layout path, as the S2D Makefile's sim-cace CACE_SOURCE=pex) and
<cace_dir>/templates/<cell>_tb_at_<kind>.sch.
"""
import re
import sys
from pathlib import Path

import yaml

S2D, D2S = 'sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single'
CORNERS = ['ss', 'sf', 'tt', 'fs', 'ff']
TEMPS = [-40, 27, 125]
F = r'CACE\{filename\}_CACE\{N\}'
WR = 'set wr_singlescale\nset wr_vecnames\noption numdgt=9\n'

# ---- S2D additions ---------------------------------------------------------------------------------------------
S2D_AC_TAIL = WR + rf"""* ---- appended (ac_tran): the signal and iovdd analyses on a finer, wider grid for the plots
alter @Vref[acmag] = 0
alter @Vgio[acmag] = 0
alter @Vio[acmag] = 0
alter @Vu[acmag] = 1
ac dec 40 10 1G
let at_vd = v(outp) - v(outn)
let at_vc = (v(outp) + v(outn))/2
let at_vd_db = db(at_vd)
let at_vd_ph = 180/pi*cph(at_vd)
let at_vc_db = db(at_vc)
wrdata {F}.at_u at_vd_db at_vd_ph at_vc_db
alter @Vu[acmag] = 0
alter @Vio[acmag] = 1
ac dec 40 10 1G
let at_vc = (v(outp) + v(outn))/2
let at_vc_db = db(at_vc)
let at_vc_ph = 180/pi*cph(at_vc)
wrdata {F}.at_vdd at_vc_db at_vc_ph
"""
S2D_TRAN_TAIL = WR + f"wrdata {F}.at_tran v(outp) v(outn) v(vcm)\n"
S2D_NOISE_TAIL = WR + rf"""* ---- appended (ac_tran): spectra on a finer grid (the same analysis as the Vn_out one)
noise v(outp,outn) Vu dec 40 10 10meg
let at_on = onoise_total
let at_in = inoise_total
echo $&at_on $&at_in > {F}.at_ntot
setplot previous
wrdata {F}.at_noise onoise_spectrum inoise_spectrum
"""
S2D_EN_TAIL = WR + rf"""wrdata {F}.at_en v(outp) v(outn) v(vcm) i(vio)
* ---- appended (ac_tran): enable at 1 us, disable at 11 us
save v(outp) v(outn) v(vcm) i(vio) i(vcore) v(en_3v3)
alter @Ven[pwl] = [ 0 0 1u 0 1.001u CACE\{{vddl=1.2\}} 11u CACE\{{vddl=1.2\}} 11.001u 0 ]
tran 5n 20u
wrdata {F}.at_endis v(outp) v(outn) v(vcm) i(vio) i(vcore) v(en_3v3)
"""

# ---- D2S additions ---------------------------------------------------------------------------------------------
D2S_AC_AFTER = [  # inserted right after the n-th 'ac dec 50 1 1G' line of the original block
    WR + f"let at_m = db(v(pad))\nlet at_p = 180/pi*cph(v(pad))\nwrdata {F}.at_sig at_m at_p\n",
    f"let at_m = db(v(pad))\nlet at_p = 180/pi*cph(v(pad))\nwrdata {F}.at_psr at_m at_p\n",
    f"let at_m = db(v(pad))\nwrdata {F}.at_cm at_m\n",
    f"let at_m = mag(v(pad))\nlet at_p = 180/pi*cph(v(pad))\nwrdata {F}.at_zo at_m at_p\n",
]
D2S_TRAN_TAIL = WR + f"wrdata {F}.at_tran v(pad)\n"
D2S_NOISE_TAIL = WR + rf"""* ---- appended (ac_tran): output-noise spectrum on a finer grid (the same span as the Vn_int one)
noise v(pad) vd dec 40 10 10meg
let at_on = onoise_total
let at_in = inoise_total
echo $&at_on $&at_in > {F}.at_ntot
setplot previous
wrdata {F}.at_noise onoise_spectrum inoise_spectrum
"""
D2S_EN_TAIL = WR + rf"""wrdata {F}.at_en v(pad) v(vref) i(vio)
* ---- appended (ac_tran): enable at 1 us, disable at 31 us
save v(pad) v(vref) i(vio) i(vcore) v(en_3v3)
alter @Ven[pwl] = [ 0 0 1u 0 1.001u CACE\{{vddl=1.2\}} 31u CACE\{{vddl=1.2\}} 31.001u 0 ]
tran 5n 60u
wrdata {F}.at_endis v(pad) v(vref) i(vio) i(vcore) v(en_3v3)
"""


def patch(src, kind, cell):
    m = re.search(r'\.control\n(.*?)\n\.endc', src, flags=re.S)
    assert m, 'no .control block'
    body = m.group(1)
    lines = body.split('\n')
    echo = max(i for i, l in enumerate(lines) if l.startswith('echo ') and '.data' in l)
    if cell == S2D:
        tail = {'ac': S2D_AC_TAIL, 'tran': S2D_TRAN_TAIL, 'noise': S2D_NOISE_TAIL, 'enable': S2D_EN_TAIL}[kind]
        lines = lines[:echo + 1] + tail.rstrip('\n').split('\n') + lines[echo + 1:]
    else:
        if kind == 'ac':
            out, k = [], 0
            for l in lines:
                out.append(l)
                if l.startswith('ac dec 50 1 1G'):
                    out += D2S_AC_AFTER[k].rstrip('\n').split('\n')
                    k += 1
            assert k == 4, k
            lines = out
        else:
            tail = {'tran': D2S_TRAN_TAIL, 'noise': D2S_NOISE_TAIL, 'enable': D2S_EN_TAIL}[kind]
            lines = lines[:echo + 1] + tail.rstrip('\n').split('\n') + lines[echo + 1:]
    new = src[:m.start(1)] + '\n'.join(lines) + src[m.end(1):]
    new = new.replace('T {CACE template: ', 'T {ac_tran curves (CACE template + wrdata): ', 1)
    return new


def groups(cell):
    """name -> (kind, original CACE group whose spec / variables are reused, conditions)"""
    g = {}
    if cell == S2D:
        g['s2d_ac'] = ('ac', 'ac_params', {'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}})
        g['s2d_tran'] = ('tran', 'tran_params', {'cload': {'enumerate': [0.001, 0.5]},
                                                 'corner_mos': {'enumerate': ['ss', 'tt', 'ff']},
                                                 'temp': {'enumerate': TEMPS}})
        g['s2d_noise'] = ('noise', 'noise_params', {'corner_mos': {'enumerate': CORNERS},
                                                    'temp': {'enumerate': TEMPS}})
        g['s2d_enable'] = ('enable', 'enable_params', {'corner_mos': {'enumerate': ['ss', 'tt', 'ff']},
                                                       'temp': {'enumerate': TEMPS}})
    else:
        slot = {'vref': {'typical': 1.26}, 'vicm': {'typical': 1.26}, 'vterm': {'typical': 1.26}}
        loads = {'cload': {'enumerate': [1e-11, 1e-10, 3e-10, 1e-09]}, 'rload': {'enumerate': [1000, 1e9]}}
        pvt = {'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}}
        tr = {'corner_mos': {'enumerate': ['ss', 'tt', 'ff']}, 'cload': {'enumerate': [1e-11, 1e-10, 3e-10]}}
        g['d2s_ac'] = ('ac', 'ac_params', dict(pvt))
        g['d2s_ac_load'] = ('ac', 'ac_params', dict(loads))
        g['d2s_tran'] = ('tran', 'tran_params', dict(tr))
        g['d2s_noise'] = ('noise', 'noise_params', dict(pvt))
        g['d2s_enable'] = ('enable', 'enable_params', {'sel': {'enumerate': [0, 1, 2]}})
        g['d2s_ac_slot'] = ('ac', 'ac_params', {**slot, **pvt})
        g['d2s_ac_load_slot'] = ('ac', 'ac_params', {**slot, **loads})
        g['d2s_tran_slot'] = ('tran', 'tran_params', {**slot, **tr})
    return g


def main(mdir, cell, source):
    cdir = Path(mdir) / 'verification' / 'cace'
    for kind in ('ac', 'tran', 'noise', 'enable'):
        src = (cdir / 'templates' / f'{cell}_tb_{kind}.sch').read_text()
        (cdir / 'templates' / f'{cell}_tb_at_{kind}.sch').write_text(patch(src, kind, cell))
    y = yaml.safe_load((cdir / f'{cell}.yaml').read_text())
    sfx = '_pex' if source == 'pex' else ''
    y['paths']['runs'] = f'cace/_runs_atg{sfx}'
    y['paths']['documentation'] = f'cace/_docs_atg{sfx}'
    if source == 'pex':
        y['paths']['netlist'] = 'cace/netlist_pex'
        y['paths']['layout'] = 'cace/layout_pex'
    orig = y['parameters']
    par = {}
    for name, (kind, base, cond) in groups(cell).items():
        o = orig[base]
        tool = dict(o['tool']['ngspice'])
        tool['template'] = f'{cell}_tb_at_{kind}.sch'
        tool.pop('collate', None)
        par[name] = {'spec': o['spec'], 'tool': {'ngspice': tool}, 'conditions': cond}
    y['parameters'] = par
    out = cdir / f'_atg_{cell}{sfx}.yaml'
    out.write_text('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                   f'# generated by ac_tran/mkgroups.py from {cell}.yaml (AC / transient / noise curves)\n'
                   + yaml.safe_dump(y, sort_keys=False, allow_unicode=True))
    print(out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
