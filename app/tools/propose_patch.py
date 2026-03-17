from ..models import ProposePatchRequest, ProposePatchResponse
from ..security import resolve_user_path
from ..adapters.diffing import generate_unified_diff


def _apply_simple_instruction(original: str, instruction: str) -> str:
    """
    Very simple editing engine so the MCP can modify or create files.

    Supported instructions:
    - "append: TEXT"
    - "replace: OLD -> NEW"
    - "delete: TEXT"
    - "prepend: TEXT"
    - "write: TEXT"   (replace entire file contents)
    """

    text = original

    if instruction.startswith("write:"):
        body = instruction[len("write:"):].lstrip()
        if body and not body.endswith("\n"):
            body += "\n"
        return body

    if instruction.startswith("append:"):
        addition = instruction[len("append:"):].lstrip()
        if not text.endswith("\n") and text:
            text += "\n"
        text += addition
        if text and not text.endswith("\n"):
            text += "\n"
        return text

    if instruction.startswith("prepend:"):
        addition = instruction[len("prepend:"):].lstrip()
        if addition and not addition.endswith("\n"):
            addition += "\n"
        return addition + text

    if instruction.startswith("replace:"):
        payload = instruction[len("replace:"):].strip()
        if "->" not in payload:
            raise ValueError("replace instruction must be: replace: OLD -> NEW")

        old, new = payload.split("->", 1)
        return text.replace(old.strip(), new.strip())

    if instruction.startswith("delete:"):
        target = instruction[len("delete:"):].strip()
        return text.replace(target, "")

    return original


def handle_propose_patch(req: ProposePatchRequest) -> ProposePatchResponse:
    p = resolve_user_path(req.path)

    if p.exists():
        if not p.is_file():
            raise IsADirectoryError(f"Expected file but got directory: {req.path}")
        original = p.read_text(encoding="utf-8", errors="replace")
    else:
        original = ""

    modified = _apply_simple_instruction(original, req.instruction)
    diff = generate_unified_diff(original, modified, req.path)

    summary = "Patch generated"
    if original == modified:
        summary = "Instruction produced no changes"
    elif not p.exists():
        summary = "Patch generated for new file"

    return ProposePatchResponse(
        path=req.path,
        diff=diff,
        summary=summary,
    )