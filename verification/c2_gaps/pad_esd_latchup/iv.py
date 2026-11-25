# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""What the compact models do at ESD / latch-up currents: forward I-V (DC, 1 uA ... 2 A) of the pad's antenna
diodes (PDK diodes.lib and the ESD-diode proxy of common.py) and of the drain paths (drain junction, and the channel where the gate tie turns it on) of the pad clamps / output
devices (PSP JUNCAP2 in the PDK hv MOS models; gate tied as in the pad: to the device's own source / rail).
IHP sg13cmos5l simulation, tt, 27 C. Usage: python3 iv.py <work_dir>  ->  csv/model_iv.csv, plots/model_iv.png"""
import sys
from pathlib import Path

import numpy as np

import common as C

DUTS = [
    # name, netlist line (forced current enters node a; return node 0), description
    ('dpantenna 1.26x27.78 (S2D DP1)', 'X1 a 0 dpantenna l=27.78u w=1.26u', 'p+/n-well, pad -> iovdd'),
    ('dantenna 1.26x27.78 (S2D DN1)', 'X1 a 0 dantenna l=27.78u w=1.26u', 'n+/p-sub forward: iovss -> pad'),
    ('dpantenna 1.26x65.8 (D2S DP0)', 'X1 a 0 dpantenna l=65.8u w=1.26u', 'p+/n-well, pad -> iovdd'),
    ('dantenna 1.26x67.6 (D2S DN0)', 'X1 a 0 dantenna l=67.6u w=1.26u', 'n+/p-sub forward: iovss -> pad'),
    ('MCP drain path, hv PMOS 266.4/0.6 ng 40 (S2D)', 'X1 a g 0 0 sg13_hv_pmos w=266.4u l=0.6u ng=40\nRg g 0 6.768k',
     'pad (drain) -> iovdd (body, source); gate to iovdd via 6.768 kOhm (rppd value of the IO library cell Clamp_P20N0D)'),
    ('MCN drain path, hv NMOS 88/0.6 ng 20 (S2D)', 'X1 0 g a a sg13_hv_nmos w=88u l=0.6u ng=20\nRg g a 1.959k',
     'iovss (body, source) -> pad (drain); gate to iovss via 1.959 kOhm (Clamp_N20N0D)'),
    ('OP drain path, hv PMOS 546.12/0.6 ng 82 (D2S)', 'X1 a 0 0 0 sg13_hv_pmos w=546.12u l=0.6u ng=82',
     'pad (drain) -> iovdd (body, source); gate at iovdd (disabled)'),
    ('ON drain path, hv NMOS 299.2/1 ng 68 (D2S)', 'X1 0 a a a sg13_hv_nmos w=299.2u l=1u ng=68',
     'iovss (body, source) -> pad (drain); gate at iovss (disabled)'),
]
POINTS = [1e-3, 1e-2, 0.1, 0.5, 1.0, 1.33, 2.0]


def main():
    work = Path(sys.argv[1]).resolve() / 'iv'
    work.mkdir(parents=True, exist_ok=True)
    rows = []
    curves = {}
    for var in ('pdk', 'esdproxy'):
        for i, (name, line, desc) in enumerate(DUTS):
            if var == 'esdproxy' and 'antenna' not in name:
                continue
            p = work / f'iv_{var}_{i}.spice'
            p.write_text(C.SPDX + f'* forward I-V: {name}\n' + C.model_block('tt', var, sys.argv[1]) +
                         f'I1 0 a 1u\n{line}\n.option rshunt=1e15\n.control\nset filetype=binary\n'
                         f'dc I1 1u 2 2m\nwrite {p.stem}.raw\n.endc\n.end\n')
            C.run_ngspice(p, p.with_suffix('.log'))
            pl = C.read_raw(p.with_suffix('.raw'))[-1]['vars']
            ii = pl['i(i1)'] if 'i(i1)' in pl else pl[list(pl)[0]]
            v = pl['v(a)']
            curves[(var, name)] = (ii, v)
            r = dict(model=var, device=name, direction=desc)
            for x in POINTS:
                r[f'v_at_{x:g}A'] = round(float(np.interp(x, ii, v)), 3)
            rows.append(r)
            p.with_suffix('.raw').unlink()
    C.write_csv(C.HERE / 'csv/model_iv.csv', rows,
                C.LABEL + '\nforward voltage (V) at the forced current, DC, tt 27 C; pdk = PDK models as they are, '
                'esdproxy = antenna diodes re-modeled with the PDK ESD-diode models (common.py)')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    cols = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#7b5ea7', '#52514e', '#0b0b0b']
    for k, ((var, name), (ii, v)) in enumerate(curves.items()):
        idx = [d[0] for d in DUTS].index(name)
        ax.plot(v, ii, color=cols[idx], ls='-' if var == 'pdk' else '--', lw=1.2,
                label=f'{name} [{var}]')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(0.3, 5000)
    ax.set_ylim(1e-4, 2)
    ax.set_xlabel('forward voltage (V)')
    ax.set_ylabel('forced current (A)')
    ax.legend(fontsize=5.8, loc='lower right')
    ax.set_title(f'Forward I-V of the pad devices in the compact models ({C.LABEL})\nsolid: PDK models as they are; '
                 'dashed: antenna diodes as ESD-diode proxy', fontsize=8)
    fig.tight_layout()
    fig.savefig(C.HERE / 'plots/model_iv.png', dpi=150)
    plt.close(fig)
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
