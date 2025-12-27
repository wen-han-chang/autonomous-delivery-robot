from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal

class Node(BaseModel):
    id: str
    x: float
    y: float

class Edge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    bidirectional: bool = True
    length: Optional[float] = None  # cm, optional

class MapData(BaseModel):
    map_id: str
    unit: Literal["cm", "m"] = "cm"
    nodes: List[Node]
    edges: List[Edge]

class CreateOrderReq(BaseModel):
    map_id: str
    from_node: str
    to_node: str
    algorithm: Literal["dijkstra", "astar"] = "dijkstra"

class CreateOrderResp(BaseModel):
    order_id: str
    map_id: str
    route: List[str]
    total_distance_cm: float
    eta_sec: float

class Telemetry(BaseModel):
    robot_id: str
    order_id: str
    node: str
    progress: float = Field(ge=0.0, le=1.0)
    speed: float = Field(gt=0.0)  # cm/s
    state: Literal["IDLE", "ASSIGNED", "MOVING", "ARRIVED"] = "MOVING"
