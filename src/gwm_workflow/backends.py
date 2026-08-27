from abc import ABC, abstractmethod
import json
import math
import os
import shlex
import subprocess
import sys

from .phase_design import beam_deflection
from .results import SimulationResult


class SimulationBackend(ABC):
    @abstractmethod
    def evaluate(self, design, targets, config, workspace):
        """Evaluate one configured device and return a SimulationResult."""


class AnalyticMockBackend(SimulationBackend):
    """Pipeline/theory check; this is not an electromagnetic solver."""

    def evaluate(self, design, targets, config, workspace):
        errors = [float(row["phase_error_rad"]) for row in targets]
        phase_rms = math.sqrt(sum(value * value for value in errors) / len(errors))
        phase_factor = math.exp(-(phase_rms / 0.6) ** 2)
        metrics = {
            "phase_rms_error_rad": phase_rms,
            "atom_count": len(targets),
        }
        if design["task"] == "beam_deflector":
            steering = beam_deflection(
                design["wavelength_um"],
                design["effective_index_initial"],
                design["supercell_period_um"],
                design.get("reported_angle_sign", 1.0),
            )
            metrics.update(steering)
            metrics["estimated_extraction_efficiency"] = (
                float(config["simulation"].get("paper_metal_efficiency_limit", 0.09))
                * phase_factor
            )
        else:
            metrics.update(
                {
                    "designed_focal_length_um": float(design["focal_length_um"]),
                    "estimated_focus_quality": phase_factor,
                }
            )
        return SimulationResult(
            metrics=metrics,
            attrs={
                "backend": "mock",
                "warning": "Pipeline/theory check only; not a COMSOL result.",
            },
        )


class ExternalComsolBackend(SimulationBackend):
    """Run the MPh adapter configured in simulation.comsol.command."""

    def evaluate(self, design, targets, config, workspace):
        settings = config["simulation"].get("comsol", {})
        command = settings.get("command")
        if not command:
            raise ValueError("simulation.comsol.command is required")
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        command = command.format(
            python=sys.executable,
            project_root=project_root,
            workspace=os.path.abspath(workspace),
        )
        argv = shlex.split(command.format(
            python=sys.executable,
            project_root=project_root,
            workspace=os.path.abspath(workspace),
        ))
        completed = subprocess.run(
            argv,
            cwd=workspace,
            shell=False,
            text=True,
            capture_output=True,
            check=False,
            timeout=settings.get("timeout_seconds", 600),
        )
        with open(os.path.join(workspace, "comsol_stdout.txt"), "w", encoding="utf-8") as handle:
            handle.write(completed.stdout)
        with open(os.path.join(workspace, "comsol_stderr.txt"), "w", encoding="utf-8") as handle:
            handle.write(completed.stderr)
        if completed.returncode != 0:
            detail = completed.stderr.strip().splitlines()
            detail = detail[-1] if detail else "no stderr was captured"
            raise RuntimeError(
                f"COMSOL adapter failed with exit code {completed.returncode}: {detail}. "
                "Inspect comsol_stderr.txt for the full traceback."
            )
        result_path = os.path.join(workspace, "result.json")
        if not os.path.exists(result_path):
            raise FileNotFoundError(f"COMSOL adapter did not write {result_path}")
        with open(result_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return SimulationResult(data.get("metrics", {}), data.get("attrs", {}))


def make_backend(name):
    if name == "mock":
        return AnalyticMockBackend()
    if name == "comsol":
        return ExternalComsolBackend()
    raise ValueError(f"Unknown backend: {name}")
