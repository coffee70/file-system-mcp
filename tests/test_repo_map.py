from app.adapters.repo_map import build_repo_map


def test_build_repo_map_for_repo_root():
    result = build_repo_map(".", max_depth=2, max_entries_per_dir=20)

    assert result["root"] == "."
    assert "python" in result["languages"]
    assert "pyproject.toml" in result["configs"]
    assert "README.md" in result["important_files"]
    assert "tests/" in result["tests"]
    assert "app" in result["top_level_dirs"]
    assert "tests" in result["top_level_dirs"]
    assert isinstance(result["summary"], str)
    assert result["summary"]


def test_build_repo_map_detects_entrypoints():
    result = build_repo_map(".", max_depth=2, max_entries_per_dir=20)

    assert "app/main.py" in result["entrypoints"]
    assert "Dockerfile" in result["entrypoints"]