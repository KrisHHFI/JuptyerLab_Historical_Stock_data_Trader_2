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
├── tools/
│   ├── cli.py                          # CLI entry point — shows help or dispatches commands
│   ├── cmd_create_new.py               # command: generate a new algorithm and activate it
│   ├── get_client.py                   # builds the OpenAI client
│   ├── get_existing_strategy_names.py  # lists already-generated strategy names
│   ├── get_strategy_name.py            # asks the model for a new strategy name
│   ├── strip_markdown_fences.py        # strips markdown fences from model output
│   ├── generate_algorithm_code.py      # calls the model to produce backtest code
│   ├── generate_ml_params_code.py      # calls the model to produce the ML param builder
│   ├── save_algorithm.py               # writes the generated file to trading_algorithms/
│   ├── save_ml_params.py               # inserts the param builder into ml_constants.py
│   ├── apply_best_params.py            # reads ml_best_params.json and patches the active algo's defaults
│   ├── update_constants.py             # updates constants.py with the new active algorithm
│   └── run_notebook.py                 # restarts the kernel and executes main.ipynb via nbconvert
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

## CLI Tool

- `tools/cli.py` is the command-line entry point for the project. Running it with no arguments (or an unrecognised command) prints a help page listing available commands.
- Each command lives in its own `cmd_*.py` file inside `tools/`.
- Commands are invoked via the `trader` shell function registered in `~/.zshrc`. **How to use**:
  ```
  trader help           # show help page
  trader create         # generate a new algorithm
  trader refine         # run the ML parameter optimizer
  ```
- To register the `trader` function on a new machine, add this to `~/.zshrc`:
  ```
  function trader() { python /Users/kristopherpepper/Documents/jupyterProjects/historicalStockTrader2/tools/cli.py "$@"; }
  ```
- On `create new`, it calls the GitHub Models API (via the `openai` package) using GPT-4o to:
  1. Generate the name of a popular quantitative trading strategy (words separated by `_`).
  2. Generate a fully compatible backtest function following the project's algorithm conventions.
  3. Save the generated file to `utils/trading_algorithms/run_mock_<strategy_name>_backtest.py`.
- Requires the `GITHUB_TOKEN` environment variable to be set to a valid GitHub personal access token. Add it permanently with:
  ```
  echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc && source ~/.zshrc
  ```
- When adding a new CLI command, add a copy-paste usage example to the **Commands** section of `README.md`.
- `trader refine` runs `machine_learning/ml_optimizer.py` via `cmd_create_refine.py`.
- After `trader create` finishes generating and activating the new algorithm, it automatically restarts the kernel and runs `main.ipynb` end-to-end via `tools/run_notebook.py` (uses `jupyter nbconvert --execute --inplace`).

## Notes

- Repository: https://github.com/KrisHHFI/JuptyerLab_Historical_Stock_data_Trader
- `main.ipynb` is the main execution entry for this project.
- Utility logic is separated under `utils/` using the one-function-per-file convention.
- The project charts from a configured CSV path and does not include in-project data download functions.
- Active CSV inputs are stored in `raw_data/` and should remain git-ignored.
- The notebook parses ticker/interval/period/timestamp from the CSV filename and prints metadata in separate `File Metadata` and `Stock Metadata` tables.
- Do not document or discuss files inside `utils/trading_algorithms/` in AGENTS notes or user-facing summaries.
