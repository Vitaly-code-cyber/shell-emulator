"""Проверка кода на типичные нарушения оформления репозитория.

Инструмент проверяет требования, предъявляемые к коду на языке
Python: длину строк и файлов, длину функций, число аргументов,
наличие документации вместо комментариев, цикломатическую сложность
и соответствие имён стандарту PEP8.

Запуск: ``python3 tools/check_style.py [путь ...]``. Без аргументов
проверяются каталоги ``src``, ``tests`` и ``tools``.
"""

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

MAX_LINE_LENGTH = 80
MAX_FILE_LINES = 1000
MAX_FUNCTION_LINES = 40
MAX_ARGUMENTS = 7
MAX_COMPLEXITY = 10
DEFAULT_TARGETS = ("src", "tests", "tools")
SNAKE_CASE = re.compile(r"^_{0,2}[a-z][a-z0-9_]*_{0,2}$")
CAPITALIZED_WORDS = re.compile(r"^[A-Z][A-Za-z0-9]*$")
FRAMEWORK_METHODS = frozenset({
    "setUp", "tearDown", "setUpClass", "tearDownClass",
})
BRANCH_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While,
                ast.ExceptHandler, ast.IfExp, ast.Assert)
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
EXIT_SUCCESS = 0
EXIT_FAILURE = 1


@dataclass(frozen=True)
class Issue:
    """Одно найденное нарушение оформления.

    Attributes:
        path: Файл, в котором найдено нарушение.
        line: Номер строки.
        rule: Обозначение правила из перечня нарушений.
        message: Описание нарушения.
    """

    path: Path
    line: int
    rule: str
    message: str

    def render(self) -> str:
        """Формирует строку отчёта о нарушении."""
        return f"{self.path}:{self.line}: [{self.rule}] {self.message}"


def iter_python_files(targets: tuple[str, ...]) -> list[Path]:
    """Собирает список проверяемых файлов с кодом.

    Args:
        targets: Пути к файлам или каталогам.

    Returns:
        Отсортированный список файлов с расширением ``.py``.
    """
    files: list[Path] = []
    for target in targets:
        path = Path(target)
        if path.is_dir():
            files.extend(sorted(path.rglob("*.py")))
        elif path.suffix == ".py":
            files.append(path)
    return files


def check_lines(path: Path, lines: list[str]) -> list[Issue]:
    """Проверяет длину файла и его строк.

    Args:
        path: Проверяемый файл.
        lines: Строки файла без символов перевода строки.

    Returns:
        Список найденных нарушений.
    """
    issues: list[Issue] = []
    if len(lines) > MAX_FILE_LINES:
        issues.append(Issue(path, 1, "Р1",
                            f"файл длиннее {MAX_FILE_LINES} строк"))
    for number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            issues.append(Issue(
                path, number, "Р2",
                f"строка длиннее {MAX_LINE_LENGTH} символов",
            ))
    return issues


def complexity_of(node: ast.AST) -> int:
    """Вычисляет цикломатическую сложность функции.

    Args:
        node: Узел определения функции.

    Returns:
        Число независимых путей исполнения.
    """
    total = 1
    for child in ast.walk(node):
        if isinstance(child, BRANCH_NODES):
            total += 1
        elif isinstance(child, ast.BoolOp):
            total += len(child.values) - 1
        elif isinstance(child, ast.comprehension):
            total += 1 + len(child.ifs)
    return total


def count_arguments(node: ast.AST) -> int:
    """Подсчитывает число аргументов функции.

    Args:
        node: Узел определения функции.

    Returns:
        Общее число аргументов, включая ``*args`` и ``**kwargs``.
    """
    arguments = node.args
    total = len(arguments.posonlyargs) + len(arguments.args)
    total += len(arguments.kwonlyargs)
    total += sum(1 for extra in (arguments.vararg, arguments.kwarg)
                 if extra is not None)
    return total


def check_function_names(path: Path, node: ast.AST) -> list[Issue]:
    """Проверяет имена функции и её аргументов на стандарт PEP8.

    Имена методов, предписанных библиотекой ``unittest``, из проверки
    исключены: стандарт PEP8 допускает следование соглашениям
    используемой библиотеки.

    Args:
        path: Проверяемый файл.
        node: Узел определения функции.

    Returns:
        Список найденных нарушений.
    """
    issues: list[Issue] = []
    if (node.name not in FRAMEWORK_METHODS
            and not SNAKE_CASE.match(node.name)):
        issues.append(Issue(path, node.lineno, "И1",
                            f"имя {node.name} не в стиле snake_case"))
    arguments = node.args
    names = arguments.posonlyargs + arguments.args + arguments.kwonlyargs
    for argument in names:
        if not SNAKE_CASE.match(argument.arg):
            issues.append(Issue(
                path, node.lineno, "И1",
                f"аргумент {argument.arg} не в стиле snake_case",
            ))
    return issues


def check_function(path: Path, node: ast.AST) -> list[Issue]:
    """Проверяет одно определение функции.

    Args:
        path: Проверяемый файл.
        node: Узел определения функции.

    Returns:
        Список найденных нарушений.
    """
    issues: list[Issue] = []
    length = node.end_lineno - node.lineno + 1
    if length > MAX_FUNCTION_LINES:
        issues.append(Issue(path, node.lineno, "Ф1",
                            f"функция {node.name} длиннее "
                            f"{MAX_FUNCTION_LINES} строк"))
    if count_arguments(node) > MAX_ARGUMENTS:
        issues.append(Issue(path, node.lineno, "А1",
                            f"у функции {node.name} больше "
                            f"{MAX_ARGUMENTS} аргументов"))
    if ast.get_docstring(node) is None:
        issues.append(Issue(path, node.lineno, "К1",
                            f"функция {node.name} без docstring"))
    if complexity_of(node) > MAX_COMPLEXITY:
        issues.append(Issue(path, node.lineno, "Ц1",
                            f"сложность функции {node.name} выше "
                            f"{MAX_COMPLEXITY}"))
    return issues + check_function_names(path, node)


def check_class(path: Path, node: ast.ClassDef) -> list[Issue]:
    """Проверяет определение класса.

    Args:
        path: Проверяемый файл.
        node: Узел определения класса.

    Returns:
        Список найденных нарушений.
    """
    issues: list[Issue] = []
    if ast.get_docstring(node) is None:
        issues.append(Issue(path, node.lineno, "К1",
                            f"класс {node.name} без docstring"))
    if not CAPITALIZED_WORDS.match(node.name):
        issues.append(Issue(path, node.lineno, "И1",
                            f"имя класса {node.name} не в стиле "
                            "CapitalizedWords"))
    return issues


def check_file(path: Path) -> list[Issue]:
    """Проверяет один файл с кодом на языке Python.

    Args:
        path: Проверяемый файл.

    Returns:
        Список найденных нарушений.
    """
    text = path.read_text(encoding="utf-8")
    issues = check_lines(path, text.splitlines())
    tree = ast.parse(text, filename=str(path))
    if ast.get_docstring(tree) is None:
        issues.append(Issue(path, 1, "К1", "модуль без docstring"))
    for node in ast.walk(tree):
        if isinstance(node, FUNCTION_NODES):
            issues.extend(check_function(path, node))
        elif isinstance(node, ast.ClassDef):
            issues.extend(check_class(path, node))
    return issues


def main(argv: list[str] | None = None) -> int:
    """Проверяет переданные пути и печатает найденные нарушения.

    Args:
        argv: Пути к файлам или каталогам; по умолчанию проверяются
            каталоги с исходным кодом, тестами и инструментами.

    Returns:
        Код возврата процесса: 1 при наличии нарушений.
    """
    targets = tuple(argv) if argv else DEFAULT_TARGETS
    issues: list[Issue] = []
    for path in iter_python_files(targets):
        issues.extend(check_file(path))
    for issue in sorted(issues, key=lambda item: (item.path, item.line)):
        print(issue.render())
    if issues:
        print(f"найдено нарушений: {len(issues)}", file=sys.stderr)
        return EXIT_FAILURE
    print("нарушений оформления не найдено")
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
