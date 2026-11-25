#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Round trip pad in -> S2D -> slot 7 (default mode) -> D2S -> pad out, DC sweep (IHP sg13cmos5l simulation).

Usage: python3 -I roundtrip.py <work_dir> <out_dir> <job> [<job> ...]
  job = <view>:<mos>:<temp>:<vdd>     view = klayout | schematic | pex (the two custom pads only, see below)
  e.g. schematic:tt:27:3.3. Writes <out_dir>/rt_<view>_<mos>_<temp>_<vdd>.csv (sweep) and .log (ngspice output).

The deck is the designer's tier-1 slot deck (design repository commit 9052bd35, docs/slot7_hookup/tier1/run_tier1.py;
imported from there, so the slot glue and the other blocks are the same): slot_7 (source netlist) in its default mode
(all mode bits 0, enable 1.2 V), pad_ref_rb and bias_dist_pd from their KLayout-extracted netlists (converted and wrapped
by run_tier1.wrapped()), bg_core_pd schematic, ls_up_fs / en_ctrl_3v3 / hv_logic source netlists; vdd_3v3 = iovdd;
S2D vref / vcm and D2S vref come from the slot's replica bias pad_ref_rb (not set by sources), iref from bg_core_pd
through bias_dist_pd. Pad out unloaded (1 Gohm to ground, as run_tier1.py). Models: MOS corner on hv and lv, res_typ,
pnp typ, diodes.lib (as run_tier1.py), plus the IHP IO library sg13cmos5l_io.spice and cap_typ (needed by the
schematic pad netlists; as the pads' CACE templates).

Pad views (both pads always the same view):
  klayout    netlist/layout/<cell>_klayout.cir at 9052bd35 (the designer's tier-1 view, converted by run_tier1.wrapped())
  schematic  the CACE schematic netlists of the pads at 91a7da8b (cace/netlist/schematic/<cell>.spice, written by
             cace_dc.sh's schematic runs)
  pex        the magic C-coupled PEX netlists as prepared by cace_dc.sh's pex runs (cace/netlist_pex/pex/<cell>.spice:
             S2D from the design repository, D2S from ../d2s_pex), with ngspice option rshunt=1e12 (needed by the D2S
             PEX netlist, see ../d2s_pex/README.md)
The pads' internal subcircuits (unit_r2 appears in both pads) get a per-pad prefix, so that the two netlists do not
redefine each other's subcircuits.

Sweep: pad in (Vin) -0.3 ... 3.3 V in 5 mV steps. Error = pad_out - (v(vcm_s2d) + v(padin) - v(vref_s2d)), the
designer's expected value with the replica's actual vcm / vref (run_tier1.py), and err_ss = deviation from the
small-signal line (slope from pad = vref_s2d +- 0.1 V).
"""
import re
import subprocess
import sys
from pathlib import Path

WORK, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
JOBS = sys.argv[3:]
T1 = WORK / 'tier1' / 'docs' / 'slot7_hookup' / 'tier1'
sys.path.insert(0, str(T1))
import run_tier1 as T  # noqa: E402

PADS = ['sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single']
RUNS = WORK / 'rt_runs'
PDK = '/foss/pdks/ihp-sg13cmos5l'


def prefixed(src, dst, cell, pfx):
    """Copy a pad netlist with every subckt except the pad cell renamed to <pfx>_<name> (definitions and calls)."""
    txt = Path(src).read_text()
    names = [n for n in re.findall(r'^\.subckt\s+(\S+)', txt, re.M | re.I) if n != cell]
    for n in names:
        txt = re.sub(r'(?<![\w.#$])' + re.escape(n) + r'(?![\w.#$])', f'{pfx}_{n}', txt)
    Path(dst).write_text(txt)
    return dst


def includes(view, rdir):
    rdir.mkdir(parents=True, exist_ok=True)
    T.RUNS = rdir
    other = [T.wrapped(c) for c in ('pad_ref_rb', 'bias_dist_pd')]
    if view == 'klayout':
        pads = [T.wrapped(c) for c in PADS]
    else:
        pads = []
        for c, pfx in zip(PADS, ('s2dpad', 'd2spad')):
            d = 'netlist/schematic' if view == 'schematic' else 'netlist_pex/pex'
            src = WORK / 'design' / 'macros' / c / 'verification' / 'cace' / d / f'{c}.spice'
            pads.append(prefixed(src, rdir / f'{c}_{view}.spice', c, pfx))
    return [str(rdir / p) for p in other] + [str(rdir / p) for p in pads]


def run(job):
    view, c, t, v = job.split(':')
    t, v = int(t), float(v)
    tag = f'rt_{view}_{c}_{t}_{v}'
    rdir = RUNS / tag
    mac = WORK / 'tier1' / 'macros'
    bg = mac / 'bg_core_pd' / 'netlist' / 'schematic' / 'bg_core_pd_magic.spice'
    opt = '.option gmin=1e-12' + (' rshunt=1e12' if view == 'pex' else '')
    deck = f"""* round trip S2D -> slot 7 default mode -> D2S, pads: {view}, {c} {t} C, {v} V
.lib cornerMOShv.lib mos_{c}
.lib cornerMOSlv.lib mos_{c}
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerPNP.lib typ
.include {PDK}/libs.tech/ngspice/models/diodes.lib
.include sg13cmos5l_io.spice
.include {mac}/hv_logic/netlist/source/hv_logic.spice
.include {mac}/en_ctrl_3v3/netlist/source/en_ctrl_3v3.spice
.include {bg}
""" + ''.join(f'.include {i}\n' for i in includes(view, rdir)) + f""".include {mac}/slot_7/netlist/source/slot_7.spice
.temp {t}
{opt}
Vslot vdd_3v3 0 {v}
Vio iovdd 0 {v}
Ven enable 0 1.2
Vin padin 0 0.5
Rout padout 0 1G
XS vdd_3v3 0 enable 0 0 0 0 0 0 b0 b1 b2 b3 vref_s2d outp outn vcm_s2d en0 enb0 iref0 vinp vinn vref_d2s iref1 enb1 en1 do0 do1 do2 do3 do4 do5 do6 do7 do8 do9 do10 do11 v12 0 slot_7
Vv12 v12 0 1.2
X2S iovdd 0 iovdd 0 padin outp outn vcm_s2d vref_s2d iref0 en0 enb0 sg13cmos5l_IOPadSingle2Diff
X2D iovdd 0 iovdd 0 padout vinp vinn vref_d2s iref1 en1 enb1 sg13cmos5l_IOPadDiff2Single
.control
save v(padin) v(padout) v(vcm_s2d) v(vref_s2d) v(vref_d2s) v(outp) v(outn) v(vinp) v(vinn) i(vio)
dc Vin -0.3 3.3 0.005
set wr_singlescale
set wr_vecnames
option numdgt=9
wrdata {OUT}/{tag}.csv v(padin) v(padout) v(vcm_s2d) v(vref_s2d) v(vref_d2s) v(outp) v(outn) v(vinp) v(vinn) i(vio)
echo "RTDONE"
.endc
.end
"""
    f = rdir / f'{tag}.spice'
    f.write_text(deck)
    spiceinit = Path(PDK) / 'libs.tech' / 'ngspice' / '.spiceinit'
    (rdir / '.spiceinit').write_text(spiceinit.read_text())
    p = subprocess.run(['ngspice', '-b', f.name], cwd=rdir, capture_output=True, text=True)
    (OUT / f'{tag}.log').write_text(p.stdout[-20000:] + '\n--- stderr ---\n' + p.stderr[-20000:])
    ok = 'RTDONE' in p.stdout and (OUT / f'{tag}.csv').exists()
    ab = re.search(r'doAnalyses: DC:\s+(.*?)\n', p.stdout + p.stderr)
    if ab or 'aborted' in p.stdout + p.stderr:
        print(tag, 'ABORTED (sweep written up to the abort point):', ab.group(1) if ab else '')
    else:
        print(tag, 'ok' if ok else 'FAILED')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    for j in JOBS:
        run(j)
