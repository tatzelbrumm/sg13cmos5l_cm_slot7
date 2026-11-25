# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Latch-up-relevant geometry of the two pad cells, read from pads/<cell>/<cell>.gds with KLayout (no simulation):
the guard rings of the ESD sub-cells and the distances that set the parasitic bipolar paths:
  d_np_inj   : n+ in p-substrate of the ESD N cells (dantenna stripes, clamp NMOS) -> nearest core n-well that holds
               p+ diffusion (a PMOS well outside the ESD cells: the "victim" that collects injected electrons)
  d_pn_inj   : n-well of the ESD P cells (holes injected by the pad p+) -> nearest n+ in p-substrate outside the
               ESD cells (core NMOS: emitter of the parasitic NPN)
  d_scr      : n+ in p-substrate of the ESD N cells -> n-well of the ESD P cells (the clamp pair's own PNPN)
plus the widths of the guard rings. Layers (IHP sg13cmos5l): Activ 1/0, GatPoly 5/0, nSD 7/0, pSD 14/0, NWell 31/0.
Usage: python3 lu_geometry.py <out_dir>   -> <out_dir>/csv/lu_geometry.csv, <out_dir>/plots/lu_layout_<pad>.png"""
import os
import sys

import klayout.db as db
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SLOT = os.path.abspath(os.path.join(HERE, '../../..'))
PADS = {'s2d': 'sg13cmos5l_IOPadSingle2Diff', 'd2s': 'sg13cmos5l_IOPadDiff2Single'}
N_CELLS = ('DCNDiode', 'Clamp_N_M1')
P_CELLS = ('DCPDiode', 'Clamp_P_M1')


def regions(ly, cell, trans=None):
    def r(l, d=0):
        reg = db.Region(cell.begin_shapes_rec(ly.layer(l, d)))
        if trans is not None:
            reg = reg.transformed(trans)
        return reg.merged()
    act, gp, psd, nw = r(1), r(5), r(14), r(31)
    diff = act - gp
    return {'nw': nw, 'pplus': diff & psd, 'nplus': diff - psd}


def min_dist(a, b, dbu, maxd=200.0):
    if a.is_empty() or b.is_empty():
        return float('nan')
    ep = a.separation_check(b, int(maxd / dbu), False, db.Metrics.Euclidian)
    ds = [e.distance() for e in ep.each()]
    inter = not (a & b).is_empty()
    if inter:
        return 0.0
    return min(ds) * dbu if ds else float('nan')


def analyze(pad, cell_name):
    ly = db.Layout()
    ly.read(os.path.join(SLOT, 'pads', cell_name, f'{cell_name}.gds'))
    top = ly.top_cell()
    dbu = ly.dbu
    allr = regions(ly, top)
    esd_n = {'nw': db.Region(), 'pplus': db.Region(), 'nplus': db.Region()}
    esd_p = {'nw': db.Region(), 'pplus': db.Region(), 'nplus': db.Region()}
    esd_box = db.Region()
    rings = []
    for inst in top.each_inst():
        nm = inst.cell.name
        if nm.startswith(N_CELLS) or nm.startswith(P_CELLS):
            rr = regions(ly, inst.cell, inst.cplx_trans)
            tgt = esd_n if nm.startswith(N_CELLS) else esd_p
            for k in tgt:
                tgt[k] += rr[k]
            esd_box += db.Region(inst.bbox())
            # ring widths: n-well ring of N cells / p+ ring around P cells (outermost diffusion ring)
            nwr = rr['nw']
            for p in nwr.each():
                holes = p.holes()
                rings.append(dict(pad=pad, cell=nm, origin=str(inst.dcplx_trans.disp),
                                  nwell_bbox=str(p.bbox().to_dtype(dbu)), nwell_is_ring=holes > 0,
                                  nwell_ring_width_um=round(_ring_width(p, dbu), 3) if holes else '',
                                  pplus_rings=sum(1 for q in rr['pplus'].each() if q.holes() > 0),
                                  nplus_rings=sum(1 for q in rr['nplus'].each() if q.holes() > 0)))
    for k in esd_n:
        esd_n[k] = esd_n[k].merged()
        esd_p[k] = esd_p[k].merged()
    esd_box = esd_box.merged()
    # n+ in p-substrate of the N cells (device stripes, not the n+ well ties of the guard ring)
    n_inj = esd_n['nplus'] - esd_n['nw']
    # n-well guard rings of the N cells: the N cells' own n-wells
    victim_nw = allr['nw'] - esd_n['nw']
    victim_nw_core = allr['nw'] - esd_box
    core_nplus = (allr['nplus'] - allr['nw']) - esd_box
    p_well = esd_p['nw']
    # core PMOS wells: n-well polygons outside the ESD cells that hold p+ diffusion (PNP emitters at iovdd or signal)
    core_pmos_nw = (victim_nw_core.interacting(allr['pplus'] - esd_box)).merged()
    res = dict(pad=pad,
               d_np_inj_to_core_pmos_nwell_um=min_dist(n_inj, core_pmos_nw, dbu),
               d_pwell_esd_to_core_nplus_um=min_dist(p_well, core_nplus, dbu),
               d_scr_esd_nplus_to_esd_pwell_um=min_dist(n_inj, p_well, dbu),
               area_n_inj_um2=round(n_inj.area() * dbu ** 2, 1), area_esd_pwell_um2=round(p_well.area() * dbu ** 2, 1))
    return res, rings, (ly, top, allr, esd_box)


def _ring_width(p, dbu):
    """Width of a ring polygon (hull minus largest hole), from areas and perimeters: w ~ A / (P_mean / 1)."""
    hull = db.Polygon(list(p.each_point_hull()))
    hole = max((db.Polygon(list(p.each_point_hole(i))) for i in range(p.holes())), key=lambda q: q.area())
    a = hull.area() - hole.area()
    per = 0.5 * (hull.perimeter() + hole.perimeter())
    return a / per * dbu


def plot(pad, ly, top, allr, esd_box, outdir, ylim):
    dbu = ly.dbu
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    styles = [('nw', '#2a78d6', 0.18, 'NWell'), ('pplus', '#eb6834', 0.55, 'p+ Activ'),
              ('nplus', '#1baf7a', 0.55, 'n+ Activ')]
    box = db.Box(int(-1 / dbu), int(ylim[0] / dbu), int(81 / dbu), int(ylim[1] / dbu))
    for k, col, alpha, lab in styles:
        first = True
        for p in (allr[k] & db.Region(box)).each():
            for poly in db.Region(p).decompose_trapezoids_to_region().each() if p.holes() else [p]:
                pts = [(q.x * dbu, q.y * dbu) for q in poly.each_point_hull()]
                ax.add_patch(MPoly(pts, closed=True, fc=col, ec='none', alpha=alpha, label=lab if first else None))
                first = False
    for p in esd_box.each():
        b = p.bbox()
        ax.add_patch(plt.Rectangle((b.left * dbu, b.bottom * dbu), b.width() * dbu, b.height() * dbu, fill=False,
                                   ec='#52514e', lw=0.6, ls='--'))
    ax.set_xlim(-1, 81)
    ax.set_ylim(*ylim)
    ax.set_aspect('equal')
    ax.set_xlabel('x (um)')
    ax.set_ylabel('y (um)')
    ax.set_title(f'{PADS[pad]}: wells and diffusions of the ESD region (dashed: ESD sub-cells)\n'
                 f'layout read from pads/{PADS[pad]}/{PADS[pad]}.gds', fontsize=8.5)
    ax.legend(loc='upper right', fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, 'plots', f'lu_layout_{pad}.png'), dpi=150)
    plt.close(fig)


def main():
    out = sys.argv[1]
    os.makedirs(os.path.join(out, 'csv'), exist_ok=True)
    os.makedirs(os.path.join(out, 'plots'), exist_ok=True)
    rows, rings = [], []
    for pad, cell in PADS.items():
        r, rg, (ly, top, allr, esd_box) = analyze(pad, cell)
        rows.append(r)
        rings += rg
        plot(pad, ly, top, allr, esd_box, out, (0, 100))
    with open(os.path.join(out, 'csv/lu_geometry.csv'), 'w') as f:
        f.write('# SPDX-FileCopyrightText: 2026 Christoph Maier\n# SPDX-License-Identifier: Apache-2.0\n')
        f.write('# latch-up geometry of the pad cells (KLayout, pads/<cell>/<cell>.gds); distances edge to edge\n')
        f.write(','.join(rows[0].keys()) + '\n')
        for r in rows:
            f.write(','.join(str(round(v, 3)) if isinstance(v, float) else str(v) for v in r.values()) + '\n')
        f.write('#\n# guard rings of the ESD sub-cells\n')
        f.write(','.join(rings[0].keys()) + '\n')
        for r in rings:
            f.write(','.join(str(v).replace(',', ' ') for v in r.values()) + '\n')
    for r in rows:
        print(r)


if __name__ == '__main__':
    main()
