import pathlib
import sys

# Ensure the package root is on the import path when running tests without
# installing the package.
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from daiku.geo.base import V3D
from daiku.geo.position import Position


def test_position_initializes_components():
    o = V3D(1.0, 2.0, 3.0)
    d = V3D(4.0, 5.0, 6.0)
    a = V3D(7.0, 8.0, 9.0)

    pos = Position('gid', o, d, a)

    assert pos.o == o
    assert (pos.dx, pos.dy, pos.dz) == (4.0, 5.0, 6.0)
    assert (pos.ax, pos.ay, pos.az) == (7.0, 8.0, 9.0)
