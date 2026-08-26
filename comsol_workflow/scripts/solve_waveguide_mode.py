"""Solve the SOI waveguide mode and calculate the 45-degree supercell period."""

import argparse
import json
import os
import sys


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gwm_workflow.comsol_mode import solve_mode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=os.path.join(PROJECT_ROOT, "configs", "beam_deflector_1550nm.json"))
    parser.add_argument("--output", default=os.path.join(PROJECT_ROOT, "comsol_models", "waveguide_mode_1550nm"))
    args = parser.parse_args()
    with open(args.config, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    result = solve_mode(config, args.output)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
