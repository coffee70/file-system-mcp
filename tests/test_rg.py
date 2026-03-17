from pathlib import Path

from app.adapters.rg import run_rg


def test_rg_finds_match(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world\nfoo bar\nhello again\n")

    result = run_rg(query="hello", cwd=Path(tmp_path), max_results=10)

    assert "matches" in result
    assert len(result["matches"]) >= 1
    assert any("hello" in m["snippet"] for m in result["matches"])