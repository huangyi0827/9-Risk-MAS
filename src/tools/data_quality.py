from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List

import os

from ..state import RiskState
from .csv_data import (
    compliance_docs_available,
    macro_docs_available,
    macro_latest_date,
    market_metrics,
    security_master_codes,
)


def check_data_quality(state: RiskState) -> Dict[str, Any]:
    normalized = state.get("normalized") or {}

    universe = normalized.get("universe") or []
    asof_date = normalized.get("asof_date") or ""
    positions_date = normalized.get("current_positions_date") or ""

    data_gaps: List[Dict[str, Any]] = []
    status = "ok"

    sec_codes, _ = security_master_codes()
    sec_checked = bool(sec_codes)
    if not sec_checked:
        data_gaps.append(
            {"type": "security_master", "severity": "warn", "message": "security master csv missing"}
        )
        if status == "ok":
            status = "degraded"

    market_codes = set()
    market_checked = False
    lookback_days = int(os.getenv("MARKET_LOOKBACK_DAYS", "60"))
    start_date = ""
    if asof_date:
        try:
            start_date = (datetime.strptime(asof_date, "%Y-%m-%d") - timedelta(days=lookback_days)).date().isoformat()
        except ValueError:
            start_date = ""

    if universe:
        metrics = market_metrics(universe, start_date or asof_date, asof_date)
        market_checked = True
        market_codes = set(metrics.keys())

    missing_master = [c for c in universe if sec_checked and c not in sec_codes]
    missing_market = [c for c in universe if market_checked and c not in market_codes]

    if missing_master:
        data_gaps.append(
            {
                "type": "security_master",
                "severity": "warn",
                "message": f"missing security master for: {', '.join(missing_master)}",
            }
        )
        if status == "ok":
            status = "degraded"
    if missing_market:
        data_gaps.append(
            {
                "type": "market_data",
                "severity": "warn",
                "message": f"missing market data for: {', '.join(missing_market)}",
            }
        )
        if status == "ok":
            status = "degraded"

    macro_latest = ""
    freshness_days = None
    macro_available = bool(os.getenv("TUSHARE_TOKEN", "").strip()) or macro_docs_available()
    macro_latest = macro_latest_date(asof_date or None)

    if asof_date and macro_latest:
        try:
            asof = datetime.strptime(asof_date, "%Y-%m-%d")
            latest = datetime.strptime(macro_latest, "%Y-%m-%d")
            freshness_days = (asof - latest).days
        except ValueError:
            freshness_days = None

    compliance_available = compliance_docs_available()

    if missing_market and len(missing_market) == len(universe):
        status = "blocked"
        data_gaps.append(
            {
                "type": "market_data",
                "severity": "block",
                "message": "all universe instruments missing market data",
            }
        )

    data_quality = {
        "status": status,
        "missing_security_master": missing_master,
        "missing_market": missing_market,
        "macro_latest_date": macro_latest,
        "macro_freshness_days": freshness_days,
        "macro_available": macro_available,
        "compliance_available": compliance_available,
    }
    if asof_date and positions_date:
        try:
            asof = datetime.strptime(asof_date, "%Y-%m-%d")
            pos_date = datetime.strptime(positions_date, "%Y-%m-%d")
            data_quality["positions_freshness_days"] = (asof - pos_date).days
        except ValueError:
            data_quality["positions_freshness_days"] = None

    return {"data_quality": data_quality, "data_gaps": data_gaps}
