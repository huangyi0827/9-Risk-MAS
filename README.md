# 风控 MAS

## 项目概述
本仓库演示一个模块化风控服务：显式 State + 确定性工具 + 工具调用型 Agent + 审计。目的是把复杂决策拆成清晰的流水线：
- 校验与确定性工具
- 路由 + 分析链路 + 工具调用 Agent
- 汇总 + 决策 + 约束求解
- 可审计输出与溯源

## 核心结构
- **显式 State**：`src/state.py`，每个节点只写自己的 slot
- **确定性工具**：`src/tools/*`，校验、数据质量、快照、规则、决策
- **路由/链路**：`src/chains/*`，包含 gatekeeper、router、supervisor
- **工具调用 Agent**：`src/agents/*`，按技能与工具白名单执行
- **Skills 运行时**：`src/skills_runtime.py`，加载 `SKILL.md`、snippet、schema
- **审计**：`audit_log` 输出 hash、工具调用、skills 版本
  - 预留字段：`trade_calendar`、`account_type`、`jurisdiction`、`cost_budget`（为未来分账户/分辖区/成本控制扩展）

## 运行方式
本项目采用 `src/` 布局，直接运行即可。

默认输出表格（推荐）：
```bash
uv run --env-file .env -- python -u -m src.app
```

输出 JSON（按需）：
```bash
uv run --env-file .env -- python -u -m src.app -JSON --pretty
```

关闭 LLM 调度器：
```bash
ENABLE_SUPERVISOR=0 uv run --env-file .env -- python -u -m src.app
```

### 封装类使用（RiskMAS）
项目提供 `RiskMAS` 门面类，便于以库方式调用。

```python
from risk_mas import RiskMAS

mas = RiskMAS(output="table")
result = mas.run(intent=..., context=...)
print(result)
```

`output` 支持 `table` 或 `json`，也可用 `run_raw()` 获取原始 dict。

### 运行 test.py
```bash
uv run --env-file .env -- python -u test.py
```

## 数据与配置
### 环境变量清单
- `CSV_DATA_DIR`：CSV 数据目录（默认 `cufel_practice_data`）
- `SAMPLE_UNIVERSE_SIZE`：随机样本标的数
- `RANDOM_SEED`：随机种子
- `MARKET_LOOKBACK_DAYS`：行情回溯天数
- `ENABLE_SUPERVISOR`：是否启用 LLM 调度
- `OPENAI_API_KEY`：LLM API Key
- `LLM_MODEL`：模型名称
- `TUSHARE_TOKEN`：Tushare Token（宏观时序查询）
- `MACRO_SERIES_CONFIG`：宏观指标配置文件路径（默认 `cufel_practice_data/macro_series.yaml`）
- `AUM` / `PORTFOLIO_AUM`：组合 AUM
- `TARGET_HOLDINGS`：调仓建议的目标持仓数量
- `LP_TURNOVER_WEIGHT`：LP 中的换手惩罚权重
- `LP_SOLVER`：LP 求解器名称（如 `ECOS` / `OSQP`）

### 数据源（CSV）
- 默认读取 `cufel_practice_data/` 下的 CSV 文件
- 可用 `CSV_DATA_DIR=/path/to/csv` 指定自定义目录

### 规则配置
- 优先读取 `cufel_practice_data/rules.yaml`（无库时也可工作）
- 可用脚本按历史数据自动校准：
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_rules --asof-date 2025-11-14 --n 5
```

### 宏观阈值校准（Tushare）
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series --asof-date 2025-01-10
```

### 线性规划依赖
- `cvxpy` 为可选依赖；未安装时退回启发式求解。

### 随机样例输入
默认从数据库随机抽样 5 只标的（`SAMPLE_UNIVERSE_SIZE` 可改），生成初始持仓与交易意图。

## LLM（可选）
- 设置 `OPENAI_API_KEY` 才会启用工具调用 Agent。
- 设置 `LLM_MODEL` 选择模型（示例：`qwen3-max`）。

## 迁移指南（适配新数据源/资产类型）
1) 数据源适配  
   - 准备 CSV 文件并对齐字段：  
     - 行情：`date, code, open, high, low, close, amount`  
     - 合规文本：`title, date, content`  
     - 宏观文本（可选）：`title, date, content`  
   - 字段不一致时，修改 `src/tools/csv_data.py` 的解析逻辑  

2) 指标口径对齐  
   - 明确波动率是否年化  
   - 明确 `spread_bps` 的计算方式（建议用真实 bid-ask spread）  
   - 若有 AUM，接入以计算 `ADV 比例` 等执行类指标

3) 规则阈值校准  
   - 修改 `cufel_practice_data/rules.yaml` 或运行校准脚本：  
     ```bash
     uv run --env-file .env -- python -u -m src.tools.calibrate_rules --year 2025 --n 5
     ```

4) Skills 与工具权限  
   - 调整 `skills/*/SKILL.md` 中的 allowlist/snippets/schema  
   - 确保工具注册表 `skills/tools/tool_interfaces.yaml` 与实际工具一致

5) 审计与输出  
   - 保持 `audit` 结构一致，方便跨系统对账与复现  
   - 若需要最小输出，可只保留表格视图



## 目录结构（精简）
```
risk-mas/
  src/
    app.py                # CLI 入口：执行单次风控并输出表格/JSON
    graph.py              # LangGraph 编排（gatekeeper → router → supervisor → 各节点）
    state.py              # 显式 State 定义
    skills_runtime.py     # 读取 SKILL.md、snippets、schema 与工具白名单
    chains/               # 分析链路（market/concentration/diversification/liquidity 等）
    agents/               # 工具调用型 Agent（macro/compliance）
    tools/                # 确定性工具（校验、数据质量、快照、规则、决策、审计）

  cufel_practice_data/    # CSV 数据源（可用 CSV_DATA_DIR 指定）
    rules.yaml            # 本地规则阈值（优先使用）
    README.md             # 数据接入说明

  skills/
    */SKILL.md            # 各技能定义（prompt/snippets/allowlist）
    */output.schema.json  # 技能输出 schema
    snippets/             # 证据与决策提示片段
    tools/                # 工具注册表
```

## 目录结构（详细）
```
risk-mas/
  README.md               # 项目说明与运行方式
  pyproject.toml          # Python 依赖与工具配置
  uv.lock                 # 依赖锁定文件

  src/
    app.py                # CLI 入口：执行单次风控并输出表格/JSON
    graph.py              # LangGraph 编排（gatekeeper → router → supervisor → 各节点）
    state.py              # 定义全局 State 结构（统一所有节点输入输出字段）、保证编排一致性
    skills_runtime.py     # 读取 SKILL.md、snippets、schema 与工具白名单
    
    chains/
      gatekeeper.py       # 确定性裁剪候选节点（数据缺失则中断）
      router.py           # 路由（基于 gatekeeper 的候选 → nodes_to_run）
      supervisor.py       # LLM 调度，失效时回退到确定性候选列表（细化 nodes_to_run）
      market.py           # 市场风险链路（波动率）
      concentration.py    # 集中度链路（HHI、最大权重）
      diversification.py  # 分散度链路（有效持仓数：1/HHI）
      liquidity.py        # 流动性链路（日内振幅做近似）
      reducer.py          # 汇总 findings 与风险报告
      formatter.py        # 输出格式化（若使用）
    
    agents/
      macro_agent.py      # 宏观工具调用 Agent（macro_timeseries 对接 Tushare；macro_search 文本检索占位）
      compliance_agent.py # 可拓展合规 Agent（RAG 检索公告/规则/内部条款，生成禁投清单与结构化风险结论）
    
    tools/
      validate.py         # 早期输入校验与归一化（交易意图可为delta，也可为最终权重）
      data_quality.py     # 数据可用性/缺失检测
      snapshot.py         # 快照指标（波动、HHI、流动性等）（将行情/宏观数据转换成统一的风险指标）
      constraints.py      # 规则评估与硬约束
      decision.py         # 决策引擎（rule_level 优先 + report_level 兜底）
      solver.py           # 约束求解与调整建议
      rules.py            # 规则加载（rules.yaml）
      audit.py            # 审计输出
      csv_data.py         # CSV 数据读取与指标派生
      calibrate_rules.py  # 规则校准脚本（基于市场数据+大量随机组合模拟自动生成rules.yaml 的阈值）

  cufel_practice_data/    # CSV 数据源（行情/合规/宏观）
    rules.yaml            # 由 calibrate_rules.py 产生的规则阈值（优先使用）
    README.md             # 数据接入说明
    etf_2025_data.csv     # 行情数据
    sampled_etf_basic.csv # 标的基础信息
    csrc_2025.csv         # 合规公告示例
    govcn_2025.csv        # 宏观文本示例

  skills/                 #把提示词/输出结构/工具权限/证据规则做成可配置的技能包，供 skills_runtime.py 加载
    risk-market-assessor/
      SKILL.md            # 技能定义
      output.schema.json  # 输出 schema
      examples.json       # 示例（可选）
    
    liquidity-execution-assessor/
      SKILL.md
      output.schema.json
    
    macro-tool-calling/
      SKILL.md
      output.schema.json
    
    compliance-evidence/
      SKILL.md
      output.schema.json
      reference/          # 合规参考样例（可选）
    
    supervisor-router/
      SKILL.md
      output.schema.json
    
    snippets/
      evidence_rules.md   # 证据规则
      decision_rubric.md  # 决策标准
    
    schemas/
      common_io.schema.json # 通用 IO schema
    
    tools/
      tool_interfaces.yaml  # 工具注册表
```
