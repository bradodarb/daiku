from daiku.geo.base import GeoBase, V3D


class Position(GeoBase):
    def __init__(self, gid: str, o: V3D, d: V3D, a: V3D):
        """A position in 3D space.

        Parameters
        ----------
        gid:
            Global identifier for the object.
        o:
            Origin of the position.
        d:
            Direction vector (typically the local x-axis).
        a:
            Axis vector (typically the local z-axis).
        """

        super().__init__(gid)

        # Store the origin vector directly and break the orientation vectors
        # into their components for easy access.  The previous implementation
        # attempted to reference undefined variables (``p``/``dx``/``ax`` ...)
        # which raised ``NameError`` on instantiation.
        self.o = o
        self.dx, self.dy, self.dz = d.x, d.y, d.z
        self.ax, self.ay, self.az = a.x, a.y, a.z
