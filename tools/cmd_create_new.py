import re
from get_client import get_client
from get_active_algorithm_name import get_active_algorithm_name
from get_strategy_name import get_strategy_name
from generate_algorithm_code import generate_algorithm_code
from generate_ml_params_code import generate_ml_params_code
from save_algorithm import save_algorithm
from save_ml_params import save_ml_params
from update_constants import update_constants
from evaluate_algorithm import evaluate_algorithm
from discard_algorithm import discard_algorithm
from run_notebook import run_notebook

MAX_ATTEMPTS = 3
MIN_TOTAL_TRADES = 1
MIN_RETURN_PCT = -10.0


def cmd_create_new() -> None:
    client = get_client()
    accepted = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        if attempt > 1:
            print(f"\n--- Attempt {attempt}/{MAX_ATTEMPTS} ---")

        prev_func_name = get_active_algorithm_name()

        strategy_name = get_strategy_name(client)
        print(f"Strategy: {strategy_name}")

        print("Generating algorithm code...")
        code = generate_algorithm_code(client, strategy_name)

        output_path = save_algorithm(strategy_name, code)
        print(f"Saved to: {output_path}")

        print("Generating ML param builder...")
        params_code = generate_ml_params_code(client, strategy_name, code)
        save_ml_params(strategy_name, params_code)
        print("ML param builder registered in ml_constants.py")

        safe_name = re.sub(r"[^a-z0-9_]", "", strategy_name.lower().replace(" ", "_"))
        update_constants(strategy_name, output_path)
        print(f"Updated constants.py: active_algorithm = run_mock_{safe_name}_backtest")

        print("Evaluating algorithm performance...")
        result = evaluate_algorithm(strategy_name)

        failures: list[str] = []
        if result.get("error"):
            failures.append("raised an error during evaluation")
        if result["trade_count"] < MIN_TOTAL_TRADES:
            failures.append("executed zero trades across all stocks")
        if result["return_pct"] < MIN_RETURN_PCT:
            failures.append(f"combined return too low ({result['return_pct']:.1f}%)")

        if failures:
            print(f"  Discarding — {'; '.join(failures)}. Retrying...")
            discard_algorithm(strategy_name, prev_func_name)
            continue

        print(f"  Accepted: {result['trade_count']} trades, {result['return_pct']:.1f}% combined return")
        accepted = True
        break

    if accepted:
        run_notebook()
    else:
        print(f"\nAll {MAX_ATTEMPTS} attempts produced unacceptable results. No new algorithm was activated.")
