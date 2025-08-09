from daiku.geo.base import GeoBase, V3D

from dataclasses import dataclass


@dataclass
class Line(GeoBase):
    gid: str
    s: V3D
    e: V3D

    def __post_init__(self):
        super().__init__(self.gid)
