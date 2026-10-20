"""Independent metalens preview; phase colors describe nominal states only."""
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.collections import PolyCollection
from matplotlib.figure import Figure
import numpy as np


def save_preview(nominal, corrected, summary, path, *, dpi=180):
    fig = Figure(figsize=(13, 7), layout='constrained')
    FigureCanvasAgg(fig)
    axes = fig.subplots(2, 2)
    polygons = [np.asarray(f.polygon.exterior.coords) for f in corrected.features]
    optical = nominal.metadata['optical_design']
    for axis, key, title in zip(axes.flat[:3], ('target_phase_deg', 'library_phase_deg', 'phase_error_deg'),
                                ('Target phase (deg)', 'Nominal library phase (deg)', 'Nominal lookup error (deg)')):
        values = [f.metadata[key] for f in corrected.features]
        coll = PolyCollection(polygons, array=np.array(values), cmap='viridis', edgecolors='none', rasterized=True)
        if key != 'phase_error_deg':
            coll.set_clim(-180, 180)
        else:
            limit = max(abs(v) for v in values) or 1
            coll.set_clim(-limit, limit)
        axis.add_collection(coll)
        axis.autoscale_view()
        axis.set_aspect('equal')
        axis.set(xlabel='x (um)', ylabel='y (um)', title=title)
        fig.colorbar(coll, ax=axis, shrink=.8)
    axis = axes.flat[3]
    coll = PolyCollection(polygons, facecolors='#23649A', edgecolors='none', rasterized=True)
    axis.add_collection(coll)
    center = corrected.boundary.centroid
    span = optical['period_um'] * 3
    axis.set(xlim=(center.x-span, center.x+span), ylim=(center.y-span, center.y+span),
             xlabel='x (um)', ylabel='y (um)', title='Corrected polygons: center detail', aspect='equal')
    fig.suptitle(f"Engineering preview | {len(polygons)} pillars | NO full-device optical validation\n"
                 f"Nominal phase error max/RMS = {optical['phase_error_max_deg']:.2f}/{optical['phase_error_rms_deg']:.2f} deg")
    fig.savefig(path, dpi=dpi)
