from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from .common import load_rules_cached, validate_finding
from ..config import RuntimeConfig


def market_risk_chain(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    metrics = state.get("snapshot_metrics") or {}
    vol = float(metrics.get("portfolio_volatility", 0.0))

    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules = load_rules_cached(profile, config)
    vol_warn = float(rules.get("volatility_warn", 0.15))
    vol_restrict = float(rules.get("volatility_restrict", 0.25))

    if vol >= vol_restrict:
        severity = 2
        summary = "组合波动率偏高"
    elif vol >= vol_warn:
        severity = 1
        summary = "组合波动率高于舒适区间"
    else:
        severity = 0
        summary = "组合波动率处于目标范围"

    finding: Finding = {
        "agent": "MarketRiskChain",
        "risk_type": "market",
        "severity": severity,
        "summary": summary,
        "metrics": {"portfolio_volatility": vol},
        "evidence": [{"ref": "snapshot_metrics.portfolio_volatility", "value": vol}],
    }

    validate_finding("risk-market-assessor", finding, "market")

    return {"finding_market": finding}
