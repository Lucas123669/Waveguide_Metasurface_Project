import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from gwm_workflow.comsol_structure import create_and_save
from gwm_workflow.config import load_config


def main():
    parser = argparse.ArgumentParser(
        description="Build the paper-seeded 3D guided-wave metasurface structure in COMSOL."
    )
    parser.add_argument(
        "--config",
        default=os.path.join(PROJECT_ROOT, "configs", "seeds", "guo2020_beam_deflector_paper_seed.json"),
    )
    parser.add_argument(
        "--output-dir",
        default=os.path.join(PROJECT_ROOT, "experiments", "l02_guo_2020", "beam_deflector", "structure"),
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
