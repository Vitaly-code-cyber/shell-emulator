"""Точка входа эмулятора командной оболочки.

Запуск: ``python3 -m src.main [--vfs ПУТЬ] [--log ПУТЬ] [--script ПУТЬ]``.
"""

import sys
from pathlib import Path

from src.cli import Options, format_options, parse_options
from src.errors import EmulatorError
from src.logger import EventLog, XmlEventLog
from src.repl import report_error, run_interactive
from src.script import run_script
from src.state import DEFAULT_VFS_NAME, ShellState

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
LOG_KIND_STARTUP = "startup"


def vfs_name_from(path: Path | None) -> str:
    """Определяет имя VFS для приглашения к вводу.

    Args:
        path: Путь к образу VFS либо ``None``.

    Returns:
        Имя файла образа без расширения либо имя по умолчанию.
    """
    return path.stem if path is not None else DEFAULT_VFS_NAME


def build_state(options: Options) -> ShellState:
    """Создаёт состояние сеанса по параметрам командной строки.

    Args:
        options: Разобранные параметры запуска.

    Returns:
        Подготовленное состояние сеанса.
    """
    log: EventLog = EventLog()
    if options.log_path is not None:
        log = XmlEventLog(options.log_path)
    return ShellState(vfs_name=vfs_name_from(options.vfs_path), log=log)


def run_startup_script(state: ShellState, path: Path) -> bool:
    """Выполняет стартовый скрипт и сообщает об ошибках доступа к нему.

    Args:
        state: Состояние сеанса.
        path: Путь к стартовому скрипту.

    Returns:
        ``True``, если скрипт выполнен полностью, иначе ``False``.
    """
    try:
        return run_script(state, path)
    except EmulatorError as error:
        report_error(error)
        state.log.log_message(LOG_KIND_STARTUP, str(error))
        return False


def main(argv: list[str] | None = None) -> int:
    """Разбирает параметры, выполняет скрипт и запускает диалог.

    Args:
        argv: Аргументы командной строки; по умолчанию ``sys.argv``.

    Returns:
        Код возврата процесса.
    """
    options = parse_options(argv)
    print(format_options(options))
    state = build_state(options)
    if options.script_path is not None:
        if not run_startup_script(state, options.script_path):
            return EXIT_FAILURE
    if state.running:
        run_interactive(state)
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
