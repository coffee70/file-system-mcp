from ..adapters import docker_exec as adapter


def handle_docker_exec_ps(container: str, args: list[str] | None = None, timeout_seconds: int | None = None):
    return adapter.docker_exec_ps(container, args, timeout_seconds)


def handle_docker_exec_env(container: str, timeout_seconds: int | None = None):
    return adapter.docker_exec_env(container, timeout_seconds)


def handle_docker_exec_ls(container: str, path: str = ".", args: list[str] | None = None, timeout_seconds: int | None = None):
    return adapter.docker_exec_ls(container, path, args, timeout_seconds)


def handle_docker_exec_cat(container: str, path: str, timeout_seconds: int | None = None):
    return adapter.docker_exec_cat(container, path, timeout_seconds)


def handle_docker_exec_http_probe(container: str, url: str, timeout_seconds: int | None = None):
    return adapter.docker_exec_http_probe(container, url, timeout_seconds)


def handle_docker_exec_python_module(container: str, module: str, args: list[str] | None = None, timeout_seconds: int | None = None):
    return adapter.docker_exec_python_module(container, module, args, timeout_seconds)


def handle_docker_exec_node(container: str, args: list[str] | None = None, timeout_seconds: int | None = None):
    return adapter.docker_exec_node(container, args, timeout_seconds)
