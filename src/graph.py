from __future__ import annotations

from typing import Any, Dict, List, Literal

from langgraph.graph import StateGraph, END
from langgraph.types import Send
from langchain_core.runnables import RunnableLambda

from .state import RiskState
from .config import RuntimeConfig, DEFAULT_CONFIG
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
    gatekeeper_chain,
    supervisor_chain,
    market_risk_chain,
    concentration_chain,
    diversification_chain,
    liquidity_chain,
    reducer_chain,
)
from .agents import run_macro_agent, run_compliance_agent


def _should_run_node(state: RiskState, name: str) -> bool:
    """Check if a node should run based on pending_agents list."""
    if state.get("stop_condition"):
        return False
    pending = state.get("pending_agents") or []
    return name in pending


def build_graph(llm=None, config: RuntimeConfig | None = None):
    """构建并返回主工作流图（含并行分析与审计链路）。"""
    cfg = config or DEFAULT_CONFIG
    g = StateGraph(RiskState)

    # ===== Pipeline nodes =====
    def validate_node(state: RiskState) -> Dict[str, Any]:
        return validate_and_normalize(state, cfg)

    def data_quality_node(state: RiskState) -> Dict[str, Any]:
        return check_data_quality(state, cfg)

    def snapshot_node(state: RiskState) -> Dict[str, Any]:
        return risk_snapshot_bundle(state, cfg)

    def constraints_node(state: RiskState) -> Dict[str, Any]:
        return constraints_evaluator(state, cfg)

    def gatekeeper_node(state: RiskState) -> Dict[str, Any]:
        return gatekeeper_chain(state)

    def supervisor_node(state: RiskState) -> Dict[str, Any]:
        candidates = state.get("candidate_nodes") or []
        return supervisor_chain(state, llm, candidates, cfg)

    # ===== Analysis nodes (deterministic chains) =====
    analysis_nodes = {
        "market": lambda state: market_risk_chain(state, cfg),
        "concentration": lambda state: concentration_chain(state, cfg),
        "diversification": lambda state: diversification_chain(state, cfg),
        "liquidity": lambda state: liquidity_chain(state, cfg),
    }

    # ===== Agent nodes (LLM-based) =====
    agent_nodes = {
        "macro": lambda state: run_macro_agent(state, llm, cfg),
        "compliance": lambda state: run_compliance_agent(state, llm, cfg),
    }

    all_analysis_nodes = {**analysis_nodes, **agent_nodes}


    def _guarded_node(name: str, fn):
        """Wrap a node function with guard logic.

        FIX: Returns explicit finding_<name>=None instead of empty dict
        to ensure state field exists for downstream nodes.
        """
        def _node(state: RiskState) -> Dict[str, Any]:
            if not _should_run_node(state, name):
                return {f"finding_{name}": None}
            return fn(state)
        return _node

    def reducer_node(state: RiskState) -> Dict[str, Any]:
        return reducer_chain(state)

    def decision_node(state: RiskState) -> Dict[str, Any]:
        return decision_engine(state)

    def solver_node(state: RiskState) -> Dict[str, Any]:
        return constraint_solver(state, cfg)

    def audit_node(state: RiskState) -> Dict[str, Any]:
        return audit_log(state, cfg)

    # ===== Parallel dispatch using LangGraph Send API =====
    def dispatch_to_parallel(state: RiskState) -> List[Send]:
        """Route to multiple analysis nodes in parallel using Send API.

        This replaces the old serial dispatch loop with true parallel execution.
        """
        if state.get("stop_condition"):
            return [Send("reducer", state)]

        pending = state.get("pending_agents") or []
        if not pending:
            return [Send("reducer", state)]

        # Send to all pending nodes in parallel
        sends = [Send(node, state) for node in pending if node in all_analysis_nodes]
        if not sends:
            return [Send("reducer", state)]
        return sends

    # ===== Register nodes =====
    g.add_node("validate", RunnableLambda(validate_node))
    g.add_node("data_quality", RunnableLambda(data_quality_node))
    g.add_node("snapshot", RunnableLambda(snapshot_node))
    g.add_node("constraints", RunnableLambda(constraints_node))
    g.add_node("gatekeeper", RunnableLambda(gatekeeper_node))
    g.add_node("supervisor", RunnableLambda(supervisor_node))

    for name, fn in all_analysis_nodes.items():
        g.add_node(name, RunnableLambda(_guarded_node(name, fn)))

    g.add_node("reducer", RunnableLambda(reducer_node))
    g.add_node("decision", RunnableLambda(decision_node))
    g.add_node("solver", RunnableLambda(solver_node))
    g.add_node("audit", RunnableLambda(audit_node))

    # ===== Build graph edges =====
    # Sequential pipeline: validate → data_quality → snapshot → gatekeeper → supervisor
    g.set_entry_point("validate")
    g.add_edge("validate", "data_quality")
    g.add_edge("data_quality", "snapshot")
    g.add_edge("snapshot", "gatekeeper")
    g.add_edge("gatekeeper", "supervisor")

    # Parallel dispatch: supervisor → [market|concentration|...] in parallel
    g.add_conditional_edges("supervisor", dispatch_to_parallel)

   
    for name in all_analysis_nodes:
        g.add_edge(name, "reducer")

    # Final pipeline: reducer → constraints → decision → solver → audit → END
    g.add_edge("reducer", "constraints")
    g.add_edge("constraints", "decision")
    g.add_edge("decision", "solver")
    g.add_edge("solver", "audit")
    g.add_edge("audit", END)

    return g.compile()
