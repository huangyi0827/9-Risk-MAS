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

## 框架图
![Risk-mas框架图](Risk-mas框架图.png)

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

### 配置 .env 文件
在项目根目录创建 `.env`，用于配置模型与数据相关参数（示例）：
```env
LLM_PROVIDER=openai_compatible
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen3-max
OPENAI_API_KEY=sk-*************************************
TUSHARE_TOKEN=your_token
```
如不使用宏观时序（Tushare）或自定义数据目录，可省略对应项。

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
`test.py` 会根据交易目标 ETF 的数量自动校准 `rules.yaml`（使用交易意图日期的前一个交易日作为 `asof_date`）。

### 部分输出示例
```text
---------------------+------------------
 KEY                 | VALUE            
---------------------+------------------
 decision            | pass             
 binding_constraints | 0                
 recommended_actions | 0                
 recommendation      | none             
 llm_used            | True             
 llm_model           | qwen3-max        
 supervisor_used     | True             
 trace_id            | 08a46c02b4e7cbd8 
---------------------+------------------

-----------------+----------+-----------------------
 RISK            | SEVERITY | SUMMARY               
-----------------+----------+-----------------------
 market          | 0        | 组合波动率处于目标范围           
 concentration   | 0        | 组合集中度在合理范围内           
 diversification | 0        | 分散度较好                 
 liquidity       | 0        | 流动性状况可接受              
 macro           | 0        | 当前宏观环境稳定，无显著风险信号。     
 compliance      | 0        | 当前组合调整符合合规要求，未发现重大风险。 
-----------------+----------+-----------------------
----------------------+-------------------------------------------------------------------------------------
 AUDIT                | VALUE                                                                                                                                                                                        
----------------------+-------------------------------------------------------------------------------------
 policy_profile       | default                                                                                                                                                                                                                                    
 ruleset_version      | rules.yaml                                                                                                                                                                                                                                 
 llm_used             | True                                                                                                                                                                                                                                       
 llm_model            | qwen3-max                                                                                                                                                                                                                                  
 gatekeeper_used      | True                                                                                                                                                                                                                                       
 gatekeeper_rationale | ok                                                                                                                                                                                                                                         
 supervisor_used      | True                                                                                                                                                                                                                                       
 supervisor_rationale | 数据质量整体良好，宏观数据新鲜度达标，合规文本可用，且无规则层面的违规发现。尽管组合集中度有所下降（HHI 降低、有效持仓数增加），但当前 top_weight 仍较高，需保留 concentration 和 diversification 节点以评估结构变化；liquidity 节点因加权价差和 ADV 指标存在而有必要运行；market 和 macro 节点因数据完整且为默认策略组成部分而保留；compliance 节点无异常且为默认必选，故全部节点均应运行。 
 candidate_nodes      | market,concentration,diversification,liquidity,macro,compliance                                                                                                                                                                            
 nodes_to_run         | market,concentration,diversification,liquidity,macro,compliance                                                                                                                                                                            
 skills_used          | 4                                                                                                                                                                                                                                          
 node_outputs         | 35                                                                                                                                                                                                                                         
 tool_calls           | 3                                                                                                                                                                                                                                          
 tool_errors          | 0                                                                                                                                                                                                                                          
 tool_latency_ms      | 598                                                                                                                                                                                                                                        
 timestamp            | 2026-01-23T16:14:51.993594Z                                                                                                                                                                                                                
 trace_id             | 08a46c02b4e7cbd8                                                                                                                                                                                                                           
----------------------+-------------------------------------------------------------------------------------
--------------------------+-------------+-------------+--------
 RULE_KEY                 | VALUE       | CURRENT     | STATUS 
--------------------------+-------------+-------------+--------
 adv_restrict             | 12702.31067 | 25976.63354 | 达标     
 adv_warn                 | 23293.91059 | 25976.63354 | 达标     
 blocklist                | CCC         | none        | 达标     
 effective_n_restrict     | 2.20007     | 4.03708     | 达标     
 effective_n_warn         | 2.53444     | 4.03708     | 达标     
 hhi_restrict             | 0.45453     | 0.24770     | 达标     
 hhi_warn                 | 0.39457     | 0.24770     | 达标     
 max_hhi                  | 0.45453     | 0.24770     | 达标     
 ...
--------------------------+-------------+-------------+--------

---------------------------
 NODE_OUTPUT               
---------------------------
 binding_constraints       
 candidate_nodes           
 compliance_blocklist      
 compliance_blocklist_meta 
 cost_budget               
 data_gaps                 
 data_quality              
 decision                     
 ...    
---------------------------
```

## 用户输入与可配置项说明

本说明聚焦“用户可以主动输入/设定”的内容，包括：RiskMAS 调用参数、风险偏好、以及常用环境变量。

### 1) RiskMAS 的调用参数

#### 1.1 intent（交易意图）
必填字段：
- `date`：交易意图日期，格式 `YYYY-MM-DD`
- `mode`：`target` 或 `delta`
- `targets`：目标权重或增量权重（dict，`code -> weight`）

行为说明：
- `mode=target`：直接使用 `targets` 作为目标权重
- `mode=delta`：将 `targets` 视为调仓增量，叠加到 `current_positions`
- 权重若不满 1，会自动归一化并给出 warning

示例：
```python
intent = {
  "date": "2025-11-15",
  "mode": "target",
  "targets": {"159213": 0.25, "159959": 0.25, "511960": 0.2, "516310": 0.2, "561180": 0.1},
}
```

#### 1.2 context（组合上下文）
常用字段：
- `current_positions`：当前持仓（dict，`code -> weight`）
- `current_positions_date`：当前持仓日期（可选，用于新鲜度检查）
- `universe`：候选 ETF 池（可选，不传时自动从持仓+目标合并）
- `policy_profile`：风险偏好配置（默认 `default`，也可用保守型 `conservative`）
- `account_type` / `jurisdiction`：预留字段（用于将来分账户/分辖区规则）
- `aum` / `portfolio_aum`：组合 AUM（用于 ADV 比例等执行类指标）

示例：
```python
context = {
  "current_positions": {"159213": 0.2, "159959": 0.2, "511960": 0.2, "516310": 0.2, "561180": 0.2},
  "current_positions_date": "2025-11-14",
  "policy_profile": "default",
  "aum": 1000000.0,
}
```

#### 1.3 RiskMAS 构造参数
- `llm`：可直接传入 LLM 实例（不传则按环境变量加载）
- `output`：`table` 或 `json`，决定返回表格还是 JSON 字符串，后者包含完整审计与细节字段
- `pretty`：JSON 是否美化（pretty=True：带缩进/换行，便于阅读；pretty=False：紧凑单行，便于传输与存储；默认 `False`）
- `use_env_llm`：是否从环境变量读取 LLM 配置（默认 `True`）

示例：
```python
from risk_mas import RiskMAS

mas = RiskMAS(output="table")
result = mas.run(intent=intent, context=context)
print(result)
```

### 2) asof_date 的取值规则

- `asof_date` 会根据 `intent.date` 自动映射为“上一个交易日”（基于 CSV 数据中的交易日序列）。
- 该日期用于截断行情/宏观/合规数据，避免使用未来数据。
- 若找不到更早交易日，则回退到 `intent.date`。

### 2.1 数据质量口径

- `data_quality.market`：ETF 主表缺失、行情缺失（含 missing_etf_master / missing_market）。
- `data_quality.macro`：
  - `timeseries_available`：是否具备宏观时序来源（`TUSHARE_TOKEN`）。
  - `text_available`：是否具备宏观文本来源（CSV）。
  - `latest_date / freshness_days / freshness_status`：新鲜度口径（`freshness_days = asof_date - latest_date`，future/stale/ok/unknown）。
  - 若文本日期晚于 asof_date，写入 `data_gaps` 为 block 级别（防止未来信息泄露）。
- `data_quality.compliance.text_available`：合规文本是否可用。
- `data_quality.positions.freshness_days`：当前持仓日期的新鲜度。
- Gatekeeper 仅在 `macro.timeseries_available` 为真时纳入宏观节点；合规模块需要 `compliance.text_available`。

### 3) 环境变量清单

#### 数据与采样
- `CSV_DATA_DIR`：CSV 数据目录（默认 `cufel_practice_data`）
- `SAMPLE_UNIVERSE_SIZE`：随机样本 ETF 数
- `RANDOM_SEED`：随机种子
- `MARKET_LOOKBACK_DAYS`：行情回溯天数

#### LLM
- `OPENAI_API_KEY`：LLM API Key
- `LLM_MODEL`：模型名称
- `ENABLE_SUPERVISOR`：是否启用 LLM 调度（0/1）

#### 宏观时序
- `TUSHARE_TOKEN`：Tushare Token（宏观时序查询），缺失则宏观节点不进入候选
- `MACRO_SERIES_CONFIG`：宏观指标配置路径（默认 `cufel_practice_data/macro_series.yaml`）
- `MACRO_STALE_DAYS`：宏观文本数据陈旧阈值（默认 30 天）

#### 组合执行与 LP
- `AUM` / `PORTFOLIO_AUM`：组合 AUM
- `TARGET_HOLDINGS`：调仓建议目标持仓数量
- `LP_TURNOVER_WEIGHT`：LP 中换手惩罚权重
- `LP_SOLVER`：LP 求解器名称（如 `ECOS` / `OSQP`）

### 4) 风险偏好（policy_profile）

- 通过 `context.policy_profile` 选择：`default` 或 `conservative`
- 规则来源：`cufel_practice_data/rules.yaml`

### 5) 阈值文件说明（原理与更新方式）

#### 5.1 rules.yaml（组合规则阈值）
原理：
- 在历史窗口内随机抽样组合：从 ETF 池随机抽取 n 只，使用 Dirichlet(1,...,1) 生成权重
- 计算组合指标并形成经验分布（波动率、HHI、ADV、spread 等）
- 波动率口径：优先使用复权价（`adj_close = close * adj_factor`）计算收益率与波动率
- 对指标分布取分位数生成 `warn/restrict` 阈值（高方向：90%/98%，低方向：10%/2%）

手动更新方式：
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_rules --asof-date <ASOF_DATE>（这里填交易意图日期的前一个交易日） --n （这里填交易意图的ETF数量）
```

#### 5.2 macro_series.yaml（宏观阈值配置）
原理：
- 拉取宏观时序数据，并按 `asof_date` 截断
- 计算相邻两期的变化幅度（`change_mode=abs` 用绝对差；`pct` 用相对变化）
- 若 `change_scale=bp`，将变化幅度转换为 bp
- 对变化幅度分布取分位数生成阈值（默认 warn=90%，restrict=98%）

手动更新方式：
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series --asof-date <ASOF_DATE>（同上）
```

### 6) 最小可运行样例
```python
from risk_mas import RiskMAS

intent = {
  "date": "2025-11-15",
  "mode": "target",
  "targets": {"159213": 0.25, "159959": 0.25, "511960": 0.2, "516310": 0.2, "561180": 0.1},
}

context = {
  "current_positions": {"159213": 0.2, "159959": 0.2, "511960": 0.2, "516310": 0.2, "561180": 0.2},
  "policy_profile": "default",
  "aum": 1000000.0,
}

mas = RiskMAS(output="table")
print(mas.run(intent=intent, context=context))
```

## 数据源（CSV）
- 默认读取 `cufel_practice_data/` 下的 CSV 文件
- 可用 `CSV_DATA_DIR=/path/to/csv` 指定自定义目录

## 线性规划依赖
- `cvxpy` 为可选依赖；未安装时退回启发式求解。

## 迁移指南（适配新数据源/资产类型）
1) 数据源与字段对齐  
   - 按“用户输入与可配置项说明”的字段口径准备 CSV  
   - 若字段不一致，修改 `src/tools/csv_data.py` 的解析逻辑  

2) 阈值与校准  
   - 组合阈值：`cufel_practice_data/rules.yaml`  

3) Skills 与工具权限  
   - 调整 `skills/*/SKILL.md` 的 allowlist/snippets/schema 与 evidence_prefixes  
   - 确保 `skills/tools/tool_interfaces.yaml` 与实际工具一致  

4) 审计与输出  
   - 保持 `audit` 结构一致，便于对账与复现  



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
      gatekeeper.py       # 确定性裁剪候选节点（宏观需时序可用，合规需文本可用）
      router.py           # 路由（基于 gatekeeper 的候选 → nodes_to_run）
      supervisor.py       # LLM 调度，失效时回退到确定性候选列表（细化 nodes_to_run）
      market.py           # 市场风险链路（波动率）
      concentration.py    # 集中度链路（HHI、最大权重）
      diversification.py  # 分散度链路（有效持仓数：1/HHI）
      liquidity.py        # 流动性链路（日内振幅做近似）
      reducer.py          # 汇总 findings 与风险报告
    
    agents/
      macro_agent.py      # 宏观工具调用 Agent（macro_timeseries 对接 Tushare；macro_search 文本检索占位）
      compliance_agent.py # 可拓展合规 Agent（RAG 检索公告/规则/内部条款，生成禁投清单与结构化风险结论）
    
    tools/
      validate.py         # 早期输入校验与归一化（交易意图可为delta，也可为最终权重）
      data_quality.py     # 数据可用性/缺失/新鲜度口径（market/macro/compliance/positions）
      snapshot.py         # 快照指标（波动、HHI、流动性等）（将行情/宏观数据转换成统一的风险指标）
      constraints.py      # 规则评估与硬约束
      decision.py         # 决策引擎（rule_level 优先 + report_level 兜底）
      solver.py           # 约束求解与调整建议（目标持仓的种类数与输入的交易意图一致）
      rules.py            # 规则加载（rules.yaml）
      audit.py            # 审计输出
      csv_data.py         # CSV 数据读取与指标派生
      calibrate_rules.py  # 规则校准脚本（基于市场数据+大量随机组合模拟自动生成rules.yaml 的阈值）
      calibrate_macro_series.py # 宏观时序阈值校准脚本（基于时序变化分位数）

  cufel_practice_data/    # CSV 数据源（行情/合规/宏观）
    rules.yaml            # 由 calibrate_rules.py 产生的规则阈值（优先使用）
    README.md             # 数据接入说明
    etf_2025_data.csv     # 行情数据
    sampled_etf_basic.csv # ETF 基础信息
    csrc_2025.csv         # 合规公告示例
    govcn_2025.csv        # 宏观文本示例
    govcn_2025_results.json # 宏观情绪分析结果（如何实现请参见NLP章节练习，本练不再赘述）

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
