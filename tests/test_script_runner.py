"""Тесты выполнения стартового скрипта."""

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from commands import ExitRequest  # noqa: E402
from repl import make_prompt  # noqa: E402
from script_runner import is_command_line, run_script  # noqa: E402

SCRIPT_EXIT_CODE = 7


class IsCommandLineTest(unittest.TestCase):
    """Проверка распознавания строк с командами."""

    def test_command(self):
        """Обычная строка — команда."""
        self.assertTrue(is_command_line("ls -l"))

    def test_comment_and_blank(self):
        """Комментарий и пустая строка — не команды."""
        self.assertFalse(is_command_line("  # comment"))
        self.assertFalse(is_command_line("   "))


class RunScriptTest(unittest.TestCase):
    """Проверка выполнения скрипта из файла."""

    def setUp(self):
        """Создаёт временный каталог для файлов скриптов."""
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Удаляет временный каталог."""
        self.tmp.cleanup()

    def write_script(self, text):
        """Записывает скрипт во временный файл и возвращает путь к нему."""
        path = Path(self.tmp.name) / "script.txt"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def test_shows_input_and_output(self):
        """Печатается приглашение с командой и результат, комментарий — нет."""
        path = self.write_script("# comment\nls a\n")
        output = io.StringIO()
        with redirect_stdout(output):
            run_script(path)
        self.assertEqual(output.getvalue(), f"{make_prompt()}ls a\nls a\n")

    def test_errors_do_not_stop_script(self):
        """Ошибка в команде не прерывает выполнение скрипта."""
        path = self.write_script("foo\nls b\n")
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            run_script(path)
        self.assertIn("foo: command not found", errors.getvalue())
        self.assertIn("ls b\n", output.getvalue())

    def test_exit_in_script(self):
        """exit в скрипте завершает эмулятор с указанным кодом."""
        path = self.write_script(f"exit {SCRIPT_EXIT_CODE}\nls\n")
        with redirect_stdout(io.StringIO()):
            with self.assertRaises(ExitRequest) as context:
                run_script(path)
        self.assertEqual(context.exception.code, SCRIPT_EXIT_CODE)

    def test_missing_file(self):
        """Несуществующий файл вызывает OSError."""
        with self.assertRaises(OSError):
            run_script(str(Path(self.tmp.name) / "missing.txt"))


if __name__ == "__main__":
    unittest.main()