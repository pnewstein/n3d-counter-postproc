"""
Some utilities that may be used after napari-3d-counter
"""

from __future__ import annotations
from pathlib import Path

import pandas as pd
import napari
import numpy as np
from napari.layers import Shapes, Image

def segment_by_shapes(viewer: napari.Viewer, in_path: Path | str, out_path: Path | str | None = None, summary_path: Path | str | None = None):
    """
    takes a shapes layer and uses it to split up the labels of a napari 3d counter
    """
    shapes_layers = [l for l in viewer.layers if isinstance(l, Shapes)]
    if len(shapes_layers) != 1:
        raise ValueError(f"There should be exactly 1 shapes layer. There are {len(shapes_layers)}")
    shapes_layer = shapes_layers[0]
    image_layer = next(l for l in viewer.layers if isinstance(l, Image))
    labels = shapes_layer.to_labels(np.squeeze(image_layer.data).shape).max(axis=0)
    in_path = Path(in_path)
    data = pd.read_csv(in_path)
    for i, row in data.iterrows():
        shape_number = labels[int(row["y"]), int(row["x"])]
        if shape_number == 0:
            raise ValueError(f"Point missing a shape at x={row['x']}, y={row['y']}")
        data.loc[i, "cell_type"] = f"{shape_number}_{row["cell_type"]}"
    if out_path is None:
        out_path = Path(in_path.with_suffix(".out.csv"))
    data.to_csv(out_path)
    if summary_path is None:
        summary_path = Path(in_path.with_suffix(".summary.csv"))
    data["cell_type"].value_counts().to_csv(summary_path)
    return data
    


