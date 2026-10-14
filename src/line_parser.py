"""Разбор командной строки эмулятора."""

import os
import re
import shlex

VARIABLE_PATTERN = re.compile(r"\$\{(\w+)\}|\$(\w+)")

class ParseError(Exception):
    """Ошибка синтаксиса командной строки (например, незакрытая кавычка)."""

def expand_variables(text, env=None):
    """Заменяет $NAME и ${NAME} значениями переменных окружения.

    Неизвестная переменная заменяется пустой строкой, как в bash.

    Args:
        text: строка, в которой нужно раскрыть переменные.
        env: словарь переменных; по умолчанию окружение реальной ОС.

    Returns:
        Строка с подставленными значениями переменных.
    """
    variables = os.environ if env is None else env

    def substitute(match):
        """Возвращает значение переменной для найденного совпадения."""
        name = match.group(1) or match.group(2)
        return variables.get(name, "")

    return VARIABLE_PATTERN.sub(substitute, text)

def parse(line, env=None):
    """Разбивает строку на имя команды и аргументы.

    Кавычки группируют слова в один аргумент, всё после # считается
    комментарием. Переменные окружения раскрываются после разбиения,
    поэтому пути Windows с обратными слэшами (например, значение
    $USERPROFILE) не искажаются. Слова, ставшие пустыми после раскрытия
    переменных, отбрасываются, как в bash.

    Args:
        line: введённая пользователем строка.
        env: словарь переменных; по умолчанию окружение реальной ОС.

    Returns:
        Кортеж (имя команды, список аргументов) или None для пустой строки.

    Raises:
        ParseError: если в строке есть незакрытая кавычка.
    """
    try:
        tokens = shlex.split(line, comments=True)
    except ValueError as error:
        raise ParseError(f"syntax error: {error}") from error
    expanded = [expand_variables(token, env) for token in tokens]
    words = [word for word in expanded if word]
    if not words:
        return None
    return words[0], words[1:]