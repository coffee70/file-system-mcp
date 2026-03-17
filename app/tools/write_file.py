from ..config import ENABLE_WRITES
from ..models import WriteFileRequest, WriteFileResponse
from ..security import resolve_user_path


def handle_write_file(req: WriteFileRequest) -> WriteFileResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    if p.exists() and not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    if not p.parent.exists():
        if req.create_dirs:
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Parent directory does not exist: {p.parent}")

    p.write_text(req.content, encoding="utf-8")

    return WriteFileResponse(
        path=req.path,
        written=True,
        bytes_written=len(req.content.encode("utf-8")),
    )