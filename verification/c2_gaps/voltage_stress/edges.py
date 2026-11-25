#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Solver check of the transient overshoots: the same enable-edge transient with different time-step limits /
integration methods, node waveforms around the edges, and the largest |VGS| / |VDS| per setting.

Usage: python3 -I edges.py <work_dir> <out_dir> <base_job> <aid> [<aid> ...]
  base_job e.g. en:tt:27:3.6 ; aid '' (the setting of the stress runs: gear, cshunt 1 fF, max step 10 ns) or one of
  step2n / step05n / step01n / trap / nocshunt / nqs (vs.py variant chk_<aid>). The runs are made with vs.py (KEEP_RAW=1).
Writes <out_dir>/csv/solver_check_<base>.csv and <out_dir>/plots/solver_check_<base>.png.
Nodes plotted: the bg_core_pd start-up chain node net1 (largest excursion found), the bias_dist_pd spare output isp,
vdd_3v3 and the slot's en_b.
"""
import csv
import gzip
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rawread  # noqa: E402

SPDX = '# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
WORK, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
BASE, AIDS = sys.argv[3], sys.argv[4:]
NODES = ['xs.xbg.net1', 'xs.xbg.net7', 'xs.isp', 'xs.en_b']
WIN = {'en': [(1.95, 2.45), (21.95, 22.45)], 'off': [(0.95, 1.45)]}
LAB = {'': 'gear, cshunt 1 fF, max step 10 ns (stress runs)', 'step2n': 'max step 2 ns', 'step05n': 'max step 0.5 ns',
       'step01n': 'max step 0.1 ns', 'trap': 'trapezoidal', 'nocshunt': 'gear, no cshunt',
       'nqs': 'NQS model (rfmode=1) on bg_core_pd and ls_up_fs', 'nqsbg': 'NQS model (rfmode=1) on bg_core_pd'}


def tag_of(job):
    p = job.split(':')
    return f'{p[0]}_{p[1]}_{p[2]}_{p[3]}' + (f'_{p[4]}' if len(p) > 4 and p[4] else '')


def main():
    kind = BASE.split(':')[0]
    res, waves = [], {}
    env = dict(os.environ, KEEP_RAW='1')
    for aid in AIDS:
        job = BASE + (f':chk_{aid}' if aid else '')
        tag = tag_of(job)
        raw = WORK / 'runs' / tag / f'{tag}.raw'
        dev = WORK / 'dev' / f'{tag}.csv.gz'
        if not (raw.exists() and dev.exists()):
            subprocess.run([sys.executable, '-I', str(HERE / 'vs.py'), str(WORK), job], env=env, check=False)
        if not (raw.exists() and dev.exists()):
            res.append([aid or 'default', LAB[aid], 'FAILED', '', '', '', '', ''])
            continue
        names, x, data = rawread.read(raw)
        idx = {n.lower(): i for i, n in enumerate(names)}
        w = {n: data[:, idx[f'v({n})']] for n in NODES}
        waves[aid] = (x, w)
        with gzip.open(WORK / 'dev' / f'{tag}.csv.gz', 'rt') as fh:
            fh.readline()
            rows = list(csv.DictReader(fh))
        mg = max(rows, key=lambda r: abs(float(r['vgs'])))
        md = max(rows, key=lambda r: abs(float(r['vds'])))
        res.append([aid or 'default', LAB[aid], len(x), f"{w['xs.xbg.net1'].max():.3f}", f"{w['xs.xbg.net1'].min():.3f}",
                    f"{w['xs.isp'].max():.3f}", f"{abs(float(mg['vgs'])):.3f} {mg['inst']}",
                    f"{abs(float(md['vds'])):.3f} {md['inst']}"])
    base = BASE.replace(':', '_')
    (OUT / 'csv').mkdir(parents=True, exist_ok=True)
    (OUT / 'plots').mkdir(parents=True, exist_ok=True)
    with open(OUT / 'csv' / f'solver_check_{base}.csv', 'w', newline='') as f:
        f.write(SPDX)
        wr = csv.writer(f)
        wr.writerow(['setting', 'what', 'time_points', 'net1_max_V', 'net1_min_V', 'isp_max_V', 'max_abs_vgs_V_device',
                     'max_abs_vds_V_device'])
        wr.writerows(res)
    wins = WIN.get(kind, [(0, float(max(x[-1] for x, _ in waves.values())) * 1e6)])
    fig, axs = plt.subplots(len(NODES), len(wins), figsize=(5 * len(wins), 2.0 * len(NODES)), squeeze=False,
                            sharex='col')
    for j, (a, b) in enumerate(wins):
        for i, n in enumerate(NODES):
            ax = axs[i][j]
            for aid, (x, w) in waves.items():
                m = (x >= a * 1e-6) & (x <= b * 1e-6)
                ax.plot(x[m] * 1e6, w[n][m], lw=1, label=LAB[aid])
            ax.set_ylabel(f'v({n}) [V]', fontsize=8)
            ax.grid(alpha=0.3)
        axs[-1][j].set_xlabel('time [us]')
    axs[0][0].legend(fontsize=7)
    fig.suptitle(f'Solver check, {BASE} (IHP sg13cmos5l simulation, ngspice-47)', fontsize=10)
    fig.tight_layout()
    fig.savefig(OUT / 'plots' / f'solver_check_{base}.png', dpi=130,
                metadata={'Copyright': '2026 Christoph Maier, Apache-2.0'})
    Path(str(OUT / 'plots' / f'solver_check_{base}.png') + '.license').write_text(SPDX.replace('# ', ''))
    for r in res:
        print(r)


if __name__ == '__main__':
    main()
