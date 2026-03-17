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
    req = ListDirRequest(path=path, max_entries=max_entries)
    result = handle_list_dir(req)
    return result.model_dump()


@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> dict:
    req = ReadFileRequest(path=path, start_line=start_line, end_line=end_line)
    result = handle_read_file(req)
    return result.model_dump()


@mcp.tool()
def read_files(paths: list[str]) -> dict:
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
    req = ProposePatchRequest(path=path, instruction=instruction)
    result = handle_propose_patch(req)
    return result.model_dump()


@mcp.tool()
def apply_patch(path: str, diff: str) -> dict:
    req = ApplyPatchRequest(path=path, diff=diff)
    result = handle_apply_patch(req)
    return result.model_dump()


@mcp.tool()
def git_command(command: str, args: list[str] | None = None) -> dict:
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
    req = GetRepoMapRequest(
        path=path,
        max_depth=max_depth,
        max_entries_per_dir=max_entries_per_dir,
    )
    result = handle_get_repo_map(req)
    return result.model_dump()


@mcp.tool()
def write_file(path: str, content: str, create_dirs: bool = True) -> dict:
    req = WriteFileRequest(path=path, content=content, create_dirs=create_dirs)
    result = handle_write_file(req)
    return result.model_dump()


@mcp.tool()
def delete_file(path: str, missing_ok: bool = False) -> dict:
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
    req = CopyFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    result = handle_copy_file(req)
    return result.model_dump()


@mcp.tool()
def move_file(src: str, dst: str, overwrite: bool = False, create_dirs: bool = True) -> dict:
    req = MoveFileRequest(src=src, dst=dst, overwrite=overwrite, create_dirs=create_dirs)
    result = handle_move_file(req)
    return result.model_dump()
