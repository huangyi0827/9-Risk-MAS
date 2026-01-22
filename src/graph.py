from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from .state import RiskState
from .tools import (
    validate_and_normalize,
    check_data_quality,
    risk_snapshot_bundle,
    constraints_evaluator,
    decision_engine,
    constraint_solver,
    audit_log,
)
from .chains import (
    router_chain,
    gatekeeper_chain,
    supervisor_chain,
    market_risk_chain,
    concentration_chain,
    diversification_chain,
    liquidity_chain,
    reducer_chain,
)
from .agents import run_macro_agent, run_compliance_agent


def _should_run(state: RiskState, name: str) -> bool:
    if state.get("stop_condition"):
        return False
    next_agent = state.get("next_agent") or ""
    return next_agent == name


def _next_node(state: RiskState) -> str:
    return state.get("next_agent") or "reducer"


def build_graph(llm=None):
    g = StateGraph(RiskState)

    def validate_node(state: RiskState) -> Dict[str, Any]:
        return validate_and_normalize(state)

    def data_quality_node(state: RiskState) -> Dict[str, Any]:
        return check_data_quality(state)

    def snapshot_node(state: RiskState) -> Dict[str, Any]:
        return risk_snapshot_bundle(state)

    def constraints_node(state: RiskState) -> Dict[str, Any]:
        return constraints_evaluator(state)

    def gatekeeper_node(state: RiskState) -> Dict[str, Any]:
        return gatekeeper_chain(state)

    def router_node(state: RiskState) -> Dict[str, Any]:
        return router_chain(state)

    def supervisor_node(state: RiskState) -> Dict[str, Any]:
        candidates = state.get("nodes_to_run") or []
        return supervisor_chain(state, llm, candidates)

    def dispatch_node(state: RiskState) -> Dict[str, Any]:
        pending = list(state.get("pending_agents") or [])
        if not pending:
            return {"next_agent": "", "pending_agents": []}
        next_agent = pending.pop(0)
        return {"next_agent": next_agent, "pending_agents": pending}

    def _guarded_node(name: str, fn):
        def _node(state: RiskState) -> Dict[str, Any]:
            if not _should_run(state, name):
                return {}
            return fn(state)

        return _node

    analysis_nodes = {
        "market": market_risk_chain,
        "concentration": concentration_chain,
        "diversification": diversification_chain,
        "liquidity": liquidity_chain,
    }
    agent_nodes = {
        "macro": lambda state: run_macro_agent(state, llm),
        "compliance": lambda state: run_compliance_agent(state, llm),
    }

    def reducer_node(state: RiskState) -> Dict[str, Any]:
        return reducer_chain(state)

    def decision_node(state: RiskState) -> Dict[str, Any]:
        return decision_engine(state)

    def solver_node(state: RiskState) -> Dict[str, Any]:
        return constraint_solver(state)

    def audit_node(state: RiskState) -> Dict[str, Any]:
        return audit_log(state)

    g.add_node("validate", RunnableLambda(validate_node))
    g.add_node("data_quality", RunnableLambda(data_quality_node))
    g.add_node("snapshot", RunnableLambda(snapshot_node))
    g.add_node("constraints", RunnableLambda(constraints_node))
    g.add_node("gatekeeper", RunnableLambda(gatekeeper_node))
    g.add_node("router", RunnableLambda(router_node))
    g.add_node("supervisor", RunnableLambda(supervisor_node))
    g.add_node("dispatch", RunnableLambda(dispatch_node))

    for name, fn in analysis_nodes.items():
        g.add_node(name, RunnableLambda(_guarded_node(name, fn)))
    for name, fn in agent_nodes.items():
        g.add_node(name, RunnableLambda(_guarded_node(name, fn)))

    g.add_node("reducer", RunnableLambda(reducer_node))
    g.add_node("decision", RunnableLambda(decision_node))
    g.add_node("solver", RunnableLambda(solver_node))
    g.add_node("audit", RunnableLambda(audit_node))

    g.set_entry_point("validate")
    g.add_edge("validate", "data_quality")
    g.add_edge("data_quality", "snapshot")
    g.add_edge("snapshot", "gatekeeper")
    g.add_edge("gatekeeper", "router")
    g.add_edge("router", "supervisor")

    g.add_edge("supervisor", "dispatch")

    dispatch_targets = {name: name for name in {**analysis_nodes, **agent_nodes}}
    dispatch_targets["reducer"] = "reducer"
    g.add_conditional_edges(
        "dispatch",
        _next_node,
        dispatch_targets,
    )

    for name in {**analysis_nodes, **agent_nodes}:
        g.add_edge(name, "dispatch")
    g.add_edge("reducer", "constraints")
    g.add_edge("constraints", "decision")
    g.add_edge("decision", "solver")
    g.add_edge("solver", "audit")
    g.add_edge("audit", END)

    return g.compile()
