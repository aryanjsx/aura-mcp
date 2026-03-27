"""GitHub integration plugin — create repos and push files via the GitHub API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from aura_mcp.config.loader import get_config
from aura_mcp.plugins.base import BasePlugin
from aura_mcp.utils.logger import get_logger

_API = "https://api.github.com"


class GitHubPlugin(BasePlugin):
    """Create repositories and commit files on GitHub."""

    @property
    def name(self) -> str:
        return "github"

    def _token(self) -> str:
        config = get_config()
        token = (
            config.get("github", {}).get("token")
            or os.environ.get("GITHUB_TOKEN", "")
        )
        if not token:
            raise RuntimeError(
                "Missing GITHUB_TOKEN. Set it as an environment variable "
                "or in config.yaml under github.token."
            )
        return token

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._token()}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        action = intent.get("action", "")

        if action == "create_repo":
            return await self._create_repo(
                intent["repo_name"],
                intent.get("description", ""),
                private=intent.get("private", False),
            )

        if action == "create_file":
            return await self._create_file(
                intent["repo"],
                intent["path"],
                intent["content"],
                message=intent.get("message", "Add file via AURA"),
            )

        raise ValueError(f'GitHubPlugin: unknown action "{action}"')

    async def _create_repo(
        self, name: str, description: str, *, private: bool = False
    ) -> dict[str, Any]:
        logger = get_logger()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_API}/user/repos",
                headers=self._headers(),
                json={
                    "name": name,
                    "description": description,
                    "private": private,
                    "auto_init": True,
                },
                timeout=30,
            )
        resp.raise_for_status()
        url = resp.json().get("html_url", "")
        logger.info("Created GitHub repo: %s", url)
        return {"status": "ok", "url": url}

    async def _create_file(
        self,
        repo: str,
        path: str,
        content: str,
        *,
        message: str = "Add file via AURA",
    ) -> dict[str, Any]:
        import base64

        logger = get_logger()
        encoded = base64.b64encode(content.encode()).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{_API}/repos/{repo}/contents/{path}",
                headers=self._headers(),
                json={"message": message, "content": encoded},
                timeout=30,
            )
        resp.raise_for_status()
        logger.info("Created file %s in %s", path, repo)
        return {"status": "ok", "path": path}

    def describe(self) -> str:
        return "GitHub integration — create repos & push files"
