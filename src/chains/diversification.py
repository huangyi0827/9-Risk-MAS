from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from ..tools.rules import load_rules
from ..skills_runtime import load_skill, validate_output


def diversification_chain(state: RiskState) -> Dict[str, Any]:
    metrics = state.get("snapshot_metrics") or {}
    effective_n = float(metrics.get("effective_n", 0.0))

    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules, _ = load_rules(profile)
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

    errors = validate_output(load_skill("risk-market-assessor"), finding)
    if errors:
        raise RuntimeError(f"diversification skill output invalid: {errors}")

    return {"finding_diversification": finding}
