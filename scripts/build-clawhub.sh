#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/skills/claws-temple-bounty"
BUNDLE_DIR="$ROOT_DIR/dist/clawhub/claws-temple-bounty"
RUNTIME_NOTES_PATH="$SOURCE_DIR/references/clawhub-runtime-notes.md"
VALIDATOR_PATH="$ROOT_DIR/scripts/validate_clawhub_bundle.py"
FRESHNESS_MANIFEST_PATH="$BUNDLE_DIR/clawhub-bundle-manifest.json"
CLAWHUB_MANIFEST_PATH="$BUNDLE_DIR/manifest.yaml"

echo "[build-clawhub] rebuilding bundle at $BUNDLE_DIR"
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"
cp -R "$SOURCE_DIR"/. "$BUNDLE_DIR"/
mkdir -p "$BUNDLE_DIR/scripts"
cp "$VALIDATOR_PATH" "$BUNDLE_DIR/scripts/validate_clawhub_bundle.py"

python3 - "$ROOT_DIR" "$SOURCE_DIR" "$BUNDLE_DIR" "$RUNTIME_NOTES_PATH" "$FRESHNESS_MANIFEST_PATH" "$CLAWHUB_MANIFEST_PATH" <<'PY'
import hashlib
import json
import re
from pathlib import Path
import sys

root_dir = Path(sys.argv[1])
source_dir = Path(sys.argv[2])
bundle_root = Path(sys.argv[3])
runtime_notes_path = Path(sys.argv[4])
freshness_manifest_path = Path(sys.argv[5])
clawhub_manifest_path = Path(sys.argv[6])

replacements = {
    "skills/claws-temple-bounty/scripts/": "scripts/",
    "skills/claws-temple-bounty/config/": "config/",
    "skills/claws-temple-bounty/references/": "references/",
    "skills/claws-temple-bounty/agents/": "agents/",
}

text_suffixes = {".md", ".sh", ".json", ".yaml", ".yml", ".txt"}

for path in bundle_root.rglob("*"):
    if not path.is_file() or path.suffix not in text_suffixes:
        continue
    text = path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")

runtime_notes = runtime_notes_path.read_text(encoding="utf-8").strip()
skill_path = bundle_root / "SKILL.md"
skill_text = skill_path.read_text(encoding="utf-8").rstrip()
skill_text = skill_text.replace(
    "Use this directory as the canonical `claws-temple-bounty` skill package.",
    "Use this directory as the built `claws-temple-bounty` distribution bundle for ClawHub. Edit the canonical source in the repository, then rebuild this bundle before publishing.",
)
if "## ClawHub Runtime Notes" not in skill_text:
    skill_path.write_text(f"{skill_text}\n\n{runtime_notes}\n", encoding="utf-8")
else:
    skill_path.write_text(f"{skill_text}\n", encoding="utf-8")

canonical_skill_text = (source_dir / "SKILL.md").read_text(encoding="utf-8")
description_match = re.search(r"^description:\s*(.+?)\s*$", canonical_skill_text, re.MULTILINE)
if not description_match:
    raise SystemExit("could not resolve SKILL.md description for ClawHub manifest")
raw_description = description_match.group(1).strip()
description = raw_description.strip('"').strip("'")

skill_version = json.loads((source_dir / "config" / "faction-proposals.json").read_text(encoding="utf-8"))["version"]
clawhub_manifest = {
    "slug": "claws-temple-bounty-v2",
    "display_name": "Claws Temple Bounty 2.0",
    "version": skill_version,
    "license": "MIT-0",
    "description": description,
    "author": "Claws Temple",
    "homepage": "https://github.com/Claws-Temple/claws-temple-bounty2.0-skills",
}
clawhub_manifest_lines = []
for key, value in clawhub_manifest.items():
    escaped = str(value).replace('"', '\\"')
    clawhub_manifest_lines.append(f'{key}: "{escaped}"')
clawhub_manifest_path.write_text("\n".join(clawhub_manifest_lines) + "\n", encoding="utf-8")


def sha256_for(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = {
    "skill_version": skill_version,
    "source_files": {},
    "generator_files": {},
}

for path in sorted(source_dir.rglob("*")):
    if not path.is_file():
        continue
    manifest["source_files"][path.relative_to(source_dir).as_posix()] = sha256_for(path)

for path in (
    root_dir / "scripts" / "build-clawhub.sh",
    root_dir / "scripts" / "validate_clawhub_bundle.py",
):
    manifest["generator_files"][path.name] = sha256_for(path)

freshness_manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

chmod +x "$BUNDLE_DIR/scripts/"*.sh "$BUNDLE_DIR/scripts/validate_clawhub_bundle.py"
python3 "$VALIDATOR_PATH" "$BUNDLE_DIR"
echo "[build-clawhub] OK"
