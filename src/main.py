"""Точка входа эмулятора командной оболочки.

Запуск: ``python3 -m src.main``.
"""

import sys

from src.repl import run_interactive
from src.state import ShellState

EXIT_SUCCESS = 0


def main() -> int:
    """Создаёт состояние сеанса и запускает интерактивный режим.

    Returns:
        Код возврата процесса.
    """
    state = ShellState()
    run_interactive(state)
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
