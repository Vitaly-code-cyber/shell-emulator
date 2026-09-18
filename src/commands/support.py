"""Вспомогательные средства, общие для команд эмулятора."""

from src.errors import VfsError
from src.state import ShellState
from src.vfs import Vfs, VfsNode

PERMISSION_SHIFTS = (6, 3, 0)
READ_BIT = 0b100
WRITE_BIT = 0b010
EXECUTE_BIT = 0b001


def require_vfs(state: ShellState) -> Vfs:
    """Возвращает загруженную VFS либо сообщает об её отсутствии.

    Args:
        state: Текущее состояние сеанса.

    Returns:
        Виртуальная файловая система сеанса.

    Raises:
        VfsError: Образ VFS не был загружен при запуске.
    """
    if state.vfs is None:
        raise VfsError(
            "VFS не загружена: укажите параметр --vfs при запуске"
        )
    return state.vfs


def format_mode(node: VfsNode) -> str:
    """Представляет права доступа узла в виде строки ``drwxr-xr-x``.

    Args:
        node: Узел виртуальной файловой системы.

    Returns:
        Десятисимвольная строка с типом узла и правами доступа.
    """
    letters = ["d" if node.is_dir else "-"]
    for shift in PERMISSION_SHIFTS:
        value = (node.mode >> shift) & 0o7
        letters.append("r" if value & READ_BIT else "-")
        letters.append("w" if value & WRITE_BIT else "-")
        letters.append("x" if value & EXECUTE_BIT else "-")
    return "".join(letters)
