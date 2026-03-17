import hashlib
import shutil

from ..config import ENABLE_WRITES
from ..models import MoveFileRequest, MoveFileResponse
from ..security import resolve_user_path


def handle_move_file(req: MoveFileRequest) -> MoveFileResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    src = resolve_user_path(req.src)
    dst = resolve_user_path(req.dst)

    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Source file not found: {req.src}")

    if dst.exists() and not req.overwrite:
        raise FileExistsError(f"Destination exists: {req.dst}")

    if not dst.parent.exists():
        if req.create_dirs:
            dst.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Parent directory does not exist: {dst.parent}")

    data = src.read_bytes()

    shutil.move(src, dst)

    sha256 = hashlib.sha256(data).hexdigest()

    return MoveFileResponse(
        src=req.src,
        dst=req.dst,
        moved=True,
        destination_created=not dst.exists(),
        bytes_moved=len(data),
        sha256=sha256,
    )
