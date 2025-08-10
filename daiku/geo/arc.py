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
    def compute(
        self,
    ) -> tuple[V3D, float, float, float, ArcDirection, V3D, V3D, V3D]:
        """Return the full geometric description of the arc."""


@dataclass
class CenterArcConfig(ArcConfig):
    center: V3D
    radius: float
    start_angle: float
    end_angle: float
    direction: ArcDirection = ArcDirection.CCW

    def compute(self):  # pragma: no cover - thin delegation
        start = _point_from_angle(self.center, self.radius, self.start_angle)
        end = _point_from_angle(self.center, self.radius, self.end_angle)
        if self.direction is ArcDirection.CCW:
            sweep = (self.end_angle - self.start_angle) % (2 * math.pi)
            mid_angle = self.start_angle + sweep / 2.0
        else:
            sweep = (self.start_angle - self.end_angle) % (2 * math.pi)
            mid_angle = self.start_angle - sweep / 2.0
        mid = _point_from_angle(self.center, self.radius, mid_angle)
        return (
            self.center,
            self.radius,
            self.start_angle,
            self.end_angle,
            self.direction,
            start,
            end,
            mid,
        )


@dataclass
class ThreePointArcConfig(ArcConfig):
    start: V3D
    mid: V3D
    end: V3D

    def compute(self):
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
        center = V3D(cx, cy, cz)

        radius = math.hypot(cx - x1, cy - y1)

        start_angle = math.atan2(y1 - cy, x1 - cx)
        end_angle = math.atan2(y3 - cy, x3 - cx)

        orientation = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        direction = ArcDirection.CCW if orientation > 0 else ArcDirection.CW

        return (
            center,
            radius,
            start_angle,
            end_angle,
            direction,
            self.start,
            self.end,
            self.mid,
        )


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
        (
            self.center,
            self.radius,
            self.start_angle,
            self.end_angle,
            self.direction,
            self.start,
            self.end,
            self.mid,
        ) = config.compute()

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
