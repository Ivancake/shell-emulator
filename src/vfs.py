"""Виртуальная файловая система (VFS), загружаемая из CSV-файла.

Формат CSV: заголовок path,type,data и по строке на каждый элемент.
path — абсолютный путь элемента, type — dir или file, data — содержимое
файла в base64 (у каталогов пусто). Вложенность задаётся путём.
"""

import base64
import binascii
import csv
from dataclasses import dataclass, field

DIR_TYPE = "dir"
FILE_TYPE = "file"
CSV_FIELDS = ["path", "type", "data"]
SEPARATOR = "/"
FIRST_DATA_LINE = 2
SPECIAL_NAMES = (".", "..")
TREE_BRANCH = "|-- "
TREE_LAST = "`-- "
TREE_PIPE = "|   "
TREE_SPACE = "    "


class VfsError(Exception):
    """Ошибка загрузки VFS или некорректная структура CSV-файла."""


@dataclass
class VfsFile:
    """Файл VFS.

    Attributes:
        name: имя файла.
        data: содержимое файла в байтах.
    """

    name: str
    data: bytes = b""


@dataclass
class VfsDir:
    """Каталог VFS.

    Attributes:
        name: имя каталога (у корня — пустая строка).
        children: вложенные элементы, ключ — имя элемента.
    """

    name: str
    children: dict = field(default_factory=dict)


def split_path(path):
    """Делит абсолютный путь на имена элементов.

    Args:
        path: путь вида "/home/user/file.txt".

    Returns:
        Список имён, например ["home", "user", "file.txt"]; для "/" — [].

    Raises:
        VfsError: если путь не абсолютный или содержит "." и "..".
    """
    if not path.startswith(SEPARATOR):
        raise VfsError(f"path must be absolute: '{path}'")
    parts = [part for part in path.split(SEPARATOR) if part]
    if any(part in SPECIAL_NAMES for part in parts):
        raise VfsError(f"path must not contain '.' or '..': '{path}'")
    return parts


def decode_data(text):
    """Декодирует содержимое файла из base64.

    Args:
        text: строка в base64.

    Returns:
        Содержимое файла в байтах.

    Raises:
        VfsError: если строка не является корректным base64.
    """
    try:
        return base64.b64decode(text, validate=True)
    except binascii.Error as error:
        raise VfsError(f"invalid base64 data: {error}") from error


def make_node(name, kind, data):
    """Создаёт элемент VFS по типу из CSV.

    Args:
        name: имя элемента.
        kind: тип элемента: "dir" или "file".
        data: содержимое файла в base64.

    Returns:
        VfsDir или VfsFile.

    Raises:
        VfsError: если тип неизвестен или у каталога указаны данные.
    """
    if kind == DIR_TYPE:
        if data:
            raise VfsError(f"directory '{name}' must not have data")
        return VfsDir(name)
    if kind == FILE_TYPE:
        return VfsFile(name, decode_data(data))
    raise VfsError(f"unknown type '{kind}' (expected dir or file)")


def add_node(root, parts, node):
    """Помещает элемент в дерево VFS.

    Args:
        root: корневой каталог.
        parts: путь элемента, разбитый на имена.
        node: добавляемый элемент.

    Raises:
        VfsError: если нет родительского каталога или путь уже занят.
    """
    parent = root
    for name in parts[:-1]:
        parent = parent.children.get(name)
        if not isinstance(parent, VfsDir):
            parent_path = SEPARATOR + SEPARATOR.join(parts[:-1])
            raise VfsError(f"parent directory not found: '{parent_path}'")
    if node.name in parent.children:
        raise VfsError(f"duplicate path: '{SEPARATOR.join([''] + parts)}'")
    parent.children[node.name] = node


def read_rows(path):
    """Читает строки CSV-файла VFS.

    Args:
        path: путь к CSV-файлу на диске реальной ОС.

    Returns:
        Список пар (номер строки в файле, словарь полей).

    Raises:
        OSError: если файл не удалось прочитать.
        VfsError: если заголовок файла неверный.
    """
    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != CSV_FIELDS:
            raise VfsError(f"CSV header must be: {','.join(CSV_FIELDS)}")
        return list(enumerate(reader, start=FIRST_DATA_LINE))


def parse_row(line, row):
    """Извлекает из строки CSV путь, тип и данные элемента.

    Args:
        line: номер строки в файле (для сообщения об ошибке).
        row: словарь полей строки.

    Returns:
        Кортеж (номер строки, список имён пути, тип, данные).

    Raises:
        VfsError: если путь некорректен.
    """
    try:
        parts = split_path(row.get("path") or "")
    except VfsError as error:
        raise VfsError(f"line {line}: {error}") from error
    return line, parts, row.get("type") or "", row.get("data") or ""


def load_vfs(path):
    """Загружает VFS из CSV-файла в память.

    Элементы добавляются по возрастанию глубины, поэтому порядок строк
    в файле не важен. Строка с путём "/" описывает корень и пропускается.

    Args:
        path: путь к CSV-файлу на диске реальной ОС.

    Returns:
        Корневой каталог VFS.

    Raises:
        OSError: если файл не удалось прочитать.
        VfsError: если данные файла некорректны.
    """
    entries = [parse_row(line, row) for line, row in read_rows(path)]
    entries.sort(key=lambda entry: len(entry[1]))
    root = VfsDir("")
    for line, parts, kind, data in entries:
        if not parts:
            continue
        try:
            add_node(root, parts, make_node(parts[-1], kind, data))
        except VfsError as error:
            raise VfsError(f"line {line}: {error}") from error
    return root


def describe(node):
    """Возвращает подпись элемента для дерева.

    Args:
        node: элемент VFS.

    Returns:
        "имя/" для каталога, "имя (N bytes)" для файла.
    """
    if isinstance(node, VfsDir):
        return node.name + SEPARATOR
    return f"{node.name} ({len(node.data)} bytes)"


def format_tree(directory, prefix=""):
    """Формирует дерево содержимого каталога.

    Args:
        directory: каталог VFS.
        prefix: отступ, накопленный на верхних уровнях.

    Returns:
        Список строк дерева без строки самого каталога.
    """
    lines = []
    children = sorted(directory.children.values(), key=lambda n: n.name)
    for index, child in enumerate(children):
        is_last = index == len(children) - 1
        lines.append(prefix + (TREE_LAST if is_last else TREE_BRANCH)
                     + describe(child))
        if isinstance(child, VfsDir):
            nested = prefix + (TREE_SPACE if is_last else TREE_PIPE)
            lines.extend(format_tree(child, nested))
    return lines