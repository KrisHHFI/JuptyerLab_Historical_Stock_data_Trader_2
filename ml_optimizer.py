"""
ML Parameter Optimizer — Optuna Bayesian Tuning Template
=========================================================
Runs Bayesian (TPE) optimization over the active trading algorithm's parameters.
Every time a new best result is found it is appended to ml_optimizer_results.txt.

To use with a different algorithm:
  1. Change `active_algorithm` in constants.py.
  2. Update the `params` dict inside `objective()` to match the new algorithm's
     parameters and search ranges (suggest_int / suggest_float / suggest_categorical).
  3. Adjust N_TRIALS (more = better results, but slower).

How to run:
  /opt/anaconda3/bin/python ml_optimizer.py

Optuna uses TPE (Tree-structured Parzen Estimator) — a Bayesian method that learns
from each trial which parameter regions are promising, far smarter than grid/random search.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
sys.path.insert(0, str(Path(__file__).parent))

import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from constants import (
    active_algorithm, raw_data_folder, capital, transaction_fee_bps,
    ml_n_trials, ml_trial_delay_seconds, ml_results_file,
)

data_files = sorted(Path(raw_data_folder).glob("*.csv"))
_best_so_far: float = float("-inf")

# Clear the results file before each run
ml_results_file.write_text("")


def objective(trial: optuna.Trial) -> float:
    # ── PARAMETER SEARCH SPACE ─────────────────────────────────────────────────
    params: dict[str, int | float] = {
        "fast_span":                  trial.suggest_int("fast_span", 5, 20),
        "slow_span":                  trial.suggest_int("slow_span", 21, 80),
        "entry_spread_threshold_pct": trial.suggest_float("entry_spread_threshold_pct", 0.05, 0.5),
        "exit_spread_threshold_pct":  trial.suggest_float("exit_spread_threshold_pct", -0.3, 0.0),
        "min_spread_momentum_pct":    trial.suggest_float("min_spread_momentum_pct", 0.01, 0.15),
        "slow_trend_lookback_bars":   trial.suggest_int("slow_trend_lookback_bars", 2, 10),
        "min_hold_bars":              trial.suggest_int("min_hold_bars", 3, 20),
        "max_hold_bars":              trial.suggest_int("max_hold_bars", 60, 300),
        "cooldown_bars":              trial.suggest_int("cooldown_bars", 3, 20),
        "stop_loss_pct":              trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct":            trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct":          trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_entry_volatility_pct":   trial.suggest_float("max_entry_volatility_pct", 0.3, 2.0),
        "volatility_lookback_bars":   trial.suggest_int("volatility_lookback_bars", 10, 40),
    }
    # ───────────────────────────────────────────────────────────────────────────

    global _best_so_far
    total = 0.0
    for f in data_files:
        total += active_algorithm(
            csv_path=str(f),
            initial_capital=capital,
            transaction_fee_bps=transaction_fee_bps,
            **params,  # type: ignore[arg-type]
        )["final_capital"]
        time.sleep(ml_trial_delay_seconds)
    avg = total / len(data_files)

    if avg > _best_so_far:
        _best_so_far = avg
        _write_best(trial.number, avg, params)

    return avg


def _write_best(trial_num: int, avg_capital: float, params: dict[str, Any]) -> None:
    """Append a new best result to the results file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"\n{'='*60}",
        f"New best  —  trial {trial_num}  —  {timestamp}",
        f"Algorithm : {active_algorithm.__name__}",
        f"Avg end   : ${avg_capital:.2f}  (baseline: $10,000.00)",
        "Params:",
        *[f"  {k} = {round(v, 4) if isinstance(v, float) else v}" for k, v in params.items()],
    ]
    with open(ml_results_file, "a") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


study = optuna.create_study(
    direction="maximize",
    sampler=optuna.samplers.TPESampler(seed=42),
)

try:
    study.optimize(objective, n_trials=ml_n_trials, show_progress_bar=True)
except KeyboardInterrupt:
    print("\n[Interrupted — results saved to ml_optimizer_results.txt]")

if study.best_trial:
    print(f"\nFinal best: ${study.best_value:.2f}  (see {ml_results_file.name} for all improvements)")

