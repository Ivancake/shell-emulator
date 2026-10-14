"""Состояние эмулятора, общее для всех команд."""

from dataclasses import dataclass, field

from vfs import VfsDir

NO_VFS_SOURCE = "(empty)"


@dataclass
class ShellState:
    """Состояние эмулятора.

    Attributes:
        vfs_root: корневой каталог VFS в памяти.
        vfs_source: путь к CSV-файлу, из которого загружена VFS.
    """

    vfs_root: VfsDir = field(default_factory=lambda: VfsDir(""))
    vfs_source: str = NO_VFS_SOURCE