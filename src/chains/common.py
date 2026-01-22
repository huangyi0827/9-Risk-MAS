from __future__ import annotations

from functools import lru_cache
from typing import Any, Dict

from ..skills_runtime import load_skill, validate_output
from ..tools.rules import load_rules


@lru_cache(maxsize=4)
def load_rules_cached(profile: str) -> Dict[str, Any]:
    rules, _ = load_rules(profile)
    return rules


def validate_finding(skill_name: str, finding: Dict[str, Any], label: str) -> None:
    errors = validate_output(load_skill(skill_name), finding)
    if errors:
        raise RuntimeError(f"{label} skill output invalid: {errors}")
