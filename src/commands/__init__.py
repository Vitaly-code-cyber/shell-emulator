"""Реестр команд эмулятора и их диспетчеризация.

Команды хранятся в словаре, а не в цепочке условий: это удерживает
цикломатическую сложность диспетчера на минимальном уровне и
позволяет добавлять новые команды без правки логики выполнения.
"""

from typing import Callable

from src.commands import basic, filesystem, permissions
from src.errors import UnknownCommandError
from src.parser import Command
from src.state import ShellState

CommandHandler = Callable[[ShellState, tuple[str, ...]], str | None]

COMMANDS: dict[str, CommandHandler] = {
    "ls": filesystem.cmd_ls,
    "cd": filesystem.cmd_cd,
    "chmod": permissions.cmd_chmod,
    "echo": basic.cmd_echo,
    "history": basic.cmd_history,
    "exit": basic.cmd_exit,
}


def dispatch(state: ShellState, command: Command) -> str | None:
    """Находит обработчик команды и выполняет его.

    Args:
        state: Текущее состояние сеанса.
        command: Разобранная команда с аргументами.

    Returns:
        Текст для показа пользователю либо ``None``, если команда
        ничего не выводит.

    Raises:
        UnknownCommandError: Команда отсутствует в реестре.
    """
    handler = COMMANDS.get(command.name)
    if handler is None:
        raise UnknownCommandError(
            f"{command.name}: команда не найдена"
        )
    return handler(state, command.args)
