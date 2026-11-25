#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""S2D pad (sg13cmos5l_IOPadSingle2Diff) alone: Bode, CM response, step, noise, enable plots and scalars
(IHP sg13cmos5l simulation, schematic | magic PEX).

Usage: s2d.py <work_out_dir> <ac_tran_dir> <design_dir>
Reads <work_out_dir>/<view>/s2d_*.csv.gz (collect.py), writes <ac_tran_dir>/plots/s2d_*.png|svg and
<ac_tran_dir>/csv/s2d_*_summary.csv; returns / prints the cross-check rows (crosscheck.py imports scalars()).
Scalar definitions = the CACE templates (tb_ac, tb_tran, tb_noise, tb_enable), evaluated here from the curves.
"""
import csv
import os
import sys

import numpy as np

from common import (COLOR, CORNERS, LS, VLS, committed, find, first_fall, last_cross, first_cross, integrate_psd,
                    load, logx_interp, plt, save, scalars as read_scalars, style, title)

CELL = 'sg13cmos5l_IOPadSingle2Diff'
VIEWS = ['schematic', 'pex']
COND_AC = 'S2D alone, CACE tb_ac: iovdd 3.3 V, vref 1.2 V, vcm 1.2 V, rsrc 50 Ω, 0.5 pF per output, harness ibias 5 µA'


def ac_scalars(d, dv=None):
    f = d['frequency']
    a = d['at_vd_db']
    acl = logx_interp(f, a, 1e3)
    i0 = np.searchsorted(f, 1e3)
    f3 = first_fall(f, a, acl - 20 * np.log10(np.sqrt(2)), i0)
    r = {'Acl_dB': acl, 'f3dB': f3, 'ph_f3dB': logx_interp(f, d['at_vd_ph'], f3)}
    if dv is not None:
        r['CMvdd_1k'] = logx_interp(dv['frequency'], dv['at_vc_db'], 1e3)
    return r


def tran_scalars(d):
    t, vd = d['time'], d['v(outp)'] - d['v(outn)']
    vc = (d['v(outp)'] + d['v(outn)']) / 2 - d['v(vcm)']
    vlo, vhi = np.interp([0.99e-6, 4.9e-6], t, vd)
    t10 = first_cross(t, vd, vlo + 0.1 * (vhi - vlo))
    t90 = first_cross(t, vd, vlo + 0.9 * (vhi - vlo))
    band = 0.01 * abs(vhi - vlo)
    ts = last_cross(t, np.abs(vd - vhi), band) - 1.0005e-6
    m = (t >= 1e-6) & (t <= 4.9e-6)
    return {'t_rise': t90 - t10, 't_settle': ts, 'Overshoot': 100 * (vd[m].max() - vhi) / (vhi - vlo),
            'Vcm_dev': 1e3 * np.abs(vc[m]).max(), 'vlo': vlo, 'vhi': vhi}


def noise_scalars(d):
    f = d['frequency']
    return {'En_1k': logx_interp(f, d['inoise_spectrum'], 1e3), 'En_100k': logx_interp(f, d['inoise_spectrum'], 1e5),
            'Vn_out': integrate_psd(f, d['onoise_spectrum'], 10, 10e6),
            'Vn_in_1M': integrate_psd(f, d['inoise_spectrum'], 10, 1e6)}


def enable_scalars(d, tstop=10e-6):
    t, vd = d['time'], d['v(outp)'] - d['v(outn)']
    vc = (d['v(outp)'] + d['v(outn)']) / 2 - d['v(vcm)']
    vend = np.interp(tstop, t, vd)
    t1 = last_cross(t, np.abs(vd - vend), 1e-3, 1e-6, tstop)
    m = (t >= 1e-6) & (t <= tstop)
    return {'t_on': t1 - 1e-6, 'Vc_max': vc[m].max(), 'Vc_min': vc[m].min(), 'Vd_end': vend,
            'Iio_on': -np.interp(tstop, t, d['i(vio)'])}


def legend_pvt(ax, loc='lower left', temps=(-40, 27, 125), corners=CORNERS):
    hs = [plt.Line2D([], [], color=COLOR[c], lw=1.6) for c in corners]
    hs += [plt.Line2D([], [], color='#52514e', ls=LS[t], lw=1.2) for t in temps]
    ax.legend(hs, list(corners) + [f'{t} °C' for t in temps], loc=loc, ncol=2, fontsize=7)


def plot_bode(R, out):
    fig, axs = plt.subplots(3, 2, figsize=(10, 8.2), gridspec_kw={'height_ratios': [3, 2.2, 2.2]})
    for j, v in enumerate(VIEWS):
        for d in R[v]['ac'].values():
            c = d['cond']
            kw = dict(color=COLOR[c['corner_mos']], ls=LS[c['temp']], lw=1.1)
            axs[0, j].semilogx(d['frequency'], d['at_vd_db'], **kw)
            axs[1, j].semilogx(d['frequency'], d['at_vd_db'], **kw)
            axs[2, j].semilogx(d['frequency'], d['at_vd_ph'], **kw)
        tt = find(R[v]['ac'], corner_mos='tt', temp=27)[0]
        s = ac_scalars(tt)
        for k in (0, 1):
            axs[k, j].axhline(s['Acl_dB'] - 3.0103, color='#52514e', lw=0.7, ls='-.')
            axs[k, j].plot([s['f3dB']], [s['Acl_dB'] - 3.0103], 'o', color='#0b0b0b', ms=4)
        axs[1, j].annotate(f"tt 27 °C: −3 dB at {s['f3dB'] / 1e6:.3f} MHz, phase {s['ph_f3dB']:.0f}°",
                           (s['f3dB'], s['Acl_dB'] - 3.0103), xytext=(-150, -28), textcoords='offset points',
                           fontsize=7.5, arrowprops=dict(arrowstyle='-', color='#52514e', lw=0.6))
        f3 = [ac_scalars(d)['f3dB'] for d in R[v]['ac'].values()]
        axs[0, j].set_title(f"{'schematic' if v == 'schematic' else 'magic PEX'}: f−3dB {min(f3) / 1e6:.2f} … "
                            f"{max(f3) / 1e6:.2f} MHz over 15 PVT")
        axs[0, j].set_ylim(-50, 12)
        axs[0, j].set_xlim(10, 1e9)
        axs[1, j].set_xlim(1e5, 1e7)
        axs[1, j].set_ylim(-4, 7.5)
        axs[1, j].set_title('zoom around the −3 dB point', fontsize=8)
        axs[2, j].set_ylim(-360, 10)
        axs[2, j].set_yticks(range(-360, 1, 90))
        axs[2, j].set_xlabel('frequency [Hz]')
        axs[2, j].set_xlim(10, 1e9)
    axs[0, 0].set_ylabel('|(outp − outn)/(pad − vref)| [dB]')
    axs[1, 0].set_ylabel('[dB]')
    axs[2, 0].set_ylabel('phase [°]')
    legend_pvt(axs[2, 0])
    title(fig, None, 'S2D closed-loop gain (outp − outn)/(pad source − vref), ideal 2 (6.02 dB); 5 MOS corners × '
          '−40 / 27 / 125 °C\n' + COND_AC, 'both')
    save(fig, os.path.join(out, 's2d_bode'))


def plot_cm(R, out):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    for v in VIEWS:
        for d in R[v]['ac_vdd'].values():
            c = d['cond']
            kw = dict(color=COLOR[c['corner_mos']], ls=VLS[v], lw=1.0)
            if c['temp'] == 27 or v == 'schematic':
                axs[0].semilogx(d['frequency'], d['at_vc_db'], **dict(kw, ls=LS[c['temp']] if v == 'schematic' else '-.'))
        for d in R[v]['ac'].values():
            c = d['cond']
            if c['temp'] == 27 or v == 'schematic':
                axs[1].semilogx(d['frequency'], d['at_vc_db'], color=COLOR[c['corner_mos']],
                                ls=LS[c['temp']] if v == 'schematic' else '-.', lw=1.0)
    axs[0].set_title('(outp + outn)/2 per volt on iovdd (CMvdd)')
    axs[1].set_title('(outp + outn)/2 per volt of signal (pad − vref)')
    for a in axs:
        a.set_xlabel('frequency [Hz]')
        a.set_xlim(10, 1e9)
    axs[0].set_ylabel('output common-mode response [dB]')
    axs[0].set_ylim(-80, 0)
    legend_pvt(axs[0], loc='upper left')
    axs[1].legend([plt.Line2D([], [], color='#52514e'), plt.Line2D([], [], color='#52514e', ls='-.')],
                  ['schematic (line style = temperature)', 'magic PEX, 27 °C (dash-dot)'], loc='upper left', fontsize=7)
    title(fig, None, 'S2D output common-mode response vs frequency (no mismatch: systematic only); ' + COND_AC, 'both')
    save(fig, os.path.join(out, 's2d_cm_response'))


def plot_step(R, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.2), sharex=True)
    for j, cl in enumerate([1e-15, 5e-13]):
        for v in VIEWS:
            d = find(R[v]['tran'], corner_mos='tt', temp=27, cload=cl)[0]
            t = (d['time'] - 1e-6) * 1e9
            s = tran_scalars(d)
            vd = d['v(outp)'] - d['v(outn)']
            ls = VLS[v]
            axs[0, j].plot(t, d['v(outp)'], color='#2a78d6', ls=ls, label=f'outp ({v})')
            axs[0, j].plot(t, d['v(outn)'], color='#eb6834', ls=ls, label=f'outn ({v})')
            axs[1, j].plot(t, vd, color='#0b0b0b' if v == 'schematic' else '#1baf7a', ls=ls,
                           label=f"outp − outn ({'schematic' if v == 'schematic' else 'magic PEX'}): "
                                 f"t10-90 {s['t_rise'] * 1e9:.0f} ns, t1% {s['t_settle'] * 1e9:.0f} ns")
            axs[1, j].axvline(s['t_settle'] * 1e9 + 0.5, color='#0b0b0b' if v == 'schematic' else '#1baf7a',
                              ls=':', lw=1)
            if v == 'schematic':
                for b in (1, -1):
                    axs[1, j].axhline(s['vhi'] + b * 0.01 * (s['vhi'] - s['vlo']), color='#8a8984', lw=0.6, ls='-.')
        axs[0, j].set_title(f'load {cl * 1e12:g} pF per output (+ built-in), tt 27 °C')
        axs[1, j].set_xlabel('time after the input step [ns]')
        axs[1, j].legend(loc='lower right', fontsize=7)
        axs[1, j].set_xlim(-100, 900)
    axs[0, 0].legend(loc='center right', fontsize=7, ncol=1)
    axs[0, 0].set_ylabel('output [V]')
    axs[1, 0].set_ylabel('outp − outn [V]')
    title(fig, None, 'S2D step response: pad − vref −0.25 → +0.25 V (1 ns edge, at 1 µs), CACE tb_tran; settling to '
          '1 % (dash-dot band) marked by the dotted lines\n' + COND_AC.replace(', 0.5 pF per output', ''), 'both')
    save(fig, os.path.join(out, 's2d_step'))


def plot_settle(R, out):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
    for j, cl in enumerate([1e-15, 5e-13]):
        for v in VIEWS:
            for d in find(R[v]['tran'], cload=cl):  # PEX: dash-dot for all temperatures
                c = d['cond']
                s = tran_scalars(d)
                vd = d['v(outp)'] - d['v(outn)']
                e = 100 * (vd - s['vhi']) / (s['vhi'] - s['vlo'])
                axs[j].plot((d['time'] - 1e-6) * 1e9, e, color=COLOR[c['corner_mos']],
                            ls=LS[c['temp']] if v == 'schematic' else '-.', lw=1.0 if v == 'schematic' else 0.8)
        axs[j].axhspan(-1, 1, color='#e6e6e3', zorder=0)
        axs[j].set_ylim(-5, 2)
        axs[j].set_xlim(0, 500 if j == 0 else 800)
        axs[j].set_title(f'load {cl * 1e12:g} pF per output')
        axs[j].set_xlabel('time after the input step [ns]')
    axs[0].set_ylabel('(outp − outn) − final [% of step]')
    legend_pvt(axs[0], loc='lower right', corners=['tt', 'ss', 'ff'])
    axs[1].legend([plt.Line2D([], [], color='#52514e'), plt.Line2D([], [], color='#52514e', ls='-.')],
                  ['schematic', 'magic PEX'], loc='lower right', fontsize=7)
    title(fig, None, 'S2D settling after the 0.5 V step (CACE tb_tran), ss / tt / ff × −40 / 27 / 125 °C; '
          'grey = ±1 % (the t_settle band); magic PEX dash-dot (all temperatures)', 'both')
    save(fig, os.path.join(out, 's2d_settling'))


def plot_noise(R, out):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    txt = []
    for v in VIEWS:
        for d in R[v]['noise'].values():
            c = d['cond']
            bold = c['corner_mos'] == 'tt' and c['temp'] == 27
            ax.loglog(d['frequency'], d['inoise_spectrum'] * 1e9, color=COLOR[c['corner_mos']],
                      ls=LS[c['temp']] if v == 'schematic' else '-.', lw=1.8 if bold else 0.8,
                      alpha=1 if bold else 0.8, zorder=3 if bold else 2)
        s = noise_scalars(find(R[v]['noise'], corner_mos='tt', temp=27)[0])
        txt.append(f"{'schematic' if v == 'schematic' else 'magic PEX'} tt 27 °C: {s['En_1k'] * 1e9:.0f} nV/√Hz at 1 kHz, "
                   f"{s['En_100k'] * 1e9:.0f} nV/√Hz at 100 kHz; output noise 10 Hz–10 MHz {s['Vn_out'] * 1e6:.0f} µVrms; "
                   f"input-referred 10 Hz–1 MHz {s['Vn_in_1M'] * 1e6:.0f} µVrms")
    ax.text(0.01, 0.02, '\n'.join(txt), transform=ax.transAxes, fontsize=7.2, va='bottom',
            bbox=dict(fc='white', ec='#d8d8d4'))
    ax.set_xlim(10, 10e6)
    ax.set_ylim(20, 2e4)
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylabel('input-referred noise density [nV/√Hz]')
    legend_pvt(ax, loc='upper right')
    title(fig, None, 'S2D input-referred noise density (referred to pad source − vref, includes rsrc 50 Ω), '
          'CACE tb_noise; bold = tt 27 °C, dash-dot = magic PEX\n' + COND_AC, 'both')
    save(fig, os.path.join(out, 's2d_noise'))


def plot_enable(R, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.0), sharex='col', gridspec_kw={'width_ratios': [3, 2]})
    for v in VIEWS:
        for c, tmp in [('tt', 27), ('ss', -40), ('ff', 125)]:
            d = find(R[v]['endis'], corner_mos=c, temp=tmp)[0]
            t = d['time'] * 1e6
            vd = d['v(outp)'] - d['v(outn)']
            vc = (d['v(outp)'] + d['v(outn)']) / 2
            kw = dict(color=COLOR[c], ls=VLS[v], lw=1.2 if v == 'schematic' else 0.9)
            for j, (t0, t1) in enumerate([(0.5, 4.5), (10.5, 13.5)]):
                m = (t >= t0) & (t <= t1)
                axs[0, j].plot(t[m], vd[m], **kw)
                axs[0, j].plot(t[m], vc[m], **dict(kw, alpha=0.55))
                axs[1, j].plot(t[m], -d['i(vio)'][m] * 1e6, **kw)
                axs[1, j].set_xlim(t0, t1)
                if v == 'schematic' and c == 'tt':
                    pk = (-d['i(vio)'][m]).max() * 1e6
                    axs[1, j].annotate(f'tt 27 °C peak {pk:.0f} µA (clipped)', (t[m][np.argmax(-d['i(vio)'][m])], 250),
                                       xytext=(10, -12), textcoords='offset points', fontsize=7)
                axs[1, j].set_ylim(-10, 260)
    axs[0, 0].set_title('enable: en_1v2 0 → 1.2 V at 1 µs')
    axs[0, 1].set_title('disable: en_1v2 1.2 → 0 V at 11 µs')
    axs[0, 0].set_ylabel('outp − outn (→ 0.5 V) and\n(outp + outn)/2 (→ vcm 1.2 V) [V]')
    axs[1, 0].set_ylabel('iovdd current [µA]')
    for j in range(2):
        axs[1, j].set_xlabel('time [µs]')
    s = enable_scalars(find(R['schematic']['en'], corner_mos='tt', temp=27)[0])
    sp = enable_scalars(find(R['pex']['en'], corner_mos='tt', temp=27)[0])
    axs[0, 0].text(0.98, 0.5, f"tt 27 °C t_on (vd within 1 mV): {s['t_on'] * 1e6:.2f} µs schematic, "
                   f"{sp['t_on'] * 1e6:.2f} µs PEX\nIio enabled {s['Iio_on'] * 1e6:.1f} µA",
                   transform=axs[0, 0].transAxes, ha='right', fontsize=7.2, bbox=dict(fc='white', ec='#d8d8d4'))
    axs[1, 1].legend([plt.Line2D([], [], color=COLOR[c]) for c in ('tt', 'ss', 'ff')] +
                     [plt.Line2D([], [], color='#52514e', ls=VLS[v]) for v in VIEWS],
                     ['tt 27 °C', 'ss −40 °C', 'ff 125 °C', 'schematic', 'magic PEX'], loc='center right', fontsize=7)
    title(fig, None, 'S2D enable / disable transient (CACE tb_enable + a disable edge): u = pad − vref = +0.25 V, '
          'tt 27 °C, ss −40 °C, ff 125 °C; faint = output common mode\n'
          'iovdd current = whole testbench ring supply (pad, bias_gen_pd, en_ctrl_3v3); ' +
          COND_AC.split(': ')[1], 'both')
    save(fig, os.path.join(out, 's2d_enable'))


def loadall(wout):
    R = {}
    for v in VIEWS:
        p = os.path.join(wout, v)
        R[v] = {'ac': load(f'{p}/s2d_ac.at_u.csv.gz'), 'ac_vdd': load(f'{p}/s2d_ac.at_vdd.csv.gz'),
                'tran': load(f'{p}/s2d_tran.at_tran.csv.gz'), 'noise': load(f'{p}/s2d_noise.at_noise.csv.gz'),
                'en': load(f'{p}/s2d_enable.at_en.csv.gz'), 'endis': load(f'{p}/s2d_enable.at_endis.csv.gz')}
        for g in ('ac', 'tran', 'noise', 'enable'):
            R[v]['sc_' + g] = read_scalars(f'{p}/s2d_{g}.scalars.csv')
    return R


def summaries(R, csvdir):
    """one row per run and view: the scalars evaluated here from the curves"""
    rows = {}
    for v in VIEWS:
        for (n, d), dv in zip(R[v]['ac'].items(), R[v]['ac_vdd'].values()):
            rows.setdefault('ac', []).append({'view': v, **{k: d['cond'][k] for k in ('corner_mos', 'temp')},
                                              **ac_scalars(d, dv)})
        for d in R[v]['tran'].values():
            s = tran_scalars(d)
            rows.setdefault('tran', []).append({'view': v, 'cload_F': d['cond']['cload'],
                                                **{k: d['cond'][k] for k in ('corner_mos', 'temp')},
                                                **{k: s[k] for k in ('t_rise', 't_settle', 'Overshoot', 'Vcm_dev')}})
        for d in R[v]['noise'].values():
            rows.setdefault('noise', []).append({'view': v, **{k: d['cond'][k] for k in ('corner_mos', 'temp')},
                                                 **noise_scalars(d)})
        for d in R[v]['en'].values():
            rows.setdefault('enable', []).append({'view': v, **{k: d['cond'][k] for k in ('corner_mos', 'temp')},
                                                  **enable_scalars(d)})
    units = {'ac': 'Acl_dB dB, f3dB Hz, ph_f3dB deg, CMvdd_1k dB', 'tran': 't_rise s, t_settle s, Overshoot %, Vcm_dev mV',
             'noise': 'En V/rtHz, Vn_out V (output, 10 Hz-10 MHz), Vn_in_1M V (input-referred, 10 Hz-1 MHz)',
             'enable': 't_on s, Vc V, Vd_end V, Iio_on A'}
    for g, rr in rows.items():
        with open(os.path.join(csvdir, f's2d_{g}_summary.csv'), 'w', newline='') as f:
            f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                    f'# IHP sg13cmos5l simulation (schematic | magic PEX): S2D {g}, scalars from the curves; units: {units[g]}\n')
            w = csv.DictWriter(f, fieldnames=list(rr[0]))
            w.writeheader()
            for r in rr:
                w.writerow({k: (f'{x:.6g}' if isinstance(x, float) else x) for k, x in r.items()})
    return rows


def crosscheck(R, design):
    """rows: (quantity, conditions, view, committed CACE, this run's ngspice .data, from the curves)"""
    res = os.path.join(design, 'macros', CELL, 'verification', 'cace', 'results')
    out = []
    for v in VIEWS:
        rd = os.path.join(res, CELL + ('' if v == 'schematic' else '_pex'))
        C = {g: committed(os.path.join(rd, f'{g}_params.csv')) for g in ('ac', 'tran', 'noise', 'enable')}
        for c, t in [('tt', 27), ('ss', -40), ('ff', 125)]:
            ca = [r for r in C['ac'] if r['corner_mos'] == c and int(r['temp']) == t][0]
            d = find(R[v]['ac'], corner_mos=c, temp=t)[0]
            dv = find(R[v]['ac_vdd'], corner_mos=c, temp=t)[0]
            sd = [x for x in R[v]['sc_ac'].values() if x['cond']['corner_mos'] == c and x['cond']['temp'] == t][0]
            s = ac_scalars(d, dv)
            out += [('S2D f3dB [MHz]', f'{c} {t} °C', v, float(ca['f3dB']) / 1e6, sd['data'][1] / 1e6, s['f3dB'] / 1e6),
                    ('S2D Acl 1 kHz [dB]', f'{c} {t} °C', v, float(ca['Acl_dB']), sd['data'][0], s['Acl_dB']),
                    ('S2D CMvdd 1 kHz [dB]', f'{c} {t} °C', v, float(ca['CMvdd_1k']), sd['data'][7], s['CMvdd_1k'])]
            cn = [r for r in C['noise'] if r['corner_mos'] == c and int(r['temp']) == t][0]
            d = find(R[v]['noise'], corner_mos=c, temp=t)[0]
            sd = [x for x in R[v]['sc_noise'].values() if x['cond']['corner_mos'] == c and x['cond']['temp'] == t][0]
            s = noise_scalars(d)
            out += [('S2D En 1 kHz [nV/√Hz]', f'{c} {t} °C', v, float(cn['En_1k']) * 1e9, sd['data'][0] * 1e9, s['En_1k'] * 1e9),
                    ('S2D En 100 kHz [nV/√Hz]', f'{c} {t} °C', v, float(cn['En_100k']) * 1e9, sd['data'][1] * 1e9, s['En_100k'] * 1e9),
                    ('S2D Vn_out 10 Hz–10 MHz [µV]', f'{c} {t} °C', v, float(cn['Vn_out']) * 1e6, sd['data'][2] * 1e6, s['Vn_out'] * 1e6)]
            ce = [r for r in C['enable'] if r['corner_mos'] == c and int(r['temp']) == t][0]
            d = find(R[v]['en'], corner_mos=c, temp=t)[0]
            sd = [x for x in R[v]['sc_enable'].values() if x['cond']['corner_mos'] == c and x['cond']['temp'] == t][0]
            s = enable_scalars(d)
            out += [('S2D t_on [µs]', f'{c} {t} °C', v, float(ce['t_on']) * 1e6, sd['data'][0] * 1e6, s['t_on'] * 1e6),
                    ('S2D Iio enabled [µA]', f'{c} {t} °C', v, float(ce['Iio_on']) * 1e6, sd['data'][4] * 1e6, s['Iio_on'] * 1e6)]
            for cl in (1e-15, 5e-13):
                ct = [r for r in C['tran'] if r['corner_mos'] == c and int(r['temp']) == t and float(r['cload']) == cl][0]
                d = find(R[v]['tran'], corner_mos=c, temp=t, cload=cl)[0]
                sd = [x for x in R[v]['sc_tran'].values() if x['cond']['corner_mos'] == c and x['cond']['temp'] == t
                      and abs(x['cond']['cload'] - cl) < 1e-20][0]
                s = tran_scalars(d)
                lab = f'{c} {t} °C {cl * 1e12:g} pF'
                out += [('S2D t_rise 10–90 % [ns]', lab, v, float(ct['t_rise']) * 1e9, sd['data'][0] * 1e9, s['t_rise'] * 1e9),
                        ('S2D t_settle 1 % [ns]', lab, v, float(ct['t_settle']) * 1e9, sd['data'][1] * 1e9, s['t_settle'] * 1e9),
                        ('S2D Vcm_dev [mV] (CACE value in V)', lab, v, 1e3 * float(ct['Vcm_dev']), 1e3 * sd['data'][3], s['Vcm_dev'])]
    return out


def main(wout, here, design):
    style()
    out = os.path.join(here, 'plots')
    R = loadall(wout)
    plot_bode(R, out)
    plot_cm(R, out)
    plot_step(R, out)
    plot_settle(R, out)
    plot_noise(R, out)
    plot_enable(R, out)
    summaries(R, os.path.join(here, 'csv'))
    return R


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
