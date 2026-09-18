"""Реестр команд эмулятора и их диспетчеризация.

Команды хранятся в словаре, а не в цепочке условий: это удерживает
цикломатическую сложность диспетчера на минимальном уровне и
позволяет добавлять новые команды на следующих этапах без правки
логики выполнения.
"""

from typing import Callable

from src.commands import stubs
from src.errors import UnknownCommandError
from src.parser import Command
from src.state import ShellState

CommandHandler = Callable[[ShellState, tuple[str, ...]], str]

COMMANDS: dict[str, CommandHandler] = {
    "ls": stubs.cmd_ls,
    "cd": stubs.cmd_cd,
    "exit": stubs.cmd_exit,
}


def dispatch(state: ShellState, command: Command) -> str:
    """Находит обработчик команды и выполняет его.

    Args:
        state: Текущее состояние сеанса.
        command: Разобранная команда с аргументами.

    Returns:
        Текст, который эмулятор должен показать пользователю.

    Raises:
        UnknownCommandError: Команда отсутствует в реестре.
    """
    handler = COMMANDS.get(command.name)
    if handler is None:
        raise UnknownCommandError(
            f"{command.name}: команда не найдена"
        )
    return handler(state, command.args)
