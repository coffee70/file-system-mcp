from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


def _get_env_bool(name: str, default: bool = False) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.lower() in ("1", "true", "yes", "on")


def _get_env_int(name: str, default: int) -> int:
    val = os.environ.get(name)
    if val is None:
        return default
    try:
        return int(val)
    except ValueError:
        return default


# Host-native is the primary runtime mode. The MCP server is expected to run as
# a normal host process with direct access to host binaries, process state,
# loopback/network ports, the workspace filesystem, and an optional host Docker
# CLI/daemon. Isolation is enforced by adapter validation rather than a
# container boundary.
HOST_NATIVE = _get_env_bool("HOST_NATIVE", True)

WORKSPACE_ROOT = Path(os.environ.get("WORKSPACE_ROOT", ".")).resolve()

ENABLE_WRITES = _get_env_bool("ENABLE_WRITES", False)
RUN_COMMAND_ENABLED = _get_env_bool("RUN_COMMAND_ENABLED", True)

MAX_READ_LINES = _get_env_int("MAX_READ_LINES", 400)
MAX_RESULTS = _get_env_int("MAX_RESULTS", 200)
SUBPROCESS_TIMEOUT_SEC = _get_env_int("SUBPROCESS_TIMEOUT_SEC", 5)
RUN_COMMAND_MAX_TIMEOUT_SEC = _get_env_int("RUN_COMMAND_MAX_TIMEOUT_SEC", 30)
RUN_COMMAND_MAX_OUTPUT_CHARS = _get_env_int("RUN_COMMAND_MAX_OUTPUT_CHARS", 40_000)

# Docker integration is optional in host-native mode. Docker tools use the host
# Docker CLI and respect DOCKER_HOST when it is set by the user/environment.
DOCKER_HOST = os.environ.get("DOCKER_HOST")

# Optional safety limits for docker commands.
DOCKER_COMMAND_TIMEOUT_SEC = _get_env_int("DOCKER_COMMAND_TIMEOUT_SEC", 120)

MAX_FILE_SIZE_BYTES = _get_env_int("MAX_FILE_SIZE_BYTES", 1_000_000)
