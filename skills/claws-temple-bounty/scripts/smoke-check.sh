#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
STRICT_DEPS="${STRICT_DEPS:-0}"
CHECK_REMOTE_SKILL="${CHECK_REMOTE_SKILL:-0}"
REMOTE_PROBE_MODE="${REMOTE_PROBE_MODE:-warn}"
SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}/skills"

echo "[smoke-check] validating repository structure and visible-layer rules"
python3 "$ROOT_DIR/scripts/validate_skill_repo.py"

echo "[smoke-check] checking Task 3 proposal URLs are present"
python3 - "$ROOT_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
config_path = root / "skills" / "claws-temple-bounty" / "config" / "faction-proposals.json"
config = json.loads(config_path.read_text(encoding="utf-8"))
for faction in config["factions"]:
    expected = f"https://tmrwdao.com/dao/{config['dao_alias']}/proposal/{faction['proposal_id']}"
    if faction["proposal_url"] != expected:
        raise SystemExit(
            f"proposal_url mismatch for {faction['brand_key']}: {faction['proposal_url']} != {expected}"
        )
print("proposal_url entries verified")
PY

echo "[smoke-check] checking local dependency skills"
missing_deps=()
for dep in agent-spectrum resonance-contract tomorrowdao-agent-skills; do
  if [[ ! -d "$SKILLS_HOME/$dep" ]]; then
    missing_deps+=("$dep")
    continue
  fi
  if [[ ! -f "$SKILLS_HOME/$dep/SKILL.md" ]]; then
    missing_deps+=("$dep:missing-skill-entry")
  fi
done

if (( ${#missing_deps[@]} > 0 )); then
  if [[ "$STRICT_DEPS" == "1" ]]; then
    echo "[smoke-check] missing dependency skills in $SKILLS_HOME: ${missing_deps[*]}" >&2
    exit 1
  fi
  echo "[smoke-check] warning: missing dependency skills in $SKILLS_HOME: ${missing_deps[*]}"
  echo "[smoke-check] warning: this is a repo self-check only; use release-gate.sh for a hard release gate"
else
  echo "[smoke-check] dependency skills verified"
fi

if [[ "$CHECK_REMOTE_SKILL" == "1" ]]; then
  echo "[smoke-check] checking remote Task 4 live skill"
  PROBE_MODE="$REMOTE_PROBE_MODE" \
    bash "$ROOT_DIR/skills/claws-temple-bounty/scripts/task4-live-skill-probe.sh"
  echo "[smoke-check] remote live skill reachable"
fi

echo "[smoke-check] OK"
