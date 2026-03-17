from pathlib import Path

from app.tools.list_dir import handle_list_dir
from app.models import ListDirRequest


def test_list_dir_basic(tmp_path):
    (tmp_path / "file1.txt").write_text("hello")
    (tmp_path / "file2.txt").write_text("world")
    (tmp_path / "subdir").mkdir()

    req = ListDirRequest(path=str(tmp_path))
    result = handle_list_dir(req)

    names = [e.name for e in result.entries]

    assert "file1.txt" in names
    assert "file2.txt" in names
    assert "subdir" in names