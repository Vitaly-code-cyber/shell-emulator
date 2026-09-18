"""Состояние сеанса работы эмулятора."""

from dataclasses import dataclass, field

from src.logger import EventLog

DEFAULT_VFS_NAME = "vfs"


@dataclass
class ShellState:
    """Изменяемое состояние одного сеанса работы эмулятора.

    Attributes:
        vfs_name: Имя VFS, отображаемое в приглашении к вводу.
        log: Журнал событий вызова команд.
        running: Признак продолжения диалога; ``False`` после ``exit``.
    """

    vfs_name: str = DEFAULT_VFS_NAME
    log: EventLog = field(default_factory=EventLog)
    running: bool = field(default=True)
