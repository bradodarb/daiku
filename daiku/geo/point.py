from daiku.geo.base import GeoBase, V3D


class Point(GeoBase):
    def __init__(self, gid: str, x: float, y: float, z: float = 0.0):
        super().__init__(gid)
        self._position = V3D(x, y, z)

    @staticmethod
    def from_vector(gid: str, v3d: V3D) -> 'Point':
        return Point(gid, v3d.x, v3d.y, v3d.z)

    @property
    def x(self) -> float:
        return self._position.x

    @property
    def y(self) -> float:
        return self._position.y

    @property
    def z(self) -> float:
        return self._position.z

    @x.setter
    def x(self, value: float) -> None:
        self._position.x = value

    @y.setter
    def y(self, value: float) -> None:
        self._position.y = value

    @z.setter
    def z(self, value: float) -> None:
        self._position.z = value
