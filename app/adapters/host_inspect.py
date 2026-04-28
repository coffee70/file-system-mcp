import os
import re
import signal
import subprocess
import time
from pathlib import Path

from ..config import RUN_COMMAND_ENABLED, RUN_COMMAND_MAX_OUTPUT_CHARS, RUN_COMMAND_MAX_TIMEOUT_SEC, WORKSPACE_ROOT

_SENSITIVE_ENV_RE = re.compile(r"(TOKEN|SECRET|PASSWORD|PASSWD|API[_-]?KEY|PRIVATE[_-]?KEY|CREDENTIAL|AUTH|COOKIE)", re.IGNORECASE)


def _truncate(text: str) -> str:
    limit = RUN_COMMAND_MAX_OUTPUT_CHARS
    if len(text) <= limit:
        return text
    extra = len(text) - limit
    return text[:limit] + f"\n...[truncated {extra} chars]"


def _validate_workspace_path(user_path: str) -> Path:
    if not user_path or "\x00" in user_path:
        raise ValueError("path must be non-empty and cannot contain NUL bytes")
    if user_path.startswith("-"):
        raise ValueError("path cannot start with '-' because it may be parsed as an option")

    candidate = (WORKSPACE_ROOT / user_path).resolve()
    if candidate != WORKSPACE_ROOT and WORKSPACE_ROOT not in candidate.parents:
        raise ValueError("path escapes workspace root")
    return candidate


def _run(argv: list[str], timeout_seconds: int | None = None) -> dict:
    if not RUN_COMMAND_ENABLED:
        raise PermissionError("run_command tool disabled")

    timeout = min(timeout_seconds or RUN_COMMAND_MAX_TIMEOUT_SEC, RUN_COMMAND_MAX_TIMEOUT_SEC)
    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONUNBUFFERED": "1",
        "CI": "1",
        "NO_COLOR": "1",
    }

    start = time.monotonic()
    try:
        proc = subprocess.Popen(
            argv,
            cwd=str(WORKSPACE_ROOT),
            env=env,
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
            "stderr": str(exc),
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
    return {
        "ok": proc.returncode == 0 and not timed_out,
        "command": argv,
        "returncode": proc.returncode,
        "stdout": _truncate(stdout or ""),
        "stderr": _truncate(stderr or ""),
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }


def _redact_env_output(stdout: str) -> str:
    redacted_lines: list[str] = []
    for line in stdout.splitlines():
        if "=" not in line:
            redacted_lines.append(line)
            continue
        key, value = line.split("=", 1)
        if _SENSITIVE_ENV_RE.search(key):
            redacted_lines.append(f"{key}=<redacted>")
        else:
            redacted_lines.append(f"{key}={value}")
    return "\n".join(redacted_lines) + ("\n" if stdout.endswith("\n") else "")


def host_ps(timeout_seconds: int | None = None) -> dict:
    return _run(["ps", "aux"], timeout_seconds)


def host_env(timeout_seconds: int | None = None) -> dict:
    result = _run(["env"], timeout_seconds)
    result["stdout"] = _redact_env_output(result["stdout"])
    return result


def host_ls(path: str = ".", long: bool = True, all: bool = True, timeout_seconds: int | None = None) -> dict:
    resolved = _validate_workspace_path(path)
    args = ["ls"]
    flags = "-"
    if long:
        flags += "l"
    if all:
        flags += "a"
    if flags != "-":
        args.append(flags)
    args.append(str(resolved))
    return _run(args, timeout_seconds)


def host_df(timeout_seconds: int | None = None) -> dict:
    return _run(["df", "-h", str(WORKSPACE_ROOT)], timeout_seconds)


def host_ports(timeout_seconds: int | None = None) -> dict:
    result = _run(["ss", "-tulpn"], timeout_seconds)
    if result["returncode"] == 127:
        return _run(["netstat", "-tulpn"], timeout_seconds)
    return result


def host_tail(path: str, lines: int = 100, timeout_seconds: int | None = None) -> dict:
    if lines < 1 or lines > 1000:
        raise ValueError("lines must be between 1 and 1000")
    resolved = _validate_workspace_path(path)
    if not resolved.exists():
        raise FileNotFoundError("path does not exist")
    if not resolved.is_file():
        raise ValueError("path must be a file")
    return _run(["tail", "-n", str(lines), str(resolved)], timeout_seconds)
