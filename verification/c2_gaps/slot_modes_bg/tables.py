# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Tabulate slot_modes.py and bg_core.py results into results.md and CSVs (IHP sg13cmos5l simulation).

usage: python3 -I tables.py <work-dir> <out-dir>
  reads <work-dir>/slot_out/slot_modes_{pu,dcop,dcns}.csv (key=value rows) and <out-dir>/bg_core_{dc,ramp,diag}.csv
  writes <out-dir>/slot_modes_powerup.csv, <out-dir>/slot_modes_dc_diag.csv, <out-dir>/results_tables.md
"""
import csv
import re
import statistics
import sys
from pathlib import Path

WORK, OUT = Path(sys.argv[1]), Path(sys.argv[2])
HDR = "# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n"
MODES = ["default", "swap", "mon", "feed", "ext", "all_high", "swap+feed", "no_key_swap"]


def kv_rows(f):
    rows = []
    if not f.exists():
        return rows
    for r in csv.reader(f.open()):
        d = {}
        for cell in r:
            k, _, v = cell.partition("=")
            d[k] = v
        rows.append(d)
    return rows


def write(rows, path, note):
    if not rows:
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as f:
        f.write(HDR + f"# IHP sg13cmos5l simulation. {note}\n")
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def read_csv(path):
    if not path.exists():
        return []
    return list(csv.DictReader(ln for ln in path.open() if not ln.startswith("#")))


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


md = []
# ---------------- slot modes from power-up
pu = kv_rows(WORK / "slot_out" / "slot_modes_pu.csv")
seen = {}
for r in pu:  # last run of a job wins
    seen[(r["mode"], r["mos"], r["temp"], r["vdd"])] = r
pu = list(seen.values())
write(pu, OUT / "slot_modes_powerup.csv", "slot 7 modes from power-up (slot_modes.py 'pu'); bg_core_pd schematic, "
      "pads / pad_ref_rb / bias_dist_pd extracted. err_max_mV = max |pad out - expected| over the pad-in steps; "
      "t_* absolute (enable at 20 us)")
pts = sorted({(r["mos"], r["temp"], r["vdd"]) for r in pu}, key=lambda p: (int(p[1]), p[0], float(p[2])))
md.append("### Slot 7 modes from power-up: max |D2S pad out - expected| [mV]\n")
md.append("IHP sg13cmos5l simulation; bg_core_pd schematic, both pads / pad_ref_rb / bias_dist_pd extracted, "
          "ls_up_fs / s7_ctrl source. Pad in 0 / 0.25 / 0.5 / 0.75 / 1.0 V (feed modes: 0.5 V). "
          "`FAILED` = simulator gave no result; empty = not run in the time box.\n")
md.append("| MOS | T [C] | V | " + " | ".join(MODES) + " | vcm / vref [V] | bandgap g [V] | t(g 90 %) after enable [us] |")
md.append("|---|---|---|" + "---|" * len(MODES) + "---|---|---|")
for p in pts:
    cells, vv, gg, tg = [], "", "", ""
    for m in MODES:
        r = seen.get((m, *p))
        cells.append("" if r is None else str(r.get("err_max_mV", "")))
        if r is not None and fnum(r.get("vcm_V")) is not None and not vv:
            vv = f"{float(r['vcm_V']):.3f} / {float(r['vref_V']):.3f}"
            gg = f"{float(r['v_g_V']):.3f}"
    tgs = [fnum(seen[(m, *p)].get("t_g90_us")) for m in MODES if (m, *p) in seen]
    tgs = [x - 20.0 for x in tgs if x is not None]
    tg = f"{min(tgs):.2f} ... {max(tgs):.2f}" if tgs else ""
    md.append(f"| {p[0]} | {p[1]} | {p[2]} | " + " | ".join(cells) + f" | {vv} | {gg} | {tg} |")
md.append("")

# ---------------- DC diagnosis
dd = kv_rows(WORK / "slot_out" / "slot_modes_dcop.csv") + kv_rows(WORK / "slot_out" / "slot_modes_dcns.csv")
for r in dd:
    lg = WORK / "slot" / f"{r['variant']}_{r['mode']}_{r['mos']}_{r['temp']}_{r['vdd']}.log"
    tr = re.findall(r"(?:Timestep too small|singular)[^\n]*", lg.read_text()) if lg.exists() else []
    r["trouble"] = tr[0].strip() if tr else ""
    r.pop("solver_notes", None)
write(dd, OUT / "slot_modes_dc_diag.csv", "the designer's DC deck (dcop) and the same with .nodeset of the bandgap nodes"
      " (dcns), ss -40 C 3.0 V; solver_notes = ngspice messages")
if dd:
    md.append("### DC solver diagnosis at ss / -40 C / 3.0 V (designer's DC deck)\n")
    md.append("| mode | variant | max error [mV] | ngspice (first failing instance, if any) |")
    md.append("|---|---|---|---|")
    for r in dd:
        md.append(f"| {r['mode']} | {r['variant']} | {r['err_max_mV']} | {r.get('trouble', '') or ''} |")
    md.append("")

# ---------------- bg_core_pd
dc = read_csv(OUT / "bg_core_dc.csv")
K = "i_op_uA"  # the DC solution; the power-up transient end is the cross-check
if dc:
    md.append("### bg_core_pd alone: iout into 0.7 V [uA] (.op; cross-checked against the end of a 200 us power-up transient)\n")
    for view in ("schematic", "extracted"):
        rows = [r for r in dc if r["view"] == view and fnum(r[K]) is not None]
        if not rows:
            continue
        vals = [float(r[K]) for r in rows]
        typ = [float(r[K]) for r in rows if r["mos"] == "tt" and r["res"] == "res_typ"
               and r["temp"] == "27" and r["vdd"] == "3.3"]
        mn = min(rows, key=lambda r: float(r[K]))
        mx = max(rows, key=lambda r: float(r[K]))
        md.append(f"**{view}** ({len(rows)} points): min {min(vals):.3f} ({mn['mos']} {mn['res']} {mn['temp']} C "
                  f"{mn['vdd']} V), typ {typ[0] if typ else 'n/a'} (tt res_typ 27 C 3.3 V), max {max(vals):.3f} "
                  f"({mx['mos']} {mx['res']} {mx['temp']} C {mx['vdd']} V).")
        res_typ = [float(r[K]) for r in rows if r["res"] == "res_typ"]
        if res_typ:
            md.append(f"res_typ only: {min(res_typ):.3f} ... {max(res_typ):.3f} uA.")
        # op vs tran
        dev = [abs(float(r["i_op_uA"]) - float(r["i_tran_uA"])) / float(r["i_op_uA"]) * 100 for r in rows
               if fnum(r["i_tran_uA"]) is not None]
        dev100 = [abs(float(r["i_tran100_uA"]) - float(r["i_tran_uA"])) / float(r["i_op_uA"]) * 100 for r in rows
                  if fnum(r["i_tran100_uA"]) is not None]
        md.append(f"|.op - transient end| max {max(dev):.2f} %; |value at 100 us - at 199 us| max {max(dev100):.2f} %.")
        # supply sensitivity
        sens = []
        for key in {(r["mos"], r["res"], r["temp"]) for r in rows}:
            d = {r["vdd"]: float(r[K]) for r in rows if (r["mos"], r["res"], r["temp"]) == key}
            if "3.0" in d and "3.6" in d and "3.3" in d:
                sens.append(((d["3.6"] - d["3.0"]) / 0.6 / d["3.3"] * 100, key))
        if sens:
            s_abs = sorted(sens, key=lambda x: abs(x[0]))
            md.append(f"Supply sensitivity (I(3.6) - I(3.0)) / 0.6 V / I(3.3): median "
                      f"{statistics.median(x[0] for x in sens):.3f} %/V, largest {s_abs[-1][0]:.3f} %/V "
                      f"({' '.join(s_abs[-1][1])} C).")
        tco = []
        for key in {(r["mos"], r["res"], r["vdd"]) for r in rows}:
            d = {r["temp"]: float(r[K]) for r in rows if (r["mos"], r["res"], r["vdd"]) == key}
            if len(d) == 3:
                tco.append((max(d.values()) - min(d.values())) / d["27"] * 100)
        if tco:
            md.append(f"Spread over -40 ... 125 C (max - min) / I(27 C): {min(tco):.2f} ... {max(tco):.2f} %.")
        md.append("")
        temps = ["-40", "27", "125"]
        md.append(f"{view}, 3.3 V: rows MOS x rhigh corner, columns T")
        md.append("")
        md.append("| MOS | res | " + " | ".join(f"{t} C" for t in temps) + " |")
        md.append("|---|---|" + "---|" * len(temps))
        for m in ("tt", "ss", "ff", "sf", "fs"):
            for rs in ("res_typ", "res_bcs", "res_wcs"):
                d = {r["temp"]: r[K] for r in rows if r["mos"] == m and r["res"] == rs and r["vdd"] == "3.3"}
                if d:
                    md.append(f"| {m} | {rs} | " + " | ".join(str(d.get(t, "")) for t in temps) + " |")
        md.append("")
ramp = read_csv(OUT / "bg_core_ramp.csv")
if ramp:
    md.append("### bg_core_pd start-up by supply ramp (vdd = en_3v3 0 -> V; iout into 0.7 V)\n")
    md.append("| view | MOS | T [C] | V | ramp | t(90 % of final) [us] | I 20 us after ramp end [uA] | I at end [uA] |")
    md.append("|---|---|---|---|---|---|---|---|")
    for r in ramp:
        md.append(f"| {r['view']} | {r['mos']} | {r['temp']} | {r['vdd']} | {r['ramp']} | {r['t90_us']} | "
                  f"{r.get('i_ramp20us_uA', '')} | {r['i_end_uA']} |")
    md.append("")
diag = read_csv(OUT / "bg_core_diag.csv")
if diag:
    md.append("### bg_core_pd: is there a zero-current state? (diagnosis)\n")
    md.append("| view | MOS | T [C] | V | .op from .nodeset at zero current: I [uA], g [V] | transient from .ic at zero "
              "current, supply up: I at 49 us [uA], t(90 %) [us] |")
    md.append("|---|---|---|---|---|---|")
    for r in diag:
        md.append(f"| {r['view']} | {r['mos']} | {r['temp']} | {r['vdd']} | {r['i_op_nodeset_off_uA']}, {r['v_g_op_V']}"
                  f" | {r['i_tran_ic_off_50us_uA']}, {r['t90_from_off_us']} |")
    md.append("")

(OUT / "results_tables.md").write_text("<!--\n" + HDR.replace("# ", "") + "-->\n" + "\n".join(md) + "\n")
print("\n".join(md))
