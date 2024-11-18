FROM python:3.10

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:0.4.8 /uv /bin/uv

COPY . .

RUN uv sync --frozen --no-cache

CMD ["/app/.venv/bin/uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
