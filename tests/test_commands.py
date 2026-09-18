"""Тесты команд эмулятора, работающих с VFS и историей."""

import tempfile
import unittest
from pathlib import Path

from src.errors import (CommandArgumentError, UnknownCommandError,
                        VfsError, VfsPathError)
from src.repl import execute_line, make_prompt
from src.state import ShellState
from src.vfs import Vfs
from tests.test_vfs import make_archive

ENTRIES = {
    "home/user/docs/report.txt": b"report",
    "home/user/notes.txt": b"notes",
    "etc/config.ini": b"[app]",
}


class CommandTestCase(unittest.TestCase):
    """Базовый класс с загруженной в память VFS."""

    def setUp(self) -> None:
        """Готовит сеанс с образом VFS из нескольких каталогов."""
        self._directory = tempfile.TemporaryDirectory()
        path = make_archive(
            Path(self._directory.name) / "deep.zip", ENTRIES
        )
        self.state = ShellState(vfs_name="deep", vfs=Vfs.load(path))

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()


class ListCommandTest(CommandTestCase):
    """Проверяет команду ``ls``."""

    def test_lists_root_directory(self) -> None:
        """Без аргументов выводится содержимое текущего каталога."""
        self.assertEqual(execute_line(self.state, "ls"), "etc\nhome")

    def test_lists_given_path(self) -> None:
        """С аргументом выводится содержимое указанного каталога."""
        output = execute_line(self.state, "ls /home/user")
        self.assertEqual(output, "docs\nnotes.txt")

    def test_long_format_shows_mode_and_size(self) -> None:
        """Ключ -l добавляет права доступа и размер файла."""
        output = execute_line(self.state, "ls -l /home/user/notes.txt")
        self.assertTrue(output.startswith("-rw-r--r--"))
        self.assertTrue(output.endswith("notes.txt"))
        self.assertIn(str(len(b"notes")), output)

    def test_unknown_option_is_rejected(self) -> None:
        """Неизвестный ключ команды порождает ошибку."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "ls -z")

    def test_missing_path_is_reported(self) -> None:
        """Несуществующий путь порождает ошибку VFS."""
        with self.assertRaises(VfsPathError):
            execute_line(self.state, "ls /home/nobody")

    def test_requires_loaded_vfs(self) -> None:
        """Без загруженной VFS команда сообщает об ошибке."""
        with self.assertRaises(VfsError):
            execute_line(ShellState(), "ls")


class ChangeDirectoryTest(CommandTestCase):
    """Проверяет команду ``cd``."""

    def test_changes_current_directory(self) -> None:
        """Переход в каталог отражается в приглашении к вводу."""
        execute_line(self.state, "cd /home/user")
        self.assertEqual(self.state.cwd, ("home", "user"))
        self.assertEqual(make_prompt(self.state), "deep:/home/user$ ")

    def test_relative_path_is_supported(self) -> None:
        """Относительный путь отсчитывается от текущего каталога."""
        execute_line(self.state, "cd home")
        execute_line(self.state, "cd user/docs")
        self.assertEqual(self.state.cwd, ("home", "user", "docs"))

    def test_without_arguments_returns_to_root(self) -> None:
        """Без аргументов команда возвращает в корень VFS."""
        execute_line(self.state, "cd /home/user")
        execute_line(self.state, "cd")
        self.assertEqual(self.state.cwd, ())

    def test_file_is_not_a_directory(self) -> None:
        """Переход в файл порождает ошибку."""
        with self.assertRaises(VfsPathError):
            execute_line(self.state, "cd /etc/config.ini")

    def test_too_many_arguments_are_rejected(self) -> None:
        """Более одного пути команда не принимает."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "cd /etc /home")


class EchoAndHistoryTest(CommandTestCase):
    """Проверяет команды ``echo`` и ``history``."""

    def test_echo_joins_arguments(self) -> None:
        """Аргументы выводятся через один пробел."""
        output = execute_line(self.state, "echo привет    мир")
        self.assertEqual(output, "привет мир")

    def test_echo_without_arguments_prints_empty_line(self) -> None:
        """Без аргументов выводится пустая строка, а не ничего."""
        self.assertEqual(execute_line(self.state, "echo"), "")

    def test_history_numbers_entered_commands(self) -> None:
        """История хранит команды в порядке ввода."""
        execute_line(self.state, "ls")
        execute_line(self.state, "cd /etc")
        output = execute_line(self.state, "history")
        self.assertEqual(
            [line.split(maxsplit=1)[1] for line in output.splitlines()],
            ["ls", "cd /etc", "history"],
        )

    def test_history_limit_shows_last_entries(self) -> None:
        """Аргумент ограничивает вывод последними записями."""
        execute_line(self.state, "echo один")
        execute_line(self.state, "echo два")
        output = execute_line(self.state, "history 2")
        self.assertEqual(len(output.splitlines()), 2)
        self.assertIn("echo два", output)

    def test_history_rejects_non_positive_limit(self) -> None:
        """Неположительное или нечисловое ограничение отвергается."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "history 0")
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "history много")

    def test_failed_command_is_kept_in_history(self) -> None:
        """Ошибочная команда также попадает в историю."""
        with self.assertRaises(UnknownCommandError):
            execute_line(self.state, "wget")
        self.assertEqual(self.state.history, ["wget"])

    def test_exit_stops_the_session(self) -> None:
        """Команда ``exit`` снимает признак продолжения работы."""
        execute_line(self.state, "exit")
        self.assertFalse(self.state.running)


if __name__ == "__main__":
    unittest.main()
