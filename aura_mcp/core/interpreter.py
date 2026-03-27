"""Task interpretation — LLM-first with a deterministic rule-based fallback."""

from __future__ import annotations

import os
import re

from aura_mcp.config.loader import get_config
from aura_mcp.core.validator import validate_plan
from aura_mcp.integrations.llm.factory import interpret_with_llm
from aura_mcp.utils.logger import get_logger

# ── Rule-based fallback ──────────────────────────────────────────────

FRAMEWORK_RULES: list[tuple[list[str], str]] = [
    (["react"], "react"),
    (["fastapi", "fast api", "flask", "python api"], "fastapi"),
    (["node", "express", "javascript api"], "node"),
]

STOP_WORDS = frozenset(
    "a an the with and for in on to of my me it is do so or by at be "
    "create build scaffold make setup set up generate new project app "
    "application using use add start write develop code please want need "
    "like should would could simple basic full complete stack web website "
    "site frontend backend server client api".split()
)


def _detect_framework(text: str) -> str:
    lower = text.lower()
    for keywords, framework in FRAMEWORK_RULES:
        if any(kw in lower for kw in keywords):
            return framework
    return "node"


def _derive_project_name(text: str, framework: str) -> str:
    all_fw_keywords = {kw for kws, _ in FRAMEWORK_RULES for kw in kws}
    ignore = STOP_WORDS | all_fw_keywords

    words = [
        w
        for w in re.sub(r"[^a-z0-9\s]", "", text.lower()).split()
        if len(w) > 1 and w not in ignore
    ]

    meaningful = words[:3]
    return "_".join(meaningful) if meaningful else f"{framework}_app"


def parse_with_rules(task_text: str) -> dict:
    """Deterministic keyword-based parser (no network calls)."""
    logger = get_logger()
    framework = _detect_framework(task_text)
    project_name = _derive_project_name(task_text, framework)

    plan = {
        "action": "scaffold_project",
        "framework": framework,
        "project_name": project_name,
        "features": [],
    }
    logger.info(
        "[rules] Parsed → action: %s, framework: %s, name: %s",
        plan["action"],
        plan["framework"],
        plan["project_name"],
    )
    return plan


# ── Main interpreter ─────────────────────────────────────────────────


async def parse_task(task_text: str) -> dict:
    """Interpret *task_text* into a structured execution plan.

    Strategy: try the LLM first; on any failure fall back to the
    deterministic rule-based parser.
    """
    logger = get_logger()

    if not task_text or not isinstance(task_text, str) or not task_text.strip():
        raise ValueError("Cannot parse empty task text")

    config = get_config()
    llm_mode = config.get("llm_mode", "openai")

    if llm_mode == "openai":
        api_key = (
            config.get("openai", {}).get("api_key")
            or os.environ.get("OPENAI_API_KEY", "")
        )
        if not api_key:
            logger.warning("OPENAI_API_KEY not set — using rule-based parser")
            return parse_with_rules(task_text)

    try:
        raw_plan = await interpret_with_llm(task_text)
        plan = validate_plan(raw_plan)
        logger.info(
            "[llm] Parsed → action: %s, framework: %s, name: %s",
            plan["action"],
            plan["framework"],
            plan["project_name"],
        )
        if plan["features"]:
            logger.info("[llm] Features: %s", ", ".join(plan["features"]))
        return plan
    except Exception as exc:
        logger.warning("LLM interpretation failed: %s", exc)
        logger.info("Falling back to rule-based parser")
        return parse_with_rules(task_text)
