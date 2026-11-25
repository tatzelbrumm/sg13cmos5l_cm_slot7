#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Terminal voltages of every MOS device of slot 7 and its two custom pads (IHP sg13cmos5l simulation, ngspice).

Usage: python3 -I vs.py <work_dir> <job> [<job> ...]
  job = <kind>:<mos>:<temp>:<vdd>[:<variant>]        e.g. dc:tt:27:3.3:open, pu:ff:-40:3.6, topo:tt:27:3.3
  kind   topo  flattened netlist (ngspice 'listing e'): every MOS instance with its four terminal nodes -> topo.csv
         dc    default mode, enable 1.2 V, DC sweep of the S2D pad source -0.2 ... max(3.3, vdd) V in 50 mV steps;
               variant open (D2S pad 1 Gohm only) | 1k (1 kOhm from the D2S pad to vterm = v(vref_d2s), as
               ../ac_tran; 100 pF is irrelevant at DC) | 1kgnd (1 kOhm from the D2S pad to ground)
         off   disabled state, quasi-static (transient, as run_tier1.py's disabled point): from the enabled operating
               point (pad 0.5 V), enable 1.2 -> 0 V at 1 us; then the S2D pad source ramps 0.5 -> -0.2 V (20 ... 30 us),
               -0.2 V -> max(3.3, vdd) (30 ... 60 us), back to 0.5 V (70 us); D2S pad 1 Gohm. (A DC sweep of the
               disabled state does not converge: gmin / source stepping and the transient op fail at pad -0.2 V.)
         fs    fail-safe, slot vdd_3v3 = 0 and vdd_1v2 = 0, enable 0, pad ring iovdd = <vdd>; both pads driven from
               one source swept 0 ... <vdd>, each through 1 kOhm
         fst   fs as a transient (for the -40 C points, where the fs DC sweep aborts in the S2D pad diode): from all
               nodes at 0 V (uic), iovdd 0 -> V in 1 us, the pad source 0 V until 2 us, then 0 -> V at 52 us
         fs0   fail-safe, all supplies 0 V (vdd_3v3 = iovdd = vdd_1v2 = 0, enable 0), both pads driven as fs
         pu    power-up transient: vdd_3v3, iovdd (and vdd_1v2 to 1.2 V) ramp 0 -> V in 10 us (from all nodes at 0 V,
               uic; two slopes, 0 -> 0.3 V in 0.4 us, then to V at 10 us: with one linear slope the time step of ngspice
               collapses at about 0.15 V, tt 27 C 3.6 V, and the run does not advance past 409.5 ns in 500 s), enable already 1.2 V from t = 0 (the harness's 1.2 V logic is up first), S2D pad 0.5 V, end 30 us
               variant fast: ramp in 1 us, end 20 us
               variant late: as ../slot_modes_bg: enable 0 during the ramp, 0 -> 1.2 V at 20 us (100 ns edge), end
               40 us
         en    enable edges at V: from the enabled operating point, enable 1.2 -> 0 V at 2 us, 0 -> 1.2 V at 22 us
               (10 ns edges), end 42 us; S2D pad 0.5 V
         step  full-swing S2D pad steps from the enabled operating point (pad 0 V): 0 -> V at 2 us, V -> -0.2 V at
               12 us, -0.2 -> 0.5 V at 22 us (10 ns edges), end 32 us; variant open | 100p (1 kOhm to vterm + 100 pF)
         (transients: variant chk_<aid> = solver check, the same deck with only that setting: chk_step2n,
         chk_step05n, chk_step01n = maximum time step 2 / 0.5 / 0.1 ns, chk_trap = trapezoidal, chk_nocshunt,
         chk_nqs = rfmode=1, the PDK's non-quasi-static model card, on bg_core_pd and ls_up_fs; chk_nqsbg = the same
         on bg_core_pd only)
         mode  mode switching at V (mode bits through the key, 10 ns edges): default, swap at 2 us, mon 12 us,
               feed 22 us, ext 32 us, all_high 42 us, default 52 us, end 62 us; analog_bus0/1 driven (10 kOhm to 1.45 /
               1.05 V) during feed, analog_bus2/3 (10 kOhm to 1.30 / 0.50 V) during ext (voltage-controlled switches,
               as ../slot_modes_bg); S2D pad 0.5 V
Writes <work_dir>/dev/<tag>.csv.gz (per MOS instance: max |VGS|, |VGD|, |VDS|, |VGB|, |VSB|, |VDB| and where; the
largest |VGS|, |VGD|, |VDS| held for at least 100 ns; time with |VGS| or |VGD| above 3.3 V),
<work_dir>/nodes/<tag>.csv.gz (max / min of every node), <work_dir>/log/<tag>.log; the raw file is deleted after
evaluation unless KEEP_RAW=1.

Deck: the designer's tier-1 slot deck (design repository commit 9052bd35, docs/slot7_hookup/tier1/run_tier1.py,
imported) as ../ac_tran/slot.py builds it for the KLayout view: slot_7 source netlist (s7_ctrl glue logic, s7_doutpd,
ls_up_fs, hv_logic), bg_core_pd schematic, pad_ref_rb, bias_dist_pd and both custom pads KLayout-extracted (converted
by run_tier1.wrapped()), the pads' antenna diodes given their extracted size by ../klayout_pad_diodes/fix_diodes.py
(and the KLayout instance names X$<n> written X_<n>, so that they can be named in ngspice's .control section).
vdd_3v3 = iovdd = <vdd>; pads' vdd / vss pins on iovdd / 0 (as run_tier1.py; the extracted pads have no separate
core-supply pins). .option gmin=1e-12 as the designer. If a DC sweep fails, it is rerun once with rshunt=1e12 (1 Tohm
from every node to ground, solver aid as ../ac_tran); transients use method=gear cshunt=1e-15 (as run_tier1.py's own
transient) and a 10 ns maximum time step (as ../slot_modes_bg); a failed transient is rerun with a 2 ns maximum
step, and if that fails too, with a 0.5 ns maximum step. Aids are recorded in the log and in the dev CSV header.
"""
import gzip
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'klayout_pad_diodes'))
import fix_diodes  # noqa: E402
import rawread  # noqa: E402

WORK = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
PDK = '/foss/pdks/ihp-sg13cmos5l'
PADS = ['sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single']
MODES = {'default': '000000', 'swap': '100100', 'mon': '010100', 'feed': '001100', 'ext': '000101',
         'all_high': '111111'}  # d0 ... d5, as ../slot_modes_bg/slot_modes.py MODES
VLIM = 3.3           # V, the spec's VGS maximum (for the over33 column)
HOLD_DT, HOLD_N = 10e-9, 11   # 'held' values: >= 100 ns on a 10 ns grid
TRAN = ('pu', 'en', 'step', 'mode', 'off', 'fst')
TMO_DC = int(os.environ.get('VS_TMO_DC', '240'))      # s per ngspice run (a stalled DC sweep is killed)
TMO_TRAN = int(os.environ.get('VS_TMO_TRAN', '1800'))
TMO_PU = int(os.environ.get('VS_TMO_PU', '150'))
MODESEQ = [('default', 0), ('swap', 2), ('mon', 12), ('feed', 22), ('ext', 32), ('all_high', 42), ('default', 52)]


def tier1():
    t1 = WORK / 'tier1' / 'docs' / 'slot7_hookup' / 'tier1'
    sys.path.insert(0, str(t1))
    import run_tier1 as T
    return T


def includes(T, rdir):
    """Converted, port-wrapped KLayout netlists (run_tier1.wrapped()) with the diode-size fix applied."""
    rdir.mkdir(parents=True, exist_ok=True)
    T.RUNS = rdir
    out = []
    for c in T.SRC_PORTS:
        name = T.wrapped(c)
        fix_diodes.fix_file(rdir / name)
        # KLayout instance names X$<n> -> X_<n>: '$' would be expanded as a variable in the .control 'save' lines
        f = rdir / name
        f.write_text(re.sub(r'^X\$', 'X_', f.read_text(), flags=re.M))
        out.append(str(f))
    return out


def pwl(pts):
    return 'pwl(' + ' '.join(f'{t:.9g} {v:.6g}' for t, v in pts) + ')'


def deck(T, kind, c, t, v, var, rdir, tag, aid):
    mac = WORK / 'tier1' / 'macros'
    bg = mac / 'bg_core_pd' / 'netlist' / 'schematic' / 'bg_core_pd_magic.spice'
    vmax = max(3.3, v)
    tran = kind in TRAN
    topt = {'trap': ' method=trap cshunt=1e-15', 'nocshunt': ' method=gear'}.get(aid, ' method=gear cshunt=1e-15')
    opt = '.option gmin=1e-12' + (topt if tran else '') + (' rshunt=1e12' if aid == 'rshunt' else '')
    tmax = {'step2n': '2n', 'step05n': '0.5n', 'step01n': '0.1n'}.get(aid, '10n')

    def inc(path):
        """aid 'nqs' (model check only): copies of bg_core_pd and en_ctrl_3v3 (ls_up_fs), the two netlists with the
        long-channel series stacks, with rfmode=1 on every sg13_hv_* instance, i.e. the PDK's NQS model card
        (pspnqs103va, swnqs = 5) instead of the quasi-static one. (rfmode=1 on every MOS of the deck: the transient
        operating point fails, 'timestep too small' at the initial time point in the S2D pad diode x_63.)"""
        path = Path(path)
        if aid not in ('nqs', 'nqsbg') or path.name not in (('bg_core_pd_magic.spice',) if aid == 'nqsbg' else
                                                          ('bg_core_pd_magic.spice', 'en_ctrl_3v3.spice')):
            return path
        txt = re.sub(r'^(X\S*\s.*\bsg13_hv_[np]mos\b.*)$', r'\1 rfmode=1', path.read_text(), flags=re.M | re.I)
        rdir.mkdir(parents=True, exist_ok=True)
        dst = rdir / f'nqs_{path.name}'
        dst.write_text(txt)
        return dst
    # sources (defaults: enabled default mode, supplies at v)
    src = dict(vslot=f'{v}', vio=f'{v}', ven='1.2', v12='1.2', vin='0.5', bits={i: '0' for i in range(6)})
    rl, cl, rsrc, drive_d2s, bus = '1e12', '1e-18', '0', False, ''
    if kind == 'dc' and var == '1k':
        rl = '1k'
    if kind == 'off':
        src['ven'] = pwl([(0, 1.2), (1e-6, 1.2), (1.01e-6, 0)])
        src['vin'] = pwl([(0, 0.5), (20e-6, 0.5), (30e-6, -0.2), (60e-6, vmax), (70e-6, 0.5)])
    if kind in ('fs', 'fs0', 'fst'):
        src.update(vslot='0', v12='0', ven='0')
        if kind == 'fs0':
            src['vio'] = '0'
        if kind == 'fst':
            src['vio'] = pwl([(0, 0), (1e-6, v)])
            src['vin'] = pwl([(0, 0), (2e-6, 0), (52e-6, v)])
        rsrc, drive_d2s = '1k', True
    if kind == 'pu':
        if var == 'fast':
            src['vslot'] = src['vio'] = pwl([(0, 0), (1e-6, v)])
            src['v12'] = pwl([(0, 0), (1e-6, 1.2)])
        else:   # two slopes: a linear 0 -> V in 10 us stalls ngspice at about 0.15 V (tt 27 C 3.6 V: at 409.5 ns)
            src['vslot'] = src['vio'] = pwl([(0, 0), (0.4e-6, 0.3), (10e-6, v)])
            src['v12'] = pwl([(0, 0), (0.4e-6, 0.1), (10e-6, 1.2)])
        src['ven'] = pwl([(0, 0), (20e-6, 0), (20.1e-6, 1.2)]) if var == 'late' else '1.2'
    if kind == 'en':
        src['ven'] = pwl([(0, 1.2), (2e-6, 1.2), (2.01e-6, 0), (22e-6, 0), (22.01e-6, 1.2)])
    if kind == 'step':
        src['vin'] = pwl([(0, 0), (2e-6, 0), (2.01e-6, v), (12e-6, v), (12.01e-6, -0.2), (22e-6, -0.2),
                          (22.01e-6, 0.5)])
        if var == '100p':
            rl, cl = '1k', '100p'
    if kind == 'mode':
        for i in range(6):
            pts, last = [], '0'
            for name, ts in MODESEQ:
                b = MODES[name][i]
                if ts == 0:
                    pts.append((0, float(b) * 1.2))
                elif b != last:
                    pts += [(ts * 1e-6, float(last) * 1.2), (ts * 1e-6 + 10e-9, float(b) * 1.2)]
                last = b
            src['bits'][i] = pwl(pts) if len(pts) > 1 else f'{pts[0][1]:.6g}'
        # analog buses: driven only during feed (bus0/1) and ext (bus2/3), through voltage-controlled switches
        bus = f""".model swb sw vt=0.6 vh=0.1 ron=10k roff=1e9
Vcf cf 0 {pwl([(0, 0), (22e-6, 0), (22.01e-6, 1.2), (32e-6, 1.2), (32.01e-6, 0)])}
Vcx cx 0 {pwl([(0, 0), (32e-6, 0), (32.01e-6, 1.2), (42e-6, 1.2), (42.01e-6, 0)])}
Vb0 b0s 0 1.45
Vb1 b1s 0 1.05
Vb2 b2s 0 1.30
Vb3 b3s 0 0.50
S0 b0s b0 cf 0 swb
S1 b1s b1 cf 0 swb
S2 b2s b2 cx 0 swb
S3 b3s b3 cx 0 swb
"""
    if kind == 'dc' and var == '1kgnd':
        rl = '1k'
    vterm = '0' if (kind == 'dc' and var == '1kgnd') else 'vref_d2s'
    if kind in ('dc', 'topo'):
        ana = f'dc Vin -0.2 {vmax:.6g} 0.05'
    elif kind in ('fs', 'fs0'):
        ana = f'dc Vin 0 {v:.6g} 0.05'
    elif kind == 'pu':
        ana = f'tran 10n {"20u" if var == "fast" else ("40u" if var == "late" else "30u")} 0 {tmax} uic'
    elif kind == 'en':
        ana = f'tran 10n 42u 0 {tmax}'
    elif kind == 'off':
        ana = f'tran 10n 70u 0 {tmax}'
    elif kind == 'fst':
        ana = f'tran 10n 52u 0 {tmax} uic'
    elif kind == 'step':
        ana = f'tran 10n 32u 0 {tmax}'
    elif kind == 'mode':
        ana = f'tran 10n 62u 0 {tmax}'
    else:
        raise ValueError(kind)
    if drive_d2s:
        d2sdrv = f'Epo padout_s 0 padin_s 0 1\nRpo padout_s padout {rsrc}\n'
    else:
        d2sdrv = ''
    vin_line = (f'Vin padin_s 0 {src["vin"]}\nRin padin_s padin {rsrc}\n' if rsrc != '0'
                else f'Vin padin 0 {src["vin"]}\n')
    ctrl = ('listing e\n' if kind == 'topo' else '') + save_lines() + f"""set filetype=binary
{ana}
write {tag}.raw
echo "VSDONE"
"""
    return f"""* slot-7 voltage stress: {kind} {var}, pads KLayout-extracted (diodes fixed), {c} {t} C, {v} V
.lib cornerMOShv.lib mos_{c}
.lib cornerMOSlv.lib mos_{c}
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.lib cornerPNP.lib typ
.include {PDK}/libs.tech/ngspice/models/diodes.lib
.include {inc(mac / 'hv_logic' / 'netlist' / 'source' / 'hv_logic.spice')}
.include {inc(mac / 'en_ctrl_3v3' / 'netlist' / 'source' / 'en_ctrl_3v3.spice')}
.include {inc(bg)}
""" + ''.join(f'.include {inc(i)}\n' for i in includes(T, rdir)) + f""".include {inc(mac / 'slot_7' / 'netlist' / 'source' / 'slot_7.spice')}
.temp {t}
{opt}
Vslot vdd_3v3 0 {src['vslot']}
Vio iovdd 0 {src['vio']}
Ven enable 0 {src['ven']}
Vv12 v12 0 {src['v12']}
""" + ''.join(f'Vd{i} d{i} 0 {src["bits"][i]}\n' for i in range(6)) + vin_line + d2sdrv + f"""Rout padout 0 1G
RL padout vterm {rl}
CL padout 0 {cl}
Et vterm 0 {vterm} 0 1
""" + (bus if bus else ''.join(f'Rb{i} b{i} 0 1G\n' for i in range(4))) + f"""XS vdd_3v3 0 enable d0 d1 d2 d3 d4 d5 b0 b1 b2 b3 vref_s2d outp outn vcm_s2d en0 enb0 iref0 vinp vinn vref_d2s iref1 enb1 en1 do0 do1 do2 do3 do4 do5 do6 do7 do8 do9 do10 do11 v12 0 slot_7
""" + ''.join(f'Rdo{i} do{i} 0 1G\n' for i in range(12)) + f"""X2S iovdd 0 iovdd 0 padin outp outn vcm_s2d vref_s2d iref0 en0 enb0 sg13cmos5l_IOPadSingle2Diff
X2D iovdd 0 iovdd 0 padout vinp vinn vref_d2s iref1 en1 enb1 sg13cmos5l_IOPadDiff2Single
.control
{ctrl}.endc
.end
"""


def save_lines():
    """'save' of the MOS terminal nodes only (from topo.csv; without it, i.e. in the topo run, ngspice keeps every node
    including the OSDI devices' internal nodes) plus the testbench nodes."""
    if not topo_csv().exists():
        return ''
    nodes = set()
    for r in load_topo():
        nodes |= {r['d'], r['g'], r['s'], r['b']}
    nodes = sorted(nodes - {'0'}) + ['padin', 'padout', 'iovdd', 'vdd_3v3', 'enable', 'vterm', 'v12']
    nodes = list(dict.fromkeys(nodes))
    return ''.join('save ' + ' '.join(f'v({n})' for n in nodes[i:i + 20]) + '\n' for i in range(0, len(nodes), 20))


def parse_listing(text):
    """MOS instances (N... devices of the PDK subckts sg13_hv_nmos / sg13_hv_pmos / sg13_lv_*) from 'listing e'."""
    rows = []
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r'^\d+\s*:\s*(n\S*\.n(sg13_\w+))\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s*(.*)$', s, re.I)
        if not m:
            continue
        inst, kind, d, g, src, b, model, prm = m.groups()
        p = dict(re.findall(r'(\w+)\s*=\s*(\S+)', prm))
        rows.append(dict(inst=inst.lower(), dev=kind.lower(), model=model.lower(), d=d.lower(), g=g.lower(),
                         s=src.lower(), b=b.lower(), w=p.get('w', ''), l=p.get('l', ''), nf=p.get('nf', ''),
                         mult=p.get('mult', '')))
    return rows


def topo_csv():
    return WORK / 'topo.csv'


def load_topo():
    import csv
    with open(topo_csv()) as f:
        return list(csv.DictReader(f))


def evaluate(tag, raw, kind, aid):
    """Per-device maxima of the terminal voltages over all points of the run; node extremes."""
    names, x, data = rawread.read(raw)
    idx = {n.lower(): i for i, n in enumerate(names)}
    top = load_topo()
    n = data.shape[0]

    def col(node):
        if node == '0' or node == 'gnd':
            return np.zeros(n)
        k = idx.get(node, idx.get(f'v({node})'))
        if k is None:
            raise KeyError(node)
        return data[:, k]

    xs = np.asarray(x)
    tran = kind in TRAN
    if tran:   # uniform 10 ns grid for the 'held for >= 100 ns' values (sliding minimum over 11 samples)
        tg = np.arange(xs[0], xs[-1], HOLD_DT)
        dt = np.gradient(xs)

    def held(a):
        if not tran:
            return float(a.max())
        ag = np.interp(tg, xs, a)
        return float(np.lib.stride_tricks.sliding_window_view(ag, HOLD_N).min(axis=1).max())

    lines = []
    for r in top:
        vd, vg, vs, vb = col(r['d']), col(r['g']), col(r['s']), col(r['b'])
        pmos = 'pmos' in r['dev']
        # electrical source: the lower of the two diffusion terminals (NMOS), the higher (PMOS)
        lo, hi = np.minimum(vd, vs), np.maximum(vd, vs)
        se, de = (hi, lo) if pmos else (lo, hi)
        q = {'vgs': vg - se, 'vgd': vg - de, 'vds': hi - lo, 'vgb': vg - vb, 'vsb': se - vb, 'vdb': de - vb}
        out = [r['inst']]
        for k in ('vgs', 'vgd', 'vds', 'vgb', 'vsb', 'vdb'):
            a = np.abs(q[k])
            j = int(np.argmax(a))
            out += [f'{q[k][j]:.5g}', f'{xs[j]:.6g}']
        mg = np.maximum(np.abs(q['vgs']), np.abs(q['vgd']))
        out += [f"{held(np.abs(q['vgs'])):.5g}", f"{held(np.abs(q['vgd'])):.5g}", f"{held(np.abs(q['vds'])):.5g}",
                f'{float(dt[mg > VLIM].sum()) if tran else int((mg > VLIM).sum()):.4g}']
        lines.append(','.join(out))
    hdr = (f'# {tag}: kind {kind}, aid {aid or "none"}, {n} points; per value: signed value at max |.|, sweep value '
           f'[V] or time [s] there; *_held = largest |.| held for at least 100 ns (transients; DC: = max |.|); '
           f'over33 = time [s] (transients) or number of sweep points (DC) with |VGS| or |VGD| > 3.3 V\n'
           f'inst,vgs,x_vgs,vgd,x_vgd,vds,x_vds,vgb,x_vgb,vsb,x_vsb,vdb,x_vdb,vgs_held,vgd_held,vds_held,over33\n')
    (WORK / 'dev').mkdir(exist_ok=True)
    with gzip.open(WORK / 'dev' / f'{tag}.csv.gz', 'wt') as f:
        f.write(hdr + '\n'.join(lines) + '\n')
    nl = []
    for nm, i in idx.items():
        if nm.endswith('#branch') or i == 0 and nm in ('time', 'v-sweep'):
            continue
        a = data[:, i]
        nl.append(f'{nm},{a.max():.5g},{xs[int(a.argmax())]:.6g},{a.min():.5g},{xs[int(a.argmin())]:.6g}')
    (WORK / 'nodes').mkdir(exist_ok=True)
    with gzip.open(WORK / 'nodes' / f'{tag}.csv.gz', 'wt') as f:
        f.write(f'# {tag}\nnode,vmax,x_vmax,vmin,x_vmin\n' + '\n'.join(nl) + '\n')


def run(T, job):
    p = job.split(':')
    kind, c, t, v = p[0], p[1], int(p[2]), float(p[3])
    var = p[4] if len(p) > 4 else ''
    tag = f'{kind}_{c}_{t}_{v}' + (f'_{var}' if var else '')
    rdir = WORK / 'runs' / tag
    (WORK / 'log').mkdir(parents=True, exist_ok=True)
    spiceinit = Path(PDK) / 'libs.tech' / 'ngspice' / '.spiceinit'
    log = ''
    # disabled / unpowered states have nodes held only by leakage: their DC sweep goes straight to the solver aid
    if var.startswith('chk_'):
        # solver check of a transient (analyze.py keeps these out of the stress tables): only the given setting,
        # step2n / step05n / step01n (maximum time step 2 / 0.5 / 0.1 ns), trap (trapezoidal integration), nocshunt
        tries = [var[4:]]
    elif kind in ('fs', 'fs0'):
        tries = ['rshunt']
    else:
        tries = [''] + (['rshunt'] if kind in ('dc', 'topo') else ['step2n', 'step05n'])
    ok, aid = False, ''
    for aid in tries:
        d = deck(T, kind, c, t, v, var, rdir, tag, aid)
        (rdir / '.spiceinit').write_text(spiceinit.read_text())
        f = rdir / f'{tag}.spice'
        f.write_text(d)
        raw = rdir / f'{tag}.raw'
        raw.unlink(missing_ok=True)
        tmo = TMO_TRAN if kind in TRAN else TMO_DC
        if kind == 'pu' and var != 'fast':
            tmo = min(tmo, TMO_PU)   # the 10 us ramps take 20 ... 60 s where they run; a stalled one is cut short
        try:
            pr = subprocess.run(['ngspice', '-b', f.name], cwd=rdir, capture_output=True, text=True, timeout=tmo)
        except subprocess.TimeoutExpired as e:
            so = e.stdout.decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
            pr = subprocess.CompletedProcess(e.cmd, -9, so, f'TIMEOUT after {tmo} s (killed)')
        out = pr.stdout + '\n--- stderr ---\n' + pr.stderr
        log += f'=== aid: {aid or "none"} ===\n' + (out if kind == 'topo' else out[-30000:]) + '\n'
        ok = 'VSDONE' in pr.stdout and raw.exists() and not re.search(r'aborted|simulation\(s\) aborted',
                                                                      pr.stdout + pr.stderr)
        if kind == 'topo':
            import csv
            rows = parse_listing(pr.stdout)
            with open(topo_csv(), 'w', newline='') as fo:
                w = csv.DictWriter(fo, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
            print(f'topo: {len(rows)} MOS instances -> {topo_csv()}', flush=True)
        if ok:
            break
    (WORK / 'log' / f'{tag}.log').write_text(log)
    if ok:
        evaluate(tag, raw, kind, aid)
        if os.environ.get('KEEP_RAW') != '1':
            raw.unlink()
    print(tag, 'ok' if ok else 'FAILED', f'(aid {aid})' if ok and aid else '', flush=True)
    return ok


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    T = tier1()
    for j in sys.argv[2:]:
        run(T, j)
