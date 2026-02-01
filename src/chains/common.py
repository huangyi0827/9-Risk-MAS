from __future__ import annotations

from typing import Any, Dict

from ..skills_runtime import load_skill, validate_output
from ..tools.rules import load_rules
from ..config import RuntimeConfig, DEFAULT_CONFIG


def load_rules_cached(profile: str, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    rules, _ = load_rules(profile, config or DEFAULT_CONFIG)
    return rules


def validate_finding(skill_name: str, finding: Dict[str, Any], label: str) -> None:
    errors = validate_output(load_skill(skill_name), finding)
    if errors:
        raise RuntimeError(f"{label} skill output invalid: {errors}")
