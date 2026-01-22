from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from ..tools.rules import load_rules
from ..skills_runtime import load_skill, validate_output


def concentration_chain(state: RiskState) -> Dict[str, Any]:
    metrics = state.get("snapshot_metrics") or {}
    hhi = float(metrics.get("hhi", 0.0))
    top_weight = float(metrics.get("top_weight", 0.0))

    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules, _ = load_rules(profile)
    hhi_warn = float(rules.get("hhi_warn", 0.25))
    hhi_restrict = float(rules.get("hhi_restrict", 0.35))
    top_warn = float(rules.get("top_weight_warn", 0.3))
    top_restrict = float(rules.get("top_weight_restrict", 0.4))

    if hhi >= hhi_restrict or top_weight >= top_restrict:
        severity = 2
        summary = "组合集中度较高"
    elif hhi >= hhi_warn or top_weight >= top_warn:
        severity = 1
        summary = "组合集中度高于目标水平"
    else:
        severity = 0
        summary = "组合集中度在合理范围内"

    finding: Finding = {
        "agent": "ConcentrationChain",
        "risk_type": "concentration",
        "severity": severity,
        "summary": summary,
        "metrics": {"hhi": hhi, "top_weight": top_weight},
        "evidence": [
            {"ref": "snapshot_metrics.hhi", "value": hhi},
            {"ref": "snapshot_metrics.top_weight", "value": top_weight},
        ],
    }

    errors = validate_output(load_skill("risk-market-assessor"), finding)
    if errors:
        raise RuntimeError(f"concentration skill output invalid: {errors}")

    return {"finding_concentration": finding}
