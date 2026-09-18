"""Выполнение стартового скрипта эмулятора.

Скрипт — это текстовый файл с командами эмулятора, по одной в строке.
При выполнении на экран выводится как ввод, так и вывод команд, что
имитирует диалог с пользователем. Выполнение прекращается на первой
же ошибке.
"""

from pathlib import Path

from src.errors import EmulatorError, ScriptError
from src.repl import execute_line, make_prompt, report_error
from src.state import ShellState

COMMENT_PREFIX = "#"
LOG_KIND_SCRIPT = "script"


def read_script_lines(path: Path) -> list[str]:
    """Читает строки стартового скрипта.

    Args:
        path: Путь к файлу скрипта.

    Returns:
        Список строк файла без символов перевода строки.

    Raises:
        ScriptError: Файл не найден или недоступен для чтения.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ScriptError(
            f"стартовый скрипт {path} недоступен: {error.strerror}"
        ) from error
    return text.splitlines()


def is_executable_line(line: str) -> bool:
    """Проверяет, содержит ли строка скрипта команду.

    Args:
        line: Строка стартового скрипта.

    Returns:
        ``True`` для строк с командами, ``False`` для пустых строк и
        строк с комментариями.
    """
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(COMMENT_PREFIX)


def run_script(state: ShellState, path: Path) -> bool:
    """Выполняет стартовый скрипт, имитируя диалог с пользователем.

    Args:
        state: Состояние сеанса, изменяемое командами скрипта.
        path: Путь к файлу скрипта.

    Returns:
        ``True``, если скрипт выполнен полностью, иначе ``False``.

    Raises:
        ScriptError: Файл скрипта недоступен для чтения.
    """
    for number, line in enumerate(read_script_lines(path), start=1):
        if not is_executable_line(line):
            continue
        print(f"{make_prompt(state)}{line.strip()}")
        try:
            output = execute_line(state, line)
        except EmulatorError as error:
            _report_script_failure(state, path, number, error)
            return False
        if output:
            print(output)
        if not state.running:
            break
    return True


def _report_script_failure(state: ShellState, path: Path, number: int,
                           error: EmulatorError) -> None:
    """Сообщает об ошибке выполнения строки стартового скрипта.

    Args:
        state: Состояние сеанса, журнал которого пополняется записью.
        path: Путь к файлу скрипта.
        number: Номер строки, вызвавшей ошибку.
        error: Возникшая ошибка эмулятора.
    """
    message = f"{path}:{number}: {error}"
    report_error(EmulatorError(f"{message} (выполнение остановлено)"))
    state.log.log_message(LOG_KIND_SCRIPT, message)
