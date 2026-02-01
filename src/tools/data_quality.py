from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from ..config import RuntimeConfig, DEFAULT_CONFIG

from ..state import RiskState
from .csv_data import (
    compliance_docs_available,
    macro_docs_available,
    macro_latest_date,
    market_metrics,
    lookback_start_date,
    security_master_codes,
)


def _append_gap(
    data_gaps: List[Dict[str, Any]],
    status: str,
    *,
    gap_type: str,
    severity: str,
    message: str,
    affect_status: bool = True,
) -> str:
    data_gaps.append({"type": gap_type, "severity": severity, "message": message})
    if not affect_status:
        return status
    if severity == "block":
        return "blocked"
    if severity == "warn" and status == "ok":
        return "degraded"
    return status


def check_data_quality(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """检查数据完整性与新鲜度，生成 data_quality 与 data_gaps。"""
    cfg = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}

    universe = normalized.get("universe") or []
    asof_date = normalized.get("asof_date") or ""
    positions_date = normalized.get("current_positions_date") or ""

    data_gaps: List[Dict[str, Any]] = []
    status = "ok"

    sec_codes, _ = security_master_codes(cfg)
    sec_checked = bool(sec_codes)
    if not sec_checked:
        status = _append_gap(
            data_gaps,
            status,
            gap_type="etf_master",
            severity="warn",
            message="ETF master csv missing",
        )

    market_codes = set()
    market_checked = False
    lookback_days = int(cfg.market_lookback_days)
    start_date = lookback_start_date(asof_date, lookback_days)

    if universe:
        metrics = market_metrics(universe, start_date or asof_date, asof_date, cfg)
        market_checked = True
        market_codes = set(metrics.keys())

    missing_master = [c for c in universe if sec_checked and c not in sec_codes]
    missing_market = [c for c in universe if market_checked and c not in market_codes]

    if missing_master:
        status = _append_gap(
            data_gaps,
            status,
            gap_type="etf_master",
            severity="warn",
            message=f"missing ETF master for: {', '.join(missing_master)}",
        )
    if missing_market:
        status = _append_gap(
            data_gaps,
            status,
            gap_type="market_data",
            severity="warn",
            message=f"missing market data for: {', '.join(missing_market)}",
        )

    freshness_days = None
    timeseries_available = bool(cfg.tushare_token)
    macro_text_available = macro_docs_available(cfg)
    macro_latest = macro_latest_date(asof_date or None, cfg)

    if asof_date and macro_latest:
        try:
            asof = datetime.strptime(asof_date, "%Y-%m-%d")
            latest = datetime.strptime(macro_latest, "%Y-%m-%d")
            freshness_days = (asof - latest).days
        except ValueError:
            freshness_days = None

    compliance_text_available = compliance_docs_available(cfg)

    if missing_market and len(missing_market) == len(universe):
        status = _append_gap(
            data_gaps,
            status,
            gap_type="market_data",
            severity="block",
            message="all universe instruments missing market data",
        )

    macro_stale_days = int(cfg.macro_stale_days)
    if freshness_days is None:
        freshness_status = "unknown"
    elif freshness_days < 0:
        freshness_status = "future"
    elif freshness_days > macro_stale_days:
        freshness_status = "stale"
    else:
        freshness_status = "ok"

    if macro_text_available and freshness_status == "future":
        status = _append_gap(
            data_gaps,
            status,
            gap_type="macro_text",
            severity="block",
            message=f"macro text data is from future date: {macro_latest}",
            affect_status=False,
        )
    elif macro_text_available and freshness_status == "stale":
        status = _append_gap(
            data_gaps,
            status,
            gap_type="macro_text",
            severity="warn",
            message=f"macro text data is stale: {macro_latest}",
            affect_status=False,
        )

    data_quality: Dict[str, Any] = {
        "status": status,
        "market": {
            "missing_etf_master": missing_master,
            "missing_market": missing_market,
        },
        "macro": {
            "timeseries_available": timeseries_available,
            "text_available": macro_text_available,
            "latest_date": macro_latest,
            "freshness_days": freshness_days,
            "freshness_status": freshness_status,
        },
        "compliance": {
            "text_available": compliance_text_available,
        },
        "positions": {
            "freshness_days": None,
        },
    }
    if asof_date and positions_date:
        try:
            asof = datetime.strptime(asof_date, "%Y-%m-%d")
            pos_date = datetime.strptime(positions_date, "%Y-%m-%d")
            data_quality["positions"]["freshness_days"] = (asof - pos_date).days
        except ValueError:
            data_quality["positions"]["freshness_days"] = None

    return {"data_quality": data_quality, "data_gaps": data_gaps}
