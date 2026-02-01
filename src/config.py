"""集中化配置管理。

本模块提供统一的环境变量配置入口，作为 risk-mas 的单一配置来源。
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_optional_float(name: str) -> Optional[float]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _env_optional_int(name: str) -> Optional[int]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        return None


def _env_bool(name: str, default: bool = True) -> bool:
    raw = os.getenv(name, "").strip().lower()
    if not raw:
        return default
    return raw not in {"0", "false", "no", "off"}


@dataclass(frozen=True)
class RuntimeConfig:
    market_lookback_days: int = 60
    macro_stale_days: int = 30
    macro_severity_weight: float = 0.7
    cash_symbol: str = "CASH"
    lp_turnover_weight: float = 0.1
    lp_solver: Optional[str] = None
    csv_data_dir: str = ""
    macro_series_config: str = ""
    tushare_token: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""
    llm_model: str = ""
    enable_supervisor: bool = True
    sample_universe_size: int = 5
    random_seed: Optional[str] = None
    asof_date: str = ""
    default_aum: Optional[float] = None
    target_holdings: Optional[int] = None
    compliance_rag_source: str = ""
    rag_engine: str = "vector"

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        return cls(
            market_lookback_days=_env_int("MARKET_LOOKBACK_DAYS", 60),
            macro_stale_days=_env_int("MACRO_STALE_DAYS", 30),
            macro_severity_weight=_env_float("MACRO_SEVERITY_WEIGHT", 0.7),
            cash_symbol=(os.getenv("CASH_SYMBOL", "CASH").strip() or "CASH"),
            lp_turnover_weight=_env_float("LP_TURNOVER_WEIGHT", 0.1),
            lp_solver=os.getenv("LP_SOLVER") or None,
            csv_data_dir=os.getenv("CSV_DATA_DIR", "").strip(),
            macro_series_config=os.getenv("MACRO_SERIES_CONFIG", "").strip(),
            tushare_token=os.getenv("TUSHARE_TOKEN", "").strip(),
            openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "").strip(),
            llm_model=os.getenv("LLM_MODEL", "").strip(),
            enable_supervisor=_env_bool("ENABLE_SUPERVISOR", True),
            sample_universe_size=_env_int("SAMPLE_UNIVERSE_SIZE", 5),
            random_seed=os.getenv("RANDOM_SEED") or None,
            asof_date=os.getenv("ASOF_DATE", "").strip(),
            default_aum=_env_optional_float("PORTFOLIO_AUM")
            or _env_optional_float("AUM"),
            target_holdings=_env_optional_int("TARGET_HOLDINGS"),
            compliance_rag_source=os.getenv("COMPLIANCE_RAG_SOURCE", "").strip(),
            rag_engine=os.getenv("RAG_ENGINE", "vector").strip().lower(),
        )

    @property
    def nlp_severity_weight(self) -> float:
        return 1 - self.macro_severity_weight


DEFAULT_CONFIG = RuntimeConfig.from_env()


# Backwards compatibility
Config = RuntimeConfig
