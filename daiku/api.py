from __future__ import annotations

from typing import Dict

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.routing import Route

from daiku.geo.base import V2D, V3D
from daiku.geo.point import Point
from daiku.parts import Part, Plane

# In-memory storage for planes and parts
planes: Dict[str, Plane] = {}
parts: Dict[str, Part] = {}
part_planes: Dict[str, Dict[str, Plane]] = {}

def _v2d(data: dict) -> V2D:
    return V2D(data["x"], data["y"])

def _v3d(data: dict) -> V3D:
    return V3D(data["x"], data["y"], data.get("z", 0.0))

def _plane_from_dict(data: dict) -> Plane:
    o = data["origin"]
    origin = Point(o["gid"], o["x"], o["y"], o.get("z", 0.0))
    normal = _v3d(data["normal"])
    shapes = [[_v2d(p) for p in shape] for shape in data.get("shapes", [])]
    return Plane(data["gid"], origin, normal, shapes=shapes)

def _plane_to_dict(plane: Plane) -> dict:
    return {
        "gid": plane.gid,
        "origin": {
            "gid": plane.origin.gid,
            "x": plane.origin.x,
            "y": plane.origin.y,
            "z": plane.origin.z,
        },
        "normal": {
            "x": plane.normal.x,
            "y": plane.normal.y,
            "z": plane.normal.z,
        },
        "shapes": [[{"x": p.x, "y": p.y} for p in shape] for shape in plane.shapes],
    }

def _part_from_dict(data: dict) -> Part:
    o = data["origin"]
    origin = Point(o["gid"], o["x"], o["y"], o.get("z", 0.0))
    part = Part(data["gid"], origin, data["width"], data["height"], data["depth"])
    plane_map: Dict[str, Plane] = {}
    for p in data.get("planes", []):
        plane = _plane_from_dict(p)
        planes[plane.gid] = plane
        plane_map[plane.gid] = plane
    part_planes[part.gid] = plane_map
    return part

def _part_to_dict(part: Part) -> dict:
    return {
        "gid": part.gid,
        "origin": {
            "gid": part.origin.gid,
            "x": part.origin.x,
            "y": part.origin.y,
            "z": part.origin.z,
        },
        "width": part.width,
        "height": part.height,
        "depth": part.depth,
        "planes": [_plane_to_dict(p) for p in part_planes.get(part.gid, {}).values()],
    }

async def create_plane(request):
    data = await request.json()
    plane = _plane_from_dict(data)
    planes[plane.gid] = plane
    return JSONResponse(_plane_to_dict(plane))

async def get_plane(request):
    plane_id = request.path_params["plane_id"]
    plane = planes.get(plane_id)
    if plane is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    return JSONResponse(_plane_to_dict(plane))

async def create_part(request):
    data = await request.json()
    part = _part_from_dict(data)
    parts[part.gid] = part
    return JSONResponse(_part_to_dict(part))

async def get_part(request):
    part_id = request.path_params["part_id"]
    part = parts.get(part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    return JSONResponse(_part_to_dict(part))

async def add_part_plane(request):
    part_id = request.path_params["part_id"]
    part = parts.get(part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    data = await request.json()
    plane = _plane_from_dict(data)
    planes[plane.gid] = plane
    part_planes.setdefault(part_id, {})[plane.gid] = plane
    return JSONResponse(_plane_to_dict(plane))

async def get_part_plane(request):
    part_id = request.path_params["part_id"]
    plane_id = request.path_params["plane_id"]
    part = parts.get(part_id)
    if part is None:
        raise HTTPException(status_code=404, detail="Part not found")
    plane = part_planes.get(part_id, {}).get(plane_id)
    if plane is None:
        raise HTTPException(status_code=404, detail="Plane not found for part")
    return JSONResponse(_plane_to_dict(plane))

routes = [
    Route("/planes", create_plane, methods=["POST"]),
    Route("/planes/{plane_id}", get_plane, methods=["GET"]),
    Route("/components/parts", create_part, methods=["POST"]),
    Route("/components/parts/{part_id}", get_part, methods=["GET"]),
    Route("/components/parts/{part_id}/planes", add_part_plane, methods=["POST"]),
    Route(
        "/components/parts/{part_id}/planes/{plane_id}",
        get_part_plane,
        methods=["GET"],
    ),
]

app = Starlette(routes=routes)
