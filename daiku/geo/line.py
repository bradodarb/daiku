from dataclasses import dataclass

from daiku.geo.base import GeoBase, V3D


@dataclass
class Line(GeoBase):
    s: V3D
    e: V3D
