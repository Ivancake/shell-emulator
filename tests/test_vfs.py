"""Тесты загрузки виртуальной файловой системы."""

import base64
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from vfs import (  # noqa: E402
    VfsDir, VfsError, VfsFile, format_tree, load_vfs, split_path,
)

HEADER = "path,type,data\n"
PROJECT_VFS = Path(__file__).resolve().parent.parent / "vfs"
BINARY_DATA = bytes([0x89, 0x50, 0x4E, 0x47, 0x00, 0xFF])


def encode(data):
    """Кодирует байты в base64-строку для CSV."""
    return base64.b64encode(data).decode()


class SplitPathTest(unittest.TestCase):
    """Проверка разбиения пути на имена."""

    def test_nested_path(self):
        """Путь делится по /."""
        self.assertEqual(split_path("/home/user/a.txt"),
                         ["home", "user", "a.txt"])

    def test_root(self):
        """Корень — пустой список имён."""
        self.assertEqual(split_path("/"), [])

    def test_relative_path(self):
        """Относительный путь — ошибка."""
        with self.assertRaises(VfsError):
            split_path("home/user")

    def test_dot_dot(self):
        """Путь с .. — ошибка."""
        with self.assertRaises(VfsError):
            split_path("/home/../etc")


class LoadVfsTest(unittest.TestCase):
    """Проверка загрузки VFS из CSV-файла."""

    def setUp(self):
        """Создаёт временный каталог для CSV-файлов."""
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        """Удаляет временный каталог."""
        self.tmp.cleanup()

    def load(self, rows):
        """Записывает строки CSV во временный файл и загружает VFS."""
        path = Path(self.tmp.name) / "vfs.csv"
        path.write_text(HEADER + rows, encoding="utf-8")
        return load_vfs(str(path))

    def test_nested_dirs_any_order(self):
        """Вложенные элементы загружаются независимо от порядка строк."""
        root = self.load(
            f"/a/b/c.txt,file,{encode(b'x')}\n/a/b,dir,\n/a,dir,\n"
        )
        node = root.children["a"].children["b"].children["c.txt"]
        self.assertEqual(node, VfsFile("c.txt", b"x"))

    def test_binary_data(self):
        """Двоичные данные декодируются из base64 без искажений."""
        root = self.load(f"/logo.bin,file,{encode(BINARY_DATA)}\n")
        self.assertEqual(root.children["logo.bin"].data, BINARY_DATA)

    def test_root_row_skipped(self):
        """Строка с корнем не создаёт лишних элементов."""
        self.assertEqual(self.load("/,dir,\n"), VfsDir(""))

    def test_bad_header(self):
        """Неверный заголовок — ошибка."""
        path = Path(self.tmp.name) / "vfs.csv"
        path.write_text("name,kind\n", encoding="utf-8")
        with self.assertRaisesRegex(VfsError, "header"):
            load_vfs(str(path))

    def test_bad_base64(self):
        """Некорректный base64 — ошибка с номером строки."""
        with self.assertRaisesRegex(VfsError, "line 2"):
            self.load("/a.txt,file,not*base64\n")

    def test_missing_parent(self):
        """Файл без родительского каталога — ошибка."""
        with self.assertRaisesRegex(VfsError, "parent"):
            self.load(f"/docs/a.txt,file,{encode(b'x')}\n")

    def test_unknown_type(self):
        """Неизвестный тип элемента — ошибка."""
        with self.assertRaisesRegex(VfsError, "unknown type"):
            self.load("/a,link,\n")

    def test_duplicate_path(self):
        """Повторяющийся путь — ошибка."""
        with self.assertRaisesRegex(VfsError, "duplicate"):
            self.load("/a,dir,\n/a,dir,\n")

    def test_dir_with_data(self):
        """Каталог с данными — ошибка."""
        with self.assertRaises(VfsError):
            self.load(f"/a,dir,{encode(b'x')}\n")

    def test_missing_file(self):
        """Несуществующий CSV-файл вызывает OSError."""
        with self.assertRaises(OSError):
            load_vfs(str(Path(self.tmp.name) / "missing.csv"))


class ProjectVfsTest(unittest.TestCase):
    """Проверка тестовых VFS из папки vfs проекта."""

    def test_deep_has_three_levels(self):
        """В deep.csv не меньше трёх уровней вложенности."""
        root = load_vfs(str(PROJECT_VFS / "deep.csv"))
        reports = root.children["home"].children["user"].children["docs"]
        self.assertIn("reports", reports.children)

    def test_minimal_is_empty(self):
        """minimal.csv содержит только корень."""
        root = load_vfs(str(PROJECT_VFS / "minimal.csv"))
        self.assertEqual(root.children, {})


class FormatTreeTest(unittest.TestCase):
    """Проверка вывода дерева VFS."""

    def test_tree(self):
        """Каталоги и файлы выводятся с отступами по уровням."""
        root = VfsDir("")
        docs = VfsDir("docs")
        docs.children["a.txt"] = VfsFile("a.txt", b"abc")
        root.children["docs"] = docs
        root.children["b.bin"] = VfsFile("b.bin")
        self.assertEqual(format_tree(root), [
            "|-- b.bin (0 bytes)",
            "`-- docs/",
            "    `-- a.txt (3 bytes)",
        ])


if __name__ == "__main__":
    unittest.main()