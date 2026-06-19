from __future__ import annotations

from pathlib import Path
from typing import Any

from .units import Quantity, mm, inch


def normalize_length_to_mm(value: Any, units: str = 'SI') -> Quantity | None:
    if value is None:
        return None
    if isinstance(value, Quantity):
        return value.to(mm)
    if units.upper() == 'SI':
        return value * mm
    return (value * inch).to(mm)


def _estimate_sectionproperties_mesh_size(geom: Any) -> float:
    try:
        bbox = geom.calculate_extents()
        width = bbox[1][0] - bbox[0][0]
        height = bbox[1][1] - bbox[0][1]
        mesh_size = min(max(width, height) / 20.0, 10.0)
        return float(mesh_size)
    except Exception:
        return 5.0


def _create_sectionproperties_geometry_from_dict(
    geometry_dict: dict,
    sp_lib: Any,
    sp_geom: Any,
    units: str = 'SI'
) -> tuple[Any, dict]:
    geom_type = geometry_dict.get('type', '').lower()
    dims: dict[str, Any] = {}

    if geom_type in ('i_section', 'i'):
        d = normalize_length_to_mm(geometry_dict['d'], units).magnitude
        b = normalize_length_to_mm(geometry_dict['b'], units).magnitude
        t_f = normalize_length_to_mm(geometry_dict['t_f'], units).magnitude
        t_w = normalize_length_to_mm(geometry_dict['t_w'], units).magnitude
        r = normalize_length_to_mm(geometry_dict.get('r', min(t_f, t_w) / 2), units).magnitude
        n_r = int(geometry_dict.get('n_r', 16))
        dims = {'h_w': d, 't_w': t_w, 'b': b, 't_f': t_f}
        return sp_lib.i_section(d=d, b=b, t_f=t_f, t_w=t_w, r=r, n_r=n_r), dims

    if geom_type in ('rectangular_section', 'rectangle', 'rect'):
        width = normalize_length_to_mm(geometry_dict['width'], units).magnitude
        height = normalize_length_to_mm(geometry_dict['height'], units).magnitude
        dims = {'h_w': height, 't_w': None, 'b': width, 't_f': None}
        return sp_lib.rectangular_section(b=width, d=height), dims

    if geom_type in ('box_girder_section', 'box', 'box_section'):
        d = normalize_length_to_mm(geometry_dict['d'], units).magnitude
        b = normalize_length_to_mm(geometry_dict['b'], units).magnitude
        t_f = normalize_length_to_mm(geometry_dict['t_f'], units).magnitude
        t_w = normalize_length_to_mm(geometry_dict['t_w'], units).magnitude
        r = normalize_length_to_mm(geometry_dict.get('r', 0), units).magnitude
        n_r = int(geometry_dict.get('n_r', 16))
        dims = {'h_w': d, 't_w': t_w, 'b': b, 't_f': t_f}
        return sp_lib.box_girder_section(d=d, b=b, t_f=t_f, t_w=t_w, r=r, n_r=n_r), dims

    if geom_type in ('angle_section', 'angle', 'l_section'):
        d = normalize_length_to_mm(geometry_dict['d'], units).magnitude
        b = normalize_length_to_mm(geometry_dict['b'], units).magnitude
        t = normalize_length_to_mm(geometry_dict['t'], units).magnitude
        r = normalize_length_to_mm(geometry_dict.get('r', 0), units).magnitude
        n_r = int(geometry_dict.get('n_r', 16))
        dims = {'h_w': d, 't_w': t, 'b': b, 't_f': None}
        return sp_lib.angle_section(d=d, b=b, t=t, r=r, n_r=n_r), dims

    if geom_type in ('dxf', 'dxf_file', 'dxf_path'):
        dxf_path = geometry_dict.get('path') or geometry_dict.get('filepath') or geometry_dict.get('file')
        if dxf_path is None:
            raise ValueError("DXF geometry requires a 'path' field pointing to the DXF file.")
        geom = sp_geom.load_dxf(
            dxf_path,
            spline_delta=float(geometry_dict.get('spline_delta', 0.1)),
            degrees_per_segment=float(geometry_dict.get('degrees_per_segment', 5.0)),
        )
        return geom, dims

    raise ValueError(
        f"Unsupported section_properties_source geometry type: {geometry_dict.get('type')}. "
        "Supported types include 'i_section', 'rectangular_section', 'box_girder_section', 'angle_section', and 'dxf'."
    )


def load_sectionproperties_geometry(
    section_geometry: Any,
    mesh_size: float | None = None,
    units: str = 'SI'
) -> tuple[Any, Any, dict[str, Any]]:
    try:
        import sectionproperties.pre.library as sp_lib
        import sectionproperties.pre.geometry as sp_geom
        import sectionproperties.analysis.section as sp_section
    except ImportError as e:
        raise ImportError(
            "sectionproperties is required when section_properties_source='sectionproperties'. "
            "Install the package in the current Python environment."
        ) from e

    if section_geometry is None:
        raise ValueError("section_geometry must be provided when section_properties_source='sectionproperties'.")

    geom = section_geometry
    geometry_dims: dict[str, Any] = {}

    if isinstance(section_geometry, dict):
        geom, geometry_dims = _create_sectionproperties_geometry_from_dict(section_geometry, sp_lib, sp_geom, units)
    elif isinstance(section_geometry, (str, Path)):
        geom = sp_geom.load_dxf(
            section_geometry,
            spline_delta=0.1,
            degrees_per_segment=5.0,
        )
    elif not hasattr(section_geometry, 'create_mesh') or not hasattr(section_geometry, 'calculate_area'):
        raise ValueError(
            "section_geometry must be a sectionproperties Geometry object, a DXF file path, or a dictionary describing the section geometry."
        )

    if mesh_size is None:
        mesh_size = _estimate_sectionproperties_mesh_size(geom)

    geom.create_mesh(mesh_sizes=mesh_size)
    section = sp_section.Section(geom)
    section.calculate_geometric_properties()
    section.calculate_plastic_properties()

    return geom, section, geometry_dims


def plot_sectionproperties_geometry(
    geom: Any,
    section: Any,
    geometry_kwargs: dict | None = None,
    centroid_kwargs: dict | None = None,
):
    geometry_kwargs = geometry_kwargs or {}
    centroid_kwargs = centroid_kwargs or {}

    ax = geom.plot_geometry(**geometry_kwargs)
    section.plot_centroids(**centroid_kwargs)
    return ax
