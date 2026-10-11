"""Цикл чтения и выполнения команд (REPL)."""

import getpass
import socket
import sys

from commands import EXIT_SUCCESS, CommandError, ExitRequest, execute
from line_parser import ParseError, parse

HOME_SYMBOL = "~"

def make_prompt(cwd=HOME_SYMBOL):
    """Формирует приглашение по данным реальной ОС.

    Args:
        cwd: текущий каталог, который показывается в приглашении.

    Returns:
        Строка вида "user@host:~$ ".
    """
    return f"{getpass.getuser()}@{socket.gethostname()}:{cwd}$ "

def run_line(line):
    """Разбирает и выполняет одну строку команды.

    Результат печатается в stdout, ошибки — в stderr.

    Args:
        line: строка, введённая пользователем.

    Raises:
        ExitRequest: если выполнена команда exit.
    """
    try:
        parsed = parse(line)
        if parsed is None:
            return
        name, args = parsed
        output = execute(name, args)
    except (ParseError, CommandError) as error:
        print(error, file=sys.stderr)
        return
    if output:
        print(output)

def repl():
    """Запускает интерактивный режим эмулятора.

    Returns:
        Код возврата эмулятора.
    """
    while True:
        try:
            line = input(make_prompt())
        except EOFError:
            print()
            return EXIT_SUCCESS
        except KeyboardInterrupt:
            print()
            continue
        try:
            run_line(line)
        except ExitRequest as request:
            return request.code