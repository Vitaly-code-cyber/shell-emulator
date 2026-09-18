"""Тесты журналирования событий в формате XML."""

import tempfile
import unittest
import xml.etree.ElementTree as ElementTree
from pathlib import Path

from src.logger import XmlEventLog

TEST_USER = "tester"


class XmlEventLogTest(unittest.TestCase):
    """Проверяет структуру и содержимое XML-журнала."""

    def setUp(self) -> None:
        """Создаёт временный каталог для лог-файла."""
        self._directory = tempfile.TemporaryDirectory()
        self.path = Path(self._directory.name) / "session.xml"
        self.log = XmlEventLog(self.path, user=TEST_USER)

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()

    def _events(self) -> list[ElementTree.Element]:
        """Читает события из созданного лог-файла."""
        return list(ElementTree.parse(self.path).getroot())

    def test_empty_log_is_valid_xml(self) -> None:
        """Журнал без событий является корректным XML-документом."""
        root = ElementTree.parse(self.path).getroot()
        self.assertEqual(root.tag, "session")
        self.assertEqual(root.get("user"), TEST_USER)

    def test_successful_command_is_recorded(self) -> None:
        """Успешный вызов команды попадает в журнал со статусом ok."""
        self.log.log_command("ls", ("-l", "/etc"))
        event = self._events()[0]
        self.assertEqual(event.get("command"), "ls")
        self.assertEqual(event.get("status"), "ok")
        self.assertEqual(event.get("user"), TEST_USER)
        self.assertEqual(event.find("arguments").text, "-l /etc")

    def test_failed_command_stores_error_message(self) -> None:
        """Ошибочный вызов сохраняет сообщение об ошибке."""
        self.log.log_command("wget", (), "wget: команда не найдена")
        event = self._events()[0]
        self.assertEqual(event.get("status"), "error")
        self.assertEqual(event.find("error").text,
                         "wget: команда не найдена")

    def test_events_are_appended_in_order(self) -> None:
        """События сохраняются в порядке их возникновения."""
        self.log.log_command("ls", ())
        self.log.log_command("cd", ("/home",))
        self.log.log_message("script", "остановка")
        tags = [event.get("command") or event.get("kind")
                for event in self._events()]
        self.assertEqual(tags, ["ls", "cd", "script"])


if __name__ == "__main__":
    unittest.main()
