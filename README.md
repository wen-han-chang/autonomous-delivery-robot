# ESP32 Autonomous Car System  
## Android ↔ Backend Communication Specification (MVP v1.0)

This repository contains the **backend service** for an ESP32 autonomous car project.  
The backend is responsible for **path planning, ETA calculation, and real-time status updates**.  
Android is a **pure client**, only responsible for UI rendering.

---

## 🧭 System Overview

- **Backend**  
  - Maintains multiple maps (Graph-based)
  - Computes shortest paths (Dijkstra / A*)
  - Calculates ETA
  - Pushes real-time updates via WebSocket

- **Android**  
  - Sends order requests
  - Displays route, vehicle position, and ETA
  - Does **no path or ETA calculation**

- **ESP32**  
  - Executes assigned route
  - Reports telemetry (node, progress, speed)


---

## 🗺️ Map Design (Multi-Map Support)

### Core Principles

- Backend supports **multiple maps**
- Each map is uniquely identified by `map_id`
- Android **must specify `map_id`** when creating an order
- Android **does not fetch or manage map data**

### Example `map_id`

```text
campus_demo
campus_2f
city_block_A
```

## 📡 REST API Specification

### 1️⃣ Create Order

**Endpoint**

POST/orders

**Request Body**

```json
{
  "map_id": "campus_demo",
  "from_node": "A",
  "to_node": "D"
}
```
| Field     | Type   | Required | Description         |
| --------- | ------ | -------- | ------------------- |
| map_id    | string | yes      | Target map          |
| from_node | string | yes      | Start node ID       |
| to_node   | string | yes      | Destination node ID |

**Response**

```json
{
  "order_id": "0cbc3d5cd",
  "map_id": "campus_demo",
  "route": ["A", "X1", "X2", "D"],
  "total_distance_cm": 150,
  "eta_sec": 14.9
}
```
| Field             | Description                      |
| ----------------- | -------------------------------- |
| order_id          | Unique order identifier          |
| route             | Node sequence for visualization  |
| total_distance_cm | Total path length                |
| eta_sec           | Estimated arrival time (seconds) |

**Get Order Status (Optional)**

Used for app restart or WebSocket reconnection.

```
bash
GET /orders/{order_id}
```
**WebSocket Specification**
Connection
```
Arduino
ws://<server-ip>:8000/ws
```
**Android → Backend (Subscribe Order)**

Send immediately after connection

```
json
{
  "type": "subscribe",
  "payload": {
    "order_id": "0cbc3d5cd"
  }
}
```
**ESP32 → Backend (Telemetry)**
```
json
{
  "type": "telemetry",
  "payload": {
    "robot_id": "R1",
    "order_id": "0cbc3d5cd",
    "node": "X2",
    "progress": 0.4,
    "speed": 12,
    "state": "MOVING"
  }
}
```
**Backend → Android (Order Update)**
```
json
{
  "type": "order_update",
  "order_id": "0cbc3d5cd",
  "robot_id": "R1",
  "node": "X2",
  "progress": 0.4,
  "speed": 12,
  "state": "MOVING"
}
```
| Field    | Description               |
| -------- | ------------------------- |
| node     | Current node              |
| progress | Edge progress (0.0 ~ 1.0) |
| speed    | cm/s                      |
| state    | Order state               |



