"""Команды, не зависящие от виртуальной файловой системы.

Сюда входят завершение работы, вывод текста и просмотр истории
введённых команд.
"""

from src.errors import CommandArgumentError
from src.state import ShellState

MAX_HISTORY_ARGS = 1
MIN_HISTORY_LIMIT = 1
NUMBER_FIELD_WIDTH = 4


def cmd_exit(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Завершает работу эмулятора.

    Args:
        state: Состояние сеанса, в котором снимается признак работы.
        args: Аргументы команды; должны отсутствовать.

    Returns:
        Прощальное сообщение.

    Raises:
        CommandArgumentError: Команде переданы лишние аргументы.
    """
    if args:
        raise CommandArgumentError("exit: аргументы не поддерживаются")
    state.running = False
    return "Выход из эмулятора."


def cmd_echo(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Выводит переданные аргументы, разделённые пробелом.

    Args:
        state: Текущее состояние сеанса (не используется).
        args: Произвольное число аргументов.

    Returns:
        Строка из аргументов; без аргументов — пустая строка.
    """
    del state
    return " ".join(args)


def parse_history_limit(value: str) -> int:
    """Разбирает число выводимых записей истории.

    Args:
        value: Аргумент команды ``history``.

    Returns:
        Положительное число записей.

    Raises:
        CommandArgumentError: Аргумент не является положительным числом.
    """
    try:
        limit = int(value)
    except ValueError as error:
        raise CommandArgumentError(
            f"history: {value} не является числом"
        ) from error
    if limit < MIN_HISTORY_LIMIT:
        raise CommandArgumentError(
            "history: ожидается положительное число записей"
        )
    return limit


def cmd_history(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Показывает историю введённых команд.

    Args:
        state: Состояние сеанса, хранящее историю.
        args: Необязательное число последних записей.

    Returns:
        Пронумерованный перечень команд либо ``None``, если история
        пуста.

    Raises:
        CommandArgumentError: Передано более одного аргумента или
            аргумент не является положительным числом.
    """
    if len(args) > MAX_HISTORY_ARGS:
        raise CommandArgumentError("history: ожидается один аргумент")
    entries = state.history
    if args:
        entries = entries[-parse_history_limit(args[0]):]
    if not entries:
        return None
    first = len(state.history) - len(entries) + 1
    return "\n".join(
        f"{first + offset:>{NUMBER_FIELD_WIDTH}}  {line}"
        for offset, line in enumerate(entries)
    )
