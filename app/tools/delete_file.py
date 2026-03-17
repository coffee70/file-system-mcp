import hashlib

from ..config import ENABLE_WRITES
from ..models import DeleteFileRequest, DeleteFileResponse
from ..security import resolve_user_path

# Files that should never be deleted by agents
PROTECTED_FILES = {
    "pyproject.toml",
    "Dockerfile",
    ".env",
    ".gitignore",
}


def handle_delete_file(req: DeleteFileRequest) -> DeleteFileResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    # Prevent deletion of protected files
    if p.name in PROTECTED_FILES:
        raise PermissionError(f"Deletion of protected file is not allowed: {p.name}")

    if not p.exists():
        if req.missing_ok:
            return DeleteFileResponse(
                path=req.path,
                deleted=False,
                existed=False,
                bytes_removed=0,
                sha256_before_delete=None,
            )
        raise FileNotFoundError(f"File not found: {req.path}")

    if not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    content = p.read_bytes()
    bytes_removed = len(content)
    sha256 = hashlib.sha256(content).hexdigest()

    try:
        p.unlink()
    except FileNotFoundError:
        pass

    return DeleteFileResponse(
        path=req.path,
        deleted=True,
        existed=True,
        bytes_removed=bytes_removed,
        sha256_before_delete=sha256,
    )
