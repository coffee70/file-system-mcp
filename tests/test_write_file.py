from pathlib import Path

import pytest

from app.tools.write_file import handle_write_file
from app.models import WriteFileRequest


def test_write_file_creates_new_file(monkeypatch, tmp_path):
    monkeypatch.setattr("app.tools.write_file.ENABLE_WRITES", True)

    req = WriteFileRequest(
        path="tmp_test_dir/example.txt",
        content="hello world\n",
        create_dirs=True,
    )

    monkeypatch.setattr("app.security.WORKSPACE_ROOT", tmp_path)
    response = handle_write_file(req)

    written_path = tmp_path / "tmp_test_dir" / "example.txt"

    assert response.written is True
    assert response.path == "tmp_test_dir/example.txt"
    assert written_path.read_text(encoding="utf-8") == "hello world\n"


def test_write_file_requires_existing_parent_when_create_dirs_false(monkeypatch, tmp_path):
    monkeypatch.setattr("app.tools.write_file.ENABLE_WRITES", True)
    monkeypatch.setattr("app.security.WORKSPACE_ROOT", tmp_path)

    req = WriteFileRequest(
        path="missing_dir/example.txt",
        content="hello\n",
        create_dirs=False,
    )

    with pytest.raises(FileNotFoundError):
        handle_write_file(req)