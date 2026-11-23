#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""bias_dist_pd copy accuracy and disabled leakage, IHP sg13cmos5l ngspice DC sweeps.

Usage: bias_dist_copy.py <design_tree> <work_dir> <out_dir> [--dut schematic|<extracted.spice>] [-j N]
Testbench: vddh = 3.3 V; ideal 5 uA sourced into iin0 (en_in0 = 1, en_in1..3 = 0, iin1..3 open); all four outputs
iout0..3 held at one voltage vc by a 0 V ammeter each; vc swept 0.5 ... 2.5 V in 50 mV steps.
Ratio = I(iout<j>) / 5 uA (current sourced out of the block); i_in0 = the current that enters iin0 (5 uA unless the
input switch is open: then the ideal source is clamped by a diode to 2.6 V, about 3.4 V at iin0). Cases:
  on      en_3v3 = 1, en_out0..3 = 1                (copy accuracy)
  outoff  en_3v3 = 1, en_out0..3 = 0                (output switch off, input enabled: leakage per output)
  off     en_3v3 = 0 (en_3v3_b = 1), all enables 1  (block disabled: leakage per output)
Corners mos_{tt,ss,ff,sf,fs} (hv and lv libraries), temperatures -40 / 27 / 125 C.
Output: <out_dir>/bias_dist_copy_<schematic|magic_pex_2>.csv: dut,case,corner,temp,vc,i_out0..3 [A], ratio0..3 (on only).
"""
import os, subprocess, sys, itertools
from concurrent.futures import ThreadPoolExecutor

CORNERS = ['tt', 'ss', 'ff', 'sf', 'fs']
TEMPS = [-40, 27, 125]
CASES = {'on': (3.3, 0.0, 3.3), 'outoff': (3.3, 0.0, 0.0), 'off': (0.0, 3.3, 3.3)}
IIN = 5e-6

def deck(tree, dut, corner, temp, case, data):
    en, enb, eo = CASES[case]
    if dut == 'schematic':
        inc = ['.include %s/macros/hv_logic/netlist/source/hv_logic.spice' % tree,
               '.include %s/macros/bias_dist_pd/netlist/source/bias_dist_pd.spice' % tree]
        sub = 'bias_dist_pd'
    else:
        inc = ['.include %s' % dut]
        sub = 'bias_dist_pd'
    return '\n'.join(['* bias_dist_pd copy accuracy: %s %s %s C case %s' % (dut, corner, temp, case),
        '.lib cornerMOShv.lib mos_%s' % corner, '.lib cornerMOSlv.lib mos_%s' % corner] + inc + [
        'Vdd vdd 0 3.3', 'Ven en 0 %g' % en, 'Venb enb 0 %g' % enb, 'Vi0 ei0 0 3.3', 'Vi1 ei1 0 0', 'Vi2 ei2 0 0',
        'Vi3 ei3 0 0', 'Veo eo 0 %g' % eo,
        'Iin 0 src %g' % IIN, 'Vmi src iin0 0',
        '* clamp of the input node while the input switch is open (a real source saturates near its supply)',
        'Dcl src vcl dcl', 'Vcl vcl 0 2.6', '.model dcl d is=1e-20 n=1',
        'Rf1 iin1 0 1e12', 'Rf2 iin2 0 1e12', 'Rf3 iin3 0 1e12',
        'Vc vc 0 1.0'] + ['Vm%d iout%d vc 0' % (j, j) for j in range(4)] + [
        'X1 vdd 0 en enb iin0 iin1 iin2 iin3 ei0 ei1 ei2 ei3 iout0 iout1 iout2 iout3 eo eo eo eo %s' % sub,
        '.temp %g' % temp,
        '.options gmin=1e-15 reltol=1e-5 abstol=1e-15',
        '.control', 'dc Vc 0.5 2.5 0.05',
        'wrdata %s i(Vm0) i(Vm1) i(Vm2) i(Vm3) i(Vmi)' % data, '.endc', '.end', ''])

def run(args):
    tree, work, dut, corner, temp, case = args
    tag = '%s_%s_%s' % (corner, temp, case)
    d = os.path.join(work, tag); os.makedirs(d, exist_ok=True)
    pi = os.path.join(os.environ['PDK_ROOT'], os.environ['PDK'], 'libs.tech/ngspice/.spiceinit')
    open(os.path.join(d, '.spiceinit'), 'w').write(open(pi).read())
    open(os.path.join(d, 'tb.spice'), 'w').write(deck(tree, dut, corner, temp, case, 'out.data'))
    p = subprocess.run(['ngspice', '-b', 'tb.spice'], cwd=d, capture_output=True, text=True)
    open(os.path.join(d, 'ngspice.log'), 'w').write(p.stdout + p.stderr)
    rows = []
    f = os.path.join(d, 'out.data')
    if not os.path.exists(f):
        print('FAILED', tag); return []
    for ln in open(f):
        t = ln.split()
        if len(t) < 10: continue
        try: vals = [float(x) for x in t]
        except ValueError: continue
        vc = vals[0]; i = [vals[1], vals[3], vals[5], vals[7]]
        # current through Vm<j> flows iout<j> -> vc, i.e. the current sourced out of the block
        iin = vals[9]
        rows.append([case, corner, temp, '%.3f' % vc, '%.6e' % iin] + ['%.6e' % x for x in i] +
                    (['%.6f' % (x / IIN) for x in i] if case == 'on' else ['', '', '', '']))
    return rows

def main(a):
    if len(a) < 3: sys.exit(__doc__)
    tree, work, out = [os.path.abspath(x) for x in a[:3]]
    dut = 'schematic'; jobs = 2
    if '--dut' in a: dut = a[a.index('--dut') + 1]
    if dut != 'schematic': dut = os.path.abspath(dut)
    if '-j' in a: jobs = int(a[a.index('-j') + 1])
    jobs_l = [(tree, work, dut, c, t, k) for k in CASES for c in CORNERS for t in TEMPS]
    with ThreadPoolExecutor(jobs) as ex:
        res = list(ex.map(run, jobs_l))
    os.makedirs(out, exist_ok=True)
    name = 'schematic' if dut == 'schematic' else 'magic_pex_2'
    fn = os.path.join(out, 'bias_dist_copy_%s.csv' % name)
    with open(fn, 'w') as f:
        f.write('dut,case,corner,temp,vc[V],i_in0[A],i_out0[A],i_out1[A],i_out2[A],i_out3[A],ratio0,ratio1,ratio2,ratio3\n')
        n = 0
        for r in res:
            for row in r:
                f.write(','.join([name] + [str(x) for x in row]) + '\n'); n += 1
    print('%d rows -> %s' % (n, fn))

if __name__ == '__main__':
    main(sys.argv[1:])
