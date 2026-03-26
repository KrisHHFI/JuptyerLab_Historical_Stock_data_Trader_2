import re
from pathlib import Path

CONSTANTS_PATH = Path(__file__).parent.parent / "constants.py"


def cmd_clear() -> None:
    """Remove the active algorithm from constants.py."""
    content = CONSTANTS_PATH.read_text(encoding="utf-8")

    # Remove any trading_algorithms import lines
    content = re.sub(
        r"^from utils\.trading_algorithms\.\S+ import \S+\n",
        "",
        content,
        flags=re.MULTILINE,
    )

    # Set active_algorithm to None
    content = re.sub(
        r"^active_algorithm\s*=.*$",
        "active_algorithm = None",
        content,
        flags=re.MULTILINE,
    )

    CONSTANTS_PATH.write_text(content, encoding="utf-8")
    print("Active algorithm cleared. active_algorithm is now None.")
