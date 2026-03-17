import hashlib

from ..config import ENABLE_WRITES
from ..models import WriteFileRequest, WriteFileResponse
from ..security import resolve_user_path


def handle_write_file(req: WriteFileRequest) -> WriteFileResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    created = not p.exists()

    if p.exists() and not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    if not p.parent.exists():
        if req.create_dirs:
            p.parent.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(f"Parent directory does not exist: {p.parent}")

    content = req.content

    if content and not content.endswith("\n"):
        content = content

    p.write_text(content, encoding="utf-8")

    byte_count = len(content.encode("utf-8"))
    line_count = content.count("\n") + (1 if content and not content.endswith("\n") else 0)

    sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()

    return WriteFileResponse(
        path=req.path,
        written=True,
        created=created,
        bytes_written=byte_count,
        line_count=line_count,
        sha256=sha256,
    )
