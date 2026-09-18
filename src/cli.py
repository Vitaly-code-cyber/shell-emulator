"""Разбор параметров командной строки эмулятора."""

import argparse
from dataclasses import dataclass
from pathlib import Path

DESCRIPTION = "Эмулятор командной оболочки UNIX-подобной ОС"


@dataclass(frozen=True)
class Options:
    """Параметры запуска эмулятора.

    Attributes:
        vfs_path: Путь к физическому расположению VFS (ZIP-архив).
        log_path: Путь к лог-файлу в формате XML.
        script_path: Путь к стартовому скрипту эмулятора.
    """

    vfs_path: Path | None = None
    log_path: Path | None = None
    script_path: Path | None = None


def build_parser() -> argparse.ArgumentParser:
    """Создаёт разборщик параметров командной строки.

    Returns:
        Настроенный экземпляр :class:`argparse.ArgumentParser`.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "--vfs", dest="vfs_path", type=Path, default=None,
        help="путь к физическому расположению VFS (ZIP-архив)",
    )
    parser.add_argument(
        "--log", dest="log_path", type=Path, default=None,
        help="путь к лог-файлу в формате XML",
    )
    parser.add_argument(
        "--script", dest="script_path", type=Path, default=None,
        help="путь к стартовому скрипту эмулятора",
    )
    return parser


def parse_options(argv: list[str] | None = None) -> Options:
    """Разбирает параметры командной строки.

    Args:
        argv: Список аргументов; по умолчанию берётся из ``sys.argv``.

    Returns:
        Параметры запуска эмулятора.
    """
    namespace = build_parser().parse_args(argv)
    return Options(
        vfs_path=namespace.vfs_path,
        log_path=namespace.log_path,
        script_path=namespace.script_path,
    )


def format_options(options: Options) -> str:
    """Формирует отладочный вывод всех заданных параметров.

    Args:
        options: Разобранные параметры запуска.

    Returns:
        Многострочный текст для печати при старте эмулятора.
    """
    rows = (
        ("Путь к VFS", options.vfs_path),
        ("Путь к лог-файлу", options.log_path),
        ("Путь к стартовому скрипту", options.script_path),
    )
    lines = ["=== Параметры запуска эмулятора ==="]
    for title, value in rows:
        lines.append(f"{title}: {value if value else 'не задан'}")
    lines.append("=" * len(lines[0]))
    return "\n".join(lines)
