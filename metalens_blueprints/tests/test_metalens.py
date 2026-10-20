"""External-library import, optical mapping and shared pipeline regression."""
from hashlib import sha256
import json
from pathlib import Path

import numpy as np
import pytest
from shapely import affinity

from metalens_workflow.config import load_config as load_blueprint_config
from metalens_workflow.cli import generate as generate_blueprint
from metalens_workflow.geometry import build_metalens_layout
from metalens_workflow.phase_library import load_phase_library, wrap_phase
from metalens_workflow.gds import readback_gds, write_gds

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'main' / 'parameter.json'


def config_data():
    data = json.loads(EXAMPLE.read_text(encoding='utf-8'))
    lib = data['geometry']['phase_library']
    for key in ('csv_path', 'metadata_path'):
        lib[key] = str((EXAMPLE.parent / lib[key]).resolve())
    return data


def library(data):
    g = data['geometry']
    return load_phase_library(g['phase_library'], base_dir=EXAMPLE.parent,
                               wavelength_nm=g['wavelength_nm'], period_um=g['period_um'])


def write_config(tmp_path, data):
    path = tmp_path / 'parameter.json'
    path.write_text(json.dumps(data), encoding='utf-8')
    return load_blueprint_config(path)


def test_example_config_and_unverified_import():
    cfg = load_blueprint_config(EXAMPLE)
    lib = library(cfg.data)
    assert len(lib.states) == 12
    assert lib.metadata['validation_status'] == 'unverified_import'
    assert lib.largest_phase_gap_deg == pytest.approx(61.438102)
    # Raw CST phase, NOT issue-10's sign-inverted design plotting coordinate.
    assert lib.states[1].phase_deg == pytest.approx(-52.637493)


@pytest.mark.parametrize('field,value,error', [
    ('period_um', .9, 'period'), ('wavelength_nm', 1064, 'wavelength')])
def test_physical_conditions_must_match(field, value, error):
    data = config_data()
    data['geometry'][field] = value
    with pytest.raises(ValueError, match=error):
        library(data)


@pytest.mark.parametrize('key', ['csv_sha256', 'metadata_sha256'])
def test_pinned_library_bytes(key):
    data = config_data()
    data['geometry']['phase_library'][key] = '0' * 64
    with pytest.raises(ValueError, match='SHA256'):
        library(data)


def test_sources_transmission_and_phase_coverage_gates():
    data = config_data()
    spec = data['geometry']['phase_library']
    spec['allowed_sources'] = ['measured']
    with pytest.raises(ValueError, match='eligible'):
        library(data)
    spec['allowed_sources'] = ['simulated']
    spec['max_phase_gap_deg'] = 35
    with pytest.raises(ValueError, match='coverage'):
        library(data)
    spec['max_phase_gap_deg'] = 360
    spec['min_transmission'] = 1
    with pytest.raises(ValueError, match='eligible'):
        library(data)


def test_full_polygon_aperture_and_lookup_sign():
    g = config_data()['geometry']
    g.update(aperture_diameter_um=10, focal_length_um=10)
    layout = build_metalens_layout(g, base_dir=EXAMPLE.parent)
    assert layout.features
    assert all(layout.boundary.covers(f.polygon) for f in layout.features)
    assert layout.metadata['optical_design']['excluded_boundary_sites'] > 0
    center = next(f for f in layout.features if f.parent_i == f.parent_j == 0)
    assert center.group_id == 1
    assert center.metadata['phase_error_deg'] == pytest.approx(0)
    for f in layout.features:
        x, y = f.nominal_centroid_um
        target = wrap_phase(g['phase_offset_deg'] - 360 / 1.55 * (np.sqrt(x*x+y*y+100)-10))
        assert f.metadata['target_phase_deg'] == pytest.approx(target)


def test_lookup_error_budget_and_candidate_budget():
    g = config_data()['geometry']
    g['max_candidate_sites'] = 1
    with pytest.raises(ValueError, match='budget'):
        build_metalens_layout(g, base_dir=EXAMPLE.parent)
    g['max_candidate_sites'] = 1000000
    g.update(aperture_diameter_um=10, focal_length_um=10, max_quantization_error_deg=.1)
    with pytest.raises(ValueError, match='quantization'):
        build_metalens_layout(g, base_dir=EXAMPLE.parent)


def test_wrap_uses_short_distance():
    assert wrap_phase(179 - (-179)) == -2
    assert wrap_phase(360) == 0


def test_import_work10_and_canonical_sources(tmp_path):
    data = config_data()
    spec = data['geometry']['phase_library']
    path = tmp_path / 'library.csv'
    path.write_text('D,phase_deg,mag_dB\n0.2,179,-0.1\n0.3,-179,-0.2\n', encoding='utf-8')
    spec.update(format='matlab_work10', csv_path=str(path), csv_sha256=sha256(path.read_bytes()).hexdigest(),
                allowed_sources=['unverified'], max_phase_gap_deg=360)
    assert all(s.source == 'unverified' for s in library(data).states)
    path.write_text('state_idx,D_um,phase_deg,transmission,source\n1,0.2,179,0.9,simulated\n2,0.3,-179,0.9,interpolated\n', encoding='utf-8')
    spec.update(format='canonical', csv_sha256=sha256(path.read_bytes()).hexdigest(), allowed_sources=['simulated'])
    with pytest.raises(ValueError, match='eligible'):
        library(data)
    spec['allowed_sources'].append('interpolated')
    assert library(data).states[1].source == 'interpolated'


def test_cli_pipeline_and_no_overwrite(tmp_path):
    data = config_data()
    data['geometry'].update(aperture_diameter_um=10, focal_length_um=10)
    data['export']['dpi'] = 50
    cfg = write_config(tmp_path, data)
    preflight = generate_blueprint(cfg, preflight_only=True)
    assert preflight.drc.passed
    assert not cfg.output_root.exists()
    result = generate_blueprint(cfg)
    assert result.drc.passed
    assert len(result.output_files) == 4
    report = json.loads((result.case_dir / 'layout_report.json').read_text(encoding='utf-8'))
    assert report['release_status'] == 'engineering_preview'
    assert report['gds']['roundtrip_geometry_verified']
    assert report['gds']['reference_count'] == result.feature_count
    assert report['gds']['structure_count'] <= 13
    assert report['optical_design']['phase_library']['csv_sha256'] == data['geometry']['phase_library']['csv_sha256']
    assert len(report['optical_design']['sites']) == result.feature_count
    assert len(report['outputs']['sha256']) == 3
    with pytest.raises(FileExistsError):
        generate_blueprint(cfg)


def test_gds_uses_corrected_polygons_and_checks_grid(tmp_path):
    g = config_data()['geometry']
    g.update(aperture_diameter_um=3, focal_length_um=3)
    layout = build_metalens_layout(g, base_dir=EXAMPLE.parent)
    # Move one real vertex, demonstrating it cannot be deduplicated by optical state alone.
    from blueprint_core.fabrication.corrections import snap_polygon_to_grid
    for f in layout.features:
        f.polygon = snap_polygon_to_grid(f.polygon, .001, (0,0))
    f = layout.features[0]
    f.polygon = affinity.scale(f.polygon, 1.1, 1.1, origin='centroid')
    path = tmp_path / 'test.gds'
    with pytest.raises(ValueError, match='off configured'):
        write_gds(layout, path, grid_nm=1, layer=1, datatype=0)
    f.polygon = snap_polygon_to_grid(f.polygon, .001, (0,0))
    report = write_gds(layout, path, grid_nm=1, layer=1, datatype=0)
    assert report['roundtrip_geometry_verified']
    raw = readback_gds(path)
    assert len(raw['flattened']) == layout.feature_count
    assert raw['database_unit_m'] == pytest.approx(1e-9)
    path.write_bytes(path.read_bytes()[:-3])
    with pytest.raises(ValueError, match='GDS'):
        readback_gds(path)


def test_strict_fields_identity_and_no_triangle_calibration(tmp_path):
    data = config_data()
    cfg = write_config(tmp_path, data)
    data['export']['gds']['enabled'] = False
    assert cfg.identity_sha256 != write_config(tmp_path, data).identity_sha256
    data['geometry']['typo'] = 1
    with pytest.raises(ValueError, match='unknown'):
        write_config(tmp_path, data)
    del data['geometry']['typo']
    data['fabrication']['triangle_side_correction'] = {'global_delta_nm': -10}
    with pytest.raises(ValueError, match='unknown'):
        write_config(tmp_path, data)


@pytest.mark.parametrize('key,value', [('phase_sign', 0), ('phase_sign', True),
    ('circle_vertices', 3), ('boundary_vertices', 8), ('max_candidate_sites', 0),
    ('max_quantization_error_deg', 181)])
def test_metalens_strict_geometry_fields(tmp_path, key, value):
    data = config_data()
    data['geometry'][key] = value
    with pytest.raises((ValueError, TypeError)):
        write_config(tmp_path, data)


@pytest.mark.parametrize('key,value', [('phase_convention', 'sign_inverted_design_coordinate'),
    ('validation_status', 'made_up'), ('incidence', 'oblique'), ('polarization', 'cross_polarized'),
    ('pillar_height_um', True)])
def test_metadata_rejects_unsupported_physics(tmp_path, key, value):
    data = config_data()
    spec = data['geometry']['phase_library']
    meta = json.loads(Path(spec['metadata_path']).read_text(encoding='utf-8'))
    meta[key] = value
    path = tmp_path / 'metadata.json'
    path.write_text(json.dumps(meta), encoding='utf-8')
    spec.update(metadata_path=str(path), metadata_sha256=sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ValueError):
        library(data)


def test_metalens_cannot_be_promoted_by_filling_process_fields(tmp_path):
    data = config_data()
    data['project']['release_status'] = 'released'
    data['fabrication'].update(profile_id='calibrated-example', provenance='test fixture')
    data['dose'].update(kind='scalar', value=100, unit='uC/cm^2')
    data['layout']['polarity'] = 'clear'
    for key in data['drc']:
        if key != 'fail_on_warning':
            data['drc'][key] = 0
    with pytest.raises(ValueError, match='engineering_preview only'):
        write_config(tmp_path, data)


def test_library_changes_affect_identity(tmp_path):
    data = config_data()
    before = write_config(tmp_path, data).identity_sha256
    data['geometry']['phase_library']['csv_sha256'] = 'f' * 64
    assert before != write_config(tmp_path, data).identity_sha256


def test_gds_opt_out_preserves_three_files(tmp_path):
    data = config_data()
    data['geometry'].update(aperture_diameter_um=3, focal_length_um=3)
    data['export']['gds']['enabled'] = False
    data['export']['dpi'] = 30
    result = generate_blueprint(write_config(tmp_path, data))
    assert result.drc.passed
    assert len(result.output_files) == 3
    assert not list(result.case_dir.glob('*.gds'))
