"""Strict configuration for the independent cylindrical-pillar workflow."""
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from pathlib import Path


def obj(value, keys, label):
    if not isinstance(value, dict):
        raise ValueError(f'{label} must be an object')
    if set(value) != set(keys):
        raise ValueError(f'{label}: missing or unknown fields: {set(value) ^ set(keys)}')


def number(value, label, low=None, high=None, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be finite numeric')
    if integer and type(value) is not int:
        raise ValueError(f'{label} must be an integer')
    if (low is not None and value < low) or (high is not None and value > high):
        raise ValueError(f'{label} is out of range')


def validate_geometry(g):
    obj(g, ('kind','length_unit','wavelength_nm','period_um','aperture_diameter_um',
            'focal_length_um','phase_sign','phase_offset_deg','circle_vertices',
            'boundary_vertices','max_candidate_sites','max_quantization_error_deg',
            'dxf_layer','phase_library'), 'geometry')
    if g['kind'] != 'phase_library_metalens_v1' or g['length_unit'] != 'um':
        raise ValueError('only phase_library_metalens_v1 in um is supported')
    for key in ('wavelength_nm','period_um','aperture_diameter_um','focal_length_um'):
        number(g[key], key, 1e-12)
    number(g['phase_sign'], 'phase_sign', integer=True)
    if g['phase_sign'] not in (-1,1):
        raise ValueError('phase_sign must be -1 or +1')
    number(g['phase_offset_deg'], 'phase_offset_deg')
    for key, low in [('circle_vertices',8),('boundary_vertices',64),('max_candidate_sites',1)]:
        number(g[key], key, low, integer=True)
    number(g['max_quantization_error_deg'], 'max_quantization_error_deg', 1e-12, 180)
    lib = g['phase_library']
    obj(lib, ('format','csv_path','csv_sha256','metadata_path','metadata_sha256',
              'allowed_sources','min_transmission','max_phase_gap_deg'), 'phase_library')
    if lib['format'] not in {'matlab_work10','matlab_work11','canonical'}:
        raise ValueError('unsupported CSV format')
    for key in ('csv_path','metadata_path'):
        if not isinstance(lib[key],str) or not lib[key]:
            raise ValueError(f'{key} must be a path')
    for key in ('csv_sha256','metadata_sha256'):
        value = lib[key]
        if not isinstance(value,str) or len(value)!=64 or any(c not in '0123456789abcdef' for c in value):
            raise ValueError(f'{key} must be lowercase SHA256')
    sources = lib['allowed_sources']
    if not isinstance(sources,list) or not sources or not all(isinstance(s,str) for s in sources):
        raise ValueError('allowed_sources must be a nonempty string list')
    if len(set(sources)) != len(sources) or set(sources)-{'simulated','measured','interpolated','unverified'}:
        raise ValueError('invalid or duplicate allowed_sources')
    number(lib['min_transmission'],'min_transmission',0,1)
    number(lib['max_phase_gap_deg'],'max_phase_gap_deg',1e-12,360)


@dataclass(frozen=True)
class Config:
    path: Path
    data: dict
    source_sha256: str

    @property
    def output_root(self):
        path = (self.path.parent / self.data['export']['output_root']).resolve()
        if not path.is_relative_to(self.path.parent):
            raise ValueError('output_root must stay in the main parameter directory')
        return path

    @property
    def identity_sha256(self):
        return sha256(json.dumps(self.data,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def load_config(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    data = json.loads(raw.decode('utf-8'))
    obj(data, ('schema_version','project','geometry','fabrication','dose','layout','drc','export'), 'parameter.json')
    if type(data['schema_version']) is not int or data['schema_version'] != 1:
        raise ValueError('schema_version must be 1')
    obj(data['project'], ('name','release_status'), 'project')
    if data['project']['release_status'] != 'engineering_preview':
        raise ValueError('metalens v1 is engineering_preview only')
    if not isinstance(data['project']['name'],str) or not data['project']['name']:
        raise ValueError('project.name must be nonempty')
    validate_geometry(data['geometry'])
    f = data['fabrication']
    obj(f, ('profile_id','revision','provenance','grid_nm','edge_bias_nm','join_style','miter_limit'), 'fabrication')
    for key in ('profile_id','revision','provenance'):
        if not isinstance(f[key],str) or not f[key]:
            raise ValueError(f'fabrication.{key} must be nonempty')
    number(f['grid_nm'],'grid_nm',1e-12)
    number(f['edge_bias_nm'],'edge_bias_nm')
    number(f['miter_limit'],'miter_limit',1e-12)
    if f['join_style'] != 'miter':
        raise ValueError('join_style must be miter')
    obj(data['dose'], ('kind','value','unit'), 'dose')
    dose = data['dose']
    if dose['kind'] == 'unassigned':
        if dose['value'] is not None or dose['unit'] is not None:
            raise ValueError('unassigned dose must have null value and unit')
    elif dose['kind'] == 'scalar':
        number(dose['value'],'dose.value',1e-12)
        if not isinstance(dose['unit'],str) or not dose['unit']:
            raise ValueError('assigned dose requires a unit')
    else:
        raise ValueError('unsupported dose kind')
    from blueprint_core.config import _validate_layout, _validate_drc
    _validate_layout(data['layout'])
    _validate_drc(data['drc'])
    if data['geometry']['dxf_layer'] != data['layout']['etch_layer']:
        raise ValueError('dxf layers must match')
    e = data['export']
    obj(e, ('output_root','overwrite','dpi','dxf_version','gds'), 'export')
    if e['overwrite'] is not False or e['dxf_version'] != 'R2010':
        raise ValueError('overwrite is forbidden; DXF must be R2010')
    number(e['dpi'],'dpi',1,integer=True)
    if not isinstance(e['output_root'],str) or not e['output_root']:
        raise ValueError('output_root must be nonempty path')
    obj(e['gds'], ('enabled','layer','datatype'), 'gds')
    if type(e['gds']['enabled']) is not bool:
        raise ValueError('gds.enabled must be boolean')
    for key in ('layer','datatype'):
        number(e['gds'][key],f'gds.{key}',0,32767,integer=True)
    cfg = Config(path,data,sha256(raw).hexdigest())
    _ = cfg.output_root
    return cfg
