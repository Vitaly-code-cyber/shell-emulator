"""Команды обхода виртуальной файловой системы: ``ls`` и ``cd``.

Все операции выполняются над деревом узлов в оперативной памяти;
исходный ZIP-архив при этом не читается повторно и не изменяется.
"""

from src.commands.support import format_mode, require_vfs
from src.errors import CommandArgumentError, VfsPathError
from src.state import ShellState
from src.vfs import CURRENT_DIR, PATH_SEPARATOR, VfsNode

LONG_OPTION = "-l"
OPTION_PREFIX = "-"
MAX_PATH_ARGS = 1
SIZE_FIELD_WIDTH = 7


def split_options(name: str,
                  args: tuple[str, ...]) -> tuple[bool, tuple[str, ...]]:
    """Отделяет ключи команды от путей.

    Args:
        name: Имя команды для сообщений об ошибках.
        args: Аргументы команды.

    Returns:
        Пару «признак подробного вывода, список путей».

    Raises:
        CommandArgumentError: Передан неизвестный ключ.
    """
    long_format = False
    paths: list[str] = []
    for argument in args:
        if not argument.startswith(OPTION_PREFIX):
            paths.append(argument)
            continue
        if argument != LONG_OPTION:
            raise CommandArgumentError(
                f"{name}: неизвестный ключ {argument}"
            )
        long_format = True
    return long_format, tuple(paths)


def format_entry(node: VfsNode, long_format: bool) -> str:
    """Формирует строку вывода для одного узла VFS.

    Args:
        node: Узел виртуальной файловой системы.
        long_format: Признак подробного вывода с правами и размером.

    Returns:
        Готовая строка вывода команды ``ls``.
    """
    if not long_format:
        return node.name
    size = f"{node.size:>{SIZE_FIELD_WIDTH}}"
    return f"{format_mode(node)} {size} {node.name}"


def cmd_ls(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Выводит содержимое каталога VFS.

    Args:
        state: Текущее состояние сеанса.
        args: Ключ ``-l`` и не более одного пути.

    Returns:
        Перечень элементов каталога либо ``None`` для пустого каталога.

    Raises:
        CommandArgumentError: Передано несколько путей или неверный ключ.
        VfsError: VFS не загружена или путь не существует.
    """
    vfs = require_vfs(state)
    long_format, paths = split_options("ls", args)
    if len(paths) > MAX_PATH_ARGS:
        raise CommandArgumentError("ls: ожидается не более одного пути")
    target = paths[0] if paths else CURRENT_DIR
    _, node = vfs.resolve(state.cwd, target)
    entries = (sorted(node.children.values(), key=lambda item: item.name)
               if node.is_dir else [node])
    if not entries:
        return None
    return "\n".join(format_entry(entry, long_format) for entry in entries)


def cmd_cd(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Меняет текущий каталог внутри VFS.

    Args:
        state: Состояние сеанса, в котором обновляется текущий каталог.
        args: Не более одного пути; без аргументов переходит в корень.

    Returns:
        ``None``: команда ничего не выводит при успехе.

    Raises:
        CommandArgumentError: Передано более одного пути.
        VfsError: VFS не загружена, путь не существует или это файл.
    """
    vfs = require_vfs(state)
    if len(args) > MAX_PATH_ARGS:
        raise CommandArgumentError("cd: ожидается не более одного пути")
    target = args[0] if args else PATH_SEPARATOR
    parts, node = vfs.resolve(state.cwd, target)
    if not node.is_dir:
        raise VfsPathError(f"{target}: не является каталогом")
    state.cwd = parts
    return None
