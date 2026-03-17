from ..models import RunCommandRequest, RunCommandResponse
from ..adapters.run_command import run_command


def handle_run_command(req: RunCommandRequest) -> RunCommandResponse:
    result = run_command(
        command=req.command,
        args=req.args,
        cwd=req.cwd,
        timeout_seconds=req.timeout_seconds,
    )

    return RunCommandResponse(**result)
