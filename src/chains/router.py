from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState


def router_chain(state: RiskState) -> Dict[str, Any]:
    validation = state.get("validation") or {}
    data_quality = state.get("data_quality") or {}
    normalized = state.get("normalized") or {}

    stop_condition = bool(state.get("stop_condition"))
    if not validation.get("is_valid", True):
        stop_condition = True
    if data_quality.get("status") == "blocked":
        stop_condition = True

    nodes: List[str] = list(state.get("candidate_nodes") or [])
    if not nodes:
        nodes = [
            "market",
            "concentration",
            "diversification",
            "liquidity",
            "compliance",
        ]
        if data_quality.get("macro_available", False):
            nodes.append("macro")

    if stop_condition:
        nodes = []

    cost_budget = {"llm_tokens": 2000, "tool_calls": 6}

    return {
        "nodes_to_run": nodes,
        "stop_condition": stop_condition,
        "cost_budget": cost_budget,
    }
