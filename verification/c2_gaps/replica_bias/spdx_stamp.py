#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Prepend the SPDX header to generated text files (.csv: '#' lines, .md: HTML comment, .spice: '*' lines), unless
present. Readers of the CSVs here skip lines that start with '#'.
Usage: spdx_stamp.py <file> [<file> ...]"""
import sys
C, L = 'SPDX-FileCopyrightText: 2026 Christoph Maier', 'SPDX-License-Identifier: Apache-2.0'
for p in sys.argv[1:]:
    s = open(p).read()
    if 'SPDX-License-Identifier' in s[:400]:
        continue
    if p.endswith('.md'):
        h = '<!--\n%s\n%s\n-->\n' % (C, L)
    elif p.endswith('.spice'):
        h = '* %s\n* %s\n' % (C, L)
    else:
        h = '# %s\n# %s\n' % (C, L)
    open(p, 'w').write(h + s)
