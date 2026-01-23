# 数据源说明

本项目从 `cufel_practice_data/` 读取 CSV 数据。
如需替换目录，请设置 `CSV_DATA_DIR=/path/to/csv`。

## 文件与字段
- `etf_2025_data.csv`  
  - 必需字段：`date, code, open, high, low, close, vol, amount`  
  - 可选字段：`pre_close, change, pct_chg, adj_factor`  
  - 说明：若提供 `adj_factor`，波动率使用复权价计算。
- `sampled_etf_basic.csv`：`code`（可含其他描述字段）
- `csrc_2025.csv`：`title, date, content, from`（合规文本）
- `govcn_2025.csv`：`title, date, content, industry_name`（宏观文本）
- `govcn_2025_results.json`：宏观情绪分析结果
- `macro_series.yaml`：宏观时序配置（Tushare，可选）
- `rules.yaml`：规则阈值文件

## 采样与校准
- 随机样例：`src.app` 会从 `etf_2025_data.csv` 随机抽样（`SAMPLE_UNIVERSE_SIZE` 可调）
- 规则校准：  
  ```bash
  uv run --env-file .env -- python -u -m src.tools.calibrate_rules --asof-date <ASOF_DATE> --n 5
  ```
  `ASOF_DATE` 建议取“交易意图日期的前一个交易日”。
- 宏观阈值校准：  
  ```bash
  uv run --env-file .env -- python -u -m src.tools.calibrate_macro_series --asof-date <ASOF_DATE>
  ```
  `ASOF_DATE` 同上。
  运行 `test.py` 时会自动更新 `rules.yaml` 与 `macro_series.yaml`（需配置 `TUSHARE_TOKEN`）。
