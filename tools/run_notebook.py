import subprocess
import sys
import os


def run_notebook() -> None:
    notebook_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.ipynb")
    python_dir = os.path.dirname(sys.executable)
    jupyter = os.path.join(python_dir, "jupyter")

    print("Restarting kernel and running main.ipynb...")
    subprocess.run(
        [jupyter, "nbconvert", "--to", "notebook", "--execute", "--inplace", notebook_path],
        check=True,
    )
    print("main.ipynb execution complete.")
