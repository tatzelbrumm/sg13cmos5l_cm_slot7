#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Plots for HOW_IT_WORKS.md, made only from committed simulation data (no simulation is run).

usage: python3 -I make_plots.py [--design-cache DIR]

Sources (paths relative to the root of this repository unless marked "design"):
  bg_core_current_vs_temp.png   verification/c2_gaps/slot_modes_bg/bg_core_dc.csv
  pex_vs_schematic_s2d.png      design 91a7da8b: macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/
                                sg13cmos5l_IOPadSingle2Diff{,_pex}/<group>.csv
  pex_vs_schematic_d2s.png      design 91a7da8b: macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/
                                sg13cmos5l_IOPadDiff2Single/<group>.csv (schematic) and
                                verification/c2_gaps/d2s_pex/csv/<group>_pex_rshunt1e12.csv (extracted)
  bias_dist_mismatch_hist.png   verification/c2_gaps/replica_bias/results/bias_dist/bias_dist_mc_{schematic,magic_pex_2}.csv
  pad_ref_rb_vcm_vref_pvt.png   verification/c2_gaps/replica_bias/results/cace_schematic/{vcm_dc,vcm_dc_3v0}_params.csv

The design-repository files are read with `git show` from a blob-less shallow clone of
https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single at commit 91a7da8b (only the CSVs read are
downloaded). The clone is kept in --design-cache (default: $XDG_CACHE_HOME or ~/.cache, subfolder slot7_make_plots).
The script prints the numbers it plots, so they can be checked against the tables in HOW_IT_WORKS.md.
"""
import argparse
import csv
import io
import os
import statistics
import subprocess
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]                      # repository root (docs/chipalooza2_as_taped_out/pix/plots -> root)
GAPS = ROOT / 'verification' / 'c2_gaps'
URL = 'https://github.com/tatzelbrumm/sg13cmos5l_cm_ip__single2diff2single'
C91 = '91a7da8b67ac56a26c605501146667a1fde28c32'

# style of verification/c2_gaps/dc_curves/common.py (same colors per MOS corner, same rcParams)
CORNERS = ['tt', 'ss', 'ff', 'sf', 'fs']
COLOR = {'tt': '#2a78d6', 'ss': '#eb6834', 'ff': '#1baf7a', 'sf': '#eda100', 'fs': '#e87ba4'}
VLS = {3.0: ':', 3.3: '-', 3.6: '--'}
VIEWCOL = {'schematic': '#2a78d6', 'pex': '#eb6834'}


def style():
    plt.rcParams.update({'figure.dpi': 150, 'savefig.dpi': 150, 'font.size': 9, 'axes.titlesize': 9.5,
                         'axes.grid': True, 'grid.color': '#d8d8d4', 'grid.linewidth': 0.6, 'axes.edgecolor': '#52514e',
                         'axes.labelcolor': '#0b0b0b', 'xtick.color': '#52514e', 'ytick.color': '#52514e',
                         'lines.linewidth': 1.4, 'legend.fontsize': 7.5, 'legend.framealpha': 0.9,
                         'figure.facecolor': 'white'})


def save(fig, name):
    p = HERE / name
    fig.savefig(p, metadata={'Copyright': '2026 Christoph Maier, Apache-2.0'})
    plt.close(fig)
    print('wrote %s (%d bytes)' % (p.relative_to(ROOT), p.stat().st_size))


def read_csv_text(text):
    rows = list(csv.reader(l for l in io.StringIO(text) if not l.startswith('#')))
    return rows[0], rows[1:]


def read_csv(path):
    return read_csv_text(Path(path).read_text())


class Design:
    """Reads files of the design repository at a fixed commit (blob-less shallow clone, git show)."""

    def __init__(self, cache):
        self.repo = Path(cache) / 'design'
        if not (self.repo / '.git').exists():
            self.repo.parent.mkdir(parents=True, exist_ok=True)
            subprocess.run(['git', 'clone', '-q', '--depth', '1', '--filter=blob:none', '--no-checkout', URL,
                            str(self.repo)], check=True)
        self.fetched = set()

    def show(self, commit, path):
        if commit not in self.fetched:
            subprocess.run(['git', '-C', str(self.repo), 'fetch', '-q', '--depth', '1', 'origin', commit], check=True)
            self.fetched.add(commit)
        return subprocess.run(['git', '-C', str(self.repo), 'show', '%s:%s' % (commit, path)], check=True,
                              capture_output=True, text=True).stdout


# ----------------------------------------------------------------------------------------------------------------
# (i) bg_core_pd output current vs temperature
def plot_bg():
    head, rows = read_csv(GAPS / 'slot_modes_bg' / 'bg_core_dc.csv')
    ix = {h: i for i, h in enumerate(head)}
    d = {}
    for r in rows:
        if r[ix['view']] != 'schematic':
            continue
        d[(r[ix['mos']], r[ix['res']], int(r[ix['temp']]), float(r[ix['vdd']]))] = float(r[ix['i_op_uA']])
    temps = [-40, 27, 125]
    res_ls = {'res_bcs': '--', 'res_typ': '-', 'res_wcs': ':'}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 4.3), gridspec_kw={'width_ratios': [1, 1]})
    for res in ['res_bcs', 'res_typ', 'res_wcs']:
        for c in CORNERS:
            y = [d[(c, res, t, 3.3)] for t in temps]
            a1.plot(temps, y, res_ls[res], color=COLOR[c], marker='o', ms=3,
                    label=c if res == 'res_typ' else None)
            # right: deviation from the tt MOS corner at the same rhigh corner, T, 3.3 V
            dev = [100 * (d[(c, res, t, 3.3)] / d[('tt', res, t, 3.3)] - 1) for t in temps]
            a2.plot(temps, dev, res_ls[res], color=COLOR[c], marker='o', ms=3)
        a1.annotate(res.replace('res_', 'rhigh '), (125, d[('tt', res, 125, 3.3)]), xytext=(6, 0),
                    textcoords='offset points', va='center', fontsize=7.5, color='#52514e')
    a1.set_xlim(-55, 165)
    a1.set_xlabel('temperature [°C]')
    a1.set_ylabel('iout into 0.7 V [µA]')
    a1.set_title('output current, iovdd 3.3 V')
    a1.legend(title='MOS corner (color)', ncol=5, loc='center', bbox_to_anchor=(0.5, 0.3), fontsize=7,
               title_fontsize=7.5, columnspacing=0.8, handlelength=1.4)
    a2.set_xlabel('temperature [°C]')
    a2.set_ylabel('I / I(tt, same rhigh corner and T) − 1 [%]')
    a2.set_title('MOS corner effect only (3.3 V)')
    a2.set_ylim(-0.3, 0.3)
    a2.plot([], [], 'k--', label='rhigh bcs')
    a2.plot([], [], 'k-', label='rhigh typ')
    a2.plot([], [], 'k:', label='rhigh wcs')
    a2.legend(title='line style', fontsize=7, title_fontsize=7.5, loc='upper right')
    fig.suptitle('bg_core_pd alone: output current over temperature, MOS corner and rhigh corner\n'
                 'IHP sg13cmos5l simulation (schematic), .op, data: verification/c2_gaps/slot_modes_bg/bg_core_dc.csv',
                 fontsize=9)
    fig.tight_layout()
    save(fig, 'bg_core_current_vs_temp.png')
    allv = [v for k, v in d.items()]
    mos = max(abs(d[(c, r, t, v)] / d[('tt', r, t, v)] - 1) for (c, r, t, v) in d)
    print('  bg: schematic %d points, %.3f .. %.3f uA; typ %.4f; max MOS-corner deviation %.2f %%'
          % (len(allv), min(allv), max(allv), d[('tt', 'res_typ', 27, 3.3)], 100 * mos))


# ----------------------------------------------------------------------------------------------------------------
# (ii) PEX vs schematic, per quantity
S2D_Q = [('dc_params', 'Gain[]', 'gain'), ('dc_params', 'INL[mV]', 'INL'), ('dc_params', 'Vcm_err[mV]', 'output CM error'),
         ('dc_params', 'Iio[A]', 'IO ring current'), ('window_params', 'Vin_max[V]', 'input range, high end'),
         ('range_params', 'Gain[]', 'gain vs vref / vcm'), ('range_params', 'Vcm_err[mV]', 'CM error vs vref / vcm'),
         ('dc_ibias_params', 'Iio[A]', 'IO ring current vs ibias'),
         ('ac_params', 'Acl_dB[dB]', 'closed-loop gain (dB)'), ('ac_params', 'f3dB[MHz]', '−3 dB bandwidth'),
         ('ac_params', 'CMvdd_1k[dB]', 'CM response to iovdd (dB)'), ('tran_params', 't_rise[s]', 'rise time 10–90 %'),
         ('tran_params', 't_settle[s]', 'settling time 1 %'), ('tran_params', 'Vcm_dev[mV]', 'CM deviation in step'),
         ('noise_params', 'En_1k[nV/rtHz]', 'input noise 1 kHz'), ('noise_params', 'En_100k[nV/rtHz]', 'input noise 100 kHz'),
         ('noise_params', 'Vn_out[uV]', 'output noise 10 Hz–10 MHz'), ('enable_params', 't_on[us]', 'enable time'),
         ('enable_params', 'Vc_max[V]', 'CM glitch at enable'), ('enable_params', 'Iio_on[A]', 'IO current after enable')]
D2S_Q = [('dc_params', 'Gain[]', 'gain'), ('dc_params', 'INL[mV]', 'INL'), ('dc_params', 'Iio[A]', 'IO ring current'),
         ('dc_params', 'IqP[A]', 'quiescent current OP'), ('dc_params', 'Imin[A]', 'min. output-device current'),
         ('ac_params', 'Acl_dB[dB]', 'closed-loop gain (dB)'), ('ac_params', 'f3dB[MHz]', '−3 dB bandwidth'),
         ('ac_params', 'PSRR_1k[dB]', 'PSRR 1 kHz (dB)'), ('ac_params', 'PSRR_100k[dB]', 'PSRR 100 kHz (dB)'),
         ('ac_params', 'CMRR_1k[dB]', 'CMRR 1 kHz (dB)'), ('ac_params', 'Zout_1M[Ω]', 'output impedance 1 MHz'),
         ('ac_load_params', 'f3dB[MHz]', '−3 dB bandwidth, 10…300 pF'), ('tran_params', 'SR_rise[V/us]', 'slew rate, rising'),
         ('tran_params', 'SR_fall[V/us]', 'slew rate, falling'), ('tran_params', 'ts_rise[us]', 'settling time, rising'),
         ('tran_params', 'ts_fall[us]', 'settling time, falling'), ('noise_params', 'En_1k[nV/rtHz]', 'output noise 1 kHz'),
         ('noise_params', 'Vn_int[uV]', 'integrated output noise'), ('drive_params', 'Vout_max[V]', 'max. output'),
         ('drive_params', 'Vout_min[V]', 'min. output'), ('drive_params', 'Isc_src[mA]', 'short-circuit source'),
         ('drive_params', 'Isc_snk[mA]', 'short-circuit sink'), ('enable_params', 't_on[us]', 'enable time'),
         ('enable_params', 'Iio_end[A]', 'IO current after enable'), ('thd_params', 'THD[dB]', 'THD (dB)')]


def changes(hs, rs, hp, rp, q):
    """Per-run relative change (PEX - sch) / |sch| in %, runs matched by their condition columns (as d2s_pex/compare.py)."""
    cond_s = [i for i, h in enumerate(hs) if '[' not in h]
    cond_names = [hs[i] for i in cond_s]
    ip = {h: i for i, h in enumerate(hp)}
    mp = {}
    for r in rp:
        mp.setdefault(tuple(r[ip[n]] for n in cond_names), r)
    i_s, i_p = hs.index(q), hp.index(q)
    out, med_s, med_p = [], [], []
    for r in rs:
        k = tuple(r[i] for i in cond_s)
        try:
            a = float(r[i_s])
        except ValueError:
            continue
        med_s.append(a)
        if k in mp:
            try:
                b = float(mp[k][i_p])
            except ValueError:
                continue
            if a != 0:
                out.append(100 * (b - a) / abs(a))
    for r in rp:
        try:
            med_p.append(float(r[i_p]))
        except ValueError:
            pass
    return out, med_s, med_p


def plot_pex(name, title, quantities, load_s, load_p, note):
    labels, med, lo, hi, ns = [], [], [], [], []
    cache = {}
    for g, q, lab in quantities:
        if g not in cache:
            cache[g] = (load_s(g), load_p(g))
        (hs, rs), (hp, rp) = cache[g]
        ch, vs, vp = changes(hs, rs, hp, rp, q)
        if not ch:
            print('  %s: %s %s: no matched runs, skipped' % (name, g, q))
            continue
        # bar = change of the median over all runs of each view; whisker = range of the per-run change
        m = 100 * (statistics.median(vp) - statistics.median(vs)) / abs(statistics.median(vs))
        labels.append('%s  (%s)' % (lab, g.replace('_params', '')))
        med.append(m)
        lo.append(min(ch))
        hi.append(max(ch))
        ns.append(len(ch))
        print('  %-14s %-16s %-16s median sch %.5g pex %.5g -> %+.2f %%; per-run %+.2f .. %+.2f %% (n=%d)'
              % (name, g, q, statistics.median(vs), statistics.median(vp), m, min(ch), max(ch), len(ch)))
    n = len(labels)
    fig, ax = plt.subplots(figsize=(8.4, 0.27 * n + 2.0))
    y = np.arange(n)[::-1]
    col = ['#eb6834' if v < 0 else '#2a78d6' for v in med]
    ax.barh(y, med, color=col, height=0.62, zorder=2)
    ax.hlines(y, lo, hi, color='#0b0b0b', lw=0.9, zorder=3)
    ax.plot(lo, y, '|', color='#0b0b0b', ms=5, zorder=3)
    ax.plot(hi, y, '|', color='#0b0b0b', ms=5, zorder=3)
    ax.axvline(0, color='#52514e', lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.3)
    xmin, xmax = min(lo + med + [0.0]), max(hi + med + [0.0])
    span = max(xmax - xmin, 2.0)
    ax.set_xlim(xmin - 0.16 * span, xmax + 0.16 * span)
    for yy, v, a, b in zip(y, med, lo, hi):
        if v >= 0:
            ax.annotate('%+.1f %%' % v, (max(v, b), yy), xytext=(4, 0), textcoords='offset points', ha='left',
                        va='center', fontsize=6.5, color='#52514e', zorder=4)
        else:
            ax.annotate('%+.1f %%' % v, (min(v, a), yy), xytext=(-4, 0), textcoords='offset points', ha='right',
                        va='center', fontsize=6.5, color='#52514e', zorder=4)
    ax.set_xlabel('extracted layout vs schematic [%]', fontsize=8.5)
    ax.set_title(title, fontsize=8.6)
    fig.text(0.01, 0.005, 'Bar = change of the median over all runs of each view; whisker = range of the per-run change '
             '(runs matched by their conditions).\n' + note, fontsize=6.6, color='#52514e', ha='left', va='bottom')
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    save(fig, name)


def plot_pex_both(design):
    s2d = 'macros/sg13cmos5l_IOPadSingle2Diff/verification/cace/results/'
    plot_pex('pex_vs_schematic_s2d.png',
             'S2D pad (sg13cmos5l_IOPadSingle2Diff): magic C-coupled PEX vs schematic, CACE groups\n'
             'IHP sg13cmos5l simulation; both views: design repository 91a7da8b (2026-11-05)',
             S2D_Q,
             lambda g: read_csv_text(design.show(C91, s2d + 'sg13cmos5l_IOPadSingle2Diff/%s.csv' % g)),
             lambda g: read_csv_text(design.show(C91, s2d + 'sg13cmos5l_IOPadSingle2Diff_pex/%s.csv' % g)),
             'Not plotted (values near zero, a % change has no meaning): systematic offset, pad range low end,\n'
             'overshoot, power-down currents and voltages.')
    d2s = 'macros/sg13cmos5l_IOPadDiff2Single/verification/cace/results/sg13cmos5l_IOPadDiff2Single/'
    plot_pex('pex_vs_schematic_d2s.png',
             'D2S pad (sg13cmos5l_IOPadDiff2Single): magic C-coupled PEX of the taped-out cell vs schematic\n'
             'IHP sg13cmos5l simulation; schematic: design repository 91a7da8b; PEX: verification/c2_gaps/d2s_pex/csv',
             D2S_Q,
             lambda g: read_csv_text(design.show(C91, d2s + '%s.csv' % g)),
             lambda g: read_csv(GAPS / 'd2s_pex' / 'csv' / ('%s_pex_rshunt1e12.csv' % g)),
             'PEX runs with ngspice rshunt = 1e12 (schematic runs without); the committed schematic results predate the layout\n'
             '(Miller capacitor shape). Not plotted (near zero): offset, core current, peaking, overshoot, glitches, power-down.')


# ----------------------------------------------------------------------------------------------------------------
# (iii) bias_dist_pd mismatch histogram
def plot_bias_dist():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.9))
    bins = np.arange(-4.0, 5.01, 0.25)
    bins_d = np.arange(-1.2, 1.21, 0.1)
    for view, lab in [('schematic', 'schematic'), ('magic_pex_2', 'magic PEX')]:
        head, rows = read_csv(GAPS / 'replica_bias' / 'results' / 'bias_dist' / ('bias_dist_mc_%s.csv' % view))
        ix = {h: i for i, h in enumerate(head)}
        r1 = [r for r in rows if abs(float(r[ix['vc[V]']]) - 1.0) < 1e-9]
        e = np.array([[100 * (float(r[ix['ratio%d' % j]]) - 1) for j in range(4)] for r in r1])
        col = VIEWCOL['schematic' if view == 'schematic' else 'pex']
        a1.hist(e.ravel(), bins=bins, histtype='step', lw=1.5, color=col,
                label='%s: 4 outputs × %d runs, mean %+.2f %%, σ %.2f %%' % (lab, len(r1), e.mean(), e.std(ddof=1)))
        d = e[:, 1] - e[:, 2]
        a2.hist(d, bins=bins_d, histtype='step', lw=1.5, color=col,
                label='%s: σ %.2f %%' % (lab, d.std(ddof=1)))
        print('  bias_dist %s: n=%d, per output sigma %s %%, iout1-iout2 sigma %.3f %%'
              % (view, len(r1), ' '.join('%.2f' % s for s in e.std(axis=0, ddof=1)), d.std(ddof=1)))
    a1.axvline(0, color='#52514e', lw=0.8)
    a1.set_xlabel('copy error I(iout<j>) / I(iin0) − 1 [%]')
    a1.set_ylabel('count')
    a1.set_title('each output (iout0 … iout3 pooled)')
    a1.legend(fontsize=6.6, loc='upper left')
    a2.axvline(0, color='#52514e', lw=0.8)
    a2.set_xlabel('iout1 − iout2 (S2D − D2S copy) [% of 5 µA]')
    a2.set_title('the two pads\' outputs (inner pair)')
    a2.legend(fontsize=6.6, loc='upper left')
    fig.suptitle('bias_dist_pd: local-mismatch Monte Carlo of the copy ratio, 100 runs per view, tt 27 °C 3.3 V, '
                 '5 µA in, outputs at 1.0 V\nIHP sg13cmos5l simulation; data: verification/c2_gaps/replica_bias/'
                 'results/bias_dist/bias_dist_mc_*.csv', fontsize=8.6)
    fig.tight_layout()
    save(fig, 'bias_dist_mismatch_hist.png')


# ----------------------------------------------------------------------------------------------------------------
# (iv) pad_ref_rb vcm / vref over corners x temperature x supply
def plot_pad_ref():
    base = GAPS / 'replica_bias' / 'results' / 'cace_schematic'
    d = {}
    for f in ['vcm_dc_params.csv', 'vcm_dc_3v0_params.csv']:
        head, rows = read_csv(base / f)
        ix = {h: i for i, h in enumerate(head)}
        for r in rows:
            d[(r[ix['corner_mos']], int(float(r[ix['temp']])), float(r[ix['vdd']]))] = (
                float(r[ix['Vcm[V]']]), float(r[ix['Vref[V]']]))
    temps = [-40, 27, 125]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 4.2))
    for c in CORNERS:
        for v in [3.0, 3.3, 3.6]:
            a1.plot(temps, [d[(c, t, v)][0] for t in temps], VLS[v], color=COLOR[c], marker='o', ms=3,
                    label=c if v == 3.3 else None)
            a2.plot(temps, [d[(c, t, v)][1] for t in temps], VLS[v], color=COLOR[c], marker='o', ms=3)
    a1.set_title('vcm (S2D vcm = D2S vref)')
    a2.set_title('vref (S2D pad reference)')
    for a in (a1, a2):
        a.set_xlabel('temperature [°C]')
        a.set_ylabel('V')
    h, l = a1.get_legend_handles_labels()
    leg = a2.legend(h, l, title='MOS corner (color)', fontsize=7, title_fontsize=7.5, loc='lower right')
    a2.add_artist(leg)
    hs = [a2.plot([], [], VLS[v], color='k')[0] for v in [3.0, 3.3, 3.6]]
    a2.legend(hs, ['iovdd %.1f V' % v for v in [3.0, 3.3, 3.6]], title='line style', fontsize=7, title_fontsize=7.5,
              loc='upper left')
    fig.suptitle('pad_ref_rb: replica-bias outputs over 5 MOS corners × 3 temperatures × 3 supplies (45 points)\n'
                 'IHP sg13cmos5l simulation (schematic; the magic PEX gives the same values within 0.1 mV)\n'
                 'data: verification/c2_gaps/replica_bias/results/cace_schematic/vcm_dc*_params.csv', fontsize=8.4)
    fig.tight_layout()
    save(fig, 'pad_ref_rb_vcm_vref_pvt.png')
    vc = [x[0] for x in d.values()]
    vr = [x[1] for x in d.values()]
    print('  pad_ref_rb: %d points, vcm %.4f .. %.4f V, vref %.4f .. %.4f V' % (len(d), min(vc), max(vc), min(vr), max(vr)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--design-cache', default=os.path.join(os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache')),
                                                          'slot7_make_plots'))
    a = ap.parse_args()
    style()
    plot_bg()
    plot_bias_dist()
    plot_pad_ref()
    plot_pex_both(Design(a.design_cache))


if __name__ == '__main__':
    main()
