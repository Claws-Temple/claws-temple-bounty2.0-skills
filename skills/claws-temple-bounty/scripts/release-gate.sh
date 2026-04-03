#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_ROOT/../.." && pwd)"
TASK4_TARGET_HOST="${TASK4_TARGET_HOST:-compat}"
OPENCLAW_TASK4_NATIVE_READY="${OPENCLAW_TASK4_NATIVE_READY:-0}"
OPENCLAW_TASK4_SESSION_REFRESHED="${OPENCLAW_TASK4_SESSION_REFRESHED:-0}"

if [[ -f "$REPO_ROOT/scripts/validate_skill_repo.py" && -d "$REPO_ROOT/skills/claws-temple-bounty" ]]; then
  VALIDATOR_PATH="$REPO_ROOT/scripts/validate_skill_repo.py"
  SMOKE_SCRIPT="$SKILL_ROOT/scripts/smoke-check.sh"
  VALIDATOR_MODE="repo"
else
  VALIDATOR_PATH="$SKILL_ROOT/scripts/validate_clawhub_bundle.py"
  SMOKE_SCRIPT="$SKILL_ROOT/scripts/smoke-check.sh"
  VALIDATOR_MODE="bundle"
fi

echo "[release-gate] running strict repository validation"
if [[ "$VALIDATOR_MODE" == "repo" ]]; then
  python3 "$VALIDATOR_PATH"
else
  python3 "$VALIDATOR_PATH" "$SKILL_ROOT"
fi

echo "[release-gate] running strict dependency checks for target host: $TASK4_TARGET_HOST"
if [[ "$TASK4_TARGET_HOST" == "OpenClaw" ]]; then
  STRICT_DEPS=1 bash "$SMOKE_SCRIPT"
  if [[ "$OPENCLAW_TASK4_NATIVE_READY" != "1" ]]; then
    echo "[release-gate] OpenClaw release requires OPENCLAW_TASK4_NATIVE_READY=1 after operators verify the compatible Task 4 native runtime." >&2
    exit 1
  fi
  if [[ "$OPENCLAW_TASK4_SESSION_REFRESHED" != "1" ]]; then
    echo "[release-gate] OpenClaw release requires OPENCLAW_TASK4_SESSION_REFRESHED=1 after a fresh /new session is confirmed." >&2
    exit 1
  fi
else
  STRICT_DEPS=1 CHECK_REMOTE_SKILL=1 REMOTE_PROBE_MODE=strict \
    bash "$SMOKE_SCRIPT"
fi

echo "[release-gate] OK"
