#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Post-process the output of datasheets/tools/make_datasheet.py for the D2S schematic re-run (no numbers change):
1. insert the hand-made '## Figures' section of the current data sheet (its marker says to keep it when
   regenerating) before '## Specification';
2. replace the generator's provenance lines, which describe committed design-repository results ("no simulation was
   run for this sheet", results directory verification/cace/results/...), by this re-run's provenance.
Links are written for the data sheet's own folder docs/chipalooza2_as_taped_out/datasheets/ (the candidate is meant
to replace sg13cmos5l_IOPadDiff2Single.md there).
Usage: ds_post.py <generated.md> <current_datasheet.md> <out.md>"""
import re, sys

RUN = '../../../verification/c2_gaps/d2s_schematic_rerun'


def main(gen, cur, out):
    g = open(gen, encoding='utf-8').read()
    c = open(cur, encoding='utf-8').read()
    m = re.search(r'^## Figures\n.*?(?=^## Specification)', c, re.S | re.M)
    if not m:
        sys.exit('no Figures section in ' + cur)
    g = g.replace('## Specification (ex post facto', m.group(0) + '## Specification (ex post facto', 1)
    rep = [
        (r'; results \[`verification/cace/results/`\]\([^)]*\)  ',
         f'; results: the schematic re-run of 2026-11-25, [`verification/c2_gaps/d2s_schematic_rerun/csv/`]({RUN}/csv) (this repository)  '),
        (r'\*\*Generated:\*\* by `datasheets/tools/make_datasheet.py` from the committed CACE files; '
         r'\*\*no simulation was run for this sheet\*\* and nothing was re-checked against the taped-out netlist\.',
         f'**Generated:** by `datasheets/tools/make_datasheet.py` from the CACE results of the schematic re-run of '
         f'2026-11-25 ([README]({RUN}/README.md), [old vs new]({RUN}/results.md)): CACE 2.11 with the design '
         f"repository's yaml and templates at `91a7da8b`, unchanged; the simulated netlist is the taped-out cell's LVS "
         f'netlist plus the simulation-only Rsub (vss to iovss, 1 Ω).'),
        (r'Results directory: `verification/cace/results/sg13cmos5l_IOPadDiff2Single`\. ',
         f'Results directory: [`verification/c2_gaps/d2s_schematic_rerun/csv/`]({RUN}/csv) (this repository; '
         f'schematic re-run of 2026-11-25). '),
        (r'- Whether the simulated netlist equals the block as taped out \(see `\.\./characterization_candidates\.md`\)\.',
         f'- Post-layout values (magic PEX of the taped-out GDS): [D2S post-layout](../../../verification/c2_gaps/d2s_pex/results.md) '
         f'(the simulated schematic netlist was checked against the taped-out LVS netlist: [netcheck.txt]({RUN}/netcheck.txt)).'),
    ]
    for pat, new in rep:
        g, n = re.subn(pat, lambda _m: new, g, count=1)
        if n != 1:
            sys.exit('pattern not found: ' + pat)
    open(out, 'w', encoding='utf-8').write(g)
    print(out)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(*sys.argv[1:])
