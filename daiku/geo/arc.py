from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import math

from daiku.geo.base import GeoBase, V3D


class ArcDirection(str, Enum):
    """Direction of the arc sweep."""

    CW = "cw"
    CCW = "ccw"


# ---------------------------------------------------------------------------
# Configuration strategies
# ---------------------------------------------------------------------------


def _point_from_angle(center: V3D, radius: float, angle: float) -> V3D:
    """Compute a point on a circle given an angle."""

    return V3D(
        center.x + radius * math.cos(angle),
        center.y + radius * math.sin(angle),
        center.z,
    )


class ArcConfig(ABC):
    """Base configuration strategy for defining an arc."""

    @abstractmethod
    def compute(self, arc: "Arc") -> None:
        """Populate ``arc`` with the full geometric description."""


@dataclass
class CenterArcConfig(ArcConfig):
    center: V3D
    radius: float
    start_angle: float
    end_angle: float
    direction: ArcDirection = ArcDirection.CCW

    def compute(self, arc: "Arc") -> None:  # pragma: no cover - thin delegation
        arc.center = self.center
        arc.radius = self.radius
        arc.start_angle = self.start_angle
        arc.end_angle = self.end_angle
        arc.direction = self.direction
        arc.start = _point_from_angle(self.center, self.radius, self.start_angle)
        arc.end = _point_from_angle(self.center, self.radius, self.end_angle)
        if self.direction is ArcDirection.CCW:
            sweep = (self.end_angle - self.start_angle) % (2 * math.pi)
            mid_angle = self.start_angle + sweep / 2.0
        else:
            sweep = (self.start_angle - self.end_angle) % (2 * math.pi)
            mid_angle = self.start_angle - sweep / 2.0
        arc.mid = _point_from_angle(self.center, self.radius, mid_angle)


@dataclass
class ThreePointArcConfig(ArcConfig):
    start: V3D
    mid: V3D
    end: V3D

    def compute(self, arc: "Arc") -> None:
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.mid.x, self.mid.y
        x3, y3 = self.end.x, self.end.y

        temp = x2 * x2 + y2 * y2
        bc = (x1 * x1 + y1 * y1 - temp) / 2.0
        cd = (temp - x3 * x3 - y3 * y3) / 2.0
        det = (x1 - x2) * (y2 - y3) - (x2 - x3) * (y1 - y2)
        if abs(det) < 1.0e-10:
            raise ValueError("Points are collinear")

        cx = (bc * (y2 - y3) - cd * (y1 - y2)) / det
        cy = ((x1 - x2) * cd - (x2 - x3) * bc) / det
        cz = self.start.z
        arc.center = V3D(cx, cy, cz)

        arc.radius = math.hypot(cx - x1, cy - y1)

        arc.start_angle = math.atan2(y1 - cy, x1 - cx)
        arc.end_angle = math.atan2(y3 - cy, x3 - cx)

        orientation = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        arc.direction = ArcDirection.CCW if orientation > 0 else ArcDirection.CW

        arc.start = self.start
        arc.end = self.end
        arc.mid = self.mid


@dataclass
class EndpointsArcConfig(ArcConfig):
    start: V3D
    end: V3D
    radius: float
    direction: ArcDirection = ArcDirection.CCW

    def compute(self, arc: "Arc") -> None:
        x1, y1 = self.start.x, self.start.y
        x2, y2 = self.end.x, self.end.y

        dx = x2 - x1
        dy = y2 - y1
        q = math.hypot(dx, dy)
        if q == 0:
            raise ValueError("Start and end points cannot be the same")
        if self.radius < q / 2.0:
            raise ValueError("Radius too small for the given points")

        mx = (x1 + x2) / 2.0
        my = (y1 + y2) / 2.0
        h = math.sqrt(self.radius * self.radius - (q / 2.0) * (q / 2.0))
        ux = -dy / q
        uy = dx / q
        if self.direction is ArcDirection.CCW:
            cx = mx + ux * h
            cy = my + uy * h
        else:
            cx = mx - ux * h
            cy = my - uy * h

        arc.center = V3D(cx, cy, self.start.z)
        arc.radius = self.radius
        arc.direction = self.direction

        arc.start_angle = math.atan2(y1 - cy, x1 - cx)
        arc.end_angle = math.atan2(y2 - cy, x2 - cx)
        arc.start = self.start
        arc.end = self.end
        if self.direction is ArcDirection.CCW:
            sweep = (arc.end_angle - arc.start_angle) % (2 * math.pi)
            mid_angle = arc.start_angle + sweep / 2.0
        else:
            sweep = (arc.start_angle - arc.end_angle) % (2 * math.pi)
            mid_angle = arc.start_angle - sweep / 2.0
        arc.mid = _point_from_angle(arc.center, self.radius, mid_angle)


# ---------------------------------------------------------------------------
# Arc geometry
# ---------------------------------------------------------------------------


@dataclass(init=False)
class Arc(GeoBase):
    """A circular arc defined using a configuration strategy."""

    center: V3D
    radius: float
    start_angle: float
    end_angle: float
    direction: ArcDirection
    start: V3D
    end: V3D
    mid: V3D

    def __init__(self, gid: str, config: ArcConfig):
        super().__init__(gid)
        config.compute(self)

    @classmethod
    def from_center(
        cls,
        gid: str,
        center: V3D,
        radius: float,
        start_angle: float,
        end_angle: float,
        direction: ArcDirection = ArcDirection.CCW,
    ) -> "Arc":
        """Construct an :class:`Arc` from a center based definition."""

        return cls(
            gid,
            CenterArcConfig(center, radius, start_angle, end_angle, direction),
        )

    @classmethod
    def from_points(cls, gid: str, start: V3D, mid: V3D, end: V3D) -> "Arc":
        """Construct an :class:`Arc` from three points."""

        return cls(gid, ThreePointArcConfig(start, mid, end))

    @classmethod
    def from_endpoints(
        cls,
        gid: str,
        start: V3D,
        end: V3D,
        radius: float,
        direction: ArcDirection = ArcDirection.CCW,
    ) -> "Arc":
        """Construct an :class:`Arc` from two end points and a radius."""

        return cls(gid, EndpointsArcConfig(start, end, radius, direction))
