from pathlib import Path
import pytest

from app.security import resolve_user_path, SecurityError
from app.config import WORKSPACE_ROOT


def test_resolve_valid_path():
    p = resolve_user_path(".")
    assert isinstance(p, Path)


def test_escape_workspace():
    with pytest.raises(SecurityError):
        resolve_user_path("../../etc/passwd")


def test_workspace_root_inside():
    p = resolve_user_path(".")

    assert WORKSPACE_ROOT in p.parents or p == WORKSPACE_ROOT