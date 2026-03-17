# Historical Stock Trader 2

A Jupyter-based backtesting framework for historical stock data with an AI-powered algorithm generator.

## Commands

### Setup — register the `trader` shell command (once per machine)

```bash
echo 'function trader() { python /Users/kristopherpepper/Documents/jupyterProjects/historicalStockTrader2/tools/cli.py "$@"; }' >> ~/.zshrc && source ~/.zshrc
```

### Setup — store your GitHub token (once per machine)

```bash
echo 'export GITHUB_TOKEN=your_token_here' >> ~/.zshrc && source ~/.zshrc
```

### Show help

```bash
trader help
```

### Generate a new trading algorithm, then runs the notebook

```bash
trader create
```

### Tune the active algorithm with the ML parameter optimizer

```bash
trader refine
```