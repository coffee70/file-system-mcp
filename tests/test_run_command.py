from pathlib import Path

import pytest

from app.adapters import run_command as run_command_module


def test_run_command_python_success(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    result = run_command_module.run_command(
        command="python3",
        args=["-c", "print('hello')"],
        cwd=".",
        timeout_seconds=5,
    )

    assert result["ok"] is True
    assert result["returncode"] == 0
    assert "hello" in result["stdout"]
    assert result["timed_out"] is False


def test_run_command_rejects_workspace_escape(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    with pytest.raises(ValueError, match="cwd escapes workspace root"):
        run_command_module.run_command(
            command="python3",
            args=["-c", "print('x')"],
            cwd="../",
            timeout_seconds=5,
        )


def test_run_command_rejects_npm_install(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    with pytest.raises(ValueError, match="npm subcommand not allowed"):
        run_command_module.run_command(
            command="npm",
            args=["install"],
            cwd=".",
            timeout_seconds=5,
        )


def test_run_command_rejects_npx_without_no_install(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    with pytest.raises(ValueError, match="npx requires --no-install flag"):
        run_command_module.run_command(
            command="npx",
            args=["prettier", "--version"],
            cwd=".",
            timeout_seconds=5,
        )


def test_run_command_timeout(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    result = run_command_module.run_command(
        command="python3",
        args=["-c", "import time; time.sleep(2)"],
        cwd=".",
        timeout_seconds=1,
    )

    assert result["ok"] is False
    assert result["timed_out"] is True


def test_run_command_output_truncation(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", True)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_MAX_OUTPUT_CHARS", 20)

    result = run_command_module.run_command(
        command="python3",
        args=["-c", "print('abcdefghijklmnopqrstuvwxyz')"],
        cwd=".",
        timeout_seconds=5,
    )

    assert "[truncated" in result["stdout"]


def test_run_command_disabled(monkeypatch, tmp_path):
    monkeypatch.setattr(run_command_module, "RUN_COMMAND_ENABLED", False)
    monkeypatch.setattr(run_command_module, "WORKSPACE_ROOT", tmp_path)

    with pytest.raises(PermissionError, match="run_command tool disabled"):
        run_command_module.run_command(
            command="python3",
            args=["-c", "print('x')"],
            cwd=".",
            timeout_seconds=5,
        )
