# Data Sources

This project reads market/compliance data from local CSV files under `cufel_practice_data/`.
Set `CSV_DATA_DIR` to point to a different folder if needed.

Expected files and columns:
- `etf_2025_data.csv`: `date, code, open, high, low, close, vol, amount`
- `sampled_etf_basic.csv`: `code` (and any descriptive fields)
- `csrc_2025.csv`: `title, date, content, from` (compliance text)
- `govcn_2025.csv`: `title, date, content, industry_name` (macro text)
- `macro_series.yaml`: macro series config for Tushare (optional)

Rules:
- Keep thresholds in `cufel_practice_data/rules.yaml`.

Demo sampling:
- `src.app` samples a random universe from `etf_2025_data.csv` when `SAMPLE_UNIVERSE_SIZE` is set.

Rule calibration:
- `python -m src.tools.calibrate_rules --year 2025 --n 5` calibrates thresholds from CSV market data and writes `cufel_practice_data/rules.yaml`.
