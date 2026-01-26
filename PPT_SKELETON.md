# Risk-MAS PPT 代码骨架合集（模块 1-10）

> 用途：PPT 展示用的“骨架代码”，只保留函数/类/参数/流程，细节留给学员补全。

---

## 1. 状态板块（state.py）

```python
from typing import TypedDict, Dict, List, Any, Optional

class Intent(TypedDict):
    date: str
    mode: str            # target | delta
    targets: Dict[str, float]

class Context(TypedDict, total=False):
    current_positions: Dict[str, float]
    current_positions_date: str
    universe: List[str]
    account_type: str
    jurisdiction: str
    policy_profile: str
    aum: float

class RiskState(TypedDict, total=False):
    intent: Intent
    context: Context
    normalized: Dict[str, Any]
    validation: Dict[str, Any]
    data_quality: Dict[str, Any]
    snapshot_metrics: Dict[str, Any]
    # ... 其他 slot 省略

def new_state(intent: Intent, context: Optional[Context] = None) -> RiskState:
    """初始化显式状态，绑定输入槽位。"""
    return {"intent": intent, "context": context or {}}
```

---

## 2. 输入规范化（validate.py）

```python
from typing import Dict, Any, Tuple
from ..state import RiskState
from ..tools.csv_data import previous_trading_date

def _sum_weights(weights: Dict[str, float]) -> float:
    return float(sum(weights.values())) if weights else 0.0

def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    # TODO: 归一化权重
    ...

def _coerce_weights(weights: Dict[str, Any], errors: list[str], label: str) -> Dict[str, float]:
    # TODO: 解析权重为 float
    ...

def _validate_date(date_str: str) -> Tuple[bool, str]:
    # TODO: 日期格式校验
    ...

def validate_and_normalize(state: RiskState) -> Dict[str, Any]:
    """
    目标：校验 intent/context、生成 asof_date、合并权重、生成 universe
    """
    intent = state.get("intent") or {}
    context = state.get("context") or {}

    # TODO: 校验 date/mode
    # TODO: 解析 targets/current_positions
    # TODO: 生成 target_weights（delta 合并或 target 归一）
    # TODO: 生成 universe
    # TODO: asof_date = previous_trading_date(intent.date)

    return {
        "normalized": {
            "asof_date": "...",
            "mode": "...",
            "targets": {},
            "current_positions": {},
            "current_positions_date": None,
            "target_weights": {},
            "universe": [],
            "policy_profile": "default",
            "aum": None,
        },
        "validation": {
            "is_valid": True,
            "errors": [],
            "warnings": [],
        },
    }
```

---

## 3. 数据与指标（csv_data.py / data_quality.py / snapshot.py）

```python
# csv_data.py
import pandas as pd
from typing import Dict, Iterable, List, Any, Tuple

def load_etf_prices() -> pd.DataFrame:
    """读取 ETF 日频价格数据 CSV。"""
    # TODO: 读取并做基础清洗
    ...

def load_etf_basic() -> pd.DataFrame:
    """读取 ETF 基础信息 CSV。"""
    ...

def load_macro_docs() -> pd.DataFrame:
    """读取宏观文本/情绪结果数据。"""
    ...

def load_compliance_docs() -> pd.DataFrame:
    """读取合规公告/规则文本。"""
    ...

def security_master_codes() -> Tuple[set, str]:
    """ETF 主数据可用代码集合。"""
    ...

def previous_trading_date(asof_date: str) -> str:
    """根据价格数据回溯到上一个交易日。"""
    ...

def lookback_start_date(asof_date: str, lookback_days: int) -> str:
    """根据 asof_date + lookback_days 计算窗口起点。"""
    ...

def market_metrics(
    codes: Iterable[str],
    start_date: str | None,
    end_date: str | None,
) -> Dict[str, Dict[str, float]]:
    """
    目标：计算 volatility / adv / spread_bps
    """
    # TODO: 过滤 dates + codes
    # TODO: 计算收益率、波动率、成交额均值、价差
    # TODO: 返回 {code: {volatility, adv, spread_bps}}
    ...

def macro_search_hits(query: str, limit: int = 5, asof_date: str | None = None) -> List[Dict[str, Any]]:
    """宏观文本检索，返回结构化命中。"""
    ...

def compliance_search_hits(query: str, limit: int = 5) -> List[str]:
    """合规文本检索，返回片段。"""
    ...

def macro_latest_date(asof_date: str | None = None) -> str:
    """宏观文本最新日期（用于新鲜度）。"""
    ...
```

```python
# data_quality.py
from typing import Dict, Any, List
from ..state import RiskState
from .csv_data import (
    security_master_codes,
    market_metrics,
    macro_docs_available,
    compliance_docs_available,
    macro_latest_date,
    lookback_start_date,
)

def check_data_quality(state: RiskState) -> Dict[str, Any]:
    """
    目标：缺失/新鲜度口径统一，输出 data_quality + data_gaps
    """
    # TODO: 检查 ETF master / market data 缺失
    # TODO: 计算宏观文本新鲜度与未来数据
    # TODO: 标记 macro/compliance 可用性
    return {
        "data_quality": {},
        "data_gaps": [],
    }
```

```python
# snapshot.py
from typing import Dict, Any
from ..state import RiskState
from .csv_data import market_metrics, lookback_start_date

def risk_snapshot_bundle(state: RiskState) -> Dict[str, Any]:
    """
    目标：输出 vol/HHI/ADV/spread + 当前/目标差分指标
    """
    # TODO: 权重归一化
    # TODO: HHI / effective_n / top_weight
    # TODO: turnover / max_position_delta / delta_hhi / delta_vol
    # TODO: 用 market_metrics 计算 vol/adv/spread_bps
    return {"snapshot_metrics": {}}
```

---

## 4. 编排与汇总（graph.py / gatekeeper.py / supervisor.py / reducer.py）

```python
# graph.py
from langgraph.graph import StateGraph
from .state import RiskState

def build_graph():
    """
    组装主流程：validate → data_quality → snapshot → gatekeeper
             → supervisor → 分析节点 → reducer → decision
    """
    graph = StateGraph(RiskState)
    # TODO: 注册各节点 + 条件路由
    return graph.compile()
```

```python
# gatekeeper.py
from typing import Dict, Any
from ..state import RiskState

def gatekeeper_chain(state: RiskState) -> Dict[str, Any]:
    """候选裁剪：基于 data_quality 过滤不可用节点。"""
    # TODO: 读取 data_quality/missing
    return {"candidate_nodes": [], "gatekeeper_used": True, "gatekeeper_rationale": "ok"}
```

```python
# supervisor.py
from typing import Dict, Any
from ..state import RiskState

def supervisor_chain(state: RiskState, llm) -> Dict[str, Any]:
    """LLM 调度：解释保留/剔除节点，并输出调度理由。"""
    # TODO: 生成 supervisor_rationale
    return {"supervisor_used": True, "supervisor_rationale": "...", "supervisor_model": "..."}
```

```python
# reducer.py
from typing import Dict, Any
from ..state import RiskState

def reducer_chain(state: RiskState) -> Dict[str, Any]:
    """汇总 findings + evidence 清洗 + data_gaps。"""
    # TODO: 聚合 finding_* → risk_report
    return {"findings": [], "risk_report": {}}
```

---

## 5. 分析链路（market.py / concentration.py / diversification.py / liquidity.py）

```python
# market.py
from typing import Dict, Any
from ..state import RiskState

def market_chain(state: RiskState) -> Dict[str, Any]:
    """市场风险链：波动率阈值。"""
    # TODO: severity + evidence
    return {"finding_market": {"agent": "MarketRiskChain", "risk_type": "market"}}
```

```python
# concentration.py
from typing import Dict, Any
from ..state import RiskState

def concentration_chain(state: RiskState) -> Dict[str, Any]:
    """集中度链：HHI / top_weight。"""
    # TODO: severity + evidence
    return {"finding_concentration": {"agent": "ConcentrationChain", "risk_type": "concentration"}}
```

```python
# diversification.py
from typing import Dict, Any
from ..state import RiskState

def diversification_chain(state: RiskState) -> Dict[str, Any]:
    """分散度链：effective_n。"""
    # TODO: severity + evidence
    return {"finding_diversification": {"agent": "DiversificationChain", "risk_type": "diversification"}}
```

```python
# liquidity.py
from typing import Dict, Any
from ..state import RiskState

def liquidity_chain(state: RiskState) -> Dict[str, Any]:
    """流动性链：spread_bps / ADV。"""
    # TODO: severity + evidence
    return {"finding_liquidity": {"agent": "LiquidityChain", "risk_type": "liquidity"}}
```

---

## 6. Agent 与工具（macro_agent.py / compliance_agent.py / agent_utils.py / prompts.py）

```python
# agent_utils.py
from typing import Any, Dict, List, Sequence, Callable
from langchain_core.tools import tool

def wrap_tool(name: str, fn: Callable[..., Dict[str, Any]]):
    """统一封装工具：记录耗时/错误。"""
    @tool(name)
    def _wrapped(*args, **kwargs) -> Dict[str, Any]:
        # TODO: 计时 + 捕获异常
        return {}
    return _wrapped
```

```python
# macro_agent.py
from typing import Dict, Any

def macro_timeseries(series: str) -> Dict[str, Any]:
    """宏观时序工具。"""
    ...

def macro_search(query: str) -> Dict[str, Any]:
    """宏观文本/情绪检索。"""
    ...

def run_macro_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """先时序，后文本；输出 finding_macro。"""
    return {"finding_macro": {"agent": "MacroToolCallingAgent", "risk_type": "macro"}}
```

```python
# compliance_agent.py
from typing import Dict, Any

def compliance_search(query: str) -> Dict[str, Any]:
    """合规检索/RAG（占位）。"""
    ...

def run_compliance_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """输出 finding_compliance + blocklist。"""
    return {"finding_compliance": {"agent": "ComplianceToolCallingAgent", "risk_type": "compliance"}}
```

---

## 7. 阈值板块（calibrate_rules.py / calibrate_macro_series.py）

```python
# calibrate_rules.py
from typing import Dict, Any

def calibrate_rules(asof_date: str, n: int) -> Dict[str, Any]:
    """生成组合规则阈值（rules.yaml）。"""
    # TODO: 随机采样组合 → 指标分布 → 分位数阈值
    return {}
```

```python
# calibrate_macro_series.py
from typing import Dict, Any

def calibrate_macro_series(asof_date: str, config_path: str) -> Dict[str, Any]:
    """生成宏观时序阈值（macro_series.yaml）。"""
    # TODO: 拉取时序 → 变化分布 → 分位数阈值
    return {}
```

---

## 8. 规则与决策（decision.py / solver.py）

```python
# decision.py
from typing import Dict, Any, List

def decision_engine(state: Dict[str, Any]) -> Dict[str, Any]:
    """rule_level 优先，report_level 兜底。"""
    # TODO: 计算决策级别
    return {"decision": {"decision": "pass", "rule_level": 0, "report_level": 0}}

def evaluate_constraints(metrics: Dict[str, Any], rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    """硬规则评估 -> rule_findings"""
    return []
```

```python
# solver.py
from typing import Dict, Any

def constraint_solver(state: Dict[str, Any]) -> Dict[str, Any]:
    """restrict 时输出建议调仓。"""
    return {"recommended_actions": []}
```

---

## 9. Skills 板块（SKILL.md / output.schema.json / tool_interfaces.yaml / skills_runtime.py）

```text
skills/
├── <skill-name>/
│   ├── SKILL.md
│   ├── output.schema.json
│   └── examples.json
├── snippets/
│   ├── evidence_rules.md
│   └── decision_rubric.md
└── tools/
    └── tool_interfaces.yaml
```

```python
# skills_runtime.py
def load_skill(skill_name: str) -> Dict[str, Any]:
    # TODO: 读取 SKILL + Schema + examples
    return {}

def build_prompt(skill: Dict[str, Any], snippets: Dict[str, str]) -> str:
    # TODO: 拼装 prompt
    return ""

def validate_output(schema: Dict[str, Any], output: Dict[str, Any]) -> bool:
    # TODO: Schema 校验
    return True
```

---

## 10. 审计与可追溯（audit.py）

```python
# audit.py
from typing import Dict, Any
from datetime import datetime

def _hash_payload(payload: Dict[str, Any]) -> str:
    # TODO: 稳定序列化 + 哈希
    return "..."

def audit_log(state: Dict[str, Any]) -> Dict[str, Any]:
    """技能版本/工具调用/hash/trace_id 输出闭环。"""
    return {
        "audit": {
            "ruleset_version": "...",
            "skills_used": [],
            "tool_calls": [],
            "tool_call_summary": {"count": 0, "errors": 0, "total_latency_ms": 0},
            "data_snapshot_hash": "...",
            "rules_snapshot_hash": "...",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "trace_id": "...",
        }
    }
```
