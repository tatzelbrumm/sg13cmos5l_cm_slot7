#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Christoph Maier
# SPDX-License-Identifier: Apache-2.0
"""Run one of the existing slot-deck scripts with the KLayout pad netlists' antenna diodes at their extracted size.

Usage: python3 -I run_fixed.py <script.py> <runs_dir> <script arguments ...>
  <script.py>  ../ac_tran/slot.py, ../dc_curves/roundtrip.py or ../slot_modes_bg/slot_modes.py (unchanged files)
  <runs_dir>   where the decks are written (replaces the script's own RUNS folder, so earlier runs are not touched)
  e.g. run_fixed.py ../ac_tran/slot.py W/fixed_runs W W/out_fixed klayout:tt:27:3.3:sine

The script is imported as it is; the only change is that run_tier1.wrapped() (design repository 9052bd35, which calls
run_starve.convert()) is wrapped so that each converted netlist then goes through fix_diodes.fix_file(): every
dantenna / dpantenna a= p= is replaced by the equivalent l= w= (see fix_diodes.py). The replacements are printed.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fix_diodes  # noqa: E402

script, runs = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.argv = [str(script)] + sys.argv[3:]
spec = importlib.util.spec_from_file_location(script.stem, script)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)  # module level only (argument parsing, run_tier1 import); __main__ block not run
T = mod.T
orig = T.wrapped
seen = set()


def wrapped(cell):
    name = orig(cell)
    log = fix_diodes.fix_file(Path(T.RUNS) / name)
    if cell not in seen:
        seen.add(cell)
        for ln in log:
            print(f'fix_diodes {cell}: {ln}', flush=True)
    return name


T.wrapped = wrapped
if hasattr(mod, 'RUNS'):
    mod.RUNS = runs
if hasattr(mod, 'main'):          # slot_modes.py: main() reads JOBS itself (its runs go to its <work-dir> argument)
    mod.main()
else:                             # slot.py / roundtrip.py
    mod.OUT.mkdir(parents=True, exist_ok=True)
    for j in mod.JOBS:
        mod.run(j)
