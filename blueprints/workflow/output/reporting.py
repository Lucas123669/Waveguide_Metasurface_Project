"""Compact reporting and stable output identity helpers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Mapping

import numpy as np


def to_jsonable(value: Any) -> Any:
    """Convert numerical, geometry, and dataclass values to plain JSON data."""
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [to_jsonable(item) for item in value]
    if hasattr(value, "__geo_interface__"):
        return to_jsonable(value.__geo_interface__)
    return value


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    """Write one deterministic UTF-8 JSON file."""
    path.write_text(
        json.dumps(to_jsonable(data), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_files(project_root: Path) -> list[Path]:
    files = [
        candidate
        for name in ("pyproject.toml", "uv.lock", "main/run_blueprint.py")
        if (candidate := project_root / name).is_file()
    ]
    package_root = project_root / "workflow"
    if package_root.is_dir():
        files.extend(path for path in package_root.rglob("*.py") if path.is_file())
    return sorted(set(files), key=lambda path: path.relative_to(project_root).as_posix())


def _git_output(working_directory: Path, *arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(working_directory), *arguments],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def blueprint_source_provenance(project_root: Path) -> dict[str, Any]:
    """Return a reproducible source-tree hash and best-effort Git identity."""

    root = project_root.resolve()
    files = _source_files(root)
    if not files:
        raise FileNotFoundError(f"no blueprint source files found below {root}")

    relative_paths = [path.relative_to(root).as_posix() for path in files]
    digest = sha256()
    for relative_path, path in zip(relative_paths, files):
        encoded_path = relative_path.encode("utf-8")
        content = path.read_bytes()
        digest.update(len(encoded_path).to_bytes(8, "big"))
        digest.update(encoded_path)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)

    repository_root_text = _git_output(root, "rev-parse", "--show-toplevel")
    git: dict[str, Any]
    if repository_root_text is None:
        git = {"available": False}
    else:
        repository_root = Path(repository_root_text).resolve()
        commit = _git_output(repository_root, "rev-parse", "HEAD")
        branch = _git_output(repository_root, "branch", "--show-current")
        repository_status = _git_output(
            repository_root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
        )
        source_status = _git_output(
            root,
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--",
            *relative_paths,
        )
        git = {
            "available": commit is not None,
            "commit": commit,
            "branch": branch or None,
            "repository_dirty": (
                None if repository_status is None else bool(repository_status)
            ),
            "source_tree_dirty": None if source_status is None else bool(source_status),
        }

    return {
        "algorithm": "sha256",
        "tree_sha256": digest.hexdigest(),
        "file_count": len(files),
        "files": relative_paths,
        "git": git,
    }


def _dxf_number(value: object) -> str:
    return f"{float(value):.6f}".rstrip("0").rstrip(".").replace("-", "m")


def _signed_parameter_number(value: object) -> str:
    return f'{float(value):.6f}'.rstrip('0').rstrip('.')


def safe_label(value: object) -> str:
    resolved = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(value).strip())
    return resolved.strip("-._") or "unnamed"


def _design_name_prefix(config: Mapping[str, Any]) -> str:
    geometry = config["geometry"]
    finite = geometry["finite"]
    unit_cell = geometry["unit_cell"]
    cavity = unit_cell["cavity"]
    cladding = unit_cell["cladding"]
    shift = geometry["cladding_shift"]
    return (
        f"dxf_{int(finite['cavity_layers'])}-{int(finite['cladding_layers'])}_"
        f"cav({_dxf_number(cavity['b0_nm'])}-{_dxf_number(cavity['eta'])}-{_dxf_number(cavity['zeta'])})_"
        f"clad({_dxf_number(cladding['b0_nm'])}-{_dxf_number(cladding['eta'])}-{_dxf_number(cladding['zeta'])})_"
        f"shift({_dxf_number(shift['x_factor'])}-{_dxf_number(shift['y_factor'])})"
    )


def _triangle_correction_suffix(config: Mapping[str, Any]) -> str:
    correction = config['fabrication']['triangle_side_correction']
    global_delta = _signed_parameter_number(correction['global_delta_nm'])
    strength = _signed_parameter_number(
        correction['envelope_modulation_strength']
    )
    return f'({global_delta},{strength})'


def dxf_artifact_name(config: Mapping[str, Any], identity_sha256: str) -> str:
    """Return a parameter-readable DXF filename with explicit corrections."""

    fabrication = config["fabrication"]
    dose = config["dose"]
    profile_label = safe_label(fabrication["profile_id"])
    dose_label = safe_label(dose["kind"])
    process_label = (
        profile_label
        if profile_label == dose_label or profile_label.endswith(f"-{dose_label}")
        else f"{profile_label}-{dose_label}"
    )
    return (
        f"{_design_name_prefix(config)}_{process_label}-"
        f"r{safe_label(fabrication['revision'])}_"
        f"{_triangle_correction_suffix(config)}.dxf"
    )


def case_name(config: Mapping[str, Any], identity_sha256: str) -> str:
    return f'{_design_name_prefix(config)}_{_triangle_correction_suffix(config)}'
