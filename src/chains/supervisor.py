from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from ..state import RiskState
from ..skills_runtime import load_skill, build_system_prompt, validate_output


_BASE_PROMPT = (
    "你是系统调度员，负责决定运行哪些分析节点。"
    "只能从提供的候选列表中选择。"
    "始终返回 JSON，包含 keys: nodes_to_run (list of strings) 和 rationale (string)。"
    "rationale 必须为中文。"
)


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")


def _normalize_nodes(nodes: List[str], candidates: List[str]) -> List[str]:
    allow = set(candidates)
    out = [n for n in nodes if n in allow]
    # Keep only nodes chosen by supervisor (within candidates).
    return out


def supervisor_chain(state: RiskState, llm, candidates: List[str]) -> Dict[str, Any]:
    if state.get("stop_condition"):
        return {}

    enabled = os.getenv("ENABLE_SUPERVISOR", "1").strip() not in {"0", "false", "False"}
    if not enabled:
        return {
            "nodes_to_run": candidates,
            "pending_agents": candidates,
            "supervisor_used": False,
            "supervisor_rationale": "disabled",
        }

    data_quality = state.get("data_quality") or {}
    unavailable = []
    if not data_quality.get("macro_available", False):
        unavailable.append("macro")
    if not data_quality.get("compliance_available", False):
        unavailable.append("compliance")

    # If no LLM available, fall back to candidates unchanged.
    if llm is None:
        rationale = "llm unavailable"
        if unavailable:
            rationale = f"未纳入候选（数据不可用）：{','.join(unavailable)}"
        return {
            "nodes_to_run": candidates,
            "pending_agents": candidates,
            "supervisor_used": False,
            "supervisor_rationale": rationale,
        }

    skill = load_skill("supervisor-router")
    system_prompt = build_system_prompt(_BASE_PROMPT, skill)

    payload = {
        "candidates": candidates,
        "validation": state.get("validation") or {},
        "data_quality": state.get("data_quality") or {},
        "snapshot_metrics": state.get("snapshot_metrics") or {},
        "rule_findings": state.get("rule_findings") or [],
        "policy_profile": (state.get("normalized") or {}).get("policy_profile", "default"),
    }

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=json.dumps(payload, ensure_ascii=False, separators=(",", ":"))),
        ]
    )

    content = getattr(response, "content", "") or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        rationale = "invalid json"
        if unavailable:
            rationale = f"未纳入候选（数据不可用）：{','.join(unavailable)}"
        return {
            "nodes_to_run": candidates,
            "pending_agents": candidates,
            "supervisor_used": True,
            "supervisor_rationale": rationale,
        }

    errors = validate_output(skill, parsed)
    if errors:
        rationale = f"schema invalid: {errors}"
        if unavailable:
            rationale = f"未纳入候选（数据不可用）：{','.join(unavailable)}"
        return {
            "nodes_to_run": candidates,
            "pending_agents": candidates,
            "supervisor_used": True,
            "supervisor_rationale": rationale,
        }

    nodes = _normalize_nodes(list(parsed.get("nodes_to_run") or []), candidates)
    rationale = str(parsed.get("rationale") or "")
    if unavailable:
        rationale = f"{rationale} 未纳入候选（数据不可用）：{','.join(unavailable)}".strip()

    chosen = nodes or candidates
    return {
        "nodes_to_run": chosen,
        "pending_agents": chosen,
        "supervisor_used": True,
        "supervisor_rationale": rationale,
        "supervisor_model": _llm_model_name(llm),
    }
