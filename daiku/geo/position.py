from daiku.geo.base import GeoBase, V3D


class Position(GeoBase):
    def __init__(self, gid: str, o: V3D, d: V3D, a: V3D):
        super().__init__(gid)
        self.p = p
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.ax = ax
        self.ay = ay
        self.az = az
