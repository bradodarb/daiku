import asyncio
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from daiku.api import (
    add_part_plane,
    create_part,
    create_plane,
    get_part,
    get_part_plane,
    get_plane,
    setup_tables,
)


class DummyRequest:
    def __init__(self, data=None, path_params=None):
        self._data = data
        self.path_params = path_params or {}

    async def json(self):
        return self._data


def run(func, request):
    return asyncio.get_event_loop().run_until_complete(func(request))


def test_create_and_get_plane():
    setup_tables()
    payload = {
        "gid": "plane1",
        "origin": {"gid": "o1", "x": 0, "y": 0, "z": 0},
        "normal": {"x": 0, "y": 0, "z": 1},
        "shapes": [[{"x": 0, "y": 0}, {"x": 1, "y": 1}]],
    }
    response = run(create_plane, DummyRequest(payload))
    assert response.status_code == 200
    data = json.loads(response.body)
    assert data["gid"] == "plane1"
    assert data["shapes"][0][1]["x"] == 1

    get_resp = run(get_plane, DummyRequest(path_params={"plane_id": "plane1"}))
    assert get_resp.status_code == 200
    assert json.loads(get_resp.body) == data


def test_create_part_and_add_plane():
    setup_tables()
    part_payload = {
        "gid": "part1",
        "origin": {"gid": "po", "x": 0, "y": 0, "z": 0},
        "width": 10.0,
        "height": 20.0,
        "depth": 30.0,
    }
    part_resp = run(create_part, DummyRequest(part_payload))
    assert part_resp.status_code == 200
    assert json.loads(part_resp.body)["gid"] == "part1"

    plane_payload = {
        "gid": "plane2",
        "origin": {"gid": "p2", "x": 0, "y": 0, "z": 0},
        "normal": {"x": 0, "y": 0, "z": 1},
        "shapes": [],
    }
    add_resp = run(
        add_part_plane,
        DummyRequest(plane_payload, path_params={"part_id": "part1"}),
    )
    assert add_resp.status_code == 200
    plane_data = json.loads(add_resp.body)
    assert plane_data["gid"] == "plane2"

    get_plane_resp = run(
        get_part_plane,
        DummyRequest(path_params={"part_id": "part1", "plane_id": "plane2"}),
    )
    assert get_plane_resp.status_code == 200
    assert json.loads(get_plane_resp.body) == plane_data
