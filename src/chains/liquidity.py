from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from .common import load_rules_cached, validate_finding


def liquidity_chain(state: RiskState) -> Dict[str, Any]:
    metrics = state.get("snapshot_metrics") or {}
    spread = float(metrics.get("weighted_spread_bps", 0.0))
    adv = float(metrics.get("weighted_adv", 0.0))

    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules = load_rules_cached(profile)
    spread_warn = float(rules.get("spread_warn", 40))
    spread_restrict = float(rules.get("spread_restrict", 60))
    adv_warn = float(rules.get("adv_warn", 5_000_000))
    adv_restrict = float(rules.get("adv_restrict", 2_000_000))

    if spread >= spread_restrict or adv <= adv_restrict:
        severity = 2
        summary = "流动性较弱"
    elif spread >= spread_warn or adv <= adv_warn:
        severity = 1
        summary = "流动性偏紧"
    else:
        severity = 0
        summary = "流动性状况可接受"

    finding: Finding = {
        "agent": "LiquidityChain",
        "risk_type": "liquidity",
        "severity": severity,
        "summary": summary,
        "metrics": {"weighted_spread_bps": spread, "weighted_adv": adv},
        "evidence": [
            {"ref": "snapshot_metrics.weighted_spread_bps", "value": spread},
            {"ref": "snapshot_metrics.weighted_adv", "value": adv},
        ],
    }

    validate_finding("liquidity-execution-assessor", finding, "liquidity")

    return {"finding_liquidity": finding}
