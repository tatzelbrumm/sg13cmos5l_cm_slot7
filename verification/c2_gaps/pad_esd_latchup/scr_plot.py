# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Plot of csv/scr_trigger.csv (lumped PNPN with ASSUMED parameters) -> plots/scr_trigger.png. Usage: python3 scr_plot.py"""
import csv
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent


def main():
    f = HERE / 'csv/scr_trigger.csv'
    if not f.exists():
        return
    rows = list(csv.DictReader(l for l in open(f) if not l.startswith('#')))
    plt.rcParams.update({'font.size': 8.5, 'axes.grid': True, 'grid.color': '#d8d8d4', 'figure.facecolor': 'white'})
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4), sharey=True)
    cols = {('300', '300'): '#2a78d6', ('300', '3000'): '#eb6834', ('3000', '300'): '#1baf7a',
            ('3000', '3000'): '#e87ba4'}
    for j, pol in enumerate(('neg', 'pos')):
        ax = axs[j]
        for (rn, rs), c in cols.items():
            for alpha, mk in (('0.01', 'o'), ('0.1', 's')):
                pts = sorted((float(r['beta_product']), float(r['i_trigger_A'])) for r in rows
                             if r['injection'] == pol and r['r_nwell_ohm'] == rn and r['r_sub_ohm'] == rs
                             and r['alpha'] == alpha and r['i_trigger_A'] != 'inf')
                if pts:
                    x, y = zip(*pts)
                    ax.loglog(x, y, mk, color=c, ms=4, mfc='none' if alpha == '0.01' else c,
                              label=f'R_nw {rn}, R_sub {rs} Ohm, alpha {alpha}' if j == 0 else None)
        ax.axhline(0.1, color='#52514e', ls='--', lw=0.8)
        ax.text(0.3, 0.11, 'JESD78 I-test 100 mA', fontsize=7)
        ax.set_xlabel('beta_npn x beta_pnp (assumed)')
        ax.set_title(f'{"negative" if pol == "neg" else "positive"} injection')
        ax.set_xlim(0.2, 200)
    axs[0].set_ylabel('forced pad current that latches the PNPN (A)')
    axs[0].legend(fontsize=5.8)
    fig.suptitle('Lumped parasitic-thyristor estimate (scr.py): ALL parameters assumed, not from the PDK; '
                 'ngspice Gummel-Poon BJTs\nmissing points: no latch up to 1 A', fontsize=8.5)
    fig.tight_layout()
    fig.savefig(HERE / 'plots/scr_trigger.png', dpi=150)
    plt.close(fig)


if __name__ == '__main__':
    main()
