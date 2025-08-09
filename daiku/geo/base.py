from abc import ABC
from dataclasses import dataclass


class GeoBase(ABC):
    def __init__(self, gid: str):
        self.gid = gid


@dataclass
class V2D:
    x: float
    y: float


@dataclass
class V3D:
    x: float
    y: float
    z: float
