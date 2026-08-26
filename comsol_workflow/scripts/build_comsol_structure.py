import argparse
import json
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from gwm_workflow.comsol_structure import create_and_save
from gwm_workflow.config import load_config


def main():
    parser = argparse.ArgumentParser(
        description="Build the paper-seeded 3D guided-wave metasurface structure in COMSOL."
    )
    parser.add_argument(
        "--config",
        default=os.path.join(os.path.dirname(__file__), "..", "configs", "beam_deflector_1550nm.json"),
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(os.path.dirname(__file__), "..", "comsol_models", "beam_deflector_structure"),
    )
    parser.add_argument("--supercells", type=int)
    parser.add_argument("--geometry-only", action="store_true")
    parser.add_argument("--build-mesh", action="store_true")
    args = parser.parse_args()
    summary = create_and_save(
        load_config(args.config),
        args.output_dir,
        supercell_count=args.supercells,
        add_physics=not args.geometry_only,
        build_mesh=args.build_mesh,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
