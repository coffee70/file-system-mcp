from pathlib import Path
from .config import WORKSPACE_ROOT


class SecurityError(Exception):
    pass


def resolve_user_path(user_path: str) -> Path:
    if not user_path:
        raise SecurityError("Path cannot be empty")

    candidate = (WORKSPACE_ROOT / user_path).resolve()

    if candidate != WORKSPACE_ROOT and WORKSPACE_ROOT not in candidate.parents:
        raise SecurityError(f"Path escapes workspace root: {user_path}")

    return candidate