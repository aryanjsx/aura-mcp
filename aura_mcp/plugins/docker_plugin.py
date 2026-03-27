"""Docker plugin — generate Dockerfiles for scaffolded projects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.file_utils import create_file
from aura_mcp.utils.logger import get_logger

_TEMPLATES: dict[str, str] = {
    "node": (
        "FROM node:18-alpine\n"
        "WORKDIR /app\n"
        "COPY package*.json ./\n"
        "RUN npm ci --omit=dev\n"
        "COPY . .\n"
        "EXPOSE 3000\n"
        "CMD [\"node\", \"index.js\"]\n"
    ),
    "react": (
        "FROM node:18-alpine AS build\n"
        "WORKDIR /app\n"
        "COPY package*.json ./\n"
        "RUN npm ci\n"
        "COPY . .\n"
        "RUN npm run build\n"
        "\n"
        "FROM nginx:alpine\n"
        "COPY --from=build /app/build /usr/share/nginx/html\n"
        "EXPOSE 80\n"
        "CMD [\"nginx\", \"-g\", \"daemon off;\"]\n"
    ),
    "fastapi": (
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        "COPY requirements.txt .\n"
        "RUN pip install --no-cache-dir -r requirements.txt\n"
        "COPY . .\n"
        "EXPOSE 8000\n"
        "CMD [\"uvicorn\", \"main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]\n"
    ),
}


class DockerPlugin(BasePlugin):
    """Generate Dockerfiles tailored to the detected framework."""

    @property
    def name(self) -> str:
        return "docker"

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        action = intent.get("action", "")

        if action == "generate_dockerfile":
            return self._generate(
                intent["framework"],
                intent["project_path"],
            )

        raise ValueError(f'DockerPlugin: unknown action "{action}"')

    def _generate(self, framework: str, project_path: str) -> dict[str, Any]:
        logger = get_logger()

        template = _TEMPLATES.get(framework)
        if template is None:
            raise ValueError(
                f"No Dockerfile template for framework: {framework}"
            )

        dest = Path(project_path) / "Dockerfile"
        create_file(dest, template)
        logger.info("Generated Dockerfile at %s", dest)
        return {"status": "ok", "path": str(dest)}

    def describe(self) -> str:
        return "Docker — generate Dockerfiles for Node, React, FastAPI"
