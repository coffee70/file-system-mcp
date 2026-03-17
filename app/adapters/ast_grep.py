import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from ..config import SUBPROCESS_TIMEOUT_SEC


def run_ast_grep(
    pattern: str,
    language: str,
    cwd: Path,
    max_results: int = 100,
) -> Dict[str, Any]:
    cmd = [
        "ast-grep",
        "scan",
        "--pattern",
        pattern,
        "--lang",
        language,
        "--json",
        str(cwd),
    ]

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_SEC,
        check=False,
    )

    raw = proc.stdout.strip()
    if not raw:
        return {"matches": []}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {"matches": []}

    matches: List[Dict[str, Any]] = []

    for item in parsed[:max_results]:
        file_path = item.get("file", "")
        start = item.get("range", {}).get("start", {})
        line = start.get("line", 0) + 1

        matches.append(
            {
                "path": file_path,
                "line": line,
                "column": 1,
                "snippet": item.get("text", "").strip(),
            }
        )

    return {"matches": matches}