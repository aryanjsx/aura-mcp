#!/usr/bin/env bash
# DevOps readiness: verify the Docker image builds and the CLI works inside it.
#
# Usage
# -----
#     bash scripts/test_docker.sh
#
# The script gracefully handles missing Docker CLI or a stopped daemon
# so it can run safely in CI and on developer machines without Docker.

set -uo pipefail

IMAGE="aura-mcp-test"
PASS=0
FAIL=0

banner() {
    printf '\n%s\n  %s\n%s\n' \
        "============================================================" \
        "$1" \
        "============================================================"
}

check() {
    local label="$1"
    shift
    printf '\n>> %s\n   $ %s\n\n' "$label" "$*"
    if output="$("$@" 2>&1)"; then
        printf '%s\n' "$output"
        echo "   [PASS] $label"
        PASS=$((PASS + 1))
    else
        printf '%s\n' "$output"
        echo "   [FAIL] $label"
        FAIL=$((FAIL + 1))
    fi
}

# ── Docker CLI detection ─────────────────────────────────────────────

if ! command -v docker >/dev/null 2>&1; then
    banner "AURA MCP — Docker Verification"
    echo ""
    echo "  Docker CLI not found. Skipping Docker verification tests."
    echo ""
    banner "Summary"
    echo "  Docker tests skipped (Docker not installed)"
    exit 0
fi

# ── Docker daemon check ──────────────────────────────────────────────

if ! docker info >/dev/null 2>&1; then
    banner "AURA MCP — Docker Verification"
    echo ""
    echo "  Docker daemon is not running. Start Docker Desktop and rerun the test."
    echo ""
    banner "Summary"
    echo "  Docker tests skipped (daemon not running)"
    exit 0
fi

banner "AURA MCP — Docker Verification"

# ── Build ────────────────────────────────────────────────────────────

check "Docker build" \
    docker build -t "$IMAGE" .

# Stop early if the image failed to build — remaining checks need it
if [ "$FAIL" -gt 0 ]; then
    banner "Summary"
    echo "  Docker build failed — skipping remaining checks."
    exit 1
fi

# ── CLI entry points ─────────────────────────────────────────────────

check "aura --help inside container" \
    docker run --rm "$IMAGE" --help

check "python -m aura_mcp --help inside container" \
    docker run --rm --entrypoint python "$IMAGE" -m aura_mcp --help

# ── Module imports ───────────────────────────────────────────────────

check "Import core modules" \
    docker run --rm --entrypoint python "$IMAGE" -c \
    "from aura_mcp.core.interpreter import parse_task; \
     from aura_mcp.core.validator import validate_plan; \
     print('Core modules OK')"

check "Plugin discovery" \
    docker run --rm --entrypoint python "$IMAGE" -c \
    "from aura_mcp.plugins.manager import plugin_manager; \
     names = plugin_manager.list_plugins(); \
     assert len(names) >= 5, f'Expected >=5 plugins, got {len(names)}'; \
     print(f'Plugins: {names}')"

# ── Cleanup ──────────────────────────────────────────────────────────

banner "Cleanup"
echo "Removing test image: $IMAGE"
docker rmi "$IMAGE" --force 2>/dev/null || true

# ── Summary ──────────────────────────────────────────────────────────

TOTAL=$((PASS + FAIL))

banner "Summary"
echo "  Passed: $PASS / $TOTAL"
if [ "$FAIL" -gt 0 ]; then
    echo "  Failed: $FAIL / $TOTAL"
    echo ""
    echo "  Some checks FAILED — review output above."
    exit 1
else
    echo ""
    echo "  All checks passed."
    exit 0
fi
