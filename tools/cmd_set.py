from pathlib import Path
from get_existing_strategy_names import get_existing_strategy_names
from update_constants import update_constants


def cmd_set() -> None:
    """List available algorithms and activate the one chosen by the user."""
    names = sorted(get_existing_strategy_names())
    if not names:
        print("No algorithms found. Run 'trader create' to generate one.")
        return

    print("Available algorithms:")
    for i, name in enumerate(names, start=1):
        print(f"  {i}. {name}")
    print()

    raw = input("Enter the number of the algorithm to activate: ").strip()
    if not raw.isdigit():
        print("Invalid input. Please enter a number.")
        return

    choice = int(raw)
    if choice < 1 or choice > len(names):
        print(f"Invalid choice. Please enter a number between 1 and {len(names)}.")
        return

    strategy_name = names[choice - 1]
    func_name = f"run_mock_{strategy_name}_backtest"
    output_path = Path(__file__).parent.parent / "utils" / "trading_algorithms" / f"{func_name}.py"

    update_constants(strategy_name, output_path)
    print(f"Active algorithm set to: {func_name}")
