"""Виртуальная файловая система, размещаемая в оперативной памяти.

Источником VFS является ZIP-архив. Архив открывается только на
чтение: его содержимое целиком переносится в дерево узлов в памяти, а
сам файл никогда не распаковывается и не изменяется. Двоичные данные
хранятся в архиве в кодировке base64 — такие элементы имеют суффикс
``.b64``, который снимается при загрузке.
"""

import base64
import binascii
import zipfile
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

from src.errors import VfsLoadError, VfsPathError

BASE64_SUFFIX = ".b64"
DEFAULT_DIR_MODE = 0o755
DEFAULT_FILE_MODE = 0o644
PATH_SEPARATOR = "/"
CURRENT_DIR = "."
PARENT_DIR = ".."


@dataclass
class VfsNode:
    """Узел дерева виртуальной файловой системы.

    Attributes:
        name: Имя файла или каталога без пути.
        is_dir: Признак каталога.
        mode: Права доступа в виде числа, как в команде ``chmod``.
        data: Содержимое файла; для каталога всегда пустое.
        children: Дочерние узлы каталога по их именам.
    """

    name: str
    is_dir: bool
    mode: int
    data: bytes = b""
    children: dict[str, "VfsNode"] = field(default_factory=dict)

    @property
    def size(self) -> int:
        """Возвращает размер содержимого файла в байтах."""
        return len(self.data)

    @property
    def is_binary(self) -> bool:
        """Сообщает, содержит ли файл двоичные данные."""
        try:
            self.data.decode("utf-8")
        except UnicodeDecodeError:
            return True
        return False


def format_path(parts: tuple[str, ...]) -> str:
    """Собирает абсолютный путь VFS из его составляющих.

    Args:
        parts: Имена каталогов от корня VFS.

    Returns:
        Путь вида ``/home/user`` либо ``/`` для корня.
    """
    return PATH_SEPARATOR + PATH_SEPARATOR.join(parts)


def decode_entry(name: str, raw: bytes) -> tuple[str, bytes]:
    """Декодирует содержимое элемента архива.

    Переводы строк внутри данных base64 допускаются: они снимаются
    перед декодированием, что позволяет хранить длинные данные
    короткими строками.

    Args:
        name: Имя элемента архива без пути.
        raw: Байты, прочитанные из архива.

    Returns:
        Пару «имя узла VFS, его содержимое».

    Raises:
        VfsLoadError: Элемент объявлен как base64, но повреждён.
    """
    if not name.endswith(BASE64_SUFFIX):
        return name, raw
    try:
        data = base64.b64decode(b"".join(raw.split()), validate=True)
    except (binascii.Error, ValueError) as error:
        raise VfsLoadError(
            f"{name}: неверный формат данных base64"
        ) from error
    return name[: -len(BASE64_SUFFIX)], data


def ensure_directory(root: VfsNode, parts: tuple[str, ...]) -> VfsNode:
    """Создаёт при необходимости цепочку каталогов и возвращает последний.

    Args:
        root: Корневой узел дерева VFS.
        parts: Имена каталогов от корня.

    Returns:
        Узел каталога, соответствующий переданному пути.
    """
    node = root
    for part in parts:
        child = node.children.get(part)
        if child is None:
            child = VfsNode(name=part, is_dir=True, mode=DEFAULT_DIR_MODE)
            node.children[part] = child
        node = child
    return node


class Vfs:
    """Дерево виртуальной файловой системы в оперативной памяти."""

    def __init__(self, name: str, root: VfsNode) -> None:
        """Сохраняет имя образа и корневой узел дерева.

        Args:
            name: Имя образа VFS без расширения.
            root: Корневой каталог дерева.
        """
        self.name = name
        self.root = root

    @classmethod
    def load(cls, path: Path) -> "Vfs":
        """Загружает VFS из ZIP-архива целиком в память.

        Args:
            path: Путь к ZIP-архиву с образом VFS.

        Returns:
            Загруженная виртуальная файловая система.

        Raises:
            VfsLoadError: Архив не найден, недоступен или повреждён.
        """
        try:
            with zipfile.ZipFile(path) as archive:
                return cls._from_archive(path.stem, archive)
        except FileNotFoundError as error:
            raise VfsLoadError(f"образ VFS {path} не найден") from error
        except zipfile.BadZipFile as error:
            raise VfsLoadError(
                f"образ VFS {path}: неверный формат, ожидается ZIP-архив"
            ) from error
        except OSError as error:
            raise VfsLoadError(
                f"образ VFS {path} недоступен: {error.strerror}"
            ) from error

    @classmethod
    def _from_archive(cls, name: str, archive: zipfile.ZipFile) -> "Vfs":
        """Строит дерево VFS по содержимому открытого архива.

        Args:
            name: Имя образа VFS без расширения.
            archive: Открытый на чтение ZIP-архив.

        Returns:
            Загруженная виртуальная файловая система.
        """
        root = VfsNode(name="", is_dir=True, mode=DEFAULT_DIR_MODE)
        for info in archive.infolist():
            parts = PurePosixPath(info.filename).parts
            if not parts:
                continue
            if info.is_dir():
                ensure_directory(root, parts)
                continue
            entry, data = decode_entry(parts[-1], archive.read(info))
            parent = ensure_directory(root, parts[:-1])
            parent.children[entry] = VfsNode(
                name=entry, is_dir=False,
                mode=DEFAULT_FILE_MODE, data=data,
            )
        return cls(name, root)

    def resolve(self, cwd: tuple[str, ...],
                path: str) -> tuple[tuple[str, ...], VfsNode]:
        """Находит узел VFS по пути, заданному пользователем.

        Поддерживаются абсолютные и относительные пути, а также
        специальные имена ``.`` и ``..``.

        Args:
            cwd: Текущий каталог в виде имён от корня VFS.
            path: Путь, введённый пользователем.

        Returns:
            Пару «нормализованный путь, найденный узел».

        Raises:
            VfsPathError: Путь не существует или ведёт через файл.
        """
        parts: list[str] = []
        if not path.startswith(PATH_SEPARATOR):
            parts = list(cwd)
        for token in path.split(PATH_SEPARATOR):
            if token in ("", CURRENT_DIR):
                continue
            if token == PARENT_DIR:
                if parts:
                    parts.pop()
                continue
            parts.append(token)
        return tuple(parts), self._node_at(tuple(parts), path)

    def _node_at(self, parts: tuple[str, ...], original: str) -> VfsNode:
        """Спускается по дереву VFS к узлу с заданным путём.

        Args:
            parts: Нормализованный путь от корня VFS.
            original: Исходный путь для сообщений об ошибках.

        Returns:
            Найденный узел дерева.

        Raises:
            VfsPathError: Узел отсутствует или путь ведёт через файл.
        """
        node = self.root
        for part in parts:
            if not node.is_dir:
                raise VfsPathError(
                    f"{original}: {node.name} не является каталогом"
                )
            child = node.children.get(part)
            if child is None:
                raise VfsPathError(
                    f"{original}: нет такого файла или каталога"
                )
            node = child
        return node

    def count_nodes(self) -> tuple[int, int]:
        """Подсчитывает число каталогов и файлов в дереве.

        Returns:
            Пару «число каталогов, число файлов», не считая корень.
        """
        directories = 0
        files = 0
        pending = list(self.root.children.values())
        while pending:
            node = pending.pop()
            if node.is_dir:
                directories += 1
                pending.extend(node.children.values())
            else:
                files += 1
        return directories, files

    def describe(self) -> str:
        """Формирует краткое описание загруженной VFS.

        Returns:
            Строка для отладочного вывода при запуске эмулятора.
        """
        directories, files = self.count_nodes()
        return (f"VFS «{self.name}» загружена в память: "
                f"каталогов {directories}, файлов {files}")
