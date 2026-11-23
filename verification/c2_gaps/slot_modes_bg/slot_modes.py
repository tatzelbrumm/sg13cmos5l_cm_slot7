# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Slot 7 modes from power-up (IHP sg13cmos5l simulation): transient power-up, enable, mode bits, pad-in staircase.

usage: python3 -I slot_modes.py <design-repo-tree> <work-dir> <out-dir> <job> [<job> ...]
  job = <mode>:<mos>:<temp>:<vdd>[:<variant>]   e.g. swap:ss:-40:3.0
  variant: "pu" (default; power-up transient, see below), "dcop" (the designer's DC sweep as in run_modes.py, stderr kept),
           "dcns" (dcop plus .nodeset of the bandgap nodes g / vpc / vpg / ks / ibg at their running values: diagnosis)

Same netlists and testbench as the designer's docs/slot7_hookup/tier1/run_modes.py at the design-repo commit (it is
imported from there, via run_tier1.wrapped(), so the decks use the same views): both custom pads, pad_ref_rb and
bias_dist_pd from their extracted layout netlists; bg_core_pd from its schematic netlist; ls_up_fs / s7_ctrl / hv_logic
/ en_ctrl_3v3 from their source netlists. MOS corner on hv and lv, res_typ, pnp typ.

"pu": vdd_3v3 and iovdd ramp 0 -> V in 10 us; v12 (1.2 V) and the mode bits d0..d5 are there from t = 0 (the harness
writes the register before enabling), enable 0 -> 1.2 V at 20 us (100 ns edge). Pad in 0.5 V until 40 us (values
"at 39 us" = settled with pad in 0.5 V), then a staircase 0 / 0.25 / 0.5 / 0.75 / 1.0 V (10 us each, 40 ... 90 us,
sampled at each step's end; settle = pad-out change between 85 and 90 us). Feed modes: bus0 / bus1 through 10 kohm to 1.45 /
1.05 V (as run_modes.py), pad in fixed at 0.5 V. ext: bus2 / bus3 through 10 kohm to 1.30 / 0.50 V. Error =
pad out - expected at the end of each step (expected as in run_modes.py). No .nodeset / .ic: plain transient with uic
from all-zero (every node starts at 0 V), i.e. no circuit change and no forced state. Integration options as the
designer's own transient in run_tier1.py (method=gear cshunt=1e-15: 1 fF from every node to ground) and a 10 ns
maximum time step: solver aids only. Without the step limit the run aborts with "timestep too small" in the D2S pad's
antenna diode X$3 (dpantenna, pad - iovdd): at 5.9 us (trapezoidal, no cshunt), 21.3 us (gear + cshunt), 6.6 us
(gear + cshunt + rshunt=1e12 itl4=100 chgtol=1e-16; default mode); README.
"""
import csv
import re
import subprocess
import sys
from pathlib import Path

TREE, WORK, OUT = (Path(a).resolve() for a in sys.argv[1:4])
JOBS = sys.argv[4:]
T1 = TREE / "docs" / "slot7_hookup" / "tier1"
sys.path.insert(0, str(T1))
import run_tier1 as T  # noqa: E402

MODES = {"default": ("0 0 0 0 0 0", "direct"), "swap": ("1 0 0 1 0 0", "crossed"), "mon": ("0 1 0 1 0 0", "direct"),
         "feed": ("0 0 1 1 0 0", "feed"), "ext": ("0 0 0 1 0 1", "ext"), "all_high": ("1 1 1 1 1 1", "direct"),
         "swap+feed": ("1 0 1 1 0 0", "feed"), "no_key_swap": ("1 0 0 0 0 0", "direct")}
EXP = {"direct": "v(vcm_s2d) + v(padin) - v(vref_s2d)", "crossed": "v(vcm_s2d) - v(padin) + v(vref_s2d)",
       "feed": "v(vcm_s2d) + (v(b0) - v(b1))/2", "ext": "1.30 + v(padin) - 0.50"}
STEPS = [(0.0, 50e-6), (0.25, 60e-6), (0.5, 70e-6), (0.75, 80e-6), (1.0, 90e-6)]  # (pad in, sample time)
TOPT = " method=gear cshunt=1e-15"
NS_ON = ".nodeset v(xs.xbg.g)=1.77 v(xs.xbg.vpc)=1.12 v(xs.xbg.vpg)=2.22 v(xs.xbg.ks)=0 v(xs.ibg)=1.0"


def header(c, t, v, incs, TOPT=""):
    return f""".lib cornerMOShv.lib mos_{c}
.lib cornerMOSlv.lib mos_{c}
.lib cornerRES.lib res_typ
.lib cornerPNP.lib typ
.include /foss/pdks/ihp-sg13cmos5l/libs.tech/ngspice/models/diodes.lib
.include {T.MAC}/hv_logic/netlist/source/hv_logic.spice
.include {T.MAC}/en_ctrl_3v3/netlist/source/en_ctrl_3v3.spice
.include {T.MAC}/bg_core_pd/netlist/schematic/bg_core_pd_magic.spice
""" + "".join(f".include {i}\n" for i in incs) + f""".include {T.MAC}/slot_7/netlist/source/slot_7.spice
.temp {t}
.option gmin=1e-12{TOPT}
"""


DUT = """XS vdd_3v3 0 enable d0 d1 d2 d3 d4 d5 b0 b1 b2 b3 vref_s2d outp outn vcm_s2d en0 enb0 iref0 vinp vinn vref_d2s iref1 \
enb1 en1 do0 do1 do2 do3 do4 do5 do6 do7 do8 do9 do10 do11 v12 0 slot_7
X2S iovdd 0 iovdd 0 padin outp outn vcm_s2d vref_s2d iref0 en0 enb0 sg13cmos5l_IOPadSingle2Diff
X2D iovdd 0 iovdd 0 padout vinp vinn vref_d2s iref1 en1 enb1 sg13cmos5l_IOPadDiff2Single
Rout padout 0 1G
"""
BG = "v(xs.xbg.g) v(xs.xbg.vpc) v(xs.xbg.vpg) v(xs.xbg.ks) v(xs.ibg)"


def deck_pu(name, c, t, v, incs):
    bits, kind = MODES[name]
    d = [float(b) * 1.2 for b in bits.split()]
    feed, ext = kind == "feed", kind == "ext"
    pin = "0.5" if feed else ("pwl(0 0.5 40u 0.5 40.1u 0 50u 0 50.1u 0.25 60u 0.25 60.1u 0.5 70u 0.5 70.1u 0.75"
                              " 80u 0.75 80.1u 1.0 90u 1.0)")
    bus = ("Vb0 b0s 0 1.45\nVb1 b1s 0 1.05\nRb0 b0s b0 10k\nRb1 b1s b1 10k" if feed else "Rb0 b0 0 1G\nRb1 b1 0 1G")
    bus += "\n" + ("Vb2 b2s 0 1.30\nVb3 b3s 0 0.50\nRb2 b2s b2 10k\nRb3 b3s b3 10k" if ext else "Rb2 b2 0 1G\nRb3 b3 0 1G")
    meas = "\n".join(f"meas tran e{k} find err at={ts * 1e6:.1f}u\nmeas tran o{k} find v(padout) at={ts * 1e6:.1f}u\n"
                     f"meas tran x{k} find ex at={ts * 1e6:.1f}u" for k, (_, ts) in enumerate(STEPS))
    tag = f"pu_{name}_{c}_{t}_{v}"
    return tag, f"* slot 7 mode {name} from power-up, {c} {t} C, {v} V\n" + header(c, t, v, incs, TOPT) + f"""
Vslot vdd_3v3 0 pwl(0 0 10u {v})
Vio iovdd 0 pwl(0 0 10u {v})
Ven enable 0 pwl(0 0 20u 0 20.1u 1.2)
Vv12 v12 0 1.2
""" + "".join(f"Vd{i} d{i} 0 {d[i]}\n" for i in range(6)) + f"""Vin padin 0 {pin}
{bus}
{DUT}.control
tran 100n 90u 0 10n uic
let ex = {EXP[kind]}
let err = v(padout) - ex
let ibgv = v(xs.ibg)
let islot = -i(Vslot)*1e6
meas tran gfin find v(xs.xbg.g) at=39u
meas tran ibgfin find v(xs.ibg) at=39u
meas tran vcm find v(vcm_s2d) at=39u
meas tran vref find v(vref_s2d) at=39u
meas tran isl find islot at=39u
meas tran tg90 when v(xs.xbg.g)=0.9*gfin cross=1
meas tran tcm when v(vcm_s2d)=0.98*vcm cross=last
{meas}
meas tran o150 find v(padout) at=85u
let dset = abs(o150 - o4)
echo "PU $&gfin $&ibgfin $&vcm $&vref $&isl $&tg90 $&tcm $&dset"
echo "STEPS {' '.join(f'$&e{k} $&o{k} $&x{k}' for k in range(len(STEPS)))}"
linearize
wrdata {tag}.dat {BG} v(vcm_s2d) v(vref_s2d) v(padout) err islot
.endc
.end
"""


def deck_dcop(name, c, t, v, incs, var="dcop"):
    """The designer's DC sweep (run_modes.py deck) unchanged, for the record of how it fails (stderr kept).
    var "dcns": the same plus .nodeset of the bandgap nodes at their running state (diagnosis only)."""
    bits, kind = MODES[name]
    d = [float(b) * 1.2 for b in bits.split()]
    feed, ext = kind == "feed", kind == "ext"
    bus = ("Vb0 b0s 0 1.45\nVb1 b1s 0 1.05\nRb0 b0s b0 10k\nRb1 b1s b1 10k" if feed else "Rb0 b0 0 1G\nRb1 b1 0 1G")
    bus += "\n" + ("Vb2 b2s 0 1.30\nVb3 b3s 0 0.50\nRb2 b2s b2 10k\nRb3 b3s b3 10k" if ext else "Rb2 b2 0 1G\nRb3 b3 0 1G")
    tag = f"{var}_{name}_{c}_{t}_{v}"
    return tag, f"* slot 7 mode {name} DC as run_modes.py, {c} {t} C, {v} V\n" + header(c, t, v, incs) + \
        (NS_ON + "\n" if var == "dcns" else "") + f"""
Vslot vdd_3v3 0 {v}
Vio iovdd 0 {v}
Ven enable 0 1.2
Vv12 v12 0 1.2
""" + "".join(f"Vd{i} d{i} 0 {d[i]}\n" for i in range(6)) + f"""Vin padin 0 0.5
{bus}
{DUT}.control
{"op" if feed else "dc Vin 0 1.0 0.05"}
let err = abs(v(padout) - ({EXP[kind]}))
let emax = maximum(err)
let gg = v(xs.xbg.g)
let gmx = maximum(gg)
echo "DCOP $&emax $&gmx"
.endc
.end
"""


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    T.RUNS = WORK
    incs = [T.wrapped(c) for c in T.SRC_PORTS]
    for job in JOBS:
        p = job.split(":")
        name, c, t, v = p[0], p[1], int(p[2]), float(p[3])
        var = p[4] if len(p) > 4 else "pu"
        tag, deck = deck_pu(name, c, t, v, incs) if var == "pu" else deck_dcop(name, c, t, v, incs, var)
        f = WORK / f"{tag}.spice"
        f.write_text(deck)
        r = subprocess.run(["ngspice", "-b", f.name], cwd=WORK, capture_output=True, text=True)
        f.with_suffix(".log").write_text(r.stdout + "\n#### stderr\n" + r.stderr)
        res = {"mode": name, "mos": c, "temp": t, "vdd": v, "variant": var}
        if var == "pu":
            a = re.search(r"^PU (.*)$", r.stdout, re.M)
            b = re.search(r"^STEPS (.*)$", r.stdout, re.M)
            vals = a.group(1).split() if a else []
            for k, key in enumerate(["v_g_V", "v_ibg_V", "vcm_V", "vref_V", "i_slot_uA", "t_g90_us",
                                     "t_vcm98_us", "settle_85_90us_V"]):
                x = vals[k] if k < len(vals) else ""
                try:
                    x = float(x)
                    x = round(x * 1e6, 2) if key.startswith("t_") else round(x, 5)
                except ValueError:
                    x = "FAILED" if not vals else "n/a"
                res[key] = x
            sv = b.group(1).split() if b else []
            errs = []
            for k, (vin, _) in enumerate(STEPS):
                try:
                    errs.append(float(sv[3 * k]))
                except (IndexError, ValueError):
                    pass
            if MODES[name][1] == "feed":
                errs = errs[2:3]  # pad in fixed: one sample
            res["err_max_mV"] = round(max(abs(e) for e in errs) * 1e3, 2) if errs else "FAILED"
            res["n_samples"] = len(errs)
        else:
            a = re.search(r"^DCOP (\S*) *(\S*)", r.stdout, re.M)
            ok = bool(a and a.group(1))
            res["err_max_mV"] = round(float(a.group(1)) * 1e3, 2) if ok else "FAILED"
            res["v_g_V"] = round(float(a.group(2)), 4) if ok and a.group(2) else ""
            res["solver_notes"] = "; ".join(sorted(set(m.strip() for m in re.findall(
                r"(?:Warning|Note|Error)[^\n]*(?:gmin|source|Transient op|singular|converge|aborted)[^\n]*",
                r.stdout + r.stderr))))[:300]
        print("ROW", res, flush=True)
        with open(OUT / f"slot_modes_{var}.csv", "a", newline="") as fo:
            w = csv.writer(fo)
            w.writerow([f"{k}={x}" for k, x in res.items()])


if __name__ == "__main__":
    main()
