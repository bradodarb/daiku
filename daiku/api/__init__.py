from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

try:  # optional dependency for real database
    import boto3  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback when boto3 unavailable
    boto3 = None

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.exceptions import HTTPException
from starlette.routing import Route

from daiku.geo.base import V2D, V3D
from daiku.geo.point import Point
from daiku.parts import Part, Plane

# In-memory fallback stores -------------------------------------------------
planes_mem: Dict[str, Plane] = {}
parts_mem: Dict[str, Part] = {}
part_planes_mem: Dict[str, Dict[str, Plane]] = {}

# DynamoDB helpers ---------------------------------------------------------
if boto3 is not None:
    def dynamodb():
        return boto3.resource(
            "dynamodb",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "dummy"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "dummy"),
        )

    def ensure_tables() -> None:
        ddb = dynamodb()
        client = ddb.meta.client
        existing = client.list_tables().get("TableNames", [])
        if "planes" not in existing:
            ddb.create_table(
                TableName="planes",
                KeySchema=[{"AttributeName": "gid", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "gid", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            ).wait_until_exists()
        if "parts" not in existing:
            ddb.create_table(
                TableName="parts",
                KeySchema=[{"AttributeName": "gid", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "gid", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST",
            ).wait_until_exists()

    def planes_table():
        ensure_tables()
        return dynamodb().Table("planes")

    def parts_table():
        ensure_tables()
        return dynamodb().Table("parts")
else:
    def ensure_tables() -> None:  # pragma: no cover - noop for memory backend
        pass

    def planes_table():  # pragma: no cover
        raise RuntimeError("DynamoDB not available")

    def parts_table():  # pragma: no cover
        raise RuntimeError("DynamoDB not available")


# Converters ----------------------------------------------------------------

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


def _part_from_dict(data: dict) -> Tuple[Part, List[Plane]]:
    o = data["origin"]
    origin = Point(o["gid"], o["x"], o["y"], o.get("z", 0.0))
    part = Part(data["gid"], origin, data["width"], data["height"], data["depth"])
    plane_list = [_plane_from_dict(p) for p in data.get("planes", [])]
    return part, plane_list


def _part_to_dict(part: Part, planes: List[Plane]) -> dict:
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
        "planes": [_plane_to_dict(p) for p in planes],
    }


# API endpoints -------------------------------------------------------------

async def create_plane(request):
    data = await request.json()
    plane = _plane_from_dict(data)
    if boto3 is None:
        planes_mem[plane.gid] = plane
    else:
        planes_table().put_item(Item={"gid": plane.gid, "data": json.dumps(_plane_to_dict(plane))})
    return JSONResponse(_plane_to_dict(plane))


async def get_plane(request):
    plane_id = request.path_params["plane_id"]
    if boto3 is None:
        plane = planes_mem.get(plane_id)
        if plane is None:
            raise HTTPException(status_code=404, detail="Plane not found")
        return JSONResponse(_plane_to_dict(plane))
    resp = planes_table().get_item(Key={"gid": plane_id})
    item = resp.get("Item")
    if item is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    return JSONResponse(json.loads(item["data"]))


async def create_part(request):
    data = await request.json()
    part, plane_list = _part_from_dict(data)
    if boto3 is None:
        parts_mem[part.gid] = part
        part_planes_mem[part.gid] = {p.gid: p for p in plane_list}
    else:
        plane_ids = []
        pt = planes_table()
        for plane in plane_list:
            pt.put_item(Item={"gid": plane.gid, "data": json.dumps(_plane_to_dict(plane))})
            plane_ids.append(plane.gid)
        part_item = {
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
            "planes": plane_ids,
        }
        parts_table().put_item(Item={"gid": part.gid, "data": json.dumps(part_item)})
    return JSONResponse(_part_to_dict(part, plane_list))


async def get_part(request):
    part_id = request.path_params["part_id"]
    if boto3 is None:
        part = parts_mem.get(part_id)
        if part is None:
            raise HTTPException(status_code=404, detail="Part not found")
        planes = list(part_planes_mem.get(part_id, {}).values())
        return JSONResponse(_part_to_dict(part, planes))
    resp = parts_table().get_item(Key={"gid": part_id})
    item = resp.get("Item")
    if item is None:
        raise HTTPException(status_code=404, detail="Part not found")
    part_data = json.loads(item["data"])
    o = part_data["origin"]
    origin = Point(o["gid"], o["x"], o["y"], o.get("z", 0.0))
    part = Part(part_data["gid"], origin, part_data["width"], part_data["height"], part_data["depth"])
    planes = []
    pt = planes_table()
    for pid in part_data.get("planes", []):
        presp = pt.get_item(Key={"gid": pid})
        pitem = presp.get("Item")
        if pitem:
            planes.append(_plane_from_dict(json.loads(pitem["data"])))
    return JSONResponse(_part_to_dict(part, planes))


async def add_part_plane(request):
    part_id = request.path_params["part_id"]
    data = await request.json()
    plane = _plane_from_dict(data)
    if boto3 is None:
        part = parts_mem.get(part_id)
        if part is None:
            raise HTTPException(status_code=404, detail="Part not found")
        planes_mem[plane.gid] = plane
        part_planes_mem.setdefault(part_id, {})[plane.gid] = plane
        return JSONResponse(_plane_to_dict(plane))
    parts_t = parts_table()
    part_resp = parts_t.get_item(Key={"gid": part_id})
    part_item = part_resp.get("Item")
    if part_item is None:
        raise HTTPException(status_code=404, detail="Part not found")
    part_data = json.loads(part_item["data"])
    planes_table().put_item(Item={"gid": plane.gid, "data": json.dumps(_plane_to_dict(plane))})
    plane_ids = part_data.get("planes", [])
    plane_ids.append(plane.gid)
    part_data["planes"] = plane_ids
    parts_t.put_item(Item={"gid": part_id, "data": json.dumps(part_data)})
    return JSONResponse(_plane_to_dict(plane))


async def get_part_plane(request):
    part_id = request.path_params["part_id"]
    plane_id = request.path_params["plane_id"]
    if boto3 is None:
        part = parts_mem.get(part_id)
        if part is None:
            raise HTTPException(status_code=404, detail="Part not found")
        plane = part_planes_mem.get(part_id, {}).get(plane_id)
        if plane is None:
            raise HTTPException(status_code=404, detail="Plane not found for part")
        return JSONResponse(_plane_to_dict(plane))
    parts_t = parts_table()
    part_resp = parts_t.get_item(Key={"gid": part_id})
    part_item = part_resp.get("Item")
    if part_item is None:
        raise HTTPException(status_code=404, detail="Part not found")
    part_data = json.loads(part_item["data"])
    if plane_id not in part_data.get("planes", []):
        raise HTTPException(status_code=404, detail="Plane not found for part")
    plane_resp = planes_table().get_item(Key={"gid": plane_id})
    plane_item = plane_resp.get("Item")
    if plane_item is None:
        raise HTTPException(status_code=404, detail="Plane not found")
    return JSONResponse(json.loads(plane_item["data"]))


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


def setup_tables():
    if boto3 is not None:
        ensure_tables()
