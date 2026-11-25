# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Markdown tables for results.md from csv/ (no simulation). Usage: python3 tables.py > _work/tables.md
Pipes inside cells are escaped as \\|."""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG = {'gnd_vss': 'iovss gnd', 'gnd_vdd': 'iovdd gnd', 'p2p': 'other pad gnd'}


def load(name):
    f = HERE / 'csv' / name
    if not f.exists():
        return []
    return list(csv.DictReader(l for l in open(f) if not l.startswith('#')))


def fmt(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if v != v:
        return 'n/a'
    a = abs(v)
    if a >= 100:
        return '%.0f' % v
    if a >= 10:
        return '%.1f' % v
    if a >= 1:
        return '%.2f' % v
    return '%.3g' % v


def table(rows, cols, heads):
    esc = [h.replace('|', '\\|') for h in heads]
    out = ['| ' + ' | '.join(esc) + ' |', '|' + '---|' * len(cols)]
    for r in rows:
        cells = [(c(r) if callable(c) else fmt(r.get(c, ''))).replace('|', '\\|') for c in cols]
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def main():
    print('## model I-V\n')
    iv = load('model_iv.csv')
    print(table(iv, ['model', 'device', 'v_at_0.01A', 'v_at_0.1A', 'v_at_0.5A', 'v_at_1.33A'],
                ['model', 'device', 'V at 10 mA', 'V at 0.1 A', 'V at 0.5 A', 'V at 1.33 A']))
    print('\n## HBM summary (esdproxy)\n')
    s = load('hbm_summary.csv')
    for pad in ('s2d', 'd2s'):
        rows = [r for r in s if r['pad'] == pad and r['diode_model'] == 'esdproxy']
        print(f'\n### {pad}\n')
        print(table(rows, [lambda r: CFG[r['config']], 'v_hbm', 'l_hbm_uH', 'i_peak_A', 'v_pad_peak', 'v_iovdd_peak',
                           'v_iovss_peak', 'v_ring_peak', 'i_rc_clamps_peak_A'],
                    ['grounded', 'V_HBM (V)', 'L (uH)', 'I peak (A)', 'V pad peak (V)', 'V iovdd peak (V)',
                     'V iovss peak (V)', 'max |iovdd - iovss| (V)', 'RC clamps peak (A)']))
    print('\n## HBM summary (pdk)\n')
    rows = [r for r in s if r['diode_model'] == 'pdk']
    print(table(rows, ['pad', lambda r: CFG[r['config']], 'v_hbm', 'status', 't_end_ns', 'v_pad_peak',
                       'v_iovdd_peak', 'v_iovss_peak'],
                ['pad', 'grounded', 'V_HBM (V)', 'status', 'ran to (ns)', 'V pad peak (V)', 'V iovdd peak (V)',
                 'V iovss peak (V)']))
    print('\n## diodes at +-2 kV (esdproxy, L fast)\n')
    d = load('hbm_diodes.csv')
    rows = [r for r in d if r['diode_model'] == 'esdproxy' and r['run'].startswith('hbm_') and abs(int(r['v_hbm'])) == 2000
            and float(r['i_peak_A']) > 0.01]
    print(table(rows, ['pad_zapped', lambda r: CFG[r['config']], 'v_hbm', 'diode', 'type', 'area_um2', 'perim_um',
                       'i_peak_A', 'j_area_mA_um2', 'j_perim_mA_um', 'v_ak_at_peak', 'energy_nJ'],
                ['zapped', 'grounded', 'V_HBM', 'diode', 'type', 'area (um2)', 'perimeter (um)', 'I peak (A)',
                 'I / area (mA/um2)', 'I / perimeter (mA/um)', 'V_ak at peak (V)', 'energy (nJ)']))
    print('\n## largest diode current per diode over all esdproxy runs, by HBM level\n')
    best = {}
    for r in d:
        if r['diode_model'] != 'esdproxy' or not r['run'].startswith('hbm_'):
            continue
        k = (r['diode'], abs(int(r['v_hbm'])))
        if float(r['i_peak_A']) > float(best.get(k, {'i_peak_A': -1})['i_peak_A']):
            best[k] = r
    rows = [best[k] for k in sorted(best)]
    print(table(rows, ['diode', 'area_um2', lambda r: str(abs(int(r['v_hbm']))), 'i_peak_A', 'j_area_mA_um2',
                       'j_perim_mA_um', 'energy_nJ', lambda r: r['run'].replace('hbm_esdproxy_', '')],
                ['diode', 'area (um2)', '|V_HBM| (V)', 'I peak forward (A)', 'mA/um2', 'mA/um', 'energy (nJ)',
                 'worst run']))
    print('\n## oxides: worst over all esdproxy runs per device and level\n')
    m = load('hbm_mos.csv')
    best = {}
    for r in m:
        if r['diode_model'] != 'esdproxy' or not r['run'].startswith('hbm_'):
            continue
        role = r['role']
        k = (r['pad'], r['device'], abs(int(r['v_hbm'])))
        if 'largest' in role:
            k = (r['pad'], 'ANY', abs(int(r['v_hbm'])))
        if k not in best or float(r['max_vox']) > float(best[k]['max_vox']):
            best[k] = r
    for pad in ('s2d', 'd2s'):
        rows = [best[k] for k in sorted(best, key=lambda k: (k[1] == 'ANY', k[1], k[2])) if k[0] == pad]
        print(f'\n### {pad}\n')
        print(table(rows, [lambda r: r['device'] if 'largest' not in r['role'] else 'any MOS of the pad: ' + r['device'],
                           lambda r: r['role'] if 'largest' not in r['role'] else 'largest of all',
                           lambda r: str(abs(int(r['v_hbm']))), 'max_vgs', 'max_vgd', 'max_vgb', 'max_vds',
                           lambda r: r['run'].replace('hbm_esdproxy_', '')],
                    ['device', 'role', '|V_HBM| (V)', 'max |vgs| (V)', 'max |vgd| (V)', 'max |vgb| (V)',
                     'max |vds| (V)', 'worst run']))
    print('\n## I-test\n')
    it = load('itest.csv')
    print(table(it, ['diode_model', 'pad', 'injection', 'status', 'v_pad', 'i_at_vpad_limit_A', 'v_iovdd_at_pad',
                     'i_supply_mA', 'i_supply_at_0_mA', 'i_iovss_pads_mA'],
                ['diode model', 'pad', 'forced', 'sweep', 'V pad (V)', 'I at 5.4 V / -1.8 V (A)', 'V iovdd at pad (V)',
                 'I supply (mA)', 'I supply at 0 (mA)', 'I into iovss pads (mA)']))
    print('\n## overvoltage\n')
    ov = load('overvoltage.csv')
    print(table(ov, ['pad', 'v_supply', 'i_supply_mA', 'max_vgs', 'dev_vgs', 'max_vgd', 'dev_vgd', 'max_vds', 'dev_vds',
                     'max_vdb', 'dev_vdb'],
                ['pad', 'supply (V)', 'I supply (mA)', 'max |vgs|', 'device', 'max |vgd|', 'device', 'max |vds|',
                 'device', 'max |vdb|', 'device']))


if __name__ == '__main__':
    main()
