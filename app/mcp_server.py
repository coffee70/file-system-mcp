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


mcp = FastMCP(
    "MCP Code Assistant",
    json_response=True,
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)


@mcp.tool()
def list_dir(path: str = ".", max_entries: int = 200) -> dict:
    """List files and directories under a path within the configured workspace root."""
    req = ListDirRequest(path=path, max_entries=max_entries)
    result = handle_list_dir(req)
    return result.model_dump()


@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int | None = None) -> dict:
    """Read a text file from the configured workspace root."""
    req = ReadFileRequest(path=path, start_line=start_line, end_line=end_line)
    result = handle_read_file(req)
    return result.model_dump()


@mcp.tool()
def read_files(paths: list[str]) -> dict:
    """Read multiple text files from the configured workspace root."""
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
    """Search repository text using ripgrep."""
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
    """Search repository code structure using ast-grep."""
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
    """Propose a patch for a file and return a unified diff."""
    req = ProposePatchRequest(path=path, instruction=instruction)
    result = handle_propose_patch(req)
    return result.model_dump()


@mcp.tool()
def apply_patch(path: str, diff: str) -> dict:
    """Apply a unified diff patch to a file when writes are enabled."""
    req = ApplyPatchRequest(path=path, diff=diff)
    result = handle_apply_patch(req)
    return result.model_dump()

@mcp.tool()
def git_command(command: str, args: list[str] | None = None) -> dict:
    """Run a git command inside the workspace repository."""
    req = GitCommandRequest(command=command, args=args)
    result = handle_git_command(req)
    return result.model_dump()

@mcp.tool()
def get_repo_map(
    path: str = ".",
    max_depth: int = 2,
    max_entries_per_dir: int = 20,
) -> dict:
    """Return a compact architectural map of the repository."""
    req = GetRepoMapRequest(
        path=path,
        max_depth=max_depth,
        max_entries_per_dir=max_entries_per_dir,
    )
    result = handle_get_repo_map(req)
    return result.model_dump()