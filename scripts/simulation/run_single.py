import argparse
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from gwm_workflow.backends import make_backend
from gwm_workflow.config import load_config
from gwm_workflow.runtime_paths import get_workspace_path
from gwm_workflow.workflow import evaluate_candidate


def main():
    parser = argparse.ArgumentParser(description="Evaluate one guided-wave metasurface design.")
    parser.add_argument(
        "--config",
        default=os.path.join(PROJECT_ROOT, "configs", "seeds", "guo2020_beam_deflector_paper_seed.json"),
    )
    parser.add_argument("--backend", choices=["mock", "comsol"], default="mock")
    parser.add_argument("--workspace")
    args, unknown = parser.parse_known_args()

    config = load_config(args.config)
    params = {}
    for index in range(0, len(unknown), 2):
        if index + 1 >= len(unknown) or not unknown[index].startswith("--"):
            raise ValueError(f"Expected override as --name value, got {unknown[index:]}")
        params[unknown[index][2:].replace("-", "_")] = float(unknown[index + 1])
    workspace = args.workspace or get_workspace_path(config["design"]["task"], args.backend)
    result = evaluate_candidate(params, config, make_backend(args.backend), workspace)
    print(json.dumps(result, indent=2))
    if not result.get("attrs", {}).get("valid_result", True):
        sys.exit(1)


if __name__ == "__main__":
    main()
