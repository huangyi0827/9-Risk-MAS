from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from ..state import RiskState
from ..skills_runtime import load_skill
from .rules import load_rules


def _hash_payload(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def audit_log(state: RiskState) -> Dict[str, Any]:
    snapshot = state.get("snapshot_metrics") or {}
    rule_findings = state.get("rule_findings") or []
    profile = (state.get("normalized") or {}).get("policy_profile", "default")
    rules, ruleset_version = load_rules(profile)
    tool_calls = []
    tool_calls.extend(state.get("tool_calls_macro") or [])
    tool_calls.extend(state.get("tool_calls_compliance") or [])
    tool_errors = [t for t in tool_calls if t.get("error")]
    tool_latency = sum(int(t.get("latency_ms") or 0) for t in tool_calls)
    llm_used = bool(
        state.get("llm_used_macro")
        or state.get("llm_used_compliance")
        or state.get("supervisor_used")
    )
    models = []
    for key in ("llm_model_macro", "llm_model_compliance", "supervisor_model"):
        val = state.get(key)
        if val and val not in models:
            models.append(val)

    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    skill_map = {
        "finding_market": "risk-market-assessor",
        "finding_concentration": "risk-market-assessor",
        "finding_diversification": "risk-market-assessor",
        "finding_liquidity": "liquidity-execution-assessor",
        "finding_macro": "macro-tool-calling",
        "finding_compliance": "compliance-evidence",
    }
    skills_used = []
    seen_skills = set()
    for key, skill_name in skill_map.items():
        if state.get(key):
            spec = load_skill(skill_name)
            if spec.name in seen_skills:
                continue
            seen_skills.add(spec.name)
            skills_used.append(
                {
                    "name": spec.name,
                    "policy_version": spec.policy_version,
                    "skills_hash": spec.skills_hash,
                }
            )

    audit = {
        "policy_profile": profile,
        "ruleset_version": ruleset_version,
        "rules_snapshot": rules,
        "rules_snapshot_hash": _hash_payload(rules),
        "data_snapshot_hash": _hash_payload({"snapshot": snapshot, "rules": rule_findings}),
        "tool_calls": tool_calls,
        "tool_call_summary": {
            "count": len(tool_calls),
            "errors": len(tool_errors),
            "total_latency_ms": tool_latency,
        },
        "llm_used": llm_used,
        "llm_model": ", ".join(models) if models else "",
        "gatekeeper_used": state.get("gatekeeper_used", False),
        "gatekeeper_rationale": state.get("gatekeeper_rationale", ""),
        "candidate_nodes": state.get("candidate_nodes") or [],
        "supervisor_used": state.get("supervisor_used", False),
        "supervisor_rationale": state.get("supervisor_rationale", ""),
        "nodes_to_run": state.get("nodes_to_run") or [],
        "skills_used": skills_used,
        "node_outputs": sorted(k for k in state.keys() if k not in {"intent", "context"}),
        "timestamp": ts,
        "trace_id": _hash_payload({"ts": ts}),
    }

    compliance_blocklist = state.get("compliance_blocklist")
    if compliance_blocklist is not None:
        audit["compliance_blocklist"] = compliance_blocklist
        audit["compliance_blocklist_meta"] = state.get("compliance_blocklist_meta") or {}

    return {"audit": audit}
