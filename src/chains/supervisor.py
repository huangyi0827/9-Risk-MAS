from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from ..state import RiskState
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..skills_runtime import load_skill, build_system_prompt, validate_output


_BASE_PROMPT = (
    "你是系统调度员，负责决定运行哪些分析节点。"
    "只能从提供的候选列表中选择。"
    "始终返回 JSON，包含 keys: nodes_to_run (list of strings) 和 rationale (string)。"
    "rationale 必须为中文。"
    "rationale 只能引用 payload 中已有的指标与结论，禁止编造具体数值；如需提及指标，优先不写具体数值。"
)


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")


def _fallback_result(
    candidates: List[str],
    *,
    used: bool,
    rationale: str,
) -> Dict[str, Any]:
    return {
        "nodes_to_run": candidates,
        "pending_agents": candidates,
        "supervisor_used": used,
        "supervisor_rationale": rationale,
    }


def _normalize_nodes(nodes: List[str], candidates: List[str]) -> List[str]:
    allow = set(candidates)
    out = [n for n in nodes if n in allow]
    # Keep only nodes chosen by supervisor (within candidates).
    return out


def supervisor_chain(
    state: RiskState, llm, candidates: List[str], config: RuntimeConfig | None = None
) -> Dict[str, Any]:
    cfg = config or DEFAULT_CONFIG
    if state.get("stop_condition"):
        return {}

    enabled = bool(cfg.enable_supervisor)
    if not enabled:
        return _fallback_result(
            candidates,
            used=False,
            rationale="disabled",
        )

    # If no LLM available, fall back to candidates unchanged.
    if llm is None:
        return _fallback_result(
            candidates,
            used=False,
            rationale="llm unavailable",
        )

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
        return _fallback_result(
            candidates,
            used=True,
            rationale="invalid json",
        )

    errors = validate_output(skill, parsed)
    if errors:
        return _fallback_result(
            candidates,
            used=True,
            rationale=f"schema invalid: {errors}",
        )

    nodes = _normalize_nodes(list(parsed.get("nodes_to_run") or []), candidates)
    rationale = str(parsed.get("rationale") or "")

    chosen = nodes or candidates
    return {
        "nodes_to_run": chosen,
        "pending_agents": chosen,
        "supervisor_used": True,
        "supervisor_rationale": rationale,
        "supervisor_model": _llm_model_name(llm),
    }
