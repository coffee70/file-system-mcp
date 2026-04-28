from ..adapters import host_inspect as adapter


def handle_host_ps(timeout_seconds: int | None = None):
    return adapter.host_ps(timeout_seconds)


def handle_host_env(timeout_seconds: int | None = None):
    return adapter.host_env(timeout_seconds)


def handle_host_ls(path: str = ".", long: bool = True, all: bool = True, timeout_seconds: int | None = None):
    return adapter.host_ls(path, long, all, timeout_seconds)


def handle_host_df(timeout_seconds: int | None = None):
    return adapter.host_df(timeout_seconds)


def handle_host_ports(timeout_seconds: int | None = None):
    return adapter.host_ports(timeout_seconds)


def handle_host_tail(path: str, lines: int = 100, timeout_seconds: int | None = None):
    return adapter.host_tail(path, lines, timeout_seconds)
