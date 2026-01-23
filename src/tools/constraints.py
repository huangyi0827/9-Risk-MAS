from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState
from .rules import load_rules


_LEVEL = {"pass": 0, "warn": 1, "restrict": 2, "block": 3}


def constraints_evaluator(state: RiskState) -> Dict[str, Any]:
    normalized = state.get("normalized") or {}
    metrics = state.get("snapshot_metrics") or {}

    rules, _ = load_rules(normalized.get("policy_profile", "default"))

    findings: List[Dict[str, Any]] = []

    def add(rule_id: str, severity: str, metric: str, value: float, limit: float, message: str) -> None:
        findings.append(
            {
                "rule_id": rule_id,
                "severity": severity,
                "level": _LEVEL.get(severity, 0),
                "metric": metric,
                "value": value,
                "limit": limit,
                "message": message,
                "evidence": [{"ref": f"snapshot_metrics.{metric}", "value": value}],
            }
        )

    def _get_float(mapping: Dict[str, Any], key: str, default: float) -> float:
        try:
            return float(mapping.get(key, default))
        except (TypeError, ValueError):
            return float(default)

    def _metric(key: str) -> float:
        return _get_float(metrics, key, 0.0)

    def _rule(key: str, default: float) -> float:
        return _get_float(rules, key, default)

    def _check_max(rule_id: str, metric_key: str, limit: float, severity: str, message: str) -> None:
        value = _metric(metric_key)
        if value > limit:
            add(rule_id, severity, metric_key, value, limit, message)

    def _check_min(rule_id: str, metric_key: str, limit: float, severity: str, message: str) -> None:
        value = _metric(metric_key)
        if limit > 0 and value < limit:
            add(rule_id, severity, metric_key, value, limit, message)

    _check_max(
        "max_single_weight",
        "top_weight",
        _rule("max_single_weight", 1.0),
        "restrict",
        "single position exceeds maximum weight",
    )
    _check_max(
        "max_hhi",
        "hhi",
        _rule("max_hhi", 1.0),
        "warn",
        "concentration exceeds target",
    )
    _check_max(
        "max_portfolio_volatility",
        "portfolio_volatility",
        _rule("max_portfolio_volatility", 1.0),
        "restrict",
        "portfolio volatility above limit",
    )
    _check_max(
        "max_weighted_spread_bps",
        "weighted_spread_bps",
        _rule("max_weighted_spread_bps", 1.0e9),
        "warn",
        "liquidity spread above threshold",
    )
    _check_min(
        "min_weighted_adv",
        "weighted_adv",
        _rule("min_weighted_adv", 0.0),
        "warn",
        "average daily value below minimum",
    )
    _check_max(
        "max_turnover",
        "turnover",
        _rule("max_turnover", 1.0),
        "warn",
        "turnover above threshold",
    )
    _check_max(
        "max_position_delta",
        "max_position_delta",
        _rule("max_position_delta", 1.0),
        "warn",
        "single position change above threshold",
    )

    max_adv_ratio = _rule("max_adv_ratio", 1.0)
    adv_ratio_raw = metrics.get("max_adv_ratio")
    try:
        adv_ratio = float(adv_ratio_raw)
    except (TypeError, ValueError):
        adv_ratio = None
    if adv_ratio is not None and adv_ratio > max_adv_ratio:
        add(
            "max_adv_ratio",
            "warn",
            "max_adv_ratio",
            adv_ratio,
            max_adv_ratio,
            "trade size above adv ratio threshold",
        )

    _check_max(
        "max_delta_hhi",
        "delta_hhi",
        _rule("max_delta_hhi", 1.0),
        "warn",
        "hhi increase above threshold",
    )
    _check_max(
        "max_delta_volatility",
        "delta_portfolio_volatility",
        _rule("max_delta_volatility", 1.0),
        "warn",
        "volatility increase above threshold",
    )

    blocklist = set(state.get("compliance_blocklist") or rules.get("blocklist") or [])
    target_weights = normalized.get("target_weights") or {}
    blocked = [c for c, w in target_weights.items() if c in blocklist and w > 0]
    if blocked:
        add(
            "blocklist",
            "block",
            "blocked_assets",
            float(len(blocked)),
            0.0,
            f"blocked assets present: {', '.join(blocked)}",
        )

    return {"rule_findings": findings}
