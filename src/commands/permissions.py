"""Команда ``chmod``, изменяющая права доступа узлов VFS.

Изменения выполняются исключительно над деревом узлов в оперативной
памяти: исходный ZIP-архив не перезаписывается и остаётся нетронутым.
Поддерживаются как восьмеричная запись режима (``755``), так и
символьная (``u+x``, ``go-w``, ``a=r``, в том числе через запятую).
"""

import re

from src.commands.support import require_vfs
from src.errors import CommandArgumentError
from src.state import ShellState

SYMBOLIC_PATTERN = re.compile(
    r"^(?P<who>[ugoa]*)(?P<operation>[-+=])(?P<permissions>[rwx]*)$"
)
WHO_MASKS = {"u": 0o700, "g": 0o070, "o": 0o007, "a": 0o777}
PERMISSION_BITS = {"r": 0o444, "w": 0o222, "x": 0o111}
CLAUSE_SEPARATOR = ","
DEFAULT_WHO = "a"
MAX_MODE = 0o777
MIN_CHMOD_ARGS = 2
OCTAL_BASE = 8


def parse_octal_mode(value: str) -> int | None:
    """Разбирает режим доступа в восьмеричной записи.

    Args:
        value: Аргумент команды, например ``755``.

    Returns:
        Числовое значение режима либо ``None``, если запись не
        является восьмеричным числом.

    Raises:
        CommandArgumentError: Режим выходит за допустимые границы.
    """
    if not value.isdigit():
        return None
    try:
        mode = int(value, OCTAL_BASE)
    except ValueError as error:
        raise CommandArgumentError(
            f"chmod: {value} не является восьмеричным режимом"
        ) from error
    if mode > MAX_MODE:
        raise CommandArgumentError(
            f"chmod: режим {value} выходит за границы 000..777"
        )
    return mode


def apply_symbolic_clause(mode: int, clause: str) -> int:
    """Применяет одно символьное правило изменения прав.

    Args:
        mode: Текущий режим доступа узла.
        clause: Правило вида ``u+x`` либо ``go-w``.

    Returns:
        Новый режим доступа.

    Raises:
        CommandArgumentError: Правило записано неверно.
    """
    match = SYMBOLIC_PATTERN.match(clause)
    if match is None:
        raise CommandArgumentError(
            f"chmod: неверный режим доступа {clause}"
        )
    mask = 0
    for letter in match["who"] or DEFAULT_WHO:
        mask |= WHO_MASKS[letter]
    bits = 0
    for letter in match["permissions"]:
        bits |= PERMISSION_BITS[letter]
    value = bits & mask
    if match["operation"] == "+":
        return mode | value
    if match["operation"] == "-":
        return mode & ~value
    return (mode & ~mask) | value


def parse_mode(value: str, current: int) -> int:
    """Вычисляет новый режим доступа по аргументу команды.

    Args:
        value: Восьмеричная или символьная запись режима.
        current: Текущий режим доступа узла.

    Returns:
        Новый режим доступа.

    Raises:
        CommandArgumentError: Запись режима не распознана.
    """
    octal = parse_octal_mode(value)
    if octal is not None:
        return octal
    mode = current
    for clause in value.split(CLAUSE_SEPARATOR):
        mode = apply_symbolic_clause(mode, clause)
    return mode


def cmd_chmod(state: ShellState, args: tuple[str, ...]) -> str | None:
    """Изменяет права доступа одного или нескольких узлов VFS.

    Args:
        state: Текущее состояние сеанса.
        args: Режим доступа и хотя бы один путь.

    Returns:
        ``None``: при успехе команда ничего не выводит.

    Raises:
        CommandArgumentError: Не задан режим или путь, либо режим
            записан неверно.
        VfsError: VFS не загружена или путь не существует.
    """
    vfs = require_vfs(state)
    if len(args) < MIN_CHMOD_ARGS:
        raise CommandArgumentError(
            "chmod: ожидается режим доступа и хотя бы один путь"
        )
    mode_text = args[0]
    for target in args[1:]:
        _, node = vfs.resolve(state.cwd, target)
        node.mode = parse_mode(mode_text, node.mode)
    return None
