from dataclasses import dataclass

from daiku.geo.base import GeoBase, V3D


@dataclass
class Position(GeoBase):
    o: V3D
    d: V3D
    a: V3D

    def __post_init__(self) -> None:
        """Break orientation vectors into their components."""

        self.dx, self.dy, self.dz = self.d.x, self.d.y, self.d.z
        self.ax, self.ay, self.az = self.a.x, self.a.y, self.a.z
