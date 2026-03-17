from app.mcp_server import list_dir, read_file


def test_mcp_list_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))

    (tmp_path / "a.txt").write_text("hello")

    result = list_dir(path=".")

    names = [e["name"] for e in result["entries"]]

    assert "a.txt" in names


def test_mcp_read_file(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))

    file_path = tmp_path / "b.txt"
    file_path.write_text("line1\nline2\n")

    result = read_file(path="b.txt")

    assert "line1" in result["content"]