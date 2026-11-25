#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""D2S pad (sg13cmos5l_IOPadDiff2Single) alone: Bode vs load and PVT, output impedance, PSRR, large-signal step,
noise, enable plots and scalars (IHP sg13cmos5l simulation, schematic | magic PEX), at the CACE condition vicm = vref
= vterm = 1.65 V and at the slot operating point 1.26 V.

Usage: d2s.py <work_out_dir> <ac_tran_dir> <design_dir>
Reads <work_out_dir>/<view>/d2s_*.csv.gz (collect.py), writes <ac_tran_dir>/plots/d2s_*.png|svg and
<ac_tran_dir>/csv/d2s_*_summary.csv. Scalar definitions = the CACE templates (tb_ac, tb_tran, tb_noise, tb_enable),
evaluated here from the curves.
"""
import csv
import os
import sys

import numpy as np

from common import (COLOR, CORNERS, LS, VLS, committed, find, first_fall, last_cross, first_cross, integrate_psd,
                    load, logx_interp, plt, save, scalars as read_scalars, style, title)
from s2d import legend_pvt

CELL = 'sg13cmos5l_IOPadDiff2Single'
VIEWS = ['schematic', 'pex']
VN = {'schematic': 'schematic', 'pex': 'magic PEX'}
COND = ('iovdd 3.3 V, harness ibias 5 µA (sel 0); schematic without, magic PEX with ngspice rshunt=1e12')
CLC = {1e-11: '#2a78d6', 1e-10: '#1baf7a', 3e-10: '#eda100', 1e-09: '#eb6834'}


def ac_scalars(d, psr=None, cm=None, zo=None):
    f, a = d['frequency'], d['at_m']
    acl = logx_interp(f, a, 1e3)
    adn = a - acl
    r = {'Acl_dB': acl, 'f3dB': first_fall(f, adn, -3.0), 'Peak_dB': float(adn.max()),
         'f_peak': float(f[np.argmax(adn)])}
    if psr is not None:
        r['PSRR_1k'] = -logx_interp(psr['frequency'], psr['at_m'], 1e3)
        r['PSRR_100k'] = -logx_interp(psr['frequency'], psr['at_m'], 1e5)
    if cm is not None:
        r['CMRR_1k'] = acl - logx_interp(cm['frequency'], cm['at_m'], 1e3)
    if zo is not None:
        r['Zout_1k'] = logx_interp(zo['frequency'], zo['at_m'], 1e3)
        r['Zout_1M'] = logx_interp(zo['frequency'], zo['at_m'], 1e6)
    return r


def tran_scalars(d):
    t, p = d['time'], d['v(pad)']
    v0, v1 = np.interp([0.99e-6, 4.9e-6], t, p)
    dv = v1 - v0
    vn = (p - v0) / dv
    t10r = first_cross(t, vn, 0.1, True, 1e-6, 5e-6)
    t90r = first_cross(t, vn, 0.9, True, 1e-6, 5e-6)
    t90f = first_cross(t, vn, 0.9, False, 5e-6, 9e-6)
    t10f = first_cross(t, vn, 0.1, False, 5e-6, 9e-6)
    m = (t >= 1e-6) & (t <= 5e-6)
    return {'SR_rise': 0.8 * dv / (t90r - t10r), 'SR_fall': 0.8 * dv / (t10f - t90f),
            'Overshoot': float(vn[m].max() - 1),
            'ts_rise': last_cross(t, np.abs(vn - 1), 0.01, 1e-6, 5e-6) - 1e-6,
            'ts_fall': last_cross(t, np.abs(vn), 0.01, 5e-6, 9e-6) - 5.001e-6, 'v0': v0, 'v1': v1}


def noise_scalars(d):
    f = d['frequency']
    return {'En_1k': logx_interp(f, d['onoise_spectrum'], 1e3), 'En_100k': logx_interp(f, d['onoise_spectrum'], 1e5),
            'Vn_int': integrate_psd(f, d['onoise_spectrum'], 10, 10e6)}


def enable_scalars(d, tstop=60e-6):
    t, e = d['time'], d['v(pad)'] - d['v(vref)']
    eend = np.interp(tstop, t, e)
    m = (t >= 1e-6) & (t <= tstop)
    return {'t_on': last_cross(t, np.abs(e - eend), 1e-3, 1e-6, tstop) - 1e-6, 'Glitch_max': e[m].max() * 1e3,
            'Glitch_min': e[m].min() * 1e3, 'Iio_end': -np.interp(tstop, t, d['i(vio)'])}


def loadall(wout):
    R = {}
    for v in VIEWS:
        p = os.path.join(wout, v)
        R[v] = {}
        for g in ('d2s_ac', 'd2s_ac_load', 'd2s_ac_slot', 'd2s_ac_load_slot'):
            for s in ('sig', 'psr', 'cm', 'zo'):
                R[v][f'{g}.{s}'] = load(f'{p}/{g}.at_{s}.csv.gz')
        for g in ('d2s_tran', 'd2s_tran_slot'):
            R[v][g] = load(f'{p}/{g}.at_tran.csv.gz')
        R[v]['noise'] = load(f'{p}/d2s_noise.at_noise.csv.gz')
        R[v]['en'] = load(f'{p}/d2s_enable.at_en.csv.gz')
        R[v]['endis'] = load(f'{p}/d2s_enable.at_endis.csv.gz')
        for g in ('ac', 'ac_load', 'tran', 'noise', 'enable'):
            R[v]['sc_' + g] = read_scalars(f'{p}/d2s_{g}.scalars.csv')
    return R


def plot_bode_loads(R, out, grp='d2s_ac_load', vic=1.65, name='d2s_bode_loads'):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.6), sharex=True)
    for j, v in enumerate(VIEWS):
        txt = []
        for d in R[v][f'{grp}.sig'].values():
            c = d['cond']
            kw = dict(color=CLC[c['cload']], ls='-' if c['rload'] < 1e6 else '--', lw=1.2)
            axs[0, j].semilogx(d['frequency'], d['at_m'], **kw)
            axs[1, j].semilogx(d['frequency'], d['at_p'], **kw)
            s = ac_scalars(d)
            if s['Peak_dB'] > 0.05:
                txt.append(f"{c['cload'] * 1e12:g} pF {'1 kΩ' if c['rload'] < 1e6 else 'no R'}: "
                           f"peak +{s['Peak_dB']:.2f} dB at {s['f_peak'] / 1e6:.2f} MHz")
        axs[0, j].text(0.02, 0.03, '\n'.join(txt) if txt else 'no peaking > 0.05 dB', transform=axs[0, j].transAxes,
                       fontsize=7, bbox=dict(fc='white', ec='#d8d8d4'))
        axs[0, j].axhline(-6.02 - 3, color='#52514e', lw=0.7, ls='-.')
        axs[0, j].set_ylim(-40, 5)
        axs[0, j].set_title(VN[v])
        axs[1, j].set_ylim(-300, 10)
        axs[1, j].set_yticks(range(-270, 1, 90))
        axs[1, j].set_xlim(1e3, 1e8)
        axs[1, j].set_xlabel('frequency [Hz]')
    axs[0, 0].set_ylabel('|pad / (vinp − vinn)| [dB] (ideal −6.02)')
    axs[1, 0].set_ylabel('phase [°]')
    hs = [plt.Line2D([], [], color=CLC[k]) for k in CLC] + [plt.Line2D([], [], color='#52514e'),
                                                            plt.Line2D([], [], color='#52514e', ls='--')]
    axs[1, 0].legend(hs, ['10 pF', '100 pF', '300 pF', '1 nF', '1 kΩ to vterm', 'unloaded (1 GΩ)'], loc='lower left',
                     ncol=2, fontsize=7)
    title(fig, None, f'D2S closed-loop gain pad / (vinp − vinn) vs load (CACE ac_load / ac_1nF), tt 27 °C, '
          f'vicm = vref = vterm = {vic} V; dash-dot = −3 dB\n' + COND, 'both')
    save(fig, os.path.join(out, name))


def plot_family(R, out, key, ycol, name, ylabel, ttl, ylim=None, neg=False, logy=False, xlim=(1, 1e9)):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True)
    for j, v in enumerate(VIEWS):
        for d in R[v][key].values():
            c = d['cond']
            y = -d[ycol] if neg else d[ycol]
            (axs[j].loglog if logy else axs[j].semilogx)(d['frequency'], y, color=COLOR[c['corner_mos']],
                                                         ls=LS[c['temp']], lw=1.0)
        axs[j].set_title(VN[v])
        axs[j].set_xlabel('frequency [Hz]')
        axs[j].set_xlim(*xlim)
        if ylim:
            axs[j].set_ylim(*ylim)
    axs[0].set_ylabel(ylabel)
    legend_pvt(axs[0], loc='best')
    title(fig, None, ttl, 'both')
    save(fig, os.path.join(out, name))


def plot_bode_corners(R, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.2), sharex=True)
    for j, v in enumerate(VIEWS):
        f3 = []
        for d in R[v]['d2s_ac.sig'].values():
            c = d['cond']
            kw = dict(color=COLOR[c['corner_mos']], ls=LS[c['temp']], lw=1.0)
            axs[0, j].semilogx(d['frequency'], d['at_m'], **kw)
            axs[1, j].semilogx(d['frequency'], d['at_p'], **kw)
            f3.append(ac_scalars(d)['f3dB'])
        axs[0, j].axhline(-9.02, color='#52514e', lw=0.7, ls='-.')
        axs[0, j].set_title(f'{VN[v]}: f−3dB {min(f3) / 1e6:.2f} … {max(f3) / 1e6:.2f} MHz over 15 PVT')
        axs[0, j].set_ylim(-40, 0)
        axs[1, j].set_ylim(-300, 10)
        axs[1, j].set_yticks(range(-270, 1, 90))
        axs[1, j].set_xlim(1e3, 1e8)
        axs[1, j].set_xlabel('frequency [Hz]')
    axs[0, 0].set_ylabel('|pad / (vinp − vinn)| [dB]')
    axs[1, 0].set_ylabel('phase [°]')
    legend_pvt(axs[1, 0])
    title(fig, None, 'D2S closed-loop gain (CACE ac_params): 5 MOS corners × −40 / 27 / 125 °C, 1 kΩ to vterm + '
          '100 pF, vicm = vref = vterm = 1.65 V\n' + COND, 'both')
    save(fig, os.path.join(out, 'd2s_bode_corners'))


def plot_step(R, out):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    txt = []
    for v in VIEWS:
        for cl in (1e-11, 1e-10, 3e-10):
            d = find(R[v]['d2s_tran'], corner_mos='tt', cload=cl)[0]
            s = tran_scalars(d)
            t = d['time'] * 1e6
            for j, (t0, t1) in enumerate([(0.8, 2.6), (4.8, 6.6)]):
                m = (t >= t0) & (t <= t1)
                axs[j].plot(t[m], d['v(pad)'][m], color=CLC[cl], ls=VLS[v], lw=1.2)
            txt.append(f"{VN[v]} {cl * 1e12:g} pF: SR {s['SR_rise'] / 1e6:.2f} / {s['SR_fall'] / 1e6:.2f} V/µs, "
                       f"t1% {s['ts_rise'] * 1e9:.0f} / {s['ts_fall'] * 1e9:.0f} ns")
    axs[0].set_title('rising: vinp − vinn −0.5 → +0.5 V at 1 µs (1 ns edge)')
    axs[1].set_title('falling at 5 µs')
    for a in axs:
        a.set_xlabel('time [µs]')
    axs[0].set_ylabel('pad [V]')
    axs[1].text(0.98, 0.5, '\n'.join(txt) + '\n(rise / fall; SR 10–90 %, t1% = settling to 1 %)',
                transform=axs[1].transAxes, ha='right', va='center', fontsize=6.8, bbox=dict(fc='white', ec='#d8d8d4'))
    hs = [plt.Line2D([], [], color=CLC[k]) for k in (1e-11, 1e-10, 3e-10)] + \
         [plt.Line2D([], [], color='#52514e'), plt.Line2D([], [], color='#52514e', ls='-.')]
    axs[0].legend(hs, ['10 pF', '100 pF', '300 pF', 'schematic', 'magic PEX'], loc='lower right', fontsize=7)
    title(fig, None, 'D2S large-signal step (CACE tb_tran): pad 1.40 → 1.90 V, 1 kΩ to vterm + CL, tt 27 °C, '
          'vicm = vref = vterm = 1.65 V\n' + COND, 'both')
    save(fig, os.path.join(out, 'd2s_step'))


def plot_slot(R, out):
    """vicm 1.65 V (CACE) vs 1.26 V (slot): Bode at the 1 kOhm loads and the 100 pF step, tt 27 C, schematic"""
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.9))
    v = 'schematic'
    for grp, ls in (('d2s_ac_load', '-'), ('d2s_ac_load_slot', '--')):
        for d in R[v][f'{grp}.sig'].values():
            c = d['cond']
            if c['rload'] > 1e6:
                continue
            axs[0].semilogx(d['frequency'], d['at_m'], color=CLC[c['cload']], ls=ls, lw=1.2)
    for grp, ls in (('d2s_ac', '-'), ('d2s_ac_slot', '--')):
        for d in R[v][f'{grp}.zo'].values():
            if d['cond']['temp'] == 27:
                axs[1].loglog(d['frequency'], d['at_m'], color=COLOR[d['cond']['corner_mos']], ls=ls, lw=1.0)
    txt = []
    for grp, ls in (('d2s_tran', '-'), ('d2s_tran_slot', '--')):
        for cl in (1e-11, 1e-10, 3e-10):
            d = find(R[v][grp], corner_mos='tt', cload=cl)[0]
            t = d['time'] * 1e6
            m = (t >= 0.8) & (t <= 2.6)
            s = tran_scalars(d)
            axs[2].plot(t[m], d['v(pad)'][m] - s['v0'], color=CLC[cl], ls=ls, lw=1.2)
            txt.append(f"{d['cond']['vicm']:.2f} V {cl * 1e12:g} pF: SR {s['SR_rise'] / 1e6:.2f} V/µs, "
                       f"t1% {s['ts_rise'] * 1e9:.0f} ns")
    axs[0].set_xlim(1e4, 1e8)
    axs[0].set_ylim(-30, 3)
    axs[0].set_title('gain, 1 kΩ + 10 / 100 / 300 pF / 1 nF')
    axs[0].set_ylabel('|pad / (vinp − vinn)| [dB]')
    axs[1].set_xlim(10, 1e8)
    axs[1].set_title('|Zout| incl. 1 kΩ ∥ 100 pF, 27 °C, corners')
    axs[1].set_ylabel('|Zout| [Ω]')
    axs[2].set_title('step, rising edge, tt')
    axs[2].set_ylabel('pad − pad(0.99 µs) [V]')
    axs[2].set_xlabel('time [µs]')
    axs[2].text(0.98, 0.04, '\n'.join(txt), transform=axs[2].transAxes, ha='right', fontsize=6.3,
                bbox=dict(fc='white', ec='#d8d8d4'))
    for a in axs[:2]:
        a.set_xlabel('frequency [Hz]')
    hs = [plt.Line2D([], [], color='#52514e'), plt.Line2D([], [], color='#52514e', ls='--')] + \
         [plt.Line2D([], [], color=CLC[k]) for k in CLC]
    axs[0].legend(hs, ['vicm 1.65 V (CACE)', 'vicm 1.26 V (slot)', '10 pF', '100 pF', '300 pF', '1 nF'],
                  loc='lower left', fontsize=6.5)
    legend_pvt(axs[1], loc='upper left', temps=())
    title(fig, None, 'D2S at the slot operating point vicm = vref = vterm = 1.26 V (dashed) vs the CACE condition '
          '1.65 V (solid), tt 27 °C unless noted, schematic', 'schematic')
    save(fig, os.path.join(out, 'd2s_slot_vs_cace'))


def plot_noise(R, out):
    fig, ax = plt.subplots(figsize=(8, 4.6))
    txt = []
    for v in VIEWS:
        for d in R[v]['noise'].values():
            c = d['cond']
            bold = c['corner_mos'] == 'tt' and c['temp'] == 27
            ax.loglog(d['frequency'], d['onoise_spectrum'] * 1e9, color=COLOR[c['corner_mos']],
                      ls=LS[c['temp']] if v == 'schematic' else '-.', lw=1.8 if bold else 0.8, zorder=3 if bold else 2)
        s = noise_scalars(find(R[v]['noise'], corner_mos='tt', temp=27)[0])
        txt.append(f"{VN[v]} tt 27 °C: {s['En_1k'] * 1e9:.0f} nV/√Hz at 1 kHz, {s['En_100k'] * 1e9:.0f} nV/√Hz at "
                   f"100 kHz; integrated 10 Hz–10 MHz {s['Vn_int'] * 1e6:.0f} µVrms")
    ax.text(0.01, 0.02, '\n'.join(txt), transform=ax.transAxes, fontsize=7.2, bbox=dict(fc='white', ec='#d8d8d4'))
    ax.set_xlim(10, 10e6)
    ax.set_ylim(5, 2e4)
    ax.set_xlabel('frequency [Hz]')
    ax.set_ylabel('output noise density at the pad [nV/√Hz]')
    legend_pvt(ax, loc='upper right')
    title(fig, None, 'D2S output noise density (CACE tb_noise; includes the 1 kΩ load), 1 kΩ to vterm + 100 pF, '
          'vicm = vref = 1.65 V; bold = tt 27 °C, dash-dot = magic PEX\n' + COND, 'both')
    save(fig, os.path.join(out, 'd2s_noise'))


def plot_enable(R, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 5.8), sharex='col', gridspec_kw={'width_ratios': [3, 2]})
    txt = []
    for v in VIEWS:
        d = find(R[v]['endis'], sel=0)[0]
        t = d['time'] * 1e6
        e = (d['v(pad)'] - d['v(vref)']) * 1e3
        for j, (t0, t1) in enumerate([(0.5, 4.5), (30.5, 34.5)]):
            m = (t >= t0) & (t <= t1)
            axs[0, j].plot(t[m], e[m], color='#2a78d6' if v == 'schematic' else '#eb6834', ls=VLS[v])
            axs[1, j].plot(t[m], -d['i(vio)'][m] * 1e6, color='#2a78d6' if v == 'schematic' else '#eb6834', ls=VLS[v])
            axs[1, j].plot(t[m], -d['i(vcore)'][m] * 1e6, color='#2a78d6' if v == 'schematic' else '#eb6834',
                           ls=VLS[v], alpha=0.45)
            axs[1, j].set_xlim(t0, t1)
        s = enable_scalars(find(R[v]['en'], sel=0)[0])
        txt.append(f"{VN[v]}: t_on {s['t_on'] * 1e6:.2f} µs, glitch {s['Glitch_min']:.2f} … {s['Glitch_max']:.2f} mV, "
                   f"Iio {s['Iio_end'] * 1e6:.0f} µA")
    for j in range(2):
        axs[0, j].set_yscale('symlog', linthresh=1)
        axs[0, j].set_ylim(-300, 300)
        axs[0, j].axhspan(-1, 1, color='#e6e6e3', zorder=0)
    axs[0, 0].text(0.98, 0.04, '\n'.join(txt) + '\n(t_on: pad − vref within 1 mV of its end value)', transform=axs[0, 0].transAxes, ha='right', fontsize=7,
                   bbox=dict(fc='white', ec='#d8d8d4'))
    axs[0, 0].set_title('enable: en_1v2 0 → 1.2 V at 1 µs')
    axs[0, 1].set_title('disable: en_1v2 1.2 → 0 V at 31 µs')
    axs[0, 0].set_ylabel('pad − vref [mV]\n(symlog: linear inside ±1 mV, grey)')
    axs[1, 0].set_ylabel('supply current [µA]\n(iovdd; faint = vdd core 1.2 V)')
    for j in range(2):
        axs[1, j].set_xlabel('time [µs]')
    axs[1, 1].legend([plt.Line2D([], [], color='#2a78d6'), plt.Line2D([], [], color='#eb6834', ls='-.')],
                     ['schematic', 'magic PEX'], fontsize=7)
    title(fig, None, 'D2S enable / disable transient (CACE tb_enable + a disable edge): vinp = vinn = 1.65 V, '
          '1 kΩ to vterm 1.65 V + 100 pF, tt 27 °C, sel 0\npad held at vterm by the 1 kΩ when off; ' + COND, 'both')
    save(fig, os.path.join(out, 'd2s_enable'))


def ac_rows(R, v, grp):
    rows = []
    for n, d in R[v][f'{grp}.sig'].items():
        s = ac_scalars(d, R[v][f'{grp}.psr'][n], R[v][f'{grp}.cm'][n], R[v][f'{grp}.zo'][n])
        rows.append({'view': v, 'group': grp, **{k: d['cond'][k] for k in ('corner_mos', 'temp', 'vicm', 'rload', 'cload')}, **s})
    return rows


def summaries(R, csvdir):
    rows = {'ac': [], 'tran': [], 'noise': [], 'enable': []}
    for v in VIEWS:
        for g in ('d2s_ac', 'd2s_ac_load', 'd2s_ac_slot', 'd2s_ac_load_slot'):
            rows['ac'] += ac_rows(R, v, g)
        for g in ('d2s_tran', 'd2s_tran_slot'):
            for d in R[v][g].values():
                s = tran_scalars(d)
                rows['tran'].append({'view': v, 'group': g, **{k: d['cond'][k] for k in ('corner_mos', 'temp', 'vicm', 'cload')},
                                     **{k: s[k] for k in ('SR_rise', 'SR_fall', 'Overshoot', 'ts_rise', 'ts_fall')}})
        for d in R[v]['noise'].values():
            rows['noise'].append({'view': v, **{k: d['cond'][k] for k in ('corner_mos', 'temp')}, **noise_scalars(d)})
        for d in R[v]['en'].values():
            rows['enable'].append({'view': v, 'sel': d['cond']['sel'], **enable_scalars(d)})
    units = {'ac': 'Acl/Peak/PSRR/CMRR dB, f Hz, Zout Ohm, cload F, rload Ohm', 'tran': 'SR V/s, Overshoot fraction, ts s',
             'noise': 'En V/rtHz (output), Vn_int V (output, 10 Hz-10 MHz)', 'enable': 't_on s, Glitch mV, Iio_end A'}
    for g, rr in rows.items():
        with open(os.path.join(csvdir, f'd2s_{g}_summary.csv'), 'w', newline='') as f:
            f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                    f'# IHP sg13cmos5l simulation (schematic | magic PEX): D2S {g}, scalars from the curves; units: {units[g]}\n')
            w = csv.DictWriter(f, fieldnames=list(rr[0]))
            w.writeheader()
            for r in rr:
                w.writerow({k: (f'{x:.6g}' if isinstance(x, float) else x) for k, x in r.items()})
    return rows


def _sd(sc, **kw):
    for x in sc.values():
        if all((x['cond'][k] == v) if isinstance(v, str) else abs(x['cond'][k] - v) <= 1e-9 * abs(v) for k, v in kw.items()):
            return x['data']
    raise KeyError(kw)


def crosscheck(R, design, slotrepo):
    out = []
    for v in VIEWS:
        if v == 'schematic':
            rd = os.path.join(design, 'macros', CELL, 'verification', 'cace', 'results', CELL)
            C = {g: committed(os.path.join(rd, f'{g}_params.csv')) for g in ('ac', 'ac_load', 'ac_1nF', 'tran', 'noise', 'enable')}
        else:
            rd = os.path.join(slotrepo, 'verification', 'c2_gaps', 'd2s_pex', 'csv')
            C = {g: committed(os.path.join(rd, f'{g}_params_pex_rshunt1e12.csv'))
                 for g in ('ac', 'ac_load', 'tran', 'noise', 'enable')}
            C['ac_1nF'] = []
        for c, t in [('tt', 27), ('ss', -40), ('ff', 125)]:
            ca = [r for r in C['ac'] if r['corner_mos'] == c and int(r['temp']) == t][0]
            n = [k for k, d in R[v]['d2s_ac.sig'].items() if d['cond']['corner_mos'] == c and d['cond']['temp'] == t][0]
            s = ac_scalars(R[v]['d2s_ac.sig'][n], R[v]['d2s_ac.psr'][n], R[v]['d2s_ac.cm'][n], R[v]['d2s_ac.zo'][n])
            sd = _sd(R[v]['sc_ac'], corner_mos=c, temp=t)
            lab = f'{c} {t} °C 1 kΩ 100 pF'
            out += [('D2S f3dB [MHz]', lab, v, float(ca['f3dB']) / 1e6, sd[1] / 1e6, s['f3dB'] / 1e6),
                    ('D2S PSRR 1 kHz [dB]', lab, v, float(ca['PSRR_1k']), sd[3], s['PSRR_1k']),
                    ('D2S PSRR 100 kHz [dB]', lab, v, float(ca['PSRR_100k']), sd[4], s['PSRR_100k']),
                    ('D2S Zout 1 kHz [Ω]', lab, v, float(ca['Zout_1k']), sd[6], s['Zout_1k']),
                    ('D2S Zout 1 MHz [Ω]', lab, v, float(ca['Zout_1M']), sd[7], s['Zout_1M'])]
        for r in C['ac_load'] + C['ac_1nF']:
            cl, rl = float(r['cload']), float(r['rload'])
            n = [k for k, d in R[v]['d2s_ac_load.sig'].items()
                 if abs(d['cond']['cload'] - cl) < 1e-3 * cl and abs(d['cond']['rload'] - rl) < 1e-3 * rl][0]
            s = ac_scalars(R[v]['d2s_ac_load.sig'][n])
            sd = _sd(R[v]['sc_ac_load'], cload=cl, rload=rl)
            lab = f"tt 27 °C {'1 kΩ' if rl < 1e6 else '1 GΩ'} {cl * 1e12:g} pF"
            out += [('D2S f3dB [MHz]', lab, v, float(r['f3dB']) / 1e6, sd[1] / 1e6, s['f3dB'] / 1e6),
                    ('D2S peaking [dB]', lab, v, float(r['Peak_dB']), sd[2], s['Peak_dB'])]
        for r in C['tran']:
            c, cl = r['corner_mos'], float(r['cload'])
            d = find(R[v]['d2s_tran'], corner_mos=c, cload=cl)[0]
            s = tran_scalars(d)
            sd = _sd(R[v]['sc_tran'], corner_mos=c, cload=cl)
            lab = f'{c} 27 °C {cl * 1e12:g} pF'
            out += [('D2S SR rise [V/µs]', lab, v, float(r['SR_rise']) / 1e6, sd[0] / 1e6, s['SR_rise'] / 1e6),
                    ('D2S SR fall [V/µs]', lab, v, float(r['SR_fall']) / 1e6, sd[1] / 1e6, s['SR_fall'] / 1e6),
                    ('D2S ts rise 1 % [ns]', lab, v, float(r['ts_rise']) * 1e9, sd[3] * 1e9, s['ts_rise'] * 1e9),
                    ('D2S ts fall 1 % [ns]', lab, v, float(r['ts_fall']) * 1e9, sd[4] * 1e9, s['ts_fall'] * 1e9)]
        for r in C['noise']:
            t = int(r['temp'])
            d = find(R[v]['noise'], corner_mos='tt', temp=t)[0]
            s = noise_scalars(d)
            sd = _sd(R[v]['sc_noise'], corner_mos='tt', temp=t)
            lab = f'tt {t} °C'
            out += [('D2S En 1 kHz [nV/√Hz]', lab, v, float(r['En_1k']) * 1e9, sd[0] * 1e9, s['En_1k'] * 1e9),
                    ('D2S En 100 kHz [nV/√Hz]', lab, v, float(r['En_100k']) * 1e9, sd[1] * 1e9, s['En_100k'] * 1e9),
                    ('D2S Vn_int 10 Hz–10 MHz [µV]', lab, v, float(r['Vn_int']) * 1e6, sd[2] * 1e6, s['Vn_int'] * 1e6)]
        for r in C['enable']:
            sel = float(r['sel'])
            d = find(R[v]['en'], sel=sel)[0]
            s = enable_scalars(d)
            sd = _sd(R[v]['sc_enable'], sel=sel)
            lab = f'tt 27 °C sel {int(sel)}'
            out += [('D2S t_on [µs]', lab, v, float(r['t_on']) * 1e6, sd[0] * 1e6, s['t_on'] * 1e6),
                    ('D2S Iio enabled [µA]', lab, v, float(r['Iio_end']) * 1e6, sd[3] * 1e6, s['Iio_end'] * 1e6)]
    return out


def main(wout, here, design):
    style()
    out = os.path.join(here, 'plots')
    R = loadall(wout)
    plot_bode_loads(R, out)
    plot_bode_corners(R, out)
    plot_family(R, out, 'd2s_ac.zo', 'at_m', 'd2s_zout', '|Zout| at the pad [Ω]',
                'D2S output impedance |v(pad)/i_test| vs frequency (CACE ac_params; includes the 1 kΩ ∥ 100 pF load), '
                'vicm = vref = vterm = 1.65 V, corners × temperatures\n' + COND, logy=True, xlim=(10, 1e9))
    plot_family(R, out, 'd2s_ac.psr', 'at_m', 'd2s_psrr', 'PSRR = −20 log|pad / iovdd| [dB]',
                'D2S supply rejection (iovdd), output-referred as CACE PSRR_1k: 1 kΩ to vterm + 100 pF, vicm = vref = '
                '1.65 V, no mismatch\n' + COND, neg=True, ylim=(-10, 110), xlim=(10, 1e9))
    plot_step(R, out)
    plot_slot(R, out)
    plot_noise(R, out)
    plot_enable(R, out)
    summaries(R, os.path.join(here, 'csv'))
    return R


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
