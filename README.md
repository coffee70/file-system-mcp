# MCP Code Assistant (Host-Native)

A host-native MCP server that runs directly on your machine and exposes safe, structured tools for interacting with your codebase and development environment.

## Key Architecture

This server runs **directly on the host (Codex-style)**:

- Full access to host filesystem (workspace-scoped)
- Access to host processes (`ps`)
- Access to host networking (`ss`, `netstat`)
- Uses host-installed binaries (git, rg, pytest, etc.)
- Optional access to Docker via host CLI

There is **no container boundary**. Safety is enforced in code.

---

## Requirements

Install the following on your host:

- Python 3.11+
- ripgrep (`rg`)
- ast-grep
- git
- Optional: Docker (for docker tools)

System utilities required:

- ps
- ss or netstat
- df
- tail

Example (macOS):

```bash
brew install ripgrep ast-grep
```

---

## Running the Server

### Option 1 — Helper script

```bash
bash scripts/run_local.sh
```

### Option 2 — Direct

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Server:

```
http://localhost:8000
```

MCP endpoint:

```
http://localhost:8000/mcp
```

---

## Safety Model

Since this runs on your host, safety is enforced by:

- Command allowlist (`run_command`)
- Argument validation (no shell injection)
- `shell=False` everywhere
- Workspace path confinement
- Output truncation
- Timeouts
- Secret redaction (env inspection)

You are responsible for trusting the client using this server.

---

## Docker Tools (Optional)

Docker tools are still available but assume:

- Docker CLI is installed on host
- Docker daemon is running

No container mounting or docker.sock tricks are used.

---

## Example Tools

- list_dir
- read_file
- ripgrep_search
- ast_grep_search
- run_command
- docker_exec_*
- host_ps / host_ports / host_env

---

## Notes

- Missing binaries will return helpful errors
- Return code 127 indicates missing command
- Prefer `write_file` over patching tools for edits

---

## Legacy Docker Mode (Optional)

You can still run this inside Docker if you choose, but it is no longer the primary or recommended mode.
