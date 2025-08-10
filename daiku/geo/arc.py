from dataclasses import dataclass
from enum import Enum

from daiku.geo.base import GeoBase, V3D


class ArcDirection(str, Enum):
    """Direction of the arc sweep."""

    CW = "cw"
    CCW = "ccw"


@dataclass
class Arc(GeoBase):
    """A circular arc defined by a center point and angles."""

    center: V3D
    radius: float
    start_angle: float
    end_angle: float
    direction: ArcDirection = ArcDirection.CCW
