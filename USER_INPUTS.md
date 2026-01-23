# 用户输入与可配置项说明

本说明聚焦“用户可以主动输入/设定”的内容，包括：RiskMAS 调用参数、风险偏好、以及常用环境变量。

## 1) RiskMAS 的调用参数

### 1.1 intent（交易意图）
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

### 1.2 context（组合上下文）
常用字段：
- `current_positions`：当前持仓（dict，`code -> weight`）
- `current_positions_date`：当前持仓日期（可选，用于新鲜度检查）
- `universe`：候选 ETF 池（可选，不传时自动从持仓+目标合并）
- `benchmark`：基准代码（可选）
- `policy_profile`：风险偏好配置（默认 `default`，也可用保守型 `conservative`）
- `account_type` / `jurisdiction`：预留字段（用于将来分账户/分辖区规则）
- `aum` / `portfolio_aum`：组合 AUM（用于 ADV 比例等执行类指标）

示例：
```python
context = {
  "current_positions": {"159213": 0.2, "159959": 0.2, "511960": 0.2, "516310": 0.2, "561180": 0.2},
  "current_positions_date": "2025-11-14",
  "policy_profile": "default",
  "benchmark": "510300",
  "aum": 1000000.0,
}
```

### 1.3 RiskMAS 构造参数
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

## 2) asof_date 的取值规则

- `asof_date` 会根据 `intent.date` 自动映射为“上一个交易日”（基于 CSV 数据中的交易日序列）。
- 该日期用于截断行情/宏观/合规数据，避免使用未来数据。
- 若找不到更早交易日，则回退到 `intent.date`。

## 2.1 数据质量口径（统一）

- `data_quality.market`：ETF 主表缺失、行情缺失（含 missing_etf_master / missing_market）。
- `data_quality.macro`：
  - `timeseries_available`：是否具备宏观时序来源（`TUSHARE_TOKEN`）。
  - `text_available`：是否具备宏观文本来源（CSV）。
  - `latest_date / freshness_days / freshness_status`：新鲜度口径（`freshness_days = asof_date - latest_date`，future/stale/ok/unknown）。
  - 若文本日期晚于 asof_date，写入 `data_gaps` 为 block 级别（不改变全局 status）。
- `data_quality.compliance.text_available`：合规文本是否可用。
- `data_quality.positions.freshness_days`：当前持仓日期的新鲜度。
- Gatekeeper 仅在 `macro.timeseries_available` 为真时纳入宏观节点；合规模块需要 `compliance.text_available`。

## 3) 环境变量清单

### 数据与采样
- `CSV_DATA_DIR`：CSV 数据目录（默认 `cufel_practice_data`）
- `SAMPLE_UNIVERSE_SIZE`：随机样本 ETF 数
- `RANDOM_SEED`：随机种子
- `MARKET_LOOKBACK_DAYS`：行情回溯天数

### LLM
- `OPENAI_API_KEY`：LLM API Key
- `LLM_MODEL`：模型名称
- `ENABLE_SUPERVISOR`：是否启用 LLM 调度（0/1）

### 宏观时序
- `TUSHARE_TOKEN`：Tushare Token（宏观时序查询），缺失则宏观节点不进入候选
- `MACRO_SERIES_CONFIG`：宏观指标配置路径（默认 `cufel_practice_data/macro_series.yaml`）
- `MACRO_STALE_DAYS`：宏观文本数据陈旧阈值（默认 30 天）

### 组合执行与 LP
- `AUM` / `PORTFOLIO_AUM`：组合 AUM
- `TARGET_HOLDINGS`：调仓建议目标持仓数量
- `LP_TURNOVER_WEIGHT`：LP 中换手惩罚权重
- `LP_SOLVER`：LP 求解器名称（如 `ECOS` / `OSQP`）

## 4) 风险偏好（policy_profile）

- 通过 `context.policy_profile` 选择：`default` 或 `conservative`
- 规则来源：`cufel_practice_data/rules.yaml`

## 5) 阈值文件说明（原理与更新方式）

### 5.1 rules.yaml（组合规则阈值）
原理：
- 在历史窗口内随机抽样组合：从 ETF 池随机抽取 n 只，使用 Dirichlet(1,...,1) 生成权重
- 计算组合指标并形成经验分布（波动率、HHI、ADV、spread 等）
- 对指标分布取分位数生成 `warn/restrict` 阈值（高方向：90%/98%，低方向：10%/2%）

更新方式：
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_rules --asof-date <ASOF_DATE>（这里填目标持仓日期的前一个交易日） --n 5
```

### 5.2 macro_series.yaml（宏观阈值配置）
原理：
- 拉取宏观时序数据，并按 `asof_date` 截断
- 计算相邻两期的变化幅度（`change_mode=abs` 用绝对差；`pct` 用相对变化）
- 若 `change_scale=bp`，将变化幅度转换为 bp
- 对变化幅度分布取分位数生成阈值（默认 warn=90%，restrict=98%）

更新方式：
```bash
uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series --asof-date <ASOF_DATE>（同上）
```

## 6) 最小可运行样例
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
