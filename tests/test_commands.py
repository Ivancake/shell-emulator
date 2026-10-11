"""Тесты команд эмулятора."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from commands import CommandError, ExitRequest, execute  # noqa: E402

CUSTOM_EXIT_CODE = 3

class StubCommandsTest(unittest.TestCase):
    """Проверка команд-заглушек ls и cd."""

    def test_ls_prints_args(self):
        """ls выводит своё имя и аргументы."""
        self.assertEqual(execute("ls", ["-l", "/tmp"]), "ls -l /tmp")

    def test_cd_prints_args(self):
        """cd выводит своё имя и аргумент."""
        self.assertEqual(execute("cd", ["docs"]), "cd docs")

    def test_cd_too_many_args(self):
        """cd с двумя аргументами — ошибка."""
        with self.assertRaises(CommandError):
            execute("cd", ["a", "b"])

class ExitCommandTest(unittest.TestCase):
    """Проверка команды exit."""

    def test_exit_default_code(self):
        """exit без аргументов завершает с кодом 0."""
        with self.assertRaises(ExitRequest) as context:
            execute("exit", [])
        self.assertEqual(context.exception.code, 0)

    def test_exit_custom_code(self):
        """exit N завершает с кодом N."""
        with self.assertRaises(ExitRequest) as context:
            execute("exit", [str(CUSTOM_EXIT_CODE)])
        self.assertEqual(context.exception.code, CUSTOM_EXIT_CODE)

    def test_exit_not_a_number(self):
        """exit с нечисловым аргументом — ошибка."""
        with self.assertRaises(CommandError):
            execute("exit", ["abc"])

class UnknownCommandTest(unittest.TestCase):
    """Проверка обработки неизвестной команды."""

    def test_unknown_command(self):
        """Неизвестная команда вызывает ошибку."""
        with self.assertRaisesRegex(CommandError, "command not found"):
            execute("foo", [])

if __name__ == "__main__":
    unittest.main()