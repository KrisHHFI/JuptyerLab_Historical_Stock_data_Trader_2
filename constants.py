from pathlib import Path
from utils.trading_algorithms.run_mock_pairs_trading_backtest import run_mock_pairs_trading_backtest

raw_data_folder: str = "/Users/kristopherpepper/Documents/jupyterProjects/historicalStockTrader2/raw_data"

# Trading
capital: int = 10000
transaction_fee_bps: float = 1.0
active_algorithm = run_mock_pairs_trading_backtest

# ML Optimizer
ml_n_trials: int = 100
ml_trial_delay_seconds: float = 0.5   # pause between trials to reduce CPU heat
ml_results_file: Path = Path(__file__).parent / "ml_optimizer_results.txt"
