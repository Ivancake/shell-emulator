"""Точка входа эмулятора оболочки."""

import sys

from commands import EXIT_FAILURE, ExitRequest
from config import format_config, parse_args
from repl import repl
from script_runner import run_script


def start(config):
    """Выполняет стартовый скрипт (если задан) и запускает REPL.

    Args:
        config: параметры командной строки.

    Returns:
        Код возврата эмулятора.
    """
    if config.script:
        run_script(config.script)
    return repl()


def main(argv=None):
    """Запускает эмулятор и завершает процесс с его кодом возврата.

    Args:
        argv: параметры командной строки; по умолчанию из sys.argv.
    """
    config = parse_args(argv)
    for line in format_config(config):
        print(line)
    try:
        code = start(config)
    except ExitRequest as request:
        code = request.code
    except OSError as error:
        print(f"shell-emulator: cannot read script: {error}", file=sys.stderr)
        code = EXIT_FAILURE
    sys.exit(code)


if __name__ == "__main__":
    main()