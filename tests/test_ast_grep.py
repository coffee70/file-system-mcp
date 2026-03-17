import pytest
from pathlib import Path

from app.adapters.ast_grep import run_ast_grep


def test_ast_grep_runs(tmp_path):
    file_path = tmp_path / "example.py"
    file_path.write_text(
        """
import requests

def fetch():
    requests.get("https://example.com")
"""
    )

    result = run_ast_grep(
        pattern="requests.$METHOD($ARGS)",
        language="python",
        cwd=Path(tmp_path),
        max_results=10,
    )

    assert "matches" in result