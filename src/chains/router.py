from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState


def router_chain(state: RiskState) -> Dict[str, Any]:
    stop_condition = bool(state.get("stop_condition"))
    nodes: List[str] = list(state.get("candidate_nodes") or [])
    if stop_condition:
        nodes = []

    cost_budget = {"llm_tokens": 2000, "tool_calls": 6}

    return {
        "nodes_to_run": nodes,
        "stop_condition": stop_condition,
        "cost_budget": cost_budget,
    }
