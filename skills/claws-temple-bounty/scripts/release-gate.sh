#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

echo "[release-gate] running strict repository validation"
python3 "$ROOT_DIR/scripts/validate_skill_repo.py"

echo "[release-gate] running strict dependency and remote checks"
STRICT_DEPS=1 CHECK_REMOTE_SKILL=1 REMOTE_PROBE_MODE=strict \
  bash "$ROOT_DIR/skills/claws-temple-bounty/scripts/smoke-check.sh"

echo "[release-gate] OK"
