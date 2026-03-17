from pathlib import Path

from ..models import RipgrepSearchRequest, RipgrepSearchResponse, SearchMatch
from ..adapters.rg import run_rg
from ..security import resolve_user_path
from ..config import MAX_RESULTS


def handle_ripgrep_search(req: RipgrepSearchRequest) -> RipgrepSearchResponse:
    search_root = resolve_user_path(req.path)

    max_results = min(req.max_results, MAX_RESULTS)

    result = run_rg(
        query=req.query,
        cwd=Path(search_root),
        glob=req.glob,
        max_results=max_results,
        context_lines=req.context_lines,
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

    return RipgrepSearchResponse(matches=matches)