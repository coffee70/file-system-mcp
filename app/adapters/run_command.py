import os
import signal
import subprocess
import time
from pathlib import Path

from ..config import (
    RUN_COMMAND_ENABLED,
    RUN_COMMAND_MAX_TIMEOUT_SEC,
    RUN_COMMAND_MAX_OUTPUT_CHARS,
    WORKSPACE_ROOT,
)

ALLOWED_COMMANDS = {
    "cat",
    "docker",
    "docker-compose",
    "echo",
    "find",
    "grep",
    "head",
    "ls",
    "mkdir",
    "node",
    "pwd",
    "python",
    "python3",
    "pytest",
    "npm",
    "npx",
    "pnpm",
    "yarn",
    "uv",
    "poetry",
    "pipenv",
    "ruff",
    "mypy",
    "rg",
    "git",
    "sed",
    "tail",
    "touch",
    "which",
}

DOCKER_ALLOWED_SUBCOMMANDS = {
    "version",
    "info",
    "ps",
    "images",
    "logs",
    "inspect",
    "exec",
    "cp",
    "port",
    "stats",
    "top",
    "events",
    "network",
    "volume",
    "compose",
}

DOCKER_COMPOSE_ALLOWED_SUBCOMMANDS = {
    "version",
    "ls",
    "ps",
    "logs",
    "config",
    "up",
    "down",
    "restart",
    "start",
    "stop",
    "exec",
    "run",
    "pull",
    "build",
}

DOCKER_NETWORK_ALLOWED_SUBCOMMANDS = {
    "ls",
    "inspect",
}

DOCKER_VOLUME_ALLOWED_SUBCOMMANDS = {
    "ls",
    "inspect",
}


def _truncate(text: str) -> str:
    limit = RUN_COMMAND_MAX_OUTPUT_CHARS
    if len(text) <= limit:
        return text
    extra = len(text) - limit
    return text[:limit] + f"\n...[truncated {extra} chars]"


def _validate_workspace_path(candidate: str) -> Path:
    p = (WORKSPACE_ROOT / candidate).resolve()

    if p != WORKSPACE_ROOT and WORKSPACE_ROOT not in p.parents:
        raise ValueError("cwd escapes workspace root")

    if not p.exists():
        raise FileNotFoundError("cwd does not exist")

    if not p.is_dir():
        raise ValueError("cwd must be a directory")

    return p


def _validate_docker_policy(command: str, args: list[str]):
    if not args:
        raise ValueError(f"{command} requires subcommand")

    if command == "docker-compose":
        if args[0] not in DOCKER_COMPOSE_ALLOWED_SUBCOMMANDS:
            raise ValueError("docker-compose subcommand not allowed")
        return

    top = args[0]
    if top not in DOCKER_ALLOWED_SUBCOMMANDS:
        raise ValueError("docker subcommand not allowed")

    if top == "compose":
        if len(args) < 2:
            raise ValueError("docker compose requires subcommand")
        if args[1] not in DOCKER_COMPOSE_ALLOWED_SUBCOMMANDS:
            raise ValueError("docker compose subcommand not allowed")
        return

    if top == "network":
        if len(args) < 2:
            raise ValueError("docker network requires subcommand")
        if args[1] not in DOCKER_NETWORK_ALLOWED_SUBCOMMANDS:
            raise ValueError("docker network subcommand not allowed")
        return

    if top == "volume":
        if len(args) < 2:
            raise ValueError("docker volume requires subcommand")
        if args[1] not in DOCKER_VOLUME_ALLOWED_SUBCOMMANDS:
            raise ValueError("docker volume subcommand not allowed")
        return


def _validate_command_policy(command: str, args: list[str]):
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"command not allowed: {command}")

    if command == "docker":
        _validate_docker_policy(command, args)

    if command == "docker-compose":
        _validate_docker_policy(command, args)

    if command == "npm":
        if not args:
            raise ValueError("npm requires subcommand")
        if args[0] not in {"test", "run", "exec", "ls"}:
            raise ValueError("npm subcommand not allowed")

    if command == "pnpm":
        if not args:
            raise ValueError("pnpm requires subcommand")
        if args[0] not in {"test", "run", "exec", "ls"}:
            raise ValueError("pnpm subcommand not allowed")

    if command == "yarn":
        if not args:
            raise ValueError("yarn requires subcommand")
        if args[0] not in {"test", "run", "exec", "list"}:
            raise ValueError("yarn subcommand not allowed")

    if command == "npx":
        if "--no-install" not in args:
            raise ValueError("npx requires --no-install flag")

    if command == "uv":
        if not args or args[0] not in {"run", "tool"}:
            raise ValueError("uv subcommand not allowed")

    if command == "poetry":
        if not args or args[0] not in {"run", "show"}:
            raise ValueError("poetry subcommand not allowed")

    if command == "pipenv":
        if not args or args[0] not in {"run", "graph"}:
            raise ValueError("pipenv subcommand not allowed")


def run_command(command: str, args: list[str], cwd: str, timeout_seconds: int | None):
    if not RUN_COMMAND_ENABLED:
        raise PermissionError("run_command tool disabled")

    _validate_command_policy(command, args)

    cwd_path = _validate_workspace_path(cwd)

    timeout = timeout_seconds or RUN_COMMAND_MAX_TIMEOUT_SEC
    timeout = min(timeout, RUN_COMMAND_MAX_TIMEOUT_SEC)

    argv = [command] + args

    env = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONUNBUFFERED": "1",
        "CI": "1",
        "NO_COLOR": "1",
        "DOCKER_HOST": os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock"),
    }

    start = time.monotonic()

    proc = subprocess.Popen(
        argv,
        cwd=str(cwd_path),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
        start_new_session=True,
    )

    timed_out = False

    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(proc.pid, signal.SIGKILL)
        stdout, stderr = proc.communicate()

    duration_ms = int((time.monotonic() - start) * 1000)

    stdout = _truncate(stdout or "")
    stderr = _truncate(stderr or "")

    return {
        "ok": proc.returncode == 0 and not timed_out,
        "command": argv,
        "cwd": str(cwd_path.relative_to(WORKSPACE_ROOT)),
        "returncode": proc.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
    }
