import util as u
import h3
import numpy as np
from scipy.spatial.transform import Rotation as R


def latlon_to_cartesian(lat, lon):
    """Convert lat/lon degrees to 3D Cartesian coordinates."""
    lat_rad = np.deg2rad(lat)
    lon_rad = np.deg2rad(lon)
    x = np.cos(lat_rad) * np.cos(lon_rad)
    y = np.cos(lat_rad) * np.sin(lon_rad)
    z = np.sin(lat_rad)
    return np.array([x, y, z])

def cartesian_to_latlon(vec):
    """Convert 3D Cartesian coordinates to lat/lon degrees."""
    x, y, z = vec
    lat_rad = np.arcsin(z)
    lon_rad = np.arctan2(y, x)
    return np.rad2deg(lat_rad), np.rad2deg(lon_rad)

def rotate_cells(cells, new_center_lat, new_center_lon):
    """Rotate a set of H3 cells to a new center point."""
    if not cells:
        return []

    resolution = h3.h3_get_resolution(cells[0])

    original_centers_latlon = [h3.cell_to_latlng(cell) for cell in cells]
    original_centers_cartesian = [latlon_to_cartesian(lat, lon) for lat, lon in original_centers_latlon]

    original_cluster_center = np.mean(original_centers_cartesian, axis=0)
    original_cluster_center /= np.linalg.norm(original_cluster_center)

    new_cluster_center = latlon_to_cartesian(new_center_lat, new_center_lon)

    rotation, _ = R.align_vectors([new_cluster_center], [original_cluster_center])

    rotated_centers_cartesian = rotation.apply(original_centers_cartesian)

    rotated_centers_latlon = [cartesian_to_latlon(vec) for vec in rotated_centers_cartesian]

    new_cells = [h3.latlng_to_cell(lat, lon, resolution) for lat, lon in rotated_centers_latlon]

    return new_cells


cells = [
    '81463ffffffffff',
    '8146bffffffffff',
    '81713ffffffffff',
    '81467ffffffffff',
    '8147bffffffffff',
    '8171bffffffffff',
    '815b3ffffffffff',
    '815afffffffffff',
    '81333ffffffffff',
    '815a7ffffffffff',
    '815b7ffffffffff',
    '81703ffffffffff',
    '81707ffffffffff',
    '8133bffffffffff',
    '81233ffffffffff',
    '81477ffffffffff',
    '81237ffffffffff',
    '8136bffffffffff',
    '8136fffffffffff',
    '81507ffffffffff',
    '81517ffffffffff',
    '81793ffffffffff',
    '8188fffffffffff',
    '8179bffffffffff',
    '8188bffffffffff',
    '815c3ffffffffff',
    '81373ffffffffff',
    '81377ffffffffff',
    '8146fffffffffff',
    '81717ffffffffff',
]

# TODO: rotate cells so they don't cross the antimeridian. keep them close to the equator

edges = u.cells_to_edges(cells)

with u.svg('figs/conn_comp.svg') as ax:
    edges1 = edges - u.twinning(
        # '1198f50703c3ffff',
        # '1198f50703cbffff',
    )
    u.plot_edges(edges1, ax=ax)

