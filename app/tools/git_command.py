from ..models import GitCommandRequest, GitCommandResponse
from ..adapters.git import run_git


def handle_git_command(req: GitCommandRequest) -> GitCommandResponse:
    result = run_git(req.command, req.args)

    return GitCommandResponse(
        command=result["command"],
        returncode=result["returncode"],
        stdout=result["stdout"],
        stderr=result["stderr"],
    )
