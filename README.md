# Historical Stock Trader

## About

 A Jupyter-based backtesting framework for analysing trading strategies against real historical stock data. It combines an AI-powered algorithm generator (using GPT-4o via the GitHub Models API) with a machine learning parameter optimizer (Optuna) to automatically create, evaluate, and tune quantitative trading strategies.

Each strategy is generated as a self-contained Python backtest function and run against a configurable set of stock CSVs (1-minute interval data). Results are printed as a formatted performance table in the notebook. Every run is also written to a `high_scores.txt` leaderboard so the best-ever result for each strategy is preserved across sessions.

The project is built around a CLI tool (`trader`) that orchestrates the full workflow — from generating new algorithms to running the notebook — without needing to open Jupyter manually. The project was created mainly using Copilot.

<img src="promo" height="600px" alt="Promo image" />


## Commands

### Setup — register the `trader` shell command (once per machine)

```bash
echo 'function trader() { python /[YOUR PATH HERE]/jupyterProjects/historicalStockTrader2/tools/cli.py "$@"; }' >> ~/.zshrc && source ~/.zshrc
```

### Setup — store your GitHub token (once per machine)

```bash
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc && source ~/.zshrc
```

### Show help

```bash
trader help
```

### Generate a new trading algorithm, then run the notebook

```bash
trader create
```

### Tune the active algorithm with the ML parameter optimizer

```bash
trader refine
```

### Choose an existing algorithm to activate

```bash
trader set
```

### Clear the active algorithm (sets it to None)

```bash
trader clear
```

### Delete the active algorithm and remove it from the project

```bash
trader delete active
```

### Restart the kernel and run the notebook end-to-end

```bash
trader run
```
