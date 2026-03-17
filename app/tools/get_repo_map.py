from ..adapters.repo_map import build_repo_map
from ..models import GetRepoMapRequest, GetRepoMapResponse, RepoMapDirSummary


def handle_get_repo_map(req: GetRepoMapRequest) -> GetRepoMapResponse:
    result = build_repo_map(
        path=req.path,
        max_depth=req.max_depth,
        max_entries_per_dir=req.max_entries_per_dir,
    )

    top_level_dirs = {
        name: RepoMapDirSummary(
            kind=value["kind"],
            children=value["children"],
        )
        for name, value in result["top_level_dirs"].items()
    }

    return GetRepoMapResponse(
        root=result["root"],
        languages=result["languages"],
        frameworks=result["frameworks"],
        entrypoints=result["entrypoints"],
        tests=result["tests"],
        configs=result["configs"],
        important_files=result["important_files"],
        top_level_dirs=top_level_dirs,
        summary=result["summary"],
    )