"""Тесты команд-заглушек первого этапа."""

import unittest

from src import commands
from src.errors import CommandArgumentError, UnknownCommandError
from src.parser import parse_line
from src.repl import execute_line, make_prompt
from src.state import ShellState


class StubCommandsTest(unittest.TestCase):
    """Проверяет поведение прототипа эмулятора."""

    def setUp(self) -> None:
        """Готовит чистое состояние сеанса для каждого теста."""
        self.state = ShellState(vfs_name="minimal")

    def test_prompt_contains_vfs_name(self) -> None:
        """Приглашение к вводу содержит имя VFS."""
        self.assertTrue(make_prompt(self.state).startswith("minimal"))

    def test_ls_stub_prints_name_and_arguments(self) -> None:
        """Заглушка ``ls`` печатает своё имя и аргументы."""
        output = execute_line(self.state, "ls -l /etc")
        self.assertEqual(output, "ls: аргументы = [-l, /etc]")

    def test_cd_stub_without_arguments(self) -> None:
        """Заглушка ``cd`` сообщает об отсутствии аргументов."""
        self.assertEqual(execute_line(self.state, "cd"),
                         "cd: аргументы = [нет]")

    def test_cd_rejects_extra_arguments(self) -> None:
        """Команда ``cd`` отвергает более одного аргумента."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "cd /etc /tmp")

    def test_unknown_command_raises_error(self) -> None:
        """Неизвестная команда порождает ошибку эмулятора."""
        with self.assertRaises(UnknownCommandError):
            commands.dispatch(self.state, parse_line("wget"))

    def test_exit_stops_the_session(self) -> None:
        """Команда ``exit`` снимает признак продолжения работы."""
        execute_line(self.state, "exit")
        self.assertFalse(self.state.running)

    def test_exit_rejects_arguments(self) -> None:
        """Команда ``exit`` не принимает аргументов."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "exit now")


if __name__ == "__main__":
    unittest.main()
