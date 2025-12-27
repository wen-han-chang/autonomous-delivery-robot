from __future__ import annotations
from typing import List

def estimate_eta_sec(route: List[str], total_distance_cm: float, avg_speed_cm_s: float = 12.0, turn_penalty_s: float = 1.2) -> float:
    """
    最簡版本：
    ETA = distance / speed + (轉彎次數 * turn_penalty)
    轉彎次數：先用「節點數 - 2」近似（中間路口每個算一次）
    """
    if avg_speed_cm_s <= 0:
        avg_speed_cm_s = 12.0

    turns = max(0, len(route) - 2)
    return (total_distance_cm / avg_speed_cm_s) + turns * turn_penalty_s
