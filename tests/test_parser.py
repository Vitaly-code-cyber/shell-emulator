"""Тесты разбора строки пользовательского ввода."""

import unittest

from src.parser import parse_line


class ParseLineTest(unittest.TestCase):
    """Проверяет деление строки на команду и аргументы."""

    def test_empty_line_gives_no_command(self) -> None:
        """Пустая строка не порождает команду."""
        self.assertIsNone(parse_line("   "))

    def test_single_word_line(self) -> None:
        """Строка из одного слова разбирается в команду без аргументов."""
        command = parse_line("exit")
        self.assertIsNotNone(command)
        self.assertEqual(command.name, "exit")
        self.assertEqual(command.args, ())

    def test_arguments_are_split_by_spaces(self) -> None:
        """Аргументы отделяются друг от друга пробелами."""
        command = parse_line("ls -l /etc")
        self.assertEqual(command.name, "ls")
        self.assertEqual(command.args, ("-l", "/etc"))

    def test_repeated_spaces_are_ignored(self) -> None:
        """Повторяющиеся пробелы не порождают пустых аргументов."""
        command = parse_line("  echo   a    b  ")
        self.assertEqual(command.name, "echo")
        self.assertEqual(command.args, ("a", "b"))


if __name__ == "__main__":
    unittest.main()
