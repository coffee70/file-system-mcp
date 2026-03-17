from ..models import ProposePatchRequest, ProposePatchResponse
from ..security import resolve_user_path
from ..adapters.diffing import generate_unified_diff


def handle_propose_patch(req: ProposePatchRequest) -> ProposePatchResponse:
    p = resolve_user_path(req.path)

    if not p.exists():
        raise FileNotFoundError(f"File not found: {req.path}")

    if not p.is_file():
        raise IsADirectoryError(f"Expected file but got directory: {req.path}")

    original = p.read_text(encoding="utf-8", errors="replace")

    # For now we return a no-op diff until an AI editing step is implemented.
    modified = original

    diff = generate_unified_diff(original, modified, req.path)

    return ProposePatchResponse(
        path=req.path,
        diff=diff,
        summary="No changes generated. Patch generation engine not yet implemented.",
    )