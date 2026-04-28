from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from .models import (
    ListDirRequest,
    ReadFileRequest,
    ReadFilesRequest,
    RipgrepSearchRequest,
    AstGrepSearchRequest,
    ProposePatchRequest,
    ApplyPatchRequest,
    GitCommandRequest,
    GetRepoMapRequest,
    WriteFileRequest,
    DeleteFileRequest,
    CopyFileRequest,
    MoveFileRequest,
    DeleteDirRequest,
    RunCommandRequest,
)
from .tools.list_dir import handle_list_dir
from .tools.read_file import handle_read_file
from .tools.read_files import handle_read_files
from .tools.ripgrep_search import handle_ripgrep_search
from .tools.ast_grep_search import handle_ast_grep_search
from .tools.propose_patch import handle_propose_patch
from .tools.apply_patch import handle_apply_patch
from .tools.git_command import handle_git_command
from .tools.get_repo_map import handle_get_repo_map
from .tools.write_file import handle_write_file
from .tools.delete_file import handle_delete_file
from .tools.copy_file import handle_copy_file
from .tools.move_file import handle_move_file
from .tools.delete_dir import handle_delete_dir
from .tools.run_command import handle_run_command
from .tools.docker_exec import (
    handle_docker_exec_ps,
    handle_docker_exec_env,
    handle_docker_exec_ls,
    handle_docker_exec_cat,
    handle_docker_exec_http_probe,
    handle_docker_exec_python_module,
    handle_docker_exec_node,
)
from .tools.host_inspect import (
    handle_host_ps,
    handle_host_env,
    handle_host_ls,
    handle_host_df,
    handle_host_ports,
    handle_host_tail,
)


mcp = FastMCP(
    "MCP Code Assistant",
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


# -----------------------------
# Host inspection tools
# -----------------------------

@mcp.tool()
def host_ps(timeout_seconds: int | None = None) -> dict:
    """List processes visible to the MCP runtime using `ps aux`.

    Use this to look for long-running processes, crashed process supervisors,
    local servers, or suspicious process state while debugging a stack. In a
    containerized MCP deployment, this reflects the MCP container's process
    namespace unless the container is started with host PID access.

    Args:
        timeout_seconds: Optional timeout for the process listing. The server
            caps this at its configured maximum.
    """
    return handle_host_ps(timeout_seconds)


@mcp.tool()
def host_env(timeout_seconds: int | None = None) -> dict:
    """Inspect environment variables visible to the MCP runtime.

    Sensitive-looking values are redacted by key name, including tokens,
    passwords, API keys, credentials, auth headers, cookies, and private keys.
    Use this to confirm runtime configuration such as WORKSPACE_ROOT,
    DOCKER_HOST, PATH, or feature flags without exposing secrets.

    Args:
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_host_env(timeout_seconds)


@mcp.tool()
def host_ls(
    path: str = ".",
    long: bool = True,
    all: bool = True,
    timeout_seconds: int | None = None,
) -> dict:
    """List files on the host filesystem, scoped to the workspace root.

    Use this for safe host-side filesystem inspection when debugging mounted
    files, generated logs, build artifacts, or volume-backed project files. The
    path is resolved relative to WORKSPACE_ROOT and cannot escape it.

    Examples:
        host_ls(path=".")
        host_ls(path="logs", long=True, all=False)

    Args:
        path: Directory or file path relative to the workspace root.
        long: Include long `ls -l` details when true.
        all: Include dotfiles with `ls -a` when true.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_host_ls(path, long, all, timeout_seconds)


@mcp.tool()
def host_df(timeout_seconds: int | None = None) -> dict:
    """Show disk usage for the filesystem containing the workspace.

    Use this to diagnose disk-full or low-space failures that can break Docker
    builds, databases, package installs, or log writes.

    Args:
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_host_df(timeout_seconds)


@mcp.tool()
def host_ports(timeout_seconds: int | None = None) -> dict:
    """List open TCP/UDP listeners visible to the MCP runtime.

    Use this to diagnose port binding conflicts, services that failed to bind,
    or whether an expected local service is listening. The adapter tries
    `ss -tulpn` and falls back to `netstat -tulpn` when `ss` is unavailable.
    In a containerized MCP deployment, this reflects the MCP network namespace
    unless the container is started with host networking.

    Args:
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_host_ports(timeout_seconds)


@mcp.tool()
def host_tail(path: str, lines: int = 100, timeout_seconds: int | None = None) -> dict:
    """Tail a file safely inside the workspace root.

    Use this to inspect recent host-side logs or generated files without reading
    an entire large file. The path is resolved relative to WORKSPACE_ROOT and
    cannot escape it.

    Examples:
        host_tail(path="logs/app.log", lines=200)

    Args:
        path: File path relative to the workspace root.
        lines: Number of trailing lines to read, between 1 and 1000.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_host_tail(path, lines, timeout_seconds)


# -----------------------------
# Docker exec tools
# -----------------------------

@mcp.tool()
def docker_exec_ps(
    container: str,
    args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    """List processes inside a Docker container with `docker exec <container> ps`.

    Use this while debugging containers to confirm the expected application,
    worker, or supervisor process is actually running. This wrapper avoids shell
    execution and passes arguments directly to `ps`.

    Examples:
        docker_exec_ps(container="api")
        docker_exec_ps(container="api", args=["aux"])

    Args:
        container: Docker container name or ID.
        args: Optional additional `ps` arguments as separate strings.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_ps(container, args, timeout_seconds)


@mcp.tool()
def docker_exec_env(container: str, timeout_seconds: int | None = None) -> dict:
    """Dump environment variables inside a Docker container with `env`.

    Use this to compare the container's runtime configuration against Docker
    Compose, `.env`, or application settings when debugging configuration or
    startup issues.

    Args:
        container: Docker container name or ID.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_env(container, timeout_seconds)


@mcp.tool()
def docker_exec_ls(
    container: str,
    path: str = ".",
    args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    """List files inside a Docker container with `docker exec <container> ls`.

    Use this to verify mounted volumes, generated files, installed artifacts,
    working directories, or config files inside a running container. The path is
    validated to avoid option injection.

    Examples:
        docker_exec_ls(container="api", path="/app")
        docker_exec_ls(container="api", path="/app", args=["-la"])

    Args:
        container: Docker container name or ID.
        path: Path inside the container to list.
        args: Optional additional `ls` arguments as separate strings.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_ls(container, path, args, timeout_seconds)


@mcp.tool()
def docker_exec_cat(container: str, path: str, timeout_seconds: int | None = None) -> dict:
    """Read a file inside a Docker container with `docker exec <container> cat`.

    Use this to inspect container-local config, generated files, lockfiles,
    logs, or mounted files when host-side code and container state disagree.
    The path is validated to avoid option injection.

    Args:
        container: Docker container name or ID.
        path: Path inside the container to read.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_cat(container, path, timeout_seconds)


@mcp.tool()
def docker_exec_http_probe(
    container: str,
    url: str,
    timeout_seconds: int | None = None,
) -> dict:
    """Run a curl-based HTTP probe from inside a Docker container.

    Use this to test service reachability from the container network namespace,
    such as health endpoints, service-to-service DNS names, or localhost inside
    the container. The URL must start with http:// or https:// and cannot contain
    whitespace.

    Examples:
        docker_exec_http_probe(container="api", url="http://localhost:8000/health")
        docker_exec_http_probe(container="worker", url="http://api:8000/health")

    Args:
        container: Docker container name or ID.
        url: HTTP or HTTPS URL to fetch from inside the container.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum and also passes it to curl as --max-time.
    """
    return handle_docker_exec_http_probe(container, url, timeout_seconds)


@mcp.tool()
def docker_exec_python_module(
    container: str,
    module: str,
    args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    """Run `python -m <module>` inside a Docker container.

    Use this for safe Python diagnostics that execute an installed module or
    checked-in module path without shell interpolation. The module name must be
    a valid dotted Python module name.

    Examples:
        docker_exec_python_module(container="api", module="pytest", args=["-q"])
        docker_exec_python_module(container="api", module="app.healthcheck")

    Args:
        container: Docker container name or ID.
        module: Dotted Python module name to run.
        args: Optional module arguments as separate strings.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_python_module(container, module, args, timeout_seconds)


@mcp.tool()
def docker_exec_node(
    container: str,
    args: list[str] | None = None,
    timeout_seconds: int | None = None,
) -> dict:
    """Run a Node command inside a Docker container using a safe subset.

    Use this to execute checked-in Node scripts or inspect Node runtime behavior
    inside a container. Inline code execution with `node -e` is blocked; prefer
    running a script file or module that exists in the container.

    Examples:
        docker_exec_node(container="web", args=["--version"])
        docker_exec_node(container="web", args=["scripts/diagnose.js"])

    Args:
        container: Docker container name or ID.
        args: Node arguments as separate strings. `-e` is not allowed.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    return handle_docker_exec_node(container, args, timeout_seconds)


# -----------------------------
# Core tools
# -----------------------------

@mcp.tool()
def list_dir(path: str = ".", max_entries: int = 200) -> dict:
    """List files and directories under a workspace path.

    Use this to inspect folder contents before reading, editing, copying,
    moving, or deleting files. Paths are relative to the workspace root and are
    validated by the underlying adapter.

    Args:
        path: Directory to inspect, relative to the workspace root.
        max_entries: Maximum number of entries to include in the response.
    """
    req = ListDirRequest(path=path, max_entries=max_entries)
    return handle_list_dir(req).model_dump()


@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> dict:
    """Read a file from the workspace, optionally limited to a line range.

    Use this to inspect source code, configuration, documentation, logs, or test
    fixtures without opening the entire file. Prefer line ranges for large files
    once you know the relevant area.

    Examples:
        read_file(path="app/main.py")
        read_file(path="app/main.py", start_line=50, end_line=120)

    Args:
        path: File path relative to the workspace root.
        start_line: First line number to include, starting at 1.
        end_line: Last line number to include. Omit to read to the end.
    """
    req = ReadFileRequest(path=path, start_line=start_line, end_line=end_line)
    return handle_read_file(req).model_dump()


@mcp.tool()
def read_files(paths: list[str]) -> dict:
    """Read multiple workspace files in one request.

    Use this when comparing related files or gathering context across several
    small files, such as a route, service, model, and test. For very large files,
    use read_file with line ranges instead.

    Args:
        paths: File paths relative to the workspace root.
    """
    req = ReadFilesRequest(paths=paths)
    return handle_read_files(req).model_dump()


@mcp.tool()
def ripgrep_search(
    query: str,
    path: str = ".",
    glob: str | None = None,
    context_lines: int = 0,
    max_results: int = 100,
) -> dict:
    """Search file contents using ripgrep.

    Use this for fast text or regex search across many files in the workspace.
    It is the best first tool for finding symbols, log messages, config keys,
    TODOs, stack-trace text, or references to a failing endpoint.

    Examples:
        ripgrep_search(query="DATABASE_URL")
        ripgrep_search(query="def health", glob="*.py", context_lines=2)

    Args:
        query: Text or regex pattern to search for.
        path: Directory to search, relative to the workspace root.
        glob: Optional file filter such as '*.py' or 'src/**/*.ts'.
        context_lines: Number of surrounding lines to include around each match.
        max_results: Maximum number of matches to return.
    """
    req = RipgrepSearchRequest(
        query=query,
        path=path,
        glob=glob,
        context_lines=context_lines,
        max_results=max_results,
    )
    return handle_ripgrep_search(req).model_dump()


@mcp.tool()
def ast_grep_search(
    pattern: str,
    language: str,
    path: str = ".",
    max_results: int = 100,
) -> dict:
    """Search source code structurally using ast-grep.

    Use this when syntax-aware matching is more reliable than plain text search,
    such as finding function definitions, import forms, decorators, call sites,
    or language-specific constructs.

    Examples:
        ast_grep_search(pattern="def $FUNC($$$ARGS): $$$BODY", language="python")
        ast_grep_search(pattern="import $X from '$Y'", language="typescript")

    Args:
        pattern: AST-grep pattern to match.
        language: Source language to parse, such as 'python' or 'typescript'.
        path: Directory to search, relative to the workspace root.
        max_results: Maximum number of matches to return.
    """
    req = AstGrepSearchRequest(pattern=pattern, language=language, path=path, max_results=max_results)
    return handle_ast_grep_search(req).model_dump()


@mcp.tool()
def propose_patch(path: str, instruction: str) -> dict:
    """Generate a proposed patch for a file from a natural-language change request.

    Use this when you want a suggested diff before applying edits manually. For
    reliable edits, the recommended workflow is still to read the file, generate
    the full updated content, and write it with write_file.

    Args:
        path: File path to modify, relative to the workspace root.
        instruction: Description of the requested code or text change.
    """
    req = ProposePatchRequest(path=path, instruction=instruction)
    return handle_propose_patch(req).model_dump()


@mcp.tool()
def apply_patch(path: str, diff: str) -> dict:
    """Apply a unified diff patch to a workspace file.

    Use this to make exact, controlled edits when you already have a unified
    diff. Prefer write_file for larger generated replacements.

    Args:
        path: File path that the diff should be applied to.
        diff: Unified diff content.
    """
    req = ApplyPatchRequest(path=path, diff=diff)
    return handle_apply_patch(req).model_dump()


@mcp.tool()
def git_command(command: str, args: list[str] | None = None) -> dict:
    """Run a git subcommand inside the workspace repository.

    Use this for repository inspection tasks such as status, diff, log, branch,
    show, or blame workflows. This is intended for git operations only; use
    run_command for project commands and the dedicated Docker/host wrappers for
    diagnostics.

    Examples:
        git_command(command="status")
        git_command(command="diff", args=["--", "app/main.py"])

    Args:
        command: Git subcommand such as 'status', 'diff', or 'log'.
        args: Additional arguments to pass to git.
    """
    req = GitCommandRequest(command=command, args=args)
    return handle_git_command(req).model_dump()


@mcp.tool()
def run_command(
    command: str,
    args: list[str] | None = None,
    cwd: str = ".",
    timeout_seconds: int | None = None,
) -> dict:
    """Run an allowlisted command in the workspace.

    Use this for project-specific tasks such as running tests, linters, builds,
    package-manager scripts, git inspection, and Docker/Docker Compose
    operations. Pass the executable name in `command` and every flag/subcommand
    as separate strings in `args`; do not combine the whole command line into
    one string. For example, use `command="echo", args=["hello"]`, not
    `command="echo hello"`.

    Allowed commands are: cat, docker, docker-compose, echo, find, grep, head,
    ls, mkdir, node, pwd, python, python3, pytest, npm, npx, pnpm, yarn, uv,
    poetry, pipenv, ruff, mypy, rg, git, sed, tail, touch, and which.

    Docker policy: `docker` supports version, info, ps, images, logs, inspect,
    exec, cp, port, stats, top, events, network, volume, and compose. For
    `docker compose` and `docker-compose`, allowed subcommands are version, ls,
    ps, logs, config, up, down, restart, start, stop, exec, run, pull, and build.
    Docker network and volume are limited to ls and inspect.

    Package-manager policy: npm and pnpm are limited to test, run, exec, and ls;
    yarn is limited to test, run, exec, and list; npx must include --no-install;
    uv is limited to run and tool; poetry is limited to run and show; pipenv is
    limited to run and graph.

    Examples:
        run_command(command="pytest", args=["-q"])
        run_command(command="docker", args=["compose", "ps"])
        run_command(command="npm", args=["run", "build"], cwd="web")

    Args:
        command: Allowlisted executable name to run, such as 'pytest', 'npm',
            'docker', or 'docker-compose'.
        args: Positional arguments, flags, and subcommands as separate strings.
        cwd: Working directory, relative to the workspace root. It must stay
            inside the workspace.
        timeout_seconds: Optional timeout. The server caps this at its
            configured maximum.
    """
    req = RunCommandRequest(command=command, args=args or [], cwd=cwd, timeout_seconds=timeout_seconds)
    return handle_run_command(req).model_dump()


@mcp.tool()
def get_repo_map(path: str = ".", max_depth: int = 2, max_entries_per_dir: int = 20) -> dict:
    """Generate a summarized map of the repository structure.

    Use this to quickly understand project layout, key directories, detected
    languages/frameworks, likely entrypoints, tests, configs, and important
    files before deeper inspection.

    Args:
        path: Root directory to analyze, relative to the workspace root.
        max_depth: Maximum directory depth to traverse.
        max_entries_per_dir: Maximum entries to include per directory.
    """
    req = GetRepoMapRequest(path=path, max_depth=max_depth, max_entries_per_dir=max_entries_per_dir)
    return handle_get_repo_map(req).model_dump()


@mcp.tool()
def write_file(path: str, content: str, create_dirs: bool = True) -> dict:
    """Create or overwrite a file in the workspace.

    Use this to save generated code, configuration, documentation, fixtures, or
    tests. For reliable edits, read the file first, produce the full updated
    content, then write the complete file.

    Args:
        path: Destination file path, relative to the workspace root.
        content: Full file contents to write.
        create_dirs: Whether to create missing parent directories automatically.
    """
    req = WriteFileRequest(path=path, content=content, create_dirs=create_dirs)
    return handle_write_file(req).model_dump()


@mcp.tool()
def delete_file(path: str, missing_ok: bool = False) -> dict:
    """Delete a file from the workspace.

    Use this for cleanup tasks or when replacing generated files. The underlying
    tool validates paths, respects the workspace root, and returns metadata about
    the removed file.

    Args:
        path: File path to remove, relative to the workspace root.
        missing_ok: Whether to succeed when the file does not exist.
    """
    req = DeleteFileRequest(path=path, missing_ok=missing_ok)
    return handle_delete_file(req).model_dump()


@mcp.tool()
def delete_dir(
    path: str,
    recursive: bool = False,
    missing_ok: bool = False,
    max_depth: int = 3,
) -> dict:
    """Delete a directory from the workspace.

    Use this for cleanup of generated folders or safe directory removal. The
    tool validates paths, respects the workspace root, and limits recursive
    deletion depth.

    Args:
        path: Directory path to remove, relative to the workspace root.
        recursive: Whether to remove non-empty directories recursively.
        missing_ok: Whether to succeed when the directory does not exist.
        max_depth: Safety limit for recursive deletion depth.
    """
    req = DeleteDirRequest(path=path, recursive=recursive, missing_ok=missing_ok, max_depth=max_depth)
    return handle_delete_dir(req).model_dump()


@mcp.tool()
def copy_file(src: str, dst: str, overwrite: bool = False, create_dirs: bool = True) -> dict:
    """Copy a file within the workspace.

    Use this to duplicate templates, fixtures, configuration files, or source
    files while preserving the original.

    Args:
        src: Source file path, relative to the workspace root.
        dst: Destination file path, relative to the workspace root.
        overwrite: Whether to replace an existing destination file.
        create_dirs: Whether to create missing parent directories for the destination.
    """
    req = CopyFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    return handle_copy_file(req).model_dump()


@mcp.tool()
def move_file(src: str, dst: str, overwrite: bool = False, create_dirs: bool = True) -> dict:
    """Move or rename a file within the workspace.

    Use this to reorganize files, rename generated outputs, or relocate source,
    config, or fixture files.

    Args:
        src: Source file path, relative to the workspace root.
        dst: Destination file path, relative to the workspace root.
        overwrite: Whether to replace an existing destination file.
        create_dirs: Whether to create missing parent directories for the destination.
    """
    req = MoveFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    return handle_move_file(req).model_dump()
