from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class Intent(TypedDict):
    date: str
    mode: str  # target | delta
    targets: Dict[str, float]


class Context(TypedDict, total=False):
    current_positions: Dict[str, float]
    current_positions_date: str
    universe: List[str]
    trade_calendar: str
    account_type: str
    jurisdiction: str
    policy_profile: str
    aum: float


class Finding(TypedDict, total=False):
    agent: str
    risk_type: str
    severity: int
    summary: str
    evidence: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    recommendations: List[str]
    policy_ids: List[str]


class RiskState(TypedDict, total=False):
    # inputs
    intent: Intent
    context: Context

    # validated/normalized
    normalized: Dict[str, Any]
    validation: Dict[str, Any]

    # deterministic tools
    data_quality: Dict[str, Any]
    data_gaps: List[Dict[str, Any]]
    snapshot_metrics: Dict[str, Any]
    rule_findings: List[Dict[str, Any]]
    compliance_blocklist: List[str]
    compliance_blocklist_meta: Dict[str, Any]

    # routing
    candidate_nodes: List[str]
    nodes_to_run: List[str]
    pending_agents: List[str]
    next_agent: str
    stop_condition: bool
    cost_budget: Dict[str, Any]
    gatekeeper_used: bool
    gatekeeper_rationale: str
    supervisor_used: bool
    supervisor_rationale: str
    supervisor_model: str

    # parallel nodes
    finding_market: Finding
    finding_concentration: Finding
    finding_diversification: Finding
    finding_liquidity: Finding
    finding_macro: Finding
    finding_compliance: Finding
    tool_calls_macro: List[Dict[str, Any]]
    tool_calls_compliance: List[Dict[str, Any]]
    llm_used_macro: bool
    llm_used_compliance: bool
    llm_model_macro: str
    llm_model_compliance: str

    # aggregation
    findings: List[Finding]
    risk_report: Dict[str, Any]

    # decision outputs
    decision: Dict[str, Any]
    binding_constraints: List[Dict[str, Any]]
    recommended_actions: List[Dict[str, Any]]

    # tooling + audit
    audit: Dict[str, Any]


def new_state(intent: Intent, context: Optional[Context] = None) -> RiskState:
    return {
        "intent": intent,
        "context": context or {},
    }
