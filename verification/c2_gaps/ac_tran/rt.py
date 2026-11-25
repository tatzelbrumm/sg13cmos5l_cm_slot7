#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Slot-7 round trip pad_s2d -> S2D -> slot 7 (default mode) -> D2S -> pad_d2s: Bode, step, sine plots and scalars
(IHP sg13cmos5l simulation; pads schematic | magic PEX | KLayout-extracted, the rest of the slot as the designer's
tier-1 deck).

Usage: rt.py <slot_out_dir> <ac_tran_dir>
Reads the slot.py outputs, writes <ac_tran_dir>/plots/rt_*.png|svg and <ac_tran_dir>/csv/rt_*_summary.csv.
"""
import csv
import glob
import os
import re
import sys

import numpy as np

from common import COLOR, first_fall, logx_interp, last_cross, plt, save, style, title

VIEWS = ['schematic', 'pex', 'klayout']
VN = {'schematic': 'schematic', 'pex': 'magic PEX', 'klayout': 'KLayout-extracted'}
VLS = {'schematic': '-', 'pex': '--', 'klayout': ':'}
POINTS = [('tt', 27, 3.3), ('ss', -40, 3.0), ('ff', 125, 3.6), ('fs', 125, 3.6), ('sf', -40, 3.0)]
LOADS = ['open', '10p', '100p']
LN = {'open': 'unloaded (1 GΩ)', '10p': '1 kΩ ∥ 10 pF', '100p': '1 kΩ ∥ 100 pF'}
LC = {'open': '#2a78d6', '10p': '#1baf7a', '100p': '#eb6834'}
PTN = lambda c, t, v: f'{c} {t} °C {v} V'  # noqa: E731
COND = ('slot 7 default mode, tier-1 deck (replica bias pad_ref_rb: vref_s2d ≈ 0.49 V, vcm ≈ 1.26 V; iref from '
        'the slot bandgap); load = 1 kΩ to an ideal copy of vref_d2s, CL to ground')


def rd(path):
    with open(path) as f:
        head = f.readline().split()
    a = np.loadtxt(path, skiprows=1, ndmin=2)
    return {h: a[:, i] for i, h in enumerate(head)} if a.size else None


def tag(view, pt, ana, load=None):
    c, t, v = pt
    return f'slot_{view}_{c}_{t}_{v}_{ana}' + (f'_{load}' if load else '')


def get(sdir, view, pt, ana, load=None, sfx=None):
    p = os.path.join(sdir, tag(view, pt, ana, None if ana == 'ac' else load) + '.' + (sfx or ana))
    return rd(p) if os.path.exists(p) and os.path.getsize(p) > 0 else None


def ac_scalars(d):
    f, g = d['frequency'], d['g_db']
    g1k = logx_interp(f, g, 1e3)
    i0 = np.searchsorted(f, 1e3)
    f3 = first_fall(f, g - g1k, -3.0, i0)
    return {'G_1k_dB': g1k, 'f3dB': f3, 'Peak_dB': float((g - g1k)[i0:].max()), 'ph_f3dB': logx_interp(f, d['g_ph'], f3)}


def step_scalars(d):
    t, o = d['time'], d['v(padout)']
    r = {}
    for edge, (t0, t1) in (('rise', (2e-6, 7e-6)), ('fall', (7e-6, 12e-6))):
        vi, vf = np.interp([t0 - 0.01e-6, t1 - 0.1e-6], t, o)
        step = vf - vi
        r[f'step_{edge}'] = step
        for p in (1.0, 0.1):
            r[f'ts{p:g}_{edge}'] = last_cross(t, np.abs(o - vf), p / 100 * abs(step), t0, t1 - 0.1e-6) - t0
        vn = (o - vi) / step
        m = (t >= t0) & (t <= t1)
        r[f'overshoot_{edge}'] = 100 * float(vn[m].max() - 1)
    r['gain_step'] = r['step_rise'] / 0.5
    return r


def harmonics(t, y, f0, n=7, t0=200e-6, periods=4):
    """amplitudes of harmonics 1..n over an integer number of periods (uniform resampling, as the D2S tb_thd)"""
    N = 1024
    tt = t0 + np.arange(N) * periods / f0 / N
    yy = np.interp(tt, t, y)
    ph = 2 * np.pi * f0 * (tt - tt[0])
    h = [2 * np.hypot(np.mean(yy * np.cos(k * ph)), np.mean(yy * np.sin(k * ph))) for k in range(1, n + 1)]
    return np.array(h), tt, yy


def sine_scalars(d):
    t = d['time']
    hi, _, _ = harmonics(t, d['v(padin)'], 1e4)
    ho, tt, yo = harmonics(t, d['v(padout)'], 1e4)
    exp = d['v(vcm_s2d)'] + d['v(padin)'] - d['v(vref_s2d)']
    err = d['v(padout)'] - exp
    m = t >= 200e-6
    # phase of the output fundamental relative to the input fundamental
    ph = 2 * np.pi * 1e4 * (tt - tt[0])
    yi = np.interp(tt, t, d['v(padin)'])
    zi = np.mean(yi * np.exp(-1j * ph))
    zo = np.mean(yo * np.exp(-1j * ph))
    lag = -np.angle(zo / zi)
    return {'THD_dB': 20 * np.log10(np.sqrt(np.sum(ho[1:] ** 2)) / ho[0]),
            'THD_in_dB': 20 * np.log10(np.sqrt(np.sum(hi[1:] ** 2)) / hi[0]),
            'H2_dBc': 20 * np.log10(ho[1] / ho[0]), 'H3_dBc': 20 * np.log10(ho[2] / ho[0]),
            'A1_out': ho[0], 'A1_in': hi[0], 'gain_10k': ho[0] / hi[0], 'delay_10k': lag / (2 * np.pi * 1e4),
            'err_pp': float(err[m].max() - err[m].min()), 'err_max_abs': float(np.abs(err[m]).max())}


def plot_bode_tt(S, out):
    fig, axs = plt.subplots(2, 1, figsize=(8.5, 6.4), sharex=True)
    txt = []
    pt = POINTS[0]
    for v in VIEWS:
        for ld in LOADS:
            d = S.get(('ac', v, pt, ld))
            if d is None:
                continue
            axs[0].semilogx(d['frequency'], d['g_db'], color=LC[ld], ls=VLS[v], lw=1.3)
            axs[1].semilogx(d['frequency'], d['g_ph'], color=LC[ld], ls=VLS[v], lw=1.3)
            s = ac_scalars(d)
            txt.append(f"{VN[v]}, {LN[ld]}: f−3dB {s['f3dB'] / 1e6:.3f} MHz, peak +{s['Peak_dB']:.2f} dB")
    axs[0].axhline(-3, color='#52514e', lw=0.7, ls='-.')
    axs[0].set_ylim(-30, 3)
    axs[0].set_ylabel('|pad_d2s / pad_s2d| [dB]')
    axs[0].text(0.01, 0.03, '\n'.join(txt), transform=axs[0].transAxes, fontsize=6.6, bbox=dict(fc='white', ec='#d8d8d4'))
    axs[1].set_ylim(-360, 10)
    axs[1].set_yticks(range(-360, 1, 90))
    axs[1].set_ylabel('phase [°]')
    axs[1].set_xlabel('frequency [Hz]')
    axs[1].set_xlim(1e3, 1e8)
    hs = [plt.Line2D([], [], color=LC[k]) for k in LOADS] + [plt.Line2D([], [], color='#52514e', ls=VLS[v]) for v in VIEWS]
    axs[1].legend(hs, [LN[k] for k in LOADS] + [f'pads {VN[v]}' for v in VIEWS], loc='lower left', fontsize=7, ncol=2)
    title(fig, None, 'Round trip pad_s2d → S2D → slot 7 → D2S → pad_d2s, small signal at pad_s2d = 0.5 V DC, '
          'tt 27 °C 3.3 V\n' + COND, 'slot3')
    save(fig, os.path.join(out, 'rt_bode_tt27'))


def plot_bode_pvt(S, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.2), sharex=True, sharey='row')
    for j, ld in enumerate(['open', '100p']):
        for v in ('schematic', 'pex'):
            for pt in POINTS:
                d = S.get(('ac', v, pt, ld))
                if d is None:
                    continue
                axs[0, j].semilogx(d['frequency'], d['g_db'], color=COLOR[pt[0]], ls=VLS[v], lw=1.1)
                axs[1, j].semilogx(d['frequency'], d['g_ph'], color=COLOR[pt[0]], ls=VLS[v], lw=1.1)
        axs[0, j].set_title(LN[ld])
        axs[0, j].axhline(-3, color='#52514e', lw=0.7, ls='-.')
        axs[1, j].set_xlabel('frequency [Hz]')
    axs[0, 0].set_ylim(-30, 3)
    axs[1, 0].set_ylim(-360, 10)
    axs[1, 0].set_yticks(range(-360, 1, 90))
    axs[1, 0].set_xlim(1e3, 1e8)
    axs[0, 0].set_ylabel('|pad_d2s / pad_s2d| [dB]')
    axs[1, 0].set_ylabel('phase [°]')
    hs = [plt.Line2D([], [], color=COLOR[p[0]]) for p in POINTS] + \
         [plt.Line2D([], [], color='#52514e', ls=VLS[v]) for v in ('schematic', 'pex')]
    axs[1, 0].legend(hs, [PTN(*p) for p in POINTS] + ['pads schematic', 'pads magic PEX'], loc='lower left', fontsize=6.8,
                     ncol=2)
    title(fig, None, 'Round trip small-signal gain over the five tier-1 PVT points (corner, temperature, '
          'iovdd = vdd_3v3), pad_s2d = 0.5 V DC\n' + COND, 'both')
    save(fig, os.path.join(out, 'rt_bode_pvt'))


def plot_f3(rows, out):
    fig, ax = plt.subplots(figsize=(9, 3.8))
    xs = np.arange(len(POINTS))
    mk = {'open': 'o', '10p': 's', '100p': 'D'}
    for i, v in enumerate(VIEWS):
        for k, ld in enumerate(LOADS):
            y = [next((r['f3dB'] / 1e6 for r in rows if r['view'] == v and r['point'] == PTN(*p) and r['load'] == ld),
                      np.nan) for p in POINTS]
            ax.plot(xs + (i - 1) * 0.22 + (k - 1) * 0.06, y, mk[ld], color=LC[ld], mfc='white' if v == 'klayout' else
                    (LC[ld] if v == 'schematic' else 'none'), ms=5.5, ls='none')
    ax.set_xticks(xs)
    ax.set_xticklabels([PTN(*p) for p in POINTS])
    ax.set_ylabel('round-trip −3 dB bandwidth [MHz]')
    ax.set_ylim(0, None)
    hs = [plt.Line2D([], [], marker=mk[k], color=LC[k], ls='none') for k in LOADS] + \
         [plt.Line2D([], [], marker='o', color='#52514e', ls='none', mfc=m) for m in ('#52514e', 'none', 'white')]
    ax.legend(hs, [LN[k] for k in LOADS] + ['pads schematic (left)', 'pads magic PEX (middle)',
                                            'pads KLayout-extracted (right)'], fontsize=7, ncol=2, loc='lower left')
    title(fig, None, 'Round-trip −3 dB bandwidth (from |gain| at 1 kHz) per tier-1 PVT point, view and load; '
          'pad_s2d = 0.5 V DC\n' + COND, 'slot3')
    save(fig, os.path.join(out, 'rt_f3db'))


def plot_step_tt(S, out):
    fig, axs = plt.subplots(2, 2, figsize=(10, 6.4), sharex='col', gridspec_kw={'height_ratios': [3, 2]})
    pt = POINTS[0]
    txt = []
    for v in ('schematic', 'pex'):
        for ld in LOADS:
            d = S.get(('step', v, pt, ld))
            if d is None:
                continue
            s = step_scalars(d)
            t = d['time'] * 1e6
            for j, (t0, t1, e0) in enumerate([(1.8, 4.0, 2.0), (6.8, 9.0, 7.0)]):
                m = (t >= t0) & (t <= t1)
                if v == 'schematic' and ld == 'open':
                    axs[0, j].plot(t[m], d['v(padin)'][m], color='#8a8984', lw=1.2, label='pad_s2d (source)')
                axs[0, j].plot(t[m], d['v(padout)'][m], color=LC[ld], ls=VLS[v], lw=1.2)
                vf = np.interp(e0 + 4.9, t, d['v(padout)'])
                axs[1, j].plot(t[m], 1e3 * (d['v(padout)'][m] - vf), color=LC[ld], ls=VLS[v], lw=1.1)
                edge = 'rise' if j == 0 else 'fall'
                ts = s[f'ts1_{edge}'] * 1e6 + e0
                axs[1, j].axvline(ts, color=LC[ld], ls=VLS[v], lw=0.7)
                axs[1, j].plot([ts], [0], 'v', color=LC[ld], ms=5)
            txt.append(f"{VN[v]}, {LN[ld]}: 1 % {s['ts1_rise'] * 1e9:.0f} / {s['ts1_fall'] * 1e9:.0f} ns, "
                       f"0.1 % {s['ts0.1_rise'] * 1e9:.0f} / {s['ts0.1_fall'] * 1e9:.0f} ns, step {s['step_rise'] * 1e3:.1f} mV")
    for j in range(2):
        axs[1, j].axhspan(-5, 5, color='#e6e6e3', zorder=0)
        axs[1, j].set_ylim(-25, 25)
        axs[1, j].set_xlabel('time [µs]')
    axs[0, 0].set_title('rising: pad_s2d 0.25 → 0.75 V at 2 µs (10 ns edge)')
    axs[0, 1].set_title('falling: 0.75 → 0.25 V at 7 µs')
    axs[0, 0].set_ylabel('voltage [V]')
    axs[1, 0].set_ylabel('pad_d2s − final [mV]\n(grey ±5 mV = ±1 %)')
    axs[0, 1].text(0.98, 0.5, 'settling (rise / fall), markers = 1 %:\n' + '\n'.join(txt), transform=axs[0, 1].transAxes,
                   ha='right', va='center', fontsize=6.2, bbox=dict(fc='white', ec='#d8d8d4'))
    axs[1, 0].set_xlim(1.9, 3.3)
    axs[1, 1].set_xlim(6.9, 8.3)
    hs = [plt.Line2D([], [], color='#8a8984')] + [plt.Line2D([], [], color=LC[k]) for k in LOADS] + \
         [plt.Line2D([], [], color='#52514e', ls=VLS[v]) for v in ('schematic', 'pex')]
    axs[0, 0].legend(hs, ['pad_s2d (source)'] + [f'pad_d2s, {LN[k]}' for k in LOADS] + ['pads schematic',
                                                                                         'pads magic PEX'],
                     loc='center right', fontsize=6.8)
    title(fig, None, 'Round-trip step response, tt 27 °C 3.3 V: pad_s2d (source) and pad_d2s; settling time to '
          '1 % of the 0.5 V step marked\n' + COND, 'both')
    save(fig, os.path.join(out, 'rt_step_tt27'))


def plot_step_pvt(S, out):
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.9), sharey=True)
    for j, ld in enumerate(['open', '100p']):
        for v in ('schematic', 'pex', 'klayout'):
            for pt in POINTS:
                d = S.get(('step', v, pt, ld))
                if d is None:
                    continue
                t = d['time'] * 1e6
                m = (t >= 1.9) & (t <= 4.0)
                vf = np.interp(6.9, t, d['v(padout)'])
                axs[j].plot((t[m] - 2) * 1e3, 1e3 * (d['v(padout)'][m] - vf), color=COLOR[pt[0]], ls=VLS[v], lw=1.0)
        axs[j].axhspan(-5, 5, color='#e6e6e3', zorder=0)
        axs[j].axhspan(-0.5, 0.5, color='#cfcfcb', zorder=0)
        axs[j].set_ylim(-30, 10)
        axs[j].set_xlim(0, 1500)
        axs[j].set_title(LN[ld])
        axs[j].set_xlabel('time after the rising input edge [ns]')
    axs[0].set_ylabel('pad_d2s − final [mV]')
    hs = [plt.Line2D([], [], color=COLOR[p[0]]) for p in POINTS] + \
         [plt.Line2D([], [], color='#52514e', ls=VLS[v]) for v in VIEWS]
    axs[0].legend(hs, [PTN(*p) for p in POINTS] + [f'pads {VN[v]}' for v in VIEWS], fontsize=6.5, ncol=2,
                  loc='lower right')
    title(fig, None, 'Round-trip settling after the 0.25 → 0.75 V pad_s2d step (10 ns edge), tier-1 PVT points; '
          'grey bands ±5 mV (1 %) and ±0.5 mV (0.1 %)\n' + COND, 'slot3')
    save(fig, os.path.join(out, 'rt_step_pvt'))


def plot_sine(S, out):
    fig, axs = plt.subplots(2, 1, figsize=(9, 6.2), sharex=True, gridspec_kw={'height_ratios': [3, 2]})
    pt = POINTS[0]
    txt = []
    for v in ('schematic', 'pex'):
        for ld in ('open', '100p'):
            d = S.get(('sine', v, pt, ld))
            if d is None:
                continue
            t = d['time'] * 1e6
            m = t >= 200
            s = sine_scalars(d)
            if v == 'schematic' and ld == 'open':
                axs[0].plot(t[m], d['v(padin)'][m], color='#8a8984', lw=1.4, label='pad_s2d (source)')
                axs[0].plot(t[m], (d['v(vcm_s2d)'] + d['v(padin)'] - d['v(vref_s2d)'])[m], color='#0b0b0b', lw=0.8,
                            ls='-.', label='expected vcm + pad_s2d − vref (replica values)')
            axs[0].plot(t[m], d['v(padout)'][m], color=LC[ld], ls=VLS[v], lw=1.1,
                        label=f'pad_d2s, {VN[v]}, {LN[ld]}')
            err = d['v(padout)'] - (d['v(vcm_s2d)'] + d['v(padin)'] - d['v(vref_s2d)'])
            axs[1].plot(t[m], 1e3 * err[m], color=LC[ld], ls=VLS[v], lw=1.1)
            if v == 'schematic' and ld == 'open':
                # residual after removing the output's fitted dc + 10 kHz fundamental: distortion (+ numerical noise)
                ph = 2 * np.pi * 1e4 * t[m] * 1e-6
                A = np.column_stack([np.ones(m.sum()), np.cos(ph), np.sin(ph)])
                cf = np.linalg.lstsq(A, d['v(padout)'][m], rcond=None)[0]
                axs[1].plot(t[m], 10e3 * (d['v(padout)'][m] - A @ cf), color='#0b0b0b', lw=0.9,
                            label='×10: schematic, unloaded: pad_d2s − its fitted dc + 10 kHz fundamental (distortion)')
            txt.append(f"{VN[v]}, {LN[ld]}: THD {s['THD_dB']:.1f} dB (H2 {s['H2_dBc']:.1f}, H3 {s['H3_dBc']:.1f} dBc), "
                       f"gain {s['gain_10k']:.4f}, delay {s['delay_10k'] * 1e9:.0f} ns, error {s['err_pp'] * 1e3:.1f} mVpp")
    axs[0].set_ylabel('voltage [V]')
    axs[0].legend(loc='upper right', fontsize=6.8)
    axs[1].set_ylabel('pad_d2s − expected [mV]')
    axs[1].set_xlabel('time [µs]')
    axs[1].set_xlim(200, 600)
    lo, hi = axs[1].get_ylim()
    axs[1].set_ylim(lo - 1.1 * (hi - lo), hi + 0.3 * (hi - lo))
    axs[1].legend(loc='upper right', fontsize=6.6)
    axs[1].text(0.01, 0.03, '\n'.join(txt), transform=axs[1].transAxes, fontsize=6.6, bbox=dict(fc='white', ec='#d8d8d4'))
    title(fig, None, 'Round trip with a 10 kHz sine pad_s2d = 0.5 + 0.5 sin(2π·10 kHz·t) (0 … 1 V), tt 27 °C 3.3 V; '
          'THD from harmonics 2–7 over the 4 periods shown. The error vs expected is dominated by the round-trip '
          'delay (2π·f·A·τ); the black curve (×10) is the distortion alone\n' + COND, 'both')
    save(fig, os.path.join(out, 'rt_sine_tt27'))


def consistency(sdir, here, S, rows):
    """round trip vs ../dc_curves (same deck, DC sweep): 10 Hz AC gain and step gain vs the DC small-signal slope,
    operating point (replica vref / vcm) vs the DC sweep at pad_s2d = 0.5 V -> tables/rt_consistency.md"""
    from common import md_table
    p = os.path.join(here, '..', 'dc_curves', 'csv', 'rt_summary.csv')
    dc = {}
    with open(p) as f:
        for r in csv.DictReader(l for l in f if not l.startswith('#')):
            dc[(r['pads'], r['corner_mos'], int(r['temp']))] = r
    out = []
    for v in VIEWS:
        for pt in POINTS:
            r = dc.get((v, pt[0], pt[1]))
            d = S.get(('ac', v, pt, 'open'))
            if r is None or d is None:
                continue
            g10 = 10 ** (d['g_db'][0] / 20)
            st = [x for x in rows['step'] if x['view'] == v and x['point'] == PTN(*pt) and x['load'] == 'open']
            op = rd(os.path.join(sdir, tag(v, pt, 'ac') + '.op'))
            out.append([VN[v], PTN(*pt), f"{float(r['gain']):.5f}", f'{g10:.5f}',
                        f"{st[0]['gain_step']:.5f}" if st else '—',
                        f"{float(r['vref_s2d']):.4f} / {float(r['vcm']):.4f}",
                        f"{op['v(vref_s2d)'][0]:.4f} / {op['v(vcm_s2d)'][0]:.4f}"])
    # effect of the solver aid rshunt=1e12 (check job schematic:tt:27:3.3:ac:open:rshunt)
    note = ''
    for ld in LOADS:
        p0 = os.path.join(sdir, 'slot_schematic_tt_27_3.3_ac.ac_' + ld)
        p1 = os.path.join(sdir, 'slot_schematic_tt_27_3.3_ac_rshunt.ac_' + ld)
        if os.path.exists(p0) and os.path.exists(p1):
            a0, a1 = ac_scalars(rd(p0)), ac_scalars(rd(p1))
            note += (f"\nrshunt=1e12 forced, schematic tt 27 °C, {LN[ld]}: f−3dB {a1['f3dB'] / 1e6:.4f} vs "
                     f"{a0['f3dB'] / 1e6:.4f} MHz ({100 * (a1['f3dB'] / a0['f3dB'] - 1):+.4f} %), gain at 1 kHz "
                     f"{a1['G_1k_dB'] - a0['G_1k_dB']:+.6f} dB\n")
    os.makedirs(os.path.join(here, 'tables'), exist_ok=True)
    open(os.path.join(here, 'tables', 'rt_consistency.md'), 'w').write(
        '<!-- SPDX-FileCopyrightText: 2026 Christoph Maier -->\n<!-- SPDX-License-Identifier: Apache-2.0 -->\n'
        '<!-- generated by rt.py -->\n' + md_table(
            ['pads', 'PVT', 'DC slope (../dc_curves)', '\\|gain\\| at 10 Hz (AC, unloaded)', 'step gain (0.5 V step, unloaded)',
             'vref_s2d / vcm DC sweep [V]', 'vref_s2d / vcm here (op) [V]'], out) + '\n' + note)


def main(sdir, here):
    style()
    out = os.path.join(here, 'plots')
    S = {}
    for v in VIEWS:
        for pt in POINTS:
            for ld in LOADS:
                d = get(sdir, v, pt, 'ac', sfx=f'ac_{ld}')
                if d is not None:
                    S[('ac', v, pt, ld)] = d
                for ana in ('step', 'sine'):
                    d = get(sdir, v, pt, ana, ld)
                    if d is not None:
                        S[(ana, v, pt, ld)] = d
    rows = {'ac': [], 'step': [], 'sine': []}
    for (ana, v, pt, ld), d in S.items():
        aid = os.path.join(sdir, tag(v, pt, ana, None if ana == 'ac' else ld) + '.aid')
        base = {'view': v, 'point': PTN(*pt), 'load': ld, 'aid': 'rshunt' if v == 'pex' or os.path.exists(aid) else ''}
        if ana == 'ac':
            rows['ac'].append({**base, **ac_scalars(d)})
        elif ana == 'step':
            if d['time'][-1] < 11.9e-6:
                continue
            rows['step'].append({**base, **step_scalars(d)})
        else:
            if d['time'][-1] < 599e-6:
                continue
            rows['sine'].append({**base, **sine_scalars(d)})
    units = {'ac': 'G_1k_dB dB (pad_d2s/pad_s2d at 1 kHz), f3dB Hz, Peak_dB dB above the 1 kHz gain, ph_f3dB deg',
             'step': 'step V, ts<p>_<edge> s (settling to p % of the step after the input edge start), overshoot %',
             'sine': 'THD / H dB(c), A1 V, gain_10k = A1_out/A1_in, delay_10k s, err V (pad_d2s - expected, 200-600 us)'}
    for g, rr in rows.items():
        if not rr:
            continue
        with open(os.path.join(here, 'csv', f'rt_{g}_summary.csv'), 'w', newline='') as f:
            f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
                    f'# IHP sg13cmos5l simulation: slot-7 round trip {g}, pads schematic | magic PEX | KLayout-extracted; '
                    f'units: {units[g]}\n')
            w = csv.DictWriter(f, fieldnames=list(rr[0]))
            w.writeheader()
            for r in sorted(rr, key=lambda r: (VIEWS.index(r['view']), r['point'], LOADS.index(r['load']))):
                w.writerow({k: (f'{x:.6g}' if isinstance(x, float) else x) for k, x in r.items()})
    consistency(sdir, here, S, rows)
    plot_bode_tt(S, out)
    plot_bode_pvt(S, out)
    plot_f3(rows['ac'], out)
    plot_step_tt(S, out)
    plot_step_pvt(S, out)
    plot_sine(S, out)
    return rows


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(*sys.argv[1:])
