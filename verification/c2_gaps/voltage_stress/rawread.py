# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Minimal reader of an ngspice binary raw file (one real plot): read(path) -> (names, scale, data[points, vars])."""
import numpy as np


def read(path):
    with open(path, 'rb') as f:
        buf = f.read()
    k = buf.index(b'Binary:\n')
    head = buf[:k].decode('latin-1').splitlines()
    nv = npt = None
    names = []
    invars = False
    for ln in head:
        if ln.startswith('No. Variables:'):
            nv = int(ln.split(':')[1])
        elif ln.startswith('No. Points:'):
            npt = int(ln.split(':')[1])
        elif ln.startswith('Flags:') and 'complex' in ln:
            raise ValueError('complex raw file not supported')
        elif ln.startswith('Variables:'):
            invars = True
        elif invars and ln.strip():
            names.append(ln.split()[1])
    assert nv == len(names), (nv, len(names))
    data = np.frombuffer(buf, dtype='<f8', offset=k + 8)
    npt = min(npt, data.size // nv)
    data = data[:npt * nv].reshape(npt, nv)
    return names, data[:, 0], data
