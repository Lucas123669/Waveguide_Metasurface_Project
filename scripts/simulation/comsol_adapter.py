"""Apply a candidate to a calibrated COMSOL template through MPh.

The initial repository intentionally does not fabricate an unverified model
tree in code. The first GUI-inspected `.mph` seed is the source of truth; this
adapter then makes repeated, auditable runs fully automatic.
"""

import argparse
import json
import os
import shutil


def _plain(value):
    try:
        import numpy as np
        if isinstance(value, np.ndarray):
            return [_plain(item) for item in value.tolist()]
        if isinstance(value, np.generic):
            return _plain(value.item())
    except ModuleNotFoundError:
        pass
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return value


def _resolve(project_root, path):
    if not path:
        return ""
    return path if os.path.isabs(path) else os.path.abspath(os.path.join(project_root, path))


def main():
    parser = argparse.ArgumentParser(description="Run a calibrated COMSOL metasurface template.")
    parser.add_argument("--candidate", default="candidate.json")
    args = parser.parse_args()

    with open(args.candidate, "r", encoding="utf-8") as handle:
        candidate = json.load(handle)
    design = candidate["design"]
    settings = candidate["config"]["simulation"]["comsol"]
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    template = _resolve(project_root, settings.get("template_model", ""))
    if not template or not os.path.exists(template):
        raise FileNotFoundError(
            "Set simulation.comsol.template_model to the calibrated .mph seed "
            "described in docs/reports/simulation/comsol_model_tree.md"
        )
    if not any(shutil.which(name) for name in ["comsol", "comsolmphserver", "comsolbatch"]):
        raise RuntimeError("COMSOL executables are not on PATH")

    import mph
    if os.name == "nt":
        mph.option("session", os.environ.get("GWM_WORKFLOW_MPH_SESSION", "client-server"))
    client = mph.start(version=os.environ.get("COMSOL_VERSION"))
    model = client.load(template)
    try:
        for design_name, spec in settings.get("parameter_map", {}).items():
            if design_name not in design:
                continue
            text = str(design[design_name])
            if spec.get("unit"):
                text = f"{text} [{spec['unit']}]"
            model.java.param().set(spec["tag"], text)
        study_tag = settings.get("study_tag", "std1")
        model.java.study(study_tag).run()
        expressions = settings.get("expressions", [])
        metrics = {}
        if expressions:
            values = model.evaluate(
                [item["expr"] for item in expressions],
                unit=[item.get("unit", "1") for item in expressions],
            )
            for item, value in zip(expressions, values):
                metrics[item["name"]] = _plain(value)
        workspace = os.getcwd()
        model.save(os.path.join(workspace, "solved_gwm.mph"))
        model.save(os.path.join(workspace, "solved_gwm.java"))
        with open(os.path.join(workspace, "result.json"), "w", encoding="utf-8") as handle:
            json.dump(
                {"metrics": metrics, "attrs": {"backend": "comsol", "template": template}},
                handle,
                indent=2,
            )
    finally:
        client.remove(model)


if __name__ == "__main__":
    main()
