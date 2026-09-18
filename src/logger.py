"""Журналирование событий вызова команд в формате XML.

Журнал перезаписывается после каждого события, поэтому файл остаётся
корректным XML-документом даже при аварийном завершении эмулятора.
Каждое событие дополнительно содержит имя пользователя и, в случае
неудачи, сообщение о возникшей ошибке.
"""

import getpass
import xml.etree.ElementTree as ElementTree
from datetime import datetime
from pathlib import Path

UNKNOWN_USER = "unknown"
STATUS_OK = "ok"
STATUS_ERROR = "error"


def current_user() -> str:
    """Определяет имя пользователя реальной операционной системы.

    Returns:
        Имя пользователя либо ``unknown``, если оно недоступно.
    """
    try:
        return getpass.getuser()
    except OSError:
        return UNKNOWN_USER


def _timestamp() -> str:
    """Возвращает текущее время в формате ISO 8601 с точностью до секунд."""
    return datetime.now().isoformat(timespec="seconds")


class EventLog:
    """Журнал-заглушка, не выполняющий записи.

    Используется, когда путь к лог-файлу не задан в параметрах
    командной строки.
    """

    def log_command(self, name: str, args: tuple[str, ...],
                    error: str | None = None) -> None:
        """Регистрирует вызов команды.

        Args:
            name: Имя вызванной команды.
            args: Аргументы команды.
            error: Сообщение об ошибке либо ``None`` при успехе.
        """

    def log_message(self, kind: str, text: str) -> None:
        """Регистрирует служебное событие эмулятора.

        Args:
            kind: Вид события, например ``vfs`` или ``script``.
            text: Описание события.
        """


class XmlEventLog(EventLog):
    """Журнал событий, сохраняемый в XML-файл."""

    def __init__(self, path: Path, user: str | None = None) -> None:
        """Создаёт журнал и немедленно записывает пустой документ.

        Args:
            path: Путь к создаваемому лог-файлу.
            user: Имя пользователя; по умолчанию определяется из ОС.
        """
        self.path = path
        self.user = user or current_user()
        self._root = ElementTree.Element(
            "session", user=self.user, started=_timestamp()
        )
        self._flush()

    def log_command(self, name: str, args: tuple[str, ...],
                    error: str | None = None) -> None:
        """Записывает событие вызова команды.

        Args:
            name: Имя вызванной команды.
            args: Аргументы команды.
            error: Сообщение об ошибке либо ``None`` при успехе.
        """
        status = STATUS_ERROR if error else STATUS_OK
        event = ElementTree.SubElement(
            self._root,
            "event",
            time=_timestamp(),
            user=self.user,
            command=name,
            status=status,
        )
        ElementTree.SubElement(event, "arguments").text = " ".join(args)
        if error:
            ElementTree.SubElement(event, "error").text = error
        self._flush()

    def log_message(self, kind: str, text: str) -> None:
        """Записывает служебное событие эмулятора.

        Args:
            kind: Вид события, например ``vfs`` или ``script``.
            text: Описание события.
        """
        message = ElementTree.SubElement(
            self._root, "message", time=_timestamp(),
            user=self.user, kind=kind,
        )
        message.text = text
        self._flush()

    def _flush(self) -> None:
        """Сохраняет текущее состояние журнала на диск."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tree = ElementTree.ElementTree(self._root)
        ElementTree.indent(tree, space="  ")
        tree.write(self.path, encoding="utf-8", xml_declaration=True)
