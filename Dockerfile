FROM python:3.11-slim

ARG GIT_USER_NAME="MCP Code Assistant"
ARG GIT_USER_EMAIL="mcp@local.dev"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ripgrep \
    git \
    docker.io \
    docker-compose-plugin \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.name "$GIT_USER_NAME" \
    && git config --global user.email "$GIT_USER_EMAIL"

COPY pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts
COPY README.md /workspace/README.md

RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir ast-grep-cli && \
    if [ -x /usr/local/bin/sg ] && [ ! -e /usr/local/bin/ast-grep ]; then ln -s /usr/local/bin/sg /usr/local/bin/ast-grep; fi

ENV WORKSPACE_ROOT=/workspace
ENV ENABLE_WRITES=false

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]