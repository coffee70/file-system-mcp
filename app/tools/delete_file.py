import hashlib

from ..config import ENABLE_WRITES
from ..models import DeleteFileRequest, DeleteFileResponse
from ..security import resolve_user_path


def handle_delete_file(req: DeleteFileRequest) -> DeleteFileResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    existed = p.exists()

    if not existed:
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

    p.unlink()

    return DeleteFileResponse(
        path=req.path,
        deleted=True,
        existed=True,
        bytes_removed=bytes_removed,
        sha256_before_delete=sha256,
    )
