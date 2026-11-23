#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Markdown data sheet of one cell from its committed CACE files (no simulation is run).

Reads <cell>.yaml (pins, default conditions, parameter groups with conditions) and, per results directory, the
summary_<group>.md written by CACE (the rows whose status is not Skip are reproduced) and <group>.csv (number of runs).
Usage: make_datasheet.py <cell.yaml> <out.md> --title T --repo-url URL --commit SHA --cell-path PATH
                         --view LABEL=RESULTS_DIR [--view ...] [--intro FILE] [--notes FILE]
"""
import argparse, csv, glob, json, os, re, yaml

ZW = "​"

def cells(line):
    return [c.strip().replace(ZW, "") for c in line.strip().strip("|").split("|")]

def read_summary(path):
    rows = []
    hdr = None
    for l in open(path, encoding="utf-8"):
        if not l.startswith("|"):
            continue
        c = cells(l)
        if c and c[0] == "Parameter":
            hdr = c; continue
        if set("".join(c)) <= set(":-"):
            continue
        if hdr and len(c) == len(hdr):
            rows.append(dict(zip(hdr, c)))
    return rows

def cond_text(v):
    if isinstance(v, dict):
        if "enumerate" in v: return ", ".join(str(x) for x in v["enumerate"])
        if "typical" in v and len(v) == 1: return str(v["typical"])
        if "range" in v: return "range " + json.dumps(v["range"])
        if "minimum" in v and "maximum" in v: return f"{v['minimum']} … {v['maximum']} (step {v.get('stepsize','')})"
        return json.dumps(v, default=str)
    return str(v)

def nruns(csvpath):
    try:
        with open(csvpath, newline="") as f:
            return max(0, sum(1 for _ in f) - 1)
    except OSError:
        return None


import statistics as _st
_NUM = re.compile(r"^\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*(.*?)\s*$")

def parse_val(txt):
    m = _NUM.match(txt or "")
    return (float(m.group(1)), m.group(2)) if m else (None, "")

def fnum(v):
    if v is None: return "—"
    return f"{v:.4g}"

def read_csv(path):
    try:
        with open(path, newline="") as f:
            return list(csv.DictReader(f))
    except OSError:
        return None

def infer_scale(vals, smin, smax):
    """Scale k such that vals*k reproduces the summary's min and max (the CSV unit labels are unreliable)."""
    tol = lambda x: max(0.0006, 0.006 * abs(x))
    cands = []
    for k in (1, 1e3, 1e6, 1e9, 1e12, 1e-3, 1e-6, 1e-9, 1e-12, 1e2, 1e-2):
        if abs(min(vals) * k - smin) <= tol(smin) and abs(max(vals) * k - smax) <= tol(smax):
            cands.append(k)
    return cands

def expost_rows(groups, d, defaults):
    """One row per quantity per group: min / typical-condition value / median / max over the CSV, scaled to the summary's unit."""
    out = []
    for g, spec in groups.items():
        sp = os.path.join(d, f"summary_{g}.md")
        if not os.path.exists(sp):
            continue
        srows = [r for r in read_summary(sp) if "Skip" not in r.get("Status", "")]
        data = read_csv(os.path.join(d, f"{g}.csv"))
        condkeys = list((spec.get("conditions") or {}).keys())
        for r in srows:
            key = r.get("Result", "")
            smin, u1 = parse_val(r["Min Value"]); styp, u2 = parse_val(r["Typ Value"]); smax, u3 = parse_val(r["Max Value"])
            unit = u1 or u3 or u2
            row = dict(group=g, quantity=r["Parameter"], unit=unit, n=None, note="")
            if not data:
                row.update(min=smin, typ=None, med=styp, max=smax, nlabel="Monte Carlo (iterations up to %s)" % (
                    (spec.get("conditions", {}).get("iterations", {}) or {}).get("maximum", "?")),
                    atmin="", atmax="", note="CACE summary values (per-run CSV not committed)")
                out.append(row); continue
            col = next((c for c in data[0].keys() if c.startswith(key + "[")), None)
            if col is None or smin is None or smax is None:
                row.update(min=smin, typ=None, med=styp, max=smax, nlabel=str(len(data)), atmin="", atmax="", note="from CACE summary (column not found)")
                out.append(row); continue
            try:
                vals = [float(x[col]) for x in data]
            except ValueError:
                continue
            ks = infer_scale(vals, smin, smax)
            if not ks:
                row.update(min=smin, typ=None, med=styp, max=smax, nlabel=str(len(data)), atmin="", atmax="", note="from CACE summary (unit scale of the CSV not resolved)")
                out.append(row); continue
            k = ks[0]
            if len(ks) > 1: row["note"] = "unit scale inferred, ambiguous near 0"
            sv = [v * k for v in vals]
            ccols = [c for c in condkeys if c in data[0]]
            def cond(x): return ", ".join(f"{c}={x[c]}" for c in ccols)
            imin = min(range(len(sv)), key=lambda i: sv[i]); imax = max(range(len(sv)), key=lambda i: sv[i])
            # typical-condition rows
            typrows = []
            for i, x in enumerate(data):
                ok = True
                for c in ccols:
                    t = (defaults.get(c) or {}).get("typical")
                    if t is None: continue
                    xv = x[c]
                    try: ok = ok and abs(float(xv) - float(t)) < 1e-9
                    except ValueError: ok = ok and str(xv) == str(t)
                if ok: typrows.append(sv[i])
            row.update(min=sv[imin], max=sv[imax], med=_st.median(sv), typ=(_st.median(typrows) if typrows else None),
                       nlabel=str(len(data)), atmin=cond(data[imin]), atmax=cond(data[imax]))
            out.append(row)
    return out

DISCLAIMER = (
    "The design is a proof of concept and had **no specification** before it was characterized. The limits and verdicts in the CACE files (section 'CACE run summaries') are the "
    "designer's *working limits*, in part set from earlier measured bands, so *Pass* means \"inside the designer's working limit\", not \"meets a specification\". "
    "This section instead states, **ex post facto**, the interval each characterized quantity covered: the minimum and maximum over every run of the group's characterization grid "
    "(corners, temperature, supply, … as listed), the value at typical conditions (default conditions of the CACE file: tt, 27 °C, 3.3 V, typical resistor / PNP corners) where such a run exists, and the median over the group "
    "(CACE's own *typ* value). It is a description of what was simulated, **not a guarantee**; Monte Carlo rows are the observed range of the sampled iterations, not ±3σ; no silicon was measured.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("yaml"); ap.add_argument("out")
    ap.add_argument("--title", required=True); ap.add_argument("--repo-url", required=True)
    ap.add_argument("--commit", required=True); ap.add_argument("--cell-path", required=True)
    ap.add_argument("--view", action="append", required=True)
    ap.add_argument("--intro"); ap.add_argument("--notes")
    a = ap.parse_args()
    y = yaml.safe_load(open(a.yaml))
    base = f"{a.repo_url}/blob/{a.commit}/{a.cell_path}"
    tree = f"{a.repo_url}/tree/{a.commit}/{a.cell_path}"
    L = ["<!--", "SPDX-FileCopyrightText: 2026 Christoph Maier", "SPDX-License-Identifier: Apache-2.0", "-->",
         f"# {a.title}", ""]
    if a.intro: L += [open(a.intro).read().strip(), ""]
    au = y.get("authorship", {})
    L += [f"**Cell:** `{y['name']}`  ", f"**Description (from the CACE file):** {y.get('description','')}  ",
          f"**PDK:** {y.get('PDK','')}  ", f"**Designer:** {au.get('designer','')}, CACE file created {au.get('creation_date','')}  ",
          f"**Source:** [`{a.cell_path}/verification/cace/{os.path.basename(a.yaml)}`]({base}/verification/cace/{os.path.basename(a.yaml)}) at design-repository commit `{a.commit[:8]}`; "
          f"results [`verification/cace/results/`]({tree}/verification/cace/results)  ",
          "**Generated:** by `datasheets/tools/make_datasheet.py` from the committed CACE files; **no simulation was run for this sheet** and nothing was re-checked against the taped-out netlist.", ""]
    L += ["## Pins", "", "| pin | type | direction | description | limits |", "|---|---|---|---|---|"]
    for n, p in (y.get("pins") or {}).items():
        lim = " ".join(f"{k} {p[k]}" for k in ("Vmin", "Vmax") if k in p)
        L.append(f"| `{n}` | {p.get('type','')} | {p.get('direction','')} | {p.get('description','')} | {lim} |")
    L += ["", "## Default conditions", "", "| condition | typical | unit | description |", "|---|---|---|---|"]
    for n, c in (y.get("default_conditions") or {}).items():
        L.append(f"| `{n}` | {c.get('typical','')} | {c.get('unit','')} | {c.get('description','')} |")
    L.append("")
    groups = y.get("parameters") or {}
    defaults = y.get("default_conditions") or {}
    total = {}
    L += ["## Specification (ex post facto, as characterized)", "", DISCLAIMER, ""]
    for label, d in (v.split("=", 1) for v in a.view):
        rows = expost_rows(groups, d, defaults)
        L += [f"### View: {label}", "", "| group | quantity | unit | min | typ (typical conditions) | median | max | runs | where min / where max |", "|---|---|---|---:|---:|---:|---:|---|---|"]
        for r in rows:
            where = (r["atmin"] + " / " + r["atmax"]) if r["atmin"] or r["atmax"] else r["note"]
            if r["atmin"] and r["note"]: where += f" ({r['note']})"
            L.append(f"| {r['group']} | {r['quantity']} | {r['unit']} | {fnum(r['min'])} | {fnum(r['typ'])} | {fnum(r['med'])} | {fnum(r['max'])} | {r['nlabel']} | {where} |")
        L.append("")
    sections = []
    for label, d in (v.split("=", 1) for v in a.view):
        S = [f"## CACE run summaries (designer's working limits): {label}", "",
             f"Results directory: `verification/cace/results/{os.path.basename(d)}`. "
             "One table per parameter group, as CACE wrote it in `summary_<group>.md` (rows with status *Skip* belong to other groups and are left out): "
             "the designer's working limits, the measured minimum / typical (median) / maximum over the runs of the group, and CACE's status against those limits (*not* a specification check). *Runs* is the number of rows of the group's CSV.", ""]
        counts = {"Pass": 0, "Fail": 0, "other": 0}
        gl = []
        for g, spec in groups.items():
            sp = os.path.join(d, f"summary_{g}.md")
            if not os.path.exists(sp):
                continue
            rows = [r for r in read_summary(sp) if "Skip" not in r.get("Status", "")]
            runs = nruns(os.path.join(d, f"{g}.csv"))
            conds = (spec.get("conditions") or {})
            ctext = "; ".join(f"{k}: {cond_text(v)}" for k, v in conds.items())
            G = [f"### {g}", ""]
            if spec.get("display") or spec.get("description"):
                G += [f"{spec.get('display','')} {spec.get('description','')}".strip(), ""]
            rt = ("n/a (no CSV in the results directory)" if runs is None else
                  f"{runs}" if runs else "0 rows in the committed CSV (header only: the per-run data were not committed; the values below are CACE's own summary)")
            G += [f"*Runs:* {rt}  ", f"*Swept conditions:* {ctext or 'default only'}  ", ""]
            G += ["| quantity | working min limit | min value | typ (median) | working max limit | max value | vs working limit |", "|---|---:|---:|---:|---:|---:|---|"]
            for r in rows:
                st = r["Status"]
                key = "Pass" if "Pass" in st else "Fail" if "Fail" in st else "other"
                counts[key] += 1
                G.append(f"| {r['Parameter']} | {r['Min Limit']} | {r['Min Value']} | {r['Typ Value']} | {r['Max Limit']} | {r['Max Value']} | {st} |")
            G.append("")
            gl += G
            sections.append((label, g, runs, len(rows)))
        S += [f"**Rows in this view:** {counts['Pass']} inside the working limits, {counts['Fail']} outside, {counts['other']} other (one row per quantity and group; not run counts).", ""]
        S += gl
        total[label] = counts
        L += S
    if a.notes: L += ["## Notes", "", open(a.notes).read().strip(), ""]
    L += ["## What is not in this sheet", "",
          "- Any group that has no CSV or summary in the results directory (not run, or run in another view).",
          "- Whether the simulated netlist equals the block as taped out (see `../characterization_candidates.md`).",
          "- Monte Carlo statistics beyond what the group's own summary reports (min / typ / max over the runs).",
          "- Measurements on silicon: none exist at the time of writing.", ""]
    open(a.out, "w", encoding="utf-8").write("\n".join(L))
    for label, c in total.items():
        print(a.out, label, c)

main()
