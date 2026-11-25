#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Prepare the extracted netlists for simulation (IHP sg13cmos5l, magic PEX of the taped-out slot_7 and pads).

Usage: python3 -I prep.py <work_dir>
Reads  <work_dir>/x_slot_7/{c,rc}/slot_7.pex.spice   magic C-coupled / full-RC extraction of final/gds/slot_7.gds
       <work_dir>/x_<cell>/{c,rc}/<cell>.pex.spice     the same for the two pad cells (extract.sh)
       the C-coupled pad netlists of the earlier slot runs (S2D: design repository 91a7da8b
       netlist/pex/<cell>_magic_pex_2.spice; D2S: ../d2s_pex/<cell>_magic_pex_2.spice; sak-pex.sh -m 2)
Writes <work_dir>/nets/slot_7_{c,rc}.spice and <work_dir>/nets/<cell>_{prev,c,rc}.spice.

Slot: the extracted subckt is renamed slot_7_x; nodes that only capacitors touch (the floating GatPoly / metal of
tughra_art and of unused pins) get 1 Tohm to vss_3v3 (scripts/cace/pex_for_sim.py --tie, as the pads); a wrapper
.subckt slot_7 with the port order of the source netlist (design repository 9052bd35, macros/slot_7/netlist/source/
slot_7.spice, which the earlier slot decks instantiate) maps the ports by name. Where the layout makes several source
ports one net (C extraction: analog_bus2 = s7_an_0_vcm = s7_an_1_vref, analog_bus3 = s7_an_0_vref, the two pads' en /
en_b), the wrapper joins them by 0 V sources, as the source netlist does (its Vs* joins). Harness pins the slot does not
use (dig_in[6..23], clk, reset, ibias0/1, vbias; no device on them, netgen: disconnected) are tied to vss_3v3;
vss_1v2_uq0 (the frame's second vss_1v2 strip, joined by the harness) to vss_1v2.
Pads (c, rc): as ../d2s_pex/run.sh for the C view: vss port added and tied to iovss by 1 Ohm (pex_add_port.py),
ports in symbol order, capacitor-only nodes 1 Tohm to iovss (pex_for_sim.py --tie iovss 1e12), subckt named as the cell.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLOT = HERE.parents[2]
WORK = Path(sys.argv[1]).resolve()
NETS = WORK / 'nets'
SCR = WORK / 'design' / 'scripts'
S2D, D2S = 'sg13cmos5l_IOPadSingle2Diff', 'sg13cmos5l_IOPadDiff2Single'
PAD_PORTS = {S2D: 'iovdd iovss vdd vss pad outp outn vcm vref iref en_3v3 en_3v3_b',
             D2S: 'iovdd iovss vdd vss pad vinp vinn vref iref en_3v3 en_3v3_b'}
SRC_PORTS = ('vdd_3v3 vss_3v3 enable dig_in0 dig_in1 dig_in2 dig_in3 dig_in4 dig_in5 analog_bus0 analog_bus1 analog_bus2 '
             'analog_bus3 s7_an_0_vref s7_an_0_outp s7_an_0_outn s7_an_0_vcm s7_an_0_en_3v3 s7_an_0_en_3v3_b '
             's7_an_0_iref s7_an_1_vinp s7_an_1_vinn s7_an_1_vref s7_an_1_iref s7_an_1_en_3v3_b s7_an_1_en_3v3 '
             + ' '.join(f'dig_out{i}' for i in range(12)) + ' vdd_1v2 vss_1v2').split()
# one net in the layout (netlist/slot_7.cdl, port mode 'comma'); the first name that the extraction keeps as a port is used
GROUPS = [['s7_an_0_vcm', 'analog_bus2', 's7_an_1_vref'], ['analog_bus3', 's7_an_0_vref'],
          ['s7_an_1_en_3v3', 's7_an_0_en_3v3'], ['s7_an_1_en_3v3_b', 's7_an_0_en_3v3_b']]
SPDX = '* SPDX-FileCopyrightText: 2026 Christoph Maier\n* SPDX-License-Identifier: Apache-2.0\n'


def subckt_ports(txt, name):
    t = txt.replace('\n+', ' ')
    m = re.search(r'^\.subckt\s+' + re.escape(name) + r'\s+(.*)$', t, re.M | re.I)
    return m.group(1).split()


def ext_name(p):
    """source port name -> extracted name (dig_in0 -> dig_in[0])"""
    m = re.fullmatch(r'(dig_in|dig_out)(\d+)', p)
    return f'{m.group(1)}[{m.group(2)}]' if m else p


def slot(view):
    src = WORK / 'x_slot_7' / view / 'slot_7.pex.spice'
    tied = NETS / f'slot_7_{view}_x.spice'
    r = subprocess.run([sys.executable, '-I', str(SCR / 'cace' / 'pex_for_sim.py'), str(src), str(tied),
                        '--tie', 'vss_3v3', '1e12'], capture_output=True, text=True, check=True)
    note = r.stdout.strip()
    txt = tied.read_text()
    txt = re.sub(r'^(\.subckt\s+)slot_7\b', r'\1slot_7_x', txt, flags=re.M | re.I)
    txt = re.sub(r'^(\.ends\s+)slot_7\b', r'\1slot_7_x', txt, flags=re.M | re.I)
    xports = subckt_ports(txt, 'slot_7_x')
    conn, joins, k = [], [], 0
    src_set = {ext_name(p) for p in SRC_PORTS}
    rep = {}
    for g in GROUPS:
        keep = [n for n in g if n in xports]
        for n in g:
            if n not in xports:
                rep[n] = keep[0]
    for p in xports:
        if p in src_set:
            conn.append(next(s for s in SRC_PORTS if ext_name(s) == p))
        elif p == 'vss_1v2_uq0':
            conn.append('vss_1v2')
        else:
            conn.append('vss_3v3')  # unused harness pin
    for s in SRC_PORTS:
        e = ext_name(s)
        if e not in xports:
            r_ = rep[e]
            joins.append(f'Vj{k} {next(x for x in SRC_PORTS if ext_name(x) == r_)} {s} 0')
            k += 1
    wrap = (f'* slot_7 wrapper (prep.py): source-netlist port order -> magic extraction ({view}) of final/gds/slot_7.gds\n'
            f'* {note}\n'
            f'.subckt slot_7 {" ".join(SRC_PORTS)}\n'
            f'Xx {" ".join(conn)} slot_7_x\n' + ''.join(j + '\n' for j in joins) + '.ends slot_7\n')
    out = NETS / f'slot_7_{view}.spice'
    out.write_text(SPDX + f'* generated by verification/c2_gaps/slot_pex/prep.py from {src.relative_to(WORK)}\n'
                   + txt + '\n' + wrap)
    tied.unlink()
    print(out, '|', note, '| joins:', joins)


def pad_c(cell):
    """the C-coupled pad netlists of the earlier slot runs, prepared as ../dc_curves/cace_dc.sh does"""
    src = (WORK / 'design' / 'macros' / cell / 'netlist' / 'pex' / f'{cell}_magic_pex_2.spice' if cell == S2D
           else HERE.parent / 'd2s_pex' / f'{cell}_magic_pex_2.spice')
    out = NETS / f'{cell}_prev.spice'
    subprocess.run([sys.executable, '-I', str(SCR / 'cace' / 'pex_for_sim.py'), str(src), str(out), '--tie', 'iovss',
                    '1e12'], check=True)
    out.write_text(re.sub(r'\b' + cell + r'_pex\b', cell, out.read_text()))


def reorder(txt, cell, want):
    """put the .subckt port list into the symbol order (same set of names required)"""
    have = subckt_ports(txt, cell)
    assert sorted(have) == sorted(want), (cell, have, want)
    t = re.sub(r'^(\.subckt\s+' + cell + r'\s).*?(?=\n[^+])', lambda m: m.group(1) + ' '.join(want), txt,
               count=1, flags=re.M | re.S)
    return t


def pad_x(cell, view):
    src = WORK / f'x_{cell}' / view / f'{cell}.pex.spice'
    tmp = NETS / f'{cell}_{view}_raw.spice'
    tmp.write_text(src.read_text())
    subprocess.run([sys.executable, '-I', str(SCR / 'pex_add_port.py'), str(tmp), f'{cell}_pex', 'vss', 'iovss', '1'],
                   check=True)
    out = NETS / f'{cell}_{view}.spice'
    subprocess.run([sys.executable, '-I', str(SCR / 'cace' / 'pex_for_sim.py'), str(tmp), str(out), '--tie', 'iovss',
                    '1e12'], check=True)
    txt = re.sub(r'\b' + cell + r'_pex\b', cell, out.read_text())
    txt = reorder(txt, cell, PAD_PORTS[cell].split())
    out.write_text(SPDX + txt)
    tmp.unlink()
    print(out)


def prb():
    """pad_ref_rb alone (magic C-coupled, cut from slot_7.gds), wrapped to the port order of run_tier1.SRC_PORTS"""
    src = WORK / 'x_pad_ref_rb' / 'pad_ref_rb.pex.spice'
    out = NETS / 'pad_ref_rb_c.spice'
    subprocess.run([sys.executable, '-I', str(SCR / 'cace' / 'pex_for_sim.py'), str(src), str(out), '--tie', 'vssh',
                    '1e12'], check=True)
    txt = out.read_text()
    m = re.search(r'^\.subckt\s+(\S+)\s+(.*)$', txt, re.M | re.I)
    txt = txt.replace(m.group(0), f'.subckt pad_ref_rb_lay {m.group(2)}', 1)
    src_ports = 'vddh vssh iref vcm vref en_3v3 en_3v3_b'
    assert sorted(src_ports.split()) == sorted(m.group(2).split()), m.group(2)
    out.write_text(SPDX + txt + f'\n.subckt pad_ref_rb {src_ports}\nXlay {m.group(2)} pad_ref_rb_lay\n.ends pad_ref_rb\n')
    print(out)


if __name__ == '__main__':
    NETS.mkdir(parents=True, exist_ok=True)
    prb()
    for v in ('c', 'rc'):
        slot(v)
    for c in (S2D, D2S):
        pad_c(c)
        pad_x(c, 'c')
        pad_x(c, 'rc')
