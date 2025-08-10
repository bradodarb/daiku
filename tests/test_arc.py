import pathlib
import sys

# Ensure the package root is on the import path when running tests without
# installing the package.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import math

from daiku.geo.base import V3D
from daiku.geo.arc import (
    Arc,
    ArcDirection,
    CenterArcConfig,
    EndpointsArcConfig,
    ThreePointArcConfig,
)


def test_arc_initializes_components():
    center = V3D(1.0, 2.0, 3.0)
    cfg = CenterArcConfig(center, 5.0, 0.0, 1.0, ArcDirection.CW)
    arc = Arc("gid", cfg)

    assert arc.center == center
    assert arc.radius == 5.0
    assert arc.start_angle == 0.0
    assert arc.end_angle == 1.0
    assert arc.direction is ArcDirection.CW


def test_arc_constructed_from_points():
    start = V3D(1.0, 0.0, 0.0)
    mid = V3D(math.sqrt(0.5), math.sqrt(0.5), 0.0)
    end = V3D(0.0, 1.0, 0.0)

    cfg = ThreePointArcConfig(start, mid, end)
    arc = Arc("gid", cfg)

    assert math.isclose(arc.center.x, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.center.y, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.radius, 1.0, rel_tol=1e-9)
    assert math.isclose(arc.start_angle, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.end_angle, math.pi / 2, rel_tol=1e-9)
    assert arc.direction is ArcDirection.CCW
    assert arc.start == start
    assert arc.mid == mid
    assert arc.end == end


def test_arc_constructed_from_endpoints_and_radius():
    start = V3D(1.0, 0.0, 0.0)
    end = V3D(0.0, 1.0, 0.0)
    cfg = EndpointsArcConfig(start, end, 1.0, ArcDirection.CCW)
    arc = Arc("gid", cfg)

    assert math.isclose(arc.center.x, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.center.y, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.radius, 1.0, rel_tol=1e-9)
    assert math.isclose(arc.start_angle, 0.0, abs_tol=1e-9)
    assert math.isclose(arc.end_angle, math.pi / 2, rel_tol=1e-9)
    assert arc.direction is ArcDirection.CCW
    assert arc.start == start
    assert arc.end == end
    assert math.isclose(arc.mid.x, math.sqrt(0.5), rel_tol=1e-9)
    assert math.isclose(arc.mid.y, math.sqrt(0.5), rel_tol=1e-9)
