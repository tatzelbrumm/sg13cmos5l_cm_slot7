# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Plots from the wrdata files (IHP sg13cmos5l simulation).

usage: python3 -I plots.py <work-dir> <out-dir>
  <work-dir>/slot/pu_<mode>_<mos>_<temp>_<vdd>.dat  (slot_modes.py, power-up transient)
  <work-dir>/bg/bgramp_<view>_<mos>_<temp>_<vdd>_<ramp>.dat (bg_core.py)
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

WORK, OUT = Path(sys.argv[1]), Path(sys.argv[2])
SLOT_SEL = [("swap", "ss", -40, 3.0), ("mon", "ss", -40, 3.0), ("default", "ss", -40, 3.0)]


def load(f):
    a = np.loadtxt(f)
    return a[:, 0], a[:, 1::2]


def slot_plot():
    files = [(s, WORK / "slot" / f"pu_{s[0]}_{s[1]}_{s[2]}_{s[3]}.dat") for s in SLOT_SEL]
    files = [(s, f) for s, f in files if f.exists()]
    if not files:
        return
    fig, ax = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    for (mode, c, t, v), f in files:
        tt, y = load(f)
        tt = tt * 1e6
        ax[0].plot(tt, y[:, 0], label=f"{mode}: bandgap g")
        ax[0].plot(tt, y[:, 4], "--", label=f"{mode}: ibg (bias_dist_pd in)")
        ax[1].plot(tt, y[:, 5], label=f"{mode}: vcm")
        ax[1].plot(tt, y[:, 6], "--", label=f"{mode}: vref")
        ax[1].plot(tt, y[:, 7], ":", label=f"{mode}: D2S pad out")
        ax[2].plot(tt, y[:, 9], label=f"{mode}: I(vdd_3v3)")
    ax[0].set_ylabel("V")
    ax[1].set_ylabel("V")
    ax[2].set_ylabel("uA")
    ax[2].set_xlabel("time [us]  (supplies 0->V 0..10 us, enable at 20 us, pad-in steps 40..90 us)")
    for a in ax:
        a.grid(alpha=0.3)
        a.legend(fontsize=6, ncol=3)
    ax[2].set_ylim(-20, 200)
    fig.suptitle("IHP sg13cmos5l simulation: slot 7 power-up, ss / -40 C / 3.0 V, pad out 1 Gohm || 10 pF\n(bg_core_pd schematic; pads, "
                 "pad_ref_rb, bias_dist_pd extracted)", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "slot_powerup_ss_m40.png", dpi=90)


def bg_plot():
    fs = sorted((WORK / "bg").glob("bgramp_schematic_*.dat"))
    if not fs:
        return
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for f in fs:
        _, _, mos, t, v, tr = f.stem.split("_")
        tt, y = load(f)
        k = 0 if tr == "1u" else 1
        ax[k].plot(tt * (1e6 if k == 0 else 1e3), y[:, 0], label=f"{mos} {t} C {v} V", lw=0.8)
    ax[0].set_xlim(0, 10)
    for a in ax:
        a.set_ylim(-1, 7)
    ax[0].set_xlabel("time [us] (vdd = en_3v3 ramp 0->V in 1 us; first 10 us of 300 us)")
    ax[1].set_xlabel("time [ms] (vdd = en_3v3 ramp 0->V in 1 ms)")
    for a in ax:
        a.set_ylabel("iout into 0.7 V [uA] (clipped: ramp displacement spikes)")
        a.grid(alpha=0.3)
        a.legend(fontsize=6)
    fig.suptitle("IHP sg13cmos5l simulation: bg_core_pd (schematic) start-up by supply ramp", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "bg_core_ramp.png", dpi=90)


slot_plot()
bg_plot()
