from ..models import ReadFilesRequest, ReadFilesResponse, FileContent
from ..adapters.filesystem import read_multiple_files


def handle_read_files(req: ReadFilesRequest) -> ReadFilesResponse:
    results = read_multiple_files(req.paths)

    files = [
        FileContent(
            path=item["path"],
            content=item["content"],
        )
        for item in results
    ]

    return ReadFilesResponse(files=files)