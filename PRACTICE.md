# 风控 MAS 实践练习

<details>
<summary><b>📝 文件完成清单（点击展开）</b></summary>

### 模块1: 状态定义 (0/1)
- [ ] src/state.py

### 模块2: 输入规范化 (0/1)
- [ ] src/tools/validate.py

### 模块3: 数据与指标 (0/4)
- [ ] src/tools/utils.py
- [ ] src/tools/csv_data.py
- [ ] src/tools/data_quality.py
- [ ] src/tools/snapshot.py

### 模块4: 编排调度 (0/3)
- [ ] src/graph.py
- [ ] src/chains/gatekeeper.py
- [ ] src/chains/supervisor.py

### 模块5: 分析链路 (0/5)
- [ ] src/chains/common.py
- [ ] src/chains/market.py
- [ ] src/chains/concentration.py
- [ ] src/chains/diversification.py
- [ ] src/chains/liquidity.py

### 模块6: Agent 模块 (0/3)
- [ ] src/agents/agent_utils.py
- [ ] src/agents/macro_agent.py
- [ ] src/agents/compliance_agent.py

### 模块7: Skills 体系 (0/1)
- [ ] src/skills_runtime.py

### 模块8: 规则与约束 (0/2)
- [ ] src/tools/rules.py
- [ ] src/tools/constraints.py

### 模块9: 决策与审计 (0/4)
- [ ] src/chains/reducer.py
- [ ] src/tools/decision.py
- [ ] src/tools/solver.py
- [ ] src/tools/audit.py

### 模块10: 阈值校准 (0/2)
- [ ] src/tools/calibrate_rules.py
- [ ] src/tools/calibrate_macro_series.py
</details>

---

## 📋 练习说明

本练习要求你从零开始构建一个基于多智能体系统（MAS）的 ETF 投资组合风控框架。

**适用对象：**
- 在校学生（金融工程、计算机相关专业）
- 金融业务条线技术人员


**前置知识：**
- Python 基础
- 基本的金融概念（ETF、投资组合、风险指标）
- LangChain/LangGraph 基础（建议先完成官方教程）
- 第二练RAG、第四练NLP

---

## ⚙️ 配置方式

- 项目运行时配置统一由 `src/config.py` 读取环境变量并注入模块。
- 不配置也可运行（使用默认值）；需要启用 LLM / Tushare / RAG 时再在 `.env` 中补充对应变量。

## 🎯 练习目标

构建一个完整的风控 MAS 系统，能够：

1. ✅ 接收交易意图（Intent）和组合上下文（Context）
2. ✅ 执行多维度风险分析（市场、集中度、分散度、流动性、宏观、合规）
3. ✅ 基于规则和 LLM 分析给出风控决策（pass/warn/restrict/block）
4. ✅ 在 restrict 情况下生成调仓建议
5. ✅ 输出完整的审计日志

---

## 📦 模块划分

你需要实现以下 10 个模块：

| 模块 | 文件数 | 难度 |
|:---|:---:|:---:|
| 模块1: 状态定义 | 1 | ⭐ |
| 模块2: 输入规范化 | 1 | ⭐⭐ |
| 模块3: 数据与指标 | 4 | ⭐⭐⭐ |
| 模块4: 编排调度 | 3 | ⭐⭐⭐⭐ |
| 模块5: 分析链路 | 5 | ⭐⭐⭐ |
| 模块6: Agent 模块 | 3 | ⭐⭐⭐⭐ |
| 模块7: Skills 体系 | 1 | ⭐⭐ |
| 模块8: 规则与约束 | 2 | ⭐⭐⭐ |
| 模块9: 决策与审计 | 4 | ⭐⭐⭐ |
| 模块10: 阈值校准 | 2 | ⭐⭐⭐ |
---

## 📝 模块1: 状态定义

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐ 入门 |
| **文件数** | 1个 |
| **文件路径** | `src/state.py` |
| **依赖模块** | 无 |
| **被依赖** | 所有其他模块 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] TypedDict 的使用方法
- [ ] 如何设计工作流状态结构
- [ ] NotRequired 类型标注的应用
- [ ] 状态字段的分组设计原则

</details>

<details>
<summary><b>📖 功能说明</b></summary>

定义整个工作流的状态结构（RiskState），使用 TypedDict 确保类型安全。

**核心概念：**
- **显式状态管理**：所有节点共享同一个状态对象
- **类型安全**：使用 TypedDict 提供类型提示
- **字段分组**：按功能将字段分为输入、预处理、分析、决策四大类

**为什么重要：**
状态定义是整个系统的基础，所有节点都依赖这个状态结构进行数据传递。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

定义 `Intent`、`Context`、`Finding` 三个子 TypedDict 和主状态 `RiskState`，以及工厂函数 `new_state()`。

**1. 子类型定义**

`Intent` TypedDict（必填字段）：
- `date`: 交易日期（str）
- `mode`: 模式 target 或 delta（str）
- `targets`: 目标权重映射（Dict[str, float]）

`Context` TypedDict（`total=False`，全部可选）：
- `current_positions`: 当前持仓权重（Dict[str, float]）
- `current_positions_date`: 持仓日期（str）
- `universe`: ETF 代码列表（List[str]）
- `trade_calendar`: 交易日历标识（str）
- `account_type`: 账户类型（str）
- `jurisdiction`: 司法管辖区（str）
- `policy_profile`: 规则配置名（str）
- `aum`: 资产管理规模（float）

`Finding` TypedDict（`total=False`，全部可选）：
- `agent`: 产生该结果的 Agent 名称（str）
- `risk_type`: 风险类型（str）
- `severity`: 风险等级 0-3（int）
- `summary`: 一句话总结（str）
- `evidence`: 证据列表（List[Dict[str, Any]]）
- `metrics`: 指标字典（Dict[str, Any]）
- `recommendations`: 建议列表（List[str]）
- `policy_ids`: 关联的政策 ID（List[str]）

**2. RiskState 字段分组**

`RiskState` TypedDict（`total=False`），按以下分组定义字段：

*输入字段*
- `intent`: 交易意图（Intent）
- `context`: 组合上下文（Context）

*预处理字段*
- `normalized`: 归一化后的数据（Dict[str, Any]）
- `validation`: 验证结果（Dict[str, Any]）

*确定性工具字段*
- `data_quality`: 数据质量检查结果（Dict[str, Any]）
- `data_gaps`: 数据缺口列表（List[Dict[str, Any]]）
- `snapshot_metrics`: 指标快照（Dict[str, Any]）
- `rule_findings`: 规则检查结果列表（List[Dict[str, Any]]）
- `compliance_blocklist`: 硬禁投清单（List[str]）
- `compliance_blocklist_soft`: 软禁投清单（List[str]）
- `compliance_blocklist_meta`: 禁投清单元数据（Dict[str, Any]）

*路由字段*
- `candidate_nodes`: 候选节点列表（List[str]）
- `nodes_to_run`: 实际运行节点列表（List[str]）
- `pending_agents`: 待执行 Agent 列表（List[str]）
- `next_agent`: 下一个 Agent（str）
- `stop_condition`: 是否终止（bool）
- `cost_budget`: 成本预算（Dict[str, Any]）
- `gatekeeper_used`: 是否使用了 Gatekeeper（bool）
- `gatekeeper_rationale`: Gatekeeper 决策理由（str）
- `supervisor_used`: 是否使用了 Supervisor（bool）
- `supervisor_rationale`: Supervisor 决策理由（str）
- `supervisor_model`: Supervisor 使用的模型（str）

*并行分析字段*
- `finding_market`: 市场风险分析结果（Finding）
- `finding_concentration`: 集中度风险分析结果（Finding）
- `finding_diversification`: 分散度风险分析结果（Finding）
- `finding_liquidity`: 流动性风险分析结果（Finding）
- `finding_macro`: 宏观风险分析结果（Finding）
- `finding_compliance`: 合规风险分析结果（Finding）
- `tool_calls_macro`: 宏观 Agent 工具调用记录（List[Dict[str, Any]]）
- `tool_calls_compliance`: 合规 Agent 工具调用记录（List[Dict[str, Any]]）
- `llm_used_macro`: 宏观分析是否使用了 LLM（bool）
- `llm_used_compliance`: 合规分析是否使用了 LLM（bool）
- `llm_model_macro`: 宏观分析使用的模型名（str）
- `llm_model_compliance`: 合规分析使用的模型名（str）

*汇总字段*
- `findings`: 所有分析结果列表（List[Finding]）
- `risk_report`: 风险报告（Dict[str, Any]）

*决策字段*
- `decision`: 决策结果（Dict[str, Any]）
- `binding_constraints`: 约束条件列表（List[Dict[str, Any]]）
- `recommended_actions`: 调仓建议列表（List[Dict[str, Any]]）

*审计字段*
- `audit`: 审计日志（Dict[str, Any]）

**3. 工厂函数**
- `new_state(intent, context=None) -> RiskState`: 创建初始状态，只填入 intent 和 context

</details>

<details>
<summary><b>💻 代码模板</b></summary>

```python
"""
风控 MAS 状态定义模块
定义整个工作流的状态结构
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class Intent(TypedDict):
    """交易意图"""
    # TODO: 定义 date 字段（交易日期，str）
    # TODO: 定义 mode 字段（模式: target | delta，str）
    # TODO: 定义 targets 字段（目标权重，Dict[str, float]）
    pass


class Context(TypedDict, total=False):
    """组合上下文（全部可选）"""
    # TODO: 定义 current_positions 字段（当前持仓权重，Dict[str, float]）
    # TODO: 定义 current_positions_date 字段（持仓日期，str）
    # TODO: 定义 universe 字段（ETF 代码列表，List[str]）
    # TODO: 定义 trade_calendar 字段（交易日历标识，str）
    # TODO: 定义 account_type 字段（账户类型，str）
    # TODO: 定义 jurisdiction 字段（司法管辖区，str）
    # TODO: 定义 policy_profile 字段（规则配置名，str）
    # TODO: 定义 aum 字段（资产管理规模，float）
    pass


class Finding(TypedDict, total=False):
    """单个分析维度的结果"""
    # TODO: 定义 agent 字段（产生该结果的 Agent 名称，str）
    # TODO: 定义 risk_type 字段（风险类型，str）
    # TODO: 定义 severity 字段（风险等级 0-3，int）
    # TODO: 定义 summary 字段（一句话总结，str）
    # TODO: 定义 evidence 字段（证据列表，List[Dict[str, Any]]）
    # TODO: 定义 metrics 字段（指标字典，Dict[str, Any]）
    # TODO: 定义 recommendations 字段（建议列表，List[str]）
    # TODO: 定义 policy_ids 字段（关联的政策 ID，List[str]）
    pass


class RiskState(TypedDict, total=False):
    """
    风控工作流的状态结构

    使用 total=False 表示所有字段都是可选的
    """

    # ========== 输入字段 ==========
    # TODO: 定义 intent 字段（Intent 类型）
    # TODO: 定义 context 字段（Context 类型）

    # ========== 预处理字段 ==========
    # TODO: 定义 normalized 字段（Dict[str, Any]）
    # TODO: 定义 validation 字段（Dict[str, Any]）

    # ========== 确定性工具字段 ==========
    # TODO: 定义 data_quality 字段（Dict[str, Any]）
    # TODO: 定义 data_gaps 字段（List[Dict[str, Any]]）
    # TODO: 定义 snapshot_metrics 字段（Dict[str, Any]）
    # TODO: 定义 rule_findings 字段（List[Dict[str, Any]]）
    # TODO: 定义 compliance_blocklist 字段（List[str]）
    # TODO: 定义 compliance_blocklist_soft 字段（List[str]）
    # TODO: 定义 compliance_blocklist_meta 字段（Dict[str, Any]）

    # ========== 路由字段 ==========
    # TODO: 定义 candidate_nodes 字段（List[str]）
    # TODO: 定义 nodes_to_run 字段（List[str]）
    # TODO: 定义 pending_agents 字段（List[str]）
    # TODO: 定义 next_agent 字段（str）
    # TODO: 定义 stop_condition 字段（bool）
    # TODO: 定义 cost_budget 字段（Dict[str, Any]）
    # TODO: 定义 gatekeeper_used 字段（bool）
    # TODO: 定义 gatekeeper_rationale 字段（str）
    # TODO: 定义 supervisor_used 字段（bool）
    # TODO: 定义 supervisor_rationale 字段（str）
    # TODO: 定义 supervisor_model 字段（str）

    # ========== 并行分析字段 ==========
    # TODO: 定义 finding_market 字段（Finding 类型）

    # TODO: 定义 finding_concentration 字段（Finding 类型）
    # TODO: 定义 finding_diversification 字段（Finding 类型）
    # TODO: 定义 finding_liquidity 字段（Finding 类型）
    # TODO: 定义 finding_macro 字段（Finding 类型）
    # TODO: 定义 finding_compliance 字段（Finding 类型）
    # TODO: 定义 tool_calls_macro 字段（List[Dict[str, Any]]）
    # TODO: 定义 tool_calls_compliance 字段（List[Dict[str, Any]]）
    # TODO: 定义 llm_used_macro 字段（bool）
    # TODO: 定义 llm_used_compliance 字段（bool）
    # TODO: 定义 llm_model_macro 字段（str）
    # TODO: 定义 llm_model_compliance 字段（str）

    # ========== 汇总字段 ==========
    # TODO: 定义 findings 字段（List[Finding]）
    # TODO: 定义 risk_report 字段（Dict[str, Any]）

    # ========== 决策字段 ==========
    # TODO: 定义 decision 字段（Dict[str, Any]）
    # TODO: 定义 binding_constraints 字段（List[Dict[str, Any]]）
    # TODO: 定义 recommended_actions 字段（List[Dict[str, Any]]）

    # ========== 审计字段 ==========
    # TODO: 定义 audit 字段（Dict[str, Any]）
    pass


def new_state(intent: Intent, context: Optional[Context] = None) -> RiskState:
    """创建初始状态，只填入 intent 和 context"""
    # TODO: 返回一个只包含 intent 和 context 的 RiskState
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

完成后请检查：
- [ ] `Intent`、`Context`、`Finding` 三个子 TypedDict 已定义
- [ ] `RiskState` 使用 `total=False`，所有字段可选
- [ ] `Finding` 类型用于 `finding_*` 字段（而非 `dict`）
- [ ] `new_state()` 工厂函数已实现
- [ ] 可以成功导入所有类型

**测试命令：**
```bash
# 测试导入
uv run --env-file .env -- python -u -c "
from src.state import RiskState, Intent, Context, Finding, new_state
s = new_state({'date': '2025-01-06', 'mode': 'target', 'targets': {'510300': 0.5}})
assert 'intent' in s
print('✅ 状态定义正确')
"
```

**预期输出：**
```
✅ 状态定义正确
```

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. 使用 `NotRequired` 而不是 `Optional`
   - `NotRequired` 表示字段可以不存在
   - `Optional` 表示字段值可以是 None

2. 字段命名规范
   - 分析结果字段统一使用 `finding_` 前缀
   - 保持与后续模块的命名一致

3. 类型标注
   - 使用 `dict[str, Any]` 而不是 `dict`
   - 使用 `list[dict[str, Any]]` 而不是 `list`

**常见错误：**
- ❌ 忘记导入 `NotRequired`
- ❌ 使用 `Optional` 代替 `NotRequired`
- ❌ 字段名拼写错误

**参考资源：**
- [TypedDict 官方文档](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- [NotRequired 说明](https://peps.python.org/pep-0655/)

</details>

---

## 📝 模块2: 输入规范化

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐ 进阶 |
| **文件数** | 1个 |
| **文件路径** | `src/tools/validate.py` |
| **依赖模块** | 模块1 |
| **被依赖** | 模块3, 4 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 输入验证的最佳实践
- [ ] 数据归一化技术
- [ ] 错误处理和警告机制
- [ ] 状态更新模式

</details>

<details>
<summary><b>📖 功能说明</b></summary>

验证和规范化用户输入，确保数据格式正确。

**核心功能：**
1. **输入验证**：检查必填字段和数据格式
2. **权重归一化**：确保权重和为1
3. **模式转换**：处理 delta 模式到 target 模式的转换
4. **错误收集**：记录所有验证问题

**为什么重要：**
输入验证是系统的第一道防线，确保后续节点接收到的数据是合法的。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

实现 `validate_and_normalize(state, config) -> Dict[str, Any]` 函数及 4 个辅助函数：

**1. 辅助函数**
- `_sum_weights(weights)`: 计算权重之和
- `_normalize_weights(weights)`: 归一化权重使其和为 1
- `_coerce_weights(weights, errors, label)`: 将权重值强制转为 float，无法转换的记录错误
- `_validate_date(date_str)`: 校验日期格式 `YYYY-MM-DD`，返回 `(bool, str)`

**2. 主函数 `validate_and_normalize`**
- 验证 `intent.date`（必填，YYYY-MM-DD 格式）
- 验证 `intent.mode`（必填，target 或 delta）
- 用 `_coerce_weights` 转换 `intent.targets` 和 `context.current_positions`
- 处理 `mode=delta`：将 delta 叠加到 current_positions 后归一化
- 处理 `mode=target`：权重和不为 1 时自动归一化并记录 warning
- 调用 `previous_trading_date(date_str, cfg)` 获取 `asof_date`（来自 csv_data 模块）
- 构建 `universe` 列表（合并 context.universe + current_positions.keys + target_weights.keys，去重）

**3. 返回值**（Dict，不是 RiskState）
```python
{
    "normalized": {
        "asof_date": str,        # 上一个交易日
        "mode": str,
        "targets": dict,         # 原始目标
        "current_positions": dict,
        "current_positions_date": str,
        "target_weights": dict,  # 归一化后的目标权重
        "universe": list,        # ETF 代码列表
        "account_type": str,
        "jurisdiction": str,
        "policy_profile": str,   # 默认 "default"
        "aum": float,
    },
    "validation": {
        "is_valid": bool,
        "errors": list,
        "warnings": list,
    },
}
```

</details>

<details>
<summary><b>💻 代码模板</b></summary>

```python
"""
输入验证与规范化模块
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Tuple

from ..state import RiskState
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..tools.csv_data import previous_trading_date


def _sum_weights(weights: Dict[str, float]) -> float:
    """计算权重之和"""
    # TODO: 实现
    pass


def _normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """归一化权重使其和为 1"""
    # TODO: 调用 _sum_weights，若 total <= 0 返回原值，否则每个值除以 total
    pass


def _coerce_weights(weights: Dict[str, Any], errors: list[str], label: str) -> Dict[str, float]:
    """将权重值强制转为 float，无法转换的记录到 errors"""
    # TODO: 遍历 weights，尝试 float(value)，失败则 append 错误信息
    pass


def _validate_date(date_str: str) -> Tuple[bool, str]:
    """校验日期格式 YYYY-MM-DD"""
    # TODO: 用 datetime.strptime 校验，返回 (True, "") 或 (False, 错误信息)
    pass


def validate_and_normalize(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """
    验证和规范化用户输入

    Args:
        state: 当前状态
        config: 运行时配置

    Returns:
        包含 "normalized" 和 "validation" 两个键的字典
    """
    cfg = config or DEFAULT_CONFIG
    intent = state.get("intent") or {}
    context = state.get("context") or {}

    errors = []
    warnings = []

    # TODO: 验证 intent.date 字段
    # - 检查是否存在（空字符串视为缺失）
    # - 用 _validate_date 检查格式

    # TODO: 验证 intent.mode 字段
    # - 默认值 "target"，只允许 "target" 或 "delta"

    # TODO: 用 _coerce_weights 转换 targets 和 current_positions
    # - targets 为空时记录错误

    # TODO: 处理 mode=delta
    # - 将 delta 叠加到 current_positions，然后 _normalize_weights
    # TODO: 处理 mode=target
    # - 权重和不为 1 时归一化并记录 warning

    # TODO: 构建 universe 列表
    # - 合并 context.universe + current.keys() + target_weights.keys()
    # - 去重保序（用 dict.fromkeys）

    # TODO: 调用 previous_trading_date(date_str, cfg) 获取 asof_date

    # TODO: 构建 normalized 字典（包含 asof_date, mode, targets, current_positions,
    #        current_positions_date, target_weights, universe, account_type,
    #        jurisdiction, policy_profile, aum）

    # TODO: 返回 {"normalized": normalized, "validation": {"is_valid": ..., "errors": ..., "warnings": ...}}
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

完成后请检查：
- [ ] 能正确验证日期格式
- [ ] 能正确验证 mode 字段
- [ ] 能正确归一化权重
- [ ] 能正确处理 delta 模式
- [ ] 错误和警告被正确记录

**测试命令：**
```bash
# 创建测试文件 test_validate.py
uv run --env-file .env -- python -u test_validate.py
```

**测试用例：**
```python
from src.tools.validate import (
    validate_and_normalize,
    _sum_weights, _normalize_weights, _coerce_weights, _validate_date,
)

# 测试1: 辅助函数
assert _sum_weights({"A": 0.3, "B": 0.7}) == 1.0
assert _sum_weights({}) == 0.0
nw = _normalize_weights({"A": 3, "B": 7})
assert abs(nw["A"] - 0.3) < 1e-9
ok, msg = _validate_date("2025-11-15")
assert ok and msg == ""
ok2, msg2 = _validate_date("bad-date")
assert not ok2

errs = []
cw = _coerce_weights({"A": "0.5", "B": "abc"}, errs, "test")
assert cw == {"A": 0.5} and len(errs) == 1

# 测试2: 正常输入
state = {
    "intent": {
        "date": "2025-11-15",
        "mode": "target",
        "targets": {"159213": 0.5, "159959": 0.5},
    },
    "context": {},
}
result = validate_and_normalize(state)
assert result["validation"]["is_valid"] is True
assert result["normalized"]["mode"] == "target"
assert abs(sum(result["normalized"]["target_weights"].values()) - 1.0) < 1e-6

# 测试3: 权重不为1 → 自动归一化 + warning
state2 = {
    "intent": {
        "date": "2025-11-15",
        "mode": "target",
        "targets": {"159213": 0.3, "159959": 0.4},
    },
    "context": {},
}
result2 = validate_and_normalize(state2)
assert len(result2["validation"]["warnings"]) > 0
assert abs(sum(result2["normalized"]["target_weights"].values()) - 1.0) < 1e-6

# 测试4: delta 模式
state3 = {
    "intent": {
        "date": "2025-11-15",
        "mode": "delta",
        "targets": {"159213": 0.1},
    },
    "context": {"current_positions": {"159213": 0.6, "159959": 0.4}},
}
result3 = validate_and_normalize(state3)
assert result3["validation"]["is_valid"] is True
assert "159213" in result3["normalized"]["target_weights"]

# 测试5: 缺失日期 → 错误
state4 = {"intent": {"targets": {"A": 1.0}}, "context": {}}
result4 = validate_and_normalize(state4)
assert result4["validation"]["is_valid"] is False

print("✅ 所有测试通过")
```

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. 日期验证可以使用 `datetime.strptime`
2. 权重归一化公式：`w_i_new = w_i / sum(w)`
3. delta 模式处理：`target = current + delta`

**常见错误：**
- ❌ 忘记处理空字典的情况
- ❌ 权重归一化后精度问题
- ❌ delta 模式下没有检查 current_positions 是否存在

**优化建议：**
- 使用 `get()` 方法避免 KeyError
- 对浮点数比较使用容差（如 `abs(x - 1.0) < 1e-6`）

</details>

---

## 📝 模块3: 数据与指标

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐ 中级 |
| **文件数** | 4个 |
| **文件路径** | `src/tools/utils.py`<br>`src/tools/csv_data.py`<br>`src/tools/data_quality.py`<br>`src/tools/snapshot.py` |
| **依赖模块** | 模块1, 2 |
| **被依赖** | 模块4, 5, 6, 7 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 金融指标计算（HHI、有效持仓数、波动率）
- [ ] CSV 数据处理技术
- [ ] 数据质量检查方法
- [ ] Pandas 数据分析应用

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块负责数据加载、质量检查和指标计算，是系统的数据基础层。

**核心功能：**
1. **工具函数**：提供权重归一化、HHI 计算等共享函数
2. **数据加载**：从 CSV 读取 ETF 行情、合规文本等
3. **质量检查**：检查数据完整性和新鲜度
4. **指标快照**：计算组合的风险指标

**为什么重要：**
数据质量直接影响风险分析的准确性，指标计算是后续决策的基础。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/tools/utils.py`

**常量：**
- `WEIGHT_TOLERANCE = 1e-6`：权重比较容差
- `EPSILON = 1e-12`：防除零常量

**实现 4 个工具函数：**

1. `normalize_weights(weights: Dict[str, float]) -> Dict[str, float]`
   - 将权重归一化为和为 1
   - 先用 `float()` 清洗值，`total <= 0` 时返回清洗后的原值

2. `compute_hhi(weights: Dict[str, float], already_normalized: bool = False) -> float`
   - 计算 HHI 指数（Herfindahl-Hirschman Index）
   - 公式：HHI = Σ(w_i²)
   - `already_normalized=True` 时跳过归一化，直接对 values 求平方和
   - `already_normalized=False` 时先除以 total 再求平方和

3. `compute_effective_n(weights: Dict[str, float], already_normalized: bool = False) -> float`
   - 计算有效持仓数（inverse HHI）
   - 公式：1 / HHI（HHI ≤ EPSILON 时返回 0.0）

4. `weights_sum_to_one(weights: Dict[str, float]) -> bool`
   - 检查权重和是否在 WEIGHT_TOLERANCE 内等于 1.0

### 文件2：`src/tools/csv_data.py`

**实现数据加载与查询函数（共 18 个函数）：**

**基础设施（3 个）：**
1. `_data_dir(config) -> Path`：根据 `config.csv_data_dir` 返回数据目录，默认 `cufel_practice_data/`
2. `_load_csv(path, *, usecols=None) -> pd.DataFrame`：通用 CSV 加载，文件不存在返回空 DataFrame
3. `_load_etf_prices_cached(path_str) -> pd.DataFrame`：带 `@lru_cache` 的 ETF 行情加载，转换 code/date/数值列类型

**数据加载（5 个）：**
4. `load_etf_prices(config) -> pd.DataFrame`：加载 `etf_2025_data.csv`
5. `load_etf_basic(config) -> pd.DataFrame`：加载 `sampled_etf_basic.csv`（ETF 基本信息）
6. `load_compliance_docs(config) -> pd.DataFrame`：加载 `csrc_2025.csv`（合规文本）
7. `load_macro_docs(config) -> pd.DataFrame`：加载宏观文本（优先 `govcn_2025_results.json`，降级到 `govcn_2025.csv`）
8. `etf_industry_map(config) -> Dict[str, str]`：从 ETF 基本信息构建 `{code: industry}` 映射

**查询函数（6 个）：**
9. `etf_codes_by_industry(industry_names, config) -> Dict[str, List[str]]`：按行业名查 ETF 代码
10. `security_master_codes(config) -> Tuple[set, str]`：返回所有已知 ETF 代码集合及来源文件名
11. `sample_universe(asof_date, size, seed, config) -> List[str]`：随机采样 ETF 代码（用于蒙特卡洛）
12. `previous_trading_date(asof_date, config) -> str`：查找 asof_date 之前最近的交易日
13. `lookback_start_date(asof_date, lookback_days) -> str`：计算回溯起始日期

**行情指标（2 个）：**
14. `market_metrics(codes, start_date, end_date, config) -> Dict[str, Dict[str, float]]`：计算每只 ETF 的 volatility / adv / spread_bps
15. `market_metrics_by_range(start_date, end_date, config) -> Tuple[List[str], Dict]`：按日期范围查全部 ETF 指标

**文本搜索（2 个）：**
16. `macro_search_hits(query, limit, asof_date, config) -> List[Dict]`：关键词搜索宏观文本
17. `compliance_search_hits(query, limit, config) -> List[str]`：关键词搜索合规文本

**可用性检查（2 个）：**
18. `macro_docs_available(config) -> bool` / `compliance_docs_available(config) -> bool`
19. `macro_latest_date(asof_date, config) -> str`：宏观文本最新日期

### 文件3：`src/tools/data_quality.py`

**实现 `check_data_quality(state, config) -> Dict[str, Any]`**（注意：函数名不是 `data_quality_node`，返回 Dict 不是 RiskState）

**辅助函数：**
- `_append_gap(data_gaps, status, *, gap_type, severity, message, affect_status=True) -> str`
  - 向 data_gaps 列表追加一条记录
  - severity 为 `"block"` 时 status 升级为 `"blocked"`
  - severity 为 `"warn"` 且当前 status 为 `"ok"` 时升级为 `"degraded"`
  - `affect_status=False` 时不改变 status

**检查项：**
- ETF 主表是否缺失（`security_master_codes`）
- universe 中哪些 ETF 缺少主表 / 缺少行情数据
- 宏观时序可用性（`bool(cfg.tushare_token)`）
- 宏观文本可用性与新鲜度（`macro_docs_available` + `macro_latest_date`）
- 新鲜度状态：`ok` / `stale` / `future` / `unknown`
- 合规文本可用性（`compliance_docs_available`）
- 持仓数据新鲜度（`current_positions_date` 与 `asof_date` 的天数差）

**返回值：**
```python
{
    "data_quality": {
        "status": "ok" | "degraded" | "blocked",
        "market": {"missing_etf_master": [...], "missing_market": [...]},
        "macro": {
            "timeseries_available": bool,
            "text_available": bool,
            "latest_date": str,
            "freshness_days": int | None,
            "freshness_status": "ok" | "stale" | "future" | "unknown",
        },
        "compliance": {"text_available": bool},
        "positions": {"freshness_days": int | None},
    },
    "data_gaps": [{"type": str, "severity": str, "message": str}, ...],
}
```

### 文件4：`src/tools/snapshot.py`

**实现 `risk_snapshot_bundle(state, config) -> Dict[str, Any]`**（注意：函数名不是 `snapshot_node`，返回 Dict 不是 RiskState）

**计算指标（返回 `{"snapshot_metrics": metrics}` 字典）：**

| 指标 | 说明 |
|:---|:---|
| `portfolio_volatility` | 目标权重的加权波动率 |
| `current_portfolio_volatility` | 当前持仓的加权波动率 |
| `delta_portfolio_volatility` | 目标 - 当前波动率差值 |
| `weighted_spread_bps` | 加权买卖价差（基点） |
| `weighted_adv` | 加权日均成交额 |
| `hhi` | 目标权重的 HHI 集中度 |
| `effective_n` | 目标权重的有效持仓数 |
| `top_weight` | 目标权重中最大单一权重 |
| `current_hhi` / `current_effective_n` / `current_top_weight` | 当前持仓的对应指标 |
| `delta_hhi` / `delta_effective_n` | 目标 - 当前的差值 |
| `turnover` | 换手率 = 0.5 × Σ|target_w - current_w| |
| `max_position_delta` | 最大单一持仓变动 |
| `max_adv_ratio` | 最大交易额/ADV 比率（需要 aum） |
| `adv_by_symbol` | 每只 ETF 的 ADV 字典 |
| `macro_severity` | 初始值 0（后续由宏观 Agent 更新） |
| `missing_market_rows` | 缺少行情数据的 ETF 列表 |

**关键实现细节：**
- 使用 `normalize_weights` / `compute_hhi` / `compute_effective_n`（来自 utils.py）
- 使用 `market_metrics` / `lookback_start_date`（来自 csv_data.py）
- aum 优先取 `normalized.aum`，为 None 时取 `cfg.default_aum`

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/utils.py`

```python
"""Common utility functions for risk tools."""
from __future__ import annotations

from typing import Dict

# Tolerance constants for floating-point comparisons
WEIGHT_TOLERANCE = 1e-6
EPSILON = 1e-12


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """Normalize weights to sum to 1.0."""
    # TODO: 用 float() 清洗每个值
    # TODO: 计算 total，若 total <= 0 返回清洗后的原值
    # TODO: 否则每个值除以 total
    pass


def compute_hhi(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """Compute HHI = Σ(w_i²).

    Args:
        weights: {symbol: weight}
        already_normalized: True 时跳过归一化，直接对 values 求平方和
    """
    # TODO: already_normalized=True → 直接 sum(w**2 for w in weights.values())
    # TODO: already_normalized=False → 先算 total，再 sum((v/total)**2)
    # TODO: total <= 0 时返回 0.0
    pass


def compute_effective_n(weights: Dict[str, float], already_normalized: bool = False) -> float:
    """Compute effective number of holdings = 1 / HHI."""
    # TODO: 调用 compute_hhi
    # TODO: hhi > EPSILON 时返回 1.0/hhi，否则返回 0.0
    pass


def weights_sum_to_one(weights: Dict[str, float]) -> bool:
    """Check if weights sum to 1.0 within WEIGHT_TOLERANCE."""
    # TODO: abs(sum - 1.0) <= WEIGHT_TOLERANCE
    pass
```

### 文件2：`src/tools/csv_data.py`

```python
"""CSV 数据读取与查询模块"""
from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

from ..config import RuntimeConfig, DEFAULT_CONFIG

_ROOT = Path(__file__).resolve().parents[2]


def _data_dir(config: RuntimeConfig | None = None) -> Path:
    """返回数据目录路径"""
    cfg = config or DEFAULT_CONFIG
    # TODO: 若 cfg.csv_data_dir 有值则用它，否则用 _ROOT / "cufel_practice_data"
    pass


def _load_csv(path: Path, *, usecols: Iterable[str] | None = None) -> pd.DataFrame:
    """通用 CSV 加载，文件不存在返回空 DataFrame"""
    # TODO: path 不存在返回 pd.DataFrame()，否则 pd.read_csv
    pass


@lru_cache(maxsize=4)
def _load_etf_prices_cached(path_str: str) -> pd.DataFrame:
    """带缓存的 ETF 行情加载"""
    # TODO: 调用 _load_csv
    # TODO: 转换列类型：code→str, date→datetime, 数值列→numeric
    #   数值列: open, high, low, close, vol, amount, pre_close, change, pct_chg, adj_factor
    # TODO: dropna(subset=["date", "code"])
    pass


def load_etf_prices(config: RuntimeConfig | None = None) -> pd.DataFrame:
    """加载 ETF 行情数据"""
    # TODO: 拼接路径 _data_dir(config) / "etf_2025_data.csv"，调用 cached 版本
    pass


@lru_cache(maxsize=4)
def _load_etf_basic_cached(path_str: str) -> pd.DataFrame:
    """带缓存的 ETF 基本信息加载"""
    # TODO: 加载 CSV，code 列转 str
    pass


def load_etf_basic(config: RuntimeConfig | None = None) -> pd.DataFrame:
    """加载 ETF 基本信息"""
    # TODO: 拼接路径 "sampled_etf_basic.csv"
    pass


@lru_cache(maxsize=4)
def _etf_industry_map_cached(path_str: str) -> Dict[str, str]:
    """构建 {code: industry} 映射"""
    # TODO: 从 _load_etf_basic_cached 取 code + indx_csname 两列
    # TODO: 遍历构建映射字典
    pass


def etf_industry_map(config: RuntimeConfig | None = None) -> Dict[str, str]:
    """返回 ETF 代码到行业的映射"""
    pass


def etf_codes_by_industry(
    industry_names: Iterable[str], config: RuntimeConfig | None = None
) -> Dict[str, List[str]]:
    """按行业名查 ETF 代码，返回 {industry: [codes]}"""
    # TODO: 调用 etf_industry_map，反转映射
    pass


@lru_cache(maxsize=4)
def _load_compliance_docs_cached(path_str: str) -> pd.DataFrame:
    """带缓存的合规文本加载"""
    # TODO: 加载 csrc_2025.csv，date→datetime，title/content/from→str
    pass


def load_compliance_docs(config: RuntimeConfig | None = None) -> pd.DataFrame:
    pass


@lru_cache(maxsize=4)
def _load_macro_docs_cached(results_str: str, csv_str: str) -> pd.DataFrame:
    """加载宏观文本（优先 JSON，降级 CSV）"""
    # TODO: 优先尝试 govcn_2025_results.json
    #   - 解析 results 列表，提取 date/title/content/industry_name/sentiment_score
    # TODO: JSON 不可用时降级到 govcn_2025.csv
    pass


def load_macro_docs(config: RuntimeConfig | None = None) -> pd.DataFrame:
    pass


def security_master_codes(config: RuntimeConfig | None = None) -> Tuple[set, str]:
    """返回 (所有已知 ETF 代码集合, 来源文件名)"""
    # TODO: 优先从 load_etf_basic 取，降级到 load_etf_prices
    # TODO: 都没有时返回 (set(), "missing")
    pass


def sample_universe(
    asof_date: str, size: int, seed: str | None, config: RuntimeConfig | None = None
) -> List[str]:
    """随机采样 ETF 代码（用于蒙特卡洛校准）"""
    # TODO: 从 load_etf_prices 取 asof_date 之前的所有 code
    # TODO: 用 random.Random(seed) 采样 size 个
    pass


def lookback_start_date(asof_date: str, lookback_days: int) -> str:
    """计算回溯起始日期 = asof_date - lookback_days"""
    pass


def previous_trading_date(asof_date: str, config: RuntimeConfig | None = None) -> str:
    """查找 asof_date 之前最近的交易日"""
    # TODO: 从 load_etf_prices 中找 date < asof_date 的最大日期
    # TODO: 找不到时返回 asof_date 本身
    pass


def market_metrics(
    codes: Iterable[str],
    start_date: str | None,
    end_date: str | None,
    config: RuntimeConfig | None = None,
) -> Dict[str, Dict[str, float]]:
    """计算每只 ETF 的 volatility / adv / spread_bps"""
    # TODO: 从 load_etf_prices 筛选 codes + 日期范围
    # TODO: 计算复权收益率 ret = groupby("code")[adj_close].pct_change()
    # TODO: spread_bps = (high - low) / close * 10000
    # TODO: volatility = grouped["ret"].std(ddof=0)
    # TODO: adv = grouped["amount"].mean()
    # TODO: spread_bps = grouped["spread_bps"].mean()
    pass


def market_metrics_by_range(
    start_date: str, end_date: str, config: RuntimeConfig | None = None
) -> Tuple[List[str], Dict[str, Dict[str, float]]]:
    """按日期范围查全部 ETF 指标"""
    # TODO: 筛选日期范围内的 codes，调用 market_metrics
    pass


def macro_docs_available(config: RuntimeConfig | None = None) -> bool:
    """宏观文本是否可用"""
    pass


def compliance_docs_available(config: RuntimeConfig | None = None) -> bool:
    """合规文本是否可用"""
    pass


def _text_mask(df: pd.DataFrame, query: str, columns: Iterable[str]) -> pd.Series:
    """关键词匹配掩码（大小写不敏感）"""
    # TODO: 对每个 column 做 str.contains(query.lower())，用 | 合并
    pass


def macro_search_hits(
    query: str,
    limit: int = 5,
    asof_date: str | None = None,
    config: RuntimeConfig | None = None,
) -> List[Dict[str, Any]]:
    """关键词搜索宏观文本，返回 [{date, title, summary, sentiment_score}]"""
    # TODO: 加载 macro_docs，按 asof_date 截断，用 _text_mask 过滤
    pass


def compliance_search_hits(
    query: str, limit: int = 5, config: RuntimeConfig | None = None
) -> List[str]:
    """关键词搜索合规文本，返回 content 列表"""
    pass


def macro_latest_date(
    asof_date: str | None = None, config: RuntimeConfig | None = None
) -> str:
    """宏观文本最新日期"""
    pass
```

### 文件3：`src/tools/data_quality.py`

```python
"""数据质量检查模块"""
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
    """向 data_gaps 追加一条记录，并根据 severity 升级 status"""
    # TODO: append {"type": gap_type, "severity": severity, "message": message}
    # TODO: affect_status=False 时直接返回原 status
    # TODO: severity=="block" → 返回 "blocked"
    # TODO: severity=="warn" 且 status=="ok" → 返回 "degraded"
    # TODO: 其他情况返回原 status
    pass


def check_data_quality(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """检查数据完整性与新鲜度，生成 data_quality 与 data_gaps。"""
    cfg = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}
    universe = normalized.get("universe") or []
    asof_date = normalized.get("asof_date") or ""
    positions_date = normalized.get("current_positions_date") or ""

    data_gaps: List[Dict[str, Any]] = []
    status = "ok"

    # TODO: 检查 ETF 主表（security_master_codes）
    # - 主表为空时 _append_gap(severity="warn")

    # TODO: 检查行情数据（market_metrics）
    # - 找出 universe 中缺少主表 / 缺少行情的 ETF
    # - 分别 _append_gap

    # TODO: 检查宏观数据
    # - timeseries_available = bool(cfg.tushare_token)
    # - text_available = macro_docs_available(cfg)
    # - latest_date = macro_latest_date(asof_date, cfg)
    # - 计算 freshness_days 和 freshness_status

    # TODO: 检查合规数据
    # - compliance_docs_available(cfg)

    # TODO: 全部 universe 缺行情时 severity="block"

    # TODO: 检查持仓数据新鲜度
    # - asof_date 与 positions_date 的天数差

    # TODO: 组装 data_quality 字典并返回
    # return {"data_quality": {...}, "data_gaps": data_gaps}
    pass
```

### 文件4：`src/tools/snapshot.py`

```python
"""指标快照计算模块"""
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

    # TODO: 获取行情数据
    # codes = set(target_weights) | set(current_weights)
    # market = market_metrics(codes, start_date or asof_date, asof_date, cfg)

    # TODO: 归一化权重
    # target_norm = normalize_weights(target_weights)
    # current_norm = normalize_weights(current_weights)

    # TODO: 计算集中度指标（hhi, effective_n, top_weight）
    # - 分别对 target_norm 和 current_norm 计算

    # TODO: 计算换手率和最大持仓变动
    # turnover = 0.5 * sum(|target_w - current_w|)

    # TODO: 计算加权波动率、价差、ADV
    # - 遍历 target_norm，从 market 取每只 ETF 的指标
    # - weighted_vol += weight * volatility
    # - weighted_spread += weight * spread_bps
    # - weighted_adv += weight * adv

    # TODO: 计算 max_adv_ratio（需要 aum）
    # ratio = (trade_amount * aum) / adv

    # TODO: 计算当前持仓的波动率 current_vol

    # TODO: 组装 metrics 字典（包含上述所有指标 + delta 指标）
    # return {"snapshot_metrics": metrics}
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试 utils.py
```python
from src.tools.utils import (
    normalize_weights, compute_hhi, compute_effective_n, weights_sum_to_one,
    WEIGHT_TOLERANCE, EPSILON,
)

# 测试归一化
weights = {"A": 3, "B": 7}
normalized = normalize_weights(weights)
assert abs(sum(normalized.values()) - 1.0) < 1e-6
assert abs(normalized["A"] - 0.3) < 1e-9

# 测试 HHI（已归一化）
hhi = compute_hhi({"A": 0.5, "B": 0.5}, already_normalized=True)
assert abs(hhi - 0.5) < 1e-6

# 测试 HHI（未归一化）
hhi2 = compute_hhi({"A": 3, "B": 7}, already_normalized=False)
assert abs(hhi2 - 0.58) < 1e-6  # (0.3^2 + 0.7^2)

# 测试有效持仓数
effective_n = compute_effective_n({"A": 0.5, "B": 0.5}, already_normalized=True)
assert abs(effective_n - 2.0) < 1e-6

# 测试 weights_sum_to_one
assert weights_sum_to_one({"A": 0.5, "B": 0.5}) is True
assert weights_sum_to_one({"A": 0.3, "B": 0.4}) is False

print("✅ utils.py 测试通过")
```

### 测试 csv_data.py
```python
from src.tools.csv_data import (
    load_etf_prices, load_etf_basic, load_compliance_docs, load_macro_docs,
    security_master_codes, previous_trading_date, market_metrics,
    macro_docs_available, compliance_docs_available,
)

# 测试数据加载
df = load_etf_prices()
assert not df.empty
assert "code" in df.columns and "date" in df.columns

# 测试 ETF 基本信息
basic = load_etf_basic()
assert not basic.empty

# 测试 security_master_codes
codes, source = security_master_codes()
assert len(codes) > 0

# 测试 previous_trading_date
prev = previous_trading_date("2025-11-15")
assert prev  # 应返回非空字符串

# 测试 market_metrics
metrics = market_metrics(list(codes)[:3], "2025-01-01", "2025-11-15")
for code, m in metrics.items():
    assert "volatility" in m and "adv" in m and "spread_bps" in m

# 测试可用性检查
print(f"macro_docs_available: {macro_docs_available()}")
print(f"compliance_docs_available: {compliance_docs_available()}")

print("✅ csv_data.py 测试通过")
```

### 测试完整流程
```bash
uv run --env-file .env -- python -u -m pytest tests/test_module3.py -v
```

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **HHI 计算**：注意权重需要先归一化
2. **波动率计算**：使用 `pandas.std()` 计算标准差
3. **数据截断**：使用 `df[df['date'] <= asof_date]`

**常见错误：**
- ❌ 忘记处理空 DataFrame
- ❌ 日期比较时类型不匹配（str vs datetime）
- ❌ 除零错误（HHI 为 0 时）

**性能优化：**
- 使用 Pandas 向量化操作而不是循环
- 缓存 ETF 数据避免重复读取

**参考资源：**
- [Pandas 官方文档](https://pandas.pydata.org/docs/)
- [HHI 指数说明](https://en.wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index)

</details>

---

## 📝 模块4: 编排调度

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐⭐ 高级 |
| **文件数** | 3个 |
| **文件路径** | `src/graph.py`<br>`src/chains/gatekeeper.py`<br>`src/chains/supervisor.py` |
| **依赖模块** | 模块1, 2, 3 |
| **被依赖** | 模块5, 6 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] LangGraph 工作流编排
- [ ] DAG（有向无环图）设计
- [ ] Send API 实现并行执行
- [ ] LLM 作为调度器的应用
- [ ] 条件路由逻辑

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块是系统的核心编排层，负责协调所有节点的执行顺序和并行调度。

**核心功能：**
1. **工作流编排**：使用 LangGraph 构建 DAG
2. **数据可用性检查**：Gatekeeper 基于数据可用性裁剪候选节点
3. **业务逻辑调度**：Supervisor 基于业务逻辑从候选节点中选择需要运行的节点
4. **并行执行**：使用 Send API 实现真正的并行

**为什么重要：**
编排层决定了系统的执行效率和灵活性，是 MAS 架构的关键。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/graph.py`

**实现 `build_graph(llm=None, config=None)` 函数**（注意：函数名是 `build_graph` 不是 `create_graph`）

**关键内部函数：**
- `_should_run_node(state, name) -> bool`：检查 `state["pending_agents"]` 中是否包含该节点，且 `stop_condition` 为 False
- `_guarded_node(name, fn)`：包装分析节点，不在 pending 列表中时返回 `{f"finding_{name}": None}`
- `dispatch_to_parallel(state) -> List[Send]`：根据 `pending_agents` 列表用 Send API 并行分发

**节点注册方式：**
- 所有节点用 `RunnableLambda` 包装后 `add_node`
- 分析节点（6个）统一用 `_guarded_node` 包装
- 每个节点函数是一个 lambda，将 `cfg` / `llm` 通过闭包传入对应的 chain/agent 函数

**边的连接：**
- 串行管道：validate → data_quality → snapshot → gatekeeper → supervisor
- 条件边：supervisor → `dispatch_to_parallel`（Send API 并行分发）
- 所有分析节点 → reducer
- 后处理管道：reducer → constraints → decision → solver → audit → END

### 文件2：`src/chains/gatekeeper.py`

**实现 `gatekeeper_chain(state) -> Dict[str, Any]`**（注意：函数名是 `gatekeeper_chain`，返回 Dict）

**逻辑：**
1. 检查 `validation.is_valid`：为 False 时设 `stop_condition=True`
2. 检查 `data_quality.status`：为 `"blocked"` 时设 `stop_condition=True`
3. 非停止时构建候选列表：4 个确定性链始终加入，macro/compliance 按数据可用性条件加入
4. 返回 `{candidate_nodes, stop_condition, gatekeeper_used, gatekeeper_rationale}`

### 文件3：`src/chains/supervisor.py`

**实现 `supervisor_chain(state, llm, candidates, config) -> Dict[str, Any]`**（注意：函数名和参数）

**辅助函数：**
- `_fallback_result(candidates, *, used, rationale) -> Dict`：降级结果，直接用全部候选
- `_normalize_nodes(nodes, candidates) -> List[str]`：过滤 LLM 输出，只保留候选中的节点

**逻辑：**
1. `cfg.enable_supervisor` 为 False 时返回 fallback（全部候选）
2. `llm is None` 时返回 fallback
3. 加载 `load_skill("supervisor-router")`，构建 system_prompt
4. 将 candidates + validation + data_quality + snapshot_metrics + rule_findings + policy_profile 打包为 JSON 发给 LLM
5. 解析 LLM 输出的 `nodes_to_run` 和 `rationale`
6. 用 `_normalize_nodes` 过滤，空列表时降级回全部候选
7. 返回 `{nodes_to_run, pending_agents, supervisor_used, supervisor_rationale, supervisor_model}`

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/graph.py`

```python
"""LangGraph 工作流编排模块"""
from __future__ import annotations

from typing import Any, Dict, List, Literal

from langgraph.graph import StateGraph, END
from langgraph.types import Send
from langchain_core.runnables import RunnableLambda

from .state import RiskState
from .config import RuntimeConfig, DEFAULT_CONFIG
from .tools import (
    validate_and_normalize,
    check_data_quality,
    risk_snapshot_bundle,
    constraints_evaluator,
    decision_engine,
    constraint_solver,
    audit_log,
)
from .chains import (
    gatekeeper_chain,
    supervisor_chain,
    market_risk_chain,
    concentration_chain,
    diversification_chain,
    liquidity_chain,
    reducer_chain,
)
from .agents import run_macro_agent, run_compliance_agent


def _should_run_node(state: RiskState, name: str) -> bool:
    """Check if a node should run based on pending_agents list."""
    # TODO: stop_condition 为 True 时返回 False
    # TODO: 检查 name 是否在 state["pending_agents"] 中
    pass


def build_graph(llm=None, config: RuntimeConfig | None = None):
    """构建并返回主工作流图。"""
    cfg = config or DEFAULT_CONFIG
    g = StateGraph(RiskState)

    # TODO: 定义 pipeline 节点函数（用闭包传入 cfg）
    # def validate_node(state): return validate_and_normalize(state, cfg)
    # def data_quality_node(state): return check_data_quality(state, cfg)
    # def snapshot_node(state): return risk_snapshot_bundle(state, cfg)
    # ... 类似定义 constraints_node, gatekeeper_node, supervisor_node

    # TODO: 定义分析节点字典
    # analysis_nodes = {"market": lambda s: market_risk_chain(s, cfg), ...}
    # agent_nodes = {"macro": lambda s: run_macro_agent(s, llm, cfg), ...}
    # all_analysis_nodes = {**analysis_nodes, **agent_nodes}

    # TODO: 实现 _guarded_node(name, fn) 包装器
    # - 不在 pending_agents 中时返回 {f"finding_{name}": None}
    # - 在列表中时正常调用 fn(state)

    # TODO: 定义后处理节点（reducer, decision, solver, audit）

    # TODO: 实现 dispatch_to_parallel(state) -> List[Send]
    # - stop_condition 或 pending 为空时 → [Send("reducer", state)]
    # - 否则为每个 pending 节点创建 Send 对象

    # TODO: 注册所有节点（用 RunnableLambda 包装）
    # g.add_node("validate", RunnableLambda(validate_node))
    # 分析节点用 _guarded_node 包装

    # TODO: 添加边
    # g.set_entry_point("validate")
    # g.add_edge("validate", "data_quality")
    # ... 串行管道
    # g.add_conditional_edges("supervisor", dispatch_to_parallel)
    # for name in all_analysis_nodes: g.add_edge(name, "reducer")
    # ... 后处理管道 → END

    return g.compile()
```

### 文件2：`src/chains/gatekeeper.py`

```python
"""前置检查模块（Gatekeeper）"""
from __future__ import annotations

from typing import Any, Dict, List

from ..state import RiskState


def gatekeeper_chain(state: RiskState) -> Dict[str, Any]:
    """前置检查，基于数据可用性和验证结果裁剪候选节点。"""
    validation = state.get("validation") or {}
    data_quality = state.get("data_quality") or {}

    stop_condition = False
    rationale: List[str] = []

    # TODO: 检查 validation.is_valid
    # - 为 False 时设 stop_condition=True，rationale 追加 "validation_failed"

    # TODO: 检查 data_quality.status
    # - 为 "blocked" 时设 stop_condition=True，rationale 追加 "data_quality_blocked"

    # TODO: 非停止时构建候选列表
    # - 4 个确定性链始终加入: market, concentration, diversification, liquidity
    # - macro: 仅当 data_quality["macro"]["timeseries_available"] 为 True
    # - compliance: 仅当 data_quality["compliance"]["text_available"] 为 True

    # TODO: 返回字典
    # return {
    #     "candidate_nodes": candidates,
    #     "stop_condition": stop_condition,
    #     "gatekeeper_used": True,
    #     "gatekeeper_rationale": "; ".join(rationale) if rationale else "ok",
    # }
    pass
```

### 文件3：`src/chains/supervisor.py`

```python
"""业务逻辑节点选择模块（Supervisor）"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from langchain_core.messages import HumanMessage, SystemMessage

from ..state import RiskState
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..skills_runtime import load_skill, build_system_prompt, validate_output

_BASE_PROMPT = (
    "你是系统调度员，负责决定运行哪些分析节点。"
    "只能从提供的候选列表中选择。"
    "始终返回 JSON，包含 keys: nodes_to_run (list of strings) 和 rationale (string)。"
    "rationale 必须为中文。"
)


def _llm_model_name(llm) -> str:
    return str(getattr(llm, "model_name", None) or getattr(llm, "model", None) or "")


def _fallback_result(candidates: List[str], *, used: bool, rationale: str) -> Dict[str, Any]:
    """降级结果：直接用全部候选节点"""
    # TODO: 返回 {nodes_to_run, pending_agents, supervisor_used, supervisor_rationale}
    pass


def _normalize_nodes(nodes: List[str], candidates: List[str]) -> List[str]:
    """过滤 LLM 输出，只保留候选中的节点"""
    # TODO: 只保留 nodes 中存在于 candidates 的元素
    pass


def supervisor_chain(
    state: RiskState, llm, candidates: List[str], config: RuntimeConfig | None = None
) -> Dict[str, Any]:
    """基于业务逻辑从候选节点中选择需要运行的节点。"""
    cfg = config or DEFAULT_CONFIG

    # TODO: stop_condition 时返回空字典
    # TODO: enable_supervisor 为 False 时返回 _fallback_result
    # TODO: llm is None 时返回 _fallback_result

    # TODO: 加载 skill = load_skill("supervisor-router")
    # TODO: 构建 system_prompt = build_system_prompt(_BASE_PROMPT, skill)

    # TODO: 构建 payload（candidates + validation + data_quality + snapshot_metrics + ...）
    # TODO: 调用 llm.invoke([SystemMessage(...), HumanMessage(...)])

    # TODO: 解析 JSON 输出，validate_output 校验
    # TODO: _normalize_nodes 过滤，空列表时降级回全部候选

    # TODO: 返回 {nodes_to_run, pending_agents, supervisor_used, supervisor_rationale, supervisor_model}
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试 Gatekeeper
```python
from src.chains.gatekeeper import gatekeeper_chain

# 测试1: macro 不可用时被裁剪
state = {
    "validation": {"is_valid": True},
    "data_quality": {
        "status": "ok",
        "macro": {"timeseries_available": False},
        "compliance": {"text_available": True},
    },
}
result = gatekeeper_chain(state)
assert "macro" not in result["candidate_nodes"]
assert "compliance" in result["candidate_nodes"]
assert result["stop_condition"] is False

# 测试2: validation 失败时 stop
state2 = {
    "validation": {"is_valid": False},
    "data_quality": {"status": "ok"},
}
result2 = gatekeeper_chain(state2)
assert result2["stop_condition"] is True
assert result2["candidate_nodes"] == []

print("✅ Gatekeeper 测试通过")
```

### 测试完整工作流
```bash
# 运行完整工作流
uv run --env-file .env -- python -u -m src.app
```

**检查项：**
- [ ] 所有节点都已添加
- [ ] 边的连接正确
- [ ] 并行执行正常工作
- [ ] 条件路由正确

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **Send API 用法**：
   ```python
   return [Send("node_name", state) for node in nodes_to_run]
   ```

2. **条件边**：使用 `add_conditional_edges` 实现条件路由

3. **LLM 调用**：使用结构化输出确保返回格式正确

**常见错误：**
- ❌ 忘记添加 END 节点
- ❌ 循环依赖导致 DAG 无效
- ❌ Send API 使用不当导致并行失败

**调试技巧：**
- 使用 `graph.get_graph().draw_mermaid()` 可视化工作流
- 打印每个节点的输入输出
- 使用 LangSmith 追踪执行过程

**参考资源：**
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [Send API 示例](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/)

</details>

---

## 📝 模块5: 分析链路

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐ 中级 |
| **文件数** | 5个 |
| **文件路径** | `src/chains/common.py`<br>`src/chains/market.py`<br>`src/chains/concentration.py`<br>`src/chains/diversification.py`<br>`src/chains/liquidity.py` |
| **依赖模块** | 模块1, 3, 7, 8 |
| **被依赖** | 模块4（graph 中注册） |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 确定性风险分析链的设计模式
- [ ] 规则阈值的应用
- [ ] 风险等级判断逻辑
- [ ] 证据收集和建议生成

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块实现4条确定性分析链，基于规则和指标进行风险评估。

**核心功能：**
1. **市场风险**：基于组合波动率
2. **集中度风险**：基于 HHI 指数
3. **分散度风险**：基于有效持仓数
4. **流动性风险**：基于买卖价差和成交量

**为什么重要：**
确定性链提供快速、可靠的风险评估，是系统的基础分析层。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 通用要求

每个分析链都遵循相同模式：
1. 从 `state["snapshot_metrics"]` 获取指标
2. 从 `state["normalized"]["policy_profile"]` 获取规则配置名（默认 `"default"`）
3. 用 `load_rules_cached(profile, config)` 加载阈值
4. 比较指标与阈值，判断 severity（0/1/2）
5. 构建 `Finding` TypedDict（包含 agent/risk_type/severity/summary/metrics/evidence）
6. 调用 `validate_finding(skill_name, finding, label)` 做 Schema 校验
7. 返回 `{f"finding_{risk_type}": finding}`（Dict，不是 RiskState）

### 文件0：`src/chains/common.py`

**实现 2 个共享函数：**
- `load_rules_cached(profile, config) -> Dict`：调用 `load_rules(profile, config)` 并返回规则字典
- `validate_finding(skill_name, finding, label) -> None`：调用 `validate_output(load_skill(skill_name), finding)`，有错误时 raise RuntimeError

### 文件1：`src/chains/market.py`

**实现 `market_risk_chain(state, config) -> Dict[str, Any]`**

- 指标：`portfolio_volatility`
- 阈值：`volatility_warn`, `volatility_restrict`
- 判断：vol >= restrict → severity=2, vol >= warn → severity=1, 否则 0

### 文件2：`src/chains/concentration.py`

**实现 `concentration_chain(state, config) -> Dict[str, Any]`**

- 指标：`hhi` + `top_weight`（两个指标取严格的）
- 阈值：`hhi_warn/restrict`, `top_weight_warn/restrict`
- 判断：任一 >= restrict → 2, 任一 >= warn → 1

### 文件3：`src/chains/diversification.py`

**实现 `diversification_chain(state, config) -> Dict[str, Any]`**

- 指标：`effective_n`（反向指标，越小越危险）
- 阈值：`effective_n_warn`, `effective_n_restrict`
- 判断：n <= restrict → 2, n <= warn → 1

### 文件4：`src/chains/liquidity.py`

**实现 `liquidity_chain(state, config) -> Dict[str, Any]`**

- 指标：`weighted_spread_bps`（正向）+ `weighted_adv`（反向）
- 阈值：`spread_warn/restrict`, `adv_warn/restrict`
- 判断：spread >= restrict 或 adv <= restrict → 2

</details>

<details>
<summary><b>💻 代码模板</b></summary>

由于4个分析链结构相似，这里先提供 common.py 和 market.py 完整模板，其余3个参照修改。

### 文件0：`src/chains/common.py`

```python
"""分析链共享工具"""
from __future__ import annotations

from typing import Any, Dict

from ..skills_runtime import load_skill, validate_output
from ..tools.rules import load_rules
from ..config import RuntimeConfig, DEFAULT_CONFIG


def load_rules_cached(profile: str, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """加载指定 profile 的规则阈值"""
    # TODO: 调用 load_rules(profile, config or DEFAULT_CONFIG)，返回规则字典
    pass


def validate_finding(skill_name: str, finding: Dict[str, Any], label: str) -> None:
    """用 Skill 的 output.schema.json 校验 Finding 结构"""
    # TODO: errors = validate_output(load_skill(skill_name), finding)
    # TODO: 有错误时 raise RuntimeError(f"{label} skill output invalid: {errors}")
    pass
```

### 文件1：`src/chains/market.py`（完整模板）

```python
"""市场风险分析模块"""
from __future__ import annotations

from typing import Dict, Any

from ..state import RiskState, Finding
from .common import load_rules_cached, validate_finding
from ..config import RuntimeConfig


def market_risk_chain(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """市场风险分析（基于波动率）"""
    metrics = state.get("snapshot_metrics") or {}
    vol = float(metrics.get("portfolio_volatility", 0.0))

    # TODO: 获取 policy_profile，加载规则阈值
    # profile = (state.get("normalized") or {}).get("policy_profile", "default")
    # rules = load_rules_cached(profile, config)
    # vol_warn = float(rules.get("volatility_warn", 0.15))
    # vol_restrict = float(rules.get("volatility_restrict", 0.25))

    # TODO: 判断 severity（0/1/2）

    # TODO: 构建 Finding（包含 agent, risk_type, severity, summary, metrics, evidence）

    # TODO: validate_finding("risk-market-assessor", finding, "market")

    # TODO: return {"finding_market": finding}
    pass
```

**其余3个文件（concentration / diversification / liquidity）结构完全相同，只需修改：**
- 函数名：`concentration_chain` / `diversification_chain` / `liquidity_chain`
- 指标名和阈值名（参见实现要求）
- Finding 的 `agent` / `risk_type` 字段
- liquidity 的 skill_name 为 `"liquidity-execution-assessor"`，其余为 `"risk-market-assessor"`

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 单元测试示例

```python
from src.chains.market import market_risk_chain
from src.chains.concentration import concentration_chain

# 测试 market_risk_chain
state = {
    "snapshot_metrics": {"portfolio_volatility": 0.10},
    "normalized": {"policy_profile": "default"},
}
result = market_risk_chain(state)
assert "finding_market" in result
assert result["finding_market"]["risk_type"] == "market"
assert result["finding_market"]["severity"] >= 0

# 测试 concentration_chain
state2 = {
    "snapshot_metrics": {"hhi": 0.8, "top_weight": 0.9},
    "normalized": {"policy_profile": "default"},
}
result2 = concentration_chain(state2)
assert result2["finding_concentration"]["severity"] == 2

print("✅ 分析链路测试通过")
```

### 集成测试

```bash
# 测试所有分析链
uv run --env-file .env -- python -u -m pytest tests/test_module5.py -v
```

**检查项：**
- [ ] 所有4个文件都已实现
- [ ] 风险等级判断正确
- [ ] 证据数据完整
- [ ] 建议文本合理

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **风险等级映射**：
   - 0: pass（无风险）
   - 1: warn（预警）
   - 2: restrict（限制）
   - 3: block（阻断，通常由合规触发）

2. **反向指标处理**：
   - 有效持仓数、成交量是"越大越好"
   - 判断逻辑需要反向：`< threshold` 而不是 `>`

3. **证据收集**：
   - 记录当前值和阈值
   - 提供计算依据

**常见错误：**
- ❌ 反向指标判断逻辑错误
- ❌ 忘记处理指标缺失的情况
- ❌ 风险摘要不够具体

**优化建议：**
- 使用辅助函数统一判断逻辑
- 风险摘要使用模板字符串
- 建议要具体可执行

**参考资源：**
- 样本答案中的 `src/chains/` 目录
- `rules.yaml` 中的阈值配置

</details>

---

## 📝 模块6: Agent 模块

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐⭐ 高级 |
| **文件数** | 3个 |
| **文件路径** | `src/agents/agent_utils.py`<br>`src/agents/macro_agent.py`<br>`src/agents/compliance_agent.py` |
| **依赖模块** | 模块1, 3, 7 |
| **被依赖** | 模块4（graph 中注册） |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] LangChain Agent 的构建方法
- [ ] 工具调用（Tool Calling）的实现
- [ ] ReAct Agent 模式
- [ ] 结构化输出的应用
- [ ] RAG 检索技术

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块实现2个 LLM Agent，使用工具调用进行智能分析。

**核心功能：**
1. **宏观 Agent**：调用 Tushare API 和文本检索，评估宏观风险
2. **合规 Agent**：使用 RAG 检索政策文本，**必须引用文档**后输出结构化合规结论

**为什么重要：**
Agent 能够处理非结构化数据和复杂推理，是系统的智能分析层。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件0：`src/agents/agent_utils.py`

**实现 4 个 Agent 共享工具函数：**

1. `extract_tool_calls(messages) -> List[Dict]`
   - 从 LangChain 消息列表中提取工具调用记录
   - 遍历 AIMessage 收集 pending 调用，遍历 ToolMessage 匹配结果
   - 返回 `[{tool, input, output, latency_ms, error}]`

2. `last_ai_content(messages) -> str`
   - 从消息列表中取最后一条 AIMessage 的 content
   - content 为 list 时 json.dumps，否则 str

3. `wrap_tool(name, fn)`
   - 用 `@tool(name)` 装饰器包装普通函数为 LangChain Tool
   - 自动记录 latency_ms 和 error 到 `result["tool_meta"]`

4. `_parse_tool_output(content) -> Any`（内部辅助）
   - 尝试 json.loads 解析字符串，失败则原样返回

### 文件1：`src/agents/macro_agent.py`

**实现宏观经济分析 Agent（约 19 个函数）：**

**工具实现层（5 个）：**
- `_macro_timeseries_impl(series, asof_date, runtime) -> dict`：调用 Tushare API 获取时序数据
- `_macro_search_impl(query, asof_date, runtime) -> dict`：关键词搜索宏观文本
- `_create_tools_with_asof_date(asof_date, runtime)`：工厂函数，用闭包绑定 asof_date 创建线程安全的工具
- `_tushare_timeseries_from_config(series, config, asof_date, runtime)`：从 macro_series.yaml 配置驱动 Tushare 调用
- `_load_macro_series_config(path_str)`：带 `@lru_cache` 加载 YAML 配置

**确定性计算层（5 个）：**
- `_prefetch_macro_timeseries(asof_date, runtime)`：预取所有时序数据
- `_compute_macro_severity(tool_results, runtime)`：基于变化率计算确定性 severity
- `_nlp_severity_from_tool_calls(tool_calls)`：从文本搜索结果的 sentiment_score 计算 NLP severity
- `_blend_severity(macro_severity, nlp_severity, runtime)`：加权混合两个 severity
- `_fallback_finding(severity) -> Finding`：降级结果

**节点函数：**
- `run_macro_agent(state, llm, config) -> Dict[str, Any]`：完整节点入口

### 文件2：`src/agents/compliance_agent.py`

**实现合规风险分析 Agent（约 25 个函数）：**

**RAG 检索层（8 个）：**
- `_get_embedding_model(runtime)`：获取 embedding 模型（text-embedding-v4 或兼容接口）
- `_embed_texts(texts, model) -> List[List[float]]`：批量文本向量化
- `_cosine_similarity(a, b) -> float`：余弦相似度计算
- `_vector_search(query, docs, model, top_k) -> List`：向量检索
- `_keyword_search(query, docs, top_k) -> List`：关键词降级检索
- `_policy_search_impl(query, asof_date, runtime) -> dict`：合规文本 RAG 检索（向量优先，关键词降级）
- `_allowlist_check_impl(codes, runtime) -> dict`：禁投清单检查
- `_create_tools_with_context(asof_date, runtime)`：工厂函数创建工具

**确定性计算层（4 个）：**
- `_compute_compliance_severity(blocklist_result, runtime) -> int`：基于禁投清单计算 severity
- `_infer_industry_from_universe(universe, runtime) -> List[str]`：从 ETF 代码推断行业
- `_fallback_finding(severity) -> Finding`：降级结果
- `_prefetch_compliance_data(state, runtime)`：预取合规数据

**节点函数：**
- `run_compliance_agent(state, llm, config) -> Dict[str, Any]`：完整节点入口
- **硬约束**：Agent 必须调用 `policy_search`，否则结果无效，降级回 fallback

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件0：`src/agents/agent_utils.py`

```python
"""Agent 共享工具函数"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Sequence, Callable

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool


def _parse_tool_output(content: Any) -> Any:
    """尝试 JSON 解析字符串，失败则原样返回"""
    # TODO: isinstance(content, str) 时尝试 json.loads
    pass


def extract_tool_calls(messages: Sequence[Any]) -> List[Dict[str, Any]]:
    """从消息列表中提取工具调用记录"""
    # TODO: 遍历 messages
    # - AIMessage: 收集 tool_calls 到 pending 字典（key=call_id）
    # - ToolMessage: 用 tool_call_id 匹配 pending，组装 {tool, input, output, latency_ms, error}
    pass


def last_ai_content(messages: Sequence[Any]) -> str:
    """取最后一条 AIMessage 的 content"""
    # TODO: reversed 遍历，找到 AIMessage 返回其 content
    # TODO: content 为 list 时 json.dumps
    pass


def wrap_tool(name: str, fn: Callable[..., Dict[str, Any]]):
    """包装普通函数为 LangChain Tool，自动记录 latency 和 error"""
    @tool(name)
    def _wrapped(*args, **kwargs) -> Dict[str, Any]:
        # TODO: 记录 start = time.monotonic()
        # TODO: try/except 调用 fn，捕获异常记录 error
        # TODO: 计算 latency_ms
        # TODO: 写入 result["tool_meta"] = {"latency_ms": ..., "error": ...}
        pass
    return _wrapped
```

### 文件1：`src/agents/macro_agent.py`

```python
"""宏观经济分析 Agent"""
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain.agents import create_agent
import tushare as ts
import yaml

from .agent_utils import extract_tool_calls, last_ai_content, wrap_tool
from ..state import RiskState, Finding
from ..tools.csv_data import macro_search_hits
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..skills_runtime import load_skill, build_system_prompt, filter_tools, validate_output

_ROOT = Path(__file__).resolve().parents[2]


def _provenance(source: str, params: dict[str, Any]) -> dict[str, Any]:
    """生成数据溯源信息（source + timestamp + params_hash）"""
    # TODO: 实现
    pass


def _macro_series_path(config: RuntimeConfig) -> Path:
    """返回 macro_series.yaml 的路径"""
    # TODO: 优先 config.macro_series_config，降级到 csv_data_dir / "macro_series.yaml"
    pass


@lru_cache(maxsize=8)
def _load_macro_series_config(path_str: str) -> dict[str, Any]:
    """加载 macro_series.yaml 配置"""
    # TODO: 读取 YAML，校验 "series" 键存在且非空
    pass


def _parse_date(value: Any) -> datetime | None:
    """解析日期字符串，支持 YYYY-MM-DD / YYYYMMDD / ISO 格式"""
    pass


def _tushare_timeseries_from_config(
    series: str, config: dict[str, Any], asof_date: str, runtime: RuntimeConfig
) -> tuple[dict[str, Any], str | None]:
    """从 Tushare API 获取时序数据（配置驱动）"""
    # TODO: 从 config 提取 api/params/fields/date_field/value_field 等
    # TODO: 调用 tushare pro_api
    # TODO: 处理 bid/ask 中间价、日期偏移、陈旧检测
    # TODO: 返回 (payload, error)
    pass


def _macro_timeseries_impl(series: str, asof_date: str, runtime: RuntimeConfig) -> dict[str, Any]:
    """工具实现：获取宏观时序数据"""
    # TODO: 加载配置，调用 _tushare_timeseries_from_config
    # TODO: 附加 provenance 信息
    pass


def _macro_search_impl(query: str, asof_date: str, runtime: RuntimeConfig) -> dict[str, Any]:
    """工具实现：搜索宏观文本"""
    # TODO: 调用 macro_search_hits(query, limit=5, asof_date=asof_date, config=runtime)
    pass


def _create_tools_with_asof_date(asof_date: str, runtime: RuntimeConfig):
    """工厂函数：用闭包绑定 asof_date 创建线程安全的工具"""
    # TODO: 定义 timeseries_impl 和 search_impl 闭包
    # TODO: 用 wrap_tool 包装并返回
    pass


def _fallback_finding(severity: int) -> Finding:
    """降级结果"""
    # TODO: 返回包含 agent/risk_type/severity/summary/metrics/evidence/recommendations 的 Finding
    pass


def _prefetch_macro_timeseries(
    asof_date: str, runtime: RuntimeConfig
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """预取所有时序数据，返回 (tool_calls, results)"""
    # TODO: 遍历 macro_series.yaml 中的所有 series
    # TODO: 逐个调用 _macro_timeseries_impl，记录 tool_calls
    pass


def _compute_macro_severity(tool_results: dict[str, Any], runtime: RuntimeConfig) -> int:
    """基于时序数据变化率计算确定性 severity"""
    # TODO: 遍历每个 series 的 values
    # TODO: 计算最近两个值的变化率（pct 或 abs 模式）
    # TODO: 与 warn_pct_change / restrict_pct_change 比较
    pass


def _nlp_severity_from_tool_calls(tool_calls: list[dict[str, Any]]) -> int | None:
    """从文本搜索结果的 sentiment_score 计算 NLP severity"""
    # TODO: 遍历 macro_search 的 tool_calls
    # TODO: 提取 hits 中的 sentiment_score
    # TODO: score >= 70 或 <= 30 → severity=2, 60-70 或 30-40 → severity=1
    pass


def _blend_severity(macro_severity: int, nlp_severity: int | None, runtime: RuntimeConfig) -> int:
    """加权混合时序 severity 和 NLP severity"""
    # TODO: nlp_severity 为 None 时直接返回 macro_severity
    # TODO: 否则 round(weight * macro + (1-weight) * nlp)，clamp 到 [0,3]
    pass


def run_macro_agent(state: RiskState, llm, config: RuntimeConfig | None = None) -> dict[str, Any]:
    """宏观 Agent 节点入口"""
    runtime = config or DEFAULT_CONFIG

    # TODO: 1. 检查 data_quality.macro.timeseries_available，不可用时返回 fallback

    # TODO: 2. 预取时序数据，计算确定性 severity
    # prefetched_calls, prefetched_results = _prefetch_macro_timeseries(asof_date, runtime)
    # macro_severity = _compute_macro_severity(prefetched_results, runtime)

    # TODO: 3. llm is None 时返回确定性结果

    # TODO: 4. 加载 Skill，创建工具，创建 Agent
    # skill = load_skill("macro-tool-calling")
    # tools = filter_tools([macro_timeseries, macro_search], skill.allowlist)
    # agent = create_agent(llm, tools, system_prompt=build_system_prompt("", skill))

    # TODO: 5. 调用 Agent，解析 JSON 输出
    # TODO: 6. validate_output 校验，失败时降级
    # TODO: 7. 计算 nlp_severity，blend_severity
    # TODO: 8. 组装 Finding，返回 {finding_macro, tool_calls_macro, llm_used_macro, ...}
    pass
```

### 文件2：`src/agents/compliance_agent.py`

```python
"""合规风险分析 Agent"""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List

from langchain.agents import create_agent

from .agent_utils import extract_tool_calls, last_ai_content, wrap_tool
from ..state import RiskState, Finding
from ..tools.csv_data import (
    compliance_search_hits,
    load_compliance_docs,
    etf_industry_map,
)
from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..skills_runtime import load_skill, build_system_prompt, filter_tools, validate_output


def _get_embedding_model(runtime: RuntimeConfig):
    """获取 embedding 模型（用于向量检索）"""
    # TODO: 根据 runtime.openai_base_url 和 runtime.embedding_model 创建模型
    # TODO: 无配置时返回 None
    pass


def _embed_texts(texts: List[str], model) -> List[List[float]]:
    """批量文本向量化"""
    # TODO: 调用 model.embed_documents(texts)
    pass


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """余弦相似度"""
    # TODO: dot(a,b) / (norm(a) * norm(b))
    pass


def _vector_search(query: str, docs: List[Dict], model, top_k: int) -> List[Dict]:
    """向量检索"""
    # TODO: embed query，计算与每个 doc 的相似度，取 top_k
    pass


def _keyword_search(query: str, docs: List[Dict], top_k: int) -> List[Dict]:
    """关键词降级检索"""
    # TODO: 调用 compliance_search_hits
    pass


def _policy_search_impl(query: str, asof_date: str, runtime: RuntimeConfig) -> dict:
    """合规文本 RAG 检索（向量优先，关键词降级）"""
    # TODO: 尝试 _vector_search，失败时降级到 _keyword_search
    # TODO: 返回 {query, hits: [{title, content, score}], provenance}
    pass


def _allowlist_check_impl(codes: List[str], runtime: RuntimeConfig) -> dict:
    """禁投清单检查"""
    # TODO: 从 rules.yaml 加载 blocklist
    # TODO: 检查 codes 中哪些在 blocklist 中
    # TODO: 返回 {blocked: [...], clean: [...], provenance}
    pass


def _create_tools_with_context(asof_date: str, runtime: RuntimeConfig):
    """工厂函数：用闭包创建工具"""
    # TODO: 类似 macro_agent 的 _create_tools_with_asof_date
    pass


def _fallback_finding(severity: int) -> Finding:
    """降级结果"""
    pass


def _compute_compliance_severity(blocklist_result: dict, runtime: RuntimeConfig) -> int:
    """基于禁投清单计算 severity"""
    # TODO: 有 blocked 项时 severity=3(block)
    pass


def run_compliance_agent(state: RiskState, llm, config: RuntimeConfig | None = None) -> dict[str, Any]:
    """合规 Agent 节点入口"""
    runtime = config or DEFAULT_CONFIG

    # TODO: 1. 检查 data_quality.compliance.text_available，不可用时返回 fallback

    # TODO: 2. 预取合规数据（禁投清单检查）

    # TODO: 3. llm is None 时返回确定性结果

    # TODO: 4. 加载 Skill，创建工具，创建 Agent
    # skill = load_skill("compliance-evidence")
    # tools = filter_tools([policy_search, allowlist_check], skill.allowlist)

    # TODO: 5. 调用 Agent，解析 JSON 输出

    # TODO: 6. 硬约束检查：Agent 必须调用 policy_search
    # if not any(call["tool"] == "policy_search" for call in tool_calls):
    #     return fallback_finding(...)

    # TODO: 7. validate_output 校验
    # TODO: 8. 组装 Finding，返回 {finding_compliance, tool_calls_compliance, ...}
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试工具函数

```python
from src.agents.macro_agent import macro_timeseries, macro_search

# 测试时序数据获取
data = macro_timeseries("SHIBOR3M", "2025-01-01", "2025-11-15")
assert data is not None

# 测试文本搜索
results = macro_search("利率政策", top_k=3)
assert len(results) <= 3

print("✅ 工具函数测试通过")
```

### 测试 Agent

```python
from src.agents.macro_agent import run_macro_agent

state = {
    "normalized": {
        "asof_date": "2025-11-14",
        "target_weights": {"159213": 0.5, "159959": 0.5},
        "policy_profile": "default",
    },
    "data_quality": {
        "macro": {"timeseries_available": True},
    },
    "snapshot_metrics": {},
}

# 无 LLM 时应返回确定性结果
result = run_macro_agent(state, llm=None)
assert "finding_macro" in result
assert result["finding_macro"]["risk_type"] == "macro"
assert result["llm_used_macro"] is False

print("✅ Agent 测试通过")
```

**检查项：**
- [ ] 工具函数正常工作
- [ ] Agent 能正确调用工具
- [ ] 输出格式符合要求
- [ ] severity 判断合理

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **工具定义**：使用 `@tool` 装饰器，提供清晰的 docstring
2. **Agent 创建**：
   ```python
   from langgraph.prebuilt import create_react_agent
   agent = create_react_agent(llm, tools=[tool1, tool2])
   ```
3. **结构化输出**：使用 Pydantic 模型或 JSON Schema 约束输出格式

**常见错误：**
- ❌ 工具 docstring 不清晰导致 LLM 误用
- ❌ 忘记处理 Agent 执行失败的情况
- ❌ 输出解析逻辑不健壮

**优化建议：**
- 使用 Skills 体系管理提示词
- 添加工具调用日志
- 设置 Agent 最大迭代次数

**参考资源：**
- [LangChain Agent 文档](https://python.langchain.com/docs/modules/agents/)
- [Tool Calling 指南](https://python.langchain.com/docs/modules/agents/tools/)
- 样本答案中的 `src/agents/` 目录

</details>

---

## 📝 模块7: Skills 体系

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐ 进阶 |
| **文件数** | 1个 Python + 配置文件 |
| **文件路径** | `src/skills_runtime.py`<br>`skills/*/SKILL.md`（已提供，无需编写）<br>`skills/*/output.schema.json`（已提供）<br>`skills/tools/tool_interfaces.yaml`（已提供）<br>`skills/snippets/*.md`（已提供） |
| **依赖模块** | 无 |
| **被依赖** | 模块4（supervisor 用 load_skill）, 模块6（Agent 用全部函数） |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 配置驱动的系统设计（SKILL.md + YAML frontmatter）
- [ ] Markdown frontmatter 解析（YAML 元数据 + 正文分离）
- [ ] `dataclass(frozen=True)` 不可变数据结构
- [ ] JSON Schema 验证（`jsonschema.Draft202012Validator`）
- [ ] 工具白名单与注册表交叉过滤
- [ ] `lru_cache` 缓存优化

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块实现 Skills 配置体系，将提示词、工具权限、输出结构做成可配置的技能包。

**核心功能：**
1. **技能加载**：从 `SKILL.md` 解析 YAML frontmatter + Markdown 正文，返回 `SkillSpec` 冻结数据类
2. **Schema 管理**：加载 `output.schema.json` 并用 `jsonschema` 校验 Agent 输出
3. **工具白名单过滤**：结合 `tool_interfaces.yaml` 注册表交叉过滤，只放行合法工具
4. **提示词构建**：拼接 base prompt + skill body + snippets + schema 约束
5. **片段加载**：从 `skills/snippets/` 加载可复用的提示词片段
6. **工具注册表**：从 `tools/tool_interfaces.yaml` 加载全局工具定义

**SKILL.md 文件格式：**
```
---
name: macro-tool-calling          # 技能名称
type: agent                       # 技能类型
inputs: [snapshot_metrics, ...]   # 输入字段
outputs: [finding_macro]          # 输出字段
tools:
  allowlist: [macro_timeseries, macro_search]  # 工具白名单
  max_calls: 3                    # 最大调用次数
  timeout_ms: 8000                # 超时时间
snippets:                         # 可复用片段引用
  - snippets/evidence_rules.md
---
# 正文部分（系统提示词）
你是 MacroToolCallingAgent，负责评估宏观经济环境...
```

**为什么重要：**
改提示词只需改 SKILL.md，不需要动 Python 代码；改工具权限只需改 allowlist，不需要改 Agent 逻辑。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件：`src/skills_runtime.py`

**数据结构：**

`SkillSpec` — 冻结数据类（`@dataclass(frozen=True)`），16 个字段：

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `name` | `str` | 技能名称 |
| `type` | `str` | 技能类型（如 `"agent"`） |
| `inputs` | `List[str]` | 输入字段列表 |
| `outputs` | `List[str]` | 输出字段列表 |
| `allowlist` | `List[str]` | 工具白名单 |
| `snippets` | `List[str]` | 片段引用路径列表 |
| `body` | `str` | SKILL.md 正文（系统提示词） |
| `schema` | `Optional[Dict]` | output.schema.json 内容 |
| `policy_version` | `str` | 策略版本 |
| `skills_hash` | `str` | 技能内容哈希（SHA256 前 16 位） |
| `max_calls` | `int` | 工具最大调用次数 |
| `timeout_ms` | `int` | 工具超时毫秒 |
| `require_evidence` | `bool` | 是否强制要求证据 |
| `evidence_prefixes` | `List[str]` | 合法证据前缀列表 |
| `limits` | `Dict[str, Any]` | 限制配置 |
| `stop_condition` | `List[str]` | 停止条件 |
| `cost_budget` | `Dict[str, Any]` | 成本预算 |

**实现函数（8 个）：**

1. `_parse_frontmatter(text: str) -> tuple[Dict, str]`（内部函数）
   - 解析 `---` 分隔的 YAML frontmatter
   - 返回 `(meta_dict, body_text)` 元组
   - 如果没有 frontmatter，返回 `({}, text)`

2. `_hash_text(text: str) -> str`（内部函数）
   - SHA256 哈希，取前 16 位十六进制

3. `load_skill(skill_dir: str) -> SkillSpec`（`@lru_cache`）
   - 读取 `skills/{skill_dir}/SKILL.md`
   - 用 `_parse_frontmatter` 解析 YAML 元数据和正文
   - 读取 `skills/{skill_dir}/output.schema.json`（如果存在）
   - 从 `meta["tools"]` 提取 allowlist / max_calls / timeout_ms / require_evidence
   - 构造并返回 `SkillSpec` 实例

4. `load_tool_registry() -> Set[str]`（`@lru_cache`）
   - 读取 `skills/tools/tool_interfaces.yaml`
   - 提取所有工具名称，返回 `Set[str]`
   - 文件不存在时返回空集合

5. `load_snippet(path: str) -> str`
   - 先尝试 `skills/{path}`，再尝试 `skills/snippets/{path}`
   - 返回文件内容（strip），找不到返回空字符串

6. `build_system_prompt(base: str, skill: SkillSpec) -> str`
   - 拼接：base + skill.body + snippets 内容 + schema 约束
   - 用 `"\n\n".join(parts).strip()` 连接
   - schema 部分格式：`"Output must conform to schema:\n" + json.dumps(schema)`

7. `filter_tools(tools: Sequence, allowlist: Sequence[str]) -> List`
   - 如果 allowlist 为空，返回全部工具
   - 用 `load_tool_registry()` 交叉过滤：只保留注册表中存在的白名单项
   - 按工具的 `name` 属性匹配

8. `validate_output(skill: SkillSpec, data: Dict) -> List[str]`
   - 如果 skill.schema 为 None 或 jsonschema 未安装，返回空列表
   - 用 `jsonschema.Draft202012Validator` 校验
   - 返回错误消息列表

**路径常量（模块级）：**
- `_ROOT`：项目根目录（`Path(__file__).resolve().parents[1]`）
- `_SKILLS_ROOT`：`_ROOT / "skills"`
- `_SNIPPETS_ROOT`：`_SKILLS_ROOT / "snippets"`
- `_TOOL_REGISTRY`：`_SKILLS_ROOT / "tools" / "tool_interfaces.yaml"`

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件：`src/skills_runtime.py`

```python
"""
Skills 运行时模块 — 配置驱动的技能加载、提示词构建、工具过滤、输出校验。
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

import yaml
import hashlib

try:
    import jsonschema
except ImportError:
    jsonschema = None


_ROOT = Path(__file__).resolve().parents[1]
_SKILLS_ROOT = _ROOT / "skills"
_SNIPPETS_ROOT = _SKILLS_ROOT / "snippets"
_TOOL_REGISTRY = _SKILLS_ROOT / "tools" / "tool_interfaces.yaml"


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SkillSpec:
    """技能规格，不可变。"""
    name: str
    type: str
    inputs: List[str]
    outputs: List[str]
    allowlist: List[str]
    snippets: List[str]
    body: str
    schema: Optional[Dict[str, Any]]
    policy_version: str
    skills_hash: str
    max_calls: int
    timeout_ms: int
    require_evidence: bool
    evidence_prefixes: List[str]
    limits: Dict[str, Any]
    stop_condition: List[str]
    cost_budget: Dict[str, Any]


# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------
def _parse_frontmatter(text: str) -> tuple[Dict[str, Any], str]:
    """解析 YAML frontmatter，返回 (meta, body)。"""
    # TODO: 检查 text 是否以 "---" 开头
    # TODO: 用 "---" 分割，取第二段做 yaml.safe_load
    # TODO: 第三段作为 body（去掉开头换行）
    # TODO: 没有 frontmatter 时返回 ({}, text)
    pass


def _hash_text(text: str) -> str:
    """SHA256 哈希，取前 16 位。"""
    # TODO: hashlib.sha256 → hexdigest()[:16]
    pass


# ---------------------------------------------------------------------------
# 核心公开函数
# ---------------------------------------------------------------------------
@lru_cache(maxsize=None)
def load_skill(skill_dir: str) -> SkillSpec:
    """加载技能配置，返回 SkillSpec。带 lru_cache 缓存。"""
    # TODO: 拼接 skill_path = _SKILLS_ROOT / skill_dir / "SKILL.md"
    # TODO: 文件不存在时 raise FileNotFoundError

    # TODO: 读取文件内容，调用 _parse_frontmatter 解析
    # raw = skill_path.read_text(encoding="utf-8")
    # meta, body = _parse_frontmatter(raw)

    # TODO: 加载 output.schema.json（如果存在）
    # schema_path = _SKILLS_ROOT / skill_dir / "output.schema.json"

    # TODO: 从 meta["tools"] 提取工具配置
    # tools_meta = meta.get("tools") or {}
    # allowlist = list(tools_meta.get("allowlist") or meta.get("allowlist") or [])
    # max_calls = int(tools_meta.get("max_calls") or 0)
    # timeout_ms = int(tools_meta.get("timeout_ms") or 0)
    # require_evidence = bool(tools_meta.get("require_evidence") or False)

    # TODO: 提取其他字段：evidence_prefixes, limits, stop_condition, cost_budget, policy_version
    # TODO: 计算 skills_hash（优先用 meta 中的值，否则 _hash_text(raw)）

    # TODO: 构造并返回 SkillSpec(name=..., type=..., ...)
    pass


@lru_cache(maxsize=None)
def load_tool_registry() -> Set[str]:
    """从 tool_interfaces.yaml 加载全局工具注册表。"""
    # TODO: 如果 _TOOL_REGISTRY 不存在，返回 set()
    # TODO: yaml.safe_load 读取，提取 tools[].name
    # TODO: 返回 Set[str]
    pass


def load_snippet(path: str) -> str:
    """加载可复用提示词片段。"""
    # TODO: 先尝试 _SKILLS_ROOT / path
    # TODO: 再尝试 _SNIPPETS_ROOT / path
    # TODO: 返回 strip() 后的内容，找不到返回 ""
    pass


def build_system_prompt(base: str, skill: SkillSpec) -> str:
    """拼接系统提示词：base + skill.body + snippets + schema。"""
    # TODO: parts = [base]
    # TODO: 如果 skill.body 非空，追加
    # TODO: 遍历 skill.snippets，load_snippet 并追加
    # TODO: 如果 skill.schema 非 None，追加 schema 约束文本
    # TODO: return "\n\n".join(parts).strip()
    pass


def filter_tools(tools: Sequence[Any], allowlist: Sequence[str]) -> List[Any]:
    """按白名单过滤工具列表，与注册表交叉验证。"""
    # TODO: allow = set(allowlist or [])
    # TODO: 如果 allow 为空，返回 list(tools)
    # TODO: 加载 registry = load_tool_registry()
    # TODO: 如果 registry 非空，allow 只保留 registry 中存在的
    # TODO: 遍历 tools，按 name 属性匹配
    pass


def validate_output(skill: SkillSpec, data: Dict[str, Any]) -> List[str]:
    """用 JSON Schema 校验 Agent 输出，返回错误列表。"""
    # TODO: 如果 skill.schema 为 None 或 jsonschema 未安装，返回 []
    # TODO: 用 jsonschema.Draft202012Validator 校验
    # TODO: 收集 iter_errors 的 message 列表
    pass
```

### 参考：`skills/macro-tool-calling/SKILL.md`（已提供，无需编写）

```markdown
---
name: macro-tool-calling
description: 宏观工具调用代理，结合时序与文本生成宏观风险结论
type: agent
inputs:
  - snapshot_metrics
  - data_quality
  - tool_results
outputs:
  - finding_macro
policy_version: "local-default"
skills_hash: ""
evidence_prefixes:
  - snapshot_metrics.
  - rules.
  - "tool:"
tools:
  allowlist:
    - macro_timeseries
    - macro_search
  max_calls: 3
  timeout_ms: 8000
  require_evidence: false
limits:
  max_retries: 1
cost_budget:
  llm_tokens: 1200
  tool_calls: 3
snippets:
  - snippets/evidence_rules.md
---

# MacroToolCallingAgent 系统提示词

你是 MacroToolCallingAgent，负责评估宏观经济环境对投资组合的影响。
...（正文即系统提示词，由 build_system_prompt 拼接到 Agent）
```

> **注意**：`skills/` 目录下的所有配置文件（SKILL.md、output.schema.json、tool_interfaces.yaml、snippets/）均已提供，你只需实现 `src/skills_runtime.py` 来解析和使用它们。

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试1：SkillSpec 数据结构

```python
from src.skills_runtime import load_skill, SkillSpec

skill = load_skill("macro-tool-calling")
assert isinstance(skill, SkillSpec)
assert skill.name == "macro-tool-calling"
assert skill.type == "agent"
assert "macro_timeseries" in skill.allowlist
assert "macro_search" in skill.allowlist
assert skill.max_calls == 3
assert skill.timeout_ms == 8000
assert len(skill.body) > 0  # 正文非空

print("✅ SkillSpec 数据结构测试通过")
```

### 测试2：frontmatter 解析

```python
from src.skills_runtime import _parse_frontmatter

text = "---\nname: test\ntype: agent\n---\n\n# Body here"
meta, body = _parse_frontmatter(text)
assert meta["name"] == "test"
assert meta["type"] == "agent"
assert "Body here" in body

# 无 frontmatter
meta2, body2 = _parse_frontmatter("plain text")
assert meta2 == {}
assert body2 == "plain text"

print("✅ frontmatter 解析测试通过")
```

### 测试3：build_system_prompt 拼接

```python
from src.skills_runtime import load_skill, build_system_prompt

skill = load_skill("macro-tool-calling")
prompt = build_system_prompt("Base prompt.", skill)
assert "Base prompt." in prompt
assert "MacroToolCallingAgent" in prompt  # skill.body 内容
# 如果有 snippets，也会被拼接进去
if skill.snippets:
    assert "证据" in prompt  # evidence_rules.md 内容

print("✅ build_system_prompt 测试通过")
```

### 测试4：filter_tools 白名单过滤

```python
from src.skills_runtime import filter_tools

class FakeTool:
    def __init__(self, name):
        self.name = name

tools = [FakeTool("macro_timeseries"), FakeTool("macro_search"), FakeTool("unknown")]
filtered = filter_tools(tools, ["macro_timeseries", "macro_search"])
assert len(filtered) <= 2
names = [t.name for t in filtered]
assert "unknown" not in names

# 空白名单返回全部
all_tools = filter_tools(tools, [])
assert len(all_tools) == 3

print("✅ filter_tools 测试通过")
```

### 测试5：validate_output Schema 校验

```python
from src.skills_runtime import load_skill, validate_output

skill = load_skill("macro-tool-calling")
# 合法输出
valid = {"severity": 1, "summary": "test", "evidence": []}
errors = validate_output(skill, valid)
assert errors == []

# 非法输出（缺少 required 字段）
invalid = {"severity": "not_int"}
errors = validate_output(skill, invalid)
assert len(errors) > 0

print("✅ validate_output 测试通过")
```

**检查项：**
- [ ] `load_skill` 返回 `SkillSpec` 实例（非 dict）
- [ ] frontmatter 正确解析 YAML 元数据和正文
- [ ] `build_system_prompt` 拼接 base + body + snippets + schema
- [ ] `filter_tools` 空白名单返回全部，非空时按名称过滤
- [ ] `validate_output` 用 JSON Schema 校验，返回错误列表
- [ ] `load_skill` 有 `lru_cache` 缓存

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **Frontmatter 解析**：用 `text.split("---", 2)` 分割，第二段 `yaml.safe_load`，第三段是正文
2. **`@dataclass(frozen=True)`**：SkillSpec 创建后不可修改，保证线程安全
3. **`@lru_cache(maxsize=None)`**：`load_skill` 和 `load_tool_registry` 都用缓存，同一 skill 只解析一次
4. **工具注册表交叉过滤**：`filter_tools` 不是只看白名单，还要和 `tool_interfaces.yaml` 交叉验证
5. **Schema 校验**：用 `Draft202012Validator`（不是 `validate`），通过 `iter_errors` 收集所有错误

**常见错误：**
- ❌ `load_skill` 返回 dict 而非 SkillSpec — 调用方用 `skill.allowlist` 属性访问
- ❌ 忘记处理 `meta.get("tools")` 嵌套结构 — allowlist 在 `tools.allowlist` 下
- ❌ `filter_tools` 空白名单时过滤掉所有工具 — 应该返回全部
- ❌ `jsonschema` 未安装时报错 — 应该 `try/except ImportError` 并返回空列表

**参考资源：**
- `skills/macro-tool-calling/SKILL.md` — 实际的 frontmatter 格式
- `skills/tools/tool_interfaces.yaml` — 工具注册表格式
- `skills/macro-tool-calling/output.schema.json` — Schema 格式

</details>

---



## 📝 模块8: 规则与约束

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐ 中级 |
| **文件数** | 2个 |
| **文件路径** | `src/tools/rules.py`<br>`src/tools/constraints.py` |
| **依赖模块** | 模块1, 3, 10 |
| **被依赖** | 模块5, 6, 9 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] YAML 配置文件处理
- [ ] 规则引擎设计
- [ ] 约束评估逻辑
- [ ] 硬约束与软约束的区分

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块负责加载规则配置并评估约束违规情况。

**核心功能：**
1. **规则加载**：从 YAML 文件读取规则配置
2. **约束评估**：检查指标是否违反阈值
3. **约束分类**：区分 hard 和 soft 约束

**为什么重要：**
规则引擎是确定性决策的基础，约束评估直接影响决策结果。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/tools/rules.py`

**模块级常量：**
- `_DEFAULT_RULES`：内置默认规则（default + conservative 两个 profile），当 rules.yaml 不存在时使用
- `_ROOT`：项目根目录

**实现函数（4 个）：**

1. `_rules_path(config) -> Path`（内部函数）
   - 如果 `config.csv_data_dir` 有值，返回 `csv_data_dir / "rules.yaml"`
   - 否则返回 `项目根目录 / "cufel_practice_data" / "rules.yaml"`

2. `_load_rules_cached(profile: str, path_str: str) -> Tuple[Dict, str]`（`@lru_cache`）
   - 读取 YAML 文件，按 profile 取规则
   - 如果指定 profile 不存在，回退到 `"default"`
   - 如果文件不存在，回退到 `_DEFAULT_RULES`
   - 返回 `(rules_dict, version_string)`，version 为 `"rules.yaml"` 或 `"local-default"`

3. `load_rules(profile: str, config) -> Tuple[Dict, str]`
   - 调用 `_rules_path` 和 `_load_rules_cached`
   - 返回 `(dict(rules), version)` — 注意返回的是**元组**，不是单个 dict

4. `get_blocklist(profile: str, config) -> Tuple[list, str]`
   - 调用 `load_rules` 提取 `rules["blocklist"]`
   - 返回 `(blocklist, version)` — 同样是元组

### 文件2：`src/tools/constraints.py`

**模块级常量：**
- `_LEVEL`：severity 到数值的映射 `{"pass": 0, "warn": 1, "restrict": 2, "block": 3}`

**实现函数（1 个主函数 + 5 个内部辅助）：**

`constraints_evaluator(state: RiskState, config) -> Dict[str, Any]`

返回 `{"rule_findings": findings}`，其中 findings 是一个列表，每项包含：

| 字段 | 类型 | 说明 |
|:---|:---|:---|
| `rule_id` | `str` | 规则标识（如 `"max_single_weight"`） |
| `severity` | `str` | `"warn"` / `"restrict"` / `"block"` |
| `level` | `int` | severity 对应的数值 |
| `metric` | `str` | 指标名称 |
| `value` | `float` | 当前值 |
| `limit` | `float` | 阈值 |
| `message` | `str` | 描述信息 |
| `evidence` | `list` | 证据引用 |

**评估的规则（10 条）：**
1. `max_single_weight` — top_weight 超上限 → restrict
2. `max_hhi` — hhi 超上限 → warn
3. `max_portfolio_volatility` — 波动率超上限 → restrict
4. `max_weighted_spread_bps` — 价差超上限 → warn
5. `min_weighted_adv` — ADV 低于下限 → warn（反向指标）
6. `max_turnover` — 换手率超上限 → warn
7. `max_position_delta` — 单一仓位变动超上限 → warn
8. `max_adv_ratio` — 交易量/ADV 比超上限 → warn
9. `max_delta_hhi` / `max_delta_volatility` — 增量指标超上限 → warn
10. `blocklist` — 禁投清单命中 → **block**（最严格）

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/rules.py`

```python
"""
规则加载与管理模块 — 从 rules.yaml 加载阈值配置，支持多 profile。
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Tuple

import yaml

from ..config import RuntimeConfig, DEFAULT_CONFIG


# ---------------------------------------------------------------------------
# 内置默认规则（rules.yaml 不存在时的 fallback）
# ---------------------------------------------------------------------------
_DEFAULT_RULES: Dict[str, Dict[str, Any]] = {
    "default": {
        "max_single_weight": 0.4,
        "max_hhi": 0.3,
        "max_portfolio_volatility": 0.24,
        "max_weighted_spread_bps": 50,
        "min_weighted_adv": 3000000,
        "blocklist": ["CCC"],
    },
    "conservative": {
        "max_single_weight": 0.3,
        "max_hhi": 0.25,
        "max_portfolio_volatility": 0.2,
        "max_weighted_spread_bps": 40,
        "min_weighted_adv": 5000000,
        "blocklist": ["CCC"],
    },
}

_ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# 路径与缓存
# ---------------------------------------------------------------------------
def _rules_path(config: RuntimeConfig | None = None) -> Path:
    """根据配置返回 rules.yaml 路径。"""
    # TODO: 如果 config.csv_data_dir 有值，返回 csv_data_dir / "rules.yaml"
    # TODO: 否则返回 _ROOT / "cufel_practice_data" / "rules.yaml"
    pass


@lru_cache(maxsize=32)
def _load_rules_cached(profile: str, path_str: str) -> Tuple[Dict[str, Any], str]:
    """带缓存的规则加载（path_str 用于 cache key）。"""
    # TODO: path = Path(path_str)
    # TODO: 如果文件存在，yaml.safe_load 读取
    # TODO: 按 profile 取规则，profile 不存在则回退 "default"
    # TODO: 文件不存在时回退 _DEFAULT_RULES
    # TODO: 返回 (rules_dict, version)，version 为 "rules.yaml" 或 "local-default"
    pass


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------
def load_rules(profile: str, config: RuntimeConfig | None = None) -> Tuple[Dict[str, Any], str]:
    """加载规则配置，返回 (rules, version) 元组。"""
    # TODO: 调用 _rules_path 和 _load_rules_cached
    # TODO: 返回 dict(rules), version — 注意拷贝一份避免缓存被修改
    pass


def get_blocklist(profile: str, config: RuntimeConfig | None = None) -> Tuple[list, str]:
    """提取禁投清单，返回 (blocklist, version) 元组。"""
    # TODO: 调用 load_rules，提取 rules["blocklist"]
    pass
```

### 文件2：`src/tools/constraints.py`

```python
"""
约束评估模块 — 逐条检查规则阈值，生成 rule_findings 列表。
"""
from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState
from ..config import RuntimeConfig, DEFAULT_CONFIG
from .rules import load_rules


_LEVEL = {"pass": 0, "warn": 1, "restrict": 2, "block": 3}


def constraints_evaluator(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """评估所有规则约束，返回 {"rule_findings": [...]}。"""
    cfg = config or DEFAULT_CONFIG
    normalized = state.get("normalized") or {}
    metrics = state.get("snapshot_metrics") or {}

    rules, _ = load_rules(normalized.get("policy_profile", "default"), cfg)

    findings: List[Dict[str, Any]] = []

    # --- 内部辅助函数 ---
    def add(rule_id: str, severity: str, metric: str,
            value: float, limit: float, message: str) -> None:
        """添加一条违规记录。"""
        # TODO: 构造 finding dict，包含 rule_id, severity, level, metric, value, limit, message, evidence
        # TODO: level = _LEVEL.get(severity, 0)
        # TODO: evidence = [{"ref": f"snapshot_metrics.{metric}", "value": value}]
        pass

    def _get_float(mapping: Dict[str, Any], key: str, default: float) -> float:
        # TODO: 安全地从 mapping 取 float 值
        pass

    def _metric(key: str) -> float:
        # TODO: 从 metrics 取指标值
        pass

    def _rule(key: str, default: float) -> float:
        # TODO: 从 rules 取阈值
        pass

    def _check_max(rule_id: str, metric_key: str, limit: float,
                   severity: str, message: str) -> None:
        """检查指标是否超过上限。"""
        # TODO: value = _metric(metric_key)
        # TODO: if value > limit: add(...)
        pass

    def _check_min(rule_id: str, metric_key: str, limit: float,
                   severity: str, message: str) -> None:
        """检查指标是否低于下限（反向指标）。"""
        # TODO: value = _metric(metric_key)
        # TODO: if limit > 0 and value < limit: add(...)
        pass

    # --- 逐条评估规则 ---
    # TODO: _check_max("max_single_weight", "top_weight", ..., "restrict", ...)
    # TODO: _check_max("max_hhi", "hhi", ..., "warn", ...)
    # TODO: _check_max("max_portfolio_volatility", "portfolio_volatility", ..., "restrict", ...)
    # TODO: _check_max("max_weighted_spread_bps", "weighted_spread_bps", ..., "warn", ...)
    # TODO: _check_min("min_weighted_adv", "weighted_adv", ..., "warn", ...)
    # TODO: _check_max("max_turnover", "turnover", ..., "warn", ...)
    # TODO: _check_max("max_position_delta", "max_position_delta", ..., "warn", ...)

    # TODO: 特殊处理 max_adv_ratio（metrics 中可能为 None）

    # TODO: _check_max("max_delta_hhi", "delta_hhi", ..., "warn", ...)
    # TODO: _check_max("max_delta_volatility", "delta_portfolio_volatility", ..., "warn", ...)

    # TODO: 禁投清单检查 → severity = "block"
    # blocklist = set(state.get("compliance_blocklist") or rules.get("blocklist") or [])
    # blocked = [c for c, w in target_weights.items() if c in blocklist and w > 0]

    return {"rule_findings": findings}
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试1：规则加载（返回元组）

```python
from src.tools.rules import load_rules, get_blocklist

rules, version = load_rules("default")
assert isinstance(rules, dict)
assert isinstance(version, str)
assert version in ("rules.yaml", "local-default")
assert "max_single_weight" in rules or "blocklist" in rules

# conservative profile
rules_c, _ = load_rules("conservative")
assert isinstance(rules_c, dict)

print("✅ 规则加载测试通过")
```

### 测试2：禁投清单

```python
from src.tools.rules import get_blocklist

blocklist, version = get_blocklist("default")
assert isinstance(blocklist, list)
assert "CCC" in blocklist  # 默认规则中有 CCC

print("✅ 禁投清单测试通过")
```

### 测试3：约束评估

```python
from src.tools.constraints import constraints_evaluator

state = {
    "normalized": {"policy_profile": "default", "target_weights": {"AAA": 0.9, "BBB": 0.1}},
    "snapshot_metrics": {
        "top_weight": 0.9,
        "hhi": 0.82,
        "portfolio_volatility": 0.03,
        "weighted_spread_bps": 300,
        "weighted_adv": 1000,
        "turnover": 0.1,
        "max_position_delta": 0.1,
        "delta_hhi": 0.01,
        "delta_portfolio_volatility": 0.001,
    },
}

result = constraints_evaluator(state)
assert "rule_findings" in result
findings = result["rule_findings"]
assert isinstance(findings, list)
# top_weight=0.9 应该触发 max_single_weight
rule_ids = [f["rule_id"] for f in findings]
assert "max_single_weight" in rule_ids

print("✅ 约束评估测试通过")
```

### 测试4：禁投清单触发 block

```python
from src.tools.constraints import constraints_evaluator

state = {
    "normalized": {"policy_profile": "default", "target_weights": {"CCC": 0.5, "BBB": 0.5}},
    "snapshot_metrics": {"top_weight": 0.5, "hhi": 0.5},
}

result = constraints_evaluator(state)
findings = result["rule_findings"]
block_findings = [f for f in findings if f["severity"] == "block"]
assert len(block_findings) > 0  # CCC 在禁投清单中

print("✅ 禁投清单 block 测试通过")
```

**检查项：**
- [ ] `load_rules` 返回 `(dict, str)` 元组，不是单个 dict
- [ ] `_load_rules_cached` 有 `@lru_cache` 缓存
- [ ] `constraints_evaluator` 返回 `{"rule_findings": [...]}`，不是修改 state
- [ ] 禁投清单命中时 severity 为 `"block"`
- [ ] 反向指标（min_weighted_adv）用 `<` 判断

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **返回值是元组**：`load_rules` 返回 `(rules, version)`，不是单个 dict
2. **`@lru_cache` 缓存**：`_load_rules_cached` 用 `path_str`（字符串）做 cache key，不能用 Path 对象
3. **内部辅助函数模式**：`constraints_evaluator` 内部定义 `add`、`_check_max`、`_check_min` 等闭包，共享 `findings` 列表
4. **反向指标**：`min_weighted_adv` 用 `_check_min`（value < limit 时触发），其他都用 `_check_max`
5. **禁投清单来源**：优先用 `state["compliance_blocklist"]`（合规 Agent 输出），回退到 `rules["blocklist"]`

**常见错误：**
- ❌ `load_rules` 返回 dict 而非元组 — 调用方用 `rules, version = load_rules(...)` 解包
- ❌ `constraints_evaluator` 修改并返回 state — 应该返回 `{"rule_findings": findings}`
- ❌ 忘记处理 `max_adv_ratio` 为 None 的情况（metrics 中可能不存在）

**参考资源：**
- `cufel_practice_data/rules.yaml` — 实际的阈值配置（蒙特卡洛校准生成）
- `src/chains/common.py` 中的 `load_rules_cached` — 分析链路也用了规则加载

</details>

---

## 📝 模块9: 决策与审计

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐ 中级 |
| **文件数** | 4个 |
| **文件路径** | `src/chains/reducer.py`<br>`src/tools/decision.py`<br>`src/tools/solver.py`<br>`src/tools/audit.py` |
| **依赖模块** | 模块1, 5, 6, 8 |
| **被依赖** | 无 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 多源数据汇总技术
- [ ] 决策引擎设计模式
- [ ] CVXPY 约束优化
- [ ] 审计日志设计

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块是系统的决策输出层，负责汇总分析结果并给出最终决策。

**核心功能：**
1. **结果汇总**：整合所有分析节点的输出
2. **决策引擎**：基于规则和风险报告给出决策
3. **约束求解**：在 restrict 情况下生成调仓建议
4. **审计日志**：记录完整的决策过程

**为什么重要：**
决策层是系统的最终输出，直接影响用户的交易决策。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/chains/reducer.py`

**模块级常量：**
- `_DEFAULT_EVIDENCE_PREFIXES`：默认合法证据前缀 `("snapshot_metrics.", "rules.", "tool:")`
- `_FINDING_KEYS`：6 个 finding 字段名元组
- `_AGENT_SKILLS`：Agent 名称到 skill 目录的映射

**实现函数（3 个）：**

1. `_is_allowed_ref(ref, prefixes) -> bool`（内部函数）
   - 检查证据引用是否以合法前缀开头

2. `_sanitize_evidence(state, evidence, gaps, prefixes) -> List[Dict]`（内部函数）
   - 过滤非法证据引用，记录到 gaps
   - 对 `snapshot_metrics.*` 引用，从 state 中补充实际值

3. `reducer_chain(state: RiskState) -> Dict[str, Any]`
   - 收集 6 个 `finding_*` 字段
   - 对每个 finding，加载对应 skill 的 `evidence_prefixes` 做证据清洗
   - 如果 skill 要求 `require_evidence`，检查证据是否有效
   - 计算 `overall_severity`（所有 finding 中最大值）
   - 返回 `{"findings": [...], "risk_report": {...}, "data_gaps": [...]}`

### 文件2：`src/tools/decision.py`

**模块级常量：**
- `_LEVEL`：`{"pass": 0, "warn": 1, "restrict": 2, "block": 3}`

**实现函数（2 个）：**

1. `_max_level(findings) -> int`（内部函数）
   - 从 rule_findings 列表中取最大 level 值

2. `decision_engine(state: RiskState) -> Dict[str, Any]`
   - 决策逻辑（两层）：
     - `rule_level >= 3` → block
     - `rule_level >= 2` → restrict
     - `report_level >= 2` → restrict
     - `report_level >= 1` 或 data_quality degraded → warn
     - 否则 → pass
   - 提取 binding_constraints（severity 为 restrict/block 的规则）
   - 返回 `{"decision": {...}, "binding_constraints": [...]}`

### 文件3：`src/tools/solver.py`

**实现函数（6 个）：**

1. `_strip_cash(weights, cash_symbol) -> Dict`（内部）
2. `_cap_and_fill(weights, cap, cash_symbol) -> Dict`（内部）— 单一仓位封顶，超额重分配
3. `_blend_equal(weights, alpha) -> Dict`（内部）— 向等权混合
4. `_limit_holdings(weights, max_holdings, cash_symbol) -> Tuple[Dict, bool]`（内部）— 限制持仓数
5. `_adjust_weights(target, profile, drivers, config) -> Tuple[Dict, List[str]]`（内部）— 启发式调整
6. `_solve_lp(target, current, profile, adv_by_symbol, aum, config) -> Optional[Dict]`（内部）— CVXPY 线性规划

7. `constraint_solver(state: RiskState, config) -> Dict[str, Any]`
   - 仅在 `decision == "restrict"` 时运行
   - 优先用 LP 求解，失败则用启发式调整
   - 返回 `{"recommended_actions": [...]}`

### 文件4：`src/tools/audit.py`

**实现函数（2 个）：**

1. `_hash_payload(payload) -> str`（内部）— SHA256 前 16 位

2. `audit_log(state: RiskState, config) -> Dict[str, Any]`
   - 汇总审计信息：
     - 规则快照 + 哈希
     - 工具调用统计（count / errors / latency）
     - LLM 使用情况
     - Gatekeeper / Supervisor 调度信息
     - Skills 版本信息（从 load_skill 获取）
     - 合规禁投清单
     - trace_id + timestamp
   - 返回 `{"audit": {...}}`

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/chains/reducer.py`

```python
"""
结果汇总模块 — 收集所有 finding，清洗证据，生成 risk_report。
"""
from __future__ import annotations

from typing import Dict, Any, List

from ..state import RiskState, Finding
from ..skills_runtime import load_skill


_DEFAULT_EVIDENCE_PREFIXES = ("snapshot_metrics.", "rules.", "tool:")
_FINDING_KEYS = (
    "finding_market", "finding_concentration", "finding_diversification",
    "finding_liquidity", "finding_macro", "finding_compliance",
)
_AGENT_SKILLS = {
    "MarketRiskChain": "risk-market-assessor",
    "ConcentrationChain": "risk-market-assessor",
    "DiversificationChain": "risk-market-assessor",
    "LiquidityChain": "liquidity-execution-assessor",
    "MacroToolCallingAgent": "macro-tool-calling",
    "ComplianceToolCallingAgent": "compliance-evidence",
}


def _is_allowed_ref(ref: str, prefixes: tuple[str, ...]) -> bool:
    """检查证据引用前缀是否合法。"""
    # TODO: return any(ref.startswith(p) for p in prefixes)
    pass


def _sanitize_evidence(
    state: RiskState,
    evidence: List[Dict[str, Any]],
    gaps: List[Dict[str, Any]],
    prefixes: tuple[str, ...],
) -> List[Dict[str, Any]]:
    """过滤非法证据引用，对 snapshot_metrics.* 补充实际值。"""
    # TODO: 遍历 evidence，检查 ref 前缀
    # TODO: 非法引用记录到 gaps，合法引用保留
    # TODO: snapshot_metrics.* 引用从 state 中补充 value
    pass


def reducer_chain(state: RiskState) -> Dict[str, Any]:
    """汇总所有分析结果，生成 risk_report。"""
    findings: List[Finding] = []
    evidence_gaps: List[Dict[str, Any]] = []

    # TODO: 遍历 _FINDING_KEYS，从 state 收集 finding
    # TODO: 对每个 finding，查 _AGENT_SKILLS 找到对应 skill
    # TODO: 用 load_skill 加载 skill，取 evidence_prefixes
    # TODO: 调用 _sanitize_evidence 清洗证据
    # TODO: 如果 skill.require_evidence，检查证据是否有效

    # TODO: 计算 overall_severity = max(所有 finding 的 severity)
    # TODO: 生成 summary

    # TODO: 构造 risk_report
    # report = {
    #     "overall_severity": overall,
    #     "summary": summary,
    #     "findings": findings,
    #     "data_gaps": (state.get("data_gaps") or []) + evidence_gaps,
    # }

    # TODO: return {"findings": findings, "risk_report": report, "data_gaps": report["data_gaps"]}
    pass
```

### 文件2：`src/tools/decision.py`

```python
"""
决策引擎模块 — 硬规则优先，风险报告兜底，输出 pass/warn/restrict/block。
"""
from __future__ import annotations

from typing import Any, Dict, List

from ..state import RiskState


_LEVEL = {"pass": 0, "warn": 1, "restrict": 2, "block": 3}


def _max_level(findings: List[Dict[str, Any]]) -> int:
    """从 rule_findings 中取最大 level。"""
    # TODO: 遍历 findings，取 f["level"]（或从 f["severity"] 映射）
    # TODO: 返回 max(levels)，空列表返回 0
    pass


def decision_engine(state: RiskState) -> Dict[str, Any]:
    """决策引擎：硬规则优先，风险报告兜底。"""
    rule_findings = state.get("rule_findings") or []
    risk_report = state.get("risk_report") or {}
    data_quality = state.get("data_quality") or {}

    rule_level = _max_level(rule_findings)
    report_level = int(risk_report.get("overall_severity") or 0)

    # TODO: 决策逻辑
    # if rule_level >= 3: decision = "block"
    # elif rule_level >= 2: decision = "restrict"
    # elif report_level >= 2: decision = "restrict"
    # elif report_level >= 1 or data_quality.get("status") == "degraded": decision = "warn"
    # else: decision = "pass"

    # TODO: 提取 binding_constraints（severity 为 restrict/block 的规则）

    # TODO: return {"decision": {...}, "binding_constraints": [...]}
    pass
```

### 文件3：`src/tools/solver.py`

```python
"""
约束求解器模块 — LP 优先，启发式兜底，仅在 restrict 时运行。
"""
from __future__ import annotations

from typing import Dict, Any, List, Tuple, Optional

try:
    import cvxpy as cp
except ImportError:
    cp = None

from ..config import RuntimeConfig, DEFAULT_CONFIG
from ..state import RiskState
from .rules import load_rules
from .utils import normalize_weights, compute_hhi, compute_effective_n


# ---------------------------------------------------------------------------
# 启发式辅助函数
# ---------------------------------------------------------------------------
def _strip_cash(weights: Dict[str, float], cash_symbol: str) -> Dict[str, float]:
    """去掉现金仓位。"""
    # TODO: 过滤掉 cash_symbol
    pass


def _cap_and_fill(weights: Dict[str, float], cap: float, cash_symbol: str) -> Dict[str, float]:
    """单一仓位封顶，超额重分配给未满仓位，剩余归现金。"""
    # TODO: 遍历 weights，超过 cap 的截断
    # TODO: 超额部分按容量比例分配给未满仓位
    # TODO: 分配不完的归 cash_symbol
    pass


def _blend_equal(weights: Dict[str, float], alpha: float) -> Dict[str, float]:
    """向等权混合：(1-alpha)*原权重 + alpha*等权。"""
    # TODO: equal = 1/n
    # TODO: 返回混合后的权重
    pass


def _limit_holdings(
    weights: Dict[str, float], max_holdings: Optional[int], cash_symbol: str
) -> Tuple[Dict[str, float], bool]:
    """限制持仓数量，保留权重最大的 top-N，其余归零后重新归一化。"""
    # TODO: 如果 max_holdings 无效或持仓数未超限，直接返回
    # TODO: 否则取 top-N，normalize_weights
    pass


def _adjust_weights(
    target_weights: Dict[str, float],
    profile: Dict[str, Any],
    drivers: List[str],
    config: RuntimeConfig,
) -> Tuple[Dict[str, float], List[str]]:
    """启发式调整：封顶 + 分散化。"""
    # TODO: 先 _cap_and_fill
    # TODO: 如果 drivers 包含 concentration/diversification，尝试 _blend_equal
    # TODO: 返回 (adjusted, notes)
    pass


# ---------------------------------------------------------------------------
# CVXPY 线性规划
# ---------------------------------------------------------------------------
def _solve_lp(
    target_weights: Dict[str, float],
    current_weights: Dict[str, float],
    profile: Dict[str, Any],
    adv_by_symbol: Dict[str, float],
    aum: Optional[float],
    config: RuntimeConfig,
) -> Optional[Dict[str, float]]:
    """用 CVXPY 求解约束优化问题。"""
    if cp is None:
        return None

    # TODO: 构建决策变量 w = cp.Variable(n)
    # TODO: 约束：w >= 0, sum(w) == 1, w <= max_single_weight
    # TODO: 约束：turnover <= max_turnover, position_delta <= max_position_delta
    # TODO: 约束：adv_ratio 限制
    # TODO: 目标函数：Minimize(|w - target| + turnover_weight * |w - current|)
    # TODO: problem.solve()
    # TODO: 返回权重字典，求解失败返回 None
    pass


# ---------------------------------------------------------------------------
# 主函数
# ---------------------------------------------------------------------------
def constraint_solver(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """在 restrict 情况下生成调仓建议（LP 优先，启发式兜底）。"""
    cfg = config or DEFAULT_CONFIG
    decision = (state.get("decision") or {}).get("decision")
    if decision != "restrict":
        return {}

    # TODO: 从 state 提取 target_weights, current_weights, rules, aum 等
    # TODO: 从 risk_report 提取 drivers（severity >= 2 的风险类型）

    # TODO: 先尝试 _solve_lp
    # TODO: LP 成功则 _limit_holdings 后返回 rebalance action
    # TODO: LP 失败则 _adjust_weights 启发式调整
    # TODO: 都失败则返回 review_targets guidance

    pass
```

### 文件4：`src/tools/audit.py`

```python
"""
审计日志模块 — 汇总规则快照、工具调用、技能版本等审计信息。
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict

from ..state import RiskState
from ..skills_runtime import load_skill
from .rules import load_rules
from ..config import RuntimeConfig, DEFAULT_CONFIG


def _hash_payload(payload: Dict[str, Any]) -> str:
    """JSON 序列化后 SHA256 取前 16 位。"""
    # TODO: json.dumps(payload, sort_keys=True, separators=(",", ":"))
    # TODO: hashlib.sha256 → hexdigest()[:16]
    pass


def audit_log(state: RiskState, config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """汇总审计信息，返回 {"audit": {...}}。"""
    runtime = config or DEFAULT_CONFIG

    # TODO: 从 state 提取基础信息
    # snapshot = state.get("snapshot_metrics") or {}
    # rule_findings = state.get("rule_findings") or []
    # profile = (state.get("normalized") or {}).get("policy_profile", "default")

    # TODO: 加载规则快照
    # rules, ruleset_version = load_rules(profile, runtime)

    # TODO: 汇总工具调用（macro + compliance）
    # tool_calls = []
    # tool_calls.extend(state.get("tool_calls_macro") or [])
    # tool_calls.extend(state.get("tool_calls_compliance") or [])
    # tool_latency = sum(t.get("latency_ms", 0) for t in tool_calls)
    # tool_error_count = sum(1 for t in tool_calls if t.get("error"))

    # TODO: 检查 LLM 使用情况
    # llm_used = bool(state.get("llm_used_macro") or ...)
    # models = [state.get(key) for key in ("llm_model_macro", ...) if state.get(key)]

    # TODO: 收集 skills 版本信息
    # skill_map = {"finding_market": "risk-market-assessor", ...}
    # 遍历 skill_map，对有 finding 的 skill 调用 load_skill 获取版本

    # TODO: 构造 audit dict，包含：
    # - policy_profile, ruleset_version, rules_snapshot, rules_snapshot_hash
    # - data_snapshot_hash
    # - tool_calls, tool_call_summary (count/errors/total_latency_ms)
    # - llm_used, llm_model
    # - gatekeeper_used, gatekeeper_rationale, candidate_nodes
    # - supervisor_used, supervisor_rationale, nodes_to_run
    # - skills_used, node_outputs
    # - timestamp (UTC ISO), trace_id (_hash_payload)

    # TODO: 可选：添加 compliance_blocklist 相关信息

    # TODO: return {"audit": audit}
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试1：Reducer 汇总

```python
from src.chains.reducer import reducer_chain

state = {
    "finding_market": {"agent": "MarketRiskChain", "severity": 1, "summary": "ok", "evidence": []},
    "finding_concentration": {"agent": "ConcentrationChain", "severity": 0, "summary": "ok", "evidence": []},
    "finding_liquidity": {"agent": "LiquidityChain", "severity": 2, "summary": "risk", "evidence": []},
}

result = reducer_chain(state)
assert "risk_report" in result
assert result["risk_report"]["overall_severity"] == 2
assert len(result["findings"]) == 3

print("✅ Reducer 测试通过")
```

### 测试2：Decision 决策逻辑

```python
from src.tools.decision import decision_engine

# 测试：无风险
state = {"rule_findings": [], "risk_report": {"overall_severity": 0}, "data_quality": {}}
result = decision_engine(state)
assert result["decision"]["decision"] == "pass"

# 测试：规则触发 restrict
state = {
    "rule_findings": [{"severity": "restrict", "level": 2, "rule_id": "test"}],
    "risk_report": {"overall_severity": 0},
    "data_quality": {},
}
result = decision_engine(state)
assert result["decision"]["decision"] == "restrict"

# 测试：规则触发 block
state = {
    "rule_findings": [{"severity": "block", "level": 3, "rule_id": "blocklist"}],
    "risk_report": {"overall_severity": 0},
    "data_quality": {},
}
result = decision_engine(state)
assert result["decision"]["decision"] == "block"

print("✅ Decision 测试通过")
```

### 测试3：Solver 仅 restrict 时运行

```python
from src.tools.solver import constraint_solver

# decision != restrict 时返回空
state = {"decision": {"decision": "pass"}}
result = constraint_solver(state)
assert result == {}

print("✅ Solver 跳过测试通过")
```

### 测试4：Audit 审计日志

```python
from src.tools.audit import audit_log

state = {
    "normalized": {"policy_profile": "default"},
    "snapshot_metrics": {"hhi": 0.5},
    "rule_findings": [],
    "tool_calls_macro": [],
    "tool_calls_compliance": [],
}

result = audit_log(state)
assert "audit" in result
audit = result["audit"]
assert "timestamp" in audit
assert "trace_id" in audit
assert "policy_profile" in audit
assert audit["policy_profile"] == "default"

print("✅ Audit 测试通过")
```

**检查项：**
- [ ] `reducer_chain` 返回 `{"findings": ..., "risk_report": ..., "data_gaps": ...}`
- [ ] `decision_engine` 返回 `{"decision": {...}, "binding_constraints": [...]}`
- [ ] `constraint_solver` 在 decision != "restrict" 时返回空 dict
- [ ] `audit_log` 返回 `{"audit": {...}}`，包含 trace_id 和 timestamp
- [ ] 所有函数返回 Dict，不修改 state

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **所有函数返回 Dict，不修改 state** — 与旧模板中 `return state` 的模式完全不同
2. **reducer 做证据清洗** — 不是简单汇总，还要用 skill 的 `evidence_prefixes` 过滤非法引用
3. **决策两层逻辑** — 先看 `rule_level`（硬规则），再看 `report_level`（风险报告）
4. **solver 三级降级** — LP 求解 → 启发式调整 → review_targets guidance
5. **CVXPY 可选依赖** — `try: import cvxpy` 失败时 `_solve_lp` 返回 None，走启发式
6. **audit 用 load_skill 获取版本** — skills_used 不是数字，是包含 name/policy_version/skills_hash 的列表

**常见错误：**
- ❌ `reducer_chain` 返回 `state` 而非 Dict — 应返回 `{"findings": ..., "risk_report": ...}`
- ❌ `decision_engine` 直接用 `risk_report["overall_severity"]` 做决策 — 应先看 `rule_level`
- ❌ `constraint_solver` 在 decision != "restrict" 时仍然运行 — 应直接返回 `{}`
- ❌ `audit_log` 用 `uuid` 生成 trace_id — 应该用 `_hash_payload` 基于时间戳生成

**参考资源：**
- [CVXPY 官方文档](https://www.cvxpy.org/)
- `src/tools/utils.py` 中的 `normalize_weights`、`compute_hhi`、`compute_effective_n`

</details>

---

## 📝 模块10: 阈值校准

<details open>
<summary><b>📋 模块信息</b></summary>

| 项目 | 内容 |
|:---|:---|
| **难度** | ⭐⭐⭐ 中级 |
| **文件数** | 2个 |
| **文件路径** | `src/tools/calibrate_rules.py`<br>`src/tools/calibrate_macro_series.py` |
| **依赖模块** | 模块3 |
| **被依赖** | 模块5, 6, 8 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 蒙特卡洛采样方法
- [ ] Dirichlet 分布应用
- [ ] 分位数阈值生成
- [ ] 时序数据处理

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块负责自动校准规则阈值，确保阈值符合实际数据分布。

**核心功能：**
1. **组合规则校准**：基于历史数据随机采样生成阈值
2. **宏观序列校准**：基于时序数据变化幅度生成阈值

**为什么重要：**
阈值直接影响风险判断的准确性，自动校准避免人工设定的主观性。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/tools/calibrate_rules.py`

**实现 `calibrate_rules(asof_date, n, *, samples, seed) -> Dict[str, Any]` 及辅助函数**

需要实现以下函数：

| 函数 | 说明 |
|:---|:---|
| `_env_float(name, default) -> float` | 从环境变量读取浮点数，失败回退默认值 |
| `_load_blocklist(path, fallback) -> List[str]` | 从已有 rules.yaml 加载 blocklist，文件不存在则用 fallback |
| `_percentile(values, p) -> float` | 纯 Python 分位数计算（不依赖 numpy），线性插值 |
| `_dirichlet(n, rng) -> List[float]` | 纯 Python Dirichlet 采样，使用 `rng.gammavariate(1.0, 1.0)` |
| `_load_market_metrics_range(start_date, end_date)` | 调用 `csv_data.market_metrics_by_range` 加载市场指标 |
| `_simulate(codes, metrics, n, samples, seed)` | 蒙特卡洛模拟：随机抽样 ETF + Dirichlet 权重，计算 6 类指标 |
| `_build_rules(series, *, high_warn, high_restrict, low_warn, low_restrict, blocklist)` | 用分位数生成一套完整规则（17 个阈值 + blocklist） |
| `calibrate_rules(asof_date, n, *, samples, seed)` | 主函数：加载数据 → 模拟 → 生成 default + conservative 两套规则 → 写入 YAML |
| `main()` | CLI 入口，argparse 解析参数 |

校准流程：
1. 解析 asof_date，计算数据窗口 `[年初, asof_date]`
2. 调用 `_load_market_metrics_range` 加载 ETF 市场指标（volatility, adv, spread_bps）
3. `_simulate` 蒙特卡洛采样：随机抽 n 只 ETF + Dirichlet 权重，计算 6 类组合指标
4. `_build_rules` 对每类指标取分位数生成阈值（高指标用 high 分位数，低指标用 low 分位数）
5. 生成 default + conservative 两套规则（分位数参数不同，从环境变量读取）
6. 写入 `cufel_practice_data/rules.yaml`，返回 `{"rules_path": ..., "profiles": [...]}`

### 文件2：`src/tools/calibrate_macro_series.py`

**实现 `calibrate_macro_series(asof_date, *, lookback_days, warn_pctl, restrict_pctl, min_samples, config_path) -> Dict[str, Any]` 及辅助函数**

需要实现以下函数：

| 函数 | 说明 |
|:---|:---|
| `_parse_date(value) -> datetime \| None` | 多格式日期解析（YYYY-MM-DD / YYYYMMDD / ISO） |
| `_format_tushare_date(value) -> str` | datetime → YYYYMMDD 格式 |
| `_format_tushare_year_start(value) -> str` | datetime → 年初日期 YYYYMMDD |
| `_percentile(values, p) -> float` | 纯 Python 分位数计算，线性插值 |
| `_load_config(path) -> Dict` | 加载 macro_series.yaml 配置，校验 series 映射 |
| `_get_tushare_client()` | 从环境变量获取 token，返回 `(pro, error)` 元组 |
| `_fetch_series(pro, series, config, asof_date)` | 调用 Tushare API 拉取单个序列，返回 `(rows, error)` |
| `_filter_window(rows, asof_date, lookback_days)` | 按时间窗口过滤数据点 |
| `_compute_changes(values, mode, scale)` | 计算相邻值变化幅度，支持 pct/abs 模式和 bp 缩放 |
| `calibrate_macro_series(asof_date, *, ...)` | 主函数：遍历序列 → 拉数据 → 算变化 → 取分位数 → 回写 YAML |
| `main()` | CLI 入口，argparse 解析参数 |

校准流程：
1. 加载 `macro_series.yaml` 配置，获取所有序列定义
2. 初始化 Tushare 客户端（从 `TUSHARE_TOKEN` 环境变量）
3. 对每个序列：拉取数据 → 按时间窗口过滤 → 计算变化幅度
4. 对变化幅度取 warn/restrict 分位数，回写到配置的 `warn_pct_change` / `restrict_pct_change`
5. 将更新后的完整配置写回 YAML 文件，返回 `{"config_path": ..., "updated": {...}}`

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/calibrate_rules.py`

```python
"""
组合规则阈值校准模块
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from .csv_data import market_metrics_by_range


def _percentile(values: List[float], p: float) -> float:
    """
    计算分位数（纯 Python 实现，线性插值）。

    Args:
        values: 数值列表
        p: 分位数 (0.0 - 1.0)
    """
    if not values:
        return 0.0
    v = sorted(values)
    # TODO: 实现分位数计算逻辑
    # k = (len(v) - 1) * p
    # f = math.floor(k)
    # c = math.ceil(k)
    # 线性插值返回 result
    pass


def _dirichlet(n: int, rng: random.Random) -> List[float]:
    """
    生成 Dirichlet 分布样本（纯 Python 实现）。
    使用 rng.gammavariate(1.0, 1.0) 生成 n 个随机数并归一化。
    """
    # TODO: 实现 Dirichlet 采样
    # raw = [rng.gammavariate(1.0, 1.0) for _ in range(n)]
    # total = sum(raw)
    # return [v / total for v in raw]
    pass


def _simulate(
    codes: List[str],
    metrics: Dict[str, Dict[str, float]],
    n: int,
    samples: int,
    seed: str | None,
) -> Dict[str, List[float]]:
    """
    蒙特卡洛模拟：随机生成组合并计算指标分布。

    Returns:
        Dict[metric_name, List[values]]
    """
    rng = random.Random(seed) if seed else random

    # 结果容器
    vols: List[float] = []
    spreads: List[float] = []
    advs: List[float] = []
    hhis: List[float] = []
    tops: List[float] = []
    effns: List[float] = []

    # TODO: 循环 samples 次
    # 1. 随机抽取 n 个代码: rng.sample(codes, n)
    # 2. 生成权重: _dirichlet(n, rng)
    # 3. 计算组合指标:
    #    - hhi = sum(w^2)
    #    - effn = 1/hhi
    #    - top = max(w)
    #    - vol = sum(w * m["volatility"])
    #    - spread = sum(w * m["spread_bps"])
    #    - adv = sum(w * m["adv"])
    # 4. 存入结果列表

    return {
        "volatility": vols,
        "spread_bps": spreads,
        "adv": advs,
        "hhi": hhis,
        "top_weight": tops,
        "effective_n": effns,
    }


def _build_rules(
    series: Dict[str, List[float]],
    *,
    high_warn: float,
    high_restrict: float,
    low_warn: float,
    low_restrict: float,
    blocklist: List[str],
) -> Dict[str, Any]:
    """
    根据模拟分布生成规则阈值。
    """
    return {
        # TODO: 使用 _percentile 计算各指标阈值
        # 注意：
        # - 高风险指标 (vol, spread, hhi, top) 使用 high_warn/high_restrict
        # - 低风险指标 (adv, effective_n) 使用 low_warn/low_restrict
        "max_single_weight": 0.0,
        "max_hhi": 0.0,
        "max_portfolio_volatility": 0.0,
        "max_weighted_spread_bps": 0.0,
        "min_weighted_adv": 0.0,

        "volatility_warn": 0.0,
        "volatility_restrict": 0.0,

        # ... 其他指标

        "blocklist": list(blocklist),
    }


def calibrate_rules(asof_date: str, n: int, *, samples: int | None = None, seed: str | None = None) -> Dict[str, Any]:
    """
    主函数：基于历史数据校准组合规则阈值。
    """
    # 1. 解析日期
    # start_date = f"{year}-01-01"

    # 2. 加载数据
    # codes, metrics = _load_market_metrics_range(start_date, asof_date)

    # 3. 运行模拟
    # series = _simulate(codes, metrics, n, samples, seed)

    # 4. 定义分位数参数 (从环境变量读取或使用默认值)
    # high_warn = 0.8, high_restrict = 0.9
    # low_warn = 0.2, low_restrict = 0.1

    # 5. 生成两套规则
    # rules = {
    #     "default": _build_rules(...),
    #     "conservative": _build_rules(...),
    # }

    # 6. 保存到 rules.yaml
    # Path(...).write_text(...)

    return {"profiles": list(rules.keys())}


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate rules from ETF history.")
    parser.add_argument("--asof-date", type=str, required=True, help="YYYY-MM-DD")
    parser.add_argument("--n", type=int, default=5, help="portfolio size")
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--seed", type=str, default=None)
    args = parser.parse_args()

    result = calibrate_rules(
        args.asof_date,
        args.n,
        samples=args.samples,
        seed=args.seed,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

### 文件2：`src/tools/calibrate_macro_series.py`

```python
"""
宏观序列阈值校准模块
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import tushare as ts
import yaml


def _parse_date(value: Any) -> datetime | None:
    """解析多种格式的日期字符串 (YYYY-MM-DD, YYYYMMDD, ISO)。"""
    pass


def _get_tushare_client() -> Tuple[Any | None, str | None]:
    """
    初始化 Tushare 客户端。
    从环境变量 TUSHARE_TOKEN 读取。
    Returns: (pro_api, error_msg)
    """
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if not token:
        return None, "TUSHARE_TOKEN not configured"
    ts.set_token(token)
    return ts.pro_api(), None


def _fetch_series(
    pro: Any,
    series: str,
    config: Dict[str, Any],
    asof_date: datetime | None,
) -> Tuple[List[Tuple[datetime, float]], str | None]:
    """
    调用 Tushare API 拉取单条序列数据。

    Args:
        config: series 配置 (api, params, fields 等)
    Returns:
        (rows, error) 其中 rows 是 (date, value) 的列表
    """
    # TODO: 解析配置参数
    # api_name = config.get("api")
    # params = config.get("params")
    # fields = config.get("fields")

    # TODO: 调用 Tushare
    # api = getattr(pro, api_name)
    # df = api(**params, fields=fields)

    # TODO: 转换为 (date, value) 列表
    # 遍历 df.iterrows()
    # 解析日期和数值
    # 处理 bid/ask 均值逻辑

    rows = []
    return rows, None


def _filter_window(
    rows: List[Tuple[datetime, float]],
    asof_date: datetime | None,
    lookback_days: int | None,
) -> List[Tuple[datetime, float]]:
    """按时间窗口过滤数据。"""
    if not rows:
        return rows
    # TODO: 过滤逻辑
    # keep if start_date <= date <= asof_date
    return rows


def _compute_changes(values: List[float], mode: str, scale: str | None) -> List[float]:
    """
    计算相邻值变化幅度。

    Args:
        mode: "pct" (百分比) 或 "abs" (绝对值)
        scale: "bp" (基点) 或 None
    """
    changes: List[float] = []
    # TODO: 计算逻辑
    # for i in range(1, len(values)):
    #     prev, curr = values[i-1], values[i]
    #     change = abs(curr - prev) if mode == "abs" else abs((curr - prev) / prev)
    #     if scale == "bp": change *= 100
    #     changes.append(change)
    return changes


def calibrate_macro_series(
    asof_date: str,
    *,
    lookback_days: int | None = None,
    warn_pctl: float | None = None,
    restrict_pctl: float | None = None,
    min_samples: int | None = None,
    config_path: str | None = None,
) -> Dict[str, Any]:
    """
    基于宏观时序数据校准宏观指标阈值。

    流程：
    1. 加载 config_path (macro_series.yaml)
    2. 初始化 Tushare
    3. 遍历每个 series:
       - _fetch_series 拉取数据
       - _filter_window 过滤窗口
       - _compute_changes 计算波动
       - _percentile 计算分位数 (warn_pctl, restrict_pctl)
       - 更新 config 字典中的 warn_pct_change / restrict_pct_change
    4. 写回 yaml 文件
    """
    # 1. 解析参数
    # asof = _parse_date(asof_date)
    # config = _load_config(path)

    # 2. 遍历处理
    updated = {}
    # for series, cfg in config["series"].items():
    #     rows, err = _fetch_series(...)
    #     changes = _compute_changes(...)
    #     warn = _percentile(changes, warn_pctl)
    #     restrict = _percentile(changes, restrict_pctl)
    #     cfg["warn_pct_change"] = warn
    #     cfg["restrict_pct_change"] = restrict

    # 3. 保存并返回
    # path.write_text(yaml.dump(config))
    return {"updated": updated}


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate macro series thresholds.")
    parser.add_argument("--asof-date", default=os.getenv("ASOF_DATE", ""))
    parser.add_argument("--lookback-days", type=int, default=365 * 3)
    parser.add_argument("--warn-pctl", type=float, default=0.9)
    parser.add_argument("--restrict-pctl", type=float, default=0.98)
    parser.add_argument("--min-samples", type=int, default=30)
    parser.add_argument("--config", default="")
    args = parser.parse_args()

    result = calibrate_macro_series(
        args.asof_date or datetime.now().date().isoformat(),
        lookback_days=args.lookback_days,
        warn_pctl=args.warn_pctl,
        restrict_pctl=args.restrict_pctl,
        min_samples=args.min_samples,
        config_path=args.config or None,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试校准流程

```bash
# 校准组合规则 (生成的 rules.yaml 会包含 default 和 conservative 两套配置)
uv run --env-file .env -- python -u -m src.tools.calibrate_rules \
  --asof-date 2025-11-14 \
  --n 5 \
  --samples 1000 \
  --seed 42

# 校准宏观序列 (会读取 TUSHARE_TOKEN 并更新 macro_series.yaml)
uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series \
  --asof-date 2025-11-14 \
  --lookback-days 1095
```

**检查项：**
- [ ] `cufel_practice_data/rules.yaml` 已更新，包含 blocklist 和完整的阈值
- [ ] `cufel_practice_data/macro_series.yaml` 已更新，各序列的 `warn_pct_change` 和 `restrict_pct_change` 已填充
- [ ] 阈值数值合理 (restrict > warn)
- [ ] `macro_series.yaml` 中没有 "error" 字段

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **纯 Python Dirichlet 采样**：
   不依赖 numpy，使用 gamma 分布生成：
   ```python
   def _dirichlet(n, rng):
       raw = [rng.gammavariate(1.0, 1.0) for _ in range(n)]
       total = sum(raw)
       return [x / total for x in raw]
   ```

2. **纯 Python 分位数计算**：
   先排序，再线性插值：
   ```python
   def _percentile(values, p):
       v = sorted(values)
       k = (len(v) - 1) * p
       f = int(k)  # floor
       c = math.ceil(k)
       if f == c: return v[int(k)]
       return v[f] + (v[c] - v[f]) * (k - f)
   ```

3. **Tushare 错误处理**：
   - 网络超时或 Token 错误时，不要让整个程序崩溃，记录 error 到结果中
   - 数据不足 (`len(changes) < min_samples`) 时跳过校准

**常见错误：**
- ❌ 忘记设置 `TUSHARE_TOKEN` 环境变量
- ❌ 宏观数据变化幅度计算错误（百分比 vs 绝对值）
- ❌ `rules.yaml` 格式错误（缩进不正确）

**参考资源：**
- [Dirichlet Distribution (Wikipedia)](https://en.wikipedia.org/wiki/Dirichlet_distribution)
- [Tushare Pro API 文档](https://tushare.pro/document/2)

</details>

---

##  🧩 拓展题：更科学的阈值生成与二次校准

本拓展题鼓励你在“统计基线”的基础上设计更可靠的阈值生成规则，并结合风控政策或业务约束做二次校准。

### 背景说明
基础方案通常是：在历史窗口内随机抽样组合（如 Dirichlet 权重），计算波动率/HHI/ADV/spread 等指标，得到经验分布，再取分位数作为 warn/restrict 阈值。  
该方法是**统计基线**，但不等同于监管标准，实际落地需要二次校准。

### 你的任务
设计一个更科学的阈值配置生成流程，并说明它为何更稳健。

### 设计要点（建议覆盖）
1. **采样设计更贴近真实组合**
   - 分层抽样（按 ETF 类型/规模/流动性分桶）
   - 权重分布更贴近真实持仓（Dirichlet α 参数可解释）
   - 约束式采样（单标的上限、最小权重等）

2. **阈值更稳健**
   - 去极值或 winsorize
   - 多窗口/多周期统计，取稳健均值或中位数
   - warn/restrict 分位数具有明确区间（如 80% / 95%）

3. **二次校准**
   - 引入业务规则（集中度、规模约束、合规限制）
   - 压力期校验（波动剧烈时期阈值不应过松）
   - 阈值稳定性约束（避免大幅漂移）

### 交付说明
请提交一份“阈值生成与校准说明文档”，包含：
- 采样设计思路与公式/伪代码
- 分位数选择理由
- 二次校准规则与约束
- 与原始基线相比的改进点

---

## 📥 输入输出示例

### 输入示例

```python
intent = {
    "date": "2025-11-15",
    "mode": "target",
    "targets": {
        "159213": 0.25,
        "159959": 0.25,
        "511960": 0.20,
        "516310": 0.20,
        "561180": 0.10
    }
}

context = {
    "current_positions": {
        "159213": 0.20,
        "159959": 0.20,
        "511960": 0.20,
        "516310": 0.20,
        "561180": 0.20
    },
    "policy_profile": "default",
    "aum": 1000000.0
}
```

### 输出示例

```python
{
    "decision": "pass",  # 或 warn/restrict/block
    "binding_constraints": [],
    "recommended_actions": [],
    "audit": {
        "policy_profile": "default",
        "llm_used": True,
        "supervisor_used": True,
        "nodes_to_run": ["market", "concentration", ...],
        "trace_id": "..."
    }
}
```

---


## 📚 参考资源

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain 官方文档](https://python.langchain.com/)
- 样本答案：`risk-mas/` 目录（仅供参考，建议先独立完成）

---

## ✅ 提交要求

1. 代码结构符合要求
2. 通过基本测试用例
3. 提供 README.md 说明如何运行
4. 提交完整的项目代码

---
**祝你练习顺利！** 🎉
