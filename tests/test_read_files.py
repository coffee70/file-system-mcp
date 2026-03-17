from app.tools.read_files import handle_read_files
from app.models import ReadFilesRequest


def test_read_multiple_files(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"

    f1.write_text("hello")
    f2.write_text("world")

    req = ReadFilesRequest(paths=[str(f1), str(f2)])
    result = handle_read_files(req)

    contents = {f.path: f.content for f in result.files}

    assert str(f1) in contents
    assert str(f2) in contents
    assert contents[str(f1)] == "hello"
    assert contents[str(f2)] == "world"