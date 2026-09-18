"""Команды-заглушки первого этапа разработки.

На этапе прототипа команды ``ls`` и ``cd`` не выполняют полезной
работы: они лишь подтверждают, что ввод разобран верно, и печатают
собственное имя вместе с полученными аргументами.
"""

from src.errors import CommandArgumentError
from src.state import ShellState

MAX_CD_ARGS = 1


def format_stub(name: str, args: tuple[str, ...]) -> str:
    """Формирует отладочный вывод команды-заглушки.

    Args:
        name: Имя вызванной команды.
        args: Аргументы, полученные командой.

    Returns:
        Строка вида ``ls: аргументы = [-l, /etc]``.
    """
    listed = ", ".join(args) if args else "нет"
    return f"{name}: аргументы = [{listed}]"


def cmd_ls(state: ShellState, args: tuple[str, ...]) -> str:
    """Заглушка команды ``ls``.

    Args:
        state: Текущее состояние сеанса (не используется).
        args: Аргументы команды.

    Returns:
        Отладочное описание вызова команды.
    """
    del state
    return format_stub("ls", args)


def cmd_cd(state: ShellState, args: tuple[str, ...]) -> str:
    """Заглушка команды ``cd``.

    Args:
        state: Текущее состояние сеанса (не используется).
        args: Аргументы команды; допускается не более одного.

    Returns:
        Отладочное описание вызова команды.

    Raises:
        CommandArgumentError: Передано более одного аргумента.
    """
    del state
    if len(args) > MAX_CD_ARGS:
        raise CommandArgumentError("cd: ожидается не более одного пути")
    return format_stub("cd", args)


def cmd_exit(state: ShellState, args: tuple[str, ...]) -> str:
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
