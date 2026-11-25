#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Slot 7 round trip pad_s2d -> S2D -> slot 7 -> D2S -> pad_d2s with the slot as extracted from final/gds/slot_7.gds
(IHP sg13cmos5l simulation, ngspice-47 with the IHP OSDI models).

Usage: python3 -I sim.py <work_dir> <job> [<job> ...]      (one ngspice process at a time)
  job = <view>:<mos>:<temp>:<vdd>:<analysis>[:<load>]
  view  prev  the deck of the earlier slot runs (../ac_tran/slot.py, ../dc_curves/roundtrip.py, pads 'pex'): slot_7
              source netlist (design repository 9052bd35) with pad_ref_rb / bias_dist_pd KLayout-extracted (converted
              and wrapped by run_tier1.wrapped()), bg_core_pd schematic, s7_ctrl / ls_up_fs / hv_logic source netlists;
              both pads magic C-coupled PEX (the netlists of those runs)
        c     the whole slot magic C-coupled (prep.py: nets/slot_7_c.spice), pads as 'prev' (nets/<cell>_prev.spice)
        cc    the whole slot magic C-coupled, both pads magic C-coupled re-extracted with their substrate capacitance
              (nets/<cell>_c.spice; the 'prev' pad netlists lack it, see pexfix.py / README.md)
        rc    the whole slot magic full-RC (nets/slot_7_rc.spice), both pads magic full-RC (nets/<cell>_rc.spice);
        cs    as c, with ngspice's default solver SPARSE 1.3 (check: every other view uses KLU, .option klu; with
              SPARSE the full-RC op took 282 s at tt 27 C, with KLU 63 s; the earlier runs used SPARSE)
        hyb   as prev, with pad_ref_rb replaced by its magic C-coupled extraction (cut from slot_7.gds; prep.py)
        ps    as prev, with SPARSE (the disabled operating point of prev does not converge with KLU)
  analysis
        op    operating point enabled (enable 1.2 V), then disabled (enable 0 V), pad in 0.5 V
        opi   operating point enabled with 0 V sources in the two iref lines slot -> pads (bias currents)
        dc    pad in -0.3 ... 3.3 V, 5 mV steps (as ../dc_curves/roundtrip.py)
        ac    pad in 0.5 V DC + 1 V AC, dec 40 10 Hz ... 1 GHz, loads open, 1k|10p, 1k|100p in one deck (../ac_tran)
        step  pad in 0.25 -> 0.75 V at 2 us (10 ns edges), back at 7 us, tran to 12 us, max step 2 ns (../ac_tran)
        pu    power-up / enable: vdd_3v3 = iovdd 0 -> V in 10 us, enable 0 -> 1.2 V at 20 us (100 ns edge), pad in
              0.5 V, pad out 1 Gohm + 10 pF (as ../slot_modes_bg 'pu'); tran to 40 us, 10 ns max step, uic
              (the extracted slot stalls in the supply ramp: c tt 27 C at 2.778 us, i.e. ~0.92 V, after 60 min)
        en    enable transient: supplies on, operating point with enable 0 V (no uic), enable 0 -> 1.2 V at 2 us
              (100 ns edge), pad in 0.5 V, pad out 1 Gohm + 10 pF; tran to 20 us, 10 ns max step
        mode_<m>  m = swap | mon | feed | ext (tt only): DC as the designer's run_modes.py (design repository 9052bd35):
              pad in 0 ... 1 V in 50 mV steps (feed: op, pad in 0.5 V); feed: bus0 / bus1 through 10 kohm from 1.45 /
              1.05 V; ext: bus2 / bus3 through 10 kohm from 1.30 / 0.50 V; key dig_in3 = 1
  load  (step) open | 10p | 100p; open = 1 Tohm / 1 aF; RL to an ideal copy of v(vref_d2s), CL to ground (../ac_tran)
Options: .option gmin=1e-12 rshunt=1e12 klu in every run (cs: no klu) (the PEX pads need rshunt, ../d2s_pex; the earlier 'pex' runs had
it too); transient additionally method=gear (as ../ac_tran), pu also cshunt=1e-15 (as ../slot_modes_bg).
Writes <work_dir>/out/<tag>.<suffix> (wrdata) and <tag>.log; prints '<tag> ok|FAILED <seconds>'. Environment:
SIM_TIMEOUT = wall-clock limit per attempt in s (default 2400 for transients, 900 otherwise); ngspice runs with OMP_NUM_THREADS=1.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(sys.argv[1]).resolve()
OUT = WORK / 'out'
RUNS = WORK / 'runs'
T1 = WORK / 'tier1' / 'docs' / 'slot7_hookup' / 'tier1'
MAC = WORK / 'tier1' / 'macros'
NETS = WORK / 'nets'
PDK = '/foss/pdks/ihp-sg13cmos5l'
PADS = ['sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single']
LOADS = {'open': ('1e12', '1e-18'), '10p': ('1k', '10p'), '100p': ('1k', '100p')}
SAVE = 'v(padin) v(padout) v(vcm_s2d) v(vref_s2d) v(vref_d2s) v(outp) v(outn) v(vinp) v(vinn) i(vio) i(vslot)'
MODES = {'default': ('0 0 0 0 0 0', 'direct'), 'swap': ('1 0 0 1 0 0', 'crossed'), 'mon': ('0 1 0 1 0 0', 'direct'),
         'feed': ('0 0 1 1 0 0', 'feed'), 'ext': ('0 0 0 1 0 1', 'ext')}
EXP = {'direct': 'v(vcm_s2d) + v(padin) - v(vref_s2d)', 'crossed': 'v(vcm_s2d) - v(padin) + v(vref_s2d)',
       'feed': 'v(vcm_s2d) + (v(b0) - v(b1))/2', 'ext': '1.30 + v(padin) - 0.50'}


def prefixed(src, dst, cell, pfx):
    """copy a pad netlist with every subckt except the pad cell renamed to <pfx>_<name> (as ../ac_tran/slot.py)"""
    txt = Path(src).read_text()
    names = [n for n in re.findall(r'^\.subckt\s+(\S+)', txt, re.M | re.I) if n != cell]
    for n in names:
        txt = re.sub(r'(?<![\w.#$])' + re.escape(n) + r'(?![\w.#$])', f'{pfx}_{n}', txt)
    Path(dst).write_text(txt)
    return dst


def includes(view, rdir):
    rdir.mkdir(parents=True, exist_ok=True)
    pv = {'rc': 'rc', 'cc': 'c'}.get(view, 'prev')
    pads = [str(prefixed(NETS / f'{c}_{pv}.spice', rdir / f'{c}_{pv}.spice', c, p))
            for c, p in zip(PADS, ('s2dpad', 'd2spad'))]
    if view in ('prev', 'ps', 'hyb'):
        sys.path.insert(0, str(T1))
        import run_tier1 as T  # noqa: E402
        T.RUNS = rdir
        other = [str(rdir / T.wrapped(c)) for c in ('pad_ref_rb', 'bias_dist_pd')]
        if view == 'hyb':
            other[0] = str(NETS / 'pad_ref_rb_c.spice')
        lib = [f'{MAC}/hv_logic/netlist/source/hv_logic.spice', f'{MAC}/en_ctrl_3v3/netlist/source/en_ctrl_3v3.spice',
               f'{MAC}/bg_core_pd/netlist/schematic/bg_core_pd_magic.spice']
        return lib + other + pads + [f'{MAC}/slot_7/netlist/source/slot_7.spice']
    return pads + [str(NETS / f"slot_7_{'rc' if view == 'rc' else 'c'}.spice")]


def deck(view, c, t, v, ana, load, rdir, tag):
    o = f'{OUT}/{tag}'
    mode = ana[5:] if ana.startswith('mode_') else 'default'
    bits = [float(b) * 1.2 for b in MODES[mode][0].split()]
    kind = MODES[mode][1]
    opt = '.option gmin=1e-12 rshunt=1e12' + ('' if view in ('cs', 'ps') else ' klu') + \
        (' method=gear' if ana in ('step', 'pu', 'en') else '') + (' cshunt=1e-15' if ana in ('pu', 'en') else '')
    vin = {'ac': 'dc 0.5 ac 1', 'step': 'pulse(0.25 0.75 2u 10n 10n 4.99u 20u)'}.get(ana, 'dc 0.5')
    rl, cl = LOADS[load] if ana == 'step' else (('1e12', '10p') if ana in ('pu', 'en') else LOADS['open'])
    sup = f'pwl(0 0 10u {v})' if ana == 'pu' else f'{v}'
    ven = {'pu': 'pwl(0 0 20u 0 20.1u 1.2)', 'en': 'pwl(0 0 2u 0 2.1u 1.2)'}.get(ana, '1.2')
    bus = 'Rb0 b0 0 1G\nRb1 b1 0 1G\nRb2 b2 0 1G\nRb3 b3 0 1G\n'
    if kind == 'feed':
        bus = 'Vb0 b0s 0 1.45\nVb1 b1s 0 1.05\nRb0 b0s b0 10k\nRb1 b1s b1 10k\nRb2 b2 0 1G\nRb3 b3 0 1G\n'
    if kind == 'ext':
        bus = 'Rb0 b0 0 1G\nRb1 b1 0 1G\nVb2 b2s 0 1.30\nVb3 b3s 0 0.50\nRb2 b2s b2 10k\nRb3 b3s b3 10k\n'
    wr = 'set wr_singlescale\nset wr_vecnames\noption numdgt=9\n'
    save = SAVE + ' v(b0) v(b1) v(b2) v(b3)'
    if ana == 'opi':
        ctl = f'op\n{wr}wrdata {o}.opi i(vpi0) i(vpi1) v(iref0) v(iref1)\n'
    elif ana == 'op':
        ctl = f"""op
{wr}wrdata {o}.op {save}
alter Ven = 0
op
wrdata {o}.opoff {save}
"""
    elif ana == 'dc':
        ctl = f'dc Vin -0.3 3.3 0.005\n{wr}wrdata {o}.dc {save}\n'
    elif ana == 'ac':
        ctl = wr
        for ld in ('open', '10p', '100p'):
            r, cc = LOADS[ld]
            ctl += f"""alter RL = {r}
alter CL = {cc}
ac dec 40 10 1G
let g_db = db(v(padout))
let g_ph = 180/pi*cph(v(padout))
let s_db = db(v(outp) - v(outn))
let l_db = db(v(vinp) - v(vinn))
wrdata {o}.ac_{ld} g_db g_ph s_db l_db
"""
    elif ana == 'step':
        ctl = f'tran 2n 12u 0 2n\n{wr}wrdata {o}.step {save}\n'
    elif ana == 'pu':
        ctl = f'tran 10n 40u 0 10n uic\n{wr}linearize\nwrdata {o}.pu {save} v(enable)\n'
    elif ana == 'en':
        ctl = f'tran 10n 20u 0 10n\n{wr}linearize\nwrdata {o}.en {save} v(enable)\n'
    elif kind == 'feed':
        ctl = f'op\nlet ex = {EXP[kind]}\n{wr}wrdata {o}.{ana} {save} ex\n'
    else:
        ctl = f'dc Vin 0 1.0 0.05\nlet ex = {EXP[kind]}\n{wr}wrdata {o}.{ana} {save} ex\n'
    return f"""* slot-7 round trip, slot view {view}, {ana} {load}, {c} {t} C, {v} V (verification/c2_gaps/slot_pex/sim.py)
.lib cornerMOShv.lib mos_{c}
.lib cornerMOSlv.lib mos_{c}
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerPNP.lib typ
.include {PDK}/libs.tech/ngspice/models/diodes.lib
.include sg13cmos5l_io.spice
""" + ''.join(f'.include {i}\n' for i in includes(view, rdir)) + f""".temp {t}
{opt}
Vslot vdd_3v3 0 {sup}
Vio iovdd 0 {sup}
Ven enable 0 {ven}
Vin padin 0 {vin}
Rout padout 0 1G
RL padout vterm {rl}
CL padout 0 {cl}
Et vterm 0 vref_d2s 0 1
""" + ''.join(f'Vd{i} d{i} 0 {bits[i]}\n' for i in range(6)) + bus + ('Vpi0 iref0s iref0 0\nVpi1 iref1s iref1 0\n' if ana == 'opi' else '') + f"""XS vdd_3v3 0 enable d0 d1 d2 d3 d4 d5 b0 b1 b2 b3 vref_s2d outp outn vcm_s2d en0 enb0 {'iref0s' if ana == 'opi' else 'iref0'} vinp vinn vref_d2s {'iref1s' if ana == 'opi' else 'iref1'} enb1 en1 do0 do1 do2 do3 do4 do5 do6 do7 do8 do9 do10 do11 v12 0 slot_7
Vv12 v12 0 1.2
X2S iovdd 0 iovdd 0 padin outp outn vcm_s2d vref_s2d iref0 en0 enb0 sg13cmos5l_IOPadSingle2Diff
X2D iovdd 0 iovdd 0 padout vinp vinn vref_d2s iref1 en1 enb1 sg13cmos5l_IOPadDiff2Single
.control
save {save} v(enable){' i(vpi0) i(vpi1) v(iref0) v(iref1)' if ana == 'opi' else ''}
{ctl}echo "SLOTDONE"
.endc
.end
"""


def suffixes(ana):
    return {'op': ['op', 'opoff'], 'ac': ['ac_open', 'ac_10p', 'ac_100p']}.get(ana, [ana])


def run(job):
    p = job.split(':')
    view, c, t, v, ana = p[0], p[1], int(p[2]), float(p[3]), p[4]
    load = p[5] if len(p) > 5 else 'open'
    tag = f'{view}_{c}_{t}_{v}_{ana}' + (f'_{load}' if ana == 'step' else '')
    rdir = RUNS / tag
    rdir.mkdir(parents=True, exist_ok=True)
    for s in suffixes(ana):
        (OUT / f'{tag}.{s}').unlink(missing_ok=True)
    f = rdir / f'{tag}.spice'
    f.write_text(deck(view, c, t, v, ana, load, rdir, tag))
    (rdir / '.spiceinit').write_text((Path(PDK) / 'libs.tech' / 'ngspice' / '.spiceinit').read_text())
    deck0 = f.read_text()
    m = re.search(r'^\.option .*$', deck0, re.M)
    # convergence aids, tried in this order only after a failed run (recorded in <tag>.aid and the log):
    #   1. ngspice's default solver SPARSE 1.3 instead of KLU (the disabled op of prev converges only with SPARSE)
    #   2. SPARSE plus more gmin / source steps and iterations (gminsteps=100 srcsteps=100 itl1=1000 itl6=1000)
    aids = [('', m.group(0))]
    if 'klu' in m.group(0):
        aids.append(('SPARSE instead of KLU', m.group(0).replace(' klu', '')))
    aids.append(('SPARSE, gminsteps=100 srcsteps=100 itl1=1000 itl6=1000',
                 m.group(0).replace(' klu', '') + ' gminsteps=100 srcsteps=100 itl1=1000 itl6=1000'))
    #   3. (dc only) as 2, the sweep split at pad in 0.5 V (0.5 -> 3.3 V and 0.5 -> -0.3 V), so that the first
    #      operating point is the one the ac runs find; both halves are joined into <tag>.dc
    split = ''
    if ana == 'dc':
        sw = re.search(r'^dc Vin -0\.3 3\.3 0\.005\n.*?wrdata (\S+) ([^\n]*)$', deck0, re.M | re.S)
        split = (f'dc Vin 0.5 3.3 0.005\nset wr_singlescale\nset wr_vecnames\noption numdgt=9\n'
                 f'wrdata {sw.group(1)}_up {sw.group(2)}\ndc Vin 0.5 -0.3 -0.005\nwrdata {sw.group(1)}_dn {sw.group(2)}')
        aids.append(('SPARSE, more steps, sweep split at 0.5 V', aids[-1][1]))
    env = dict(os.environ, OMP_NUM_THREADS='1')  # one thread: the CPUs are shared with other jobs
    # s per attempt; a stalled run is stopped and counts as failed (then the next aid is tried)
    tmo = float(os.environ.get('SIM_TIMEOUT', '2400' if ana in ('step', 'pu', 'en') else '900'))
    if os.environ.get('SIM_NO_AIDS') or ana == 'pu':
        aids = aids[:1]  # power-up from 0 V: one attempt only (long)
    (OUT / f'{tag}.aid').unlink(missing_ok=True)
    log, t00 = '', time.time()
    for k, (what, line) in enumerate(aids):
        dk = deck0.replace(m.group(0), line, 1)
        if what.endswith('sweep split at 0.5 V'):
            dk = dk.replace(sw.group(0), split, 1)
        f.write_text(dk)
        t0 = time.time()
        try:
            pr = subprocess.run(['ngspice', '-b', f.name], cwd=rdir, capture_output=True, text=True, env=env,
                                timeout=tmo)
        except subprocess.TimeoutExpired as e:
            pr = subprocess.CompletedProcess(e.cmd, -9, (e.stdout or b'').decode(errors='replace') if isinstance(
                e.stdout, bytes) else (e.stdout or ''), f'TIMEOUT after {tmo:.0f} s (SIM_TIMEOUT)')
        dt = time.time() - t0
        up, dn = OUT / f'{tag}.dc_up', OUT / f'{tag}.dc_dn'
        if up.exists() and dn.exists():  # join the split sweep: down half reversed (without 0.5 V), then up half
            lu, ld = up.read_text().splitlines(), dn.read_text().splitlines()
            (OUT / f'{tag}.dc').write_text('\n'.join([lu[0]] + ld[:0:-1][:-1] + lu[1:]) + '\n')
            up.unlink()
            dn.unlink()
        log += (f'\n=== attempt {k + 1}: {what or "as written"} ({line})\n' + pr.stdout[-20000:] +
                '\n--- stderr ---\n' + pr.stderr[-15000:] + f'\n--- wall time {dt:.1f} s\n')
        ok = 'SLOTDONE' in pr.stdout and all((OUT / f'{tag}.{s}').exists() for s in suffixes(ana)) and \
            'aborted' not in (pr.stdout + pr.stderr)
        if ok:
            if k:
                (OUT / f'{tag}.aid').write_text(what + '\n')
            break
        for s in suffixes(ana):
            (OUT / f'{tag}.{s}').unlink(missing_ok=True) if k + 1 < len(aids) else None
    (OUT / f'{tag}.log').write_text(log + ('\nSLOTDONE (final attempt ok)\n' if ok else '\nFINAL: FAILED\n'))
    print(tag, 'ok' if ok else 'FAILED', f'{time.time() - t00:.0f} s', f'(aid: {what})' if ok and what else '',
          flush=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    OUT.mkdir(parents=True, exist_ok=True)
    for j in sys.argv[2:]:
        run(j)
