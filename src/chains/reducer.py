from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState, Finding
from ..skills_runtime import load_skill


_ALLOWED_EVIDENCE_PREFIXES = ("snapshot_metrics.", "rules.", "tool:")


def _is_allowed_ref(ref: str) -> bool:
    return any(ref.startswith(p) for p in _ALLOWED_EVIDENCE_PREFIXES)


def _sanitize_evidence(
    state: RiskState, evidence: List[Dict[str, Any]], gaps: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    sanitized: List[Dict[str, Any]] = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        ref = str(item.get("ref") or "").strip()
        if not ref:
            continue
        if not _is_allowed_ref(ref):
            gaps.append(
                {
                    "type": "evidence",
                    "severity": "warn",
                    "message": f"evidence ref not allowed: {ref}",
                }
            )
            continue
        cleaned = dict(item)
        if ref.startswith("snapshot_metrics."):
            key = ref.split(".", 1)[1]
            cleaned["value"] = (state.get("snapshot_metrics") or {}).get(key)
        sanitized.append(cleaned)
    return sanitized


def reducer_chain(state: RiskState) -> Dict[str, Any]:
    findings: List[Finding] = []
    evidence_gaps: List[Dict[str, Any]] = []
    skill_map = {
        "MarketRiskChain": "risk-market-assessor",
        "ConcentrationChain": "risk-market-assessor",
        "DiversificationChain": "risk-market-assessor",
        "LiquidityChain": "liquidity-execution-assessor",
        "MacroToolCallingAgent": "macro-tool-calling",
        "ComplianceToolCallingAgent": "compliance-evidence",
    }
    for key in (
        "finding_market",
        "finding_concentration",
        "finding_diversification",
        "finding_liquidity",
        "finding_macro",
        "finding_compliance",
    ):
        f = state.get(key)
        if f:
            f = dict(f)
            findings.append(f)
            skill_name = skill_map.get(str(f.get("agent") or ""))
            if skill_name:
                spec = load_skill(skill_name)
                evidence = f.get("evidence") or []
                if isinstance(evidence, list):
                    evidence = _sanitize_evidence(state, evidence, evidence_gaps)
                else:
                    evidence = []
                f["evidence"] = evidence
                if spec.require_evidence:
                    ok = bool(evidence) and all(isinstance(item, dict) and item.get("ref") for item in evidence)
                    if not ok:
                        evidence_gaps.append(
                            {
                                "type": "evidence",
                                "severity": "warn",
                                "message": f"missing or invalid evidence for {f.get('agent')}",
                            }
                        )

    overall = max((int(f.get("severity", 0)) for f in findings), default=0)
    summary = "未发现显著风险" if overall == 0 else "发现风险，请查看明细"

    report = {
        "overall_severity": overall,
        "summary": summary,
        "findings": findings,
        "data_gaps": (state.get("data_gaps") or []) + evidence_gaps,
    }

    return {
        "findings": findings,
        "risk_report": report,
        "data_gaps": report["data_gaps"],
    }
