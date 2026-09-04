import argparse
import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

from gwm_workflow.config import load_config
from gwm_workflow.phase_design import build_phase_targets
from gwm_workflow.runtime_paths import get_workspace_path


def main():
    parser = argparse.ArgumentParser(description="Build the discrete meta-atom placement table.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    config = load_config(args.config)
    rows = build_phase_targets(config["design"])
    output = args.output or get_workspace_path(config["design"]["task"], "phase_targets.csv")
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(output)


if __name__ == "__main__":
    main()
