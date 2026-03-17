from pathlib import Path
from app.tools.read_file import handle_read_file
from app.models import ReadFileRequest


def test_read_file_basic(tmp_path):
    file_path = tmp_path / "test.txt"
    file_path.write_text("line1\nline2\nline3\n")

    req = ReadFileRequest(path=str(file_path))
    result = handle_read_file(req)

    assert "line1" in result.content
    assert result.start_line == 1


def test_read_file_range(tmp_path):
    file_path = tmp_path / "range.txt"
    file_path.write_text("a\nb\nc\nd\n")

    req = ReadFileRequest(path=str(file_path), start_line=2, end_line=3)
    result = handle_read_file(req)

    assert result.content == "b\nc"
    assert result.start_line == 2
    assert result.end_line == 3