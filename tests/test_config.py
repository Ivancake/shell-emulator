"""Тесты разбора параметров командной строки."""

import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from config import NOT_SET, format_config, parse_args  # noqa: E402


class ParseArgsTest(unittest.TestCase):
    """Проверка разбора параметров."""

    def test_no_args(self):
        """Без параметров оба значения не заданы."""
        config = parse_args([])
        self.assertIsNone(config.vfs)
        self.assertIsNone(config.script)

    def test_all_args(self):
        """Оба параметра сохраняются."""
        config = parse_args(["--vfs", "fs.csv", "--script", "start.txt"])
        self.assertEqual(config.vfs, "fs.csv")
        self.assertEqual(config.script, "start.txt")

    def test_unknown_arg(self):
        """Неизвестный параметр завершает программу с ошибкой."""
        with redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parse_args(["--unknown"])


class FormatConfigTest(unittest.TestCase):
    """Проверка отладочного вывода параметров."""

    def test_format_all_params(self):
        """Выводятся все параметры, незаданные отмечаются особо."""
        lines = format_config(parse_args(["--vfs", "fs.csv"]))
        self.assertEqual(lines, [
            "[config] vfs = fs.csv",
            f"[config] script = {NOT_SET}",
        ])


if __name__ == "__main__":
    unittest.main()