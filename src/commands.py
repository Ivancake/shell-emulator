"""Команды эмулятора оболочки.

Каждая команда принимает список аргументов и состояние эмулятора
и возвращает текст для вывода на экран.
"""

from vfs import format_tree

EXIT_SUCCESS = 0
EXIT_FAILURE = 1
MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


class CommandError(Exception):
    """Ошибка выполнения команды: неизвестная команда или неверные аргументы."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора.

    Attributes:
        code: код возврата, с которым завершается эмулятор.
    """

    def __init__(self, code):
        """Сохраняет код возврата.

        Args:
            code: код возврата эмулятора.
        """
        super().__init__(code)
        self.code = code


def ls_command(args, state):
    """Заглушка ls: возвращает имя команды и аргументы.

    Args:
        args: список аргументов команды.
        state: состояние эмулятора (не используется).

    Returns:
        Строка вида "ls arg1 arg2".
    """
    return " ".join(["ls", *args])


def cd_command(args, state):
    """Заглушка cd: возвращает имя команды и аргументы.

    Args:
        args: список аргументов команды (не более одного).
        state: состояние эмулятора (не используется).

    Returns:
        Строка вида "cd arg".

    Raises:
        CommandError: если передано больше одного аргумента.
    """
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: too many arguments")
    return " ".join(["cd", *args])


def exit_command(args, state):
    """Завершает работу эмулятора.

    Args:
        args: необязательный код возврата (целое число).
        state: состояние эмулятора (не используется).

    Raises:
        CommandError: если аргументов больше одного или код не число.
        ExitRequest: всегда при корректных аргументах.
    """
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("exit: too many arguments")
    code = EXIT_SUCCESS
    if args:
        try:
            code = int(args[0])
        except ValueError as error:
            raise CommandError(
                f"exit: {args[0]}: numeric argument required"
            ) from error
    raise ExitRequest(code)


def vfs_info_command(args, state):
    """Служебная команда: источник и дерево загруженной VFS.

    Args:
        args: список аргументов (должен быть пустым).
        state: состояние эмулятора с загруженной VFS.

    Returns:
        Путь к CSV-файлу VFS и дерево её содержимого.

    Raises:
        CommandError: если переданы аргументы.
    """
    if args:
        raise CommandError("vfs-info: too many arguments")
    lines = [f"VFS: {state.vfs_source}", "/"]
    lines.extend(format_tree(state.vfs_root))
    return "\n".join(lines)


COMMANDS = {
    "ls": ls_command,
    "cd": cd_command,
    "exit": exit_command,
    "vfs-info": vfs_info_command,
}


def execute(name, args, state):
    """Выполняет команду по имени.

    Args:
        name: имя команды.
        args: список аргументов.
        state: состояние эмулятора.

    Returns:
        Текст, который нужно вывести на экран.

    Raises:
        CommandError: если команда неизвестна или аргументы неверны.
        ExitRequest: если выполнена команда exit.
    """
    if name not in COMMANDS:
        raise CommandError(f"{name}: command not found")
    return COMMANDS[name](args, state)