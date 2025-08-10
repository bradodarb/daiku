from abc import ABC
from dataclasses import dataclass


@dataclass
class GeoBase(ABC):
    gid: str


@dataclass
class V2D:
    x: float
    y: float


@dataclass
class V3D:
    x: float
    y: float
    z: float
