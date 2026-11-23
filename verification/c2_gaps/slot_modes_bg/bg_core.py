# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""bg_core_pd alone (IHP sg13cmos5l simulation): output current over corners, supply ramps, supply sensitivity.

usage: python3 -I bg_core.py <design-repo-tree> <work-dir> <out-dir> [dc|ramp|all]

<design-repo-tree> holds macros/bg_core_pd/netlist/{schematic,pex} at the design-repo commit (run.sh fetches them).
Views: schematic = netlist/schematic/bg_core_pd_magic.spice (subckt bg_core_pd), extracted =
netlist/pex/bg_core_pd_magic_pex_3.spice (magic PEX with R and C; subckt bg_core_pd_pex, same port order vdd vss iout en_3v3 en_3v3_b).

Load: iout into a 0.7 V source (I reported = current sourced by the core). Enabled: en_3v3 = vdd, en_3v3_b = 0.
DC: end state of a transient (vdd and en_3v3 0 -> V in 2 us, 200 us; the value at 100 us as a settling check),
cross-checked with a plain .op; for the extracted view both on the DC-equivalent netlist (capacitors dropped, see noc()); MOS tt/ss/ff/sf/fs x rhigh res_typ/res_bcs/res_wcs x -40/27/125 C x 3.0/3.3/3.6 V, pnpMPA typ.
Ramp: vdd and en_3v3 ramp 0 -> V in 1 us and in 1 ms, iout vs time, at the five MOS corners at -40 C / 3.0 V and
125 C / 3.6 V (extracted view: ss and ff only).
Diag (second-state check): .op with .nodeset at the zero-current state, and a transient with the supply already up and
.ic at the zero-current state (diagnosis only; neither changes the circuit).
Ramp and diag use method=gear: with the default trapezoidal integration iout (the current of the ideal 0.7 V load
source) alternates from one time point to the next (e.g. 4.59 / 5.18 uA, extracted ss 125 C, 1 us ramp) around the
DC value, the known trapezoidal ringing; the DC table keeps trapezoidal and reports .op (the transient end only as a
cross-check).
usage of the last argument: dc | ramp | diag | all
"""
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TREE, WORK, OUT = (Path(a).resolve() for a in sys.argv[1:4])
WHAT = sys.argv[4] if len(sys.argv) > 4 else "all"
BG = TREE / "macros" / "bg_core_pd" / "netlist"
VIEWS = {"schematic": (BG / "schematic" / "bg_core_pd_magic.spice", "bg_core_pd"),
         "extracted": (BG / "pex" / "bg_core_pd_magic_pex_3.spice", "bg_core_pd_pex")}
MOS = ["tt", "ss", "ff", "sf", "fs"]
RES = ["res_typ", "res_bcs", "res_wcs"]
TEMPS = [-40, 27, 125]
VDDS = [3.0, 3.3, 3.6]
NPAR = int(os.environ.get("NPAR", "2"))  # parallel ngspice runs


def noc(f):
    """DC-equivalent copy of a PEX netlist: capacitor lines dropped (they carry no DC current). Used for the DC table:
    ngspice's .op of the full PEX at ss / -40 C ends in its 'transient op' with capacitor currents still flowing
    (iout 6.92 uA with pex_3, 8.29 uA with pex_2, against 4.85 uA without the capacitors and for the schematic)."""
    g = WORK / (f.stem + "_noC.spice")
    g.write_text("".join(ln for ln in f.read_text().splitlines(True) if not ln[:1] in "cC"))
    return g


def head(view, mos, res, t, dc=False, gear=True):
    f, cell = VIEWS[view]
    if dc and view == "extracted":
        f = noc(f)
    return f"""* bg_core_pd {view} {mos} {res} {t} C
.lib cornerMOShv.lib mos_{mos}
.lib cornerRES.lib {res}
.lib cornerPNP.lib typ
.include {f}
.temp {t}
.option gmin=1e-12{" method=gear" if gear else ""}
.param vdd=3.3
Vdd vdd 0 {{vdd}}
Ven en 0 {{vdd}}
Venb enb 0 0
Vload iout 0 0.7
X1 vdd 0 iout en enb {cell}
"""


def run(deck, name):
    f = WORK / f"{name}.spice"
    f.write_text(deck)
    log = subprocess.run(["ngspice", "-b", f.name], cwd=WORK, capture_output=True, text=True).stdout
    f.with_suffix(".log").write_text(log)
    return log


def dc_job(view, mos, res, t):
    # per V (own deck): 2 us supply ramp from 0 V (en tied to vdd), values at 100 / 199 us; then a plain op
    g = "x1.g" if view == "schematic" else "x1.bg_n4_0.g"
    rows = []
    for v in VDDS:
        deck = head(view, mos, res, t, dc=True, gear=False).replace("Vdd vdd 0 {vdd}", f"Vdd vdd 0 pwl(0 0 2u {v})").replace(
            "Ven en 0 {vdd}", f"Ven en 0 pwl(0 0 2u {v})") + f""".control
tran 50n 200u uic
meas tran iend find i(Vload) at=199u
meas tran i100 find i(Vload) at=100u
meas tran gend find v({g}) at=199u
echo "TRAN $&iend $&i100 $&gend"
destroy all
alter Vdd dc {v}
alter Ven dc {v}
op
let iop = i(Vload)
echo "OP $&iop"
.endc
.end
"""
        log = run(deck, f"bgdc_{view}_{mos}_{res}_{t}_{v}")
        a = re.search(r"^TRAN (\S+) (\S+) (\S+)", log, re.M)
        b = re.search(r"^OP (\S+)", log, re.M)
        if not (a and b):
            rows.append(dict(view=view, mos=mos, res=res, temp=t, vdd=v, i_tran_uA="FAILED", i_tran100_uA="",
                             i_op_uA="", v_g_V=""))
            continue
        iend, i100, gv = (float(x) for x in a.groups())
        rows.append(dict(view=view, mos=mos, res=res, temp=t, vdd=v, i_tran_uA=round(iend * 1e6, 4),
                         i_tran100_uA=round(i100 * 1e6, 4), i_op_uA=round(float(b.group(1)) * 1e6, 4),
                         v_g_V=round(gv, 4)))
    return rows


def ramp_job(view, mos, t, v, tr):
    tstop = {"1u": "300u", "1m": "1.5m"}[tr]
    tstep = {"1u": "20n", "1m": "1u"}[tr]
    t20 = {"1u": "21u", "1m": "1.02m"}[tr]
    deck = head(view, mos, "res_typ", t).replace(f"Vdd vdd 0 {{vdd}}", f"Vdd vdd 0 pwl(0 0 {tr} {v})").replace(
        "Ven en 0 {vdd}", f"Ven en 0 pwl(0 0 {tr} {v})")
    g = "x1.g" if view == "schematic" else "x1.bg_n4_0.g"
    name = f"bgramp_{view}_{mos}_{t}_{v}_{tr}"
    deck += f""".control
tran {tstep} {tstop} uic
let iu = i(Vload)*1e6
meas tran iend find iu at={tstop}
let thr = 0.9*iend
meas tran t90 when iu=thr cross=last
meas tran i20 find iu at={t20}
wrdata {name}.dat iu v(vdd) v({g})
echo "RAMP $&iend $&t90 $&i20"
.endc
.end
"""
    log = run(deck, name)
    m = re.search(r"^RAMP (\S+) (\S+) (\S+)", log, re.M)
    if not m:
        return dict(view=view, mos=mos, temp=t, vdd=v, ramp=tr, i_end_uA="FAILED", t90_us="", i_ramp20us_uA="")
    return dict(view=view, mos=mos, temp=t, vdd=v, ramp=tr, i_end_uA=round(float(m.group(1)), 4),
                t90_us=round(float(m.group(2)) * 1e6, 3), i_ramp20us_uA=round(float(m.group(3)), 4))


def diag_job(view, mos, t, v):
    """Is there a second (zero-current) state? (a) .op with .nodeset at the off state; (b) transient with vdd at its
    final value and .ic at the off state (g = 0, vpg = vpc = ks = vdd, iout node held by the load)."""
    pre = "x1." if view == "schematic" else "x1.bg_n4_0."
    vpg = "x1.vpg" if view == "schematic" else "x1.bg_pmir_pcas_c_0.vpg"
    off = f"v({pre}g)=0 v({vpg})={v} v({pre}vpc)={v} v({pre}ks)={v}"
    base = head(view, mos, "res_typ", t, dc=True).replace("Vdd vdd 0 {vdd}", f"Vdd vdd 0 {v}").replace(
        "Ven en 0 {vdd}", f"Ven en 0 {v}")
    deck = base + f""".nodeset {off}
.ic {off}
.control
op
let iop = i(Vload)
let gop = v({pre}g)
echo "NSOP $&iop $&gop"
destroy all
tran 10n 50u uic
meas tran ifin find i(Vload) at=49u
let thr = 0.9*ifin
meas tran t90 when i(Vload)=thr cross=last
meas tran g0 find v({pre}g) at=10n
echo "ICTR $&ifin $&t90 $&g0"
.endc
.end
"""
    name = f"bgdiag_{view}_{mos}_{t}_{v}"
    log = run(deck, name)
    a = re.search(r"^NSOP (\S+) (\S+)", log, re.M)
    b = re.search(r"^ICTR (\S+) (\S+) (\S+)", log, re.M)
    r = dict(view=view, mos=mos, temp=t, vdd=v)
    r["i_op_nodeset_off_uA"] = round(float(a.group(1)) * 1e6, 4) if a else "FAILED"
    r["v_g_op_V"] = round(float(a.group(2)), 4) if a else ""
    r["i_tran_ic_off_50us_uA"] = round(float(b.group(1)) * 1e6, 4) if b else "FAILED"
    r["t90_from_off_us"] = round(float(b.group(2)) * 1e6, 3) if b else ""
    r["v_g_t0_V"] = round(float(b.group(3)), 4) if b else ""
    return r


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        f.write("# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n"
                "# IHP sg13cmos5l simulation, bg_core_pd alone (view per row)\n")
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    if WHAT in ("dc", "all"):
        jobs = [(vw, m, r, t) for vw in VIEWS for m in MOS for r in RES for t in TEMPS
                if vw == "schematic" or r == "res_typ"]
        with ThreadPoolExecutor(NPAR) as ex:
            rows = [r for rs in ex.map(lambda a: dc_job(*a), jobs) for r in rs]
        write_csv(rows, OUT / "bg_core_dc.csv")
    if WHAT in ("ramp", "all"):
        jobs = [(vw, m, t, v, tr) for vw in VIEWS for m in ("tt", "ss", "ff", "sf", "fs") for (t, v) in
                ((-40, 3.0), (125, 3.6)) for tr in ("1u", "1m")
                if vw == "schematic" or m in ("ss", "ff")]
        with ThreadPoolExecutor(NPAR) as ex:
            rows = list(ex.map(lambda a: ramp_job(*a), jobs))
        write_csv(rows, OUT / "bg_core_ramp.csv")
    if WHAT in ("diag", "all"):
        jobs = [(vw, m, t, v) for vw in VIEWS for m in MOS for (t, v) in ((-40, 3.0), (125, 3.6))
                if vw == "schematic" or m in ("ss", "ff")]
        with ThreadPoolExecutor(NPAR) as ex:
            rows = list(ex.map(lambda a: diag_job(*a), jobs))
        write_csv(rows, OUT / "bg_core_diag.csv")


if __name__ == "__main__":
    main()
