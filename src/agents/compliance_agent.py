from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from langchain.agents import create_agent

from .agent_utils import extract_tool_calls, last_ai_content, wrap_tool
from ..state import RiskState, Finding
from ..tools.csv_data import compliance_search_hits
from ..tools.rules import get_blocklist
from ..skills_runtime import load_skill, build_system_prompt, filter_tools, validate_output


def _provenance(source: str, params: Dict[str, Any]) -> Dict[str, Any]:
    payload = json.dumps(params, sort_keys=True, separators=(",", ":"))
    return {
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "params_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
    }


def _blocklist_payload(profile: str) -> Dict[str, Any]:
    # TODO: replace with RAG-based blocklist retrieval from compliance corpus.
    blocklist, ruleset_version = get_blocklist(profile)
    return {
        "items": list(blocklist),
        "source": ruleset_version,
        "note": "rag_placeholder",
    }


def _policy_search_impl(query: str) -> Dict[str, Any]:
    """Search compliance docs for a query string."""
    hits = compliance_search_hits(query, limit=5)
    return {
        "query": query,
        "hits": hits,
        "provenance": _provenance("compliance_docs", {"query": query, "hits": len(hits)}),
    }


def _allowlist_check_impl(code: str, profile: str = "default") -> Dict[str, Any]:
    """Check if a code is allowed by policy."""
    payload = _blocklist_payload(profile)
    blocked = payload.get("items") or []
    allowed = code not in blocked
    return {
        "code": code,
        "allowed": allowed,
        "blocklist_source": payload.get("source"),
        "provenance": _provenance("risk_rules", {"code": code, "allowed": allowed, "profile": profile}),
    }


policy_search = wrap_tool("policy_search", _policy_search_impl)
allowlist_check = wrap_tool("allowlist_check", _allowlist_check_impl)


def _fallback_finding(state: RiskState, blocklist: List[str]) -> Finding:
    normalized = state.get("normalized") or {}
    targets = normalized.get("target_weights") or {}
    blocked = [c for c in targets if c in blocklist]
    if blocked:
        severity = 3
        summary = f"目标中包含禁投标的: {', '.join(blocked)}"
        policy_ids = ["blocklist"]
    else:
        severity = 0
        summary = "未发现合规问题"
        policy_ids = []

    return {
        "agent": "ComplianceToolCallingAgent",
        "risk_type": "compliance",
        "severity": severity,
        "summary": summary,
        "policy_ids": policy_ids,
        "evidence": [{"ref": "tool:compliance_blocklist", "value": blocked}],
        "recommendations": ["请复核合规规则"],
    }


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")


def run_compliance_agent(state: RiskState, llm) -> Dict[str, Any]:
    normalized = state.get("normalized") or {}
    profile = normalized.get("policy_profile", "default")
    blocklist_payload = _blocklist_payload(profile)
    blocklist = blocklist_payload.get("items") or []

    if llm is None:
        return {
            "finding_compliance": _fallback_finding(state, blocklist),
            "compliance_blocklist": blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": [],
            "llm_used_compliance": False,
            "llm_model_compliance": "",
        }

    skill = load_skill("compliance-evidence")
    tools = filter_tools([policy_search, allowlist_check], skill.allowlist)
    if not tools:
        return {
            "finding_compliance": _fallback_finding(state, blocklist),
            "compliance_blocklist": blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": [],
            "llm_used_compliance": False,
            "llm_model_compliance": "",
        }

    system_prompt = build_system_prompt("", skill)
    agent = create_agent(llm, tools, system_prompt=system_prompt)

    payload = {
        "normalized": normalized,
        "snapshot_metrics": state.get("snapshot_metrics") or {},
        "policy_profile": profile,
    }
    user_payload = json.dumps(payload, separators=(",", ":"))
    result = agent.invoke({"messages": [{"role": "user", "content": f"Input state: {user_payload}"}]})
    llm_model = _llm_model_name(llm)

    messages = result.get("messages", []) if isinstance(result, dict) else []
    tool_calls = extract_tool_calls(messages)

    output = last_ai_content(messages)
    try:
        parsed = json.loads(output)
    except json.JSONDecodeError:
        parsed = {}

    errors = validate_output(skill, parsed)
    if errors:
        tool_calls.append({"tool": "schema_validation", "errors": errors, "skill": skill.name})
        return {
            "finding_compliance": _fallback_finding(state, blocklist),
            "compliance_blocklist": blocklist,
            "compliance_blocklist_meta": blocklist_payload,
            "tool_calls_compliance": tool_calls,
            "llm_used_compliance": True,
            "llm_model_compliance": llm_model,
        }

    finding: Finding = {
        "agent": "ComplianceToolCallingAgent",
        "risk_type": "compliance",
        "severity": int(parsed.get("severity", 0)),
        "summary": parsed.get("summary", ""),
        "evidence": parsed.get("evidence", []),
        "recommendations": parsed.get("recommendations", []),
        "policy_ids": parsed.get("policy_ids", []),
    }

    return {
        "finding_compliance": finding,
        "compliance_blocklist": blocklist,
        "compliance_blocklist_meta": blocklist_payload,
        "tool_calls_compliance": tool_calls,
        "llm_used_compliance": True,
        "llm_model_compliance": llm_model,
    }
