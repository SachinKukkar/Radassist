# syntax=docker/dockerfile:1

# ============ Stage 1: builder - install dependencies into a virtual environment ============
FROM python:3.12-slim-trixie AS builder

# Copy the uv binaries from the official uv image (pinned to the same version as your laptop)
COPY --from=ghcr.io/astral-sh/uv:0.12.18 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Install ONLY the dependencies. This layer is cached until pyproject.toml or uv.lock changes,
# so editing application code doesn't trigger a slow reinstall.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# ============ Stage 2: runtime - small final image without uv or build caches ============
FROM python:3.12-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Create an unprivileged user; the app never runs as root
RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# Files stay owned by root: the app user can read and execute them, but not modify them
COPY --from=builder /app/.venv /app/.venv
COPY app ./app

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-m", "app.healthcheck"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
