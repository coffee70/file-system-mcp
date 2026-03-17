import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from ..config import SUBPROCESS_TIMEOUT_SEC


def run_rg(
    query: str,
    cwd: Path,
    glob: str | None = None,
    max_results: int = 100,
    context_lines: int = 0,
) -> Dict[str, Any]:
    cmd = [
        "rg",
        "--json",
        "--line-number",
        "--column",
        "--max-count",
        str(max_results),
    ]

    if context_lines > 0:
        cmd.extend(["-C", str(context_lines)])

    if glob:
        cmd.extend(["-g", glob])

    cmd.extend([query, str(cwd)])

    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=SUBPROCESS_TIMEOUT_SEC,
        check=False,
    )

    matches: List[Dict[str, Any]] = []

    for line in proc.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        if event.get("type") != "match":
            continue

        data = event.get("data", {})
        path = data.get("path", {}).get("text")
        line_number = data.get("line_number")
        lines = data.get("lines", {}).get("text", "")
        submatches = data.get("submatches", [])

        column = 1
        if submatches:
            column = submatches[0].get("start", 0) + 1

        matches.append(
            {
                "path": path,
                "line": line_number,
                "column": column,
                "snippet": lines.rstrip("\n"),
            }
        )

    return {"matches": matches}