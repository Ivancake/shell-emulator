"""Параметры командной строки эмулятора."""

import argparse

NOT_SET = "(not set)"


def parse_args(argv=None):
    """Разбирает параметры командной строки.

    Args:
        argv: список параметров; по умолчанию берётся из sys.argv.

    Returns:
        Объект с атрибутами vfs и script (None, если параметр не задан).
    """
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="Эмулятор командной оболочки UNIX-подобной ОС.",
    )
    parser.add_argument(
        "--vfs", help="путь к физическому расположению VFS (CSV-файл)"
    )
    parser.add_argument("--script", help="путь к стартовому скрипту")
    return parser.parse_args(argv)


def format_config(config):
    """Формирует строки отладочного вывода всех параметров.

    Args:
        config: результат parse_args.

    Returns:
        Список строк вида "[config] имя = значение".
    """
    return [
        f"[config] {name} = {NOT_SET if value is None else value}"
        for name, value in vars(config).items()
    ]