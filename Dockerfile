FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY scripts ./scripts

RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir ast-grep-cli && \
    if [ -x /usr/local/bin/sg ] && [ ! -e /usr/local/bin/ast-grep ]; then ln -s /usr/local/bin/sg /usr/local/bin/ast-grep; fi

ENV WORKSPACE_ROOT=/workspace
ENV ENABLE_WRITES=false

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]