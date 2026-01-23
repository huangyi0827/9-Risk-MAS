from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml


_DEFAULT_RULES = {
    "default": {
        "max_single_weight": 0.4,
        "max_hhi": 0.3,
        "max_portfolio_volatility": 0.24,
        "max_weighted_spread_bps": 50,
        "min_weighted_adv": 3000000,
        "blocklist": ["CCC"],
    },
    "conservative": {
        "max_single_weight": 0.3,
        "max_hhi": 0.25,
        "max_portfolio_volatility": 0.2,
        "max_weighted_spread_bps": 40,
        "min_weighted_adv": 5000000,
        "blocklist": ["CCC"],
    },
}

_ROOT = Path(__file__).resolve().parents[2]
_RULES_BASE = Path(os.getenv("CSV_DATA_DIR", "")).expanduser() if os.getenv("CSV_DATA_DIR") else _ROOT / "cufel_practice_data"
_RULES_PATH = _RULES_BASE / "rules.yaml"


@lru_cache(maxsize=8)
def _load_rules_cached(profile: str) -> Tuple[Dict[str, Any], str]:
    if _RULES_PATH.exists():
        data = yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            if profile in data:
                return dict(data.get(profile) or {}), "rules.yaml"
            if "default" in data:
                return dict(data.get("default") or {}), "rules.yaml"

    fallback = _DEFAULT_RULES.get(profile) or _DEFAULT_RULES["default"]
    return fallback, "local-default"


def load_rules(profile: str) -> Tuple[Dict[str, Any], str]:
    rules, version = _load_rules_cached(profile)
    return dict(rules), version


def get_blocklist(profile: str) -> Tuple[list, str]:
    rules, version = load_rules(profile)
    blocklist = rules.get("blocklist") or []
    return list(blocklist), version
