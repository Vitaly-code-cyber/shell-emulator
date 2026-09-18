"""Тесты выполнения стартового скрипта и разбора параметров."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from src.cli import format_options, parse_options
from src.errors import ScriptError
from src.script import is_executable_line, run_script
from src.state import ShellState


def run_script_quietly(state: ShellState, path: Path) -> tuple[bool, str]:
    """Выполняет скрипт, перехватывая его вывод.

    Args:
        state: Состояние сеанса.
        path: Путь к стартовому скрипту.

    Returns:
        Пару «признак успеха, перехваченный вывод».
    """
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        with contextlib.redirect_stderr(stream):
            completed = run_script(state, path)
    return completed, stream.getvalue()


class ScriptRunnerTest(unittest.TestCase):
    """Проверяет поведение исполнителя стартовых скриптов."""

    def setUp(self) -> None:
        """Создаёт временный каталог для файлов скриптов."""
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name)
        self.state = ShellState(vfs_name="test")

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()

    def _write_script(self, text: str) -> Path:
        """Сохраняет текст скрипта во временный файл."""
        path = self.root / "startup.vsh"
        path.write_text(text, encoding="utf-8")
        return path

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        """Комментарии и пустые строки командами не считаются."""
        self.assertFalse(is_executable_line("   "))
        self.assertFalse(is_executable_line("  # комментарий"))
        self.assertTrue(is_executable_line("ls -l"))

    def test_script_echoes_input_and_output(self) -> None:
        """При выполнении отображается и ввод, и вывод команд."""
        path = self._write_script("echo привет\n")
        completed, output = run_script_quietly(self.state, path)
        self.assertTrue(completed)
        self.assertIn("test:/$ echo привет", output)
        self.assertIn("\nпривет\n", output)

    def test_script_stops_at_first_error(self) -> None:
        """Выполнение прекращается на первой ошибочной команде."""
        path = self._write_script("echo начало\nwget\necho конец\n")
        completed, output = run_script_quietly(self.state, path)
        self.assertFalse(completed)
        self.assertIn("команда не найдена", output)
        self.assertNotIn("конец", output)

    def test_missing_script_raises_error(self) -> None:
        """Отсутствующий файл скрипта порождает ошибку эмулятора."""
        with self.assertRaises(ScriptError):
            run_script(self.state, self.root / "no_such_file.vsh")


class OptionsTest(unittest.TestCase):
    """Проверяет разбор и отладочный вывод параметров запуска."""

    def test_all_options_are_parsed(self) -> None:
        """Разбираются все три параметра командной строки."""
        options = parse_options(
            ["--vfs", "a.zip", "--log", "b.xml", "--script", "c.vsh"]
        )
        self.assertEqual(options.vfs_path, Path("a.zip"))
        self.assertEqual(options.log_path, Path("b.xml"))
        self.assertEqual(options.script_path, Path("c.vsh"))

    def test_missing_options_are_reported_as_absent(self) -> None:
        """Незаданные параметры отражаются в отладочном выводе."""
        text = format_options(parse_options([]))
        self.assertEqual(text.count("не задан"), 3)


if __name__ == "__main__":
    unittest.main()
