# app/state.py
from typing import Dict, Any
from .models import MapData

# in-memory stores (之後可換成 DB)
MAP_STORE: Dict[str, MapData] = {}
GRAPH_STORE: Dict[str, Any] = {}   # map_id -> Graph
ORDER_STORE: Dict[str, Dict[str, Any]] = {}  # order_id -> order dict
