FROM python:3.11-slim AS base

WORKDIR /app

COPY pyproject.toml README.md ./
COPY aura_mcp/ aura_mcp/

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["aura"]
CMD ["start"]
