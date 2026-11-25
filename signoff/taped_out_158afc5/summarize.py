#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Summarize a run of run_signoff.sh: OUT_DIR/summary/<cell>.<check>.txt and OUT_DIR/summary/summary.txt.

Everything is read from the tool output files; nothing is assumed:
  KLayout DRC  .lyrdb  -> number of rule categories, items (violations) per category
  KLayout logs         -> lines with 'exception', 'Traceback', 'ERROR' (a bare "Passed" is not trusted)
  KLayout LVS  .lvsdb  -> cross-reference status per circuit pair, device / net / pin pairs and their status
  magic DRC    .rpt    -> COUNT and the error types
  netgen       .out    -> 'Final result' lines, per-cell match lines, pin (port) mismatches of the top cell
Large result databases (> 2 MB) are not copied; their sha256 is listed in OUT_DIR/summary/files.txt.
"""
import glob
import hashlib
import os
import re
import shutil
import sys

import klayout.db as kdb
import klayout.rdb as krdb

OUT = os.path.abspath(sys.argv[1])
SUM = os.path.join(OUT, "summary")
os.makedirs(SUM, exist_ok=True)
CELLS = ["slot_7", "S2D", "D2S", "bg_core_pd"]
LIMIT = 2 * 1024 * 1024
lines_all = []
files = []


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def rel(p):
    return os.path.relpath(p, OUT)


def keep(p, name, copy=True):
    """copy a result file into summary/ if < 2 MB (and copy is set), always record size and sha256"""
    size = os.path.getsize(p)
    copied = copy and size < LIMIT
    if copied:
        shutil.copyfile(p, os.path.join(SUM, name))
    files.append("%s\t%d\t%s\t%s" % (rel(p), size, sha(p), ("copied as summary/" + name) if copied else ("not copied (> 2 MB)" if copy else "not copied (diagnostic run)")))


def log_scan(paths):
    exc = tb = err = 0
    hits = []
    for p in paths:
        with open(p, errors="replace") as f:
            for ln in f:
                low = ln.lower()
                e = "exception" in low
                t = "traceback" in low
                r = re.search(r"\bERROR\b", ln) is not None
                exc += e
                tb += t
                err += r
                if (e or t or r) and len(hits) < 20:
                    hits.append("    %s: %s" % (os.path.basename(p), ln.rstrip()[:200]))
    return exc, tb, err, hits


def runtime(cell, step):
    p = os.path.join(OUT, "runtimes.txt")
    res = []
    if os.path.exists(p):
        for ln in open(p):
            f = ln.rstrip("\n").split("\t")
            if len(f) >= 5 and f[0] == cell and f[1] == step:
                res.append((f[2], f[3], f[4]))
    return res


def drc_summary(cell, step, subdir):
    d = os.path.join(OUT, cell, subdir)
    out = []
    dbs = sorted(glob.glob(os.path.join(d, "*.lyrdb")))
    logs = sorted(glob.glob(os.path.join(d, "*.log"))) + [os.path.join(OUT, "logs", "%s.%s.log" % (cell, step))]
    logs = [p for p in logs if os.path.exists(p)]
    for rc, t, cmd in runtime(cell, step):
        out.append("command: %s\nexit code: %s, wall time: %s" % (cmd, rc.replace("rc=", ""), t))
    if not dbs:
        out.append("NO .lyrdb produced in %s" % rel(d))
    total = 0
    for p in dbs:
        db = krdb.ReportDatabase("")
        db.load(p)
        cats = list(db.each_category())
        n = db.num_items()
        total += n
        out.append("report %s: %d rule categories, %d items (violations)" % (rel(p), len(cats), n))
        for c in cats:
            if c.num_items() > 0:
                out.append("    %-14s %6d   %s" % (c.name(), c.num_items(), (c.description or "")[:110]))
        keep(p, "%s.%s.%s" % (cell, step, os.path.basename(p)))
    exc, tb, err, hits = log_scan(logs)
    out.append("logs scanned: %s" % ", ".join(rel(p) for p in logs))
    out.append("log lines: 'exception' %d, 'Traceback' %d, 'ERROR' %d" % (exc, tb, err))
    out.extend(hits)
    for p in logs:
        if p.endswith("_density.log"):
            for ln in open(p, errors="replace"):
                if "Density % =" in ln:
                    out.append("density: " + ln.split(" : ", 1)[-1].strip())
    runner = os.path.join(OUT, "logs", "%s.%s.log" % (cell, step))
    if os.path.exists(runner):
        for ln in open(runner, errors="replace"):
            if "DRC Check" in ln or "Violated rules" in ln:
                out.append("runner says: " + ln.strip()[:300])
    return out, total, (exc + tb), len(dbs)


def lvs_summary(cell, step, subdir):
    d = os.path.join(OUT, cell, subdir)
    out = []
    for rc, t, cmd in runtime(cell, step):
        out.append("command: %s\nexit code: %s, wall time: %s" % (cmd, rc.replace("rc=", ""), t))
    dbs = sorted(glob.glob(os.path.join(d, "*.lvsdb")))
    verdict = None
    for p in sorted(glob.glob(os.path.join(d, "*.log"))):
        for ln in open(p, errors="replace"):
            if re.search(r"Netlists match|Netlists don't match|Devices to compare|strict port mode|port mismatch", ln):
                out.append("log %s: %s" % (os.path.basename(p), ln.strip()[:250]))
                if "Congratulations! Netlists match" in ln:
                    verdict = "match"
                elif "Netlists don't match" in ln:
                    verdict = "no match"
    if not dbs:
        out.append("NO .lvsdb produced in %s" % rel(d))
        return out, "no result", None
    lvs = kdb.LayoutVsSchematic()
    lvs.read(dbs[0])
    xr = lvs.xref()
    top_dev = None
    S = kdb.NetlistCrossReference
    for cp in xr.each_circuit_pair():
        a, b = cp.first(), cp.second()
        dev = list(xr.each_device_pair(cp))
        nets = list(xr.each_net_pair(cp))
        pins = list(xr.each_pin_pair(cp))
        subs = list(xr.each_subcircuit_pair(cp))
        bad = lambda L: [x for x in L if x.status() not in (S.Match, S.MatchWithWarning)]
        out.append("circuit %s / %s: %s; device pairs %d (not matching %d), net pairs %d (not matching %d, with warning %d), "
                   "pin pairs %d (not matching %d), subcircuit pairs %d (not matching %d)" % (
                       a.name if a else "-", b.name if b else "-", cp.status(), len(dev), len(bad(dev)), len(nets),
                       len(bad(nets)), len([x for x in nets if x.status() == S.MatchWithWarning]), len(pins),
                       len(bad(pins)), len(subs), len(bad(subs))))
        for x in bad(pins)[:20]:
            out.append("    pin %s / %s: %s" % (x.first().expanded_name() if x.first() else "-",
                                                x.second().expanded_name() if x.second() else "-", x.status()))
        for x in bad(nets)[:20]:
            out.append("    net %s / %s: %s" % (x.first().expanded_name() if x.first() else "-",
                                                x.second().expanded_name() if x.second() else "-", x.status()))
        for x in bad(dev)[:20]:
            out.append("    device %s / %s: %s" % (x.first().expanded_name() if x.first() else "-",
                                                   x.second().expanded_name() if x.second() else "-", x.status()))
    # devices of the whole extracted layout netlist (flattened count over the hierarchy)
    nl = lvs.netlist()
    top = nl.circuit_by_name(os.path.basename(dbs[0])[:-6])
    if top is not None:
        flat = nl.dup()
        flat.flatten()
        n = sum(1 for c in flat.each_circuit() for _ in c.each_device())
        out.append("layout netlist flattened: %d devices" % n)
        top_dev = n
    keep(dbs[0], "%s.%s.%s" % (cell, step, os.path.basename(dbs[0])), copy=(step == "lvs"))
    exc, tb, err, hits = log_scan(sorted(glob.glob(os.path.join(d, "*.log"))))
    out.append("log lines: 'exception' %d, 'Traceback' %d, 'ERROR' %d" % (exc, tb, err))
    out.extend(hits)
    return out, verdict, top_dev


def magic_drc_summary(cell):
    out = []
    for rc, t, cmd in runtime(cell, "magicdrc"):
        out.append("command: %s\nexit code: %s, wall time: %s" % (cmd, rc.replace("rc=", ""), t))
    rpts = glob.glob(os.path.join(OUT, cell, "magic_drc", "*.magic.drc", "*.magic.drc.rpt"))
    if not rpts:
        out.append("NO magic DRC report")
        return out, None
    p = rpts[0]
    txt = open(p, errors="replace").read().splitlines()
    count = None
    types = []
    for i, ln in enumerate(txt):
        m = re.search(r"COUNT: (\d+)", ln)
        if m:
            count = int(m.group(1))
        if i > 1 and i + 1 < len(txt) and txt[i + 1].startswith("-----") and not ln.startswith(" ") and not ln.startswith("---"):
            types.append(ln)
    out.append("report %s: COUNT %s" % (rel(p), count))
    for t in types:
        n = 0
        j = txt.index(t) + 2
        while j < len(txt) and txt[j].startswith(" "):
            n += 1
            j += 1
        out.append("    %5d  %s" % (n, t[:160]))
    keep(p, "%s.magicdrc.%s" % (cell, os.path.basename(p)))
    log = glob.glob(os.path.join(OUT, cell, "magic_drc", "*.magic.drc", "*.magic.drc.log"))
    if log:
        keep(log[0], "%s.magicdrc.%s" % (cell, os.path.basename(log[0])))
    return out, count


def netgen_summary(cell):
    out = []
    for rc, t, cmd in runtime(cell, "netgen"):
        out.append("command: %s\nexit code: %s, wall time: %s" % (cmd, rc.replace("rc=", ""), t))
    if cell == "slot_7":
        rpt = os.path.join(OUT, cell, "netgen", "comp_slot_7.out")
        extra = [os.path.join(OUT, cell, "netgen", f) for f in ("magic.log", "netgen.log")]
    else:
        rpt = (glob.glob(os.path.join(OUT, cell, "magic_lvs", "*.magic.lvs", "*.lvs.out")) or [""])[0]
        extra = glob.glob(os.path.join(OUT, cell, "magic_lvs", "*.magic.lvs", "*.lvs.log"))
    if not rpt or not os.path.exists(rpt):
        out.append("NO netgen report")
        return out, None
    txt = open(rpt, errors="replace").read().splitlines()
    final = [ln.strip() for ln in txt if "Final result" in ln]
    res = {}
    for ln in txt:
        for key in ("Circuits match uniquely", "Netlists match uniquely", "Netlists do not match",
                    "Netlists match with", "match uniquely with port errors", "Top level cell failed pin matching",
                    "Property errors were found", "Cells have no pins"):
            if key in ln:
                res[ln.strip()] = res.get(ln.strip(), 0) + 1
                break
    out.append("report %s" % rel(rpt))
    for k, v in res.items():
        out.append("    %3d x  %s" % (v, k[:160]))
    for f in final:
        out.append("    " + f)
    # pin tables: rows flagged "**Mismatch**" (netgen cuts the flag at the column width, so match "**Mis")
    # are pins matched under different names; "(no matching pin)" is a pin without a partner
    mism = [ln.rstrip() for ln in txt if "**Mis" in ln or "no matching pin" in ln]
    out.append("pin-table rows: %d flagged '**Mismatch**' (same net, different pin names), %d '(no matching pin)'" % (
        sum(1 for m in mism if "**Mis" in m), sum(1 for m in mism if "no matching pin" in m)))
    out.extend("    " + m[:200] for m in mism[:20])
    # device / net counts of each compared cell
    for ln in txt:
        if re.match(r"^(Circuit [12] contains|Number of devices|Number of nets)", ln.strip()):
            out.append("    " + ln.strip())
    keep(rpt, "%s.netgen.%s" % (cell, os.path.basename(rpt)))
    for e in extra:
        if os.path.exists(e):
            exc = sum(1 for ln in open(e, errors="replace") if re.search(r"error|unknown layer|context", ln, re.I))
            out.append("log %s: %d lines with error / unknown layer / context" % (rel(e), exc))
            for ln in open(e, errors="replace"):
                if re.search(r"error|unknown layer|context", ln, re.I):
                    out.append("    " + ln.rstrip()[:200])
            keep(e, "%s.netgen.%s" % (cell, os.path.basename(e)))
    return out, final


HDR = "# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n"


def write(name, out):
    with open(os.path.join(SUM, name), "w") as f:
        f.write(HDR + "# written by summarize.py from the run directory of run_signoff.sh\n")
        f.write("\n".join(out) + "\n")
    lines_all.append("=== %s" % name)
    lines_all.extend(out)
    lines_all.append("")


table = []
for cell in CELLS:
    if not os.path.isdir(os.path.join(OUT, cell)):
        continue
    for step, sub in (("drc", "klayout_drc"), ("maxlu", "klayout_maximal_lu"), ("density", "klayout_density")):
        if os.path.isdir(os.path.join(OUT, cell, sub)):
            out, total, exc, ndb = drc_summary(cell, step, sub)
            write("%s.%s.txt" % (cell, step), out)
            table.append("%s\t%s\t%d report(s)\t%d violations\t%d exception/Traceback log lines" % (cell, step, ndb, total, exc))
    for step, sub in (("lvs", "klayout_lvs"), ("lvs_spice_as_given", "klayout_lvs_spice_as_given")):
        if os.path.isdir(os.path.join(OUT, cell, sub)):
            out, verdict, ndev = lvs_summary(cell, step, sub)
            write("%s.%s.txt" % (cell, step), out)
            table.append("%s\t%s\t%s\t%s devices (layout, flattened)" % (cell, step, verdict, ndev))
    if os.path.isdir(os.path.join(OUT, cell, "magic_drc")):
        out, count = magic_drc_summary(cell)
        write("%s.magicdrc.txt" % cell, out)
        table.append("%s\tmagicdrc\tCOUNT %s" % (cell, count))
    if os.path.isdir(os.path.join(OUT, cell, "netgen")) or os.path.isdir(os.path.join(OUT, cell, "magic_lvs")):
        out, final = netgen_summary(cell)
        write("%s.netgen.txt" % cell, out)
        table.append("%s\tnetgen\t%s" % (cell, "; ".join(final or [])))

for cdl in sorted(glob.glob(os.path.join(OUT, "*", "netlist", "*.cdl"))):
    keep(cdl, "%s.netlist.%s" % (cdl.split(os.sep)[-3], os.path.basename(cdl)))
for p in ("versions.txt", "runtimes.txt"):
    if os.path.exists(os.path.join(OUT, p)):
        shutil.copyfile(os.path.join(OUT, p), os.path.join(SUM, p))
with open(os.path.join(SUM, "files.txt"), "w") as f:
    f.write(HDR)
    f.write("# result file (relative to the run directory)\tbytes\tsha256\tcopied?\n")
    f.write("\n".join(files) + "\n")
with open(os.path.join(SUM, "summary.txt"), "w") as f:
    f.write(HDR + "# one line per check\n" + "\n".join(table) + "\n\n" + "\n".join(lines_all))
print("\n".join(table))
