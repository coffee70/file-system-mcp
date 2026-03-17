from ..models import ListDirRequest, ListDirResponse, DirEntry
from ..adapters.filesystem import list_dir as fs_list_dir


def handle_list_dir(req: ListDirRequest) -> ListDirResponse:
    result = fs_list_dir(req.path, req.max_entries)

    entries = [
        DirEntry(
            name=e["name"],
            type=e["type"],
            size=e.get("size"),
        )
        for e in result["entries"]
    ]

    return ListDirResponse(
        path=result["path"],
        entries=entries,
    )