from get_active_algorithm_name import get_active_algorithm_name
from discard_algorithm import discard_algorithm
from cmd_clear import cmd_clear


def cmd_delete_active() -> None:
    """Delete the active algorithm file, remove it from ml_constants.py, and clear constants.py."""
    func_name = get_active_algorithm_name()

    if not func_name or func_name == "None":
        print("No active algorithm to delete.")
        return

    # Derive the strategy name from the function name (strip run_mock_ prefix and _backtest suffix)
    strategy_name = func_name.removeprefix("run_mock_").removesuffix("_backtest")

    print(f"Deleting active algorithm: {func_name}")
    discard_algorithm(strategy_name, "")
    cmd_clear()
    print("Done. No active algorithm is set.")
