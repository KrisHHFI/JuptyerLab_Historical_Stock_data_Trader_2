# AGENTS.md

## Development Rules

1. **One function per file**
   - Each standalone function must live in its own Python file.
   - Keep files small, focused, and single-purpose.

2. **Sensitive data must be git-ignored**
   - Never commit secrets or sensitive artifacts.
   - Examples: API keys, tokens, credentials, local env files, generated private datasets, and large downloaded outputs.
   - Ensure `.gitignore` is updated whenever new sensitive/generated paths are introduced.

3. **Keep this document up to date**
   - Update `AGENTS.md` whenever project structure, conventions, or workflow rules change.

4. **Reuse active runtime sessions**
   - Do not repeatedly establish a new notebook kernel or Python environment when one is already active and working.
   - Only restart or reconfigure the kernel/environment when there is a concrete execution/import failure that requires it.

5. **Trading algorithms must be realistic**
   - Strategy logic and backtests must use realistic market assumptions.
   - No fantasy behavior (for example: perfect fills, impossible timing, guaranteed wins, or clairvoyant signals).
   - Include practical constraints when relevant (for example: execution frictions, liquidity limits, and risk controls).

6. **Trading algorithm files need a logic header**
   - Every file in `utils/trading_algorithms/` must start with a short top-of-file comment.
   - The comment should explain the algorithm’s core logic, entry/exit concept, and key risk controls in plain language.
   - Write the comment so an everyday person can understand it without finance or coding jargon.

## Project Architecture

```text
historicalStockTrader2/
├── .gitignore
├── AGENTS.md
├── README.md
├── constants.py
├── main.ipynb
├── machine_learning/
│   ├── ml_constants.py
│   └── ml_optimizer.py
├── raw_data/  # local CSV inputs (git-ignored)
└── utils/
   ├── __init__.py
   ├── data/
   │   ├── __init__.py
   │   ├── aggregate_performances.py
   │   ├── build_file_metadata_rows.py
   │   ├── build_performance_rows.py
   │   ├── build_stock_metadata_rows.py
   │   ├── parse_stock_filename_metadata.py
   │   └── chart/
   │       ├── __init__.py
   │       ├── plot_compressed_trading_chart.py
   │       └── helpers/
   │           ├── build_time_to_position.py
   │           ├── extract_trade_markers.py
   │           ├── get_time_column.py
   │           ├── load_and_prepare_data.py
   │           ├── plot_trade_markers.py
   │           └── set_day_xticks.py
   ├── printing/
   │   ├── __init__.py
   │   ├── create_metadata_table.py
   │   ├── print_h1.py
   │   ├── print_h2.py
   │   ├── print_header.py
   │   ├── print_metadata_tables.py
   │   ├── print_performance_table.py
   │   ├── print_subheader.py
   │   └── print_trades_table.py
   ├── trade_actions/
   │   ├── __init__.py
   │   ├── execute_buy_trade.py
   │   └── execute_sell_trade.py
   └── trading_algorithms/  # internal algorithm files (git-ignored)
```

## ML Parameter Optimizer

- `machine_learning/ml_optimizer.py` is a fully generic runner — it contains no algorithm-specific logic.
- `machine_learning/ml_constants.py` holds the parameter search spaces. Each algorithm has a registered builder function that defines its tunable parameters and search ranges.
- To switch algorithms: change `active_algorithm` in `constants.py`. The correct param builder is resolved automatically from `ml_constants.py`.
- To add a new algorithm: add a `_<algo_name>_params(trial)` function and register it in `ML_PARAM_BUILDERS` inside `ml_constants.py`.
- Every time a new best result is found during the run, it is appended to `ml_optimizer_results.txt` (git-ignored).
- **How to run** (from the project root directory):
  ```
  /opt/anaconda3/bin/python machine_learning/ml_optimizer.py
  ```
- Increase `ml_n_trials` in `constants.py` for more thorough search. Results are saved incrementally so interrupting early still keeps all improvements found so far.

## Notes

- Repository: https://github.com/KrisHHFI/JuptyerLab_Historical_Stock_data_Trader
- `main.ipynb` is the main execution entry for this project.
- Utility logic is separated under `utils/` using the one-function-per-file convention.
- The project charts from a configured CSV path and does not include in-project data download functions.
- Active CSV inputs are stored in `raw_data/` and should remain git-ignored.
- The notebook parses ticker/interval/period/timestamp from the CSV filename and prints metadata in separate `File Metadata` and `Stock Metadata` tables.
- Do not document or discuss files inside `utils/trading_algorithms/` in AGENTS notes or user-facing summaries.
