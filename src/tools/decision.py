from __future__ import annotations

from typing import Any, Dict, List

from ..state import RiskState


_LEVEL = {"pass": 0, "warn": 1, "restrict": 2, "block": 3}


def _max_level(findings: List[Dict[str, Any]]) -> int:
    if not findings:
        return 0
    return max(int(f.get("level") or _LEVEL.get(f.get("severity", "pass"), 0)) for f in findings)


def decision_engine(state: RiskState) -> Dict[str, Any]:
    rule_findings = state.get("rule_findings") or []
    risk_report = state.get("risk_report") or {}
    data_quality = state.get("data_quality") or {}

    rule_level = _max_level(rule_findings)
    report_level = int(risk_report.get("overall_severity") or 0)

    if rule_level >= 3:
        decision = "block"
    elif rule_level >= 2:
        decision = "restrict"
    elif report_level >= 2:
        decision = "restrict"
    elif report_level >= 1 or data_quality.get("status") == "degraded":
        decision = "warn"
    else:
        decision = "pass"

    binding_constraints = [
        {
            "rule_id": f.get("rule_id"),
            "message": f.get("message"),
            "severity": f.get("severity"),
        }
        for f in rule_findings
        if f.get("severity") in {"restrict", "block"}
    ]

    return {
        "decision": {
            "decision": decision,
            "rule_level": rule_level,
            "report_level": report_level,
            "reason": "rule findings and risk report aggregation",
        },
        "binding_constraints": binding_constraints,
    }
