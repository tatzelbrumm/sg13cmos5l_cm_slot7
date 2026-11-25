# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Shared pieces of the ESD / latch-up study (IHP sg13cmos5l simulation, ngspice-47 + IHP OSDI models):
netlist preparation (ammeters in the pad netlists, antenna-diode model variants, the IO-library supply cells with the
172-finger clamp lumped as m = 172), the pad-ring model, the ngspice runner (one process at a time), a raw-file
reader and a flattener of the pad netlists (device terminals for the oxide / junction stress tables)."""
import csv
import os
import re
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SLOT = HERE.parents[2]
PDK_ROOT = os.environ.get('PDK_ROOT', '/foss/pdks')
PDK = os.path.join(PDK_ROOT, os.environ.get('PDK', 'ihp-sg13cmos5l'))
MODELS = os.path.join(PDK, 'libs.tech/ngspice/models')
IOLIB = os.path.join(PDK, 'libs.ref/sg13cmos5l_io/spice/sg13cmos5l_io.spice')
S2D = 'sg13cmos5l_IOPadSingle2Diff'
D2S = 'sg13cmos5l_IOPadDiff2Single'
SPDX = '* SPDX-FileCopyrightText: 2026 Christoph Maier\n* SPDX-License-Identifier: Apache-2.0\n'
CSV_HEAD = '# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n'
LABEL = 'IHP sg13cmos5l simulation (ngspice, PDK models; not ESD-calibrated)'

# Ammeters inserted into copies of the pad netlists: (subckt, instance, terminal index, label).
# Each 0 V source sits between the named terminal's node and the device; current is positive INTO the device from
# that node (for a diode on the pad: from the pad into the diode).
AMMETERS = {
    S2D: [('s2d_pad_esd', 'XDP1', 0, 'DP1'), ('s2d_pad_esd', 'XDP2', 0, 'DP2'),
          ('s2d_pad_esd', 'XDN1', 1, 'DN1'), ('s2d_pad_esd', 'XDN2', 1, 'DN2'),
          ('s2d_pad_esd', 'XMCP', 0, 'MCP'), ('s2d_pad_esd', 'XMCN', 0, 'MCN')],
    D2S: [(D2S, 'XDP0', 0, 'DP0'), (D2S, 'XDP1', 0, 'DP1'), (D2S, 'XDN0', 1, 'DN0'), (D2S, 'XDN1', 1, 'DN1'),
          ('d2s_out_p', 'XOP', 0, 'OP'), ('d2s_out_n', 'XON', 0, 'ON'),
          ('d2s_sp2k', 'XR0', 0, 'SP_R'), ('d2s_sp2k', 'XD0', 0, 'SP_DP'), ('d2s_sp2k', 'XD1', 1, 'SP_DN')],
}
# ngspice branch-current vectors of those ammeters, per pad (hierarchical names of the testbench, see build_tb)
def ammeter_vectors(cell, inst='xpad'):
    out = {}
    for sub, dev, _, lab in AMMETERS[cell]:
        if sub == cell:
            path = f'{inst}'
        elif sub == 's2d_pad_esd':
            path = f'{inst}.xp'
        elif sub == 'd2s_out_p':
            path = f'{inst}.xfp'
        elif sub == 'd2s_out_n':
            path = f'{inst}.xfn'
        elif sub == 'd2s_sp2k':
            for k in ('xspa', 'xspb'):
                out[f'{lab}_{k[-1].upper()}'] = f'v.{inst}.{k}.vam_{lab.lower()}#branch'
            continue
        out[lab] = f'v.{path}.vam_{lab.lower()}#branch'
    return out


# Diode sizes on the pad (l, w in um; from the pad netlists), for current density
DIODES = {
    S2D: {'DP1': ('dpantenna', 27.78, 1.26), 'DP2': ('dpantenna', 27.78, 1.26),
          'DN1': ('dantenna', 27.78, 1.26), 'DN2': ('dantenna', 27.78, 1.26)},
    D2S: {'DP0': ('dpantenna', 65.8, 1.26), 'DP1': ('dpantenna', 65.8, 1.26),
          'DN0': ('dantenna', 67.6, 1.26), 'DN1': ('dantenna', 67.6, 1.26),
          'SP_DP_A': ('dpantenna', 4.98, 0.64), 'SP_DP_B': ('dpantenna', 4.98, 0.64),
          'SP_DN_A': ('dantenna', 3.1, 0.64), 'SP_DN_B': ('dantenna', 3.1, 0.64)},
}


def _split_inst(line):
    return line.split()


def add_ammeters(text, cell):
    """Insert the AMMETERS of `cell` into its netlist text (subckt bodies)."""
    lines = text.split('\n')
    out = []
    cur = None
    todo = {(s, d): (t, lab) for s, d, t, lab in AMMETERS[cell]}
    done = set()
    for ln in lines:
        m = re.match(r'^\.subckt\s+(\S+)', ln, re.I)
        if m:
            cur = m.group(1)
        if re.match(r'^\.ends', ln, re.I):
            cur = None
        w = ln.split()
        if cur and w and (cur, w[0]) in todo:
            t, lab = todo[(cur, w[0])]
            node = w[1 + t]
            new = f'{node}_am_{lab.lower()}'
            w[1 + t] = new
            out.append(' '.join(w))
            out.append(f'Vam_{lab.lower()} {node} {new} 0')
            done.add((cur, w[0]))
            continue
        out.append(ln)
    missing = set(todo) - done
    if missing:
        raise RuntimeError(f'ammeters not placed: {missing}')
    return '\n'.join(out)


DIODE_VARIANTS = {
    'pdk': 'PDK diodes.lib dantenna / dpantenna as they are (fitted for the reverse direction, -15 ... 1 V; '
           'series resistance 2.19e5 Ohm um^2 / area, high-injection knee 0.14 uA/um^2)',
    'esdproxy': 'antenna diodes re-modeled with the PDK ESD-diode models diodevss_mod / diodevdd_mod of '
                'sg13g2_esd.lib (series resistance 200 / 289.6 Ohm um^2 / area), area = l w; a proxy, not a '
                'calibrated model of these diodes',
}


def diode_lib(work, variant):
    """Path of the antenna-diode library for `variant` (written into the work dir)."""
    if variant == 'pdk':
        return os.path.join(MODELS, 'diodes.lib')
    p = Path(work).resolve() / "net" / "diodes_esdproxy.lib"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(SPDX + """* dantenna / dpantenna re-modeled with the PDK's ESD diode models (sg13g2_esd.lib, shipped with ihp-sg13cmos5l):
* n+/p-sub (dantenna) -> diodevss_mod, p+/n-well (dpantenna) -> diodevdd_mod, area = l*w in um^2.
* A proxy for an ESD-capable forward characteristic; NOT a calibrated model of the antenna diodes.
.include %s/sg13g2_esd.lib
.subckt dantenna 1 2
.params l=780n w=780n DEV_A=(l*w)/1p DEV_P=2*(l+w)/1u
D1 1 2 diodevss_mod area=DEV_A pj=DEV_P
.ends dantenna
.subckt dpantenna 1 2
.params l=780n w=780n DEV_A=(l*w)/1p DEV_P=2*(l+w)/1u
D1 1 2 diodevdd_mod area=DEV_A pj=DEV_P
.ends dpantenna
""" % MODELS)
    return str(p)


def prep_netlists(work):
    """Pad netlists with ammeters and the IO library with the clamp lumped; returns dict of paths."""
    net = Path(work).resolve() / "net"
    net.mkdir(parents=True, exist_ok=True)
    paths = {}
    for cell in (S2D, D2S):
        src = (SLOT / 'pads' / cell / f'{cell}.spice').read_text()
        (net / f'{cell}_am.spice').write_text(SPDX + '* copy of pads/%s/%s.spice with 0 V ammeters (common.py)\n' %
                                              (cell, cell) + add_ammeters(src, cell))
        paths[cell] = str(net / f'{cell}_am.spice')
    io = Path(IOLIB).read_text().split('\n')
    out, insub = [], False
    for ln in io:
        if ln.startswith('.subckt sg13cmos5l_Clamp_N43N43D4R'):
            insub = True
        if insub and ln.startswith('XN0['):
            if ln.startswith('XN0[1] '):
                out.append(ln.replace(' m=1', ' m=172'))
            continue
        if insub and ln.startswith('.ends'):
            insub = False
        out.append(ln)
    out = _local_substrate(out)
    (net / 'sg13cmos5l_io_lumped.spice').write_text(
        SPDX + '* copy of the PDK sg13cmos5l_io.spice; Clamp_N43N43D4R: its 172 identical fingers as one instance '
               'with m=172; the substrate node sub! of the supply cells IOPadIOVdd / IOPadIOVss passed to their '
               'sub-cells as a port "sub" (one local substrate node per supply cell, tied to its iovss by the '
               "library's ptap1 resistors) (common.py)\n" + '\n'.join(out))
    paths['io'] = str(net / 'sg13cmos5l_io_lumped.spice')
    return paths


IO_CHILDREN = ('sg13cmos5l_Clamp_N43N43D4R', 'sg13cmos5l_RCClampResistor', 'sg13cmos5l_RCClampInverter',
               'sg13cmos5l_DCNDiode', 'sg13cmos5l_DCPDiode')
IO_PARENTS = ('sg13cmos5l_IOPadIOVdd', 'sg13cmos5l_IOPadIOVss')


def _local_substrate(lines):
    """In the IO library, sub! is meant as a global node; ngspice keeps it local to every sub-cell, which leaves
    the sub-cells' substrate floating. Pass it down as a port instead (supply cells and their sub-cells only)."""
    out, cur = [], None
    for ln in lines:
        w = ln.split()
        if w and w[0] == '.subckt':
            cur = w[1]
            if cur in IO_CHILDREN:
                ln = ln.rstrip() + ' sub'
        elif w and w[0].startswith('.ends'):
            cur = None
        elif cur in IO_CHILDREN + IO_PARENTS and w and w[0][0] in 'XxDdRr':
            if cur in IO_PARENTS and w[-1] in IO_CHILDREN:
                w = w[:-1] + ['sub', w[-1]]
            ln = ' '.join(t if t != 'sub!' else 'sub' for t in w)
        out.append(ln)
    return out


def model_block(corner='tt', variant='pdk', work='.'):
    return f""".lib {MODELS}/cornerMOShv.lib mos_{corner}
.lib {MODELS}/cornerMOSlv.lib mos_{corner}
.lib {MODELS}/cornerRES.lib res_typ
.lib {MODELS}/cornerCAP.lib cap_typ
.include {diode_lib(work, variant)}
"""


# ----------------------------------------------------------------------------------------------------------------
# pad ring
def read_ring():
    rper = {}
    for ln in open(HERE / 'csv/ring_metal.csv'):
        m = re.match(r'# resistance per um: iovdd (\S+) mOhm/um, iovss (\S+) mOhm/um', ln)
        if m:
            rper = {'iovdd': float(m.group(1)) * 1e-3, 'iovss': float(m.group(2)) * 1e-3}
    rows = [r for r in csv.DictReader(l for l in open(HERE / 'csv/ring_cells.csv') if not l.startswith('#'))]
    return rper, rows


def ring_netlist(mode, vsup=3.6, ring_scale=1.0):
    """Pad-ring subcircuit text. Nodes: iovdd / iovss of the S2D pad = vd_s2d / vs_s2d, of the D2S = vd_d2s /
    vs_d2s. mode: 'gnd_vss' (IOVss bond pads at 0 V, iovdd floating), 'gnd_vdd' (IOVdd bond pads at 0 V, iovss
    floating), 'float' (no supply pad connected), 'powered' (IOVdd pads at vsup, IOVss pads at 0 V).
    Each supply bond pad connects through a 0 V ammeter Vbp_<inst>; each IOVdd cell's iovdd through Vcl_<inst>."""
    rper, rows = read_ring()
    # the ring nodes: IOVdd / IOVss supply cells and the two slot-7 pads (the 1.2 V IOPadVdd / IOPadVss cells,
    # corners and splitters carry the iovdd / iovss ring through but put no device on it in this model)
    rows = [r for r in rows if r['cell'] in ('sg13cmos5l_IOPadIOVdd', 'sg13cmos5l_IOPadIOVss', S2D, D2S)]
    total = 10120.0
    nodes = []
    for r in rows:
        tag = {S2D: 's2d', D2S: 'd2s'}.get(r['cell'], r['instance'].replace('pad_', ''))
        nodes.append((float(r['s_um']), tag, r['cell'], r['instance']))
    nodes.sort()
    L = ['* pad ring: iovdd / iovss loops, resistance per um from csv/ring_metal.csv (x %g)' % ring_scale]
    n = len(nodes)
    for i in range(n):
        s0, t0 = nodes[i][0], nodes[i][1]
        s1, t1 = (nodes[i + 1][0], nodes[i + 1][1]) if i + 1 < n else (nodes[0][0] + total, nodes[0][1])
        d = s1 - s0
        L.append(f'Rrd_{t0}_{t1} vd_{t0} vd_{t1} {rper["iovdd"] * d * ring_scale:.6g}')
        L.append(f'Rrs_{t0}_{t1} vs_{t0} vs_{t1} {rper["iovss"] * d * ring_scale:.6g}')
    L.append('Vcore vcore 0 0')   # the 1.2 V core ring pins of the supply cells (unused by their devices)
    for s, tag, cell, inst in nodes:
        if cell == 'sg13cmos5l_IOPadIOVdd':
            L.append(f'Vcl_{tag} vd_{tag} vdc_{tag} 0')
            L.append(f'X{tag} vcore vs_{tag} vdc_{tag} vs_{tag} sg13cmos5l_IOPadIOVdd')
            if mode == 'gnd_vdd':
                L.append(f'Vbp_{tag} vd_{tag} 0 0')
            elif mode == 'powered':
                L.append(f'Vbp_{tag} vd_{tag} vsup 0')
        elif cell == 'sg13cmos5l_IOPadIOVss':
            L.append(f'X{tag} vcore vs_{tag} vd_{tag} vs_{tag} sg13cmos5l_IOPadIOVss')
            if mode in ('gnd_vss', 'powered'):
                L.append(f'Vbp_{tag} vs_{tag} 0 0')
    if mode == 'powered':
        L.append(f'Vsup vsup 0 {vsup}')
    # DC reference for floating rings (1 TOhm; no effect on the transients)
    L.append('Rfl_d vd_s2d 0 1e12')
    L.append('Rfl_s vs_s2d 0 1e12')
    return '\n'.join(L) + '\n', nodes


# ----------------------------------------------------------------------------------------------------------------
# pad instances with their core-side pins
def pad_instance(cell, state, inst='xpad', bias=None):
    """Pad instance line plus its core-side connections.
    state 'unpowered': core-side gate inputs (vref, vcm, vinp, vinn) and en_3v3 at the pad's iovss, en_3v3_b at its
    iovdd (the disabled state the fail-safe enables present), iref / outp / outn open (1 TOhm).
    state 'enabled': en_3v3 = iovdd, en_3v3_b = iovss, iref 5 uA from iovdd, vref / vcm / vinp / vinn ideal sources
    against the pad's iovss (bias dict)."""
    t = 's2d' if cell == S2D else 'd2s'
    vd, vs = f'vd_{t}', f'vs_{t}'
    pad = f'pad_{t}'
    L = []
    if cell == S2D:
        # iovdd iovss vdd vss pad outp outn vcm vref iref en_3v3 en_3v3_b
        L.append(f'{inst} {vd} {vs} vcore {vs} {pad} {t}_outp {t}_outn {t}_vcm {t}_vref {t}_iref {t}_en {t}_enb {cell}')
        L += [f'Ro_{t}p {t}_outp {vs} 1e12', f'Ro_{t}n {t}_outn {vs} 1e12']
        gates = {'vcm': 1.26, 'vref': 0.49}
    else:
        # iovdd iovss vdd vss pad vinp vinn vref iref en_3v3 en_3v3_b
        L.append(f'{inst} {vd} {vs} vcore {vs} {pad} {t}_vinp {t}_vinn {t}_vref {t}_iref {t}_en {t}_enb {cell}')
        gates = {'vinp': 1.26, 'vinn': 1.26, 'vref': 1.26}
    if bias:
        gates.update(bias)
    if state == 'unpowered':
        for g in gates:
            L.append(f'Vg_{t}_{g} {t}_{g} {vs} 0')
        L += [f'Ven_{t} {t}_en {vs} 0', f'Venb_{t} {t}_enb {vd} 0', f'Ri_{t} {t}_iref {vs} 1e12']
    else:
        for g, v in gates.items():
            L.append(f'Vg_{t}_{g} {t}_{g} {vs} {v}')
        L += [f'Ven_{t} {t}_en {vd} 0', f'Venb_{t} {t}_enb {vs} 0', f'Ii_{t} {vd} {t}_iref 5u']
    return '\n'.join(L) + '\n'


# ----------------------------------------------------------------------------------------------------------------
def run_ngspice(deck_path, log_path, timeout=3600):
    """Run one ngspice batch job (the caller runs them one at a time)."""
    rdir = Path(deck_path).parent
    spi = Path(PDK) / 'libs.tech' / 'ngspice' / '.spiceinit'
    (rdir / '.spiceinit').write_text(spi.read_text())
    env = dict(os.environ, PDK_ROOT=PDK_ROOT, PDK=os.path.basename(PDK))
    with open(log_path, 'w') as lf:
        r = subprocess.run(['ngspice', '-b', Path(deck_path).name], cwd=rdir, stdout=lf, stderr=subprocess.STDOUT,
                           env=env, timeout=timeout)
    return r.returncode


def read_raw(path):
    """ngspice binary raw file -> list of plots, each dict(name, vars: OrderedDict name -> np.array)."""
    data = open(path, 'rb').read()
    plots = []
    pos = 0
    while pos < len(data):
        hdr = {}
        varnames = []
        while True:
            e = data.index(b'\n', pos)
            line = data[pos:e].decode('latin-1')
            pos = e + 1
            if line.startswith('Variables:'):
                nv = int(hdr['No. Variables'])
                for _ in range(nv):
                    e = data.index(b'\n', pos)
                    w = data[pos:e].decode('latin-1').split()
                    pos = e + 1
                    varnames.append(w[1])
                continue
            if line.startswith('Binary:'):
                break
            if ':' in line:
                k, v = line.split(':', 1)
                hdr[k.strip()] = v.strip()
        nv, npnt = int(hdr['No. Variables']), int(hdr['No. Points'])
        cplx = 'complex' in hdr.get('Flags', '')
        dt = np.complex128 if cplx else np.float64
        cnt = nv * npnt
        arr = np.frombuffer(data, dtype=dt, count=cnt, offset=pos).reshape(npnt, nv)
        pos += cnt * np.dtype(dt).itemsize
        plots.append({'name': hdr.get('Plotname', ''), 'vars': {n.lower(): arr[:, i].real if not cplx else arr[:, i]
                                                                  for i, n in enumerate(varnames)}})
    return plots


# ----------------------------------------------------------------------------------------------------------------
PRIMS = {'sg13_hv_nmos': 'nmos', 'sg13_hv_pmos': 'pmos', 'sg13_lv_nmos': 'nmos', 'sg13_lv_pmos': 'pmos',
         'rppd': 'res', 'rhigh': 'res', 'rsil': 'res', 'dantenna': 'dio', 'dpantenna': 'dio'}


def flatten(netlist_text, top, top_nodes, prefix):
    """Flatten `top` of netlist_text with its ports bound to top_nodes; returns list of devices
    dict(name, kind, nodes, params) with ngspice-style lower-case hierarchical node names."""
    subs = {}
    cur = None
    for ln in netlist_text.split('\n'):
        w = ln.split()
        if not w or w[0].startswith('*'):
            continue
        if w[0].lower() == '.subckt':
            cur = w[1]
            subs[cur] = {'ports': [p for p in w[2:] if '=' not in p], 'lines': []}
            continue
        if w[0].lower().startswith('.ends'):
            cur = None
            continue
        if cur and w[0][0] in 'XxVv':
            subs[cur]['lines'].append(w)
    devs = []

    def rec(sub, binding, path):
        for w in subs[sub]['lines']:
            name = w[0].lower()
            if name[0] == 'v':   # ammeter: short its two nodes for the terminal table
                continue
            args = [a for a in w[1:] if '=' not in a]
            params = dict(a.split('=', 1) for a in w[1:] if '=' in a)
            model = args[-1]
            nodes = []
            for a in args[:-1]:
                a0 = re.sub(r'_am_[a-z0-9_]+$', '', a)   # ammeter node: the 0 V source joins it to a0
                nodes.append(binding.get(a0, f'{path}.{a0}'.lower()))
            if model in PRIMS:
                devs.append({'name': f'{path}.{name}', 'kind': PRIMS[model], 'model': model, 'nodes': nodes,
                             'params': params})
            elif model in subs:
                b = dict(zip(subs[model]['ports'], nodes))
                rec(model, b, f'{path}.{name}')
    rec(top, dict(zip(subs[top]['ports'], top_nodes)), prefix)
    return devs


def write_csv(path, rows, comment):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='') as f:
        f.write(CSV_HEAD)
        for c in comment.split('\n'):
            f.write(f'# {c}\n')
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
