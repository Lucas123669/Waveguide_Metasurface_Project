"""Phase-library driven circular-pillar source, independent of all solvers."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Mapping
import numpy as np
from shapely.geometry import Polygon

from blueprint_core.models import LayoutFeature, LayoutPlan
from .phase_library import load_phase_library, wrap_phase


KIND = 'phase_library_metalens_v1'


def build_metalens_layout(geometry: Mapping[str, Any], *, base_dir: Path) -> LayoutPlan:
    lib = load_phase_library(geometry['phase_library'], base_dir=base_dir,
                             wavelength_nm=geometry['wavelength_nm'],
                             period_um=geometry['period_um'])
    radius = geometry['aperture_diameter_um'] / 2
    period = geometry['period_um']
    n_half = math.floor(radius / period)
    if (2 * n_half + 1) ** 2 > geometry['max_candidate_sites']:
        raise ValueError('candidate grid exceeds explicit max_candidate_sites budget')
    theta = np.arange(geometry['circle_vertices']) * (2 * np.pi / geometry['circle_vertices'])
    unit_circle = np.column_stack((np.cos(theta), np.sin(theta)))
    boundary_theta = np.arange(geometry['boundary_vertices']) * (2 * np.pi / geometry['boundary_vertices'])
    boundary = Polygon(radius * np.column_stack((np.cos(boundary_theta), np.sin(boundary_theta))))
    phases = np.array([s.phase_deg for s in lib.states])
    features = []
    errors = []
    excluded = 0
    for j in range(-n_half, n_half + 1):
        for i in range(-n_half, n_half + 1):
            x, y = i * period, j * period
            if math.hypot(x, y) > radius:
                continue
            optical_path = math.hypot(math.hypot(x, y), geometry['focal_length_um']) - geometry['focal_length_um']
            target = wrap_phase(geometry['phase_offset_deg'] + geometry['phase_sign'] * 360 * optical_path / (geometry['wavelength_nm'] / 1000))
            # Stable ID order breaks ties; never interpolate wrapped angles.
            best = int(np.argmin(np.abs((phases - target + 180) % 360 - 180)))
            state = lib.states[best]
            polygon = Polygon(unit_circle * (state.diameter_um / 2) + [x, y])
            # Complete polygons, not just centers, must fit the aperture. Do not clip pillars.
            if not boundary.covers(polygon):
                excluded += 1
                continue
            error = wrap_phase(state.phase_deg - target)
            features.append(LayoutFeature(
                feature_id=f'pillar_{i}_{j}', region='pillar', parent_i=i, parent_j=j,
                group_id=state.state_id, local_index=0, layer=0,
                nominal_polygon=polygon, polygon=polygon, shift_um=(0, 0),
                dxf_layer=geometry['dxf_layer'],
                metadata={'state_id': state.state_id, 'diameter_um': state.diameter_um,
                          'target_phase_deg': target, 'library_phase_deg': state.phase_deg,
                          'phase_error_deg': error, 'transmission': state.transmission,
                          'source': state.source, 'local_axis_angle_deg': 0.0}))
            errors.append(error)
    if not features:
        raise ValueError('no complete pillars fit aperture')
    maximum = max(map(abs, errors))
    if maximum > geometry['max_quantization_error_deg'] + 1e-9:
        raise ValueError(f'phase quantization error {maximum:.6f} exceeds configured limit')
    return LayoutPlan(KIND, features, boundary, metadata={'optical_design': {
        'wavelength_nm': geometry['wavelength_nm'], 'period_um': period,
        'aperture_diameter_um': 2 * radius, 'focal_length_um': geometry['focal_length_um'],
        'phase_sign': geometry['phase_sign'], 'phase_offset_deg': geometry['phase_offset_deg'],
        'largest_phase_gap_deg': lib.largest_phase_gap_deg,
        'phase_error_max_deg': maximum,
        'phase_error_rms_deg': float(np.sqrt(np.mean(np.square(errors)))),
        'excluded_boundary_sites': excluded, 'state_count': len(lib.states),
        'phase_library': dict(lib.provenance), 'physical_metadata': dict(lib.metadata),
        'warning': 'Nominal unit-cell lookup only; no full-device simulation or post-correction optical validation.',
        'state_counts': {str(s.state_id): sum(f.group_id == s.state_id for f in features) for s in lib.states}}})


class MetalensSource:
    kind = KIND

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def build(self, geometry: Mapping[str, object]) -> LayoutPlan:
        return build_metalens_layout(geometry, base_dir=self.base_dir)
