"""Цикл «чтение — разбор — выполнение» (REPL).

Модуль отвечает за диалог с пользователем: формирует приглашение к
вводу, передаёт строку парсеру и диспетчеру команд и печатает
результат либо сообщение об ошибке.
"""

import sys

from src import commands
from src.errors import EmulatorError
from src.parser import parse_line
from src.state import ShellState


def make_prompt(state: ShellState) -> str:
    """Формирует приглашение к вводу, содержащее имя VFS.

    Args:
        state: Текущее состояние сеанса.

    Returns:
        Строка приглашения, например ``minimal$``.
    """
    return f"{state.vfs_name}$ "


def execute_line(state: ShellState, line: str) -> str | None:
    """Разбирает и выполняет одну строку ввода.

    Args:
        state: Текущее состояние сеанса.
        line: Строка, введённая пользователем.

    Returns:
        Вывод команды либо ``None``, если строка пуста.

    Raises:
        EmulatorError: Команда неизвестна или вызвана неверно.
    """
    command = parse_line(line)
    if command is None:
        return None
    return commands.dispatch(state, command)


def report_error(error: EmulatorError) -> None:
    """Печатает сообщение об ошибке в стандартный поток ошибок.

    Args:
        error: Возникшая ошибка эмулятора.
    """
    print(f"ошибка: {error}", file=sys.stderr)


def run_interactive(state: ShellState) -> None:
    """Запускает интерактивный диалог с пользователем.

    Диалог продолжается до команды ``exit`` или до конца ввода
    (сочетание клавиш Ctrl+D).

    Args:
        state: Состояние сеанса, изменяемое командами.
    """
    while state.running:
        try:
            line = input(make_prompt(state))
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            output = execute_line(state, line)
        except EmulatorError as error:
            report_error(error)
            continue
        if output:
            print(output)
