"""Minimal standard GDSII: integer-grid BOUNDARY children and translated SREFs.

No MEX, solver, optional binary library, or compound-GDS records. Deduplication
uses actual corrected vertices, never nominal optical state identifiers.
"""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import struct

from blueprint_core.output.dxf import _polygon_vertices
from blueprint_core.models import LayoutPlan


def _record(kind: int, datatype: int, payload: bytes = b'') -> bytes:
    if len(payload) % 2:
        payload += b'\0'
    if len(payload) + 4 > 65535:
        raise ValueError('GDS record exceeds standard size')
    return struct.pack('>HBB', len(payload) + 4, kind, datatype) + payload


def _real8(value: float) -> bytes:
    if value == 0:
        return bytes(8)
    sign = 128 if value < 0 else 0
    value = abs(value)
    exponent = 64
    while value >= 1:
        value /= 16
        exponent += 1
    while value < 1 / 16:
        value *= 16
        exponent -= 1
    mantissa = round(value * (1 << 56))
    if mantissa == 1 << 56:
        mantissa >>= 4
        exponent += 1
    if not 0 < exponent < 128:
        raise ValueError('GDS real8 exponent overflow')
    return bytes([sign | exponent]) + mantissa.to_bytes(7, 'big')


def _decode_real8(raw: bytes) -> float:
    if raw == bytes(8):
        return 0.0
    return (-1 if raw[0] & 128 else 1) * int.from_bytes(raw[1:], 'big') / (1 << 56) * 16.0 ** ((raw[0] & 127) - 64)


def _points_bytes(points) -> bytes:
    return b''.join(struct.pack('>ii', int(x), int(y)) for x, y in points)


def readback_gds(path: Path) -> dict:
    """Parse this strict standard subset; reject missing/invalid hierarchy."""
    raw = path.read_bytes()
    cursor = 0
    cells = {}
    cell = None
    element = None
    units = None
    ended = False
    version = None
    while cursor < len(raw):
        if len(raw) - cursor < 4:
            raise ValueError('truncated GDS header')
        length, kind, dtype = struct.unpack_from('>HBB', raw, cursor)
        if length < 4 or length % 2 or cursor + length > len(raw):
            raise ValueError('invalid GDS record length')
        payload = raw[cursor + 4:cursor + length]
        cursor += length
        if kind == 0:
            version = struct.unpack('>h', payload)[0]
        elif kind == 3:
            units = [_decode_real8(payload[:8]), _decode_real8(payload[8:])]
        elif kind == 6:
            cell = payload.rstrip(b'\0').decode('ascii')
            if cell in cells:
                raise ValueError('duplicate GDS cell')
            cells[cell] = []
        elif kind in (8, 10):
            element = {'kind': 'boundary' if kind == 8 else 'sref'}
        elif kind in (13, 14):
            element['layer' if kind == 13 else 'datatype'] = struct.unpack('>h', payload)[0]
        elif kind == 18:
            element['sname'] = payload.rstrip(b'\0').decode('ascii')
        elif kind == 16:
            if len(payload) % 8:
                raise ValueError('invalid GDS XY')
            element['xy'] = list(struct.iter_unpack('>ii', payload))
        elif kind == 17:
            if cell is None or element is None:
                raise ValueError('GDS ENDEL without element')
            cells[cell].append(element)
            element = None
        elif kind == 7:
            cell = None
        elif kind == 4:
            ended = True
            if cursor != len(raw):
                raise ValueError('GDS trailing records')
        elif kind not in (1, 2, 5):
            raise ValueError(f'unsupported GDS record {kind}')
    if not ended or element is not None or cell is not None or units is None or version != 600:
        raise ValueError('incomplete GDS library')
    referenced = {e['sname'] for entries in cells.values() for e in entries if e['kind'] == 'sref'}
    tops = set(cells) - referenced
    if not referenced.issubset(cells) or len(tops) != 1:
        raise ValueError('invalid GDS hierarchy')
    top = next(iter(tops))
    flattened = []
    for ref in cells[top]:
        if ref['kind'] != 'sref' or len(ref.get('xy', [])) != 1:
            raise ValueError('top must contain scalar translated SREFs only')
        offset = ref['xy'][0]
        for poly in cells[ref['sname']]:
            points = poly.get('xy', [])
            if poly['kind'] != 'boundary' or len(points) < 4 or points[0] != points[-1]:
                raise ValueError('child must contain closed BOUNDARY')
            flattened.append((poly['layer'], poly['datatype'], tuple((x + offset[0], y + offset[1]) for x, y in points[:-1])))
    return {'structure_count': len(cells), 'top_cell': top, 'reference_count': len(cells[top]),
            'database_unit_in_user_units': units[0], 'database_unit_m': units[1], 'flattened': flattened}


def write_gds(layout: LayoutPlan, path: Path, *, grid_nm: float,
              layer: int, datatype: int) -> dict:
    if not math.isfinite(grid_nm) or grid_nm <= 0:
        raise ValueError('positive GDS grid required')
    for value in (layer, datatype):
        if type(value) is not int or not 0 <= value <= 32767:
            raise ValueError('GDS layer/datatype must be integers in [0,32767]')
    step_um = grid_nm / 1000
    shapes = {}
    refs = []
    expected = []
    for feature in layout.features:
        points = _polygon_vertices(feature.polygon, feature_id=feature.feature_id)
        integer = []
        for x, y in points:
            ix, iy = round(x / step_um), round(y / step_um)
            if max(abs(ix), abs(iy)) > 2147483647:
                raise ValueError('GDS coordinate overflow')
            if abs(x - ix * step_um) > 1e-9 or abs(y - iy * step_um) > 1e-9:
                raise ValueError('GDS input is off configured writer grid')
            integer.append((ix, iy))
        ox, oy = integer[0]
        local = tuple((x - ox, y - oy) for x, y in integer)
        if local not in shapes:
            shapes[local] = f'SHAPE_{len(shapes):06d}'
        refs.append((shapes[local], (ox, oy)))
        expected.append((layer, datatype, tuple(integer)))
    date = struct.pack('>12h', *([2000, 1, 1, 0, 0, 0] * 2))
    chunks = [_record(0, 2, struct.pack('>h', 600)), _record(1, 2, date),
              _record(2, 6, b'BLUEPRINT'), _record(3, 5, _real8(step_um) + _real8(grid_nm * 1e-9))]
    for points, name in shapes.items():
        chunks.extend([_record(5, 2, date), _record(6, 6, name.encode('ascii')),
                       _record(8, 0), _record(13, 2, struct.pack('>h', layer)),
                       _record(14, 2, struct.pack('>h', datatype)),
                       _record(16, 3, _points_bytes((*points, points[0]))), _record(17, 0), _record(7, 0)])
    chunks.extend([_record(5, 2, date), _record(6, 6, b'BLUEPRINT_TOP')])
    for name, offset in refs:
        chunks.extend([_record(10, 0), _record(18, 6, name.encode('ascii')),
                       _record(16, 3, _points_bytes([offset])), _record(17, 0)])
    chunks.extend([_record(7, 0), _record(4, 0)])
    path.write_bytes(b''.join(chunks))
    report = readback_gds(path)
    if Counter(report.pop('flattened')) != Counter(expected):
        raise ValueError('GDS round-trip corrected geometry mismatch')
    if not math.isclose(report['database_unit_m'], grid_nm * 1e-9, rel_tol=1e-12):
        raise ValueError('GDS database unit mismatch')
    report.update({'user_unit_m': 1e-6, 'layer': layer, 'datatype': datatype,
                   'deduplication': 'actual corrected integer-grid polygons',
                   'roundtrip_geometry_verified': True})
    return report
