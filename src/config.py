"""Centralized configuration management.

This module provides a single source of truth for all environment-based
configuration values used across the risk-mas system. This replaces
scattered os.getenv() calls throughout the codebase.

Usage:
    from src.config import Config

    lookback = Config.MARKET_LOOKBACK_DAYS
    aum = Config.get_aum()
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional


class Config:
    """Centralized configuration class.

    All configuration values are loaded from environment variables with
    sensible defaults. Values are accessed as class attributes.
    """

    # ===== Market Data Configuration =====
    MARKET_LOOKBACK_DAYS: int = int(os.getenv("MARKET_LOOKBACK_DAYS", "60"))
    """Number of days to look back for market data (default: 60)"""

    # ===== Macro Data Configuration =====
    MACRO_STALE_DAYS: int = int(os.getenv("MACRO_STALE_DAYS", "30"))
    """Number of days after which macro data is considered stale (default: 30)"""

    MACRO_SEVERITY_WEIGHT: float = float(os.getenv("MACRO_SEVERITY_WEIGHT", "0.7"))
    """Weight for timeseries-based macro severity vs NLP (default: 0.7)"""

    # ===== Portfolio Configuration =====
    CASH_SYMBOL: str = os.getenv("CASH_SYMBOL", "CASH").strip() or "CASH"
    """Symbol used for cash positions (default: CASH)"""

    # ===== Solver Configuration =====
    LP_TURNOVER_WEIGHT: float = float(os.getenv("LP_TURNOVER_WEIGHT", "0.1"))
    """Weight for turnover penalty in LP solver (default: 0.1)"""

    LP_SOLVER: Optional[str] = os.getenv("LP_SOLVER") or None
    """CVXPY solver to use (default: None = auto-select)"""

    # ===== Data Paths =====
    CSV_DATA_DIR: str = os.getenv("CSV_DATA_DIR", "").strip()
    """Directory containing CSV data files"""

    MACRO_SERIES_CONFIG: str = os.getenv("MACRO_SERIES_CONFIG", "").strip()
    """Path to macro series configuration file"""

    # ===== API Tokens =====
    TUSHARE_TOKEN: str = os.getenv("TUSHARE_TOKEN", "").strip()
    """Tushare API token for market data"""

    @classmethod
    def get_aum(cls) -> Optional[float]:
        """Get portfolio AUM from environment.

        Checks both PORTFOLIO_AUM and AUM environment variables.

        Returns:
            AUM value as float, or None if not configured
        """
        env_aum = os.getenv("PORTFOLIO_AUM") or os.getenv("AUM")
        if env_aum:
            try:
                return float(env_aum)
            except ValueError:
                return None
        return None

    @classmethod
    def get_target_holdings(cls) -> Optional[int]:
        """Get target number of holdings from environment.

        Returns:
            Target holdings as int, or None if not configured
        """
        env_holdings = os.getenv("TARGET_HOLDINGS", "").strip()
        if env_holdings:
            try:
                return int(env_holdings)
            except ValueError:
                return None
        return None

    @classmethod
    @lru_cache(maxsize=1)
    def nlp_severity_weight(cls) -> float:
        """Get NLP severity weight (1 - MACRO_SEVERITY_WEIGHT)."""
        return 1 - cls.MACRO_SEVERITY_WEIGHT


# Convenience exports
MARKET_LOOKBACK_DAYS = Config.MARKET_LOOKBACK_DAYS
MACRO_STALE_DAYS = Config.MACRO_STALE_DAYS
CASH_SYMBOL = Config.CASH_SYMBOL
LP_TURNOVER_WEIGHT = Config.LP_TURNOVER_WEIGHT
