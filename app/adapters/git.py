import subprocess
from pathlib import Path
from typing import Any

from ..config import SUBPROCESS_TIMEOUT_SEC, WORKSPACE_ROOT


ALLOWED_COMMANDS = {
    "status",
    "diff",
    "add",
    "commit",
    "log",
    "branch",
    "checkout",
}


def run_git(command: str, args: list[str] | None = None) -> dict[str, Any]:
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Unsupported git command: {command}")

    args = args or []
    cmd = ["git", command, *args]

    proc = subprocess.run(
        cmd,
        cwd=Path(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_SEC,
        check=False,
    )

    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }
