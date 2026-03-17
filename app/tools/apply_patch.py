from pathlib import Path

from ..models import ApplyPatchRequest, ApplyPatchResponse
from ..config import ENABLE_WRITES
from ..security import resolve_user_path
from ..adapters.diffing import apply_unified_patch


def handle_apply_patch(req: ApplyPatchRequest) -> ApplyPatchResponse:
    if not ENABLE_WRITES:
        raise PermissionError("Write operations are disabled (ENABLE_WRITES=false).")

    p = resolve_user_path(req.path)

    if p.exists() and not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    if p.exists():
        original = p.read_text(encoding="utf-8", errors="replace")
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        original = ""

    updated = apply_unified_patch(original, req.diff)

    p.write_text(updated, encoding="utf-8")

    return ApplyPatchResponse(
        path=req.path,
        applied=True,
    )