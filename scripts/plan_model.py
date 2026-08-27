import argparse
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from gwm_workflow.config import load_config
from gwm_workflow.model_plan import build_model_plan
from gwm_workflow.runtime_paths import get_workspace_path


def main():
    parser = argparse.ArgumentParser(description="Write a COMSOL construction plan.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    config = load_config(args.config)
    output = args.output or get_workspace_path(config["design"]["task"], "model_plan.json")
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    with open(output, "w", encoding="utf-8") as handle:
        json.dump(build_model_plan(config), handle, indent=2)
    print(output)


if __name__ == "__main__":
    main()
