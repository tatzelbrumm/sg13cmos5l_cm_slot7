#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Tables (markdown, printed) and plots from the result CSVs of run.sh.
Usage: analyze.py <results_dir> <committed_schematic_csv_dir>
<results_dir> holds cace_schematic/, cace_pex/, mc/, bias_dist/ as written by run.sh; plots go to <results_dir>/."""
import csv, os, sys, statistics as st
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

GROUPS = ['vcm_dc_params', 'vcm_dc_3v0_params', 'vref_room_params', 'vref_hot_params', 'vref_cold_params', 'pd_params']
Q = [('Vcm[V]', 'V', 1), ('Vref[V]', 'V', 1), ('Ib[A]', 'uA', 1e6)]

def load(p):
    with open(p) as f:
        r = list(csv.DictReader(l for l in f if not l.startswith('#')))
    return r

def key(row, conds):
    return tuple(row[c] for c in conds)

def cace_tables(res, ref):
    print('### pad_ref_rb: schematic vs magic C-coupled PEX (IHP sg13cmos5l simulation, CACE 2.11, ngspice-47)\n')
    print('Min .. max over the runs of each group; "max |PEX - sch|" = the largest difference of one run between the views')
    print('(runs matched by their conditions); "rerun vs committed" = the same for this schematic rerun against the CSV committed')
    print('in the design repository (2026-11-07).\n')
    print('| group | runs | quantity | committed schematic min .. max | PEX min .. max | max \\|PEX - sch\\| | rerun vs committed max \\|diff\\| |')
    print('|---|---|---|---|---|---|---|')
    out = []
    for g in GROUPS:
        a = load(os.path.join(ref, g + '.csv'))
        b = load(os.path.join(res, 'cace_pex', g + '.csv'))
        c = load(os.path.join(res, 'cace_schematic', g + '.csv'))
        conds = [k for k in a[0] if '[' not in k]
        bm = {key(r, conds): r for r in b}; cm = {key(r, conds): r for r in c}
        for q, u, f in Q:
            xa = [float(r[q]) * f for r in a]; xb = [float(r[q]) * f for r in b]
            d = max(abs(float(bm[key(r, conds)][q]) - float(r[q])) * f for r in a)
            dr = max(abs(float(cm[key(r, conds)][q]) - float(r[q])) * f for r in a)
            fmt = '%.4g'
            if g == 'pd_params':
                fmt = '%.3e'
            print('| %s | %d / %d | %s [%s] | %s .. %s | %s .. %s | %.3g %s | %.3g %s |' % (g, len(a), len(b), q.split('[')[0], u,
                  fmt % min(xa), fmt % max(xa), fmt % min(xb), fmt % max(xb), d, u, dr, u))
    print()

def mc(res):
    r = load(os.path.join(res, 'mc', 'mm_params_runs.csv'))
    print('### pad_ref_rb: local-mismatch Monte Carlo (IHP sg13cmos5l simulation, schematic, tt_mismatch, 27 C, 3.3 V, 100 runs)\n')
    print('| quantity | n | mean | sigma | min | max | mean - 3 sigma .. mean + 3 sigma |')
    print('|---|---|---|---|---|---|---|')
    data = {}
    for q, u, f in Q:
        x = [float(t[q]) * f for t in r]; data[q] = x
        m, s = st.mean(x), st.stdev(x)
        unit = 'mV' if u == 'V' else u
        k = 1e3 if u == 'V' else 1
        print('| %s | %d | %.2f %s | %.3f %s | %.2f %s | %.2f %s | %.2f .. %.2f %s |' % (q.split('[')[0], len(x), m * k, unit, s * k, unit,
              min(x) * k, unit, max(x) * k, unit, (m - 3 * s) * k, (m + 3 * s) * k, unit))
    print()
    fig, ax = plt.subplots(1, 2, figsize=(8, 3))
    for a, q, lab in ((ax[0], 'Vcm[V]', 'vcm [mV]'), (ax[1], 'Vref[V]', 'vref [mV]')):
        a.hist([v * 1e3 for v in data[q]], bins=20, color='#4a6fa5', edgecolor='white')
        a.set_xlabel(lab); a.set_ylabel('runs')
    fig.suptitle('pad_ref_rb mismatch MC, 100 runs, tt 27 C 3.3 V\nIHP sg13cmos5l simulation, schematic', fontsize=9)
    fig.tight_layout(); fig.savefig(os.path.join(res, 'pad_ref_rb_mc_hist.png'), dpi=90); plt.close(fig)

def bd(res):
    print('### bias_dist_pd: copy ratio I(iout<j>) / I(iin0) at 5 uA, all four outputs on, 3.3 V (IHP sg13cmos5l simulation)\n')
    for view in ('schematic', 'magic_pex_2'):
        r = [t for t in load(os.path.join(res, 'bias_dist', 'bias_dist_copy_%s.csv' % view)) if t['case'] == 'on']
        print('View **%s**%s. Ratio min .. max over vc = 0.5 ... 2.5 V (41 points), all four outputs; spread = largest' % (view,
              ' (magic C-coupled extraction of the bias_dist_pd cell of slot_7.gds)' if view != 'schematic' else ' (netlist/source/bias_dist_pd.spice + hv_logic.spice)'))
        print('|ratio(out j) - ratio(out k)| at one vc.\n')
        print('| corner | T [C] | ratio @ 0.5 V | ratio @ 1.0 V | ratio @ 2.5 V | min .. max (all outputs, 0.5 ... 2.5 V) | output spread |')
        print('|---|---|---|---|---|---|---|')
        allr = []
        for c in ['tt', 'ss', 'ff', 'sf', 'fs']:
            for T in ['-40', '27', '125']:
                rows = [t for t in r if t['corner'] == c and t['temp'] == T]
                rat = [[float(t['ratio%d' % j]) for j in range(4)] for t in rows]
                at = lambda v: [t for t in rows if abs(float(t['vc[V]']) - v) < 1e-6][0]
                fl = [x for rr in rat for x in rr]; allr += fl
                sp = max(max(rr) - min(rr) for rr in rat)
                print('| %s | %s | %.4f | %.4f | %.4f | %.4f .. %.4f | %.1e |' % (c, T, float(at(0.5)['ratio0']), float(at(1.0)['ratio0']),
                      float(at(2.5)['ratio0']), min(fl), max(fl), sp))
        print('\nAll corners and temperatures (%s): ratio %.4f .. %.4f, i.e. copy error %+.2f %% .. %+.2f %%.\n' % (view, min(allr), max(allr),
              (min(allr) - 1) * 100, (max(allr) - 1) * 100))
    # leakage
    print('### bias_dist_pd: leakage of the outputs (IHP sg13cmos5l simulation; |I(iout<j>)| max over the 4 outputs and vc = 0.5 ... 2.5 V)\n')
    print('| view | case | corner / T of the maximum | max \\|I\\| per output | at tt 27 C |')
    print('|---|---|---|---|---|')
    for view in ('schematic', 'magic_pex_2'):
        r = load(os.path.join(res, 'bias_dist', 'bias_dist_copy_%s.csv' % view))
        for case, txt in (('off', 'en_3v3 = 0 (block off)'), ('outoff', 'en_3v3 = 1, en_out = 0, input on')):
            rows = [t for t in r if t['case'] == case]
            def mx(rs): return max((abs(float(t['i_out%d[A]' % j])), t['corner'], t['temp']) for t in rs for j in range(4))
            m = mx(rows); m27 = mx([t for t in rows if t['corner'] == 'tt' and t['temp'] == '27'])
            print('| %s | %s | %s / %s C | %.3g pA | %.3g pA |' % (view, txt, m[1], m[2], m[0] * 1e12, m27[0] * 1e12))
    print()
    # plot
    r = [t for t in load(os.path.join(res, 'bias_dist', 'bias_dist_copy_schematic.csv')) if t['case'] == 'on']
    fig, ax = plt.subplots(figsize=(6.5, 3.6))
    cols = {'-40': '#4a6fa5', '27': '#5a9a5a', '125': '#c0504d'}
    ls = {'tt': '-', 'ss': '--', 'ff': ':', 'sf': '-.', 'fs': (0, (5, 1, 1, 1, 1, 1))}
    for c in ['tt', 'ss', 'ff', 'sf', 'fs']:
        for T in ['-40', '27', '125']:
            rows = [t for t in r if t['corner'] == c and t['temp'] == T]
            ax.plot([float(t['vc[V]']) for t in rows], [(float(t['ratio0']) - 1) * 100 for t in rows], color=cols[T], linestyle=ls[c],
                    lw=1.2, label='%s %s C' % (c, T))
    ax.set_xlabel('output voltage vc [V]'); ax.set_ylabel('copy error I(iout)/I(iin) - 1 [%]')
    ax.set_title('bias_dist_pd copy error, 5 uA in, 3.3 V (all outputs equal in this view)\nIHP sg13cmos5l simulation, schematic', fontsize=9)
    ax.grid(alpha=0.3); ax.legend(fontsize=6, ncol=3)
    fig.tight_layout(); fig.savefig(os.path.join(res, 'bias_dist_copy_error.png'), dpi=90); plt.close(fig)
    # MC
    print('### bias_dist_pd: local-mismatch Monte Carlo of the copy ratio (IHP sg13cmos5l simulation, tt_mismatch, 27 C, 3.3 V, 100 runs)\n')
    print('mm_ok=1 added to every MOSFET (pex_for_sim.py --mm-ok); the source netlist of bias_dist_pd has no mm_ok, so this')
    print('MC is new. Ratio at vc = 1.0 V.\n')
    print('| view | output | mean | sigma | min | max |')
    print('|---|---|---|---|---|---|')
    for view in ('schematic', 'magic_pex_2'):
        r = [t for t in load(os.path.join(res, 'bias_dist', 'bias_dist_mc_%s.csv' % view)) if abs(float(t['vc[V]']) - 1.0) < 1e-6]
        for j in range(4):
            x = [float(t['ratio%d' % j]) for t in r]
            print('| %s | iout%d | %.4f | %.4f | %.4f | %.4f |' % (view, j, st.mean(x), st.stdev(x), min(x), max(x)))
        d = [float(t['ratio1']) - float(t['ratio2']) for t in r]
        print('| %s | iout1 - iout2 (the pads\' pair) | %.4f | %.4f | %.4f | %.4f |' % (view, st.mean(d), st.stdev(d), min(d), max(d)))
    print('\n(n = %d iterations per view)\n' % len(r))

if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    res, ref = sys.argv[1], sys.argv[2]
    cace_tables(res, ref); mc(res); bd(res)
