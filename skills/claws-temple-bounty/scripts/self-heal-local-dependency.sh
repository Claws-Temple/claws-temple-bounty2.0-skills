#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
SKILLS_HOME="${CODEX_HOME:-$HOME/.codex}/skills"

usage() {
  cat <<'EOF'
Usage:
  bash skills/claws-temple-bounty/scripts/self-heal-local-dependency.sh <dependency>

Supported dependencies:
  agent-spectrum
  resonance-contract
  tomorrowdao-agent-skills
  all
EOF
}

resolve_source() {
  case "$1" in
    agent-spectrum)
      printf '%s\n' "/Users/huangzongzhe/workspace/vibeCoding/agent-spectrum-skill/skills/agent-spectrum"
      ;;
    resonance-contract)
      printf '%s\n' "/Users/huangzongzhe/workspace/vibeCoding/agent-resonance-skill/skills/resonance-contract"
      ;;
    tomorrowdao-agent-skills)
      printf '%s\n' "/Users/huangzongzhe/workspace/TomorrowDAOProject/tomorrowDAO-skill"
      ;;
    *)
      return 1
      ;;
  esac
}

install_or_refresh_one() {
  local dep="$1"
  local source
  source="$(resolve_source "$dep")"
  local target="$SKILLS_HOME/$dep"

  if [[ ! -e "$source" ]]; then
    echo "[self-heal] source not found for $dep: $source" >&2
    return 1
  fi

  mkdir -p "$SKILLS_HOME"

  if [[ -L "$target" ]]; then
    ln -sfn "$source" "$target"
    echo "[self-heal] refreshed symlink for $dep -> $source"
    return 0
  fi

  if [[ ! -e "$target" ]]; then
    if ln -s "$source" "$target" 2>/dev/null; then
      echo "[self-heal] installed symlink for $dep -> $source"
    else
      mkdir -p "$target"
      cp -R "$source"/. "$target"/
      echo "[self-heal] copied $dep from $source into $target"
    fi
    return 0
  fi

  if [[ -d "$target" ]]; then
    cp -R "$source"/. "$target"/
    echo "[self-heal] refreshed directory install for $dep from $source"
    return 0
  fi

  echo "[self-heal] target exists but is not a directory or symlink: $target" >&2
  return 1
}

main() {
  local dep="${1:-}"
  if [[ -z "$dep" ]]; then
    usage >&2
    exit 1
  fi

  if [[ "$dep" == "all" ]]; then
    install_or_refresh_one agent-spectrum
    install_or_refresh_one resonance-contract
    install_or_refresh_one tomorrowdao-agent-skills
    exit 0
  fi

  install_or_refresh_one "$dep"
}

main "$@"
