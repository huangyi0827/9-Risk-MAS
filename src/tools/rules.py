from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

from ..config import RuntimeConfig, DEFAULT_CONFIG

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


def _rules_path(config: RuntimeConfig | None = None) -> Path:
    cfg = config or DEFAULT_CONFIG
    if cfg.csv_data_dir:
        return Path(cfg.csv_data_dir).expanduser() / "rules.yaml"
    return _ROOT / "cufel_practice_data" / "rules.yaml"


@lru_cache(maxsize=32)
def _load_rules_cached(profile: str, path_str: str) -> Tuple[Dict[str, Any], str]:
    path = Path(path_str)
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data, dict):
            if profile in data:
                return dict(data.get(profile) or {}), "rules.yaml"
            if "default" in data:
                return dict(data.get("default") or {}), "rules.yaml"

    fallback = _DEFAULT_RULES.get(profile) or _DEFAULT_RULES["default"]
    return fallback, "local-default"


def load_rules(profile: str, config: RuntimeConfig | None = None) -> Tuple[Dict[str, Any], str]:
    path = _rules_path(config)
    rules, version = _load_rules_cached(profile, str(path))
    return dict(rules), version


def get_blocklist(profile: str, config: RuntimeConfig | None = None) -> Tuple[list, str]:
    rules, version = load_rules(profile, config)
    blocklist = rules.get("blocklist") or []
    return list(blocklist), version
