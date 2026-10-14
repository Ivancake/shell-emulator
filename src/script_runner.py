"""Выполнение стартового скрипта эмулятора."""

from repl import make_prompt, run_line

COMMENT_PREFIX = "#"


def is_command_line(line):
    """Проверяет, содержит ли строка скрипта команду.

    Args:
        line: строка из файла скрипта.

    Returns:
        False для пустых строк и строк-комментариев, иначе True.
    """
    stripped = line.strip()
    return bool(stripped) and not stripped.startswith(COMMENT_PREFIX)


def run_script(path, state):
    """Выполняет команды из файла, имитируя диалог с пользователем.

    Перед каждой командой печатается приглашение и сама команда,
    затем результат её выполнения.

    Args:
        path: путь к файлу стартового скрипта.
        state: состояние эмулятора.

    Raises:
        OSError: если файл не удалось прочитать.
        ExitRequest: если в скрипте выполнена команда exit.
    """
    with open(path, encoding="utf-8") as file:
        lines = file.read().splitlines()
    for line in lines:
        if is_command_line(line):
            print(make_prompt() + line)
            run_line(line, state)