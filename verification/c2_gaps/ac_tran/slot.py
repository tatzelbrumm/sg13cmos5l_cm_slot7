#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Round trip pad_s2d -> S2D -> slot 7 (default mode) -> D2S -> pad_d2s: AC, step and sine (IHP sg13cmos5l simulation).

Usage: python3 -I slot.py <work_dir> <out_dir> <job> [<job> ...]
  job = <view>:<mos>:<temp>:<vdd>:<analysis>[:<load>]
    view      klayout | schematic | pex (the two custom pads; see ../dc_curves/roundtrip.py, identical deck)
    analysis  ac    pad_s2d DC 0.5 V + AC 1 V, dec 40 10 Hz ... 1 GHz, three loads in one deck (open, 1k|10p, 1k|100p)
              step  pad_s2d 0.25 V -> 0.75 V at 2 us (10 ns edge), back at 7 us (10 ns), tran to 12 us, max step 2 ns
              sine  pad_s2d 0.5 + 0.5 sin(2 pi 10 kHz t) (0 ... 1 V), tran 0 ... 600 us, written from 200 us (4 periods)
    load      (step / sine) open | 10p | 100p      open = 1 Gohm to ground only (the designer's tier-1 deck)
  e.g. schematic:tt:27:3.3:ac, pex:tt:27:3.3:step:100p; a 7th field 'rshunt' forces the solver aid rshunt=1e12 (check
  of its effect, tag suffix _rshunt), e.g. schematic:tt:27:3.3:ac:open:rshunt
Writes <out_dir>/<tag>.<suffix> (wrdata) and <tag>.log.

The deck is the designer's tier-1 slot deck (design repository commit 9052bd35, docs/slot7_hookup/tier1/run_tier1.py,
imported from there) exactly as ../dc_curves/roundtrip.py builds it: slot_7 source netlist in its default mode (all
mode bits 0, enable 1.2 V), pad_ref_rb and bias_dist_pd KLayout-extracted (run_tier1.wrapped()), bg_core_pd schematic,
S2D vref / vcm and D2S vref from the replica pad_ref_rb, iref from bg_core_pd through bias_dist_pd; vdd_3v3 = iovdd;
.option gmin=1e-12 (+ rshunt=1e12 for the PEX pads); 1 Gohm from pad_d2s to ground. Load (added here): RL from pad_d2s
to vterm, CL from pad_d2s to ground; vterm = an ideal copy (VCVS, gain 1) of the D2S reference v(vref_d2s), so the
1 kOhm carries no DC current at the operating point, as the CACE testbench's vterm = vref; open = RL 1 Tohm, CL 1 aF.
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
RUNS = WORK / 'slot_runs'
PDK = '/foss/pdks/ihp-sg13cmos5l'
LOADS = {'open': ('1e12', '1e-18'), '10p': ('1k', '10p'), '100p': ('1k', '100p')}
# transient solver aid as the designer's own tier-1 transient (run_tier1.py) and ../slot_modes_bg: gear integration
# (without it the sine run aborted at 66 us, 'timestep too small' at the slot's vcm sense source v.xs.vsv0)
TOPT = ' method=gear'
SAVE = 'v(padin) v(padout) v(vcm_s2d) v(vref_s2d) v(vref_d2s) v(outp) v(outn) v(vinp) v(vinn) i(vio) i(vslot)'


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


def control(ana, load, tag):
    o = f'{OUT}/{tag}'
    wr = 'set wr_singlescale\nset wr_vecnames\noption numdgt=9\n'
    if ana == 'ac':
        s = wr
        for ld in ('open', '10p', '100p'):
            r, c = LOADS[ld]
            s += f"""alter RL = {r}
alter CL = {c}
ac dec 40 10 1G
let g_db = db(v(padout))
let g_ph = 180/pi*cph(v(padout))
let s_db = db(v(outp) - v(outn))
let s_ph = 180/pi*cph(v(outp) - v(outn))
let l_db = db(v(vinp) - v(vinn))
wrdata {o}.ac_{ld} g_db g_ph s_db s_ph l_db
"""
        return s
    r, c = LOADS[load]
    head = f'alter RL = {r}\nalter CL = {c}\n'
    if ana == 'step':
        return head + wr + f"""tran 2n 12u 0 2n
wrdata {o}.step {SAVE}
"""
    if ana == 'sine':
        return head + wr + f"""tran 39.0625n 600u 200u 39.0625n
wrdata {o}.sine {SAVE}
"""
    raise ValueError(ana)


def run(job):
    p = job.split(':')
    view, c, t, v, ana = p[0], p[1], int(p[2]), float(p[3]), p[4]
    load = p[5] if len(p) > 5 else 'open'
    force = len(p) > 6 and p[6] == 'rshunt'  # check job: the solver aid forced on (effect of rshunt)
    tag = f'slot_{view}_{c}_{t}_{v}_{ana}' + ('' if ana == 'ac' else f'_{load}') + ('_rshunt' if force else '')
    rdir = RUNS / tag
    mac = WORK / 'tier1' / 'macros'
    bg = mac / 'bg_core_pd' / 'netlist' / 'schematic' / 'bg_core_pd_magic.spice'
    opt = '.option gmin=1e-12' + (' rshunt=1e12' if view == 'pex' or force else '') + ('' if ana == 'ac' else TOPT)
    vin = {'ac': 'dc 0.5 ac 1', 'step': 'pulse(0.25 0.75 2u 10n 10n 4.99u 20u)',
           'sine': 'dc 0.5 sin(0.5 0.5 10k)'}[ana]
    deck = f"""* slot-7 round trip S2D -> slot 7 default mode -> D2S, {ana} {load}, pads: {view}, {c} {t} C, {v} V
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
Vin padin 0 {vin}
Rout padout 0 1G
RL padout vterm 1e12
CL padout 0 1e-18
Et vterm 0 vref_d2s 0 1
XS vdd_3v3 0 enable 0 0 0 0 0 0 b0 b1 b2 b3 vref_s2d outp outn vcm_s2d en0 enb0 iref0 vinp vinn vref_d2s iref1 enb1 en1 do0 do1 do2 do3 do4 do5 do6 do7 do8 do9 do10 do11 v12 0 slot_7
Vv12 v12 0 1.2
X2S iovdd 0 iovdd 0 padin outp outn vcm_s2d vref_s2d iref0 en0 enb0 sg13cmos5l_IOPadSingle2Diff
X2D iovdd 0 iovdd 0 padout vinp vinn vref_d2s iref1 en1 enb1 sg13cmos5l_IOPadDiff2Single
.control
save {SAVE}
op
set wr_singlescale
set wr_vecnames
option numdgt=9
wrdata {OUT}/{tag}.op {SAVE}
{control(ana, load, tag)}echo "SLOTDONE"
.endc
.end
"""
    spiceinit = Path(PDK) / 'libs.tech' / 'ngspice' / '.spiceinit'
    (rdir / '.spiceinit').write_text(spiceinit.read_text())
    sfx = ['ac_open', 'ac_10p', 'ac_100p'] if ana == 'ac' else [ana]
    for f0 in [OUT / f'{tag}.{x}' for x in sfx + ['op', 'aid']]:
        f0.unlink(missing_ok=True)
    f = rdir / f'{tag}.spice'
    f.write_text(deck)
    pr = subprocess.run(['ngspice', '-b', f.name], cwd=rdir, capture_output=True, text=True)
    log = pr.stdout[-20000:] + '\n--- stderr ---\n' + pr.stderr[-20000:]
    ok = all((OUT / f'{tag}.{x}').exists() for x in sfx) and 'aborted' not in pr.stdout + pr.stderr
    if not ok and 'rshunt' not in opt:
        # solver aid on failure only (the operating point of some cold schematic runs does not converge, e.g.
        # schematic ss -40 C 3.0 V: gmin and source stepping fail): rerun with rshunt=1e12 (1 Tohm from every node to
        # ground), as the PEX pads always have; recorded in <tag>.aid and in the summary CSVs
        f.write_text(deck.replace(opt, opt + ' rshunt=1e12', 1))
        pr = subprocess.run(['ngspice', '-b', f.name], cwd=rdir, capture_output=True, text=True)
        log += '\n=== retry with rshunt=1e12 ===\n' + pr.stdout[-20000:] + '\n--- stderr ---\n' + pr.stderr[-20000:]
        ok = all((OUT / f'{tag}.{x}').exists() for x in sfx) and 'aborted' not in pr.stdout + pr.stderr
        (OUT / f'{tag}.aid').write_text('rshunt=1e12 (retry after the run without it failed)\n')
    (OUT / f'{tag}.log').write_text(log)
    print(tag, 'ok' if ok else 'FAILED', '(rshunt retry)' if (OUT / f'{tag}.aid').exists() else '', flush=True)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    for j in JOBS:
        run(j)
