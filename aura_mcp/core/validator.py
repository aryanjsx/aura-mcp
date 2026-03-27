"""Plan validation and sanitization.

Every LLM-generated plan is run through ``validate_plan`` before the executor
touches the filesystem, ensuring only safe, well-formed plans are acted upon.
"""

from __future__ import annotations

import re

ALLOWED_ACTIONS = ("scaffold_project",)
ALLOWED_FRAMEWORKS = ("react", "node", "fastapi")
PROJECT_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def validate_plan(plan: dict) -> dict:
    """Validate and lightly sanitize *plan*.

    Returns a cleaned copy or raises ``ValueError`` on any violation.
    """
    if not plan or not isinstance(plan, dict):
        raise ValueError("Plan must be a non-null object")

    if plan.get("action") not in ALLOWED_ACTIONS:
        raise ValueError(
            f"Invalid action \"{plan.get('action')}\". "
            f"Allowed: {', '.join(ALLOWED_ACTIONS)}"
        )

    if plan.get("framework") not in ALLOWED_FRAMEWORKS:
        raise ValueError(
            f"Invalid framework \"{plan.get('framework')}\". "
            f"Allowed: {', '.join(ALLOWED_FRAMEWORKS)}"
        )

    raw_name = plan.get("project_name")
    if not raw_name or not isinstance(raw_name, str):
        raise ValueError("Plan must include a non-empty project_name string")

    sanitized = (
        raw_name.lower()
        .encode("ascii", "ignore")
        .decode()
    )
    sanitized = re.sub(r"[^a-z0-9_-]", "_", sanitized)
    sanitized = re.sub(r"_{2,}", "_", sanitized)
    sanitized = sanitized.strip("-_")[:64]

    if not PROJECT_NAME_RE.match(sanitized):
        raise ValueError(
            f'Could not produce a valid project name from "{raw_name}"'
        )

    features = plan.get("features", [])
    if not isinstance(features, list):
        features = []

    return {
        "action": plan["action"],
        "framework": plan["framework"],
        "project_name": sanitized,
        "features": features,
    }
