from dataclasses import dataclass

from .ensemble_surface_provider import SurfaceAddress
from enum import Enum


class LayerTypes(str, Enum):
    HILLSHADING = "Hillshading2DLayer"
    MAP3D = "MapLayer"
    COLORMAP = "ColormapLayer"
    WELL = "WellsLayer"
    WELLTOPSLAYER = "GeoJsonLayer"
    DRAWING = "DrawingLayer"
    FAULTPOLYGONS = "FaultPolygonsLayer"
    GEOJSON = "GeoJsonLayer"


class LayerNames(str, Enum):
    HILLSHADING = "Surface (hillshading)"
    MAP3D = "3D Map"
    COLORMAP = "Surface (color)"
    WELL = "Wells"
    WELLTOPSLAYER = "Well tops"
    DRAWING = "Drawings"
    FAULTPOLYGONS = "Fault polygons"
    GEOJSON = "GeoJsonLayer"



@dataclass(frozen=True)
class QualifiedSurfaceAddress:
    provider_id: str
    address: SurfaceAddress


@dataclass(frozen=True)
class QualifiedDiffSurfaceAddress:
    provider_id_a: str
    address_a: SurfaceAddress
    provider_id_b: str
    address_b: SurfaceAddress
