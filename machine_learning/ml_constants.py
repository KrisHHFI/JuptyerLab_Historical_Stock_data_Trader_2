"""
ML Constants — Parameter Search Spaces per Algorithm
=====================================================
Each algorithm has a registered params builder function that takes an Optuna
trial and returns a dict of suggested parameter values.

To add a new algorithm:
  1. Define a function  _<algo_name>_params(trial) -> dict
  2. Register it in ML_PARAM_BUILDERS using the algorithm function's __name__.

The active algorithm is resolved automatically from constants.py.
"""

import sys
from pathlib import Path
from typing import Callable
sys.path.insert(0, str(Path(__file__).parent.parent))

import optuna
from constants import active_algorithm

ParamBuilder = Callable[[optuna.Trial], dict[str, int | float]]


# ── PARAM BUILDERS ────────────────────────────────────────────────────────────

def _run_mock_ema_crossover_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "fast_ema_window":            trial.suggest_int("fast_ema_window", 5, 20),
        "slow_ema_window":            trial.suggest_int("slow_ema_window", 21, 80),
        "trend_ema_window":           trial.suggest_int("trend_ema_window", 50, 200),
        "stop_loss_pct":              trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct":            trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct":          trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars":              trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars":              trial.suggest_int("cooldown_bars", 3, 30),
    }


def _run_mock_vwap_ema_crossover_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "fast_span":                  trial.suggest_int("fast_span", 5, 20),
        "slow_span":                  trial.suggest_int("slow_span", 21, 80),
        "entry_spread_threshold_pct": trial.suggest_float("entry_spread_threshold_pct", 0.05, 0.5),
        "exit_spread_threshold_pct":  trial.suggest_float("exit_spread_threshold_pct", -0.3, 0.0),
        "min_hold_bars":              trial.suggest_int("min_hold_bars", 3, 20),
        "max_hold_bars":              trial.suggest_int("max_hold_bars", 60, 300),
        "cooldown_bars":              trial.suggest_int("cooldown_bars", 3, 20),
        "stop_loss_pct":              trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct":            trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct":          trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
    }


def _run_mock_turtle_trading_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "entry_breakout_bars":   trial.suggest_int("entry_breakout_bars", 20, 120),
        "exit_breakout_bars":    trial.suggest_int("exit_breakout_bars", 5, 60),
        "atr_stop_multiplier":   trial.suggest_float("atr_stop_multiplier", 1.0, 4.0),
        "max_hold_bars":         trial.suggest_int("max_hold_bars", 60, 300),
        "cooldown_bars":         trial.suggest_int("cooldown_bars", 5, 50),
    }


def _run_mock_orb_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "opening_range_minutes":    trial.suggest_int("opening_range_minutes", 15, 90),
        "profit_target_multiplier": trial.suggest_float("profit_target_multiplier", 0.5, 3.0),
        "atr_stop_multiplier":      trial.suggest_float("atr_stop_multiplier", 0.5, 3.0),
        "max_hold_bars":            trial.suggest_int("max_hold_bars", 30, 240),
    }


def _run_mock_rsi_bb_mean_reversion_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "bb_period":      trial.suggest_int("bb_period", 10, 50),
        "bb_std":         trial.suggest_float("bb_std", 1.5, 3.5),
        "rsi_period":     trial.suggest_int("rsi_period", 7, 21),
        "rsi_oversold":   trial.suggest_float("rsi_oversold", 15.0, 35.0),
        "rsi_exit":       trial.suggest_float("rsi_exit", 35.0, 60.0),
        "stop_loss_pct":  trial.suggest_float("stop_loss_pct", 0.3, 2.0),
        "max_hold_bars":  trial.suggest_int("max_hold_bars", 10, 60),
        "cooldown_bars":  trial.suggest_int("cooldown_bars", 3, 20),
    }




def _run_mock_bollinger_band_breakout_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "bollinger_window": trial.suggest_int("bollinger_window", 10, 50),
        "bollinger_std_dev": trial.suggest_float("bollinger_std_dev", 1.0, 3.0),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30)
    }


def _run_mock_keltner_channel_breakout_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "ema_period":    trial.suggest_int("ema_period", 10, 50),
        "atr_period":    trial.suggest_int("atr_period", 5, 30),
        "kc_multiplier": trial.suggest_float("kc_multiplier", 1.0, 3.0),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30),
    }


def _run_mock_mean_reversion_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "rsi_period": trial.suggest_int("rsi_period", 5, 30),
        "bollinger_period": trial.suggest_int("bollinger_period", 10, 50),
        "bollinger_std_dev": trial.suggest_float("bollinger_std_dev", 1.5, 3.5),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30),
    }


def _run_mock_momentum_trading_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "ema_short_period": trial.suggest_int("ema_short_period", 5, 50),
        "ema_long_period": trial.suggest_int("ema_long_period", 20, 200),
        "rsi_period": trial.suggest_int("rsi_period", 5, 50),
        "rsi_entry_threshold": trial.suggest_int("rsi_entry_threshold", 50, 90),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30)
    }


def _run_mock_statistical_arbitrage_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "lookback_period": trial.suggest_int("lookback_period", 5, 100),
        "threshold_deviation": trial.suggest_float("threshold_deviation", 0.5, 3.0),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30),
    }


def _run_mock_market_making_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "volatility_window": trial.suggest_int("volatility_window", 5, 50),
        "mean_reversion_window": trial.suggest_int("mean_reversion_window", 3, 20),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30),
    }


def _run_mock_index_arbitrage_backtest_params(trial: optuna.Trial) -> dict[str, int | float]:
    return {
        "discount_threshold_pct": trial.suggest_float("discount_threshold_pct", -3.0, -0.1),
        "ema_period": trial.suggest_int("ema_period", 5, 50),
        "stop_loss_pct": trial.suggest_float("stop_loss_pct", 0.5, 3.0),
        "take_profit_pct": trial.suggest_float("take_profit_pct", 1.0, 5.0),
        "trailing_stop_pct": trial.suggest_float("trailing_stop_pct", 0.3, 2.0),
        "max_hold_bars": trial.suggest_int("max_hold_bars", 30, 300),
        "cooldown_bars": trial.suggest_int("cooldown_bars", 3, 30),
    }
# ── REGISTRY ──────────────────────────────────────────────────────────────────

ML_PARAM_BUILDERS: dict[str, ParamBuilder] = {
    "run_mock_ema_crossover_backtest":          _run_mock_ema_crossover_backtest_params,
    "run_mock_vwap_ema_crossover_backtest":     _run_mock_vwap_ema_crossover_backtest_params,
    "run_mock_turtle_trading_backtest":         _run_mock_turtle_trading_backtest_params,
    "run_mock_orb_backtest":                    _run_mock_orb_backtest_params,
    "run_mock_rsi_bb_mean_reversion_backtest":  _run_mock_rsi_bb_mean_reversion_backtest_params,
    "run_mock_bollinger_band_breakout_backtest":         _run_mock_bollinger_band_breakout_backtest_params,
    "run_mock_keltner_channel_breakout_backtest":        _run_mock_keltner_channel_breakout_backtest_params,
    "run_mock_mean_reversion_backtest":                  _run_mock_mean_reversion_backtest_params,
    "run_mock_momentum_trading_backtest":                _run_mock_momentum_trading_backtest_params,
    "run_mock_statistical_arbitrage_backtest":           _run_mock_statistical_arbitrage_backtest_params,
    "run_mock_market_making_backtest":                   _run_mock_market_making_backtest_params,
    "run_mock_index_arbitrage_backtest":                 _run_mock_index_arbitrage_backtest_params,
}

# Resolve builder for the currently active algorithm
_algo_name = active_algorithm.__name__
if _algo_name not in ML_PARAM_BUILDERS:
    raise ValueError(
        f"No ML param builder registered for '{_algo_name}'. "
        f"Add one to ML_PARAM_BUILDERS in machine_learning/ml_constants.py."
    )

ml_params_builder: ParamBuilder = ML_PARAM_BUILDERS[_algo_name]
