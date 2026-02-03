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

### 模块5: 分析链路 (0/4)
- [ ] src/chains/market.py
- [ ] src/chains/concentration.py
- [ ] src/chains/diversification.py
- [ ] src/chains/liquidity.py

### 模块6: Agent 模块 (0/2)
- [ ] src/agents/macro_agent.py
- [ ] src/agents/compliance_agent.py

### 模块7: Skills 体系 (0/2)
- [ ] src/skills_runtime.py
- [ ] skills/*/SKILL.md

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
| 模块5: 分析链路 | 4 | ⭐⭐⭐ |
| 模块6: Agent 模块 | 2 | ⭐⭐⭐⭐ |
| 模块7: Skills 体系 | 2 | ⭐⭐ |
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

定义 `RiskState` TypedDict，包含以下字段分组：

**1. 输入字段**
- `intent`: 交易意图（dict）
- `context`: 组合上下文（dict）

**2. 预处理字段**
- `normalized`: 归一化后的数据（dict）
- `validation`: 验证结果（dict）
- `snapshot_metrics`: 指标快照（dict）
- `data_quality`: 数据质量（dict）

**3. 分析结果字段**
- `finding_market`: 市场风险分析结果（dict）
- `finding_concentration`: 集中度风险分析结果（dict）
- `finding_diversification`: 分散度风险分析结果（dict）
- `finding_liquidity`: 流动性风险分析结果（dict）
- `finding_macro`: 宏观风险分析结果（dict）
- `finding_compliance`: 合规风险分析结果（dict）

**4. 决策字段**
- `decision`: 决策结果 pass/warn/restrict/block（str）
- `binding_constraints`: 约束条件列表（list）
- `recommended_actions`: 调仓建议列表（list）

**5. 其他字段**
- `audit`: 审计日志（dict）
- `candidate_nodes`: 候选节点列表（list）
- `nodes_to_run`: 实际运行节点列表（list）

</details>

<details>
<summary><b>💻 代码模板</b></summary>

```python
"""
风控 MAS 状态定义模块
定义整个工作流的状态结构
"""
from typing import TypedDict, NotRequired, Any


class RiskState(TypedDict):
    """
    风控工作流的状态结构

    所有字段都是可选的，使用 NotRequired 标记
    """

    # ========== 输入字段 ==========
    # TODO: 定义 intent 字段（交易意图）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 context 字段（组合上下文）
    # 类型: NotRequired[dict[str, Any]]


    # ========== 预处理字段 ==========
    # TODO: 定义 normalized 字段（归一化后的数据）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 validation 字段（验证结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 snapshot_metrics 字段（指标快照）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 data_quality 字段（数据质量）
    # 类型: NotRequired[dict[str, Any]]


    # ========== 分析结果字段 ==========
    # TODO: 定义 finding_market 字段（市场风险分析结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 finding_concentration 字段（集中度风险分析结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 finding_diversification 字段（分散度风险分析结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 finding_liquidity 字段（流动性风险分析结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 finding_macro 字段（宏观风险分析结果）
    # 类型: NotRequired[dict[str, Any]]

    # TODO: 定义 finding_compliance 字段（合规风险分析结果）
    # 类型: NotRequired[dict[str, Any]]


    # ========== 决策字段 ==========
    # TODO: 定义 decision 字段（决策结果: pass/warn/restrict/block）
    # 类型: NotRequired[str]

    # TODO: 定义 binding_constraints 字段（约束条件列表）
    # 类型: NotRequired[list[dict[str, Any]]]

    # TODO: 定义 recommended_actions 字段（调仓建议列表）
    # 类型: NotRequired[list[dict[str, Any]]]


    # ========== 其他字段 ==========
    # TODO: 根据需要添加其他字段（如 audit、candidate_nodes 等）
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

完成后请检查：
- [ ] 所有必需字段都已定义
- [ ] 所有字段都使用了 `NotRequired` 标记
- [ ] 类型标注正确（dict, list, str 等）
- [ ] 可以成功导入

**测试命令：**
```bash
# 测试导入
uv run --env-file .env -- python -u -c "from src.state import RiskState; print('✅ 状态定义正确')"

# 测试类型检查（如果安装了 mypy）
uv run --env-file .env -- mypy src/state.py
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

实现 `validate_node(state: RiskState) -> RiskState` 函数：

**1. 验证 intent 字段**
- `date`: 必填，格式 `YYYY-MM-DD`
- `mode`: 必填，值为 `target` 或 `delta`
- `targets`: 必填，dict 类型

**2. 权重归一化**
- 计算 targets 的权重和
- 如果权重和不为 1，自动归一化
- 记录 warning 到 `validation` 字段

**3. 处理 mode=delta**
- 将 delta 叠加到 `current_positions`
- 生成新的 targets

**4. 输出**
- `state['normalized']`: 归一化后的数据
- `state['validation']`: 验证结果

</details>

<details>
<summary><b>💻 代码模板</b></summary>

```python
"""
输入验证与规范化模块
"""
from typing import Any
from src.state import RiskState
from src.config import RuntimeConfig, DEFAULT_CONFIG


def validate_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    验证和规范化用户输入

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    intent = state.get("intent", {})
    context = state.get("context", {})

    validation_result = {
        "status": "ok",
        "warnings": [],
        "errors": []
    }

    # TODO: 验证 intent.date 字段
    # - 检查是否存在
    # - 检查格式是否为 YYYY-MM-DD
    # - 如果不合法，添加错误到 validation_result["errors"]


    # TODO: 验证 intent.mode 字段
    # - 检查是否存在
    # - 检查值是否为 "target" 或 "delta"
    # - 如果不合法，添加错误到 validation_result["errors"]


    # TODO: 验证 intent.targets 字段
    # - 检查是否存在
    # - 检查是否为 dict 类型
    # - 如果不合法，添加错误到 validation_result["errors"]


    # TODO: 权重归一化
    # - 计算 targets 的权重和
    # - 如果权重和不为 1，进行归一化
    # - 记录 warning 到 validation_result["warnings"]


    # TODO: 处理 mode=delta
    # - 如果 mode 为 "delta"，将 delta 叠加到 current_positions
    # - 生成新的 targets


    # TODO: 更新 state
    # - 将归一化后的数据写入 state["normalized"]
    # - 将验证结果写入 state["validation"]

    return state
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
from src.state import RiskState
from src.tools.validate import validate_node

# 测试1: 正常输入
state = {
    "intent": {
        "date": "2025-11-15",
        "mode": "target",
        "targets": {"159213": 0.5, "159959": 0.5}
    }
}
result = validate_node(state)
assert result["validation"]["status"] == "ok"

# 测试2: 权重不为1
state = {
    "intent": {
        "date": "2025-11-15",
        "mode": "target",
        "targets": {"159213": 0.3, "159959": 0.4}
    }
}
result = validate_node(state)
assert len(result["validation"]["warnings"]) > 0
assert abs(sum(result["normalized"]["targets"].values()) - 1.0) < 1e-6

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

**实现3个工具函数：**

1. `normalize_weights(weights: dict) -> dict`
   - 将权重归一化为和为 1

2. `compute_hhi(weights: dict) -> float`
   - 计算 HHI 指数（Herfindahl-Hirschman Index）
   - 公式：HHI = Σ(weight_i²)

3. `compute_effective_n(weights: dict) -> float`
   - 计算有效持仓数
   - 公式：1 / HHI

### 文件2：`src/tools/csv_data.py`

**实现数据加载函数：**

1. `load_etf_data(asof_date: str) -> pd.DataFrame`
   - 读取 `cufel_practice_data/etf_2025_data.csv`
   - 截断到 asof_date 之前的数据

2. `load_compliance_texts() -> list`
   - 读取合规文本库

3. `load_macro_texts(asof_date: Optional[str]) -> list`
   - 读取宏观文本库

### 文件3：`src/tools/data_quality.py`

**实现 `data_quality_node(state: RiskState) -> RiskState`**

检查项：
- 市场数据是否缺失
- 宏观数据新鲜度
- 合规文本是否可用
- 持仓数据新鲜度

### 文件4：`src/tools/snapshot.py`

**实现 `snapshot_node(state: RiskState) -> RiskState`**

计算指标：
- 组合波动率（基于历史收益率）
- HHI 指数
- 有效持仓数
- 加权买卖价差
- 加权成交量

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/utils.py`

```python
"""
共享工具函数模块
"""
from typing import Dict


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    """
    将权重归一化为和为 1

    Args:
        weights: 权重字典 {code: weight}

    Returns:
        归一化后的权重字典
    """
    # TODO: 实现权重归一化
    # - 计算权重总和
    # - 将每个权重除以总和
    # - 返回归一化后的字典
    pass


def compute_hhi(weights: Dict[str, float]) -> float:
    """
    计算 HHI 指数（Herfindahl-Hirschman Index）

    公式: HHI = Σ(weight_i²)

    Args:
        weights: 权重字典 {code: weight}

    Returns:
        HHI 指数
    """
    # TODO: 实现 HHI 计算
    # - 对每个权重求平方
    # - 求和
    # - 返回结果
    pass


def compute_effective_n(weights: Dict[str, float]) -> float:
    """
    计算有效持仓数

    公式: 1 / HHI

    Args:
        weights: 权重字典 {code: weight}

    Returns:
        有效持仓数
    """
    # TODO: 实现有效持仓数计算
    # - 调用 compute_hhi 计算 HHI
    # - 返回 1 / HHI
    pass
```

### 文件2：`src/tools/csv_data.py`

```python
"""
CSV 数据读取模块
"""
import pandas as pd
from typing import List, Optional
from src.config import RuntimeConfig, DEFAULT_CONFIG


def load_etf_data(asof_date: str, config: RuntimeConfig | None = None) -> pd.DataFrame:
    """
    读取 ETF 行情数据并截断到 asof_date

    Args:
        asof_date: 截止日期，格式 YYYY-MM-DD

    Returns:
        ETF 行情数据 DataFrame
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 实现 ETF 数据加载
    # - 读取 cufel_practice_data/etf_2025_data.csv
    # - 支持从 runtime.csv_data_dir 读取数据目录
    # - 筛选日期 <= asof_date 的数据
    # - 返回 DataFrame
    pass


def load_compliance_texts(config: RuntimeConfig | None = None) -> List[dict]:
    """
    读取合规文本库

    Returns:
        合规文本列表
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 实现合规文本加载
    # - 读取合规文本 CSV 文件
    # - 支持从 runtime.csv_data_dir 读取数据目录
    # - 转换为字典列表
    # - 返回结果
    pass


def load_macro_texts(asof_date: Optional[str] = None, config: RuntimeConfig | None = None) -> List[dict]:
    """
    读取宏观文本库

    Args:
        asof_date: 截止日期（可选）

    Returns:
        宏观文本列表
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 实现宏观文本加载
    # - 读取宏观文本 CSV 文件
    # - 支持从 runtime.csv_data_dir 读取数据目录
    # - 如果提供 asof_date，筛选日期 <= asof_date 的数据
    # - 返回结果
    pass
```

### 文件3：`src/tools/data_quality.py`

```python
"""
数据质量检查模块
"""
from src.state import RiskState
from src.config import RuntimeConfig, DEFAULT_CONFIG


def data_quality_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    检查数据质量（完整性、新鲜度）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    quality_report = {
        "market": {},
        "macro": {},
        "compliance": {},
        "positions": {}
    }

    # TODO: 检查市场数据质量
    # - 检查 ETF 主表是否缺失
    # - 检查行情数据是否缺失
    # - 将结果写入 quality_report["market"]


    # TODO: 检查宏观数据质量
    # - 检查 runtime.tushare_token（时序数据可用性）
    # - 检查宏观文本是否可用
    # - 检查数据新鲜度（距离 asof_date 的天数）
    # - 使用 runtime.macro_stale_days 作为陈旧阈值
    # - 将结果写入 quality_report["macro"]


    # TODO: 检查合规数据质量
    # - 检查合规文本是否可用
    # - 将结果写入 quality_report["compliance"]


    # TODO: 检查持仓数据质量
    # - 检查 current_positions_date 新鲜度
    # - 将结果写入 quality_report["positions"]


    # TODO: 更新 state
    state["data_quality"] = quality_report

    return state
```

### 文件4：`src/tools/snapshot.py`

```python
"""
指标快照计算模块
"""
from src.state import RiskState
from src.tools.utils import compute_hhi, compute_effective_n
from src.config import RuntimeConfig, DEFAULT_CONFIG


def snapshot_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    计算投资组合的风险指标快照

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    normalized = state.get("normalized", {})
    targets = normalized.get("targets", {})

    snapshot = {}

    # TODO: 计算组合波动率
    # - 从 ETF 数据中获取历史收益率
    # - 使用 runtime.market_lookback_days 作为回溯窗口
    # - 计算加权组合收益率
    # - 计算组合波动率（标准差）
    # - 将结果写入 snapshot["portfolio_volatility"]


    # TODO: 计算 HHI 指数
    # - 调用 compute_hhi 函数
    # - 将结果写入 snapshot["hhi"]


    # TODO: 计算有效持仓数
    # - 调用 compute_effective_n 函数
    # - 将结果写入 snapshot["effective_n"]


    # TODO: 计算加权买卖价差
    # - 从 ETF 数据中获取买卖价差
    # - 计算加权平均
    # - 将结果写入 snapshot["weighted_spread"]


    # TODO: 计算加权成交量
    # - 从 ETF 数据中获取成交量（ADV）
    # - 计算加权平均
    # - 将结果写入 snapshot["weighted_adv"]


    # TODO: 更新 state
    state["snapshot_metrics"] = snapshot

    return state
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试 utils.py
```python
from src.tools.utils import normalize_weights, compute_hhi, compute_effective_n

# 测试归一化
weights = {"A": 0.3, "B": 0.4}
normalized = normalize_weights(weights)
assert abs(sum(normalized.values()) - 1.0) < 1e-6

# 测试 HHI
weights = {"A": 0.5, "B": 0.5}
hhi = compute_hhi(weights)
assert abs(hhi - 0.5) < 1e-6

# 测试有效持仓数
effective_n = compute_effective_n(weights)
assert abs(effective_n - 2.0) < 1e-6

print("✅ utils.py 测试通过")
```

### 测试 csv_data.py
```python
from src.tools.csv_data import load_etf_data

df = load_etf_data("2025-11-15")
assert not df.empty
assert df["trade_date"].max() <= "2025-11-15"

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

**创建 LangGraph 工作流：**

1. 创建 StateGraph
2. 添加所有节点
3. 定义节点间的边
4. 实现并行分发逻辑（Send API）
5. 编译并导出 graph

**节点列表：**
- validate, data_quality, snapshot
- gatekeeper, supervisor
- market, concentration, diversification, liquidity, macro, compliance
- reducer, constraints, decision, solver, audit

### 文件2：`src/chains/gatekeeper.py`

**实现 `gatekeeper_node(state: RiskState) -> RiskState`**

**裁剪逻辑：**
- 基于 data_quality.macro.timeseries_available 决定是否保留 macro 节点
- 基于 data_quality.compliance.text_available 决定是否保留 compliance 节点

### 文件3：`src/chains/supervisor.py`

**实现 `supervisor_node(state: RiskState) -> RiskState`**

**调度逻辑：**
- 从 gatekeeper 提供的候选节点中选择（候选节点已通过数据可用性检查）
- 使用 LLM 基于业务逻辑（风险指标、成本优化、性能考量）决定需要运行的节点
- 提供决策理由（不需要再次检查数据可用性）

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/graph.py`

```python
"""
LangGraph 工作流编排模块
"""
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from src.state import RiskState
from src.config import RuntimeConfig, DEFAULT_CONFIG


def create_graph(llm=None, config: RuntimeConfig | None = None):
    """
    创建 LangGraph 工作流

    Returns:
        编译后的 graph
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 创建 StateGraph
    # graph = StateGraph(RiskState)


    # TODO: 添加节点
    # - validate: 输入验证
    # - data_quality: 数据质量检查
    # - snapshot: 指标快照
    # - gatekeeper: 数据可用性检查与候选节点筛选
    # - supervisor: 业务逻辑节点选择
    # - market, concentration, diversification, liquidity: 分析链路
    # - macro, compliance: Agent 节点
    # - reducer: 结果汇总
    # - constraints: 约束评估
    # - decision: 决策引擎
    # - solver: 约束求解
    # - audit: 审计日志


    # TODO: 添加边
    # - validate -> data_quality
    # - data_quality -> snapshot
    # - snapshot -> gatekeeper
    # - gatekeeper -> supervisor
    # - supervisor -> (并行分发到分析节点)
    # - 所有分析节点 -> reducer
    # - reducer -> constraints
    # - constraints -> decision
    # - decision -> solver (条件边：仅当 decision=restrict 时)
    # - solver -> audit
    # - audit -> END


    # TODO: 实现并行分发逻辑
    # 使用 Send API 将任务分发到多个分析节点
    def route_to_analysis(state: RiskState):
        """根据 supervisor 决策分发任务"""
        # TODO: 从 state["nodes_to_run"] 获取需要运行的节点
        # TODO: 为每个节点创建 Send 对象
        # TODO: 返回 Send 对象列表
        pass


    # TODO: 编译 graph
    # graph = graph.compile()

    # return graph
    pass
```

### 文件2：`src/chains/gatekeeper.py`

```python
"""
前置检查模块（Gatekeeper）
"""
from src.state import RiskState


def gatekeeper_node(state: RiskState) -> RiskState:
    """
    前置检查，裁剪候选节点

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # 默认候选节点
    candidate_nodes = [
        "market",
        "concentration",
        "diversification",
        "liquidity",
        "macro",
        "compliance"
    ]

    # TODO: 检查宏观时序可用性
    # - 从 state["data_quality"]["macro"]["timeseries_available"] 判断
    # - 不可用则移除 "macro"


    # TODO: 检查合规文本可用性
    # - 从 state["data_quality"]["compliance"]["text_available"] 判断
    # - 不可用则移除 "compliance"


    # TODO: 更新 state
    state["candidate_nodes"] = candidate_nodes
    state["gatekeeper_rationale"] = "ok"  # 或记录裁剪原因

    return state
```

### 文件3：`src/chains/supervisor.py`

```python
"""
业务逻辑节点选择模块（Supervisor）
"""
from src.state import RiskState
from langchain_core.messages import SystemMessage, HumanMessage
from src.config import RuntimeConfig, DEFAULT_CONFIG


def supervisor_node(state: RiskState, llm=None, config: RuntimeConfig | None = None) -> RiskState:
    """
    基于业务逻辑从候选节点中选择需要运行的节点

    注意：候选节点已通过 gatekeeper 的数据可用性检查，
    supervisor 只需关注业务逻辑（风险指标、成本优化、性能考量）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    candidate_nodes = state.get("candidate_nodes", [])
    data_quality = state.get("data_quality", {})
    snapshot_metrics = state.get("snapshot_metrics", {})

    # TODO: 构建 LLM 提示词
    # - 系统提示词：说明 supervisor 的角色和任务
    # - 用户提示词：包含候选节点、指标快照、规则发现等业务信息


    # TODO: 调用 LLM
    # - 使用 LangChain 的 ChatModel
    # - 传入提示词
    # - 获取 LLM 的决策结果


    # TODO: 解析 LLM 输出
    # - 提取需要运行的节点列表
    # - 提取决策理由


    # TODO: 更新 state
    # state["nodes_to_run"] = nodes_to_run
    # state["supervisor_rationale"] = rationale

    return state
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试 Gatekeeper
```python
from src.chains.gatekeeper import gatekeeper_node

state = {
    "data_quality": {
        "macro": {"timeseries_available": False},
        "compliance": {"text_available": True}
    }
}

result = gatekeeper_node(state)
assert "macro" not in result["candidate_nodes"]
assert "compliance" in result["candidate_nodes"]

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
| **文件数** | 4个 |
| **文件路径** | `src/chains/market.py`<br>`src/chains/concentration.py`<br>`src/chains/diversification.py`<br>`src/chains/liquidity.py` |
| **依赖模块** | 模块1, 3, 4 |
| **被依赖** | 模块8 |

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

每个分析节点都需要：
1. 从 state 获取相关指标
2. 加载规则阈值
3. 判断风险等级（0-3）
4. 生成风险结论

### 文件1：`src/chains/market.py`

**实现 `market_node(state: RiskState) -> RiskState`**

- 指标：`portfolio_volatility`
- 阈值：`volatility_warn`, `volatility_restrict`
- 判断：波动率越高风险越大

### 文件2：`src/chains/concentration.py`

**实现 `concentration_node(state: RiskState) -> RiskState`**

- 指标：`hhi`
- 阈值：`hhi_warn`, `hhi_restrict`
- 判断：HHI 越高风险越大

### 文件3：`src/chains/diversification.py`

**实现 `diversification_node(state: RiskState) -> RiskState`**

- 指标：`effective_n`
- 阈值：`effective_n_warn`, `effective_n_restrict`
- 判断：有效持仓数越小风险越大（反向指标）

### 文件4：`src/chains/liquidity.py`

**实现 `liquidity_node(state: RiskState) -> RiskState`**

- 指标：`weighted_spread`, `weighted_adv`
- 阈值：`spread_warn`, `spread_restrict`, `adv_warn`, `adv_restrict`
- 判断：价差越大或成交量越小风险越大

</details>

<details>
<summary><b>💻 代码模板</b></summary>

由于4个文件结构相似，这里提供通用模板和具体示例。

### 通用模板结构

```python
"""
[风险类型]分析模块
"""
from src.state import RiskState
from src.tools.rules import load_rules


def [risk_type]_node(state: RiskState) -> RiskState:
    """
    [风险类型]分析

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    snapshot = state.get("snapshot_metrics", {})
    [indicator] = snapshot.get("[indicator_name]", 0.0)

    # TODO: 加载规则阈值
    # rules = load_rules()
    # [indicator]_warn = rules.get("[indicator]_warn")
    # [indicator]_restrict = rules.get("[indicator]_restrict")


    # TODO: 判断风险等级
    # - 如果 [indicator] > [indicator]_restrict，severity = 2
    # - 如果 [indicator] > [indicator]_warn，severity = 1
    # - 否则 severity = 0


    # TODO: 生成风险结论
    finding = {
        "severity": 0,  # TODO: 填充实际值
        "summary": "",  # TODO: 填充风险摘要
        "evidence": {},  # TODO: 填充证据数据
        "recommendation": ""  # TODO: 填充建议
    }

    # TODO: 更新 state
    state["finding_[risk_type]"] = finding

    return state
```

### 示例：market.py（完整代码模板）

```python
"""
市场风险分析模块
"""
from src.state import RiskState
from src.tools.rules import load_rules


def market_node(state: RiskState) -> RiskState:
    """
    市场风险分析（基于波动率）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    snapshot = state.get("snapshot_metrics", {})
    portfolio_volatility = snapshot.get("portfolio_volatility", 0.0)

    # TODO: 加载规则阈值
    # rules = load_rules()
    # vol_warn = rules.get("volatility_warn")
    # vol_restrict = rules.get("volatility_restrict")


    # TODO: 判断风险等级
    # - 如果 portfolio_volatility > vol_restrict，severity = 2
    # - 如果 portfolio_volatility > vol_warn，severity = 1
    # - 否则 severity = 0


    # TODO: 生成风险结论
    finding = {
        "severity": 0,  # TODO: 填充实际值
        "summary": "",  # TODO: 填充风险摘要
        "evidence": {
            "portfolio_volatility": portfolio_volatility,
            # TODO: 添加更多证据
        },
        "recommendation": ""  # TODO: 填充建议
    }

    # TODO: 更新 state
    state["finding_market"] = finding

    return state
```

**其他3个文件请参考此模板，修改对应的指标和阈值名称。**

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 单元测试示例

```python
from src.chains.market import market_node

# 测试：低风险场景
state = {
    "snapshot_metrics": {
        "portfolio_volatility": 0.10
    }
}
result = market_node(state)
assert result["finding_market"]["severity"] == 0

# 测试：高风险场景
state = {
    "snapshot_metrics": {
        "portfolio_volatility": 0.30
    }
}
result = market_node(state)
assert result["finding_market"]["severity"] > 0

print("✅ market.py 测试通过")
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
| **文件数** | 2个 |
| **文件路径** | `src/agents/macro_agent.py`<br>`src/agents/compliance_agent.py` |
| **依赖模块** | 模块1, 3, 4 |
| **被依赖** | 模块8 |

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

### 文件1：`src/agents/macro_agent.py`

**实现宏观经济分析 Agent：**

1. **定义工具**：
   - `macro_timeseries`: 获取宏观时序数据（Tushare API）
   - `macro_search`: 搜索宏观文本

2. **创建 Agent**：
   - 使用 `create_react_agent` 创建 ReAct Agent
   - 配置工具白名单

3. **实现节点函数**：
   - `macro_node(state: RiskState) -> RiskState`
   - 构建提示词，运行 Agent，解析输出

### 文件2：`src/agents/compliance_agent.py`

**实现合规风险分析 Agent：**

1. **定义工具**：
   - `policy_search`: 检索合规文本（RAG，返回片段化上下文）
   - `allowlist_check`: 检查禁投清单

2. **创建 Agent**：
   - 使用 `create_react_agent` 创建 ReAct Agent
   - 配置工具白名单

3. **实现节点函数**：
   - `compliance_node(state: RiskState, llm=None, config=None) -> RiskState`
   - 构建提示词，运行 Agent，解析输出
   - **要求 evidence 至少包含 1 条 `rag:doc[i]` 引用**

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/agents/macro_agent.py`

```python
"""
宏观经济分析 Agent
"""
from src.state import RiskState
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from src.config import RuntimeConfig, DEFAULT_CONFIG
from src.config import RuntimeConfig, DEFAULT_CONFIG


@tool
def macro_timeseries(indicator: str, start_date: str, end_date: str) -> dict:
    """
    获取宏观时序数据（Tushare API）

    Args:
        indicator: 指标代码（如 "SHIBOR3M", "USD_CNY"）
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        时序数据字典
    """
    # TODO: 实现宏观时序数据获取
    # - 使用 Tushare API 获取数据
    # - 返回时序数据
    pass


@tool
def macro_search(query: str, top_k: int = 3) -> list:
    """
    搜索宏观文本

    Args:
        query: 搜索查询
        top_k: 返回结果数量

    Returns:
        相关文本列表
    """
    # TODO: 实现宏观文本搜索
    # - 从宏观文本库中检索相关内容
    # - 返回 top_k 条结果
    pass


def macro_node(state: RiskState, llm=None, config: RuntimeConfig | None = None) -> RiskState:
    """
    宏观经济分析 Agent

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 创建 Agent
    # - 定义工具列表：[macro_timeseries, macro_search]
    # - 创建 LLM
    # - 使用 create_react_agent 创建 Agent


    # TODO: 构建提示词
    # - 说明 Agent 的任务：评估宏观环境对组合的影响
    # - 提供组合信息、当前日期等上下文


    # TODO: 运行 Agent
    # - 调用 Agent
    # - 获取分析结果


    # TODO: 解析输出
    # - 提取 severity (0-3)
    # - 提取 summary
    # - 提取 evidence
    # - 提取 recommendation


    # TODO: 更新 state
    finding = {
        "severity": 0,
        "summary": "",
        "evidence": {},
        "recommendation": ""
    }
    state["finding_macro"] = finding

    return state
```

### 文件2：`src/agents/compliance_agent.py`

```python
"""
合规风险分析 Agent
"""
from src.state import RiskState
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent


@tool
def policy_search(query: str, top_k: int = 3) -> list:
    """
    检索合规文本

    Args:
        query: 搜索查询
        top_k: 返回结果数量

    Returns:
        相关政策文本列表（含片段化内容，供 LLM 引用）
    """
    # TODO: 实现合规文本检索
    # - 从合规文本库中检索相关内容
    # - 支持向量检索或关键词检索
    # - 返回 top_k 条结果
    pass


@tool
def allowlist_check(etf_codes: list) -> dict:
    """
    检查禁投清单

    Args:
        etf_codes: ETF 代码列表

    Returns:
        禁投清单检查结果
    """
    # TODO: 实现禁投清单检查
    # - 检查 ETF 是否在禁投清单中
    # - 返回检查结果
    pass


def compliance_node(state: RiskState, llm=None, config: RuntimeConfig | None = None) -> RiskState:
    """
    合规风险分析 Agent

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 创建 Agent
    # - 定义工具列表：[policy_search, allowlist_check]
    # - 创建 LLM
    # - 使用 create_react_agent 创建 Agent


    # TODO: 构建提示词
    # - 说明 Agent 的任务：评估合规风险
    # - 提供组合信息、交易意图等上下文


    # TODO: 运行 Agent
    # - 调用 Agent
    # - 获取分析结果


    # TODO: 解析输出
    # - 提取 severity (0-3)
    # - 提取 summary
    # - 提取 evidence（必须包含 rag:doc[i]）
    # - 提取 blocklist（禁投清单）


    # TODO: 更新 state
    finding = {
        "severity": 0,
        "summary": "",
        "evidence": {},
        "recommendation": "",
        "blocklist": []
    }
    state["finding_compliance"] = finding

    return state
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
from src.agents.macro_agent import macro_node

state = {
    "normalized": {
        "targets": {"159213": 0.5, "159959": 0.5}
    },
    "intent": {
        "date": "2025-11-15"
    }
}

result = macro_node(state)
assert "finding_macro" in result
assert "severity" in result["finding_macro"]

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
| **文件数** | 2个 |
| **文件路径** | `src/skills_runtime.py`<br>`skills/*/SKILL.md` |
| **依赖模块** | 无 |
| **被依赖** | 模块4, 6 |

</details>

<details>
<summary><b>🎯 学习目标</b></summary>

完成本模块后，你将掌握：
- [ ] 配置驱动的系统设计
- [ ] Markdown 文件解析
- [ ] JSON Schema 应用
- [ ] 提示词工程最佳实践

</details>

<details>
<summary><b>📖 功能说明</b></summary>

本模块实现 Skills 配置体系，将提示词、工具权限、输出结构做成可配置的技能包。

**核心功能：**
1. **技能加载**：从 SKILL.md 读取技能配置
2. **Schema 管理**：加载和验证输出 Schema
3. **工具白名单**：提取允许调用的工具列表
4. **提示词渲染**：支持模板变量替换

**为什么重要：**
Skills 体系提高了系统的可维护性和可扩展性，便于调整提示词和工具配置。

</details>

<details>
<summary><b>✅ 实现要求</b></summary>

### 文件1：`src/skills_runtime.py`

**实现 Skills 运行时函数：**

1. `load_skill(skill_name: str) -> dict`
   - 读取 SKILL.md
   - 解析技能配置

2. `load_output_schema(skill_name: str) -> dict`
   - 读取 output.schema.json
   - 返回 JSON Schema

3. `get_tool_whitelist(skill_name: str) -> list`
   - 提取工具白名单

4. `render_prompt(template: str, context: dict) -> str`
   - 渲染提示词模板

### 文件2：`skills/*/SKILL.md`

**创建技能定义文件：**

包含以下部分：
1. 技能描述
2. 提示词模板
3. 工具白名单
4. 输出结构
5. 可复用片段引用

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/skills_runtime.py`

```python
"""
Skills 运行时模块
"""
import os
import json
from typing import Dict, Any, List


def load_skill(skill_name: str) -> Dict[str, Any]:
    """
    加载技能配置

    Args:
        skill_name: 技能名称（如 "macro-tool-calling"）

    Returns:
        技能配置字典
    """
    skill_dir = f"skills/{skill_name}"

    # TODO: 读取 SKILL.md
    # skill_md_path = os.path.join(skill_dir, "SKILL.md")
    # with open(skill_md_path, "r") as f:
    #     skill_content = f.read()


    # TODO: 解析 SKILL.md
    # - 提取技能描述
    # - 提取提示词模板
    # - 提取工具白名单
    # - 提取输出 Schema 引用


    # TODO: 加载输出 Schema
    # schema = load_output_schema(skill_name)


    # TODO: 返回技能配置
    skill_config = {
        "name": skill_name,
        "description": "",  # TODO: 填充
        "prompt_template": "",  # TODO: 填充
        "tool_whitelist": [],  # TODO: 填充
        "output_schema": {}  # TODO: 填充
    }

    # return skill_config
    pass


def load_output_schema(skill_name: str) -> Dict[str, Any]:
    """
    加载输出 Schema

    Args:
        skill_name: 技能名称

    Returns:
        JSON Schema 字典
    """
    # TODO: 读取 output.schema.json
    # schema_path = f"skills/{skill_name}/output.schema.json"
    # with open(schema_path, "r") as f:
    #     schema = json.load(f)


    # TODO: 返回 Schema
    # return schema
    pass


def get_tool_whitelist(skill_name: str) -> List[str]:
    """
    获取工具白名单

    Args:
        skill_name: 技能名称

    Returns:
        工具名称列表
    """
    # TODO: 从 SKILL.md 提取工具白名单
    # - 解析 SKILL.md 中的工具列表
    # - 返回工具名称列表
    pass


def render_prompt(template: str, context: Dict[str, Any]) -> str:
    """
    渲染提示词模板

    Args:
        template: 提示词模板
        context: 上下文变量

    Returns:
        渲染后的提示词
    """
    # TODO: 实现模板渲染
    # - 使用 context 中的变量替换模板中的占位符
    # - 返回渲染后的提示词
    pass
```

### 文件2：`skills/*/SKILL.md` 示例

```markdown
# Skill: macro-tool-calling

## 技能描述

**名称：** 宏观工具调用代理

**功能：** 使用工具调用获取宏观时序数据和文本，评估宏观环境对投资组合的影响

**使用场景：** 宏观风险分析节点

---

## 提示词模板

### 系统提示词

你是一个宏观经济分析专家，负责评估宏观环境对 ETF 投资组合的影响。

你可以使用以下工具：
- macro_timeseries: 获取宏观时序数据
- macro_search: 搜索宏观文本

请分析当前宏观环境，并给出风险评估。

### 用户提示词模板

当前日期：{asof_date}
投资组合：{portfolio}

请评估宏观环境对该组合的影响，包括：
1. 利率环境
2. 汇率波动
3. 政策变化

---

## 工具白名单

- macro_timeseries
- macro_search

---

## 输出结构

参考：`output.schema.json`

输出字段：
- severity: 风险等级（0-3）
- summary: 风险摘要
- evidence: 证据数据
- recommendation: 建议

---

## 可复用片段

引用：`snippets/evidence_rules.md`
引用：`snippets/decision_rubric.md`

---

## 注意事项

1. 必须提供证据支持结论
2. severity 必须基于客观数据
3. 建议必须具体可执行
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试技能加载

```python
from src.skills_runtime import load_skill

skill = load_skill("macro-tool-calling")
assert skill["name"] == "macro-tool-calling"
assert len(skill["tool_whitelist"]) > 0

print("✅ 技能加载测试通过")
```

### 测试提示词渲染

```python
from src.skills_runtime import render_prompt

template = "当前日期：{date}，组合：{portfolio}"
context = {"date": "2025-11-15", "portfolio": "ETF组合"}
result = render_prompt(template, context)
assert "2025-11-15" in result

print("✅ 提示词渲染测试通过")
```

**检查项：**
- [ ] 技能文件正确加载
- [ ] Schema 验证正常
- [ ] 工具白名单提取正确
- [ ] 提示词渲染正常

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **Markdown 解析**：可以使用简单的字符串分割，或使用 `markdown` 库
2. **模板渲染**：可以使用 `str.format()` 或 `jinja2`
3. **Schema 验证**：使用 `jsonschema` 库验证输出

**常见错误：**
- ❌ 文件路径错误
- ❌ Markdown 解析不完整
- ❌ 模板变量未替换

**优化建议：**
- 缓存已加载的技能配置
- 使用 Jinja2 支持更复杂的模板
- 添加 Schema 验证

**参考资源：**
- 样本答案中的 `skills/` 目录
- [JSON Schema 文档](https://json-schema.org/)

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

**实现规则加载函数：**

1. `load_rules(profile: str, config: RuntimeConfig | None) -> dict`
   - 从 rules.yaml 加载规则
   - 支持多个风险偏好配置
   - 规则路径由配置注入（CSV_DATA_DIR）

2. `get_blocklist(profile: str, config: RuntimeConfig | None) -> list`
   - 从规则中提取禁投清单

3. `get_rule_value(rules, key, default) -> Any`
   - 获取规则值（带默认值）

### 文件2：`src/tools/constraints.py`

**实现 `constraints_node(state: RiskState) -> RiskState`**

评估逻辑：
1. 加载规则配置
2. 获取当前指标
3. 评估各类约束（波动率、HHI、流动性等）
4. 分类约束（hard/soft）
5. 生成约束列表

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/rules.py`

```python
"""
规则加载与管理模块
"""
import yaml
from typing import Dict, Any
from pathlib import Path
from src.config import RuntimeConfig, DEFAULT_CONFIG


def load_rules(profile: str = "default", config: RuntimeConfig | None = None) -> Dict[str, Any]:
    """
    加载规则配置

    Args:
        profile: 风险偏好配置（default/conservative）

    Returns:
        规则字典
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 读取 rules.yaml
    # - 从 runtime.csv_data_dir 读取数据目录
    # rules_path = Path(runtime.csv_data_dir) / "rules.yaml"
    # with open(rules_path, "r") as f:
    #     rules_data = yaml.safe_load(f)


    # TODO: 获取指定 profile 的规则
    # rules = rules_data.get(profile, {})


    # TODO: 返回规则字典
    # return rules
    pass


def get_blocklist(profile: str = "default", config: RuntimeConfig | None = None) -> list:
    """
    获取禁投清单
    """
    # TODO: 复用 load_rules 获取 blocklist
    pass


def get_rule_value(rules: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    获取规则值（带默认值）

    Args:
        rules: 规则字典
        key: 规则键
        default: 默认值

    Returns:
        规则值
    """
    # TODO: 实现规则值获取
    # - 从 rules 字典中获取 key 对应的值
    # - 如果不存在，返回 default
    pass
```

### 文件2：`src/tools/constraints.py`

```python
"""
约束评估模块
"""
from src.state import RiskState
from src.tools.rules import load_rules
from typing import List, Dict, Any
from src.config import RuntimeConfig, DEFAULT_CONFIG


def constraints_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    评估硬约束，生成约束列表

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 加载规则
    context = state.get("context", {})
    profile = context.get("policy_profile", "default")
    rules = load_rules(profile, runtime)

    # TODO: 获取当前指标
    snapshot = state.get("snapshot_metrics", {})

    binding_constraints = []
    rule_violations = {}

    # TODO: 评估波动率约束
    # - 获取 portfolio_volatility
    # - 对比 volatility_warn 和 volatility_restrict
    # - 如果违规，添加到 binding_constraints


    # TODO: 评估 HHI 约束
    # - 获取 hhi
    # - 对比 hhi_warn 和 hhi_restrict
    # - 如果违规，添加到 binding_constraints


    # TODO: 评估有效持仓数约束
    # - 获取 effective_n
    # - 对比 effective_n_warn 和 effective_n_restrict
    # - 注意：有效持仓数是"越大越好"
    # - 如果违规，添加到 binding_constraints


    # TODO: 评估流动性约束
    # - 获取 weighted_spread 和 weighted_adv
    # - 对比相应阈值
    # - 如果违规，添加到 binding_constraints


    # TODO: 评估合规约束
    # - 检查是否有禁投清单
    # - 如果有，添加到 binding_constraints（hard 约束）


    # TODO: 分类约束
    # 将约束分为 hard 和 soft：
    # - hard: 必须满足（block 级别）
    # - soft: 建议满足（warn/restrict 级别）


    # TODO: 更新 state
    state["binding_constraints"] = binding_constraints
    state["rule_violations"] = rule_violations

    return state


def evaluate_constraint(
    value: float,
    warn_threshold: float,
    restrict_threshold: float,
    reverse: bool = False
) -> Dict[str, Any]:
    """
    评估单个约束

    Args:
        value: 当前值
        warn_threshold: 预警阈值
        restrict_threshold: 限制阈值
        reverse: 是否反向（越小越好）

    Returns:
        约束评估结果
    """
    # TODO: 实现约束评估逻辑
    # - 判断是否违反阈值
    # - 返回违规等级（none/warn/restrict）
    # - 返回违规详情
    pass
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试规则加载

```python
from src.tools.rules import load_rules

rules = load_rules("default")
assert "volatility_warn" in rules
assert "hhi_restrict" in rules

print("✅ 规则加载测试通过")
```

### 测试约束评估

```python
from src.tools.constraints import constraints_node

state = {
    "context": {"policy_profile": "default"},
    "snapshot_metrics": {
        "portfolio_volatility": 0.30,  # 假设超过阈值
        "hhi": 0.50
    }
}

result = constraints_node(state)
assert len(result["binding_constraints"]) > 0

print("✅ 约束评估测试通过")
```

**检查项：**
- [ ] 规则文件正确加载
- [ ] 约束评估逻辑正确
- [ ] hard/soft 分类合理

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **YAML 加载**：使用 `yaml.safe_load()` 而不是 `yaml.load()`
2. **约束分类**：
   - hard: 合规禁投清单
   - soft: 其他所有规则
3. **反向指标**：有效持仓数、ADV 判断逻辑需要反向

**常见错误：**
- ❌ YAML 文件路径错误
- ❌ 反向指标判断逻辑错误
- ❌ 约束分类不清晰

**参考资源：**
- [PyYAML 文档](https://pyyaml.org/wiki/PyYAMLDocumentation)
- 样本答案中的规则配置

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

**实现 `reducer_node(state: RiskState) -> RiskState`**

- 收集所有 `finding_*` 字段
- 统计各风险等级的数量
- 找出最高风险等级
- 汇总所有建议

### 文件2：`src/tools/decision.py`

**实现 `decision_node(state: RiskState) -> RiskState`**

决策逻辑：
1. 硬规则优先（rule_level）
2. 风险报告兜底（report_level）
3. 输出：pass/warn/restrict/block

### 文件3：`src/tools/solver.py`

**实现 `solver_node(state: RiskState) -> RiskState`**

- 仅在 decision=restrict 时运行
- 使用 CVXPY 构建优化问题
- 生成满足约束的调仓建议

### 文件4：`src/tools/audit.py`

**实现 `audit_node(state: RiskState) -> RiskState`**

- 记录决策过程
- 统计执行信息
- 生成 trace_id

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/chains/reducer.py`

```python
"""
结果汇总模块
"""
from src.state import RiskState


def reducer_node(state: RiskState) -> RiskState:
    """
    汇总所有分析结果

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # TODO: 收集所有 finding_* 字段
    findings = {}
    for key in ["market", "concentration", "diversification", "liquidity", "macro", "compliance"]:
        finding_key = f"finding_{key}"
        if finding_key in state:
            findings[key] = state[finding_key]

    # TODO: 生成综合风险报告
    # - 统计各风险等级的数量
    # - 找出最高风险等级
    # - 汇总所有建议

    risk_summary = {
        "findings": findings,
        "max_severity": 0,  # TODO: 填充最高风险等级
        "risk_count": {},  # TODO: 填充各等级风险数量
        "all_recommendations": []  # TODO: 填充所有建议
    }

    # TODO: 更新 state
    state["risk_summary"] = risk_summary

    return state
```

### 文件2：`src/tools/decision.py`

```python
"""
决策引擎模块
"""
from src.state import RiskState


def decision_node(state: RiskState) -> RiskState:
    """
    决策引擎，给出最终决策

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # TODO: 获取约束违规情况
    binding_constraints = state.get("binding_constraints", [])

    # TODO: 获取风险报告
    risk_summary = state.get("risk_summary", {})
    max_severity = risk_summary.get("max_severity", 0)

    # TODO: 决策逻辑
    # 1. 硬规则优先（rule_level）
    #    - 如果有 hard 约束违规，decision = "block"
    #    - 如果有 soft 约束违规，decision = "restrict"

    # 2. 风险报告兜底（report_level）
    #    - 如果 max_severity == 3，decision = "block"
    #    - 如果 max_severity == 2，decision = "restrict"
    #    - 如果 max_severity == 1，decision = "warn"
    #    - 如果 max_severity == 0，decision = "pass"

    decision = "pass"  # TODO: 填充实际决策

    # TODO: 更新 state
    state["decision"] = decision

    return state
```

### 文件3：`src/tools/solver.py`

```python
"""
约束求解器模块（CVXPY）
"""
from src.state import RiskState
import cvxpy as cp
import numpy as np
from src.config import RuntimeConfig, DEFAULT_CONFIG


def solver_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    约束求解器（restrict 时触发）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    decision = state.get("decision")

    # 仅在 restrict 时运行
    if decision != "restrict":
        return state

    # TODO: 获取当前持仓和目标持仓
    normalized = state.get("normalized", {})
    current_positions = normalized.get("current_positions", {})
    targets = normalized.get("targets", {})

    # TODO: 获取约束条件
    binding_constraints = state.get("binding_constraints", [])

    # TODO: 构建优化问题
    # - 决策变量：新的持仓权重
    # - 目标函数：最小化与目标持仓的偏差 + 换手惩罚
    # - 可使用 runtime.lp_turnover_weight / runtime.lp_solver / runtime.target_holdings
    # - 约束条件：
    #   1. 权重和为 1
    #   2. 权重非负
    #   3. 满足所有 binding_constraints


    # TODO: 求解优化问题
    # - 使用 CVXPY 求解
    # - 获取最优解


    # TODO: 生成调仓建议
    recommended_actions = []
    # TODO: 对比当前持仓和最优解，生成调仓建议列表

    # TODO: 更新 state
    state["recommended_actions"] = recommended_actions

    return state
```

### 文件4：`src/tools/audit.py`

```python
"""
审计日志模块
"""
from src.state import RiskState
import uuid
from datetime import datetime
from src.config import RuntimeConfig, DEFAULT_CONFIG


def audit_node(state: RiskState, config: RuntimeConfig | None = None) -> RiskState:
    """
    生成审计日志

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    runtime = config or DEFAULT_CONFIG
    # TODO: 收集审计信息
    audit = {
        "trace_id": str(uuid.uuid4().hex[:16]),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "policy_profile": state.get("context", {}).get("policy_profile", "default"),
        "ruleset_version": "rules.yaml",  # TODO: 可用 runtime 配置的规则路径

        # LLM 使用情况
        "llm_used": False,  # TODO: 检查是否使用了 LLM
        "llm_model": "",  # TODO: 填充 LLM 模型名称

        # 调度信息
        "gatekeeper_used": True,
        "gatekeeper_rationale": state.get("gatekeeper_rationale", ""),
        "supervisor_used": False,  # TODO: 检查是否使用了 supervisor
        "supervisor_rationale": state.get("supervisor_rationale", ""),

        # 节点执行情况
        "candidate_nodes": state.get("candidate_nodes", []),
        "nodes_to_run": state.get("nodes_to_run", []),

        # 统计信息
        "skills_used": 0,  # TODO: 统计使用的 skills 数量
        "node_outputs": 0,  # TODO: 统计节点输出数量
        "tool_calls": 0,  # TODO: 统计工具调用次数
        "tool_errors": 0,  # TODO: 统计工具错误次数
    }

    # TODO: 添加合规相关信息
    # - compliance_blocklist_soft
    # - compliance_industry_hits

    # TODO: 更新 state
    state["audit"] = audit

    return state
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试 Reducer

```python
from src.chains.reducer import reducer_node

state = {
    "finding_market": {"severity": 1},
    "finding_concentration": {"severity": 0},
    "finding_liquidity": {"severity": 2}
}

result = reducer_node(state)
assert result["risk_summary"]["max_severity"] == 2

print("✅ Reducer 测试通过")
```

### 测试 Decision

```python
from src.tools.decision import decision_node

# 测试：无风险
state = {"risk_summary": {"max_severity": 0}, "binding_constraints": []}
result = decision_node(state)
assert result["decision"] == "pass"

# 测试：高风险
state = {"risk_summary": {"max_severity": 2}, "binding_constraints": []}
result = decision_node(state)
assert result["decision"] == "restrict"

print("✅ Decision 测试通过")
```

**检查项：**
- [ ] Reducer 正确汇总所有风险
- [ ] Decision 逻辑符合要求
- [ ] Solver 能生成合理建议
- [ ] Audit 记录完整

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **决策优先级**：硬规则 > 风险报告
2. **CVXPY 基本用法**：
   ```python
   x = cp.Variable(n)
   objective = cp.Minimize(cp.sum_squares(x - target))
   constraints = [cp.sum(x) == 1, x >= 0]
   problem = cp.Problem(objective, constraints)
   problem.solve()
   ```
3. **审计完整性**：记录所有关键决策点

**常见错误：**
- ❌ 决策逻辑不完整
- ❌ CVXPY 约束定义错误
- ❌ 审计日志缺失关键信息

**参考资源：**
- [CVXPY 官方文档](https://www.cvxpy.org/)
- 样本答案中的决策逻辑

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

**实现 `calibrate_rules(asof_date, n_holdings, n_samples)` 函数**

校准流程：
1. 加载 ETF 数据
2. 随机抽样组合（Dirichlet 分布）
3. 计算组合指标
4. 生成阈值（分位数）
5. 保存到 rules.yaml

### 文件2：`src/tools/calibrate_macro_series.py`

**实现 `calibrate_macro_series(asof_date)` 函数**

校准流程：
1. 拉取宏观时序数据
2. 计算变化幅度
3. 生成阈值（分位数）
4. 保存到 macro_series.yaml

</details>

<details>
<summary><b>💻 代码模板</b></summary>

### 文件1：`src/tools/calibrate_rules.py`

```python
"""
组合规则阈值校准模块
"""
import pandas as pd
import numpy as np
from typing import Dict
import yaml


def calibrate_rules(asof_date: str, n_holdings: int, n_samples: int = 1000) -> None:
    """
    基于历史数据校准组合规则阈值

    Args:
        asof_date: 截止日期
        n_holdings: 目标持仓数量
        n_samples: 采样数量
    """
    # TODO: 加载 ETF 数据
    # - 使用 load_etf_data 加载行情数据
    # - 截断到 asof_date


    # TODO: 随机抽样组合
    # - 从 ETF 池中随机抽取 n_holdings 只 ETF
    # - 使用 Dirichlet(1,...,1) 生成随机权重
    # - 重复 n_samples 次


    # TODO: 计算组合指标
    # 对每个样本组合计算：
    # - 波动率（基于历史收益率）
    # - HHI 指数
    # - 有效持仓数
    # - 加权买卖价差
    # - 加权成交量（ADV）


    # TODO: 生成阈值
    # 对每个指标的分布取分位数：
    # - warn: 75th 分位数
    # - restrict: 90th 分位数
    # 注意：对于"越小越好"的指标（如有效持仓数），使用 25th/10th 分位数


    # TODO: 保存到 YAML
    rules = {
        "default": {
            "volatility_warn": 0.0,  # TODO: 填充实际值
            "volatility_restrict": 0.0,
            "hhi_warn": 0.0,
            "hhi_restrict": 0.0,
            "effective_n_warn": 0.0,
            "effective_n_restrict": 0.0,
            "spread_warn": 0.0,
            "spread_restrict": 0.0,
            "adv_warn": 0.0,
            "adv_restrict": 0.0,
        }
    }

    # with open("cufel_practice_data/rules.yaml", "w") as f:
    #     yaml.dump(rules, f)

    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof-date", required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--samples", type=int, default=1000)
    args = parser.parse_args()

    calibrate_rules(args.asof_date, args.n, args.samples)
```

### 文件2：`src/tools/calibrate_macro_series.py`

```python
"""
宏观序列阈值校准模块
"""
import tushare as ts
import pandas as pd
import numpy as np
import yaml
from typing import Dict


def calibrate_macro_series(asof_date: str) -> None:
    """
    基于宏观时序数据校准宏观指标阈值

    Args:
        asof_date: 截止日期
    """
    # TODO: 初始化 Tushare
    # pro = ts.pro_api()


    # TODO: 定义宏观指标列表
    indicators = [
        {"code": "SHIBOR3M", "name": "3个月SHIBOR"},
        {"code": "USD_CNY", "name": "美元兑人民币汇率"},
        # TODO: 添加更多指标
    ]


    # TODO: 拉取宏观时序数据
    # 对每个指标：
    # - 使用 Tushare API 拉取数据
    # - 截断到 asof_date
    # - 计算相邻两期的变化幅度


    # TODO: 生成阈值
    # 对每个指标的变化幅度分布取分位数：
    # - warn: 75th 分位数
    # - restrict: 90th 分位数


    # TODO: 保存到 YAML
    macro_config = {
        "series": []
        # TODO: 填充每个指标的配置
        # {
        #     "code": "SHIBOR3M",
        #     "name": "3个月SHIBOR",
        #     "warn_threshold": 0.0,
        #     "restrict_threshold": 0.0
        # }
    }

    # with open("cufel_practice_data/macro_series.yaml", "w") as f:
    #     yaml.dump(macro_config, f)

    pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof-date", required=True)
    args = parser.parse_args()

    calibrate_macro_series(args.asof_date)
```

</details>

<details>
<summary><b>🧪 测试检查</b></summary>

### 测试校准流程

```bash
# 校准组合规则
uv run --env-file .env -- python -u -m src.tools.calibrate_rules --asof-date 2025-11-14 --n 5 --samples 1000

# 校准宏观序列
uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series --asof-date 2025-11-14
```

**检查项：**
- [ ] rules.yaml 已生成
- [ ] macro_series.yaml 已生成
- [ ] 阈值数值合理
- [ ] warn < restrict

</details>

<details>
<summary><b>💡 提示与技巧</b></summary>

**关键点：**
1. **Dirichlet 分布**：
   ```python
   weights = np.random.dirichlet(np.ones(n_holdings))
   ```
2. **分位数计算**：
   ```python
   warn_threshold = np.percentile(values, 75)
   restrict_threshold = np.percentile(values, 90)
   ```
3. **反向指标**：有效持仓数、ADV 使用 25th/10th 分位数

**常见错误：**
- ❌ 采样数量太少导致阈值不稳定
- ❌ 反向指标分位数方向错误
- ❌ 时序数据变化幅度计算错误

**参考资源：**
- [Dirichlet 分布](https://en.wikipedia.org/wiki/Dirichlet_distribution)
- 样本答案中的校准脚本

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
