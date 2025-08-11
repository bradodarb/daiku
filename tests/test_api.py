from starlette.testclient import TestClient

from daiku.api import app

client = TestClient(app)


def test_create_and_get_plane():
    payload = {
        "gid": "plane1",
        "origin": {"gid": "o1", "x": 0, "y": 0, "z": 0},
        "normal": {"x": 0, "y": 0, "z": 1},
        "shapes": [[{"x": 0, "y": 0}, {"x": 1, "y": 1}]],
    }
    response = client.post("/planes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["gid"] == "plane1"
    assert data["shapes"][0][1]["x"] == 1

    get_resp = client.get("/planes/plane1")
    assert get_resp.status_code == 200
    assert get_resp.json() == data


def test_create_part_and_add_plane():
    part_payload = {
        "gid": "part1",
        "origin": {"gid": "po", "x": 0, "y": 0, "z": 0},
        "width": 10.0,
        "height": 20.0,
        "depth": 30.0,
    }
    part_resp = client.post("/components/parts", json=part_payload)
    assert part_resp.status_code == 200
    assert part_resp.json()["gid"] == "part1"

    plane_payload = {
        "gid": "plane2",
        "origin": {"gid": "p2", "x": 0, "y": 0, "z": 0},
        "normal": {"x": 0, "y": 0, "z": 1},
        "shapes": [],
    }
    add_resp = client.post("/components/parts/part1/planes", json=plane_payload)
    assert add_resp.status_code == 200
    plane_data = add_resp.json()
    assert plane_data["gid"] == "plane2"

    get_plane = client.get("/components/parts/part1/planes/plane2")
    assert get_plane.status_code == 200
    assert get_plane.json() == plane_data
