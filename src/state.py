"""Состояние сеанса работы эмулятора."""

from dataclasses import dataclass, field

DEFAULT_VFS_NAME = "vfs"


@dataclass
class ShellState:
    """Изменяемое состояние одного сеанса работы эмулятора.

    Attributes:
        vfs_name: Имя VFS, отображаемое в приглашении к вводу.
        running: Признак продолжения диалога; ``False`` после ``exit``.
    """

    vfs_name: str = DEFAULT_VFS_NAME
    running: bool = field(default=True)
