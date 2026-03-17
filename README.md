# MCP Code Assistant

A local code-search MCP-style server that exposes safe tools for interacting with a code repository.

Tools include:

- list_dir
- read_file
- read_files
- ripgrep_search
- ast_grep_search
- propose_patch
- apply_patch

This server is designed to run locally and be exposed through a tunnel (e.g., Cloudflare Tunnel or ngrok) so ChatGPT can access it.

## Requirements

Install:

- Python 3.11+
- ripgrep (`rg`)
- ast-grep

Example macOS install:

```bash
brew install ripgrep ast-grep
```

## Run the MCP Server

Option 1 — Using the helper script:

```bash
bash scripts/run_local.sh
```

Option 2 — Run directly with uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs on:

```
http://localhost:8000
```

The MCP endpoint is:

```
http://localhost:8000/mcp
```

## Exposing to ChatGPT

Expose the MCP endpoint through a tunnel.

### Cloudflare Tunnel

```bash
cloudflared tunnel --url http://localhost:8000
```

### ngrok

```bash
ngrok http 8000
```

Your MCP endpoint will be:

```
https://your-tunnel-url/mcp
```

## Connecting in ChatGPT

1. Enable **Developer Mode**
2. Go to **Settings → Apps & Connectors**
3. Click **Create App**
4. Enter your MCP endpoint:

```
https://your-tunnel-url/mcp
```

5. Save and start a new chat.

ChatGPT will automatically discover the tools:

- list_dir
- read_file
- read_files
- ripgrep_search
- ast_grep_search
- propose_patch
- apply_patch