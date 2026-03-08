"""
ML Parameter Optimizer — Optuna Bayesian Tuning Template
=========================================================
Runs Bayesian (TPE) optimization over the active trading algorithm's parameters.
Every time a new best result is found it is appended to ml_optimizer_results.txt.

To use with a different algorithm:
  1. Change `active_algorithm` in constants.py.
  2. Ensure a param builder is registered for it in machine_learning/ml_constants.py.
  3. Adjust ml_n_trials in constants.py for more thorough search.

How to run:
  /opt/anaconda3/bin/python machine_learning/ml_optimizer.py

Optuna uses TPE (Tree-structured Parzen Estimator) — a Bayesian method that learns
from each trial which parameter regions are promising, far smarter than grid/random search.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
sys.path.insert(0, str(Path(__file__).parent.parent))  # project root
sys.path.insert(0, str(Path(__file__).parent))          # machine_learning/

import optuna
optuna.logging.set_verbosity(optuna.logging.WARNING)

from constants import (
    active_algorithm, raw_data_folder, capital, transaction_fee_bps,
    ml_n_trials, ml_trial_delay_seconds, ml_results_file,
)
from ml_constants import ml_params_builder

data_files = sorted(Path(raw_data_folder).glob("*.csv"))
_best_so_far: float = float("-inf")

# Clear the results file before each run
ml_results_file.write_text("")


def objective(trial: optuna.Trial) -> float:
    params: dict[str, int | float] = ml_params_builder(trial)

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

