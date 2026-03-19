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


mcp = FastMCP(
    "MCP Code Assistant",
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


@mcp.tool()
def list_dir(path: str = ".", max_entries: int = 200) -> dict:
    """List files and directories under a workspace path.

    Use this to inspect the contents of a folder before reading, editing,
    copying, moving, or deleting files.

    Args:
        path: Directory to inspect, relative to the workspace root.
        max_entries: Maximum number of entries to include in the response.
    """
    req = ListDirRequest(path=path, max_entries=max_entries)
    result = handle_list_dir(req)
    return result.model_dump()


@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> dict:
    """Read a file from the workspace, optionally limited to a line range.

    Use this when you need to inspect source code, configuration, or text files
    without opening the entire file.

    Args:
        path: File path relative to the workspace root.
        start_line: First line number to include, starting at 1.
        end_line: Last line number to include. Omit to read to the end.
    """
    req = ReadFileRequest(path=path, start_line=start_line, end_line=end_line)
    result = handle_read_file(req)
    return result.model_dump()


@mcp.tool()
def read_files(paths: list[str]) -> dict:
    """Read multiple files from the workspace in one request.

    This is useful when comparing related files or gathering context across
    several small files.

    Args:
        paths: File paths relative to the workspace root.
    """
    req = ReadFilesRequest(paths=paths)
    result = handle_read_files(req)
    return result.model_dump()


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
    result = handle_ripgrep_search(req)
    return result.model_dump()


@mcp.tool()
def ast_grep_search(
    pattern: str,
    language: str,
    path: str = ".",
    max_results: int = 100,
) -> dict:
    """Search source code structurally using ast-grep.

    Use this when syntax-aware matching is more reliable than plain text search,
    such as finding function definitions, import forms, or language constructs.

    Args:
        pattern: AST-grep pattern to match.
        language: Source language to parse, such as 'python' or 'typescript'.
        path: Directory to search, relative to the workspace root.
        max_results: Maximum number of matches to return.
    """
    req = AstGrepSearchRequest(
        pattern=pattern,
        language=language,
        path=path,
        max_results=max_results,
    )
    result = handle_ast_grep_search(req)
    return result.model_dump()


@mcp.tool()
def propose_patch(path: str, instruction: str) -> dict:
    """Generate a proposed patch for a file from a natural-language change request.

    Use this when you want a suggested diff before applying edits manually.

    Args:
        path: File path to modify, relative to the workspace root.
        instruction: Description of the requested code or text change.
    """
    req = ProposePatchRequest(path=path, instruction=instruction)
    result = handle_propose_patch(req)
    return result.model_dump()


@mcp.tool()
def apply_patch(path: str, diff: str) -> dict:
    """Apply a unified diff patch to a file.

    Use this to make exact, controlled edits when you already have a patch.

    Args:
        path: File path that the diff should be applied to.
        diff: Unified diff content.
    """
    req = ApplyPatchRequest(path=path, diff=diff)
    result = handle_apply_patch(req)
    return result.model_dump()


@mcp.tool()
def git_command(command: str, args: list[str] | None = None) -> dict:
    """Run a git subcommand inside the workspace repository.

    Use this for repository inspection tasks such as status, diff, log, or
    branch-aware workflows.

    Args:
        command: Git subcommand such as 'status', 'diff', or 'log'.
        args: Additional arguments to pass to git.
    """
    req = GitCommandRequest(command=command, args=args)
    result = handle_git_command(req)
    return result.model_dump()


@mcp.tool()
def run_command(
    command: str,
    args: list[str] | None = None,
    cwd: str = ".",
    timeout_seconds: int | None = None,
) -> dict:
    """Run a command in the workspace.

    Use this for project-specific tasks such as running tests, linters, build
    commands, or small helper scripts.

    Args:
        command: Executable or command name to run.
        args: Positional arguments for the command.
        cwd: Working directory, relative to the workspace root.
        timeout_seconds: Optional timeout for command execution.
    """
    req = RunCommandRequest(
        command=command,
        args=args or [],
        cwd=cwd,
        timeout_seconds=timeout_seconds,
    )
    result = handle_run_command(req)
    return result.model_dump()


@mcp.tool()
def get_repo_map(
    path: str = ".",
    max_depth: int = 2,
    max_entries_per_dir: int = 20,
) -> dict:
    """Generate a summarized map of the repository structure.

    Use this to quickly understand the project layout, key directories, likely
    entrypoints, and important files before deeper inspection.

    Args:
        path: Root directory to analyze, relative to the workspace root.
        max_depth: Maximum directory depth to traverse.
        max_entries_per_dir: Maximum entries to include per directory.
    """
    req = GetRepoMapRequest(
        path=path,
        max_depth=max_depth,
        max_entries_per_dir=max_entries_per_dir,
    )
    result = handle_get_repo_map(req)
    return result.model_dump()


@mcp.tool()
def write_file(path: str, content: str, create_dirs: bool = True) -> dict:
    """Create or overwrite a file in the workspace.

    Use this to save generated code, configuration, documentation, or test data.

    Args:
        path: Destination file path, relative to the workspace root.
        content: Full file contents to write.
        create_dirs: Whether to create missing parent directories automatically.
    """
    req = WriteFileRequest(path=path, content=content, create_dirs=create_dirs)
    result = handle_write_file(req)
    return result.model_dump()


@mcp.tool()
def delete_file(path: str, missing_ok: bool = False) -> dict:
    """Delete a file from the workspace.

    Use this for cleanup tasks or when replacing files through other workflows.

    Args:
        path: File path to remove, relative to the workspace root.
        missing_ok: Whether to succeed when the file does not exist.
    """
    req = DeleteFileRequest(path=path, missing_ok=missing_ok)
    result = handle_delete_file(req)
    return result.model_dump()


@mcp.tool()
def delete_dir(
    path: str,
    recursive: bool = False,
    missing_ok: bool = False,
    max_depth: int = 3,
) -> dict:
    """Delete a directory from the workspace.

    Use this for cleanup of generated folders or safe directory removal.

    Args:
        path: Directory path to remove, relative to the workspace root.
        recursive: Whether to remove non-empty directories recursively.
        missing_ok: Whether to succeed when the directory does not exist.
        max_depth: Safety limit for recursive deletion depth.
    """
    req = DeleteDirRequest(
        path=path,
        recursive=recursive,
        missing_ok=missing_ok,
        max_depth=max_depth,
    )
    result = handle_delete_dir(req)
    return result.model_dump()


@mcp.tool()
def copy_file(src: str, dst: str, overwrite: bool = False, create_dirs: bool = True) -> dict:
    """Copy a file within the workspace.

    Use this to duplicate code, templates, fixtures, or configuration files.

    Args:
        src: Source file path, relative to the workspace root.
        dst: Destination file path, relative to the workspace root.
        overwrite: Whether to replace an existing destination file.
        create_dirs: Whether to create missing parent directories for the destination.
    """
    req = CopyFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    result = handle_copy_file(req)
    return result.model_dump()


@mcp.tool()
def move_file(src: str, dst: str, overwrite: bool = False, create_dirs: bool = True) -> dict:
    """Move or rename a file within the workspace.

    Use this to reorganize files, rename outputs, or relocate generated assets.

    Args:
        src: Source file path, relative to the workspace root.
        dst: Destination file path, relative to the workspace root.
        overwrite: Whether to replace an existing destination file.
        create_dirs: Whether to create missing parent directories for the destination.
    """
    req = MoveFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    result = handle_move_file(req)
    return result.model_dump()
