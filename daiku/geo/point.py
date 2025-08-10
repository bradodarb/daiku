from dataclasses import dataclass

from daiku.geo.base import GeoBase, V3D


@dataclass
class Point(GeoBase):
    x: float
    y: float
    z: float = 0.0

    @staticmethod
    def from_vector(gid: str, v3d: V3D) -> 'Point':
        return Point(gid, v3d.x, v3d.y, v3d.z)
