import pathlib
import sys

# Ensure the package root is on the import path when running tests without
# installing the package.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from daiku.geo.base import V3D
from daiku.geo.arc import Arc, ArcDirection


def test_arc_initializes_components():
    center = V3D(1.0, 2.0, 3.0)
    arc = Arc("gid", center, 5.0, 0.0, 1.0, ArcDirection.CW)

    assert arc.center == center
    assert arc.radius == 5.0
    assert arc.start_angle == 0.0
    assert arc.end_angle == 1.0
    assert arc.direction is ArcDirection.CW
