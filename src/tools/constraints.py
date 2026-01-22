from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState
from .rules import load_rules


_LEVEL = {"pass": 0, "warn": 1, "restrict": 2, "block": 3}


def constraints_evaluator(state: RiskState) -> Dict[str, Any]:
    normalized = state.get("normalized") or {}
    metrics = state.get("snapshot_metrics") or {}

    profile, _ = load_rules(normalized.get("policy_profile", "default"))

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

    max_single = float(profile.get("max_single_weight", 1.0))
    top_weight = float(metrics.get("top_weight", 0.0))
    if top_weight > max_single:
        add(
            "max_single_weight",
            "restrict",
            "top_weight",
            top_weight,
            max_single,
            "single position exceeds maximum weight",
        )

    max_hhi = float(profile.get("max_hhi", 1.0))
    hhi = float(metrics.get("hhi", 0.0))
    if hhi > max_hhi:
        add(
            "max_hhi",
            "warn",
            "hhi",
            hhi,
            max_hhi,
            "concentration exceeds target",
        )

    max_vol = float(profile.get("max_portfolio_volatility", 1.0))
    vol = float(metrics.get("portfolio_volatility", 0.0))
    if vol > max_vol:
        add(
            "max_portfolio_volatility",
            "restrict",
            "portfolio_volatility",
            vol,
            max_vol,
            "portfolio volatility above limit",
        )

    max_spread = float(profile.get("max_weighted_spread_bps", 1.0e9))
    spread = float(metrics.get("weighted_spread_bps", 0.0))
    if spread > max_spread:
        add(
            "max_weighted_spread_bps",
            "warn",
            "weighted_spread_bps",
            spread,
            max_spread,
            "liquidity spread above threshold",
        )

    min_adv = float(profile.get("min_weighted_adv", 0.0))
    adv = float(metrics.get("weighted_adv", 0.0))
    if adv < min_adv and min_adv > 0:
        add(
            "min_weighted_adv",
            "warn",
            "weighted_adv",
            adv,
            min_adv,
            "average daily value below minimum",
        )

    max_turnover = float(profile.get("max_turnover", 1.0))
    turnover = float(metrics.get("turnover", 0.0))
    if turnover > max_turnover:
        add(
            "max_turnover",
            "warn",
            "turnover",
            turnover,
            max_turnover,
            "turnover above threshold",
        )

    max_delta = float(profile.get("max_position_delta", 1.0))
    max_position_delta = float(metrics.get("max_position_delta", 0.0))
    if max_position_delta > max_delta:
        add(
            "max_position_delta",
            "warn",
            "max_position_delta",
            max_position_delta,
            max_delta,
            "single position change above threshold",
        )

    max_adv_ratio = float(profile.get("max_adv_ratio", 1.0))
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

    max_delta_hhi = float(profile.get("max_delta_hhi", 1.0))
    delta_hhi = float(metrics.get("delta_hhi", 0.0))
    if delta_hhi > max_delta_hhi:
        add(
            "max_delta_hhi",
            "warn",
            "delta_hhi",
            delta_hhi,
            max_delta_hhi,
            "hhi increase above threshold",
        )

    max_delta_vol = float(profile.get("max_delta_volatility", 1.0))
    delta_vol = float(metrics.get("delta_portfolio_volatility", 0.0))
    if delta_vol > max_delta_vol:
        add(
            "max_delta_volatility",
            "warn",
            "delta_portfolio_volatility",
            delta_vol,
            max_delta_vol,
            "volatility increase above threshold",
        )

    blocklist = set(state.get("compliance_blocklist") or profile.get("blocklist") or [])
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
