import importlib
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent


def evaluate_algorithm(strategy_name: str) -> dict[str, Any]:
    """Run the algorithm on all raw_data CSVs and return aggregated metrics.

    Returns a dict with:
        trade_count (int):   total trades across all CSV files
        return_pct  (float): combined net return percentage across all CSVs
        error       (bool):  True if the algorithm raised an exception
    """
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)

    safe_name = re.sub(r"[^a-z0-9_]", "", strategy_name.lower().replace(" ", "_"))
    func_name = f"run_mock_{safe_name}_backtest"
    module_name = f"utils.trading_algorithms.run_mock_{safe_name}_backtest"

    # Force a fresh import so we pick up the just-written file
    for key in list(sys.modules.keys()):
        if key in (module_name, "constants"):
            del sys.modules[key]

    try:
        mod = importlib.import_module(module_name)
        algo = getattr(mod, func_name)
    except Exception as exc:
        print(f"  Could not import algorithm: {exc}")
        return {"trade_count": 0, "return_pct": 0.0, "error": True}

    if "constants" in sys.modules:
        del sys.modules["constants"]
    constants = importlib.import_module("constants")

    raw_data_folder = Path(constants.raw_data_folder)
    capital = constants.capital
    fee_bps = constants.transaction_fee_bps

    data_files = sorted(raw_data_folder.glob("*.csv"))
    if not data_files:
        return {"trade_count": 0, "return_pct": 0.0, "error": False}

    total_initial = 0.0
    total_final = 0.0
    total_trades = 0

    for csv_path in data_files:
        try:
            perf = algo(
                csv_path=str(csv_path),
                initial_capital=capital,
                transaction_fee_bps=fee_bps,
            )
            total_initial += float(perf.get("initial_capital", capital))
            total_final += float(perf.get("final_capital", capital))
            total_trades += int(perf.get("trade_count", 0))
        except Exception as exc:
            print(f"  Error on {csv_path.name}: {exc}")
            return {"trade_count": 0, "return_pct": 0.0, "error": True}

    return_pct = (
        (total_final - total_initial) / total_initial * 100.0
        if total_initial
        else 0.0
    )
    return {"trade_count": total_trades, "return_pct": return_pct, "error": False}
