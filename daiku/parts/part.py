"""Representation of three‑dimensional parts.

Parts are the building blocks for higher level assemblies such as doors,
windows or cabinet boxes.  A part behaves like a six‑sided block by default
with each face represented by a :class:`~daiku.parts.plane.Plane` instance.

Faces can store 2‑D geometry that describes machining operations; the
orientation of each face is derived from the size of the part and its origin
within a global coordinate system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from daiku.geo.base import GeoBase, V3D
from daiku.geo.point import Point

from .plane import Plane


@dataclass
class Part(GeoBase):
    """A rectangular block shaped part.

    Parameters
    ----------
    gid:
        Identifier for the part.
    origin:
        The lower‑left, front corner of the part in 3‑D space.
    width, height, depth:
        Dimensions of the part along the X, Y and Z axes respectively.
    """

    origin: Point
    width: float
    height: float
    depth: float
    sides: Dict[str, Plane] = field(init=False)

    def __post_init__(self) -> None:
        self.sides = self._create_sides()

    # ------------------------------------------------------------------
    # Face helpers
    # ------------------------------------------------------------------
    def _create_sides(self) -> Dict[str, Plane]:
        """Create the six default planes describing this part."""

        o = self.origin
        w, h, d = self.width, self.height, self.depth

        sides = {
            "front": Plane(f"{self.gid}_front", o, V3D(0, 0, 1)),
            "back": Plane(
                f"{self.gid}_back",
                Point(f"{self.gid}_back_o", o.x, o.y, o.z + d),
                V3D(0, 0, -1),
            ),
            "left": Plane(f"{self.gid}_left", o, V3D(-1, 0, 0)),
            "right": Plane(
                f"{self.gid}_right",
                Point(f"{self.gid}_right_o", o.x + w, o.y, o.z),
                V3D(1, 0, 0),
            ),
            "bottom": Plane(f"{self.gid}_bottom", o, V3D(0, -1, 0)),
            "top": Plane(
                f"{self.gid}_top",
                Point(f"{self.gid}_top_o", o.x, o.y + h, o.z),
                V3D(0, 1, 0),
            ),
        }
        return sides

    # Public API -------------------------------------------------------
    def get_side(self, name: str) -> Plane:
        """Return one of the part's sides by name."""

        return self.sides[name]

