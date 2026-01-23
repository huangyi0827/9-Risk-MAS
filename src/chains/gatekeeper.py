from __future__ import annotations

from typing import Any, Dict, List

from ..state import RiskState


def gatekeeper_chain(state: RiskState) -> Dict[str, Any]:
    validation = state.get("validation") or {}
    data_quality = state.get("data_quality") or {}

    stop_condition = False
    rationale: List[str] = []

    if not validation.get("is_valid", True):
        stop_condition = True
        rationale.append("validation_failed")
    if data_quality.get("status") == "blocked":
        stop_condition = True
        rationale.append("data_quality_blocked")

    candidates: List[str] = []
    if not stop_condition:
        candidates = [
            "market",
            "concentration",
            "diversification",
            "liquidity",
        ]
        if (data_quality.get("macro") or {}).get("timeseries_available", False):
            candidates.append("macro")
        if (data_quality.get("compliance") or {}).get("text_available", False):
            candidates.append("compliance")

    return {
        "candidate_nodes": candidates,
        "stop_condition": stop_condition,
        "gatekeeper_used": True,
        "gatekeeper_rationale": "; ".join(rationale) if rationale else "ok",
    }
