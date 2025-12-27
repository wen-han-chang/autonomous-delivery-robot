from fastapi import FastAPI, HTTPException
from typing import Dict
import uuid
import json
from pathlib import Path

from .models import MapData, CreateOrderReq, CreateOrderResp
from .graph import build_graph, dijkstra, astar
from .services import estimate_eta_sec
from .ws import ws_router

app = FastAPI(title="ESP32 Car Backend")

from .state import MAP_STORE, GRAPH_STORE, ORDER_STORE


@app.post("/maps/import")
def import_map(path: str = "data/map.json"):
    try:
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        map_data = MapData.model_validate(data)
        g = build_graph(map_data)
        MAP_STORE[map_data.map_id] = map_data
        GRAPH_STORE[map_data.map_id] = g
        return {"ok": True, "map_id": map_data.map_id, "nodes": len(map_data.nodes), "edges": len(map_data.edges)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/orders", response_model=CreateOrderResp)
def create_order(req: CreateOrderReq):
    if req.map_id not in GRAPH_STORE:
        raise HTTPException(status_code=404, detail="map_id not loaded; call /maps/import first")

    g = GRAPH_STORE[req.map_id]
    try:
        if req.algorithm == "astar":
            route, dist = astar(g, req.from_node, req.to_node)
        else:
            route, dist = dijkstra(g, req.from_node, req.to_node)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    eta = estimate_eta_sec(route, dist)
    order_id = "O" + uuid.uuid4().hex[:8]

    ORDER_STORE[order_id] = {
        "order_id": order_id,
        "map_id": req.map_id,
        "route": route,
        "total_distance_cm": dist,
        "eta_sec": eta,
        "state": "CREATED",
    }

    return CreateOrderResp(
        order_id=order_id,
        map_id=req.map_id,
        route=route,
        total_distance_cm=dist,
        eta_sec=eta,
    )

@app.get("/orders/{order_id}")
def get_order(order_id: str):
    if order_id not in ORDER_STORE:
        raise HTTPException(status_code=404, detail="order not found")
    return ORDER_STORE[order_id]

app.include_router(ws_router)
