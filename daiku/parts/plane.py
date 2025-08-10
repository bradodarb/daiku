"""Geometry helpers for part faces.

This module defines a :class:`Plane` that represents a single face of a
three‑dimensional part.  Each plane stores an origin, a normal and a list of
2D shapes that describe features on that face (for example cut‑outs or tool
paths for CNC machining).

The implementation relies on the basic geometry primitives defined under the
``daiku.geo`` package such as :class:`~daiku.geo.point.Point` and
``V3D``/``V2D`` vectors.
"""

from dataclasses import dataclass, field
from typing import List

from daiku.geo.base import GeoBase, V2D, V3D
from daiku.geo.point import Point


@dataclass
class Plane(GeoBase):
    """A single planar face of a part.

    Parameters
    ----------
    gid:
        Identifier for the plane.
    origin:
        A point on the plane.  Typically the lower‑left corner of the face in
        the part's local coordinate system.
    normal:
        The outward facing normal vector.
    shapes:
        Optional list of 2‑D shapes (each represented as a list of ``V2D``
        points) that live on this plane.  These shapes can later be translated
        to CNC tool paths.
    """

    gid: str
    origin: Point
    normal: V3D
    shapes: List[List[V2D]] = field(default_factory=list)

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        # Initialise GeoBase with the provided identifier.
        super().__init__(self.gid)

    def add_shape(self, shape: List[V2D]) -> None:
        """Attach a 2‑D shape to this plane.

        Parameters
        ----------
        shape:
            A sequence of :class:`~daiku.geo.base.V2D` points describing the
            shape to add.
        """

        self.shapes.append(shape)

