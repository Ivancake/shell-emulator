"""Тесты команд эмулятора."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from commands import CommandError, ExitRequest, execute  # noqa: E402
from state import ShellState  # noqa: E402
from vfs import VfsDir, VfsFile  # noqa: E402

CUSTOM_EXIT_CODE = 3


class StubCommandsTest(unittest.TestCase):
    """Проверка команд-заглушек ls и cd."""

    def setUp(self):
        """Создаёт пустое состояние эмулятора."""
        self.state = ShellState()

    def test_ls_prints_args(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(
            execute("ls", ["-l", "/tmp"], self.state), "ls -l /tmp"
        )

    def test_cd_prints_args(self):
        """cd выводит своё имя и аргумент."""
        self.assertEqual(execute("cd", ["docs"], self.state), "cd docs")

    def test_cd_too_many_args(self):
        """cd с двумя аргументами — ошибка."""
        with self.assertRaises(CommandError):
            execute("cd", ["a", "b"], self.state)


class ExitCommandTest(unittest.TestCase):
    """Проверка команды exit."""

    def setUp(self):
        """Создаёт пустое состояние эмулятора."""
        self.state = ShellState()

    def test_exit_default_code(self):
        """exit без аргументов завершает с кодом 0."""
        with self.assertRaises(ExitRequest) as context:
            execute("exit", [], self.state)
        self.assertEqual(context.exception.code, 0)

    def test_exit_custom_code(self):
        """exit N завершает с кодом N."""
        with self.assertRaises(ExitRequest) as context:
            execute("exit", [str(CUSTOM_EXIT_CODE)], self.state)
        self.assertEqual(context.exception.code, CUSTOM_EXIT_CODE)

    def test_exit_not_a_number(self):
        """exit с нечисловым аргументом — ошибка."""
        with self.assertRaises(CommandError):
            execute("exit", ["abc"], self.state)


class VfsInfoCommandTest(unittest.TestCase):
    """Проверка служебной команды vfs-info."""

    def test_shows_source_and_tree(self):
        """Выводятся путь к CSV-файлу и дерево VFS."""
        root = VfsDir("")
        root.children["a.txt"] = VfsFile("a.txt", b"hi")
        state = ShellState(root, "fs.csv")
        self.assertEqual(
            execute("vfs-info", [], state),
            "VFS: fs.csv\n/\n`-- a.txt (2 bytes)",
        )

    def test_extra_args(self):
        """vfs-info с аргументами — ошибка."""
        with self.assertRaises(CommandError):
            execute("vfs-info", ["x"], ShellState())


class UnknownCommandTest(unittest.TestCase):
    """Проверка обработки неизвестной команды."""

    def test_unknown_command(self):
        """Неизвестная команда вызывает ошибку."""
        with self.assertRaisesRegex(CommandError, "command not found"):
            execute("foo", [], ShellState())


if __name__ == "__main__":
    unittest.main()