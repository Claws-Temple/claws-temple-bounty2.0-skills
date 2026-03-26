#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

echo "[test-rollout-gate] running repository validation"
python3 "$ROOT_DIR/scripts/validate_skill_repo.py"

echo "[test-rollout-gate] running strict local dependency checks"
STRICT_DEPS=1 bash "$ROOT_DIR/skills/claws-temple-bounty/scripts/smoke-check.sh"

echo "[test-rollout-gate] probing Task 4 live skill in warn mode"
PROBE_MODE=warn bash "$ROOT_DIR/skills/claws-temple-bounty/scripts/task4-live-skill-probe.sh"

echo "[test-rollout-gate] OK"
