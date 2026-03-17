import re
from get_client import get_client
from get_strategy_name import get_strategy_name
from generate_algorithm_code import generate_algorithm_code
from generate_ml_params_code import generate_ml_params_code
from save_algorithm import save_algorithm
from save_ml_params import save_ml_params
from update_constants import update_constants
from run_notebook import run_notebook


def cmd_create_new() -> None:
    client = get_client()

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

    update_constants(strategy_name, output_path)
    print(f"Updated constants.py: active_algorithm = run_mock_{re.sub(r'[^a-z0-9_]', '', strategy_name.lower().replace(' ', '_'))}_backtest")

    run_notebook()
