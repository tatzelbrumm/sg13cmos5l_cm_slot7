#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""bias_dist_pd: local-mismatch Monte Carlo of the copy ratio per output, IHP sg13cmos5l ngspice, tt_mismatch.

Usage: bias_dist_mc.py <dut.spice> <work_dir> <out.csv> [-n 100] [-j 2] [--temp 27]
<dut.spice> must hold subckt bias_dist_pd (and what it needs) with mm_ok=1 on every MOSFET (pex_for_sim.py --mm-ok).
Same testbench as bias_dist_copy.py, case on (en_3v3 = 1, en_in0 = 1, en_out0..3 = 1, 5 uA into iin0), 3.3 V, vc
= 0.5 / 1.0 / 1.5 / 2.0 / 2.5 V; one ngspice run per iteration with .options SEED = 12345 + iteration.
Output CSV: iteration,vc[V],ratio0..3 (= I(iout<j>) / 5 uA)."""
import os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
IIN = 5e-6

def run(a):
    dut, work, it, temp = a
    d = os.path.join(work, 'it%03d' % it); os.makedirs(d, exist_ok=True)
    pi = os.path.join(os.environ['PDK_ROOT'], os.environ['PDK'], 'libs.tech/ngspice/.spiceinit')
    open(os.path.join(d, '.spiceinit'), 'w').write(open(pi).read())
    open(os.path.join(d, 'tb.spice'), 'w').write('\n'.join([
        '* bias_dist_pd mismatch MC iteration %d' % it,
        '.lib cornerMOShv.lib mos_tt_mismatch', '.lib cornerMOSlv.lib mos_tt_mismatch', '.include %s' % dut,
        'Vdd vdd 0 3.3', 'Ven en 0 3.3', 'Venb enb 0 0', 'Vi0 ei0 0 3.3', 'Vi1 ei1 0 0', 'Vi2 ei2 0 0', 'Vi3 ei3 0 0',
        'Veo eo 0 3.3', 'Iin 0 iin0 %g' % IIN, 'Rf1 iin1 0 1e12', 'Rf2 iin2 0 1e12', 'Rf3 iin3 0 1e12', 'Vc vc 0 1.0'] +
        ['Vm%d iout%d vc 0' % (j, j) for j in range(4)] + [
        'X1 vdd 0 en enb iin0 iin1 iin2 iin3 ei0 ei1 ei2 ei3 iout0 iout1 iout2 iout3 eo eo eo eo bias_dist_pd',
        '.temp %g' % temp, '.options gmin=1e-15 reltol=1e-5 abstol=1e-15 SEED=%d' % (12345 + it),
        '.control', 'dc Vc 0.5 2.5 0.5', 'wrdata out.data i(Vm0) i(Vm1) i(Vm2) i(Vm3)', '.endc', '.end', '']))
    subprocess.run(['ngspice', '-b', 'tb.spice'], cwd=d, capture_output=True, text=True)
    rows = []
    f = os.path.join(d, 'out.data')
    if not os.path.exists(f): return rows
    for ln in open(f):
        t = ln.split()
        try: v = [float(x) for x in t]
        except ValueError: continue
        if len(v) < 8: continue
        rows.append([it, '%.2f' % v[0]] + ['%.6f' % (v[k] / IIN) for k in (1, 3, 5, 7)])
    return rows

def main(a):
    if len(a) < 3: sys.exit(__doc__)
    dut, work, out = [os.path.abspath(x) for x in a[:3]]
    n = int(a[a.index('-n') + 1]) if '-n' in a else 100
    j = int(a[a.index('-j') + 1]) if '-j' in a else 2
    temp = float(a[a.index('--temp') + 1]) if '--temp' in a else 27
    with ThreadPoolExecutor(j) as ex:
        res = list(ex.map(run, [(dut, work, i, temp) for i in range(n)]))
    with open(out, 'w') as f:
        f.write('iteration,vc[V],ratio0,ratio1,ratio2,ratio3\n')
        k = 0
        for r in res:
            for row in r: f.write(','.join(str(x) for x in row) + '\n'); k += 1
    print('%d rows (%d iterations) -> %s' % (k, sum(1 for r in res if r), out))

if __name__ == '__main__':
    main(sys.argv[1:])
