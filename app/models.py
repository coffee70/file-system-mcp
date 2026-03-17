from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ListDirRequest(BaseModel):
    path: str = Field(default=".")
    max_entries: int = Field(default=200, ge=1, le=1000)


class DirEntry(BaseModel):
    name: str
    type: str  # "file" | "dir"
    size: Optional[int] = None


class ListDirResponse(BaseModel):
    path: str
    entries: List[DirEntry]


class ReadFileRequest(BaseModel):
    path: str
    start_line: int = Field(default=1, ge=1)
    end_line: Optional[int] = Field(default=None, ge=1)


class ReadFileResponse(BaseModel):
    path: str
    start_line: int
    end_line: int
    content: str


class ReadFilesRequest(BaseModel):
    paths: List[str]


class FileContent(BaseModel):
    path: str
    content: str


class ReadFilesResponse(BaseModel):
    files: List[FileContent]


class RipgrepSearchRequest(BaseModel):
    query: str
    path: str = "."
    glob: Optional[str] = None
    context_lines: int = Field(default=0, ge=0, le=10)
    max_results: int = Field(default=100, ge=1, le=1000)


class SearchMatch(BaseModel):
    path: str
    line: int
    column: int
    snippet: str


class RipgrepSearchResponse(BaseModel):
    matches: List[SearchMatch]


class AstGrepSearchRequest(BaseModel):
    pattern: str
    language: str
    path: str = "."
    max_results: int = Field(default=100, ge=1, le=1000)


class AstGrepSearchResponse(BaseModel):
    matches: List[SearchMatch]


class ProposePatchRequest(BaseModel):
    path: str
    instruction: str


class ProposePatchResponse(BaseModel):
    path: str
    diff: str
    summary: str


class ApplyPatchRequest(BaseModel):
    path: str
    diff: str


class ApplyPatchResponse(BaseModel):
    path: str
    applied: bool


class GitCommandRequest(BaseModel):
    command: str
    args: Optional[List[str]] = None


class GitCommandResponse(BaseModel):
    command: str
    returncode: int
    stdout: str
    stderr: str


class RepoMapDirSummary(BaseModel):
    kind: str
    children: List[str]


class GetRepoMapRequest(BaseModel):
    path: str = Field(default=".")
    max_depth: int = Field(default=2, ge=0, le=8)
    max_entries_per_dir: int = Field(default=20, ge=1, le=200)


class GetRepoMapResponse(BaseModel):
    root: str
    languages: List[str]
    frameworks: List[str]
    entrypoints: List[str]
    tests: List[str]
    configs: List[str]
    important_files: List[str]
    top_level_dirs: Dict[str, RepoMapDirSummary]
    summary: str