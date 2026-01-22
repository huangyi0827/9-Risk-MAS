# 练习题：搭建一个最小可运行的风控 MAS

## 练习题说明
### 背景
你将基于给定的代码骨架，完成一个简化版风控 MAS（多智能体协作系统）流程：从输入校验、风险指标计算、路由选择，到汇总与决策输出。系统应能跑通主流程，并包含一个“Agent + Tool”的最小闭环。

### 目标
- 理解并搭建 MAS 的主流程编排
- 形成“硬规则优先 + 软报告兜底”的决策逻辑
- 体验工具调用型 Agent 的最小使用场景

### 你需要完成的模块
- 核心流程：`state.py` / `graph.py` / `router.py`
- 核心工具：`validate.py` / `snapshot.py` / `constraints.py` / `decision.py`
- 汇总模块：`reducer.py`
- Agent + Tool：`macro_agent.py` + `macro_search.py`

### 输入
上游输入包含：当前持仓、交易意图、组合上下文、AUM 等（由 `app.py` 或测试脚本提供）。

### 输出
返回统一结构的结果对象，至少包含：
- `risk_report`（findings + overall_severity）
- `decision`（rule_level + report_level + decision）
- `binding_constraints`（规则触发列表）

### 要求
- 保持函数签名与返回结构不变
- 关键逻辑需要由你实现（TODO 部分）
- 系统必须可运行，不允许报错
- Agent 必须调用工具并形成一个 finding

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

## 关键骨架模板（保持字段完整，返回默认值）

### 核心流程

`state.py`
定义显式 State 字段，约定每个模块的输入输出槽位。

```python
from typing import TypedDict, Dict, Any, List

class RiskState(TypedDict, total=False):
    intent: Dict[str, Any]
    context: Dict[str, Any]
    normalized: Dict[str, Any]
    data_quality: Dict[str, Any]
    snapshot_metrics: Dict[str, Any]
    candidate_nodes: List[str]
    nodes_to_run: List[str]
    findings: List[Dict[str, Any]]
    risk_report: Dict[str, Any]
    rule_findings: List[Dict[str, Any]]
    decision: Dict[str, Any]
    binding_constraints: List[Dict[str, Any]]
    audit: Dict[str, Any]


```

`graph.py`
编排主流程调用顺序，串起校验、质量、快照、路由、汇总与决策。

```python
from typing import Callable
from .state import RiskState
from .tools.validate import validate_and_normalize
from .tools.data_quality import check_data_quality
from .tools.snapshot import risk_snapshot_bundle
from .chains.router import router_chain
from .chains.reducer import reducer_chain
from .tools.constraints import constraints_evaluator
from .tools.decision import decision_engine

def build_graph() -> Callable[[RiskState], RiskState]:
    def _run(state: RiskState) -> RiskState:
        state.update(validate_and_normalize(state.get("intent", {}), state.get("context", {})))
        state.update(check_data_quality(state))
        state.update(risk_snapshot_bundle(state))
        state.update(router_chain(state))
        # 这里可调用 chain/agent（骨架版可直接跳过或给默认 finding）
        state.update(reducer_chain(state))
        state.update(constraints_evaluator(state))
        state.update(decision_engine(state))
        return state
    return _run


```

`router.py`
根据数据质量与策略，决定哪些分析节点要运行。

```python
from typing import Dict, Any
from ..state import RiskState

def router_chain(state: RiskState) -> Dict[str, Any]:
    # TODO: 基于 data_quality / policy_profile 选择候选节点
    candidate_nodes = ["market", "concentration", "diversification", "liquidity", "macro"]
    return {"candidate_nodes": candidate_nodes, "nodes_to_run": candidate_nodes}


```

### 核心工具

`validate.py`
解析并归一化输入，输出统一的目标权重与策略配置。

```python
from typing import Dict, Any

def validate_and_normalize(intent: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    # TODO: 归一化权重 / mode 处理
    return {"normalized": {"target_weights": {}, "current_weights": {}, "policy_profile": "default"}}


```

`snapshot.py`
计算风险快照指标（如 HHI、波动率、流动性、换手等）。

```python
from typing import Dict, Any
from ..state import RiskState

def risk_snapshot_bundle(state: RiskState) -> Dict[str, Any]:
    # TODO: 计算 HHI/波动率/流动性/换手等指标
    return {"snapshot_metrics": {"hhi": 0.0, "top_weight": 0.0}}


```

`constraints.py`
基于规则阈值生成硬规则触发项（rule_findings）。

```python
from typing import Dict, Any
from ..state import RiskState

def constraints_evaluator(state: RiskState) -> Dict[str, Any]:
    # TODO: 根据规则阈值生成 rule_findings
    return {"rule_findings": []}


```

### 汇总模块

`reducer.py`
汇总各节点 finding，生成统一的风险报告。

```python
from typing import Dict, Any
from ..state import RiskState

def reducer_chain(state: RiskState) -> Dict[str, Any]:
    findings = []
    report = {"overall_severity": 0, "summary": "占位", "findings": findings, "data_gaps": []}
    return {"findings": findings, "risk_report": report}


```

`decision.py`
根据规则优先与报告兜底输出最终决策。

```python
from typing import Dict, Any
from ..state import RiskState

def decision_engine(state: RiskState) -> Dict[str, Any]:
    # TODO: rule_level 优先 + report_level 兜底
    return {"decision": {"decision": "pass", "rule_level": 0, "report_level": 0}, "binding_constraints": []}


```

### Agent + Tool

`macro_search.py`（示例工具）
提供一个最小可用的宏观检索工具接口。

```python
from typing import Dict, Any, List

def macro_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    # TODO: 模拟检索或返回占位
    return []


```

`macro_agent.py`（示例 agent）
调用宏观工具并产出结构化的宏观风险 finding。

```python
from typing import Dict, Any
from ..state import RiskState
from ..tools.macro_search import macro_search

def run_macro_agent(state: RiskState) -> Dict[str, Any]:
    _ = macro_search("placeholder", limit=3)
    finding = {"agent": "MacroAgent", "risk_type": "macro", "severity": 0, "summary": "占位", "evidence": []}
    return {"finding_macro": finding}


```
