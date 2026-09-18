"""Состояние сеанса работы эмулятора."""

from dataclasses import dataclass, field

from src.logger import EventLog
from src.vfs import Vfs

DEFAULT_VFS_NAME = "vfs"


@dataclass
class ShellState:
    """Изменяемое состояние одного сеанса работы эмулятора.

    Attributes:
        vfs_name: Имя VFS, отображаемое в приглашении к вводу.
        log: Журнал событий вызова команд.
        vfs: Загруженная в память VFS либо ``None``.
        cwd: Текущий каталог внутри VFS в виде имён от корня.
        history: Введённые команды в порядке их выполнения.
        running: Признак продолжения диалога; ``False`` после ``exit``.
    """

    vfs_name: str = DEFAULT_VFS_NAME
    log: EventLog = field(default_factory=EventLog)
    vfs: Vfs | None = None
    cwd: tuple[str, ...] = ()
    history: list[str] = field(default_factory=list)
    running: bool = field(default=True)
