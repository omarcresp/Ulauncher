from __future__ import annotations

import os
from typing import Generator

from ulauncher.config import PATHS


def is_extension(ext_path: str) -> bool:
    """
    Tells whether the argument is an extension directory
    """
    expected_files = [
        "manifest.json",
        "main.py",
    ]
    return all(os.path.isfile(os.path.join(ext_path, file)) for file in expected_files)


def is_manageable(ext_path: str, user_ext_path: str = PATHS.USER_EXTENSIONS_DIR) -> bool:
    """
    Tells the directory is user-provided extension.
    """
    ext_path = os.path.realpath(ext_path)
    return os.path.dirname(ext_path) == user_ext_path and is_extension(ext_path)


def locate_iter(ext_id: str, exts_dirs: list[str] = PATHS.ALL_EXTENSIONS_DIRS) -> Generator[str, None, None]:
    """
    Yields all existing directories for given `ext_id`
    """
    for exts_dir in exts_dirs:
        ext_path = os.path.join(exts_dir, ext_id)
        if is_extension(ext_path):
            yield os.path.realpath(ext_path)


def locate(ext_id: str, exts_dirs: list[str] = PATHS.ALL_EXTENSIONS_DIRS) -> str | None:
    """
    Locates (an existing) extension directory.
    """
    return next(locate_iter(ext_id, exts_dirs=exts_dirs), None)


def get_user_dir(ext_id: str, user_ext_path: str = PATHS.USER_EXTENSIONS_DIR) -> str:
    """
    Returns path to writable extension directory
    """
    return os.path.realpath(os.path.join(user_ext_path, ext_id))


def iterate(
    exts_dirs: list[str] = PATHS.ALL_EXTENSIONS_DIRS, duplicates: bool = False
) -> Generator[tuple[str, str], None, None]:
    """
    Yields `(extension_id, extension_path)` tuples found in a given extensions dirs
    """
    occurrences = set()
    for ext_path in exts_dirs:
        if not os.path.exists(ext_path):
            continue
        for entry in os.scandir(ext_path):
            ext_id = entry.name
            if is_extension(entry.path) and (duplicates or ext_id not in occurrences):
                occurrences.add(ext_id)
                yield ext_id, os.path.realpath(entry.path)
