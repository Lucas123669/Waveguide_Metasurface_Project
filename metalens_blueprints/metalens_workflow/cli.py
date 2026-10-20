"""Independent entry point, reusing existing geometry-neutral fabrication tools."""
import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile

from blueprint_core.fabrication.corrections import apply_corrections
from blueprint_core.quality.drc import run_drc
from blueprint_core.output.dxf import write_dxf
from blueprint_core.output.reporting import safe_label
from .config import load_config
from .geometry import build_metalens_layout
from .gds import write_gds
from .preview import save_preview

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Result:
    case_dir: Path | None
    feature_count: int
    drc: object
    output_files: tuple


def generate(cfg, *, preflight_only=False):
    data = cfg.data
    g, f = data['geometry'], data['fabrication']
    nominal = build_metalens_layout(g,base_dir=cfg.path.parent)
    fabrication = {'grid_nm':f['grid_nm'], 'local_correction': {'default': {'operators':[
        {'kind':'edge_offset','value_nm':f['edge_bias_nm'],
         'join_style':f['join_style'],'miter_limit':f['miter_limit']}]}, 'by_region':{}}}
    dose = {**data['dose'], 'response':{'kind':'pass_through'}, 'encoder':{'kind':'external_recipe'}}
    corrected = apply_corrections(nominal,fabrication,dose,data['layout'])
    drc_cfg = {k:v for k,v in data['drc'].items() if v is not None}
    drc_cfg.update(grid_nm=f['grid_nm'],allowed_dxf_layers=[data['layout']['etch_layer']])
    drc = run_drc(corrected,drc_cfg)
    if preflight_only:
        return Result(None,corrected.feature_count,drc,())
    drc.raise_for_errors()
    fmt = lambda v: f'{v:g}'.replace('-','m')
    name = (f"metalens_D{fmt(g['aperture_diameter_um'])}_f{fmt(g['focal_length_um'])}_"
            f"p{fmt(g['period_um'])}_wl{fmt(g['wavelength_nm'])}_square_"
            f"{safe_label(f['profile_id'])}-r{safe_label(f['revision'])}")
    target = cfg.output_root/name
    if target.exists() or target.is_symlink():
        raise FileExistsError(f'case already exists: {target}; use a new revision')
    cfg.output_root.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.stage-',dir=cfg.output_root))
    try:
        dxf_name = name+'.dxf'
        dxf = write_dxf(corrected,stage/dxf_name,version=data['export']['dxf_version'])
        gds = None
        gds_options = data['export']['gds']
        if gds_options['enabled']:
            gds = write_gds(corrected,stage/(name+'.gds'),grid_nm=f['grid_nm'],
                            layer=gds_options['layer'],datatype=gds_options['datatype'])
        save_preview(nominal,corrected,{},stage/'preview.png',dpi=data['export']['dpi'])
        optical = dict(nominal.metadata['optical_design'])
        optical['sites'] = [{'feature_id':s.feature_id,'center_um':list(s.nominal_centroid_um),**s.metadata}
                            for s in nominal.features]
        files = sorted(p.name for p in stage.iterdir())
        source_hashes = {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()
                         for folder in ('metalens_workflow','main') for p in (ROOT/folder).rglob('*.py')}
        import blueprint_core.models as shared
        shared_root = Path(shared.__file__).parent
        shared_hashes = {p.relative_to(shared_root).as_posix():sha256(p.read_bytes()).hexdigest()
                         for p in shared_root.rglob('*.py')}
        report = {'release_status':'engineering_preview','workflow':'independent_metalens',
                  'identity_sha256':cfg.identity_sha256,'source_parameter_sha256':cfg.source_sha256,
                  'config':data,'source_hashes':source_hashes,'shared_core_source_hashes':shared_hashes,
                  'optical_design':optical,'drc':drc.to_dict(),'dxf':dxf,
                  'correction':corrected.metadata['correction_pipeline'],
                  'outputs':{'artifact_names':sorted(files+['layout_report.json']),
                  'sha256':{s:sha256((stage/s).read_bytes()).hexdigest() for s in files}}}
        if gds is not None:
            report['gds'] = gds
        (stage/'layout_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        # Atomic directory rename; never overwrite an existing case.
        if target.exists() or target.is_symlink():
            raise FileExistsError(f'case appeared during generation: {target}')
        stage.rename(target)
    except BaseException:
        if stage.is_dir():
            shutil.rmtree(stage)
        raise
    return Result(target,corrected.feature_count,drc,tuple(sorted(files+['layout_report.json'])))


def main(argv=None):
    parser = argparse.ArgumentParser(description='Independent cylindrical metalens DXF/GDS workflow')
    parser.add_argument('--config',type=Path,default=ROOT/'main'/'parameter.json')
    parser.add_argument('--preflight-only',action='store_true')
    args = parser.parse_args(argv)
    result = generate(load_config(args.config),preflight_only=args.preflight_only)
    print(f'features: {result.feature_count}; DRC passed={result.drc.passed}, errors={result.drc.error_count}, warnings={result.drc.warning_count}')
    print('preflight only; no artifacts written' if args.preflight_only else f'output: {result.case_dir}')
    return 0 if result.drc.passed else 2
