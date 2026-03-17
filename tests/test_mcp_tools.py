from importlib import reload

import app.config
import app.tools.apply_patch as apply_patch_module
import app.tools.propose_patch as propose_patch_module
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


def test_propose_patch_for_new_file(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))

    result = propose_patch_module.handle_propose_patch(
        propose_patch_module.ProposePatchRequest(
            path="newfile.txt",
            instruction="write: hello\nworld",
        )
    )

    assert result.path == "newfile.txt"
    assert "--- a/newfile.txt" in result.diff
    assert "+++ b/newfile.txt" in result.diff
    assert "+hello\n" in result.diff
    assert "+world\n" in result.diff


def test_apply_patch_creates_new_file(tmp_path, monkeypatch):
    monkeypatch.setenv("WORKSPACE_ROOT", str(tmp_path))
    monkeypatch.setenv("ENABLE_WRITES", "true")

    reload(app.config)
    reload(apply_patch_module)

    diff = (
        "--- a/newfile.txt\n"
        "+++ b/newfile.txt\n"
        "@@ -0,0 +1,2 @@\n"
        "+hello\n"
        "+world\n"
    )

    result = apply_patch_module.handle_apply_patch(
        apply_patch_module.ApplyPatchRequest(
            path="newfile.txt",
            diff=diff,
        )
    )

    assert result.applied is True
    assert (tmp_path / "newfile.txt").read_text() == "hello\nworld\n"