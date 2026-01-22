from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import yaml
import hashlib

try:
    import jsonschema
except ImportError:  # pragma: no cover - optional dependency drift
    jsonschema = None


_ROOT = Path(__file__).resolve().parents[1]
_SKILLS_ROOT = _ROOT / "skills"
_SNIPPETS_ROOT = _SKILLS_ROOT / "snippets"
_TOOL_REGISTRY = _SKILLS_ROOT / "tools" / "tool_interfaces.yaml"


@dataclass(frozen=True)
class SkillSpec:
    name: str
    type: str
    inputs: List[str]
    outputs: List[str]
    allowlist: List[str]
    snippets: List[str]
    body: str
    schema: Optional[Dict[str, Any]]
    policy_version: str
    skills_hash: str
    max_calls: int
    timeout_ms: int
    require_evidence: bool
    limits: Dict[str, Any]
    stop_condition: List[str]
    cost_budget: Dict[str, Any]


def _parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            meta = yaml.safe_load(parts[1]) or {}
            body = parts[2].lstrip("\n")
            return meta, body
    return {}, text


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


@lru_cache(maxsize=None)
def load_skill(skill_dir: str) -> SkillSpec:
    skill_path = _SKILLS_ROOT / skill_dir / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"skill not found: {skill_dir}")

    raw = skill_path.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)

    schema_path = _SKILLS_ROOT / skill_dir / "output.schema.json"
    schema = None
    if schema_path.exists():
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

    tools_meta = meta.get("tools") or {}
    allowlist = list(tools_meta.get("allowlist") or meta.get("allowlist") or [])
    max_calls = int(tools_meta.get("max_calls") or 0)
    timeout_ms = int(tools_meta.get("timeout_ms") or 0)
    require_evidence = bool(tools_meta.get("require_evidence") or False)

    limits = dict(meta.get("limits") or {})
    stop_condition = list(meta.get("stop_condition") or [])
    cost_budget = dict(meta.get("cost_budget") or {})
    policy_version = str(meta.get("policy_version") or "")
    skills_hash = str(meta.get("skills_hash") or _hash_text(raw))

    return SkillSpec(
        name=str(meta.get("name") or skill_dir),
        type=str(meta.get("type") or ""),
        inputs=list(meta.get("inputs") or []),
        outputs=list(meta.get("outputs") or []),
        allowlist=allowlist,
        snippets=list(meta.get("snippets") or []),
        body=body.strip(),
        schema=schema,
        policy_version=policy_version,
        skills_hash=skills_hash,
        max_calls=max_calls,
        timeout_ms=timeout_ms,
        require_evidence=require_evidence,
        limits=limits,
        stop_condition=stop_condition,
        cost_budget=cost_budget,
    )


@lru_cache(maxsize=None)
def load_tool_registry() -> Set[str]:
    if not _TOOL_REGISTRY.exists():
        return set()
    data = yaml.safe_load(_TOOL_REGISTRY.read_text(encoding="utf-8")) or {}
    tools = data.get("tools") or []
    names = [t.get("name") for t in tools if t.get("name")]
    return set(names)


def load_snippet(path: str) -> str:
    snippet_path = _SKILLS_ROOT / path
    if snippet_path.exists():
        return snippet_path.read_text(encoding="utf-8").strip()
    fallback = _SNIPPETS_ROOT / path
    if fallback.exists():
        return fallback.read_text(encoding="utf-8").strip()
    return ""


def build_system_prompt(base: str, skill: SkillSpec) -> str:
    parts = [base]
    if skill.body:
        parts.append(skill.body)
    for snippet in skill.snippets:
        text = load_snippet(snippet)
        if text:
            parts.append(text)
    if skill.schema is not None:
        parts.append("Output must conform to schema:\n" + json.dumps(skill.schema, ensure_ascii=False))
    return "\n\n".join(parts).strip()


def filter_tools(tools: Sequence[Any], allowlist: Sequence[str]) -> List[Any]:
    allow = set(allowlist or [])
    if not allow:
        return list(tools)
    registry = load_tool_registry()
    if registry:
        allow = {name for name in allow if name in registry}
    filtered = []
    for t in tools:
        name = getattr(t, "name", None) or getattr(t, "__name__", "")
        if name in allow:
            filtered.append(t)
    return filtered


def validate_output(skill: SkillSpec, data: Dict[str, Any]) -> List[str]:
    if skill.schema is None or jsonschema is None:
        return []
    validator = jsonschema.Draft202012Validator(skill.schema)
    errors = [e.message for e in validator.iter_errors(data)]
    return errors
