import shutil
from pathlib import Path

from ..config import ENABLE_WRITES
from ..models import DeleteDirRequest, DeleteDirResponse
from ..security import resolve_user_path

PROTECTED_DIRS = {
    ".git",
    ".venv",
    "app",
    "tests",
    "scripts",
}


def _count_items(root: Path) -> int:
    count = 0
    for _ in root.rglob("*"):
        count += 1
    return count


def _dir_depth(root: Path) -> int:
    max_depth = 0
    for child in root.rglob("*"):
        try:
            rel = child.relative_to(root)
            max_depth = max(max_depth, len(rel.parts))
        except Exception:
            continue
    return max_depth


def handle_delete_dir(req: DeleteDirRequest) -> DeleteDirResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    if p.name in PROTECTED_DIRS:
        raise PermissionError(f"Deletion of protected directory is not allowed: {p.name}")

    if not p.exists():
        if req.missing_ok:
            return DeleteDirResponse(
                path=req.path,
                deleted=False,
                existed=False,
                recursive=req.recursive,
                items_removed=0,
            )
        raise FileNotFoundError(f"Directory not found: {req.path}")

    if not p.is_dir():
        raise NotADirectoryError(f"Expected directory but got file: {req.path}")

    items_removed = _count_items(p)

    if req.recursive:
        actual_depth = _dir_depth(p)
        if actual_depth > req.max_depth:
            raise PermissionError(
                f"Directory depth {actual_depth} exceeds allowed max_depth {req.max_depth}"
            )
        shutil.rmtree(p)
    else:
        p.rmdir()

    return DeleteDirResponse(
        path=req.path,
        deleted=True,
        existed=True,
        recursive=req.recursive,
        items_removed=items_removed,
    )
