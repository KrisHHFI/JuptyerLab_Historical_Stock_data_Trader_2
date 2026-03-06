"""Create display rows for a performance summary.

This module formats numeric values (currency, percentages, counts)
into a list of (label, string) tuples suitable for printing.
"""
from typing import Any, Dict, List, Tuple


def build_performance_rows(performance: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Return formatted performance rows.

    Args:
        performance: Dictionary containing performance metrics.
    """
    strategy = str(performance.get("strategy", ""))
    starting_value = float(performance.get("starting_value", performance.get("initial_capital", 0.0)))
    worst_end_value = float(performance.get("worst_end_value", 0.0))
    worst_ticker = str(performance.get("worst_ticker", ""))
    best_end_value = float(performance.get("best_end_value", 0.0))
    best_ticker = str(performance.get("best_ticker", ""))
    median_end_value = float(performance.get("median_end_value", 0.0))
    avg_end_value = float(performance.get("avg_end_value", 0.0))
    avg_fees = float(performance.get("avg_fees", 0.0))
    trade_count = int(performance.get("trade_count", 0))
    winning_trades = int(performance.get("winning_trades", 0))
    losing_trades = int(performance.get("losing_trades", 0))
    win_rate_pct = float(performance.get("win_rate_pct", 0.0))
    avg_trade_return_pct = float(performance.get("avg_trade_return_pct", 0.0))

    return [
        ("Strategy", strategy),
        ("Starting value", f"${starting_value:,.2f}"),
        ("Worst end value", f"${worst_end_value:,.2f} ({worst_ticker})"),
        ("Best end value", f"${best_end_value:,.2f} ({best_ticker})"),
        ("Median end value", f"${median_end_value:,.2f}"),
        ("Average end value", f"${avg_end_value:,.2f}"),
        ("Average fees", f"${avg_fees:,.2f}"),
        ("Trades", str(trade_count)),
        ("Winning trades", str(winning_trades)),
        ("Losing trades", str(losing_trades)),
        ("Win rate", f"{win_rate_pct:.2f}%"),
        ("Average trade return", f"{avg_trade_return_pct:.2f}%"),
    ]
