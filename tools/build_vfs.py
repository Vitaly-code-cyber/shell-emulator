"""Сборка ZIP-образов VFS из каталогов с исходными файлами.

Архивы являются артефактами сборки и не хранятся в репозитории,
поэтому перед запуском эмулятора образ нужно собрать.

Запуск: ``python3 tools/build_vfs.py [имя ...]``. Без аргументов
собираются все образы из каталога ``vfs``.
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "vfs"
BUILD_DIR = ROOT / "build"
IGNORED_NAMES = frozenset({".DS_Store", "README.md"})
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


def available_images() -> list[str]:
    """Возвращает имена всех исходных образов VFS.

    Returns:
        Отсортированный список имён каталогов внутри ``vfs``.
    """
    return sorted(item.name for item in SOURCE_DIR.iterdir()
                  if item.is_dir())


def build_image(name: str) -> Path:
    """Собирает один ZIP-образ VFS.

    Args:
        name: Имя каталога с исходными файлами образа.

    Returns:
        Путь к созданному ZIP-архиву.

    Raises:
        FileNotFoundError: Каталог с исходными файлами отсутствует.
    """
    source = SOURCE_DIR / name
    if not source.is_dir():
        raise FileNotFoundError(f"нет исходного образа VFS: {source}")
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    target = BUILD_DIR / f"{name}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.name in IGNORED_NAMES:
                continue
            archive.write(path, path.relative_to(source).as_posix())
    return target


def main(argv: list[str] | None = None) -> int:
    """Собирает перечисленные образы VFS или все сразу.

    Args:
        argv: Имена образов; по умолчанию собираются все.

    Returns:
        Код возврата процесса.
    """
    names = argv if argv else available_images()
    for name in names:
        try:
            target = build_image(name)
        except FileNotFoundError as error:
            print(f"ошибка: {error}", file=sys.stderr)
            return EXIT_FAILURE
        print(f"собран образ VFS: {target.relative_to(ROOT)}")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
