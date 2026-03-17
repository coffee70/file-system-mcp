from pathlib import Path
from typing import List, Dict, Any

from ..config import MAX_FILE_SIZE_BYTES
from ..security import resolve_user_path


def list_dir(path: str, max_entries: int) -> Dict[str, Any]:
    p = resolve_user_path(path)

    if not p.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if not p.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    entries = []
    count = 0

    for child in sorted(p.iterdir(), key=lambda x: x.name):
        if count >= max_entries:
            break

        if child.is_dir():
            entries.append(
                {
                    "name": child.name,
                    "type": "dir",
                }
            )
        else:
            try:
                size = child.stat().st_size
            except OSError:
                size = None

            entries.append(
                {
                    "name": child.name,
                    "type": "file",
                    "size": size,
                }
            )

        count += 1

    return {
        "path": path,
        "entries": entries,
    }


def read_file_lines(path: str) -> List[str]:
    p = resolve_user_path(path)

    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {path}")

    size = p.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File exceeds max size limit: {size} bytes")

    text = p.read_text(encoding="utf-8", errors="replace")
    return text.splitlines()


def read_multiple_files(paths: List[str]) -> List[Dict[str, str]]:
    results = []

    for path in paths:
        try:
            p = resolve_user_path(path)

            if not p.exists() or not p.is_file():
                continue

            size = p.stat().st_size
            if size > MAX_FILE_SIZE_BYTES:
                continue

            content = p.read_text(encoding="utf-8", errors="replace")

            results.append(
                {
                    "path": path,
                    "content": content,
                }
            )
        except Exception:
            continue

    return results