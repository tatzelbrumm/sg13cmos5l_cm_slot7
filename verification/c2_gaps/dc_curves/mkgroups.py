#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Write the DC-curve CACE groups next to a pad's own CACE file (IHP sg13cmos5l simulation).

Usage: mkgroups.py <macro_dir> <cell> <source: schematic|pex>

The sweeps reuse the pad's committed CACE testbench tb_dc (design repository commit 91a7da8b...) unchanged except for
its .control block: same sources (harness iDAC 5 uA into bias_gen_pd, sel 0, en_ctrl_3v3 next to the cell), same
models (MOS corner hv + lv, res / cap / pnp typ, dio_tt), same .options. The new .control block runs one wide DC sweep
and writes it with wrdata to <testbench>_<N>.sweep in the CACE run folder (collect.py reads it); the .data file holds a
dummy 1 (CACE needs a result).

Writes <cace_dir>/_dcg_<cell>[_pex].yaml (copy of the cell yaml: same pins / default_conditions / paths, parameters
replaced by the groups below; pex: own runs / netlist / docs folders and a layout path, as the S2D Makefile's
sim-cace CACE_SOURCE=pex) and <cace_dir>/templates/<cell>_tb_dcsweep.sch.
"""
import re
import sys
from pathlib import Path

import yaml

S2D, D2S = 'sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single'
CORNERS = ['ss', 'sf', 'tt', 'fs', 'ff']
TEMPS = [-40, 27, 125]

# S2D: pad = vref + u through rsrc (50 Ohm); sweep the pad source from -0.3 V to 3.3 V in 2 mV steps.
S2D_CONTROL = r""".control
save v(pad) v(outp) v(outn) v(vcm) v(vref) v(u) i(vio)
dc Vu CACE[-0.3 - CACE\{vref=1.2\}] CACE[3.3 - CACE\{vref=1.2\}] 0.002
set wr_singlescale
set wr_vecnames
option numdgt=9
wrdata CACE\{filename\}_CACE\{N\}.sweep v(u) v(pad) v(outp) v(outn) v(vcm) v(vref) i(vio)
echo 1 > CACE\{filename\}_CACE\{N\}.data
.endc"""

# D2S: vinp - vinn = v(dp) around vicm (vinp = vicm + dp/2, vinn = vicm - dp/2); dp swept from 0 V outward in 5 mV
# steps, to +vdmax and to -vdmax (inputs stay inside 0 ... 3.3 V at vicm = 1.65 V). Two branches from the operating
# point at dp = 0: a single sweep starting at dp = -3.3 V (both inputs at the rails) did not finish in 13 min at
# tt / -40 C / 3.3 V and ff / -40 C / 3.6 V (schematic), while the other runs took about 1 min.
D2S_CONTROL = r""".control
save v(pad) v(vinp) v(vinn) v(vref) v(dp) i(vio)
set wr_singlescale
set wr_vecnames
option numdgt=9
dc Vd 0 CACE\{vdmax=3.3\} 0.005
wrdata CACE\{filename\}_CACE\{N\}.sweep_p v(dp) v(pad) v(vinp) v(vinn) v(vref) i(vio)
dc Vd 0 CACE[-CACE\{vdmax=3.3\}] -0.005
wrdata CACE\{filename\}_CACE\{N\}.sweep_n v(dp) v(pad) v(vinp) v(vinn) v(vref) i(vio)
echo 1 > CACE\{filename\}_CACE\{N\}.data
.endc"""


def groups(cell):
    g = {}
    if cell == S2D:
        # corner grid at the window_params conditions (vref 0.5 V; vcm, ibias, rsrc, cload at the yaml defaults)
        g['s2d_grid'] = {'vref': {'typical': 0.5}, 'vcm': {'typical': 1.2}, 'vdd': {'enumerate': [3.0, 3.3, 3.6]},
                         'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}}
        # the slot's nominal replica values (pad_ref_rb tt 27 C: vref_s2d about 0.49 V, vcm about 1.26 V)
        g['s2d_slot'] = {'vref': {'typical': 0.49}, 'vcm': {'typical': 1.26}, 'vdd': {'enumerate': [3.0, 3.3, 3.6]},
                         'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}}
        # range vs vref and vcm (the range_params grid: vref 0.5 / 0.8 / 1.2 / 1.65, vcm 1.0 ... 1.65)
        g['s2d_vrefvcm'] = {'vref': {'enumerate': [0.5, 0.8, 1.2, 1.65]}, 'vcm': {'enumerate': [1.0, 1.2, 1.4, 1.65]},
                            'vdd': {'enumerate': [3.0, 3.3]}, 'corner_mos': {'enumerate': ['ss', 'tt', 'ff']},
                            'temp': {'enumerate': [-40, 27, 125]}}
    else:
        # corner grid at the dc_params / dc_3v0_params conditions (vref = vicm = vterm 1.65 V, 1 kOhm to vterm,
        # 100 pF), iovdd 3.0 / 3.3 / 3.6 V
        g['d2s_grid'] = {'vdd': {'enumerate': [3.0, 3.3, 3.6]}, 'corner_mos': {'enumerate': CORNERS},
                         'temp': {'enumerate': TEMPS}}
        # unloaded (1 TOhm to vterm instead of 1 kOhm)
        g['d2s_noload'] = {'rload': {'typical': 1e12}, 'vdd': {'enumerate': [3.0, 3.3, 3.6]},
                           'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}}
        # the slot's operating point: vref = vicm = vcm 1.26 V, 1 kOhm to vref (vterm 1.26 V); dp to +-2.52 V keeps
        # the inputs inside 0 ... 2.52 V
        # solver-aid check: vd 0 ... +-1 V (the CACE INL span) at a few PVT points, run with and without rshunt
        # (cace_dc.sh NORSHUNT=1) to separate the effect of rshunt=1e12 from that of the sweep
        g['d2s_rshunt_chk'] = {'vdmax': {'typical': 1.0}, 'vdd': {'enumerate': [3.0, 3.3]},
                               'corner_mos': {'enumerate': ['ss', 'tt']}, 'temp': {'enumerate': [-40, 27]}}
        g['d2s_slot'] = {'vref': {'typical': 1.26}, 'vicm': {'typical': 1.26}, 'vterm': {'typical': 1.26},
                         'vdmax': {'typical': 2.52}, 'vdd': {'enumerate': [3.0, 3.3, 3.6]},
                         'corner_mos': {'enumerate': CORNERS}, 'temp': {'enumerate': TEMPS}}
    return g


def main(mdir, cell, source):
    cdir = Path(mdir) / 'verification' / 'cace'
    src = (cdir / 'templates' / f'{cell}_tb_dc.sch').read_text()
    ctl = S2D_CONTROL if cell == S2D else D2S_CONTROL
    new, n = re.subn(r'\.control\n.*?\n\.endc', lambda m: ctl, src, count=1, flags=re.S)
    assert n == 1, 'no .control block in tb_dc'
    new = new.replace('CACE template: DC transfer', 'DC-curve sweep (from tb_dc): DC transfer', 1)
    (cdir / 'templates' / f'{cell}_tb_dcsweep.sch').write_text(new)
    y = yaml.safe_load((cdir / f'{cell}.yaml').read_text())
    if source == 'pex':
        y['paths']['runs'] = 'cace/_runs_dcg_pex'
        y['paths']['documentation'] = 'cace/_docs_dcg_pex'
        y['paths']['netlist'] = 'cace/netlist_pex'
        y['paths']['layout'] = 'cace/layout_pex'
    else:
        y['paths']['runs'] = 'cace/_runs_dcg'
        y['paths']['documentation'] = 'cace/_docs_dcg'
    spec = {'ok': {'display': 'sweep written', 'minimum': {'value': 'any'}, 'typical': {'value': 'any'},
                   'maximum': {'value': 'any'}}}
    y['parameters'] = {
        name: {'spec': spec,
               'tool': {'ngspice': {'template': f'{cell}_tb_dcsweep.sch', 'format': 'ascii', 'suffix': '.data',
                                    'variables': ['ok']}},
               'conditions': cond}
        for name, cond in groups(cell).items()}
    out = cdir / f'_dcg_{cell}{"_pex" if source == "pex" else ""}.yaml'
    out.write_text('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                   f'# generated by dc_curves/mkgroups.py from {cell}.yaml (DC-curve sweeps)\n'
                   + yaml.safe_dump(y, sort_keys=False, allow_unicode=True))
    print(out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
