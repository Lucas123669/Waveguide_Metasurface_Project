"""Strict CSV bridge for the independent cylindrical-metalens workflow.

No solver or MATLAB dependency. Physical phase (not a sign-flipped plotting
coordinate) is imported. Interpolated values remain distinguishable.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from hashlib import sha256
import io
import json
import math
from pathlib import Path
from typing import Any, Mapping


def wrap_phase(value: float) -> float:
    return (value + 180.0) % 360.0 - 180.0


@dataclass(frozen=True)
class PhaseState:
    state_id: int
    diameter_um: float
    phase_deg: float
    transmission: float
    source: str


@dataclass(frozen=True)
class PhaseLibrary:
    states: tuple[PhaseState, ...]
    metadata: Mapping[str, Any]
    provenance: Mapping[str, Any]
    largest_phase_gap_deg: float


def _finite(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f'{name} must be numeric, not boolean')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _verified_bytes(path: Path, expected: str) -> bytes:
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != expected:
        raise ValueError(f"phase library SHA256 mismatch: {path}")
    return raw


def load_phase_library(spec: Mapping[str, Any], *, base_dir: Path,
                       wavelength_nm: float, period_um: float) -> PhaseLibrary:
    """Import canonical, issue-10 summary, or issue-11 CSV with pinned metadata."""
    csv_path = (base_dir / spec['csv_path']).resolve()
    meta_path = (base_dir / spec['metadata_path']).resolve()
    raw = _verified_bytes(csv_path, spec['csv_sha256'])
    meta = json.loads(_verified_bytes(meta_path, spec['metadata_sha256']).decode('utf-8'))
    required = {'schema_version', 'wavelength_nm', 'period_um', 'pillar_height_um',
                'pillar_material', 'substrate_material', 'incidence', 'polarization',
                'phase_convention', 'validation_status', 'provenance'}
    if not isinstance(meta, dict) or set(meta) != required or type(meta['schema_version']) is not int or meta['schema_version'] != 1:
        raise ValueError('phase metadata has missing/unknown fields or schema version')
    for key in ('wavelength_nm', 'period_um', 'pillar_height_um'):
        if _finite(meta[key], key) <= 0:
            raise ValueError(f'metadata.{key} must be positive')
    for key in required - {'schema_version', 'wavelength_nm', 'period_um', 'pillar_height_um'}:
        if not isinstance(meta[key], str) or not meta[key].strip():
            raise ValueError(f'metadata.{key} must be a non-empty string')
    if meta['phase_convention'] != 'physical_transmission_phase_deg':
        raise ValueError('explicit physical transmission phase convention required')
    if meta['incidence'] != 'normal' or meta['polarization'] != 'co_polarized':
        raise ValueError('v1 supports normal-incidence co-polarized libraries only')
    if meta['validation_status'] not in {'unverified_import', 'unit_cell_validated', 'device_validated'}:
        raise ValueError('invalid phase-library validation_status')
    if not math.isclose(float(meta['wavelength_nm']), wavelength_nm, rel_tol=0, abs_tol=1e-9):
        raise ValueError('phase library wavelength does not match lens')
    if not math.isclose(float(meta['period_um']), period_um, rel_tol=0, abs_tol=1e-12):
        raise ValueError('phase library period does not match lens')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    format_name = spec['format']
    required_columns = {
        'matlab_work10': {'D', 'phase_deg', 'mag_dB'},
        'matlab_work11': {'state_idx', 'D_um', 'actual_phase_deg', 'mag_dB', 'source'},
        'canonical': {'state_idx', 'D_um', 'phase_deg', 'transmission', 'source'},
    }[format_name]
    if not required_columns.issubset(reader.fieldnames or []):
        raise ValueError(f'phase CSV missing required columns for {format_name}')
    states = []
    seen = set()
    rejected = 0
    for index, row in enumerate(reader, 1):
        state_id = index if format_name == 'matlab_work10' else int(row['state_idx'])
        if state_id <= 0 or state_id in seen:
            raise ValueError('phase state identifiers must be positive and unique')
        seen.add(state_id)
        diameter = _finite(row['D'] if format_name == 'matlab_work10' else row['D_um'], 'diameter')
        phase = _finite(row['actual_phase_deg'] if format_name == 'matlab_work11' else row['phase_deg'], 'phase')
        transmission = (_finite(row['transmission'], 'transmission') if format_name == 'canonical'
                        else 10 ** (_finite(row['mag_dB'], 'mag_dB') / 10))
        source = 'unverified' if format_name == 'matlab_work10' else row['source'].strip()
        if source not in {'simulated', 'interpolated', 'measured', 'unverified'}:
            raise ValueError(f'unsupported phase state source: {source}')
        if not 0 < diameter < period_um or not 0 <= transmission <= 1.000001:
            raise ValueError('invalid diameter or normalized power transmission')
        if source not in spec['allowed_sources'] or transmission < spec['min_transmission']:
            rejected += 1
            continue
        states.append(PhaseState(state_id, diameter, wrap_phase(phase), transmission, source))
    if len(states) < 2:
        raise ValueError('at least two eligible phase states required')
    angles = sorted(state.phase_deg % 360 for state in states)
    gap = max(b - a for a, b in zip(angles, angles[1:] + [angles[0] + 360]))
    if gap > spec['max_phase_gap_deg'] + 1e-9:
        raise ValueError(f'phase coverage gap {gap:.6f} exceeds max_phase_gap_deg')
    provenance = {'csv_path': str(csv_path), 'csv_sha256': spec['csv_sha256'],
                  'metadata_sha256': spec['metadata_sha256'], 'format': format_name,
                  'eligible_states': len(states), 'rejected_states': rejected,
                  'source_counts': {source: sum(s.source == source for s in states)
                                    for source in sorted({s.source for s in states})}}
    return PhaseLibrary(tuple(sorted(states, key=lambda s: s.state_id)), meta, provenance, gap)
