"""
Some utilities that may be used after napari-3d-counter
"""

from __future__ import annotations
from pathlib import Path

import pandas as pd
import napari
import numpy as np
from napari.layers import Shapes, Image
import napari
import click
from h5py import Group
from imaris_ims_file_reader.ims import ims, ims_reader
from napari_3d_counter import Count3D, CellTypeConfig


def segment_by_shapes(
    viewer: napari.Viewer,
    in_path: Path | str,
    out_path: Path | str | None = None,
    summary_path: Path | str | None = None,
):
    """
    takes a shapes layer and uses it to split up the labels of a napari 3d counter

    arguments are viewer, and path to a csv file made by napari-3d-counter
    optionaly takes two other paths for the layers whith changed names, and the
        summary including the number of points in each category
    """
    shapes_layers = [l for l in viewer.layers if isinstance(l, Shapes)]
    if len(shapes_layers) != 1:
        raise ValueError(
            f"There should be exactly 1 shapes layer. There are {len(shapes_layers)}"
        )
    shapes_layer = shapes_layers[0]
    image_layer = next(l for l in viewer.layers if isinstance(l, Image))
    labels = shapes_layer.to_labels(image_layer.data.shape).squeeze().max(axis=0)
    in_path = Path(in_path)
    data = pd.read_csv(in_path)
    for i, row in data.iterrows():
        y_pix = int(row["y"] / shapes_layer.scale[-2])
        x_pix = int(row["x"] / shapes_layer.scale[-1])
        shape_number = labels[y_pix, x_pix]
        if shape_number == 0:
            raise ValueError(f"Point missing a shape at x={row['x']}, y={row['y']}")
        data.loc[i, "cell_type"] = f"{shape_number}_{row['cell_type']}"
    if out_path is None:
        out_path = Path(in_path.with_suffix(".out.csv"))
    data.to_csv(out_path)
    if summary_path is None:
        summary_path = Path(in_path.with_suffix(".summary.csv"))
    data.groupby("cell_type").count()["z"].to_csv(summary_path)
    return data


def read_into_napari(path: str, low_res=False, viewer: napari.Viewer | None = None):
    """
    view an imaris file with napari-3d-counter

    optionaly takes in a viewer, and can optionaly load the low res version
    """
    ims_object = ims(path)
    assert isinstance(ims_object, ims_reader)
    if low_res:
        ims_object.change_resolution_lock(2)
    hf = ims_object.hf
    assert hf is not None
    dset = hf["Scene8/Content"]
    assert isinstance(dset, Group)
    dfs: dict[str, pd.DataFrame] = {}
    for item in dset.values():
        name = item.attrs["Name"][0].decode("utf-8")
        df = pd.DataFrame(np.array(item["Spot"]))
        dfs[name] = df.loc[:, ["PositionX", "PositionY", "PositionZ"]]
        click.echo(f"{name} has length {len(df)}")

    if len(dfs) == 0:
        click.echo("No spots found")
    # get channel names
    dset_info = hf["DataSetInfo"]
    assert isinstance(dset_info, Group)
    image_names: list[str] = []
    for key in dset_info.keys():
        if key.startswith("Channel "):
            name = b"".join(dset_info[key].attrs["Name"]).decode().split("-")[0]
            image_names.append(f"raw-{name}-channel")
    # assert False
    data = ims_object[0, :, :, :, :]
    if viewer is None:
        viewer = napari.Viewer(title=Path(path).name)
    scale = ims_object.resolution
    viewer.add_image(data, channel_axis=0, scale=scale, name=image_names)
    configs: list[CellTypeConfig] = []
    if len(dfs) == 0:
        return viewer
    for name in dfs.keys():
        configs.append(CellTypeConfig(name=name))
    count_3d = Count3D(viewer, configs)
    out_df = pd.DataFrame(
        np.nan,
        columns=["cell_type", "z", "y", "x"],
        index=range(sum(len(v) for v in dfs.values())),
    )
    i = 0
    out_df["cell_type"] = out_df["cell_type"].astype(str)
    for name, df in dfs.items():
        i_max = len(df)
        index = range(i, i_max)
        out_df.loc[index, "cell_type"] = name
        out_df.loc[index, "x"] = df["PositionX"]
        out_df.loc[index, "y"] = df["PositionY"]
        out_df.loc[index, "z"] = df["PositionZ"]
    count_3d.read_points_from_df(out_df)
    viewer.window.add_dock_widget(count_3d)
    return viewer


@click.command("read-into-napari", help="View an imaris file with napari 3d counter")
@click.argument("path", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--low-res/--high-res",
    default=False,
    help=(
        "read at full resolution or a downsampled copy saved in the file. Default is --high-res"
    ),
)
def main(path: str, low_res=False):
    read_into_napari(path, low_res)
    napari.run()
