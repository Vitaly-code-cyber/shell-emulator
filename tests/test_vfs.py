"""Тесты загрузки и обхода виртуальной файловой системы."""

import base64
import tempfile
import unittest
import zipfile
from pathlib import Path

from src.errors import VfsLoadError, VfsPathError
from src.vfs import Vfs, format_path

PNG_BYTES = b"\x89PNG\r\n\x1a\n"
DEEP_ENTRIES = {
    "home/user/docs/report.txt": b"report",
    "home/user/docs/archive/old.txt": b"old",
    "etc/app/config.ini": b"[app]",
}


def make_archive(path: Path, entries: dict[str, bytes]) -> Path:
    """Создаёт ZIP-архив с заданным содержимым.

    Args:
        path: Путь к создаваемому архиву.
        entries: Содержимое архива по именам элементов.

    Returns:
        Путь к созданному архиву.
    """
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return path


class VfsLoadTest(unittest.TestCase):
    """Проверяет загрузку образа VFS из ZIP-архива."""

    def setUp(self) -> None:
        """Создаёт временный каталог для архивов."""
        self._directory = tempfile.TemporaryDirectory()
        self.root = Path(self._directory.name)

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()

    def test_minimal_image_contains_single_file(self) -> None:
        """Минимальный образ содержит ровно один файл."""
        path = make_archive(self.root / "minimal.zip",
                            {"readme.txt": b"hello"})
        vfs = Vfs.load(path)
        self.assertEqual(vfs.name, "minimal")
        self.assertEqual(vfs.count_nodes(), (0, 1))

    def test_deep_image_keeps_directory_structure(self) -> None:
        """Образ с вложенными каталогами сохраняет структуру."""
        path = make_archive(self.root / "deep.zip", DEEP_ENTRIES)
        vfs = Vfs.load(path)
        _, node = vfs.resolve((), "/home/user/docs/archive/old.txt")
        self.assertFalse(node.is_dir)
        self.assertEqual(node.data, b"old")

    def test_base64_entry_is_decoded(self) -> None:
        """Элемент с суффиксом .b64 декодируется при загрузке."""
        encoded = base64.b64encode(PNG_BYTES)
        path = make_archive(self.root / "bin.zip",
                            {"logo.png.b64": encoded})
        vfs = Vfs.load(path)
        _, node = vfs.resolve((), "/logo.png")
        self.assertEqual(node.data, PNG_BYTES)
        self.assertTrue(node.is_binary)

    def test_missing_image_is_reported(self) -> None:
        """Отсутствующий образ VFS порождает ошибку загрузки."""
        with self.assertRaises(VfsLoadError):
            Vfs.load(self.root / "no_such_image.zip")

    def test_broken_image_is_reported(self) -> None:
        """Файл неверного формата порождает ошибку загрузки."""
        path = self.root / "broken.zip"
        path.write_text("это не ZIP-архив", encoding="utf-8")
        with self.assertRaises(VfsLoadError):
            Vfs.load(path)

    def test_archive_is_not_modified(self) -> None:
        """Загрузка не изменяет исходный ZIP-архив."""
        path = make_archive(self.root / "deep.zip", DEEP_ENTRIES)
        before = path.read_bytes()
        Vfs.load(path)
        self.assertEqual(path.read_bytes(), before)


class VfsResolveTest(unittest.TestCase):
    """Проверяет разбор путей внутри VFS."""

    def setUp(self) -> None:
        """Загружает образ с вложенными каталогами."""
        self._directory = tempfile.TemporaryDirectory()
        path = make_archive(
            Path(self._directory.name) / "deep.zip", DEEP_ENTRIES
        )
        self.vfs = Vfs.load(path)

    def tearDown(self) -> None:
        """Удаляет временный каталог."""
        self._directory.cleanup()

    def test_relative_path_uses_current_directory(self) -> None:
        """Относительный путь отсчитывается от текущего каталога."""
        parts, node = self.vfs.resolve(("home", "user"), "docs")
        self.assertEqual(parts, ("home", "user", "docs"))
        self.assertTrue(node.is_dir)

    def test_parent_directory_is_supported(self) -> None:
        """Имя ``..`` поднимает путь на уровень выше."""
        parts, _ = self.vfs.resolve(("home", "user", "docs"), "../..")
        self.assertEqual(parts, ("home",))

    def test_parent_of_root_stays_at_root(self) -> None:
        """Подъём выше корня VFS оставляет путь в корне."""
        parts, _ = self.vfs.resolve((), "..")
        self.assertEqual(format_path(parts), "/")

    def test_missing_path_is_reported(self) -> None:
        """Несуществующий путь порождает ошибку."""
        with self.assertRaises(VfsPathError):
            self.vfs.resolve((), "/home/nobody")

    def test_path_through_file_is_reported(self) -> None:
        """Путь, проходящий через файл, порождает ошибку."""
        with self.assertRaises(VfsPathError):
            self.vfs.resolve((), "/etc/app/config.ini/inner")


if __name__ == "__main__":
    unittest.main()
