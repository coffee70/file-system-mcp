from pathlib import Path

from ..models import AstGrepSearchRequest, AstGrepSearchResponse, SearchMatch
from ..adapters.ast_grep import run_ast_grep
from ..security import resolve_user_path
from ..config import MAX_RESULTS


def handle_ast_grep_search(req: AstGrepSearchRequest) -> AstGrepSearchResponse:
    search_root = resolve_user_path(req.path)

    max_results = min(req.max_results, MAX_RESULTS)

    result = run_ast_grep(
        pattern=req.pattern,
        language=req.language,
        cwd=Path(search_root),
        max_results=max_results,
    )

    matches = [
        SearchMatch(
            path=m["path"],
            line=m["line"],
            column=m["column"],
            snippet=m["snippet"],
        )
        for m in result["matches"]
    ]

    return AstGrepSearchResponse(matches=matches)