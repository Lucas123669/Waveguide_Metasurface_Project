import csv
import json
import os

from .config import design_with_params
from .phase_design import build_phase_targets


def _write_targets(path, targets):
    if not targets:
        return
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(targets[0]))
        writer.writeheader()
        writer.writerows(targets)


def evaluate_candidate(params, config, backend, workspace):
    os.makedirs(workspace, exist_ok=True)
    design = design_with_params(config, params)
    targets = build_phase_targets(design)
    candidate = {"params": params, "design": design, "config": config}
    with open(os.path.join(workspace, "candidate.json"), "w", encoding="utf-8") as handle:
        json.dump(candidate, handle, indent=2)
    _write_targets(os.path.join(workspace, "phase_targets.csv"), targets)
    try:
        result = backend.evaluate(design, targets, config, workspace).to_dict()
        result["attrs"]["valid_result"] = True
    except Exception as error:
        result = {
            "metrics": {},
            "attrs": {"valid_result": False, "error": str(error)},
        }
    with open(os.path.join(workspace, "scored_result.json"), "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    return result
