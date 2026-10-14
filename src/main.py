"""Точка входа эмулятора оболочки."""

import sys

from commands import EXIT_FAILURE, ExitRequest
from config import format_config, parse_args
from repl import repl
from script_runner import run_script
from state import ShellState
from vfs import VfsError, load_vfs


def create_state(config):
    """Создаёт состояние эмулятора и загружает VFS, если она задана.

    Args:
        config: параметры командной строки.

    Returns:
        Состояние эмулятора; без --vfs VFS состоит из пустого корня.

    Raises:
        OSError: если CSV-файл VFS не удалось прочитать.
        VfsError: если данные VFS некорректны.
    """
    if not config.vfs:
        return ShellState()
    return ShellState(load_vfs(config.vfs), config.vfs)


def run(config, state):
    """Выполняет стартовый скрипт (если задан) и запускает REPL.

    Args:
        config: параметры командной строки.
        state: состояние эмулятора.

    Returns:
        Код возврата эмулятора.
    """
    try:
        if config.script:
            run_script(config.script, state)
        return repl(state)
    except ExitRequest as request:
        return request.code
    except OSError as error:
        print(f"shell-emulator: cannot read script: {error}", file=sys.stderr)
        return EXIT_FAILURE


def main(argv=None):
    """Запускает эмулятор и завершает процесс с его кодом возврата.

    Args:
        argv: параметры командной строки; по умолчанию из sys.argv.
    """
    config = parse_args(argv)
    for line in format_config(config):
        print(line)
    try:
        state = create_state(config)
    except (OSError, VfsError) as error:
        print(f"shell-emulator: cannot load VFS: {error}", file=sys.stderr)
        sys.exit(EXIT_FAILURE)
    sys.exit(run(config, state))


if __name__ == "__main__":
    main()