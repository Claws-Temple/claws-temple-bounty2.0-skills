#!/usr/bin/env bash

CLAWS_TEMPLE_RESOLVER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAWS_TEMPLE_SKILL_ROOT="${CLAWS_TEMPLE_SKILL_ROOT:-$(cd "$CLAWS_TEMPLE_RESOLVER_DIR/.." && pwd)}"
CLAWS_TEMPLE_CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CLAWS_TEMPLE_RUNTIME_INSTALL_ROOT="${CLAWS_TEMPLE_RUNTIME_INSTALL_ROOT:-}"
CLAWS_TEMPLE_SKILL_ROOTS=()

claws_temple_current_install_root() {
  local skill_parent
  skill_parent="$(dirname "$CLAWS_TEMPLE_SKILL_ROOT")"
  if [[ "$(basename "$skill_parent")" == "skills" ]]; then
    printf '%s\n' "${skill_parent%/}"
    return 0
  fi
  return 1
}

claws_temple_workspace_root() {
  local install_root="${1:-}"
  if [[ -z "$install_root" ]]; then
    return 1
  fi

  install_root="${install_root%/}"
  if [[ "$install_root" == "$HOME/.agents/skills" || "$install_root" == "$HOME/.openclaw/skills" || "$install_root" == "${CLAWS_TEMPLE_CODEX_HOME%/}/skills" ]]; then
    return 1
  fi

  if [[ "$install_root" == */.agents/skills ]]; then
    printf '%s\n' "${install_root%/.agents/skills}"
    return 0
  fi

  if [[ "$install_root" == */skills ]]; then
    printf '%s\n' "${install_root%/skills}"
    return 0
  fi

  return 1
}

_claws_temple_add_unique_root() {
  local candidate="${1:-}"
  local existing
  if [[ -z "$candidate" ]]; then
    return 0
  fi
  candidate="${candidate%/}"
  for existing in "${CLAWS_TEMPLE_ROOTS[@]:-}"; do
    if [[ "$existing" == "$candidate" ]]; then
      return 0
    fi
  done
  CLAWS_TEMPLE_ROOTS+=("$candidate")
}

claws_temple_list_skill_roots() {
  local current_install_root=""
  local workspace_root=""
  local override_root=""
  local root
  CLAWS_TEMPLE_ROOTS=()

  if [[ -n "${CLAWS_TEMPLE_SKILLS_HOME:-}" ]]; then
    IFS=':' read -r -a CLAWS_TEMPLE_OVERRIDE_ROOTS <<<"$CLAWS_TEMPLE_SKILLS_HOME"
    for override_root in "${CLAWS_TEMPLE_OVERRIDE_ROOTS[@]}"; do
      _claws_temple_add_unique_root "$override_root"
    done
  fi

  current_install_root="$(claws_temple_current_install_root 2>/dev/null || true)"
  workspace_root="$(claws_temple_workspace_root "$current_install_root" 2>/dev/null || true)"

  if [[ -n "$workspace_root" ]]; then
    _claws_temple_add_unique_root "$workspace_root/skills"
    _claws_temple_add_unique_root "$workspace_root/.agents/skills"
  fi

  _claws_temple_add_unique_root "$HOME/.agents/skills"
  _claws_temple_add_unique_root "$HOME/.openclaw/skills"
  _claws_temple_add_unique_root "${CLAWS_TEMPLE_CODEX_HOME%/}/skills"
  _claws_temple_add_unique_root "$current_install_root"

  for root in "${CLAWS_TEMPLE_ROOTS[@]:-}"; do
    printf '%s\n' "$root"
  done
}

claws_temple_default_install_root() {
  local root
  while IFS= read -r root; do
    if [[ -z "$root" ]]; then
      continue
    fi
    if mkdir -p "$root" >/dev/null 2>&1; then
      printf '%s\n' "$root"
      return 0
    fi
  done < <(claws_temple_list_skill_roots)
  return 1
}

claws_temple_runtime_install_root() {
  if [[ -n "${CLAWS_TEMPLE_RUNTIME_INSTALL_ROOT:-}" ]]; then
    printf '%s\n' "$CLAWS_TEMPLE_RUNTIME_INSTALL_ROOT"
    return 0
  fi
  claws_temple_default_install_root
}

claws_temple_resolve_skill_dir() {
  local skill_name="${1:-}"
  local root
  if [[ -z "$skill_name" ]]; then
    return 1
  fi

  while IFS= read -r root; do
    if [[ -d "$root/$skill_name" && ( -f "$root/$skill_name/SKILL.md" || -f "$root/$skill_name/package.json" ) ]]; then
      printf '%s\n' "$root/$skill_name"
      return 0
    fi
  done < <(claws_temple_list_skill_roots)

  return 1
}

claws_temple_init_skill_roots() {
  local configured_skill_root="${1:-}"
  local root
  CLAWS_TEMPLE_SKILL_ROOTS=()
  if [[ -n "$configured_skill_root" ]]; then
    CLAWS_TEMPLE_SKILL_ROOT="$(cd "$configured_skill_root" && pwd)"
  fi
  while IFS= read -r root; do
    CLAWS_TEMPLE_SKILL_ROOTS+=("$root")
  done < <(claws_temple_list_skill_roots)
  CLAWS_TEMPLE_RUNTIME_INSTALL_ROOT="$(claws_temple_default_install_root 2>/dev/null || true)"
}

claws_temple_usage() {
  cat <<'EOF'
Usage:
  bash scripts/skill-root-resolver.sh list-roots
  bash scripts/skill-root-resolver.sh install-root
  bash scripts/skill-root-resolver.sh default-install-root
  bash scripts/skill-root-resolver.sh resolve-skill <skill-name>

Environment:
  CLAWS_TEMPLE_SKILLS_HOME   Override preferred roots with a ':'-separated list.
EOF
}

claws_temple_main() {
  local command="${1:-}"
  case "$command" in
    list-roots)
      if [[ -n "${2:-}" ]]; then
        claws_temple_init_skill_roots "$2"
      fi
      claws_temple_list_skill_roots
      ;;
    install-root)
      if [[ -n "${2:-}" ]]; then
        claws_temple_init_skill_roots "$2"
      fi
      claws_temple_runtime_install_root
      ;;
    default-install-root)
      if [[ -n "${2:-}" ]]; then
        claws_temple_init_skill_roots "$2"
      fi
      claws_temple_default_install_root
      ;;
    resolve-skill)
      if [[ -n "${3:-}" ]]; then
        claws_temple_init_skill_roots "$3"
      fi
      claws_temple_resolve_skill_dir "${2:-}"
      ;;
    ""|-h|--help|help)
      claws_temple_usage
      ;;
    *)
      echo "[skill-root-resolver] unsupported command: $command" >&2
      claws_temple_usage >&2
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  set -euo pipefail
  claws_temple_main "$@"
fi
