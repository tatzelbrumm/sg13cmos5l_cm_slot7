#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Tables and plots of the KLayout-pad antenna-diode check (IHP sg13cmos5l simulation).

Usage: python3 -I evaluate.py <work_dir> <ref_slot_dir> <dest_dir>
  <work_dir>      this folder's run.sh work dir: out_fixed/slot (sine, KLayout pads with the fixed diodes),
                  out_fixed/rt + out_orig/rt (DC round trip, KLayout pads fixed / as converted),
                  modes_out_fixed/<job>/slot_modes_*.csv + modes_fixed/<job>/*.log (slot_modes.py runs)
  <ref_slot_dir>  ../ac_tran's slot output (out/slot of its work dir): the schematic / magic PEX sine runs and the
                  failed KLayout sine log, as committed in ../ac_tran
  <dest_dir>      writes csv/sine_summary.csv, csv/sine_tt27.csv, csv/rt_range.csv, csv/ac_step_tt27.csv,
                  csv/modes_fixed.csv, plots/sine_tt27_fixed.png, plots/diode_step_27C.png (+ .svg if small)
Sine scalars with ../ac_tran/rt.py sine_scalars() (THD harmonics 2-7 over 200 ... 600 us); DC range metrics with
../dc_curves/rt.py metrics() (contiguous range around pad in = vref with |error from the small-signal line| < 1 mV).
"""
import csv
import glob
import importlib.util
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
WORK, REF, DEST = (Path(a).resolve() for a in sys.argv[1:4])


def load_module(name, path):
    sys.path.insert(0, str(path.parent))
    sys.modules.pop('common', None)          # ../dc_curves and ../ac_tran each have their own common.py
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    sys.path.pop(0)
    return mod


DC = load_module('dc_rt', HERE.parent / 'dc_curves' / 'rt.py')
AT = load_module('at_rt', HERE.parent / 'ac_tran' / 'rt.py')
ATC = sys.modules['common']                  # ../ac_tran/common.py (save, title, style)
HDR = ('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
       '# IHP sg13cmos5l simulation, slot 7 tier-1 deck; %s\n')
VCOL = {'schematic': '#2a78d6', 'pex': '#eb6834', 'klayout': '#1baf7a'}
VLS = {'schematic': '-', 'pex': '-.', 'klayout': ':'}
VN = {'schematic': 'schematic', 'pex': 'magic PEX', 'klayout': 'KLayout-extracted, diodes fixed'}


def sine():
    runs = {}
    for v in ('schematic', 'pex'):
        for ld in ('open', '100p'):
            runs[(v, ld)] = AT.rd(REF / f'slot_{v}_tt_27_3.3_sine_{ld}.sine')
    for ld in ('open', '100p'):
        p = WORK / 'out_fixed' / 'slot' / f'slot_klayout_tt_27_3.3_sine_{ld}.sine'
        runs[('klayout', ld)] = AT.rd(p) if p.exists() and p.stat().st_size else None
    aid = {k: (REF if k[0] != 'klayout' else WORK / 'out_fixed' / 'slot').joinpath(
        f'slot_{k[0]}_tt_27_3.3_sine_{k[1]}.aid').exists() for k in runs}
    keys = ['THD_dB', 'H2_dBc', 'H3_dBc', 'A1_out', 'gain_10k', 'delay_10k', 'err_pp', 'err_max_abs']
    rows = []
    for (v, ld), d in runs.items():
        if d is None:
            rows.append([v, ld, 'no result'] + [''] * len(keys))
            continue
        s = AT.sine_scalars(d)
        rows.append([v + ('' if v != 'klayout' else ' (antenna diodes l/w from the extracted A/P)'), ld,
                     ('rshunt=1e12' if v == 'pex' or aid[(v, ld)] else 'none')] + ['%.6g' % s[k] for k in keys])
    with open(DEST / 'csv' / 'sine_summary.csv', 'w', newline='') as f:
        f.write(HDR % 'round trip 10 kHz sine 0 ... 1 V, tt 27 C 3.3 V; THD / H dB(c) (harmonics 2-7, 200 ... 600 us), '
                'A1 V, gain_10k = A1_out / A1_in, delay_10k s, err V = pad_d2s - (vcm + pad_s2d - vref)')
        w = csv.writer(f)
        w.writerow(['pads', 'load', 'solver_aid'] + keys)
        w.writerows(rows)
    # waveform CSV (unloaded, 256 points per period over the 4 periods) and plot
    tt = 200e-6 + np.arange(1024) * 400e-6 / 1024
    cols, names = [tt], ['time']
    for v in ('schematic', 'pex', 'klayout'):
        d = runs[(v, 'open')]
        if d is None:
            continue
        if not names[1:]:
            cols.append(np.interp(tt, d['time'], d['v(padin)']))
            names.append('pad_s2d')
        exp = d['v(vcm_s2d)'] + d['v(padin)'] - d['v(vref_s2d)']
        cols += [np.interp(tt, d['time'], d['v(padout)']), np.interp(tt, d['time'], d['v(padout)'] - exp)]
        names += [f'pad_d2s_{v}', f'err_{v}']
    with open(DEST / 'csv' / 'sine_tt27.csv', 'w', newline='') as f:
        f.write(HDR % 'round trip 10 kHz sine, tt 27 C 3.3 V, unloaded (1 Gohm): pad_s2d, pad_d2s and err = pad_d2s - '
                '(vcm + pad_s2d - vref) [V] per pad view (klayout = antenna diodes fixed), resampled to 1024 points')
        w = csv.writer(f)
        w.writerow(names)
        for r in np.array(cols).T:
            w.writerow(['%.7e' % r[0]] + ['%.7f' % x for x in r[1:]])
    ATC.style()
    plt = ATC.plt
    fig, axs = plt.subplots(2, 1, figsize=(9, 6.4), sharex=True, gridspec_kw={'height_ratios': [3, 2]})
    txt = []
    ks = runs.get(('schematic', 'open'))
    for v in ('schematic', 'pex', 'klayout'):
        for ld in ('open', '100p'):
            d = runs[(v, ld)]
            if d is None:
                continue
            m = d['time'] >= 200e-6
            t = d['time'][m] * 1e6
            err = (d['v(padout)'] - (d['v(vcm_s2d)'] + d['v(padin)'] - d['v(vref_s2d)']))[m]
            axs[0].plot(t, 1e3 * err, color=VCOL[v], ls=VLS[v], lw=1.6 if ld == 'open' else 0.9,
                        alpha=1 if ld == 'open' else 0.6, label=f'{VN[v]}, {AT.LN[ld]}')
            s = AT.sine_scalars(d)
            txt.append(f"{VN[v]}, {AT.LN[ld]}: THD {s['THD_dB']:.1f} dB (H2 {s['H2_dBc']:.1f}, H3 {s['H3_dBc']:.1f} "
                       f"dBc), gain {s['gain_10k']:.4f}, delay {s['delay_10k'] * 1e9:.0f} ns, "
                       f"error {s['err_pp'] * 1e3:.1f} mVpp")
            if v != 'schematic' and ks is not None and ld == 'open':
                dd = np.interp(d['time'][m], ks['time'], ks['v(padout)'])
                axs[1].plot(t, 1e3 * (d['v(padout)'][m] - dd), color=VCOL[v], ls=VLS[v], lw=1.3,
                            label=f'pad_d2s ({VN[v]}) − pad_d2s (schematic), unloaded')
    axs[0].set_ylabel('pad_d2s − (vcm + pad_s2d − vref) [mV]')
    lo, hi = axs[0].get_ylim()
    axs[0].set_ylim(lo - 0.9 * (hi - lo), hi + 0.45 * (hi - lo))
    axs[0].legend(loc='upper right', fontsize=6.8, ncol=2)
    axs[0].text(0.01, 0.03, '\n'.join(txt), transform=axs[0].transAxes, fontsize=6.4,
                bbox=dict(fc='white', ec='#d8d8d4'))
    axs[1].axhline(0, color='#8a8984', lw=0.6)
    axs[1].set_ylabel('difference to schematic [mV]')
    axs[1].set_xlabel('time [µs]  (pad_s2d = 0.5 + 0.5 sin(2π·10 kHz·t); the run without the fix aborts at 66 µs)')
    axs[1].set_xlim(200, 600)
    axs[1].legend(loc='upper right', fontsize=6.8)
    ATC.title(fig, None, 'Round trip 10 kHz sine 0 … 1 V, tt 27 °C 3.3 V, slot 7 default mode: pads schematic, magic '
              'PEX and KLayout-extracted with the antenna diodes at their extracted size (l / w from A / P; as converted, '
              'a= / p= are ignored and the run aborts). The error vs expected is mostly the round-trip delay.\n'
              + AT.COND, 'slot3')
    ATC.save(fig, str(DEST / 'plots' / 'sine_tt27_fixed'))
    plt.close(fig)


def diode_plot():
    p = DEST / 'csv' / 'diode_iv_27C.csv'
    if not p.exists():
        return
    lines = [line for line in p.read_text().splitlines() if line and not line.startswith('#')][1:]
    a = np.array([[float(x) for x in line.split(',')] for line in lines])
    plt = ATC.plt
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.plot(a[:, 0] * 1e3, a[:, 1] * 1e12, color='#eb6834', lw=2.0,
            label='default size 0.78 × 0.78 µm (a= / p= ignored)')
    ax.plot(a[:, 0] * 1e3, a[:, 2] * 1e12, color='#2a78d6', lw=1.2, ls='--',
            label='extracted size 27.78 × 1.26 µm (l= / w= from A / P)')
    vt = 3 * 1.009 * 1.380649e-23 * 300.15 / 1.602176634e-19
    ax.axvline(vt * 1e3, color='#8a8984', lw=0.8, ls=':')
    ax.text(vt * 1e3 + 0.5, 0.5 * (a[:, 1].max() * 1e12), '3·n·kT/q = %.1f mV\n(darea n = 1.009):\nngspice switches\n'
            'to its reverse-region\nexpression, which adds\nthe soft-breakdown term\n(ibv, nbv = 48.9)' % (vt * 1e3),
            fontsize=7.2, va='center')
    ax.set_xlabel('reverse voltage on the S2D pad diode X$65 (cathode = pad, anode = iovss) [mV]')
    ax.set_ylabel('reverse current [pA]')
    ax.legend(loc='upper left', fontsize=7.4)
    fig.suptitle('IHP sg13cmos5l simulation (PDK diodes.lib, ngspice-47): dantenna alone\nm = 2 as the S2D pad\'s '
                 'X$65, 27 °C, DC sweep in 0.5 mV steps, gmin 1e-12: the same 74 pA step for both sizes;\nonly with '
                 'the default size does the sine through it abort (csv/diode_tran.csv)', fontsize=9, y=0.995, va='top')
    fig.tight_layout()
    ATC.save(fig, str(DEST / 'plots' / 'diode_step_27C'))
    plt.close(fig)


def rt_range():
    ref = {}
    with open(HERE.parent / 'dc_curves' / 'csv' / 'rt_summary.csv') as f:
        for r in csv.DictReader(line for line in f if not line.startswith('#')):
            ref[(r['pads'], r['corner_mos'], int(r['temp']), float(r['vdd']))] = r
    runs = {('fixed',) + k: d for k, d in DC.load(WORK / 'out_fixed' / 'rt').items()}
    runs.update({('rerun',) + k: d for k, d in DC.load(WORK / 'out_orig' / 'rt').items()})
    rows = []
    for (c, t, v) in DC.PTS:
        for view in ('schematic', 'pex', 'klayout'):
            r = ref.get((view, c, t, v))
            if r:
                rows.append([f'{view} (../dc_curves committed)', c, t, v, r['gain'], r['max_abs_err_0to1V_mV'],
                             r['in_lo_1mV'], r['in_hi_1mV'], r['out_lo_1mV'], r['out_hi_1mV'], '', ''])
        for tagv, view, lab in (('rerun', 'schematic', 'schematic (rerun here)'), ('rerun', 'pex', 'pex (rerun here)'),
                                ('rerun', 'klayout', 'klayout as converted (rerun here)'),
                                ('fixed', 'klayout', 'klayout, antenna diodes fixed')):
            d = runs.get((tagv, view, c, t, v))
            if d is None:
                continue
            m = DC.metrics(d)
            x = d['v(padin)']
            cm = float(np.interp(0.5, x, (d['v(outp)'] + d['v(outn)']) / 2))
            rows.append([lab, c, t, v, '%.5f' % m['G'], '%.3f' % (m['emax01'] * 1e3), '%.4f' % m['lo1'],
                         '%.4f' % m['hi1'], '%.4f' % m['olo1'], '%.4f' % m['ohi1'],
                         '%.4f' % float(np.interp(0.5, x, d['v(vcm_s2d)'])), '%.4f' % cm])
    with open(DEST / 'csv' / 'rt_range.csv', 'w', newline='') as f:
        f.write(HDR % 'DC round trip, pad out unloaded; gain, max |err| over pad in 0 ... 1 V [mV], pad in / out range '
                'with |error from the small-signal line| < 1 mV [V] (../dc_curves/rt.py definitions); vcm_s2d and the S2D '
                'output common mode (outp + outn) / 2 at pad in 0.5 V [V]')
        w = csv.writer(f)
        w.writerow(['pads', 'corner_mos', 'temp', 'vdd', 'gain', 'max_abs_err_0to1V_mV', 'in_lo_1mV', 'in_hi_1mV',
                    'out_lo_1mV', 'out_hi_1mV', 'vcm_s2d_V', 's2d_out_cm_V'])
        w.writerows(rows)
    # largest difference fixed vs as-converted over all saved node voltages
    diffs = []
    for k in runs:
        if k[0] == 'fixed' and ('rerun',) + k[1:] in runs:   # klayout only
            a, b = runs[k], runs[('rerun',) + k[1:]]
            n = min(len(a['v(padin)']), len(b['v(padin)']))
            diffs.append(max(float(np.abs(a[h][:n] - b[h][:n]).max()) for h in a if h.startswith('v(')))
    return max(diffs) if diffs else None


def ac_step():
    """AC / step at tt 27 C with the fixed diodes against ../ac_tran's committed KLayout / schematic rows."""
    ref = {}
    for ana in ('ac', 'step'):
        with open(HERE.parent / 'ac_tran' / 'csv' / f'rt_{ana}_summary.csv') as f:
            for r in csv.DictReader(line for line in f if not line.startswith('#')):
                if r['point'] == 'tt 27 °C 3.3 V' and r['view'] in ('schematic', 'pex', 'klayout'):
                    ref[(ana, r['view'], r['load'])] = r
    rows = []
    sd = WORK / 'out_fixed' / 'slot'
    for ld in ('open', '10p', '100p'):
        p = sd / f'slot_klayout_tt_27_3.3_ac.ac_{ld}'
        fx = AT.ac_scalars(AT.rd(p)) if p.exists() else None
        for v in ('schematic', 'pex', 'klayout'):
            r = ref.get(('ac', v, ld))
            if r:
                rows.append(['ac', f'{v} (../ac_tran committed)', ld, 'f3dB_Hz', '%.6g' % float(r['f3dB'])])
        if fx:
            rows.append(['ac', 'klayout, antenna diodes fixed', ld, 'f3dB_Hz', '%.6g' % fx['f3dB']])
    p = sd / 'slot_klayout_tt_27_3.3_step_open.step'
    fx = AT.step_scalars(AT.rd(p)) if p.exists() else None
    for k in ('ts1_rise', 'ts0.1_rise', 'gain_step'):
        for v in ('schematic', 'pex', 'klayout'):
            r = ref.get(('step', v, 'open'))
            if r:
                rows.append(['step', f'{v} (../ac_tran committed)', 'open', k, '%.6g' % float(r[k])])
        if fx:
            rows.append(['step', 'klayout, antenna diodes fixed', 'open', k, '%.6g' % fx[k]])
    with open(DEST / 'csv' / 'ac_step_tt27.csv', 'w', newline='') as f:
        f.write(HDR % 'round trip tt 27 C 3.3 V: f-3dB (relative to 1 kHz) and step 0.25 -> 0.75 V settling (1 % / '
                '0.1 %, s) and gain, ../ac_tran/rt.py definitions')
        w = csv.writer(f)
        w.writerow(['analysis', 'pads', 'load', 'quantity', 'value'])
        w.writerows(rows)


def modes():
    rows = []
    keys = ['err_max_mV', 'v_g_V', 'vcm_V', 'vref_V']
    for f in sorted(glob.glob(str(WORK / 'modes_out_fixed' / '*' / 'slot_modes_*.csv'))):
        d = Path(f).parent.name
        logs = sorted(glob.glob(str(WORK / 'modes_fixed' / d / '*.log')))
        tr = ''
        if logs:
            m = re.search(r'doAnalyses: \w+:\s+(.*?)\n', Path(logs[0]).read_text())
            tr = m.group(1).strip() if m else ''
        with open(f) as fh:   # slot_modes.py writes key=value fields
            for rec in csv.reader(line for line in fh if line.strip() and not line.startswith('#')):
                r = dict(x.split('=', 1) for x in rec)
                rows.append([r['mode'], r['mos'], r['temp'], r['vdd'], r['variant'], r.get('cload', '')]
                            + [r.get(k, '') for k in keys] + [tr])
    with open(DEST / 'csv' / 'modes_fixed.csv', 'w', newline='') as f:
        f.write(HDR % "../slot_modes_bg/slot_modes.py (dcop = the designer's mode DC deck; pu / pu0 = power-up transient "
                'with / without 10 pF on pad out), KLayout pads with the antenna diodes fixed; err_max_mV = max |pad out - '
                'expected| or FAILED; ngspice = first abort message')
        w = csv.writer(f)
        w.writerow(['mode', 'corner_mos', 'temp', 'vdd', 'variant', 'cload'] + keys + ['ngspice'])
        w.writerows(rows)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    for s in ('csv', 'plots'):
        (DEST / s).mkdir(parents=True, exist_ok=True)
    sine()
    diode_plot()
    ac_step()
    print('max |dV| DC round trip, fixed vs as converted (all saved nodes, all PVT):', rt_range())
    modes()
