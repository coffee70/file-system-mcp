import os
import re
import signal
import subprocess
import time
from collections.abc import Sequence

from ..config import RUN_COMMAND_ENABLED, RUN_COMMAND_MAX_OUTPUT_CHARS, RUN_COMMAND_MAX_TIMEOUT_SEC

_CONTAINER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_MODULE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*$")


def _truncate(text: str) -> str:
    limit = RUN_COMMAND_MAX_OUTPUT_CHARS
    if len(text) <= limit:
        return text
    extra = len(text) - limit
    return text[:limit] + f"\n...[truncated {extra} chars]"


def _validate_container(container: str) -> str:
    if not _CONTAINER_RE.fullmatch(container):
        raise ValueError("container must be a Docker container name or ID")
    return container


def _validate_path(path: str) -> str:
    if not path or "\x00" in path:
        raise ValueError("path must be non-empty and cannot contain NUL bytes")
    if path.startswith("-"):
        raise ValueError("path cannot start with '-' because it may be parsed as an option")
    return path


def _validate_url(url: str) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("url must start with http:// or https://")
    if "\x00" in url or any(char.isspace() for char in url):
        raise ValueError("url cannot contain whitespace or NUL bytes")
    return url


def _validate_module(module: str) -> str:
    if not _MODULE_RE.fullmatch(module):
        raise ValueError("module must be a dotted Python module name")
    return module


def _clean_args(args: Sequence[str] | None) -> list[str]:
    cleaned: list[str] = []
    for arg in args or []:
        if "\x00" in arg:
            raise ValueError("arguments cannot contain NUL bytes")
        cleaned.append(str(arg))
    return cleaned


def _host_env() -> dict:
    env = dict(os.environ)
    env.setdefault("PYTHONUNBUFFERED", "1")
    env.setdefault("CI", "1")
    env.setdefault("NO_COLOR", "1")
    return env


def _docker_exec(container: str, inner_args: list[str], timeout_seconds: int | None = None) -> dict:
    if not RUN_COMMAND_ENABLED:
        raise PermissionError("run_command tool disabled")

    container = _validate_container(container)
    timeout = min(timeout_seconds or RUN_COMMAND_MAX_TIMEOUT_SEC, RUN_COMMAND_MAX_TIMEOUT_SEC)
    argv = ["docker", "exec", container] + inner_args

    start = time.monotonic()

    try:
        proc = subprocess.Popen(
            argv,
            env=_host_env(),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
            start_new_session=True,
        )
    except FileNotFoundError as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        return {
            "ok": False,
            "command": argv,
            "returncode": 127,
            "stdout": "",
            "stderr": f"docker CLI not found. Install Docker on the host. ({exc})",
            "timed_out": False,
            "duration_ms": duration_ms,
        }

    timed_out = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()

    duration_ms = int((time.monotonic() - start) * 1000)

    if proc.returncode == 127:
        stderr += "\nHint: docker not available or not on PATH."

    return {
        "ok": proc.returncode == 0 and not timed_out,
        "command": argv,
        "returncode": proc.returncode,
        "stdout": _truncate(stdout or ""),
        "stderr": _truncate(stderr or ""),
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }


def docker_exec_ps(container: str, args: list[str] | None = None, timeout_seconds: int | None = None) -> dict:
    return _docker_exec(container, ["ps"] + _clean_args(args), timeout_seconds)


def docker_exec_env(container: str, timeout_seconds: int | None = None) -> dict:
    return _docker_exec(container, ["env"], timeout_seconds)


def docker_exec_ls(container: str, path: str = ".", args: list[str] | None = None, timeout_seconds: int | None = None) -> dict:
    return _docker_exec(container, ["ls"] + _clean_args(args) + [_validate_path(path)], timeout_seconds)


def docker_exec_cat(container: str, path: str, timeout_seconds: int | None = None) -> dict:
    return _docker_exec(container, ["cat", _validate_path(path)], timeout_seconds)


def docker_exec_http_probe(container: str, url: str, timeout_seconds: int | None = None) -> dict:
    timeout = min(timeout_seconds or RUN_COMMAND_MAX_TIMEOUT_SEC, RUN_COMMAND_MAX_TIMEOUT_SEC)
    return _docker_exec(
        container,
        ["curl", "--fail", "--silent", "--show-error", "--location", "--max-time", str(timeout), _validate_url(url)],
        timeout,
    )


def docker_exec_python_module(
    container: str,
    module: str,
    args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    return _docker_exec(
        container,
        ["python", "-m", _validate_module(module)] + _clean_args(args),
        timeout_seconds,
    )


def docker_exec_node(container: str, args: list[str] | None = None, timeout_seconds: int | None = None) -> dict:
    cleaned_args = _clean_args(args)
    if cleaned_args and cleaned_args[0] == "-e":
        raise ValueError("node -e is not allowed; use a checked-in script or module path")
    return _docker_exec(container, ["node"] + cleaned_args, timeout_seconds)
