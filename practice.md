# 练习题：搭建一个最小可运行的风控 MAS

## 练习题说明
### 背景
你将基于给定的代码骨架，完成一个简化版风控 MAS（多智能体协作系统）流程：从输入校验、风险指标计算、路由选择，到汇总与决策输出。系统应能跑通主流程，并包含一个"Agent + Tool"的最小闭环。

### 目标
- 理解并搭建 MAS 的主流程编排
- 形成"硬规则优先 + 软报告兜底"的决策逻辑
- 体验工具调用型 Agent 的最小使用场景
- 理解 LangGraph 并行执行机制

### 你需要完成的模块

| 模块 | 需要完成的文件 |
| --- | --- |
| 状态板块 | `src/state.py` |
| 输入规范化 | `src/tools/validate.py` |
| 数据与指标 | `src/tools/utils.py` / `src/tools/csv_data.py` / `src/tools/data_quality.py` / `src/tools/snapshot.py` |
| 编排与汇总 | `src/graph.py` / `src/chains/gatekeeper.py` / `src/chains/supervisor.py` / `src/chains/reducer.py` |
| 分析链路 | `src/chains/market.py` / `src/chains/concentration.py` / `src/chains/diversification.py` / `src/chains/liquidity.py` |
| Agent + Tool（必做） | `src/agents/macro_agent.py` / `src/agents/agent_utils.py` / `src/agents/prompts.py` |
| 阈值板块 | `src/tools/calibrate_rules.py` / `src/tools/calibrate_macro_series.py` |
| 规则与决策 | `src/tools/decision.py` / `src/tools/solver.py` |
| Skills | `skills/macro-tool-calling/SKILL.md` / `skills/macro-tool-calling/output.schema.json` / `skills/snippets/*` / `skills/tools/tool_interfaces.yaml` / `src/skills_runtime.py` |
| 审计与可追溯 | `src/tools/audit.py` |

### 输入
上游输入包含：当前持仓、交易意图、组合上下文、AUM 等（由 `app.py` 或测试脚本提供）。

### 输出
返回统一结构的结果对象，至少包含：
- `risk_report`（findings + overall_severity）
- `decision`（rule_level + report_level + decision）
- `binding_constraints`（规则触发列表）
- `audit`（trace_id / tool_calls / ruleset_version）

### 要求
- 保持函数签名与返回结构不变
- 关键逻辑需要由你实现（TODO 部分）
- 系统必须可运行，不允许报错
- 必须包含一个 Agent + 一个工具调用，并形成一个 finding

### 评分要点
- 流程编排完整且清晰（25%）
- 规则评估与决策逻辑正确（25%）
- 风险指标计算合理（20%）
- 汇总输出结构正确（15%）
- Agent + Tool 闭环可运行（15%）

### 加分项
- 支持更多规则或指标
- 为 findings 添加证据引用
- 输出更可读（表格/摘要）

## Risk-MAS骨架模板（模块 1-10）

为避免限制用户实现方式，本练习不在此处给出细化步骤。请参考以下模板文件：

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
from ..tools.utils import normalize_weights

def _sum_weights(weights: Dict[str, float]) -> float:
    return float(sum(weights.values())) if weights else 0.0

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
    # TODO: 生成 target_weights（delta 合并或 target 归一，使用 normalize_weights）
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

## 3. 数据与指标（config.py / csv_data.py / data_quality.py / snapshot.py / utils.py）

```python
# src/config.py
import os

class Config:
    """集中管理配置项，避免环境变量分散读取。"""

    # 市场数据

    # 宏观数据
   
    # 组合约束
   
    # LLM 配置
   
```

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
from ..config import Config
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
    # 使用 Config 获取配置
    lookback = Config.MARKET_LOOKBACK_DAYS
    stale_days = Config.MACRO_STALE_DAYS

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
from .utils import normalize_weights, compute_hhi, compute_effective_n

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

```python
# src/tools/utils.py
from typing import Dict

WEIGHT_TOLERANCE = 1e-6
EPSILON = 1e-12

def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """归一化权重，使其总和为 1。"""

def compute_hhi(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """计算 Herfindahl-Hirschman Index（集中度指标）。"""
   
def compute_effective_n(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """计算有效标的数（1/HHI）。"""
  
```

---

## 4. 编排与汇总（graph.py / gatekeeper.py / supervisor.py / reducer.py）

```python
# graph.py
from langgraph.graph import StateGraph
from langgraph.constants import Send
from typing import List
from .state import RiskState

def _guarded_node(name: str, fn):
    """
    包装节点函数，支持条件执行。
    重要：不执行时返回显式的 finding_{name}=None，避免状态丢失。
    """
  
def dispatch_to_parallel(state: RiskState) -> List[Send]:
    """
    使用 LangGraph Send API 实现真正的并行执行。
    将所有待执行节点同时发送，而非串行循环。
    """


def build_graph():
    """
    组装主流程（v2.0 并行架构）：
    validate → data_quality → snapshot → gatekeeper → supervisor
            → 并行分析节点 → reducer → decision
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
    """
    LLM 调度：从 candidate_nodes 生成 pending_agents，并输出调度理由。
    注意：v2.0 移除了 router，supervisor 直接接收 candidate_nodes。
    """
    candidate = state.get("candidate_nodes") or []

    # TODO: LLM 决策保留/剔除节点
    # TODO: 生成 supervisor_rationale

    return {
        "pending_agents": candidate,  # 待执行的节点列表
        "supervisor_used": True,
        "supervisor_rationale": "...",
        "supervisor_model": "...",
    }
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
from .agent_utils import wrap_tool

def _macro_timeseries_impl(series: str, asof_date: str) -> Dict[str, Any]:
    """宏观时序工具实现（接收 asof_date 参数）。"""
    ...

def _macro_search_impl(query: str, asof_date: str) -> Dict[str, Any]:
    """宏观文本/情绪检索实现（接收 asof_date 参数）。"""
    ...

def _create_tools_with_asof_date(asof_date: str):
    """
    创建绑定特定 asof_date 的工具实例。
    使用闭包而非全局变量，确保线程安全。
    """
    def timeseries_impl(series: str) -> Dict[str, Any]:
        return _macro_timeseries_impl(series, asof_date)

    def search_impl(query: str) -> Dict[str, Any]:
        return _macro_search_impl(query, asof_date)

    return (
        wrap_tool("macro_timeseries", timeseries_impl),
        wrap_tool("macro_search", search_impl),
    )

def run_macro_agent(state: Dict[str, Any], llm) -> Dict[str, Any]:
    """
    执行宏观分析 Agent。
    注意：通过闭包传入 asof_date，避免全局变量的线程安全问题。
    """
    # TODO: 调用 LLM with tools
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

```python
# prompts.py
"""风险评估智能体系统提示语。
每项提示语均包含：
- 角色与职责说明
- 输入数据解读
- 工具使用指南
- 带示例的输出格式规范
- 证据要求
"""
MACRO_SYSTEM_PROMPT = ""

COMPLIANCE_SYSTEM_PROMPT =""
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
from .utils import normalize_weights, compute_hhi

def constraint_solver(state: Dict[str, Any]) -> Dict[str, Any]:
    """restrict 时输出建议调仓。"""
    # 使用共享的工具函数
    # normalized = normalize_weights(weights)
    # hhi = compute_hhi(normalized, already_normalized=True)
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
