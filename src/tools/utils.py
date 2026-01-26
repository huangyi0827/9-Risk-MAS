"""Common utility functions for risk tools.

This module contains shared helper functions used across multiple tools,
extracted to reduce code duplication and ensure consistency.
"""
from __future__ import annotations

from typing import Dict

# Tolerance constants for floating-point comparisons
WEIGHT_TOLERANCE = 1e-6
EPSILON = 1e-12


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize weights to sum to 1.0.

    Args:
        weights: Dictionary of symbol -> weight

    Returns:
        Dictionary with normalized weights summing to 1.0
    """
    cleaned = {k: float(v) for k, v in weights.items()}
    total = sum(cleaned.values())
    if total <= 0:
        return cleaned
    return {k: v / total for k, v in cleaned.items()}


def compute_hhi(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """Compute Herfindahl-Hirschman Index (HHI) for concentration.

    HHI = sum(w_i^2) where w_i are normalized weights.
    Values range from 1/n (perfectly diversified) to 1.0 (single holding).

    Args:
        weights: Dictionary of symbol -> weight
        already_normalized: If True, skip normalization step

    Returns:
        HHI value between 0 and 1
    """
    if already_normalized:
        return sum(w ** 2 for w in weights.values())

    total = sum(weights.values())
    if total <= 0:
        return 0.0
    return sum((v / total) ** 2 for v in weights.values())


def compute_effective_n(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """Compute effective number of holdings (inverse HHI).

    Represents the equivalent number of equal-weighted positions
    that would produce the same concentration level.

    Args:
        weights: Dictionary of symbol -> weight
        already_normalized: If True, skip normalization in HHI calculation

    Returns:
        Effective number of holdings (1.0 for single holding, n for equal-weight)
    """
    hhi = compute_hhi(weights, already_normalized)
    return 1.0 / hhi if hhi > EPSILON else 0.0


def weights_sum_to_one(weights: Dict[str, float]) -> bool:
    """Check if weights sum to 1.0 within tolerance.

    Args:
        weights: Dictionary of symbol -> weight

    Returns:
        True if sum is within WEIGHT_TOLERANCE of 1.0
    """
    total = sum(weights.values())
    return abs(total - 1.0) <= WEIGHT_TOLERANCE
