from typing import Any, Callable, Dict
from pathlib import Path

from utils.data.parse_stock_filename_metadata import parse_stock_filename_metadata
from utils.data.chart.plot_compressed_trading_chart import plot_compressed_trading_chart
from utils.printing.print_trades_table import print_trades_table


def print_all_stock_trades(
    data_files: list[Path],
    performance_by_csv: dict[str, dict[str, Any]],
    active_algorithm: Callable[..., Dict[str, Any]],
    capital: int,
    transaction_fee_bps: float,
) -> None:
    """Plot the trading chart and print the trades table for every CSV file."""
    for stock_data_path in data_files:
        csv_path = str(stock_data_path)
        metadata = parse_stock_filename_metadata(csv_path)
        performance = performance_by_csv.get(csv_path)
        if performance is None:
            performance = active_algorithm(
                csv_path=csv_path,
                initial_capital=capital,
                transaction_fee_bps=transaction_fee_bps,
            )

        plot_compressed_trading_chart(
            csv_path=csv_path,
            ticker=metadata["ticker"],
            interval=metadata["interval"],
            trades=performance["trades"],
        )
        print_trades_table(performance["trades"])
