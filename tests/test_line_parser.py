"""Тесты разбора командной строки."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from line_parser import ParseError, expand_variables, parse  # noqa: E402

ENV = {"HOME": "/home/ivan", "WIN": "C:\\Users\\ivan"}

class ExpandVariablesTest(unittest.TestCase):
    """Проверка раскрытия переменных окружения."""

    def test_simple_variable(self):
        """$NAME заменяется значением."""
        self.assertEqual(expand_variables("$HOME/docs", ENV), "/home/ivan/docs")

    def test_braced_variable(self):
        """${NAME} заменяется значением."""
        self.assertEqual(expand_variables("${HOME}x", ENV), "/home/ivanx")

    def test_unknown_variable(self):
        """Неизвестная переменная заменяется пустой строкой."""
        self.assertEqual(expand_variables("a$NOPE", ENV), "a")

class ParseTest(unittest.TestCase):
    """Проверка разбиения строки на команду и аргументы."""

    def test_command_with_args(self):
        """Команда и аргументы разделяются пробелами."""
        self.assertEqual(parse("ls -l /tmp", ENV), ("ls", ["-l", "/tmp"]))

    def test_quotes_group_words(self):
        """Слова в кавычках образуют один аргумент."""
        self.assertEqual(parse('cd "my dir"', ENV), ("cd", ["my dir"]))

    def test_variable_in_args(self):
        """Переменная раскрывается в аргументе."""
        self.assertEqual(parse("cd $HOME", ENV), ("cd", ["/home/ivan"]))

    def test_windows_path_preserved(self):
        """Обратные слэши в значении переменной не теряются."""
        self.assertEqual(parse("cd $WIN", ENV), ("cd", ["C:\\Users\\ivan"]))

    def test_empty_line(self):
        """Пустая строка не является командой."""
        self.assertIsNone(parse("   ", ENV))

    def test_comment_ignored(self):
        """Всё после # отбрасывается как комментарий."""
        self.assertEqual(parse("ls -a  # hidden", ENV), ("ls", ["-a"]))

    def test_comment_only_line(self):
        """Строка из одного комментария не является командой."""
        self.assertIsNone(parse("# comment", ENV))

    def test_unclosed_quote(self):
        """Незакрытая кавычка вызывает ошибку разбора."""
        with self.assertRaises(ParseError):
            parse('ls "abc', ENV)

    def test_empty_variable_dropped(self):
        """Слово, ставшее пустым после раскрытия, отбрасывается."""
        self.assertEqual(parse("ls $NOPE /tmp", ENV), ("ls", ["/tmp"]))

    def test_only_empty_variable(self):
        """Строка из одной пустой переменной не является командой."""
        self.assertIsNone(parse("$NOPE", ENV))

if __name__ == "__main__":
    unittest.main()