from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set, Dict, Any
import json

from .models import Telemetry
from .state import ORDER_STORE


ws_router = APIRouter()
CLIENTS: Set[WebSocket] = set()

async def broadcast(msg: Dict[str, Any]):
    dead = []
    for ws in CLIENTS:
        try:
            await ws.send_text(json.dumps(msg, ensure_ascii=False))
        except Exception:
            dead.append(ws)
    for ws in dead:
        CLIENTS.discard(ws)

@ws_router.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    CLIENTS.add(ws)
    try:
        await ws.send_text(json.dumps({"type": "hello", "msg": "connected"}, ensure_ascii=False))
        while True:
            text = await ws.receive_text()
            data = json.loads(text)

            # 兩種消息：
            # 1) telemetry (robot -> server)
            # 2) subscribe (android -> server)
            msg_type = data.get("type")

            if msg_type == "telemetry":
                t = Telemetry.model_validate(data["payload"])
                # 更新 order 狀態（最簡版）
                if t.order_id in ORDER_STORE:
                    ORDER_STORE[t.order_id]["state"] = t.state
                    ORDER_STORE[t.order_id]["robot_id"] = t.robot_id
                    ORDER_STORE[t.order_id]["node"] = t.node
                    ORDER_STORE[t.order_id]["progress"] = t.progress
                    ORDER_STORE[t.order_id]["speed"] = t.speed

                await broadcast({
                    "type": "order_update",
                    "order_id": t.order_id,
                    "robot_id": t.robot_id,
                    "node": t.node,
                    "progress": t.progress,
                    "speed": t.speed,
                    "state": t.state
                })

            elif msg_type == "subscribe":
                # demo: 你可以忽略或做訂閱機制
                await ws.send_text(json.dumps({"type": "subscribed", "payload": data.get("payload")}, ensure_ascii=False))
            else:
                await ws.send_text(json.dumps({"type": "error", "msg": "unknown message type"}, ensure_ascii=False))

    except WebSocketDisconnect:
        CLIENTS.discard(ws)
