from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from ..security import resolve_user_path


IGNORED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "mcp_code_assistant.egg-info",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".rb": "ruby",
    ".php": "php",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".toml": "toml",
}

SPECIAL_LANGUAGE_FILES = {
    "Makefile": "make",
}

CONFIG_FILE_NAMES = {
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "package.json",
    "package-lock.json",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    ".env",
    ".env.example",
    ".gitignore",
    "mypy.ini",
    "pytest.ini",
    "ruff.toml",
}

IMPORTANT_FILE_NAMES = {
    "README.md",
    "README.rst",
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "Makefile",
    ".env.example",
    "mcp_server.py",
}

ENTRYPOINT_FILE_NAMES = {
    "main.py",
    "app.py",
    "manage.py",
    "index.js",
    "index.ts",
}

FRAMEWORK_DEPENDENCY_MAP = {
    "fastapi": "fastapi",
    "flask": "flask",
    "django": "django",
    "starlette": "starlette",
    "pytest": "pytest",
    "pydantic": "pydantic",
    "uvicorn": "uvicorn",
    "typer": "typer",
    "click": "click",
    "mcp": "mcp",
}


def _path_depth(rel_path: Path) -> int:
    return len(rel_path.parts)


def _should_ignore_dir(name: str) -> bool:
    return name in IGNORED_DIR_NAMES


def _detect_language(path: Path) -> str | None:
    if path.name in SPECIAL_LANGUAGE_FILES:
        return SPECIAL_LANGUAGE_FILES[path.name]
    return LANGUAGE_BY_SUFFIX.get(path.suffix.lower())


def _is_config_file(path: Path) -> bool:
    return path.name in CONFIG_FILE_NAMES


def _is_test_path(path: Path) -> bool:
    parts = set(path.parts)
    name = path.name
    return (
        "tests" in parts
        or "__tests__" in parts
        or name.startswith("test_")
        or name.endswith("_test.py")
        or name.endswith(".spec.ts")
        or name.endswith(".spec.js")
    )


def _is_important_file(path: Path) -> bool:
    if path.name in IMPORTANT_FILE_NAMES:
        return True
    return path.as_posix() in {"app/main.py", "app/mcp_server.py", "src/main.py", "main.py"}


def _read_text_preview(path: Path, limit: int = 4000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except Exception:
        return ""


def _is_entrypoint_candidate(path: Path, full_path: Path) -> bool:
    posix_path = path.as_posix()

    if path.name in ENTRYPOINT_FILE_NAMES:
        return True

    if posix_path in {"app/main.py", "app/mcp_server.py", "src/main.py"}:
        return True

    if path.parts and path.parts[0] == "scripts":
        return True

    if path.suffix == ".py":
        preview = _read_text_preview(full_path)
        if (
            "if __name__ == \"__main__\":" in preview
            or "if __name__ == '__main__':" in preview
            or "FastAPI(" in preview
            or "uvicorn.run(" in preview
            or "FastMCP(" in preview
        ):
            return True

    return False


def _classify_top_level_dir(name: str) -> str:
    if name in {"tests", "__tests__"}:
        return "tests"
    if name in {"scripts", "bin"}:
        return "scripts"
    if name in {"docs", "documentation"}:
        return "docs"
    if name in {"infra", "ops", "deploy", ".github"}:
        return "infra"
    if name in {"app", "src", "lib"}:
        return "source"
    return "source"


def _collect_frameworks(root: Path) -> list[str]:
    frameworks: set[str] = set()

    pyproject_path = root / "pyproject.toml"
    if pyproject_path.exists():
        try:
            data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            project = data.get("project", {})
            dependencies = project.get("dependencies", [])
            optional = project.get("optional-dependencies", {})
            all_deps = list(dependencies)
            for values in optional.values():
                all_deps.extend(values)

            dep_text = " ".join(str(dep).lower() for dep in all_deps)
            for dep_name, framework_name in FRAMEWORK_DEPENDENCY_MAP.items():
                if dep_name in dep_text:
                    frameworks.add(framework_name)
        except Exception:
            pass

    likely_files = [
        root / "app" / "main.py",
        root / "app" / "mcp_server.py",
        root / "main.py",
    ]
    for file_path in likely_files:
        if not file_path.exists():
            continue
        preview = _read_text_preview(file_path).lower()
        if "fastmcp(" in preview or "from mcp.server" in preview:
            frameworks.add("mcp")
        if "fastapi(" in preview or "from fastapi" in preview:
            frameworks.add("fastapi")
        if "import pytest" in preview or "from pytest" in preview:
            frameworks.add("pytest")

    return sorted(frameworks)


def _build_top_level_dirs(root: Path, max_entries_per_dir: int) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}

    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        if _should_ignore_dir(child.name):
            continue

        children: list[str] = []
        try:
            for nested in sorted(child.iterdir(), key=lambda p: p.name)[:max_entries_per_dir]:
                children.append(nested.name)
        except Exception:
            children = []

        result[child.name] = {
            "kind": _classify_top_level_dir(child.name),
            "children": children,
        }

    return result


def _build_summary(languages: list[str], frameworks: list[str], entrypoints: list[str]) -> str:
    language_part = ", ".join(languages) if languages else "unknown-language"
    framework_part = ", ".join(frameworks) if frameworks else "no obvious framework"
    entrypoint_part = ", ".join(entrypoints[:3]) if entrypoints else "no obvious entrypoints"
    return (
        f"Repository appears to use {language_part}. "
        f"Detected frameworks/tools: {framework_part}. "
        f"Likely entrypoints include: {entrypoint_part}."
    )


def build_repo_map(
    path: str = ".",
    max_depth: int = 2,
    max_entries_per_dir: int = 20,
) -> dict[str, Any]:
    root = resolve_user_path(path)

    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    languages: set[str] = set()
    configs: set[str] = set()
    tests: set[str] = set()
    entrypoints: set[str] = set()
    important_files: set[str] = set()

    for current_root, dirs, files in os.walk(root):
        current_path = Path(current_root)
        rel_dir = current_path.relative_to(root)

        dirs[:] = [d for d in dirs if not _should_ignore_dir(d)]

        current_depth = _path_depth(rel_dir)
        if current_depth >= max_depth:
            dirs[:] = []

        for file_name in files:
            rel_path = (rel_dir / file_name) if rel_dir != Path(".") else Path(file_name)

            if _path_depth(rel_path) > max_depth:
                continue

            full_path = current_path / file_name

            language = _detect_language(rel_path)
            if language:
                languages.add(language)

            if _is_config_file(rel_path):
                configs.add(rel_path.as_posix())

            if _is_test_path(rel_path):
                if rel_path.parts and rel_path.parts[0] == "tests":
                    tests.add("tests/")
                else:
                    tests.add(rel_path.as_posix())

            if _is_important_file(rel_path):
                important_files.add(rel_path.as_posix())

            if _is_entrypoint_candidate(rel_path, full_path):
                entrypoints.add(rel_path.as_posix())

    frameworks = _collect_frameworks(root)
    top_level_dirs = _build_top_level_dirs(root, max_entries_per_dir)

    languages_list = sorted(languages)
    entrypoints_list = sorted(entrypoints)
    tests_list = sorted(tests)
    configs_list = sorted(configs)
    important_files_list = sorted(important_files)

    return {
        "root": path,
        "languages": languages_list,
        "frameworks": frameworks,
        "entrypoints": entrypoints_list,
        "tests": tests_list,
        "configs": configs_list,
        "important_files": important_files_list,
        "top_level_dirs": top_level_dirs,
        "summary": _build_summary(languages_list, frameworks, entrypoints_list),
    }
