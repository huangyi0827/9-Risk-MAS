from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from .common import load_rules_cached, validate_finding


def diversification_chain(state: RiskState) -> Dict[str, Any]:
    metrics = state.get("snapshot_metrics") or {}
    effective_n = float(metrics.get("effective_n", 0.0))

    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules = load_rules_cached(profile)
    n_warn = float(rules.get("effective_n_warn", 5))
    n_restrict = float(rules.get("effective_n_restrict", 3))

    if effective_n <= n_restrict:
        severity = 2
        summary = "有效持仓数偏低"
    elif effective_n <= n_warn:
        severity = 1
        summary = "分散度有提升空间"
    else:
        severity = 0
        summary = "分散度较好"

    finding: Finding = {
        "agent": "DiversificationChain",
        "risk_type": "diversification",
        "severity": severity,
        "summary": summary,
        "metrics": {"effective_n": effective_n},
        "evidence": [{"ref": "snapshot_metrics.effective_n", "value": effective_n}],
    }

    validate_finding("risk-market-assessor", finding, "diversification")

    return {"finding_diversification": finding}
