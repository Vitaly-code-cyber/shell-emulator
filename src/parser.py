"""Разбор строки пользовательского ввода.

Согласно варианту задания парсер простой: строка делится на команду и
аргументы по пробельным символам, без обработки кавычек.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    """Результат разбора строки ввода.

    Attributes:
        name: Имя команды (первое слово строки).
        args: Аргументы команды в порядке их следования.
    """

    name: str
    args: tuple[str, ...]


def parse_line(line: str) -> Command | None:
    """Разбирает строку ввода на команду и аргументы.

    Args:
        line: Строка, введённая пользователем или прочитанная из
            стартового скрипта.

    Returns:
        Разобранная команда либо ``None``, если строка пуста или
        содержит только пробельные символы.
    """
    tokens = line.split()
    if not tokens:
        return None
    return Command(name=tokens[0], args=tuple(tokens[1:]))
