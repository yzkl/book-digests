## ----------------------------- Builder stage ----------------------------- ##
FROM python:3.12-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.4 /uv /uvx /bin/

# COPY project dependencies
WORKDIR /app
COPY ./pyproject.toml ./pyproject.toml
COPY ./uv.lock ./uv.lock
RUN uv sync --locked

## ---------------------------- Production stage --------------------------- ##
FROM python:3.12-slim-bookworm AS production

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY ./src ./src
COPY ./migrations ./migrations
COPY ./alembic.ini ./alembic.ini
COPY ./.env.prod ./.env.prod 

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 4001

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4001", "--log-level", "info"]