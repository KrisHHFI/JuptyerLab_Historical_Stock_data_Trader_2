import sys
from cmd_create_new import cmd_create_new
from cmd_create_refine import cmd_create_refine
from cmd_clear import cmd_clear
from cmd_delete_active import cmd_delete_active
from cmd_run import cmd_run
from cmd_set import cmd_set

COMMANDS = {
    "help":          "Show this help page.",
    "create":        "Generate a new trading algorithm and set it as the active strategy.",
    "refine":        "Run the ML parameter optimizer to tune the active algorithm.",
    "set":           "Choose an existing algorithm to set as the active strategy.",
    "clear":         "Remove the active algorithm (sets active_algorithm to None).",
    "delete active": "Delete the active algorithm file and remove it from the project.",
    "run":           "Restart the kernel and run main.ipynb end-to-end.",
}


def print_help() -> None:
    print("Usage: trader <command>")
    print()
    print("Available commands:")
    for cmd, description in COMMANDS.items():
        print(f"  {cmd:<20} {description}")
    print()


if __name__ == "__main__":
    args = sys.argv[1:]
    command = " ".join(args).strip().lower()

    if command == "create":
        cmd_create_new()
    elif command == "refine":
        cmd_create_refine()
    elif command == "set":
        cmd_set()
    elif command == "clear":
        cmd_clear()
    elif command == "delete active":
        cmd_delete_active()
    elif command == "run":
        cmd_run()
    else:
        print_help()

