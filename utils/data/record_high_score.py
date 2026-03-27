"""Append a backtest result to the high scores leaderboard file.

Reads existing records from the DATA section of high_scores.txt, adds the
new result, sorts all entries by combined return % (descending), then
re-writes the whole file as a formatted fixed-width table followed by a
machine-readable DATA section used for future parsing.
"""
from datetime import date
from pathlib import Path
from typing import Any


_HEADER_FIELDS = [
    "strategy", "return_pct", "trade_count",
    "win_rate_pct", "avg_trade_pct", "net_pnl", "num_stocks", "date",
]

# Column layout: (header label, width, right-align?)
_COLS: list[tuple[str, int, bool]] = [
    ("Rank",       5,  True),
    ("Strategy",  50, False),
    ("Return",     9,  True),
    ("Trades",     7,  True),
    ("Win Rate",   9,  True),
    ("Avg Trade", 10,  True),
    ("Net P&L",   13,  True),
    ("Stocks",     7,  True),
    ("Date",      10, False),
]


def _sep_line() -> str:
    return "─" + "─┼─".join("─" * w for w in (c[1] for c in _COLS)) + "─"


def _header_line() -> str:
    parts = []
    for label, width, right in _COLS:
        parts.append(f"{label:>{width}}" if right else f"{label:<{width}}")
    return " │ ".join(parts)


def _format_row(rank: int, rec: dict[str, Any]) -> str:
    strategy = str(rec["strategy"])[:50]
    return_pct = float(rec["return_pct"])
    trade_count = int(rec["trade_count"])
    win_rate = float(rec["win_rate_pct"])
    avg_trade = float(rec["avg_trade_pct"])
    net_pnl = float(rec["net_pnl"])
    num_stocks = int(rec["num_stocks"])
    run_date = str(rec["date"])

    cells = [
        f"{rank:>5}",
        f"{strategy:<50}",
        f"{return_pct:>+8.2f}%",
        f"{trade_count:>7}",
        f"{win_rate:>8.1f}%",
        f"{avg_trade:>+9.2f}%",
        f"${net_pnl:>+12,.2f}",
        f"{num_stocks:>7}",
        f"{run_date:<10}",
    ]
    return " │ ".join(cells)


def _parse_existing(path: Path) -> list[dict[str, Any]]:
    """Read records from the DATA section of the file."""
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    in_data = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## FIELDS:"):
            in_data = True
            continue
        if in_data and line.startswith("## "):
            parts = line[3:].split("|")
            if len(parts) == len(_HEADER_FIELDS):
                records.append(dict(zip(_HEADER_FIELDS, parts)))
    return records


def record_high_score(
    performance: dict[str, Any],
    num_stocks: int,
    high_scores_file: Path,
    strategy_name: str = "",
) -> None:
    """Append the current run to the high scores table and re-write the file."""
    new_record: dict[str, Any] = {
        "strategy":      strategy_name or str(performance.get("strategy", "")),
        "return_pct":    float(performance.get("return_pct", 0.0)),
        "trade_count":   int(performance.get("trade_count", 0)),
        "win_rate_pct":  float(performance.get("win_rate_pct", 0.0)),
        "avg_trade_pct": float(performance.get("avg_trade_return_pct", 0.0)),
        "net_pnl":       float(performance.get("net_pnl", 0.0)),
        "num_stocks":    num_stocks,
        "date":          str(date.today()),
    }

    records = _parse_existing(high_scores_file)
    records.append(new_record)

    # Keep only the best result per strategy
    best: dict[str, dict[str, Any]] = {}
    for rec in records:
        name = str(rec["strategy"])
        if name not in best or float(rec["return_pct"]) > float(best[name]["return_pct"]):
            best[name] = rec
    records = sorted(best.values(), key=lambda r: float(r["return_pct"]), reverse=True)

    sep = _sep_line()
    lines: list[str] = [
        "High Scores — Historical Backtest Results",
        "=" * (len(sep) + 2),
        "",
        _header_line(),
        sep,
    ]
    for rank, rec in enumerate(records, start=1):
        lines.append(_format_row(rank, rec))

    lines += [
        "",
        f"Total entries: {len(records)}",
        "",
        "# ── Machine-readable data (do not edit) ──────────────────────────────────────",
        f"## FIELDS: {' | '.join(_HEADER_FIELDS)}",
    ]
    for rec in records:
        row_data = "|".join(str(rec[f]) for f in _HEADER_FIELDS)
        lines.append(f"## {row_data}")

    high_scores_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"High score recorded — rank determined by return %  →  {high_scores_file.name}")
