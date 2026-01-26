from __future__ import annotations

import os
from typing import Dict, Any, List, Tuple, Optional

try:
    import cvxpy as cp
except ImportError:  # pragma: no cover - optional dependency
    cp = None

from ..state import RiskState
from .rules import load_rules
from .utils import normalize_weights, compute_hhi, compute_effective_n


def _strip_cash(weights: Dict[str, float], cash_symbol: str) -> Dict[str, float]:
    return {k: v for k, v in weights.items() if k != cash_symbol}


def _cap_and_fill(
    weights: Dict[str, float], cap: float, cash_symbol: str
) -> Dict[str, float]:
    out = {k: float(v) for k, v in weights.items() if float(v) > 0}
    if cap <= 0:
        return out

    excess = 0.0
    for k, v in list(out.items()):
        if v > cap:
            excess += v - cap
            out[k] = cap

    # redistribute excess to those under cap
    for _ in range(5):
        if excess <= 1e-12:
            break
        capacity = {k: cap - v for k, v in out.items() if k != cash_symbol and v < cap}
        total_cap = float(sum(capacity.values()))
        if total_cap <= 1e-12:
            break
        for k, cap_left in capacity.items():
            out[k] += excess * (cap_left / total_cap)
        excess = max(0.0, 1.0 - float(sum(out.values())))

    if excess > 1e-8:
        out[cash_symbol] = out.get(cash_symbol, 0.0) + excess

    return out


def _blend_equal(weights: Dict[str, float], alpha: float) -> Dict[str, float]:
    keys = list(weights.keys())
    n = len(keys)
    if n == 0:
        return weights
    equal = 1.0 / n
    return {k: (1.0 - alpha) * float(weights.get(k, 0.0)) + alpha * equal for k in keys}


def _limit_holdings(
    weights: Dict[str, float],
    max_holdings: Optional[int],
    cash_symbol: str,
) -> Tuple[Dict[str, float], bool]:
    if not max_holdings or max_holdings <= 0:
        return weights, False
    non_cash = {k: float(v) for k, v in weights.items() if k != cash_symbol}
    if len(non_cash) <= max_holdings:
        return weights, False
    top = sorted(non_cash.items(), key=lambda kv: kv[1], reverse=True)[:max_holdings]
    trimmed = {k: v for k, v in top}
    cash = float(weights.get(cash_symbol, 0.0))
    if cash > 0:
        trimmed[cash_symbol] = cash
    return normalize_weights(trimmed), True

def _adjust_weights(
    target_weights: Dict[str, float],
    profile: Dict[str, Any],
    drivers: List[str],
) -> Tuple[Dict[str, float], List[str]]:
    notes: List[str] = []
    cash_symbol = str(profile.get("cash_symbol") or os.getenv("CASH_SYMBOL", "CASH")).strip() or "CASH"
    cap = float(profile.get("max_single_weight", 1.0))
    adjusted = _cap_and_fill(target_weights, cap, cash_symbol)
    if adjusted != target_weights:
        notes.append("cap_max_single_weight")

    need_diversify = "concentration" in drivers or "diversification" in drivers
    hhi_target = float(profile.get("hhi_restrict") or profile.get("max_hhi") or 0.0)
    n_target = float(profile.get("effective_n_restrict") or 0.0)
    if need_diversify:
        base = _strip_cash(adjusted, cash_symbol)
        if (hhi_target and compute_hhi(base) > hhi_target) or (n_target and compute_effective_n(base) < n_target):
            for alpha in (0.3, 0.6, 1.0):
                blended = _blend_equal(base, alpha)
                candidate = _cap_and_fill(blended, cap, cash_symbol)
                cand_base = _strip_cash(candidate, cash_symbol)
                if (not hhi_target or compute_hhi(cand_base) <= hhi_target) and (
                    not n_target or compute_effective_n(cand_base) >= n_target
                ):
                    adjusted = candidate
                    notes.append("improve_diversification")
                    break
            else:
                adjusted = candidate
                notes.append("improve_diversification")

    return adjusted, notes


def _solve_lp(
    target_weights: Dict[str, float],
    current_weights: Dict[str, float],
    profile: Dict[str, Any],
    adv_by_symbol: Dict[str, float],
    aum: Optional[float],
) -> Optional[Dict[str, float]]:
    if cp is None:
        return None

    codes = list(dict.fromkeys(list(target_weights.keys()) + list(current_weights.keys())))
    n = len(codes)
    if n == 0:
        return None

    target_vec = [float(target_weights.get(c, 0.0)) for c in codes]
    current_vec = [float(current_weights.get(c, 0.0)) for c in codes]

    w = cp.Variable(n)
    t = cp.Variable(n)  # |w - target|
    u = cp.Variable(n)  # |w - current|

    constraints = [w >= 0, cp.sum(w) == 1]

    max_single = float(profile.get("max_single_weight", 1.0))
    if max_single > 0:
        constraints.append(w <= max_single)

    constraints += [t >= w - target_vec, t >= -(w - target_vec)]
    constraints += [u >= w - current_vec, u >= -(w - current_vec)]

    max_turnover = float(profile.get("max_turnover", 0.0))
    if max_turnover > 0:
        constraints.append(0.5 * cp.sum(u) <= max_turnover)

    max_delta = float(profile.get("max_position_delta", 0.0))
    if max_delta > 0:
        constraints.append(u <= max_delta)

    max_adv_ratio = float(profile.get("max_adv_ratio", 0.0))
    if max_adv_ratio > 0:
        for i, code in enumerate(codes):
            adv = float(adv_by_symbol.get(code, 0.0))
            if adv > 0 and aum:
                limit = max_adv_ratio * adv / float(aum)
            else:
                limit = max_adv_ratio
            constraints.append(u[i] <= limit)

    turnover_weight = float(os.getenv("LP_TURNOVER_WEIGHT", "0.1"))
    objective = cp.Minimize(cp.sum(t) + turnover_weight * cp.sum(u))
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=os.getenv("LP_SOLVER") or None)

    if w.value is None:
        return None

    raw = [max(0.0, float(v)) for v in w.value]
    total = sum(raw) or 1.0
    weights = {code: v / total for code, v in zip(codes, raw)}
    return weights


def constraint_solver(state: RiskState) -> Dict[str, Any]:
    decision = (state.get("decision") or {}).get("decision")
    if decision != "restrict":
        return {}

    normalized = state.get("normalized") or {}
    target_weights = {k: float(v) for k, v in (normalized.get("target_weights") or {}).items()}
    current_weights = {k: float(v) for k, v in (normalized.get("current_positions") or {}).items()}
    rules, _ = load_rules(normalized.get("policy_profile", "default"))
    max_holdings = normalized.get("target_holdings")
    if max_holdings is None:
        env_holdings = os.getenv("TARGET_HOLDINGS", "").strip()
        if env_holdings:
            try:
                max_holdings = int(env_holdings)
            except ValueError:
                max_holdings = None
    aum = normalized.get("aum")
    if aum is None:
        env_aum = os.getenv("PORTFOLIO_AUM") or os.getenv("AUM")
        if env_aum:
            try:
                aum = float(env_aum)
            except ValueError:
                aum = None

    report = state.get("risk_report") or {}
    findings = report.get("findings") or []
    drivers: List[str] = []
    for f in findings:
        try:
            sev = int(f.get("severity", 0))
        except (TypeError, ValueError):
            sev = 0
        if sev >= 2:
            label = f.get("risk_type") or f.get("agent")
            if label and label not in drivers:
                drivers.append(str(label))
    if not drivers:
        drivers = ["risk_report"]

    snapshot = state.get("snapshot_metrics") or {}
    adv_by_symbol = snapshot.get("adv_by_symbol") or {}

    cash_symbol = str(rules.get("cash_symbol") or os.getenv("CASH_SYMBOL", "CASH")).strip() or "CASH"
    adjusted_lp = _solve_lp(target_weights, current_weights, rules, adv_by_symbol, aum)
    if adjusted_lp and adjusted_lp != target_weights:
        adjusted_lp, limited = _limit_holdings(adjusted_lp, max_holdings, cash_symbol)
        rationale = "使用线性规划在约束下优化目标权重"
        if limited:
            rationale = f"{rationale}；按目标持仓数{max_holdings}收缩"
        return {
            "recommended_actions": [
                {
                    "action": "rebalance",
                    "rationale": rationale,
                    "drivers": drivers,
                    "target_weights": adjusted_lp,
                }
            ]
        }

    adjusted, notes = _adjust_weights(target_weights, rules, drivers)
    if adjusted and adjusted != target_weights:
        adjusted, limited = _limit_holdings(adjusted, max_holdings, cash_symbol)
        rationale_parts = []
        if "cap_max_single_weight" in notes:
            rationale_parts.append("单一仓位触顶，已按上限约束")
        if "improve_diversification" in notes:
            rationale_parts.append("向更分散的权重结构调整以降低集中度")
        if "CASH" in adjusted and "CASH" not in target_weights:
            rationale_parts.append("无法分配部分暂记为现金")
        rationale = "；".join(rationale_parts) or "调整权重以满足阈值要求"
        return {
            "recommended_actions": [
                {
                    "action": "rebalance",
                    "rationale": rationale,
                    "drivers": drivers,
                    "target_weights": adjusted,
                }
            ]
        }

    guidance = {
        "max_single_weight": float(rules.get("max_single_weight", 1.0)),
        "max_hhi": float(rules.get("max_hhi", 1.0)),
        "max_portfolio_volatility": float(rules.get("max_portfolio_volatility", 1.0)),
        "max_weighted_spread_bps": float(rules.get("max_weighted_spread_bps", 1.0e9)),
        "min_weighted_adv": float(rules.get("min_weighted_adv", 0.0)),
        "hhi_restrict": float(rules.get("hhi_restrict", 0.0)),
        "top_weight_restrict": float(rules.get("top_weight_restrict", 0.0)),
        "effective_n_restrict": float(rules.get("effective_n_restrict", 0.0)),
        "volatility_restrict": float(rules.get("volatility_restrict", 0.0)),
        "spread_restrict": float(rules.get("spread_restrict", 0.0)),
        "adv_restrict": float(rules.get("adv_restrict", 0.0)),
    }

    return {
        "recommended_actions": [
            {
                "action": "review_targets",
                "rationale": "风控结果为 restrict，建议调整权重以满足阈值要求。",
                "drivers": drivers,
                "guidance": guidance,
            }
        ]
    }
