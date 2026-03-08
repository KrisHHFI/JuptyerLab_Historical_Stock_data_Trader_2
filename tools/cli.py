import sys
import os
import re
from pathlib import Path
from openai import OpenAI

ALGORITHMS_DIR = Path(__file__).parent.parent / "utils" / "trading_algorithms"
CONSTANTS_PATH = Path(__file__).parent.parent / "constants.py"

SYSTEM_PROMPT = """\
You are an expert Python quant developer. Output a single raw Python source file — \
no markdown, no code fences, no backticks, no explanation. \
The very first character of your response must be # (the top-of-file comment). \
Do not wrap the code in ```python or ``` or any other delimiters.

Rules:
1. Top-of-file comment: 2-3 plain-English lines explaining the strategy logic, entry/exit \
concept, and key risk controls — no jargon.
2. Imports — exactly these four, nothing else:
   from typing import Any
   import pandas as pd
   from utils.trade_actions.execute_buy_trade import execute_buy_trade
   from utils.trade_actions.execute_sell_trade import execute_sell_trade
3. One public function: run_mock_<strategy_snake_case>_backtest(
       csv_path: str, initial_capital: int, <strategy params with defaults>,
       transaction_fee_bps: float = 1.0, entry_slippage_bps: float = 3.0,
       exit_slippage_bps: float = 3.0, session_entry_start_minute: int = 0,
       session_entry_end_minute: int = 23*60+59) -> dict[str, Any]
4. Load data: pd.read_csv(csv_path). Detect time column:
       time_column = "Datetime" if "Datetime" in price_data.columns else "Date"
   Parse to datetime, coerce Close to numeric, dropna, sort, reset_index(drop=True).
   AVAILABLE CSV COLUMNS (after load): Open, High, Low, Close, Volume, plus the time column.
   NEVER access any column you did not explicitly create yourself from those base columns.
   All indicators (e.g. EMA, RSI, BB) must be computed from Close/Open/High/Low/Volume only
   and added as new columns via pandas — never assumed to exist in the raw CSV.
5. Return early zeroed dict if dataset is empty.
6. Pending-order pattern — CRITICAL: signal detected at bar N must NEVER fill at bar N.
   Use a boolean flag `pending_buy = False` (initialised before the loop).
   The loop body must follow this EXACT three-step order every iteration:

   STEP 1 — fill any pending buy at THIS bar's open (top of loop, before risk checks):
       if pending_buy and shares == 0:
           fill_price = row['Open'] * (1 + entry_slippage_bps / 10000.0)
           result = execute_buy_trade(...)
           pending_buy = False
           if result['executed']: <update cash/shares/buy_price/buy_time/entry_fee_paid>

   STEP 2 — manage open position / risk exits (uses current bar's High/Low/Open).

   STEP 3 — generate entry signal for the NEXT bar (NEVER fill here — only set flag):
       if <entry conditions met>:
           pending_buy = True

   Loop MUST use iterrows(): `for index, row in dataset.iterrows()`
   Skip index 0. Access the time column as `row[time_column]` (string key, not attribute).
7. execute_buy_trade exact call signature and return keys:
       result = execute_buy_trade(
           cash=cash, close_price=fill_price,
           trade_time=row[time_column], transaction_fee_bps=transaction_fee_bps)
       # returns: result["executed"] bool, result["cash"], result["shares"],
       #          result["buy_price"], result["buy_time"], result["entry_fee_paid"]
8. execute_sell_trade exact call signature and return keys:
       result = execute_sell_trade(
           cash=cash, shares=shares, buy_price=buy_price, buy_time=buy_time,
           sell_price=fill_price, sell_time=row[time_column],
           trade_number=len(trades)+1, transaction_fee_bps=transaction_fee_bps,
           entry_fee_paid=entry_fee_paid)
       # result keys: result["cash"], result["trade_return_pct"], result["trade_record"]
       # trade_record keys — EXACT, do not rename or recreate:
       #   "trade", "entry_time", "exit_time", "entry_price", "exit_price",
       #   "shares", "pnl", "return_pct", "entry_fee", "exit_fee"
       # FORBIDDEN key names on trade_record (will raise KeyError at runtime):
       #   entry_fee_paid, exit_fee_paid, trade_return_pct — these do NOT exist.
       After a sell:
           cash = result["cash"]
           if result["trade_return_pct"] is not None:
               trade_returns.append(result["trade_return_pct"])
           if result["trade_record"] is not None:
               trades.append(result["trade_record"])
               total_fees_paid += result["trade_record"]["entry_fee"] + result["trade_record"]["exit_fee"]
9. State to track: cash, shares, buy_price, buy_time, entry_fee_paid, bars_held,
   bars_since_exit, highest_price_since_entry.
   Also initialise before the loop: trade_returns = [], trades = [], total_fees_paid = 0.0
10. Risk controls — use these EXACT parameter names with these EXACT sensible defaults:
       stop_loss_pct: float = 2.0        # exit if price drops this % below entry
       take_profit_pct: float = 4.0      # exit if price rises this % above entry
       trailing_stop_pct: float = 1.5    # exit if price falls this % from the highest point since entry
       max_hold_bars: int = 60           # force-exit after this many bars
       cooldown_bars: int = 5            # minimum bars to wait between an exit and the next entry
    All five controls MUST be active every bar while in a position.
    Trailing stop: track highest_price_since_entry (update each bar); trigger if Close < highest * (1 - trailing_stop_pct/100).
11. DEFENSIVE CODING — these rules prevent impossible negative-cash results:
    a. NEVER call execute_sell_trade unless `shares > 0`. Guard every sell with `if shares > 0:`.
    b. fill_price for any buy or sell MUST be computed from row['Open'], which is always > 0.
       Never use row['Close'] or a computed value that could be zero or negative as fill_price.
    c. After execute_buy_trade, only update state when `result["executed"] is True`.
    d. After execute_sell_trade, always reset: shares = 0, buy_price = 0.0, buy_time = None,
       entry_fee_paid = 0.0, bars_held = 0, highest_price_since_entry = 0.0, bars_since_exit = 0.
    e. cash must NEVER be set to a negative value. It starts at initial_capital and only changes
       via result["cash"] from execute_buy_trade / execute_sell_trade — never compute it manually.
12. SIGNAL QUALITY — entries must require a clear, meaningful technical condition:
    The entry signal must combine at least two independent conditions (e.g. trend filter + momentum
    confirmation), so the strategy is selective and avoids random overtrading.
    Do NOT enter on every bar — the strategy should be in a position less than 30% of the time.
13. Force-exit any open position on the last bar of the loop (same sell pattern as rule 8).
14. After the loop, compute metrics EXACTLY like this — use these key names verbatim:
       final_capital = cash
       net_pnl = final_capital - initial_capital
       return_pct = (net_pnl / initial_capital * 100.0) if initial_capital > 0 else 0.0
       trade_count = len(trades)
       winning_trades = sum(1 for r in trade_returns if r > 0)
       losing_trades = sum(1 for r in trade_returns if r <= 0)
       win_rate_pct = (winning_trades / trade_count * 100.0) if trade_count > 0 else 0.0
       avg_trade_return_pct = (sum(trade_returns) / trade_count) if trade_count > 0 else 0.0
    Return dict with EXACTLY these keys:
       strategy, initial_capital, final_capital, net_pnl, total_fees_paid, return_pct,
       trade_count, winning_trades, losing_trades, win_rate_pct, avg_trade_return_pct, trades
15. No print statements. No external downloads. No extra imports. No invented columns.
Remember: raw Python only — first character must be #, last character must be a newline.
"""

def get_client() -> OpenAI:
    token = os.environ.get("GITHUB_TOKEN")
    return OpenAI(base_url="https://models.inference.ai.azure.com", api_key=token)

def get_existing_strategy_names() -> list[str]:
    names = []
    for f in ALGORITHMS_DIR.glob("run_mock_*_backtest.py"):
        name = f.stem  # e.g. run_mock_ema_crossover_backtest
        name = re.sub(r"^run_mock_", "", name)
        name = re.sub(r"_backtest$", "", name)
        names.append(name)
    return names

def get_strategy_name(client: OpenAI) -> str:
    existing = get_existing_strategy_names()
    exclusion = (
        f" Do NOT suggest any of these already-existing strategies: {', '.join(existing)}."
        if existing else ""
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    "Name one popular quantitative trading strategy with the words "
                    "separated by \"_\". Reply with only the strategy name, nothing else."
                    + exclusion
                ),
            }
        ],
        max_tokens=32,
    )
    return (response.choices[0].message.content or "").strip()

def strip_markdown_fences(code: str) -> str:
    """Remove any markdown code fences the model may have added."""
    code = re.sub(r"^```[a-zA-Z]*\n", "", code.strip())
    code = re.sub(r"\n```$", "", code)
    return code.strip()

def generate_algorithm_code(client: OpenAI, strategy_name: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Generate the backtest function for the strategy: {strategy_name}",
            },
        ],
        max_tokens=6144,
    )
    code = (response.choices[0].message.content or "").strip()
    return strip_markdown_fences(code)

def save_algorithm(strategy_name: str, code: str) -> Path:
    safe_name = re.sub(r"[^a-z0-9_]", "", strategy_name.lower().replace(" ", "_"))
    filename = f"run_mock_{safe_name}_backtest.py"
    output_path = ALGORITHMS_DIR / filename
    output_path.write_text(code + "\n", encoding="utf-8")
    return output_path

def update_constants(strategy_name: str, output_path: Path) -> None:
    if not output_path.exists():
        print(f"Skipping constants.py update — file not found: {output_path}")
        return
    safe_name = re.sub(r"[^a-z0-9_]", "", strategy_name.lower().replace(" ", "_"))
    func_name = f"run_mock_{safe_name}_backtest"
    module = f"utils.trading_algorithms.run_mock_{safe_name}_backtest"
    import_line = f"from {module} import {func_name}"

    content = CONSTANTS_PATH.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Find and remove the old active_algorithm import (the uncommented one)
    old_func_match = re.search(r"^active_algorithm\s*=\s*(\w+)", content, re.MULTILINE)
    if old_func_match:
        old_func_name = old_func_match.group(1)
        if old_func_name != func_name:
            lines = [
                line for line in lines
                if not re.match(rf"^from utils\.trading_algorithms\.\S+ import {re.escape(old_func_name)}\s*$", line)
            ]

    # Add new import if not already present
    content = "\n".join(lines) + "\n"
    if import_line not in content:
        lines = content.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from utils.trading_algorithms"):
                insert_idx = i + 1
            elif "from pathlib import Path" in line and insert_idx == 0:
                insert_idx = i + 1
        lines.insert(insert_idx, import_line)
        content = "\n".join(lines) + "\n"

    # Update active_algorithm
    content = re.sub(
        r"^active_algorithm\s*=.*$",
        f"active_algorithm = {func_name}",
        content,
        flags=re.MULTILINE,
    )

    CONSTANTS_PATH.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        client = get_client()

        strategy_name = get_strategy_name(client)
        print(f"Strategy: {strategy_name}")

        print("Generating algorithm code...")
        code = generate_algorithm_code(client, strategy_name)

        output_path = save_algorithm(strategy_name, code)
        print(f"Saved to: {output_path}")

        update_constants(strategy_name, output_path)
        print(f"Updated constants.py: active_algorithm = run_mock_{re.sub(r'[^a-z0-9_]', '', strategy_name.lower().replace(' ', '_'))}_backtest")

