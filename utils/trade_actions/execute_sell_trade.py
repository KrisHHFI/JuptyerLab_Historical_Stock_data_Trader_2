from typing import Any

import pandas as pd


def execute_sell_trade(
    cash: float,
    shares: int,
    buy_price: float | None,
    buy_time: pd.Timestamp | None,
    sell_price: float,
    sell_time: pd.Timestamp,
    trade_number: int,
    transaction_fee_bps: float = 0.0,
    entry_fee_paid: float = 0.0,
) -> dict[str, Any]:
    fee_rate = abs(transaction_fee_bps) / 10000
    gross_proceeds = shares * sell_price
    exit_fee_paid = gross_proceeds * fee_rate
    net_proceeds = gross_proceeds - exit_fee_paid
    updated_cash = cash + net_proceeds

    if buy_price is None or buy_price <= 0:
        return {
            "cash": updated_cash,
            "trade_return_pct": None,
            "trade_record": None,
        }

    gross_cost = buy_price * shares
    total_cost_basis = gross_cost + float(entry_fee_paid)
    trade_pnl = net_proceeds - total_cost_basis
    trade_return_pct = (trade_pnl / total_cost_basis) * 100 if total_cost_basis > 0 else 0.0

    return {
        "cash": updated_cash,
        "trade_return_pct": float(trade_return_pct),
        "trade_record": {
            "trade": trade_number,
            "entry_time": buy_time,
            "exit_time": sell_time,
            "entry_price": float(buy_price),
            "exit_price": float(sell_price),
            "shares": int(shares),
            "pnl": float(trade_pnl),
            "return_pct": float(trade_return_pct),
            "entry_fee": float(entry_fee_paid),
            "exit_fee": float(exit_fee_paid),
        },
    }
