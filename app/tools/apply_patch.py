from ..models import ApplyPatchRequest, ApplyPatchResponse
from ..config import ENABLE_WRITES
from ..security import resolve_user_path
from ..adapters.diffing import apply_unified_patch


def handle_apply_patch(req: ApplyPatchRequest) -> ApplyPatchResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    if not p.exists():
        raise FileNotFoundError(f"File not found: {req.path}")

    if not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    original = p.read_text(encoding="utf-8", errors="replace")
    updated = apply_unified_patch(original, req.diff)

    p.write_text(updated, encoding="utf-8")

    return ApplyPatchResponse(
        path=req.path,
        applied=True,
    )