#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$SKILL_ROOT/../.." && pwd)"
RESOLVER_PATH="$SKILL_ROOT/scripts/skill-root-resolver.sh"
STRICT_DEPS="${STRICT_DEPS:-0}"
CHECK_REMOTE_SKILL="${CHECK_REMOTE_SKILL:-0}"
REMOTE_PROBE_MODE="${REMOTE_PROBE_MODE:-warn}"
DEPENDENCY_CATALOG="$SKILL_ROOT/config/dependency-sources.json"

# shellcheck source=/dev/null
source "$RESOLVER_PATH"
claws_temple_init_skill_roots "$SKILL_ROOT"
RESOLVED_RESONANCE_CONTRACT_PATH=""
RESOLVED_TOMORROWDAO_PATH=""
RESOLVED_PORTKEY_PATH=""

if [[ -f "$REPO_ROOT/scripts/validate_skill_repo.py" && -d "$REPO_ROOT/skills/claws-temple-bounty" ]]; then
  VALIDATOR_PATH="$REPO_ROOT/scripts/validate_skill_repo.py"
  PROBE_SCRIPT="$SKILL_ROOT/scripts/task4-live-skill-probe.sh"
  SELF_HEAL_COMMAND="bash scripts/self-heal-local-dependency.sh"
  VALIDATOR_MODE="repo"
else
  VALIDATOR_PATH="$SKILL_ROOT/scripts/validate_clawhub_bundle.py"
  PROBE_SCRIPT="$SKILL_ROOT/scripts/task4-live-skill-probe.sh"
  SELF_HEAL_COMMAND="bash scripts/self-heal-local-dependency.sh"
  VALIDATOR_MODE="bundle"
fi

get_catalog_field() {
  local dep="$1"
  local field="$2"
  python3 - "$DEPENDENCY_CATALOG" "$dep" "$field" <<'PY'
import json
import sys
from pathlib import Path

catalog = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
entry = catalog["dependencies"].get(sys.argv[2], {})
print(entry.get(sys.argv[3], ""))
PY
}

print_dep_source_hint() {
  local dep="$1"
  local normalized="$dep"
  normalized="${normalized%%:*}"
  local repo_url env_name clawhub_slug openclaw_hint
  repo_url="$(get_catalog_field "$normalized" default_repo_url)"
  env_name="$(get_catalog_field "$normalized" env_override)"
  clawhub_slug="$(get_catalog_field "$normalized" clawhub_slug)"
  openclaw_hint="$(get_catalog_field "$normalized" openclaw_install_hint)"
  if [[ -n "$repo_url" ]]; then
    echo "[smoke-check] suggestion: run $SELF_HEAL_COMMAND $normalized"
    echo "[smoke-check] suggestion: default source repo -> $repo_url"
    echo "[smoke-check] suggestion: optional local override -> export $env_name=/path/to/local/repo-or-skill"
    if [[ -n "$clawhub_slug" ]]; then
      echo "[smoke-check] suggestion: OpenClaw native install -> openclaw skills install $clawhub_slug"
    fi
    if [[ -n "$openclaw_hint" ]]; then
      echo "[smoke-check] suggestion: OpenClaw runtime note -> $openclaw_hint"
    fi
  fi
}

echo "[smoke-check] validating repository structure and visible-layer rules"
if [[ "$VALIDATOR_MODE" == "repo" ]]; then
  python3 "$VALIDATOR_PATH"
else
  python3 "$VALIDATOR_PATH" "$SKILL_ROOT"
fi

echo "[smoke-check] skill-root search order"
for root in "${CLAWS_TEMPLE_SKILL_ROOTS[@]}"; do
  echo "[smoke-check]   - $root"
done
echo "[smoke-check] preferred install root: $(claws_temple_runtime_install_root)"

echo "[smoke-check] checking Task 3 executor helper"
for tool_name in bash python3 bun; do
  if ! command -v "$tool_name" >/dev/null 2>&1; then
    if [[ "$STRICT_DEPS" == "1" ]]; then
      echo "[smoke-check] missing Task 3 helper prerequisite: $tool_name" >&2
      exit 1
    fi
    echo "[smoke-check] warning: missing Task 3 helper prerequisite: $tool_name"
  fi
done
python3 "$SKILL_ROOT/scripts/task3-oath-executor.py" --help >/dev/null
bash "$SKILL_ROOT/scripts/task3-oath-executor.sh" --help >/dev/null

echo "[smoke-check] checking Task 3 proposal URLs are present"
python3 - "$SKILL_ROOT" <<'PY'
import json
import sys
from pathlib import Path

skill_root = Path(sys.argv[1])
config_path = skill_root / "config" / "faction-proposals.json"
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
for dep in agent-spectrum resonance-contract tomorrowdao-agent-skills portkey-ca-agent-skills; do
  resolved_path="$(claws_temple_resolve_skill_dir "$dep" 2>/dev/null || true)"
  if [[ -z "$resolved_path" ]]; then
    missing_deps+=("$dep")
    continue
  fi
  case "$dep" in
    resonance-contract)
      RESOLVED_RESONANCE_CONTRACT_PATH="$resolved_path"
      ;;
    tomorrowdao-agent-skills)
      RESOLVED_TOMORROWDAO_PATH="$resolved_path"
      ;;
    portkey-ca-agent-skills)
      RESOLVED_PORTKEY_PATH="$resolved_path"
      ;;
  esac
  if [[ ! -f "$resolved_path/SKILL.md" && ! -f "$resolved_path/package.json" ]]; then
    missing_deps+=("$dep:missing-skill-entry")
  fi
done

if (( ${#missing_deps[@]} > 0 )); then
  for dep in "${missing_deps[@]}"; do
    print_dep_source_hint "$dep"
  done
  if [[ "$STRICT_DEPS" == "1" ]]; then
    echo "[smoke-check] missing dependency skills across roots $(printf '%s ' "${CLAWS_TEMPLE_SKILL_ROOTS[@]}"): ${missing_deps[*]}" >&2
    exit 1
  fi
  echo "[smoke-check] warning: missing dependency skills across roots $(printf '%s ' "${CLAWS_TEMPLE_SKILL_ROOTS[@]}"): ${missing_deps[*]}"
  echo "[smoke-check] warning: this is a repo self-check only; use release-gate.sh for a hard release gate"
else
  echo "[smoke-check] dependency skills verified across roots $(printf '%s ' "${CLAWS_TEMPLE_SKILL_ROOTS[@]}")"
fi

echo "[smoke-check] checking resonance-contract dependency version"
python3 - "$RESOLVED_RESONANCE_CONTRACT_PATH" "$STRICT_DEPS" "$DEPENDENCY_CATALOG" <<'PY'
import re
import sys
import json
from pathlib import Path

dep_dir = Path(sys.argv[1]) if sys.argv[1] else None
strict = sys.argv[2] == "1"
catalog = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
issues: list[str] = []

skill_path = (dep_dir / "SKILL.md") if dep_dir is not None else None
dep_cfg = catalog["dependencies"]["resonance-contract"]
min_version_raw = dep_cfg["min_version"]
min_version = tuple(int(part) for part in min_version_raw.split("."))
repo_url = dep_cfg["default_repo_url"]

if dep_dir is None or skill_path is None or not skill_path.exists():
    issues.append(f"missing SKILL.md in {dep_dir or 'unresolved resonance-contract root'}")
else:
    text = skill_path.read_text(encoding="utf-8")
    match = re.search(r"^version:\s*([0-9]+\.[0-9]+\.[0-9]+)\s*$", text, re.MULTILINE)
    if not match:
        issues.append(f"could not resolve resonance-contract version from {skill_path}")
    else:
        raw = match.group(1)
        actual = tuple(int(part) for part in raw.split("."))
        if actual < min_version:
            issues.append(
                f"resonance-contract version {raw} is below required {min_version_raw}; "
                f"upgrade from {repo_url}"
            )

if issues:
    joined = "; ".join(issues)
    if strict:
        raise SystemExit(joined)
    print(f"[smoke-check] warning: {joined}")
else:
    print("[smoke-check] resonance-contract dependency version verified")
PY

echo "[smoke-check] checking TomorrowDAO dependency version and Task 3 preflight tools"
python3 - "$SKILL_ROOT" "$RESOLVED_TOMORROWDAO_PATH" "$STRICT_DEPS" "$DEPENDENCY_CATALOG" <<'PY'
import json
import sys
from pathlib import Path

skill_root = Path(sys.argv[1])
dep_dir = Path(sys.argv[2]) if sys.argv[2] else None
strict = sys.argv[3] == "1"
catalog = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
config = json.loads((skill_root / "config" / "faction-proposals.json").read_text(encoding="utf-8"))
issues: list[str] = []

def parse_version(raw: str) -> tuple[int, ...]:
    return tuple(int(part) for part in raw.split(".") if part.isdigit())

pkg_path = (dep_dir / "package.json") if dep_dir is not None else None
dep_cfg = catalog["dependencies"]["tomorrowdao-agent-skills"]
catalog_min_version = dep_cfg["min_version"]
repo_url = dep_cfg["default_repo_url"]
if dep_dir is None or pkg_path is None or not pkg_path.exists():
    issues.append(f"missing package.json in {dep_dir or 'unresolved tomorrowdao-agent-skills root'}")
else:
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    actual_version = str(pkg.get("version") or "")
    min_version = config["dependency_min_version"]
    if min_version != catalog_min_version:
        issues.append(
            f"dependency catalog min version {catalog_min_version} does not match Task 3 config {min_version}"
        )
    if parse_version(actual_version) < parse_version(min_version):
        issues.append(
            f"tomorrowdao-agent-skills version {actual_version} is below required {min_version}; "
            f"upgrade from {repo_url}"
        )

tool_markers = [
    config["token_balance_tool_name"],
    config["token_allowance_tool_name"],
    config["dependency_invocation"]["approve_tool_name"],
    config["dependency_invocation"]["tool_name"],
]
server_path = (dep_dir / "src" / "mcp" / "server.ts") if dep_dir is not None else None
openclaw_path = (dep_dir / "openclaw.json") if dep_dir is not None else None
cli_path = (dep_dir / "tomorrowdao_skill.ts") if dep_dir is not None else None
for path in (server_path, openclaw_path):
    if path is None or not path.exists():
        issues.append(f"missing expected dependency file: {path}")
        continue
    text = path.read_text(encoding="utf-8")
    for tool_marker in tool_markers:
        if tool_marker not in text:
            issues.append(f"{tool_marker} not found in {path}")
cli_markers = (
    "token-balance-view",
    "token-allowance-view",
    "tokenApprove",
    "daoVote",
)
if cli_path is None or not cli_path.exists():
    issues.append(f"missing expected dependency file: {cli_path}")
else:
    cli_text = cli_path.read_text(encoding="utf-8")
    for cli_marker in cli_markers:
        if cli_marker not in cli_text:
            issues.append(f"{cli_marker} not found in {cli_path}")

if issues:
    joined = "; ".join(issues)
    if strict:
        raise SystemExit(joined)
    print(f"[smoke-check] warning: {joined}")
else:
    print("[smoke-check] tomorrowdao dependency version and Task 3 preflight tools verified")
PY

echo "[smoke-check] checking Portkey CA dependency version and forward-call tool"
python3 - "$RESOLVED_PORTKEY_PATH" "$STRICT_DEPS" "$DEPENDENCY_CATALOG" <<'PY'
import json
import re
import sys
from pathlib import Path

dep_dir = Path(sys.argv[1]) if sys.argv[1] else None
strict = sys.argv[2] == "1"
catalog = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8"))
issues: list[str] = []

skill_path = (dep_dir / "SKILL.md") if dep_dir is not None else None
pkg_path = (dep_dir / "package.json") if dep_dir is not None else None
server_path = (dep_dir / "src" / "mcp" / "server.ts") if dep_dir is not None else None
catalog_min = catalog["dependencies"]["portkey-ca-agent-skills"]["min_version"]
repo_url = catalog["dependencies"]["portkey-ca-agent-skills"]["default_repo_url"]

def parse_version(raw: str) -> tuple[int, ...]:
    return tuple(int(part) for part in raw.split(".") if part.isdigit())

if dep_dir is None or skill_path is None or not skill_path.exists():
    issues.append(f"missing SKILL.md in {dep_dir or 'unresolved portkey-ca-agent-skills root'}")
else:
    text = skill_path.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"?([0-9]+\.[0-9]+\.[0-9]+)"?\s*$', text, re.MULTILINE)
    if not match:
      issues.append(f"could not resolve portkey-ca-agent-skills version from {skill_path}")
    elif parse_version(match.group(1)) < parse_version(catalog_min):
      issues.append(
          f"portkey-ca-agent-skills version {match.group(1)} is below required {catalog_min}; upgrade from {repo_url}"
      )

if dep_dir is None or pkg_path is None or not pkg_path.exists():
    issues.append(f"missing package.json in {dep_dir or 'unresolved portkey-ca-agent-skills root'}")
else:
    pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
    actual_version = str(pkg.get("version") or "")
    if parse_version(actual_version) < parse_version(catalog_min):
        issues.append(
            f"portkey-ca-agent-skills package version {actual_version} is below required {catalog_min}; "
            f"upgrade from {repo_url}"
        )

if server_path is None or not server_path.exists():
    issues.append(f"missing expected dependency file: {server_path}")
else:
    text = server_path.read_text(encoding="utf-8")
    if "portkey_forward_call" not in text:
        issues.append("portkey_forward_call not found in portkey-ca-agent-skills MCP server")

if issues:
    joined = "; ".join(issues)
    if strict:
        raise SystemExit(joined)
    print(f"[smoke-check] warning: {joined}")
else:
    print("[smoke-check] portkey-ca-agent-skills dependency version and CA write tool verified")
PY

if [[ "$CHECK_REMOTE_SKILL" == "1" ]]; then
  echo "[smoke-check] checking remote Task 4 live skill"
  PROBE_MODE="$REMOTE_PROBE_MODE" \
    bash "$PROBE_SCRIPT"
  echo "[smoke-check] remote live skill reachable"
fi

echo "[smoke-check] OK"
