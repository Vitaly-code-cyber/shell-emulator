"""Тесты команды chmod, изменяющей права доступа в памяти."""

import tempfile
import unittest
from pathlib import Path

from src.commands.support import format_mode
from src.errors import CommandArgumentError, VfsPathError
from src.repl import execute_line
from src.state import ShellState
from src.vfs import Vfs
from tests.test_vfs import make_archive

ENTRIES = {
    "home/user/notes.txt": b"notes",
    "etc/config.ini": b"[app]",
}


class ChmodTest(unittest.TestCase):
    """Проверяет разбор режимов доступа и их применение."""

    def setUp(self) -> None:
        """Готовит сеанс с загруженной в память VFS."""
        self._directory = tempfile.TemporaryDirectory()
        self.image = make_archive(
            Path(self._directory.name) / "deep.zip", ENTRIES
        )
        self.state = ShellState(vfs_name="deep", vfs=Vfs.load(self.image))

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()

    def _node_mode(self, path: str) -> str:
        """Возвращает строковое представление прав узла."""
        _, node = self.state.vfs.resolve((), path)
        return format_mode(node)

    def test_octal_mode_is_applied(self) -> None:
        """Восьмеричная запись задаёт права целиком."""
        execute_line(self.state, "chmod 600 /home/user/notes.txt")
        self.assertEqual(self._node_mode("/home/user/notes.txt"),
                         "-rw-------")

    def test_symbolic_mode_adds_permission(self) -> None:
        """Символьная запись добавляет право выполнения."""
        execute_line(self.state, "chmod u+x /home/user/notes.txt")
        self.assertEqual(self._node_mode("/home/user/notes.txt"),
                         "-rwxr--r--")

    def test_symbolic_mode_removes_permission(self) -> None:
        """Символьная запись снимает право записи."""
        execute_line(self.state, "chmod a-w /home/user/notes.txt")
        self.assertEqual(self._node_mode("/home/user/notes.txt"),
                         "-r--r--r--")

    def test_several_clauses_are_applied_in_order(self) -> None:
        """Правила, перечисленные через запятую, применяются подряд."""
        execute_line(self.state, "chmod u=rw,go= /etc/config.ini")
        self.assertEqual(self._node_mode("/etc/config.ini"), "-rw-------")

    def test_directory_mode_is_changed(self) -> None:
        """Права каталога изменяются так же, как права файла."""
        execute_line(self.state, "chmod 700 /home")
        self.assertEqual(self._node_mode("/home"), "drwx------")

    def test_several_paths_are_supported(self) -> None:
        """Один вызов изменяет права нескольких узлов."""
        execute_line(self.state, "chmod 640 /etc/config.ini /home")
        self.assertEqual(self._node_mode("/etc/config.ini"), "-rw-r-----")
        self.assertEqual(self._node_mode("/home"), "drw-r-----")

    def test_invalid_mode_is_rejected(self) -> None:
        """Нераспознанная запись режима порождает ошибку."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "chmod рwx /etc/config.ini")

    def test_too_large_octal_mode_is_rejected(self) -> None:
        """Восьмеричный режим больше 777 отвергается."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "chmod 7777 /etc/config.ini")

    def test_missing_arguments_are_rejected(self) -> None:
        """Без пути команда сообщает об ошибке."""
        with self.assertRaises(CommandArgumentError):
            execute_line(self.state, "chmod 755")

    def test_missing_path_is_reported(self) -> None:
        """Несуществующий путь порождает ошибку VFS."""
        with self.assertRaises(VfsPathError):
            execute_line(self.state, "chmod 755 /home/nobody")

    def test_changes_are_kept_in_memory_only(self) -> None:
        """Изменение прав не затрагивает исходный ZIP-архив."""
        before = self.image.read_bytes()
        execute_line(self.state, "chmod 000 /home/user/notes.txt")
        self.assertEqual(self.image.read_bytes(), before)
        reloaded = Vfs.load(self.image)
        _, node = reloaded.resolve((), "/home/user/notes.txt")
        self.assertEqual(format_mode(node), "-rw-r--r--")


if __name__ == "__main__":
    unittest.main()
