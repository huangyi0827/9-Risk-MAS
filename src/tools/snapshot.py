from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState
from ..config import RuntimeConfig, DEFAULT_CONFIG
from .csv_data import market_metrics, lookback_start_date
from .utils import normalize_weights, compute_hhi, compute_effective_n


def risk_snapshot_bundle(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """基于输入权重与行情数据计算指标快照。"""
    cfg = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}
    target_weights = normalized.get("target_weights") or {}
    current_weights = normalized.get("current_positions") or {}
    asof_date = normalized.get("asof_date") or ""
    aum = normalized.get("aum")
    if aum is None:
        aum = cfg.default_aum
    lookback_days = int(cfg.market_lookback_days)
    start_date = lookback_start_date(asof_date, lookback_days)

    codes = set(target_weights) | set(current_weights)
    market = market_metrics(codes, start_date or asof_date, asof_date, cfg)
    missing = [c for c in target_weights if c not in market]

    # Use shared utility functions instead of local definitions
    target_norm = normalize_weights(target_weights)
    current_norm = normalize_weights(current_weights)
    hhi = compute_hhi(target_norm, already_normalized=True)
    effective_n = compute_effective_n(target_norm, already_normalized=True)
    top_weight = max(target_norm.values(), default=0.0)

    current_hhi = compute_hhi(current_norm, already_normalized=True)
    current_effective_n = compute_effective_n(current_norm, already_normalized=True)
    current_top_weight = max(current_norm.values(), default=0.0)

    # turnover and max single position change (based on current vs target)
    all_codes = set(current_weights) | set(target_weights)
    deltas = {c: float(target_weights.get(c, 0.0)) - float(current_weights.get(c, 0.0)) for c in all_codes}
    turnover = 0.5 * sum(abs(v) for v in deltas.values())
    max_position_delta = max((abs(v) for v in deltas.values()), default=0.0)

    weighted_vol = 0.0
    weighted_spread = 0.0
    weighted_adv = 0.0
    max_adv_ratio = None
    adv_by_symbol: Dict[str, float] = {
        code: float(row.get("adv") or 0.0) for code, row in market.items()
    }
    for code, weight in target_norm.items():
        row = market.get(code)
        if not row:
            continue
        weighted_vol += weight * float(row.get("volatility") or 0.0)
        weighted_spread += weight * float(row.get("spread_bps") or 0.0)
        adv = adv_by_symbol.get(code, 0.0)
        weighted_adv += weight * adv
        trade = abs(deltas.get(code, 0.0))
        if adv > 0 and aum:
            ratio = (trade * float(aum)) / adv
            if max_adv_ratio is None or ratio > max_adv_ratio:
                max_adv_ratio = ratio

    current_vol = 0.0
    for code, weight in current_norm.items():
        row = market.get(code)
        if not row:
            continue
        current_vol += weight * float(row.get("volatility") or 0.0)

    macro_severity = 0

    metrics = {
        "portfolio_volatility": weighted_vol,
        "current_portfolio_volatility": current_vol,
        "delta_portfolio_volatility": weighted_vol - current_vol,
        "weighted_spread_bps": weighted_spread,
        "weighted_adv": weighted_adv,
        "hhi": hhi,
        "effective_n": effective_n,
        "top_weight": top_weight,
        "current_hhi": current_hhi,
        "current_effective_n": current_effective_n,
        "current_top_weight": current_top_weight,
        "delta_hhi": hhi - current_hhi,
        "delta_effective_n": effective_n - current_effective_n,
        "turnover": turnover,
        "max_position_delta": max_position_delta,
        "max_adv_ratio": max_adv_ratio,
        "adv_by_symbol": adv_by_symbol,
        "macro_severity": macro_severity,
        "missing_market_rows": missing,
    }

    return {"snapshot_metrics": metrics}
