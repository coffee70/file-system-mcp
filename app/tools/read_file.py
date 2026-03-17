from ..models import ReadFileRequest, ReadFileResponse
from ..adapters.filesystem import read_file_lines
from ..config import MAX_READ_LINES


def handle_read_file(req: ReadFileRequest) -> ReadFileResponse:
    lines = read_file_lines(req.path)

    start = max(1, req.start_line)
    if start > len(lines):
        return ReadFileResponse(
            path=req.path,
            start_line=start,
            end_line=start,
            content=""
        )

    if req.end_line is None:
        end = min(len(lines), start + MAX_READ_LINES - 1)
    else:
        end = min(len(lines), req.end_line)

    if end - start + 1 > MAX_READ_LINES:
        end = start + MAX_READ_LINES - 1

    content = "\n".join(lines[start - 1:end])

    return ReadFileResponse(
        path=req.path,
        start_line=start,
        end_line=end,
        content=content,
    )