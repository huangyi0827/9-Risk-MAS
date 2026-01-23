from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Tuple

from ..state import RiskState
from ..tools.csv_data import previous_trading_date


def _sum_weights(weights: Dict[str, float]) -> float:
    return float(sum(weights.values())) if weights else 0.0


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = _sum_weights(weights)
    if total <= 0:
        return weights
    return {k: v / total for k, v in weights.items()}


def _coerce_weights(weights: Dict[str, Any], errors: list[str], label: str) -> Dict[str, float]:
    coerced: Dict[str, float] = {}
    for key, value in (weights or {}).items():
        try:
            coerced[key] = float(value)
        except (TypeError, ValueError):
            errors.append(f"{label} weight for {key} is not a number")
    return coerced


def _validate_date(date_str: str) -> Tuple[bool, str]:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True, ""
    except ValueError as exc:
        return False, f"invalid date: {exc}"


def validate_and_normalize(state: RiskState) -> Dict[str, Any]:
    intent = state.get("intent") or {}
    context = state.get("context") or {}

    errors = []
    warnings = []

    date_str = str(intent.get("date") or "").strip()
    if not date_str:
        errors.append("missing date")
    else:
        ok, msg = _validate_date(date_str)
        if not ok:
            errors.append(msg)

    mode = str(intent.get("mode") or "target").strip().lower()
    if mode not in {"target", "delta"}:
        errors.append("mode must be target or delta")

    targets = _coerce_weights(intent.get("targets") or {}, errors, "target")
    if not targets:
        errors.append("no targets provided")

    current = _coerce_weights(context.get("current_positions") or {}, errors, "current")
    current_positions_date = context.get("current_positions_date")

    if mode == "delta":
        target_weights = {k: current.get(k, 0.0) + v for k, v in targets.items()}
        target_weights = _normalize_weights(target_weights)
    else:
        target_weights = dict(targets)
        total = _sum_weights(target_weights)
        if abs(total - 1.0) > 1e-6:
            warnings.append("target weights do not sum to 1.0; normalized")
            target_weights = _normalize_weights(target_weights)

    universe_sources = []
    universe_sources.extend(context.get("universe") or [])
    universe_sources.extend(current.keys())
    universe_sources.extend(target_weights.keys())
    universe = [u for u in dict.fromkeys(universe_sources) if str(u).strip()]
    if not universe:
        universe = list(target_weights.keys())

    asof_date = previous_trading_date(date_str)
    normalized = {
        "asof_date": asof_date,
        "mode": mode,
        "targets": targets,
        "current_positions": current,
        "current_positions_date": current_positions_date,
        "target_weights": target_weights,
        "universe": universe,
        "account_type": context.get("account_type"),
        "jurisdiction": context.get("jurisdiction"),
        "policy_profile": context.get("policy_profile", "default"),
        "aum": context.get("aum"),
    }

    return {
        "normalized": normalized,
        "validation": {
            "is_valid": not errors,
            "errors": errors,
            "warnings": warnings,
        },
    }
