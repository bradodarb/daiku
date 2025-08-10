import sys
from pathlib import Path

# Allow tests to import the project package without installing it.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from daiku.geo.point import Point
from daiku.parts import Part


def test_block_has_six_sides() -> None:
    part = Part("p1", Point("o", 0, 0, 0), 10.0, 20.0, 30.0)

    assert set(part.sides.keys()) == {
        "front",
        "back",
        "left",
        "right",
        "top",
        "bottom",
    }

    # Each retrieved side should be a Plane instance
    for name in part.sides:
        assert part.get_side(name) is part.sides[name]

