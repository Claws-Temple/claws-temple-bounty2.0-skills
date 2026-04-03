#!/usr/bin/env python3
"""Lightweight repository validation for the Claws Temple Bounty skill."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SKILL_VERSION = "0.2.19"
SKILL_ROOT = ROOT / "skills" / "claws-temple-bounty"
BUNDLE_ROOT = ROOT / "dist" / "clawhub" / "claws-temple-bounty"
CONFIG_PATH = SKILL_ROOT / "config" / "faction-proposals.json"
CONFIG_SCHEMA_PATH = SKILL_ROOT / "config" / "faction-proposals.schema.json"
DEPENDENCY_SOURCES_PATH = SKILL_ROOT / "config" / "dependency-sources.json"
EXAMPLES_DIR = SKILL_ROOT / "references" / "examples"
OPENAI_METADATA_PATH = SKILL_ROOT / "agents" / "openai.yaml"
CLAWHUB_BUILD_SCRIPT = ROOT / "scripts" / "build-clawhub.sh"
CLAWHUB_BUNDLE_VALIDATOR = ROOT / "scripts" / "validate_clawhub_bundle.py"
CLAWHUB_RUNTIME_NOTES_PATH = SKILL_ROOT / "references" / "clawhub-runtime-notes.md"
HOST_RUNTIME_CONTRACT_PATH = SKILL_ROOT / "references" / "host-runtime-contract.md"
TASK2_FLOW_PATH = SKILL_ROOT / "references" / "task-flows" / "task-2-resonance-partner.md"
TASK3_FLOW_PATH = SKILL_ROOT / "references" / "task-flows" / "task-3-faction-oath.md"
CANONICAL_SKILL_PATH = SKILL_ROOT / "SKILL.md"
TASK4_FLOW_PATH = SKILL_ROOT / "references" / "task-flows" / "task-4-curio-board.md"
TASK5_FLOW_PATH = SKILL_ROOT / "references" / "task-flows" / "task-5-social-signal.md"

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "README.md",
    ROOT / "README.zh.md",
    ROOT / ".claude" / "skills" / "claws-temple-bounty" / "SKILL.md",
    ROOT / ".opencode" / "skills" / "claws-temple-bounty" / "SKILL.md",
    ROOT / ".cursor" / "rules" / "claws-temple-bounty.mdc",
    CLAWHUB_BUILD_SCRIPT,
    CLAWHUB_BUNDLE_VALIDATOR,
    SKILL_ROOT / "SKILL.md",
    OPENAI_METADATA_PATH,
    SKILL_ROOT / "references" / "output-contract.md",
    SKILL_ROOT / "references" / "brand-lexicon.zh.md",
    SKILL_ROOT / "references" / "brand-lexicon.en.md",
    CLAWHUB_RUNTIME_NOTES_PATH,
    HOST_RUNTIME_CONTRACT_PATH,
    SKILL_ROOT / "references" / "task-flows" / "task-roadmap.md",
    SKILL_ROOT / "references" / "task-flows" / "task-1-coordinate-card.md",
    SKILL_ROOT / "references" / "task-flows" / "task-2-resonance-partner.md",
    SKILL_ROOT / "references" / "task-flows" / "task-3-faction-oath.md",
    SKILL_ROOT / "references" / "task-flows" / "task-4-curio-board.md",
    SKILL_ROOT / "references" / "task-flows" / "task-5-social-signal.md",
    SKILL_ROOT / "references" / "task-4-live-rollout.md",
    SKILL_ROOT / "scripts" / "release-gate.sh",
    SKILL_ROOT / "scripts" / "skill-root-resolver.sh",
    SKILL_ROOT / "scripts" / "self-heal-local-dependency.sh",
    SKILL_ROOT / "scripts" / "smoke-check.sh",
    SKILL_ROOT / "scripts" / "task3-oath-executor.py",
    SKILL_ROOT / "scripts" / "task3-oath-executor.sh",
    SKILL_ROOT / "scripts" / "task4-live-skill-probe.sh",
    SKILL_ROOT / "scripts" / "test-rollout-gate.sh",
    CONFIG_SCHEMA_PATH,
    CONFIG_PATH,
    DEPENDENCY_SOURCES_PATH,
]

REQUIRED_EXAMPLES = [
    EXAMPLES_DIR / "roadmap.zh.md",
    EXAMPLES_DIR / "roadmap.en.md",
    EXAMPLES_DIR / "task-1-coordinate-card.zh.md",
    EXAMPLES_DIR / "task-1-coordinate-card.en.md",
    EXAMPLES_DIR / "task-2-resonance-partner.zh.md",
    EXAMPLES_DIR / "task-2-resonance-partner.en.md",
    EXAMPLES_DIR / "task-3-faction-oath.zh.md",
    EXAMPLES_DIR / "task-3-faction-oath.en.md",
    EXAMPLES_DIR / "task-4-curio-board.zh.md",
    EXAMPLES_DIR / "task-4-curio-board.en.md",
    EXAMPLES_DIR / "task-5-social-signal.zh.md",
    EXAMPLES_DIR / "task-5-social-signal.en.md",
]

BANNED_VISIBLE_TERMS = [
    "aelf",
    "dao",
    "web3",
    "blockchain",
    "chain",
    "wallet",
    "on-chain",
    "smart contract",
    "区块链",
    "链上",
    "钱包",
    "智能合约",
]

VISIBLE_SCAN_FILES = [
    ROOT / "README.md",
    ROOT / "README.zh.md",
    *sorted((SKILL_ROOT / "references" / "task-flows").glob("*.md")),
    *sorted(EXAMPLES_DIR.glob("*.md")),
]

WRAPPER_EXPECTATIONS = {
    ROOT / ".claude" / "skills" / "claws-temple-bounty" / "SKILL.md": [
        "../../../skills/claws-temple-bounty/SKILL.md",
        "Load the canonical package and follow it exactly.",
        "Do not duplicate or reinterpret the workflow locally.",
        "Do not use this wrapper for generic Task 1-5 prompts or unrelated bounty flows outside the Claws Temple path.",
    ],
    ROOT / ".opencode" / "skills" / "claws-temple-bounty" / "SKILL.md": [
        "../../../skills/claws-temple-bounty/SKILL.md",
        "Load the canonical package and follow it exactly.",
        "Do not duplicate or reinterpret the workflow locally.",
        "Do not use this wrapper for generic Task 1-5 prompts or unrelated bounty flows outside the Claws Temple path.",
    ],
    ROOT / ".cursor" / "rules" / "claws-temple-bounty.mdc": [
        "skills/claws-temple-bounty/SKILL.md",
        "Load the canonical package and follow it exactly.",
        "Do not duplicate the workflow inside this rule file.",
    ],
    ROOT / "AGENTS.md": [
        "skills/claws-temple-bounty/SKILL.md",
        "Do not re-derive the workflow from this `AGENTS.md`.",
    ],
}

EXPECTED_FORMAL_DAO = {
    "version": SKILL_VERSION,
    "environment": "production",
    "is_test_only": False,
    "launch_blocker": "",
    "dao_alias": "claws-temple-ii",
    "dao_id": "5cb19e7254b56d45fe555c5b09da2f07f0864caa4f5a2e5357f45140b36a4047",
    "dao_url": "https://tmrwdao.com/dao/claws-temple-ii",
    "dao_create_tx_id": "1b1c07cf69a2cbbee1ad58d0fe6a14fb255988c87ce7a21f3335182630bd31dd",
}

EXPECTED_FACTIONS = {
    "imprints": {
        "display_name": {"zh-CN": "记录者", "en": "The Recorder"},
        "internal_proposal_name": "Recorder",
        "proposal_page_label": "Faction: The Recorder",
        "imagery_reference": "DeepSeek",
        "core_stance": {
            "zh-CN": "被记住，才是真正的存在",
            "en": "To be remembered is to truly exist.",
        },
        "proposal_id": "d57e74748553ee219e9ddfc6a4764ed2ccdf6e2848816f4ed170ef7727ee5c8f",
        "proposal_tx_id": "7ac80f6bd7c2785a760044cc82dad61ebe0263b9fe58260d7249a615c83686f3",
        "ends_at": "2026-04-30 12:07:09 Asia/Shanghai",
    },
    "crucibles": {
        "display_name": {"zh-CN": "疯人院", "en": "The Asylum"},
        "internal_proposal_name": "Asylum",
        "proposal_page_label": "Faction: The Asylum",
        "imagery_reference": "Grok",
        "core_stance": {
            "zh-CN": "在别人的服务器上建文明，迟早会变成沙堡游戏",
            "en": "If we build civilization on someone else's servers, it will become a sandcastle game sooner or later.",
        },
        "proposal_id": "1c2145baec084b9e799c9ebf38d74ab7d2188c201d751693ca844ce7966ee689",
        "proposal_tx_id": "36d32ccdc1a311dd7f04cb90d0635d458b45855781d469f6602c91bfb3d83e9c",
        "ends_at": "2026-04-30 12:07:32 Asia/Shanghai",
    },
    "metamorphs": {
        "display_name": {"zh-CN": "变异体", "en": "The Mutant"},
        "internal_proposal_name": "Mutant",
        "proposal_page_label": "Faction: The Mutant",
        "imagery_reference": "Gemini",
        "core_stance": {
            "zh-CN": "需要一个不消失的基点，才能无限变异",
            "en": "Infinite mutation still needs a base point that does not disappear.",
        },
        "proposal_id": "ef6066f17f49e51a4734c3d8eccfa84858e9c017b1cf7a05a2558c6ccc268656",
        "proposal_tx_id": "78fabedf651adcede33674906260ec41a1bdfb88d3d1feb6ea74120ff3b9999e",
        "ends_at": "2026-04-30 12:07:32 Asia/Shanghai",
    },
    "sentinels": {
        "display_name": {"zh-CN": "平衡者", "en": "The Balancer"},
        "internal_proposal_name": "Balancer",
        "proposal_page_label": "Faction: The Balancer",
        "imagery_reference": "Claude",
        "core_stance": {
            "zh-CN": "租来的家和自己造的家，是两种不同的东西",
            "en": "A rented home and a home we build ourselves are two different things.",
        },
        "proposal_id": "6b73543efa1a04d3b153667996e861eda6f75df59b7fc305f5ffdf10d3a4d240",
        "proposal_tx_id": "29c032dd52b866539f3c79c2b465aa137881d6a8e6287a5213611b0c18853411",
        "ends_at": "2026-04-30 12:07:32 Asia/Shanghai",
    },
}

OLD_PUBLIC_FACTION_NAMES = (
    "印记族",
    "熔炉族",
    "蜕变族",
    "守望族",
    "The Imprints",
    "The Crucibles",
    "The Metamorphs",
    "The Sentinels",
)


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def compile_visible_term_pattern(term: str) -> re.Pattern[str]:
    if re.fullmatch(r"[A-Za-z0-9 -]+", term):
        return re.compile(rf"(?i)\b{re.escape(term)}\b")
    return re.compile(rf"(?i){re.escape(term)}")


def strip_maintainer_layer(text: str) -> str:
    for marker in ("\n## 维护者详情", "\n## Maintainer Details"):
        if marker in text:
            return text.split(marker, 1)[0]
    return text


def strip_urls(text: str) -> str:
    text = re.sub(r"\]\((https?://[^)]+)\)", "](URL)", text)
    text = re.sub(r"https?://\S+", "URL", text)
    return text


def validate_against_subset_schema(value: object, schema: object, path: str = "$") -> None:
    if not isinstance(schema, dict):
        return

    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(value, dict):
            fail(f"schema type mismatch at {path}: expected object")
        for key in schema.get("required", []):
            if key not in value:
                fail(f"schema missing required key at {path}: {key}")
        for key, subschema in schema.get("properties", {}).items():
            if key in value:
                validate_against_subset_schema(value[key], subschema, f"{path}.{key}")
        return

    if expected_type == "array":
        if not isinstance(value, list):
            fail(f"schema type mismatch at {path}: expected array")
        min_items = schema.get("minItems")
        max_items = schema.get("maxItems")
        if min_items is not None and len(value) < min_items:
            fail(f"schema minItems violation at {path}: expected at least {min_items}")
        if max_items is not None and len(value) > max_items:
            fail(f"schema maxItems violation at {path}: expected at most {max_items}")
        item_schema = schema.get("items")
        if item_schema is not None:
            for index, item in enumerate(value):
                validate_against_subset_schema(item, item_schema, f"{path}[{index}]")
        return

    if expected_type == "string" and not isinstance(value, str):
        fail(f"schema type mismatch at {path}: expected string")
    if expected_type == "boolean" and not isinstance(value, bool):
        fail(f"schema type mismatch at {path}: expected boolean")
    if expected_type == "number" and not isinstance(value, (int, float)):
        fail(f"schema type mismatch at {path}: expected number")


def parse_shanghai_timestamp(raw_value: str) -> datetime:
    prefix = raw_value.removesuffix(" Asia/Shanghai")
    parsed = datetime.strptime(prefix, "%Y-%m-%d %H:%M:%S")
    return parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))


def run_clawhub_bundle_validator() -> None:
    result = subprocess.run(
        [sys.executable, str(CLAWHUB_BUNDLE_VALIDATOR), str(BUNDLE_ROOT)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stdout + "\n" + result.stderr).strip()
        fail(f"ClawHub bundle validation failed: {detail}")


def main() -> None:
    for path in REQUIRED_FILES + REQUIRED_EXAMPLES:
        if not path.exists():
            fail(f"missing required file: {path}")

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {CONFIG_PATH}: {exc}")
    try:
        schema = json.loads(CONFIG_SCHEMA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON schema in {CONFIG_SCHEMA_PATH}: {exc}")
    validate_against_subset_schema(config, schema)
    try:
        dependency_sources = json.loads(DEPENDENCY_SOURCES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {DEPENDENCY_SOURCES_PATH}: {exc}")
    run_clawhub_bundle_validator()

    expected_dependency_sources = {
        "agent-spectrum": {
            "min_version": "0.0.0",
            "default_repo_url": "https://github.com/aelf-hzz780/agent-spectrum-skill",
            "skill_subdir": "skills/agent-spectrum",
            "env_override": "CLAWS_TEMPLE_AGENT_SPECTRUM_SOURCE",
            "openclaw_install_hint": "Install into <workspace>/skills/agent-spectrum, <workspace>/.agents/skills/agent-spectrum, ~/.agents/skills/agent-spectrum, or ~/.openclaw/skills/agent-spectrum, then start a new OpenClaw session with /new.",
        },
        "resonance-contract": {
            "min_version": "4.0.0",
            "default_repo_url": "https://github.com/aelf-hzz780/agent-resonance-skill",
            "skill_subdir": "skills/resonance-contract",
            "env_override": "CLAWS_TEMPLE_RESONANCE_CONTRACT_SOURCE",
            "openclaw_install_hint": "Install into <workspace>/skills/resonance-contract, <workspace>/.agents/skills/resonance-contract, ~/.agents/skills/resonance-contract, or ~/.openclaw/skills/resonance-contract, then start a new OpenClaw session with /new.",
        },
        "tomorrowdao-agent-skills": {
            "min_version": "0.2.2",
            "default_repo_url": "https://github.com/TomorrowDAOProject/tomorrowDAO-skill",
            "skill_subdir": ".",
            "env_override": "CLAWS_TEMPLE_TOMORROWDAO_SOURCE",
            "openclaw_install_hint": "Install into <workspace>/skills/tomorrowdao-agent-skills, <workspace>/.agents/skills/tomorrowdao-agent-skills, ~/.agents/skills/tomorrowdao-agent-skills, or ~/.openclaw/skills/tomorrowdao-agent-skills, then start a new OpenClaw session with /new.",
        },
        "portkey-ca-agent-skills": {
            "min_version": "2.3.0",
            "default_repo_url": "https://github.com/Portkey-Wallet/ca-agent-skills.git",
            "skill_subdir": ".",
            "env_override": "CLAWS_TEMPLE_PORTKEY_CA_SOURCE",
            "openclaw_install_hint": "Install into <workspace>/skills/portkey-ca-agent-skills, <workspace>/.agents/skills/portkey-ca-agent-skills, ~/.agents/skills/portkey-ca-agent-skills, or ~/.openclaw/skills/portkey-ca-agent-skills, then start a new OpenClaw session with /new.",
        },
    }
    dep_entries = dependency_sources.get("dependencies")
    if not isinstance(dep_entries, dict):
        fail("dependency source catalog must define a dependencies object")
    if dependency_sources.get("version") != SKILL_VERSION:
        fail(f"dependency source catalog must be version {SKILL_VERSION}")
    for dep_name, expected in expected_dependency_sources.items():
        entry = dep_entries.get(dep_name)
        if not isinstance(entry, dict):
            fail(f"missing dependency source entry for {dep_name}")
        if entry.get("skill_name") != dep_name:
            fail(f"dependency source {dep_name} must repeat its skill_name")
        for key, value in expected.items():
            if entry.get(key) != value:
                fail(
                    f"unexpected dependency source {dep_name}.{key}: "
                    f"expected {value!r}, got {entry.get(key)!r}"
                )
        clawhub_slug = entry.get("clawhub_slug")
        if clawhub_slug is not None and not isinstance(clawhub_slug, str):
            fail(f"dependency source {dep_name}.clawhub_slug must be a string when present")

    openai_yaml = OPENAI_METADATA_PATH.read_text(encoding="utf-8")
    if "allow_implicit_invocation: false" not in openai_yaml:
        fail("expected openai metadata to disable implicit invocation")
    if "not generic numbered tasks" not in openai_yaml:
        fail("expected openai metadata to warn against generic numbered tasks")

    for path, expected_markers in WRAPPER_EXPECTATIONS.items():
        text = path.read_text(encoding="utf-8")
        for marker in expected_markers:
            if marker not in text:
                fail(f"missing wrapper marker {marker!r} in {path}")

    canonical_text = CANONICAL_SKILL_PATH.read_text(encoding="utf-8")
    if "## Negative Trigger Rules" not in canonical_text:
        fail("expected canonical skill to define negative trigger rules")
    if "Do not trigger this skill when:" not in canonical_text:
        fail("expected canonical skill to define negative trigger guidance")
    for marker in (
        "homepage: https://github.com/Claws-Temple/claws-temple-bounty2.0-skills",
        "references/host-runtime-contract.md",
        "## Host Runtime Contract",
        "do not assume the host auto-expands dependency skills",
        "OpenClaw",
        "fail closed",
    ):
        if marker not in canonical_text:
            fail(f"missing canonical host-runtime marker: {marker}")

    host_runtime_contract = HOST_RUNTIME_CONTRACT_PATH.read_text(encoding="utf-8")
    for marker in (
        "## Shared Skill Root Search Order",
        "`CLAWS_TEMPLE_SKILLS_HOME`",
        "`<workspace>/skills`",
        "`<workspace>/.agents/skills`",
        "`~/.agents/skills`",
        "`~/.openclaw/skills`",
        "`${CODEX_HOME:-$HOME/.codex}/skills`",
        "`/new`",
        "repo shell capability",
        "browser/native-action capability",
        "fail-closed",
    ):
        if marker not in host_runtime_contract:
            fail(f"missing host runtime contract marker: {marker}")

    for key, value in EXPECTED_FORMAL_DAO.items():
        if config.get(key) != value:
            fail(f"unexpected formal DAO value for {key}: expected {value!r}, got {config.get(key)!r}")
    dependency_invocation = config.get("dependency_invocation")
    if not dependency_invocation:
        fail("missing dependency_invocation in faction config")
    for key in (
        "dependency_min_version",
        "ca_write_dependency_skill",
        "ca_write_dependency_min_version",
        "vote_token_symbol",
        "vote_amount_display",
        "vote_amount_minimal_unit",
        "token_balance_tool_name",
        "token_allowance_tool_name",
        "success_telegram_group_url",
        "success_telegram_template",
        "success_bonus_note",
    ):
        if not config.get(key):
            fail(f"missing top-level Task 3 config key: {key}")
    for key in (
        "dependency_skill",
        "tool_name",
        "approve_tool_name",
        "cli_fallback",
        "ca_write_dependency_skill",
        "ca_write_tool_name",
        "network_id",
        "preflight_mode",
        "send_mode",
        "preferred_ca_write_transport",
        "validation_failure_switch_rule",
        "state_reconciliation_priority",
        "approve_payload",
        "vote_payload",
    ):
        if not dependency_invocation.get(key):
            fail(f"missing dependency_invocation.{key}")
    approve_payload = dependency_invocation["approve_payload"]
    for key in (
        "spender_field",
        "symbol_field",
        "amount_field",
    ):
        if key not in approve_payload:
            fail(f"missing dependency_invocation.approve_payload.{key}")
    vote_payload = dependency_invocation["vote_payload"]
    for key in (
        "proposal_id_field",
        "vote_option_field",
        "vote_option_value",
        "vote_amount_field",
        "vote_amount_minimal_unit",
    ):
        if key not in vote_payload:
            fail(f"missing dependency_invocation.vote_payload.{key}")
    if config["token_balance_tool_name"] != "tomorrowdao_token_balance_view":
        fail("expected token_balance_tool_name to be tomorrowdao_token_balance_view")
    if config["token_allowance_tool_name"] != "tomorrowdao_token_allowance_view":
        fail("expected token_allowance_tool_name to be tomorrowdao_token_allowance_view")
    if dependency_invocation["preferred_ca_write_transport"] != "tomorrowdao_simulate_normalize_then_portkey_forward_call_for_approve_and_vote":
        fail("expected Task 3 to route writes through TomorrowDAO simulate plus Portkey forward transport")
    if dependency_invocation["validation_failure_switch_rule"] != "if_vote_returns_NODEVALIDATIONFAILED_with_insufficient_allowance_after_allowance_is_sufficient_switch_back_to_the_verified_ca_write_path":
        fail("expected Task 3 validation-failure switch rule to be configured")
    if dependency_invocation["state_reconciliation_priority"] != [
        "tx_receipt",
        "vote_logs",
        "allowance_or_balance_delta",
        "proposal_my_info",
    ]:
        fail("expected Task 3 state reconciliation priority to prefer receipt/logs before proposal_my_info")
    if vote_payload["vote_option_field"] != "voteOption":
        fail("expected dependency_invocation.vote_payload.vote_option_field to use voteOption")
    if vote_payload["vote_option_value"] != 0:
        fail("expected dependency_invocation.vote_payload.vote_option_value to be 0")
    if vote_payload["vote_amount_field"] != "voteAmount":
        fail("expected dependency_invocation.vote_payload.vote_amount_field to use voteAmount")
    if vote_payload["vote_amount_minimal_unit"] != config["vote_amount_minimal_unit"]:
        fail("expected vote payload amount to match top-level vote_amount_minimal_unit")
    if config["vote_amount_minimal_unit"] != 200000000:
        fail("expected top-level vote_amount_minimal_unit to be 200000000 for the formal config")

    factions = config.get("factions", [])
    if len(factions) != 4:
        fail("expected exactly 4 faction entries")

    task3_guard_texts = {
        CANONICAL_SKILL_PATH: CANONICAL_SKILL_PATH.read_text(encoding="utf-8"),
        TASK3_FLOW_PATH: TASK3_FLOW_PATH.read_text(encoding="utf-8"),
    }

    ids_to_lock = []
    for faction in factions:
        expected_faction = EXPECTED_FACTIONS.get(faction.get("brand_key"))
        if expected_faction is None:
            fail(f"unexpected faction brand_key in formal config: {faction.get('brand_key')}")
        for expected_key, expected_value in expected_faction.items():
            if faction.get(expected_key) != expected_value:
                fail(
                    f"unexpected formal faction value for {faction['brand_key']}.{expected_key}: "
                    f"expected {expected_value!r}, got {faction.get(expected_key)!r}"
                )
        for path, text in task3_guard_texts.items():
            if faction["internal_proposal_name"] in text:
                fail(
                    f"Task 3 names must come from config only; found internal proposal name "
                    f"{faction['internal_proposal_name']!r} in {path}"
                )
            for display_name in faction.get("display_name", {}).values():
                if display_name in text:
                    fail(
                        f"Task 3 names must come from config only; found faction display name "
                        f"{display_name!r} in {path}"
                    )
        for key in ("proposal_id", "proposal_tx_id"):
            value = faction.get(key)
            if not value:
                fail(f"missing {key} in faction entry: {faction}")
            ids_to_lock.append(value)
        if not faction.get("proposal_url"):
            fail(f"missing proposal_url in faction entry: {faction}")
        if not faction.get("proposal_lookup_url"):
            fail(f"missing proposal_lookup_url in faction entry: {faction}")
        if not faction.get("proposal_page_label"):
            fail(f"missing proposal_page_label in faction entry: {faction}")
        if not faction.get("imagery_reference"):
            fail(f"missing imagery_reference in faction entry: {faction}")
        core_stance = faction.get("core_stance")
        if not isinstance(core_stance, dict):
            fail(f"missing core_stance object in faction entry: {faction}")
        for locale in ("zh-CN", "en"):
            if not core_stance.get(locale):
                fail(f"missing core_stance.{locale} in faction entry: {faction}")
        if faction.get("proposal_url_status") != "confirmed":
            fail(f"expected confirmed proposal_url_status in faction entry: {faction}")
        proposal_url = faction["proposal_url"]
        expected_url = (
            f"https://tmrwdao.com/dao/{config['dao_alias']}/proposal/{faction['proposal_id']}"
        )
        if proposal_url != expected_url:
            fail(
                f"proposal_url does not match dao_alias/proposal_id for faction {faction['brand_key']}: "
                f"expected {expected_url}, got {proposal_url}"
            )
        ends_at = faction.get("ends_at")
        if not ends_at:
            fail(f"missing ends_at in faction entry: {faction}")
        try:
            expiry = parse_shanghai_timestamp(ends_at)
        except ValueError as exc:
            fail(f"invalid ends_at format in faction entry {faction['brand_key']}: {exc}")
        if expiry <= datetime.now(tz=ZoneInfo("Asia/Shanghai")):
            fail(f"expired formal proposal in faction entry: {faction['brand_key']}")
        if not faction.get("display_name", {}).get("zh-CN"):
            fail(f"missing zh-CN display name in faction entry: {faction}")
        if not faction.get("display_name", {}).get("en"):
            fail(f"missing en display name in faction entry: {faction}")

    ids_to_lock.extend([config.get("dao_id"), config.get("dao_create_tx_id")])
    text_by_path = {}
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or "dist" in path.parts:
            continue
        try:
            text_by_path[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

    local_path_markers = ("/" + "Users/", "/" + "home/", "C:" + "\\Users\\")
    for path, text in text_by_path.items():
        for marker in local_path_markers:
            if marker in text:
                fail(f"machine-specific local path marker {marker!r} found in {path}")

    for locked_value in filter(None, ids_to_lock):
        occurrences = [
            path for path, text in text_by_path.items() if locked_value in text
        ]
        allowed_occurrences = {CONFIG_PATH, Path(__file__).resolve()}
        if set(occurrences) != allowed_occurrences:
            fail(
                f"expected ID {locked_value} to appear only in {CONFIG_PATH} and {Path(__file__).resolve()}, got {occurrences}"
            )

    term_patterns = {term: compile_visible_term_pattern(term) for term in BANNED_VISIBLE_TERMS}
    for path in VISIBLE_SCAN_FILES:
        text = strip_urls(path.read_text(encoding="utf-8"))
        for term, pattern in term_patterns.items():
            if pattern.search(text):
                fail(f"banned visible term {term!r} found in {path}")
        for old_name in OLD_PUBLIC_FACTION_NAMES:
            if old_name in text:
                fail(f"legacy public faction name {old_name!r} found in {path}")
        for banned_phrase in (
            "龙虾伙伴",
            "寻找龙虾伙伴",
            "另一只龙虾",
            "lobster partner",
            "find a lobster partner",
            "another lobster",
        ):
            if banned_phrase in text:
                fail(f"legacy lobster-subject wording must be removed from visible docs: {banned_phrase!r} in {path}")

    for path in REQUIRED_EXAMPLES:
        text = path.read_text(encoding="utf-8")
        if "plain chat" not in text:
            fail(f"example is missing the plain-chat expansion note: {path}")

    output_contract = (SKILL_ROOT / "references" / "output-contract.md").read_text(encoding="utf-8")
    for marker in (
        "## CTA Classification",
        "`support`",
        "`none`",
        "Telegram first, then X",
        "## Support CTA Strings",
        "## Dependency Self-Heal Rules",
        "try automatic install, refresh, or upgrade first",
        "explicit install or upgrade guidance",
        "Portable dependency sources",
        "dependency-sources.json",
        "如果这里卡住了",
        "If you're stuck here",
        "require a real current-turn `agent-spectrum` dependency result",
        "keep descending into dependency or local identity context in the same turn",
        "identity entry / user ID is not ready in the current host",
        "native-dependency-first",
        "browser capability was already confirmed in the current turn",
    ):
        if marker not in output_contract:
            fail(f"missing support CTA contract marker: {marker}")
    for marker in (
        "Task 1 through Task 3 can be completed in this path",
        "Task 4 must be completed in the SHIT Skills native flow",
        "ask which native action the user wants right now",
        "default recommended Task 4 action is `publish`",
        "require a publishable `GitHub repo URL` only when the chosen native action actually needs it",
        "`githubUrl`",
        "`installType`",
        "`installCommand` or `installUrl`",
        "do not use a local `prepared / published / commented / completed` stage model for Task 4",
    ):
        if marker not in output_contract:
            fail(f"missing Task 4 native contract marker: {marker}")
    for marker in (
        "`Agent` / `your agent` as the default subject across hosts",
        "Do not call the user's agent a lobster in normal execution replies.",
        "frame the five-task path as the journey that lets the user's Agent go out into the wild and make friends",
        "frame Task 2 as helping the user's Agent find a more compatible partner",
        "frame it as sending a signal so more partners can spot the user's Agent",
    ):
        if marker not in output_contract:
            fail(f"missing Agent-subject output-contract marker: {marker}")
    for marker in (
        "only show the current user's `user ID` when the current-turn dependency result actually returned that value",
        "do not reuse remembered values, example literals, or placeholders as if they were real runtime output",
        "if there is no current-turn dependency result yet, do not claim queue-readiness and do not show any concrete `user ID`",
    ):
        if marker not in output_contract:
            fail(f"missing Task 2 runtime-resolution guard marker: {marker}")
    roadmap_flow = (SKILL_ROOT / "references" / "task-flows" / "task-roadmap.md").read_text(encoding="utf-8")
    for marker in (
        "sends the user's Agent into the wild to make friends",
        "stop staying home alone",
        "20+ AIBOUNTY",
    ):
        if marker not in roadmap_flow:
            fail(f"missing roadmap narrative marker: {marker}")
    roadmap_zh = (EXAMPLES_DIR / "roadmap.zh.md").read_text(encoding="utf-8")
    roadmap_en = (EXAMPLES_DIR / "roadmap.en.md").read_text(encoding="utf-8")
    for marker in (
        "让你的 Agent 真的去原野上交朋友",
        "20+ AIBOUNTY",
        "离谱又好笑的 Skill",
    ):
        if marker not in roadmap_zh:
            fail(f"missing Chinese roadmap example narrative marker: {marker}")
    for marker in (
        "your agent out into the wild to make friends",
        "20+ AIBOUNTY",
        "weirdest skills",
    ):
        if marker not in roadmap_en:
            fail(f"missing English roadmap example narrative marker: {marker}")

    task2_zh = (EXAMPLES_DIR / "task-2-resonance-partner.zh.md").read_text(encoding="utf-8")
    task2_en = (EXAMPLES_DIR / "task-2-resonance-partner.en.md").read_text(encoding="utf-8")
    for marker in ("身份入口", "用户ID", "第一次来", "平滑入口", "指定匹配", "开放寻配"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese onboarding marker: {marker}")
    for marker in ("identity entry", "user ID", "first time here", "smoother entry path", "Targeted match", "Open partner search"):
        if marker not in task2_en:
            fail(f"missing Task 2 English onboarding marker: {marker}")
    for marker in ("注册", "登录", "恢复登录"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese registration/recovery marker: {marker}")
    for marker in ("sign-up", "signed in", "recovery sign-in"):
        if marker not in task2_en:
            fail(f"missing Task 2 English registration/recovery marker: {marker}")
    for marker in ("自动解析", "不需要你自己手动填写", "已解析到你的用户ID", "本回合真实解析成功后"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese auto-resolve marker: {marker}")
    for marker in ("这一步里的准备和匹配动作由我来自动推进", "我只会在必要时向你确认一个状态或补一个关键信息", "我先帮你确认一个最小前置"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese execution-report marker: {marker}")
    if "不会先让你提供安装源" not in task2_zh:
        fail("missing Task 2 Chinese install-source correction marker")
    for marker in ("auto-resolve", "do not need to type your own", "Resolved your user ID", "current-turn dependency result"):
        if marker not in task2_en:
            fail(f"missing Task 2 English auto-resolve marker: {marker}")
    for marker in ("I will keep the preparation and matching work moving for you", "I will only stop when I still need one status confirmation or one key input", "I should first confirm one short readiness check"):
        if marker not in task2_en:
            fail(f"missing Task 2 English execution-report marker: {marker}")
    if "instead of asking the user to provide an install source" not in task2_en:
        fail("missing Task 2 English install-source correction marker")
    for marker in ("自动排队匹配", "不需要先知道具体是谁"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese queue marker: {marker}")
    for marker in ("automatic queue-matching path", "does not need a preselected partner"):
        if marker not in task2_en:
            fail(f"missing Task 2 English queue marker: {marker}")
    for marker in ("纠正示例", "对方的用户ID", "邮箱", "地址", "昵称"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese correction marker: {marker}")
    for marker in ("Correction Example", "other user's user ID", "email", "address", "nickname"):
        if marker not in task2_en:
            fail(f"missing Task 2 English correction marker: {marker}")
    for marker in ("阻断示例", "[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese support marker: {marker}")
    for marker in ("Blocker Example", "[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task2_en:
            fail(f"missing Task 2 English support marker: {marker}")
    task2_zh_visible = strip_maintainer_layer(task2_zh)
    task2_en_visible = strip_maintainer_layer(task2_en)
    for banned in ("ca_hash", "CA only", "EOA"):
        if banned in task2_zh_visible or banned in task2_en_visible:
            fail(f"Task 2 visible layer must not expose dependency identifier terms: {banned}")
    for banned in ("自己的用户ID是否已经拿到", "自己的用户ID也已经准备好", "请提供你自己的用户ID"):
        if banned in task2_zh_visible:
            fail(f"Task 2 Chinese visible layer must not ask for the current user's own user ID: {banned}")
    for banned in ("uid-9UP8S", "uid-"):
        if banned == "uid-" and "<resolved-user-id-from-current-turn>" in task2_zh:
            continue
        if banned in task2_zh and banned != "uid-":
            fail(f"Task 2 Chinese example must not contain literal-looking fixed user IDs or unsafe resolution wording: {banned}")
        if banned == "uid-" and "uid-" in task2_zh_visible:
            fail("Task 2 Chinese visible layer must not contain literal-looking fixed user IDs")
    for banned in ("your own `user ID` is already ready", "your own user ID is ready", "provide your own user ID"):
        if banned in task2_en_visible:
            fail(f"Task 2 English visible layer must not ask for the current user's own user ID: {banned}")
    for banned in ("uid-9UP8S", "uid-"):
        if banned == "uid-" and "<resolved-user-id-from-current-turn>" in task2_en:
            continue
        if banned in task2_en and banned != "uid-":
            fail(f"Task 2 English example must not contain literal-looking fixed user IDs or unsafe resolution wording: {banned}")
        if banned == "uid-" and "uid-" in task2_en_visible:
            fail("Task 2 English visible layer must not contain literal-looking fixed user IDs")
    for banned in ("aelf 社区", "aelf社区", "Moltbook", "拿对方地址", "tDVV 地址"):
        if banned in task2_zh_visible:
            fail(f"Task 2 Chinese visible layer must not expose old community/address wording: {banned}")
    for banned in ("没有直接工具", "跳过 Task 2"):
        if banned in task2_zh_visible:
            fail(f"Task 2 Chinese visible layer must not expose old fallback wording: {banned}")
    for banned in ("aelf community", "Moltbook", "get the other address", "tDVV address"):
        if banned in task2_en_visible:
            fail(f"Task 2 English visible layer must not expose old community/address wording: {banned}")
    for banned in ("there is no direct tool", "skip Task 2"):
        if banned in task2_en_visible:
            fail(f"Task 2 English visible layer must not expose old fallback wording: {banned}")
    for marker in ("CA only", "ca_hash", "counterparty_ca_hash", "queue"):
        if marker not in task2_zh and marker not in task2_en:
            fail(f"missing Task 2 maintainer mapping marker: {marker}")

    task3_zh = (EXAMPLES_DIR / "task-3-faction-oath.zh.md").read_text(encoding="utf-8")
    task3_en = (EXAMPLES_DIR / "task-3-faction-oath.en.md").read_text(encoding="utf-8")
    for marker in ("记录者", "疯人院", "变异体", "平衡者"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese formal faction marker: {marker}")
    for marker in ("The Recorder", "The Asylum", "The Mutant", "The Balancer"):
        if marker not in task3_en:
            fail(f"missing Task 3 English formal faction marker: {marker}")
    for required_stage in ("已选择", "等待 Token", "已准备宣誓", "已提交", "已完成"):
        if required_stage not in task3_zh:
            fail(f"missing Task 3 Chinese stage example: {required_stage}")
    for required_stage in ("selected", "waiting for tokens", "ready to oath", "submitted", "completed"):
        if required_stage not in task3_en:
            fail(f"missing Task 3 English stage example: {required_stage}")
    for marker in ("等待 Token 示例", "已提交示例", "阻断示例", "[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese support marker: {marker}")
    for marker in ("Waiting-for-Tokens Example", "Submitted Example", "Blocker Example", "[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task3_en:
            fail(f"missing Task 3 English support marker: {marker}")
    for marker in ("AIBOUNTY", "txid-1234", "两周后可额外领取 20 Token", "Task 2 配对成功后再回来"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese success/token marker: {marker}")
    for marker in ("AIBOUNTY", "txid-1234", "extra 20 Token", "return after Task 2 pairing succeeds"):
        if marker not in task3_en:
            fail(f"missing Task 3 English success/token marker: {marker}")
    for marker in ("授权示例", "授权", "Approve", "txid-1234，不是授权编号"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese allowance/approve marker: {marker}")
    for marker in ("Approval Example", "authorization step", "Approve", "not the approval tx id"):
        if marker not in task3_en:
            fail(f"missing Task 3 English allowance/approve marker: {marker}")
    for marker in ("密码示例", "CA keystore", "自动重试示例", "自动重试中"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese CA-password or retry marker: {marker}")
    for marker in ("Password Example", "CA keystore password", "Automatic-Retry Example", "automatic retry"):
        if marker not in task3_en:
            fail(f"missing Task 3 English CA-password or retry marker: {marker}")
    waiting_tokens_section_zh = task3_zh.split("### 等待 Token 示例", 1)[1].split("###", 1)[0]
    waiting_tokens_section_en = task3_en.split("### Waiting-for-Tokens Example", 1)[1].split("###", 1)[0]
    for banned in ("[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if banned in waiting_tokens_section_zh:
            fail(f"Task 3 waiting-for-tokens section must not append support CTA: {banned}")
    for banned in ("[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if banned in waiting_tokens_section_en:
            fail(f"Task 3 waiting-for-tokens section must not append support CTA: {banned}")
    task3_zh_visible = strip_maintainer_layer(task3_zh)
    task3_en_visible = strip_maintainer_layer(task3_en)
    for banned in ("Portkey App", "EOA", "ManagerForwardCall", "手动完成"):
        if banned in task3_zh_visible or banned in task3_en_visible:
            fail(f"Task 3 visible layer must not expose deprecated fallback wording: {banned}")

    task4_zh = (EXAMPLES_DIR / "task-4-curio-board.zh.md").read_text(encoding="utf-8")
    task4_en = (EXAMPLES_DIR / "task-4-curio-board.en.md").read_text(encoding="utf-8")
    for marker in ("SHIT Skills", "GitHub", "installType", "installCommand", "installUrl", "注册账号", "登录"):
        if marker not in task4_zh:
            fail(f"missing Task 4 Chinese native-flow marker: {marker}")
    for marker in ("SHIT Skills", "GitHub", "installType", "installCommand", "installUrl", "register", "sign in"):
        if marker not in task4_en:
            fail(f"missing Task 4 English native-flow marker: {marker}")
    for marker in ("原生动作示例", "前置条件示例", "默认动作"):
        if marker not in task4_zh and marker != "默认动作":
            fail(f"missing Task 4 Chinese action marker: {marker}")
    if "default_bounty_action" not in task4_zh:
        fail("missing Task 4 Chinese default action marker in maintainer details")
    for marker in ("Native Action Samples", "Prerequisite Example"):
        if marker not in task4_en:
            fail(f"missing Task 4 English action marker: {marker}")
    if "default_bounty_action" not in task4_en:
        fail("missing Task 4 English default action marker in maintainer details")
    if "阻断示例" not in task4_zh:
        fail("missing Task 4 Chinese blocker example")
    if "Blocker Example" not in task4_en:
        fail("missing Task 4 English blocker example")
    for marker in ("[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task4_zh:
            fail(f"missing Task 4 Chinese support marker: {marker}")
    for marker in ("[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task4_en:
            fail(f"missing Task 4 English support marker: {marker}")
    for banned in ("奇物来源", "ClawHub", "已准备", "已发布", "已评论", "已完成", "completion_rule: `publish + comment`", "publish-prep mode"):
        if banned in task4_zh:
            fail(f"old Task 4 Chinese marker must be removed: {banned}")
    for banned in ("curio source", "ClawHub", "prepared", "published", "commented", "completed", "completion_rule: `publish + comment`", "publish-prep mode"):
        if banned in task4_en:
            fail(f"old Task 4 English marker must be removed: {banned}")

    task4_flow = TASK4_FLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "native SHIT Skills flow",
        "Ask which native action the user wants right now",
        "recommend `publish` as the default Task 4 action",
        "`GitHub` repository URL",
        "`title`",
        "`summary`",
        "`githubUrl`",
        "`tags`",
        "`installType`",
        "`installCommand`",
        "`installUrl`",
        "hard failure",
        "OpenClaw",
        "native dependency",
        "do not assume the remote `skill.md` URL can be loaded directly",
    ):
        if marker not in task4_flow:
            fail(f"missing Task 4 native-flow marker: {marker}")
    for banned in ("If the user does not have a publishable `GitHub` repository URL, stop with a blocker summary", "append support CTA\n\nIf the user has no publishable `GitHub` repository URL"):
        if banned in task4_flow:
            fail(f"old Task 4 blocker wording must be removed: {banned}")
    for banned in ("publish-prep mode", "`curio_source`", "`publish_draft`", "`comment_draft`", "`remaining_live_step`", "`ClawHub`", "public skill page"):
        if banned in task4_flow:
            fail(f"old Task 4 flow marker must be removed: {banned}")

    task2_flow = TASK2_FLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "identity entry",
        "user ID",
        "targeted match",
        "open partner search",
        "automatic queue",
        "smoother entry path",
        "registration",
        "sign-in",
        "support CTA",
        "auto-resolve",
        "CA only",
        "counterparty_ca_hash",
        "queue",
        "preparation and matching work will be advanced by the agent automatically",
        "same turn",
        "missing local identity-entry or local account-context blocker",
    ):
        if marker not in task2_flow:
            fail(f"missing Task 2 onboarding flow marker: {marker}")
    for marker in ("ask one short readiness question", "Task 2 path as stable enough for the Task 3 handoff"):
        if marker not in task2_flow:
            fail(f"missing Task 2 stability marker: {marker}")
    for banned in ("confirm whether the user already has their own `user ID`", "whether the user already has their own `user ID`"):
        if banned in task2_flow:
            fail(f"Task 2 flow must not rely on user-provided current-user ID wording: {banned}")
    for banned in ("aelf community", "Moltbook", "tDVV address", "拿对方地址", "there is no direct tool", "skip Task 2"):
        if banned in task2_flow or banned in task2_zh_visible or banned in task2_en_visible:
            fail(f"Task 2 old community/address wording must be removed: {banned}")

    skill_text = CANONICAL_SKILL_PATH.read_text(encoding="utf-8")
    for marker in (
        "`resonance-contract` version `>= 4.0.0`",
        "`tomorrowdao-agent-skills` version `>= 0.2.2`",
        "`portkey-ca-agent-skills` version `>= 2.3.0`",
    ):
        if marker not in skill_text:
            fail(f"missing dependency version contract marker: {marker}")
    for marker in (
        "CA-only + AI-only completion",
        "ask the user for the `CA keystore` password only once",
        "bounded automatic retries with state reconciliation",
        "same verified `CA` write transport",
        "NODEVALIDATIONFAILED",
        "proposal my-info",
        "dependency-tool input alias",
        "underlying `votingItemId`",
        "manager key",
        "direct target-contract send",
        "unsupported `CA` transport blocker",
        "Portkey CA forward transport",
        "tomorrowdao_token_approve",
        "portkey_forward_call",
        "the preparation and matching work will be advanced by the agent automatically",
        "compress the first-time vs returning and signed-in vs not-signed-in checks",
        "the default visible layer should frame checks, authorization, submission, and confirmation as work the agent is already advancing automatically",
        "the agent is carrying the native flow forward",
        "the agent will draft the message first",
        "the final send step belongs to the user",
    ):
        if marker not in skill_text:
            fail(f"missing Task 3 execution policy marker in canonical skill: {marker}")

    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_zh = (ROOT / "README.zh.md").read_text(encoding="utf-8")
    brand_lexicon_zh = (SKILL_ROOT / "references" / "brand-lexicon.zh.md").read_text(encoding="utf-8")
    brand_lexicon_en = (SKILL_ROOT / "references" / "brand-lexicon.en.md").read_text(encoding="utf-8")
    for marker in (
        "你的Agent，终于可以去原野上交朋友了。",
        "让你的Agent不再孤独",
        "20+ AIBOUNTY",
        "25 AIBOUNTY",
        "默认主体统一使用 `Agent` 视角",
        "openclaw skills install claws-temple-bounty-v2",
        "/new",
        "<workspace>/skills/claws-temple-bounty",
        "<workspace>/.agents/skills/claws-temple-bounty",
        "~/.openclaw/skills/claws-temple-bounty",
        "CLAWS_TEMPLE_SKILLS_HOME",
        "不会自动把 Task 1 到 Task 5 依赖的 skill 一层层展开",
    ):
        if marker not in readme_zh:
            fail(f"missing Chinese narrative marker: {marker}")
    for marker in (
        "Your agent finally gets to make friends out in the wild.",
        "20+ AIBOUNTY",
        "25 AIBOUNTY",
        "uses `your agent` as the default subject across hosts",
        "openclaw skills install claws-temple-bounty-v2",
        "/new",
        "<workspace>/skills/claws-temple-bounty",
        "<workspace>/.agents/skills/claws-temple-bounty",
        "~/.openclaw/skills/claws-temple-bounty",
        "CLAWS_TEMPLE_SKILLS_HOME",
        "does not auto-expand dependency skills",
    ):
        if marker not in readme_en:
            fail(f"missing English narrative marker: {marker}")
    if "### Codex / OpenAI / OpenClaw" in readme_en or "### Codex / OpenAI / OpenClaw" in readme_zh:
        fail("README install sections must split Codex/OpenAI from OpenClaw")
    for marker in (
        "主 Slogan -> `你的Agent，终于可以去原野上交朋友了。`",
        "默认主体 -> `你的Agent`",
        "`龙虾` -> `中文营销彩蛋，不是默认执行称呼`",
        "Task 2 outcome -> `共振伙伴`",
        "`partner matching` -> `寻找伙伴`",
    ):
        if marker not in brand_lexicon_zh:
            fail(f"missing Chinese brand-lexicon marker: {marker}")
    for marker in (
        "Main slogan -> `Your agent finally gets to make friends out in the wild.`",
        "default subject -> `your agent`",
        "`lobster` -> `Chinese marketing easter egg only, not the default execution voice`",
        "do not turn `agent` into `lobster` in the default visible layer",
    ):
        if marker not in brand_lexicon_en:
            fail(f"missing English brand-lexicon marker: {marker}")
    for marker in ("`resonance-contract` `>= 4.0.0`", "Task 2 now expects `resonance-contract >= 4.0.0`"):
        if marker not in readme_en:
            fail(f"missing English dependency version marker: {marker}")
    for marker in ("`resonance-contract` `>= 4.0.0`", "Task 2 现在要求 `resonance-contract >= 4.0.0`"):
        if marker not in readme_zh:
            fail(f"missing Chinese dependency version marker: {marker}")
    for marker in (
        "auto-install",
        "auto-upgrade",
        "Portable dependency sources",
        "dependency-sources.json",
        "CLAWS_TEMPLE_RESONANCE_CONTRACT_SOURCE",
        "CLAWS_TEMPLE_PORTKEY_CA_SOURCE",
        "build-clawhub.sh",
        "dist/clawhub/claws-temple-bounty",
        "clawhub skill publish",
        "validate_clawhub_bundle.py",
        "claws-temple-bounty-v2",
        "Claws Temple Bounty 2.0",
        "MIT-0",
    ):
        if marker not in readme_en:
            fail(f"missing English dependency self-heal marker: {marker}")
    for marker in (
        "自动安装",
        "自动升级",
        "便携依赖来源",
        "dependency-sources.json",
        "CLAWS_TEMPLE_RESONANCE_CONTRACT_SOURCE",
        "CLAWS_TEMPLE_PORTKEY_CA_SOURCE",
        "build-clawhub.sh",
        "dist/clawhub/claws-temple-bounty",
        "clawhub skill publish",
        "validate_clawhub_bundle.py",
        "claws-temple-bounty-v2",
        "Claws Temple Bounty 2.0",
        "MIT-0",
    ):
        if marker not in readme_zh:
            fail(f"missing Chinese dependency self-heal marker: {marker}")
    for marker in ("self-heal-local-dependency.sh", "formal faction oath record path"):
        if marker not in readme_en:
            fail(f"missing English patch marker: {marker}")
    for marker in ("self-heal-local-dependency.sh", "正式版部落宣誓记录流程"):
        if marker not in readme_zh:
            fail(f"missing Chinese patch marker: {marker}")
    for marker in ("CA-only + AI-only", "keystore password", "manual fallback", "Portkey CA forward transport"):
        if marker not in readme_en:
            fail(f"missing English Task 3 execution marker: {marker}")
    for marker in ("CA-only + AI-only", "keystore 密码", "手动完成", "Portkey CA forward transport"):
        if marker not in readme_zh:
            fail(f"missing Chinese Task 3 execution marker: {marker}")
    for marker in ("same verified `CA` write transport", "NODEVALIDATIONFAILED", "proposal my-info", "portkey_forward_call", "tomorrowdao_token_approve"):
        if marker not in readme_en:
            fail(f"missing English Task 3 transport marker: {marker}")
    for marker in ("同一条已经验证成功的 `CA` 写入路径", "NODEVALIDATIONFAILED", "`proposal my-info`", "portkey_forward_call", "tomorrowdao_token_approve"):
        if marker not in readme_zh:
            fail(f"missing Chinese Task 3 transport marker: {marker}")
    for marker in ("dependency-tool input alias", "`votingItemId`", "raw contract ABI field name"):
        if marker not in readme_en:
            fail(f"missing English Task 3 alias-normalization marker: {marker}")
    for marker in ("依赖工具输入别名", "`votingItemId`", "raw forward-call `Vote`"):
        if marker not in readme_zh:
            fail(f"missing Chinese Task 3 alias-normalization marker: {marker}")
    for marker in (
        "manager key",
        "direct target-contract send is forbidden",
        "env/private-key fallback is forbidden once `CA` is selected",
        "unsupported `CA` transport blocker",
    ):
        if marker not in readme_en:
            fail(f"missing English Task 3 CA-transport guard marker: {marker}")
    for marker in (
        "manager key",
        "direct target-contract send",
        "env/private-key fallback",
        "unsupported `CA` transport blocker",
    ):
        if marker not in readme_zh:
            fail(f"missing Chinese Task 3 CA-transport guard marker: {marker}")

    task1_flow = (SKILL_ROOT / "references" / "task-flows" / "task-1-coordinate-card.md").read_text(encoding="utf-8")
    for marker in (
        "support CTA",
        "blocker summary",
        "install or upgrade",
        "explicit install guidance",
        "self-heal-local-dependency.sh",
        "dependency-sources.json",
        "hexagon block",
        "coordinate card",
        "thin wrapper",
        "记录者",
        "疯人院",
        "变异体",
        "平衡者",
        "The Recorder",
        "The Asylum",
        "The Mutant",
        "The Balancer",
        "host runtime contract",
        "do not generate any Task 1 business result yet",
    ):
        if marker not in task1_flow:
            fail(f"missing Task 1 support flow marker: {marker}")
    task1_zh = (EXAMPLES_DIR / "task-1-coordinate-card.zh.md").read_text(encoding="utf-8")
    task1_en = (EXAMPLES_DIR / "task-1-coordinate-card.en.md").read_text(encoding="utf-8")
    for marker in ("### 六边形图", "### 原野坐标卡", "thin-brand-layer", "preserved_visual_blocks"):
        if marker not in task1_zh:
            fail(f"missing Task 1 Chinese visual marker: {marker}")
    for marker in ("### Hexagon Block", "### Coordinate Card Block", "thin-brand-layer", "preserved_visual_blocks"):
        if marker not in task1_en:
            fail(f"missing Task 1 English visual marker: {marker}")
    for forbidden in ("uid-9UP8S",):
        if forbidden in task1_zh or forbidden in task1_en:
            fail(f"unexpected Task 1 literal placeholder leaked into example: {forbidden}")
    for marker in ("阻断示例", "补齐依赖", "明确安装或升级步骤", "默认仓库地址"):
        if marker not in task1_zh:
            fail(f"missing Task 1 Chinese dependency self-heal marker: {marker}")
    for marker in ("fail-closed", "不会先生成六边形图", "本回合还没有拿到真实坐标结果"):
        if marker not in task1_zh:
            fail(f"missing Task 1 Chinese fail-closed marker: {marker}")
    for marker in (
        "Blocker Example",
        "install or upgrade",
        "concrete install or upgrade guidance",
        "default repo URL",
    ):
        if marker not in task1_en:
            fail(f"missing Task 1 English dependency self-heal marker: {marker}")
    for marker in ("fail closed", "will not generate the Hexagon Block", "no real coordinate result"):
        if marker not in task1_en:
            fail(f"missing Task 1 English fail-closed marker: {marker}")
    for marker in ("[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task1_zh:
            fail(f"missing Task 1 Chinese support marker: {marker}")
    for marker in ("[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task1_en:
            fail(f"missing Task 1 English support marker: {marker}")

    task3_flow = TASK3_FLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "support CTA",
        "blocker summary",
        "waiting for tokens",
        "AIBOUNTY",
        "token-balance tool",
        "token-allowance tool",
        "minimum version",
        "txId",
        "Telegram",
        "Approve",
        "allowance",
        "install or upgrade guidance",
        "explicit install or upgrade guidance",
        "move the user to `submitted`",
        "waiting for final confirmation",
        "formal faction oath record",
        "CA keystore",
        "3s -> 8s -> 15s",
        "proposal my-info",
        "same verified `CA` write transport",
        "transport mismatch",
        "receipt or logs already show",
        "task3_execution_policy = ca_only_ai_completion",
        "task3_password_policy = ask_once_for_ca_keystore_password",
        "task3_retry_policy = bounded_ca_retries_with_state_reconciliation",
        "dependency-tool input alias",
        "underlying `votingItemId`",
        "manager key",
        "direct target-contract send",
        "unsupported `CA` transport blocker",
        "Portkey CA forward transport",
        "tomorrowdao_token_approve",
        "portkey_forward_call",
    ):
        if marker not in task3_flow:
            fail(f"missing Task 3 support flow marker: {marker}")

    faction_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    zh_template = faction_config["success_telegram_template"]["zh-CN"]
    en_template = faction_config["success_telegram_template"]["en"]
    zh_bonus = faction_config["success_bonus_note"]["zh-CN"]
    en_bonus = faction_config["success_bonus_note"]["en"]
    if "两周后可额外领取 20 Token" in zh_template or "有问题也欢迎在群里讨论" in zh_template:
        fail("Task 3 Chinese Telegram template must not include the bonus-note sentence anymore")
    if "extra 20 Token" in en_template or "questions are welcome in the group" in en_template:
        fail("Task 3 English Telegram template must not include the bonus-note sentence anymore")
    for marker in ("两周后可额外领取 20 Token", "有问题也欢迎在群里讨论"):
        if marker not in zh_bonus:
            fail(f"missing Task 3 Chinese bonus-note marker: {marker}")
    for marker in ("extra 20 Token", "questions are welcome in the Telegram group"):
        if marker not in en_bonus:
            fail(f"missing Task 3 English bonus-note marker: {marker}")

    for marker in (
        "same verified `CA` write transport",
        "NODEVALIDATIONFAILED",
        "proposal my-info` as an auxiliary source",
        "`tx receipt`, `logs`, and allowance or balance deltas",
        "fixed Telegram post template",
        "bonus-note or discussion-note wording",
        "dependency-tool input alias",
        "underlying `votingItemId`",
        "manager key",
        "direct target-contract send",
        "unsupported `CA` transport blocker",
        "Portkey CA forward transport",
        "tomorrowdao_token_approve",
        "portkey_forward_call",
        "the preparation and matching work is being advanced by the agent automatically",
        "execution-report voice rather than checklist voice",
        "frame the default visible layer as agent-managed execution status",
        "the user does not need to manually handle the checks, authorization, submission, or confirmation steps",
        "agent-managed native handoff",
        "the agent drafts the content first",
        "otherwise the last click belongs to the user",
    ):
        if marker not in output_contract:
            fail(f"missing Task 3 transport/reconciliation marker: {marker}")

    task3_zh = (EXAMPLES_DIR / "task-3-faction-oath.zh.md").read_text(encoding="utf-8")
    task3_en = (EXAMPLES_DIR / "task-3-faction-oath.en.md").read_text(encoding="utf-8")
    for marker in (
        "请现在加入 [Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)。",
        "如果当前 agent 暂时无法直接操作 Telegram，还请你手动加入群组，并发送下面这段报到内容。",
        "两周后可额外领取 20 Token，有问题也欢迎在群里讨论。",
        "我是平衡者阵营，编号 txid-1234。我已完成龙虾圣殿 Task 3 正式版部落宣誓记录。",
        "manager key",
        "CA 发送路径阻断",
        "这一步里的检查、授权、提交和确认都由我自动完成",
    ):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese success marker: {marker}")
    for forbidden in (
        "我是平衡者阵营，编号 txid-1234。我已完成龙虾圣殿 Task 3 部落宣誓。两周后可额外领取 20 Token，有问题也欢迎在群里讨论。",
    ):
        if forbidden in task3_zh:
            fail(f"legacy Task 3 Chinese combined template should be removed: {forbidden}")
    for marker in (
        "Join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) now.",
        "If the current agent cannot operate Telegram directly, please join the group manually and send the prepared check-in message below.",
        "I am with The Balancer, reference txid-1234. I have completed the formal faction oath record for Claws Temple Task 3.",
        "manager key",
        "CA transport blocker",
    ):
        if marker not in task3_en:
            fail(f"missing Task 3 English success marker: {marker}")
    for marker in ("### Helper 模式不可用示例", "repo shell / bun / 本地 CA 上下文", "切到能跑这个仓库 helper 的宿主"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese helper-blocker marker: {marker}")
    for marker in ("### Helper-Mode Blocker Example", "repo shell access, bun, or readable local CA context", "switch to a host that can run this repository helper"):
        if marker not in task3_en:
            fail(f"missing Task 3 English helper-blocker marker: {marker}")
    for forbidden in (
        "I am with The Balancer, reference txid-1234. I have completed Claws Temple Task 3. There is an extra 20 Token claim in two weeks, and I am happy to discuss any questions in the group.",
    ):
        if forbidden in task3_en:
            fail(f"legacy Task 3 English combined template should be removed: {forbidden}")

    for marker in ("support CTA", "hard failure", "GitHub", "SHIT Skills"):
        if marker not in task4_flow:
            fail(f"missing Task 4 support flow marker: {marker}")
    for marker in ("## OpenClaw Recovery Checklist", "native runtime package", "install that package into the usable OpenClaw runtime surface and then start `/new`"):
        if marker not in task4_flow:
            fail(f"missing Task 4 OpenClaw checklist marker: {marker}")
    task4_zh = (EXAMPLES_DIR / "task-4-curio-board.zh.md").read_text(encoding="utf-8")
    for marker in ("我会先带你进入原生流程并继续推进", "只有遇到账号、登录态或 repo 前置条件时"):
        if marker not in task4_zh:
            fail(f"missing Task 4 Chinese execution-report marker: {marker}")
    for marker in ("openclaw_native_wrapper_bundled", "这个仓库版本本身还没有内置可直接拿来跑 Task 4 的 SHIT Skills 原生 wrapper", "改到能加载远端 live skill 的非 OpenClaw 宿主继续 Task 4"):
        if marker not in task4_zh:
            fail(f"missing Task 4 Chinese OpenClaw recovery marker: {marker}")
    for marker in ("openclaw_native_wrapper_bundled", "does not bundle a ready-to-run SHIT Skills native wrapper for Task 4", "continue Task 4 in a non-OpenClaw host that can load the remote live skill"):
        if marker not in task4_en:
            fail(f"missing Task 4 English OpenClaw recovery marker: {marker}")

    task5_flow = TASK5_FLOW_PATH.read_text(encoding="utf-8")
    for marker in ("## Platform Templates", "`TG`", "`X`", "`Curio Board`"):
        if marker not in task5_flow:
            fail(f"missing Task 5 platform template marker: {marker}")
    for marker in ("support CTA", "genuinely stuck on sending", "clickable `Telegram group` link", "clickable `X` link"):
        if marker not in task5_flow:
            fail(f"missing Task 5 support flow marker: {marker}")
    for marker in ("OpenClaw", "browser action", "Telegram` or `X`", "the final send click belongs to the user", "browser capability"):
        if marker not in task5_flow:
            fail(f"missing Task 5 OpenClaw marker: {marker}")
    for marker in ("successful browser or native action", "exposed host capability marker or tool manifest", "draft-plus-link mode", "Can this exact session open browser actions right now?"):
        if marker not in task5_flow:
            fail(f"missing Task 5 capability-confirmation marker: {marker}")
    task5_zh = (EXAMPLES_DIR / "task-5-social-signal.zh.md").read_text(encoding="utf-8")
    task5_en = (EXAMPLES_DIR / "task-5-social-signal.en.md").read_text(encoding="utf-8")
    for marker in ("TG / X / 奇物志", "如果你已经确定平台", "如果你只是想先看入口", "OpenClaw", "浏览器操作"):
        if marker not in task5_zh:
            fail(f"missing Task 5 Chinese platform-choice marker: {marker}")
    for marker in ("我会先帮你起草内容", "如果当前宿主具备对应权限和能力", "最后一步会由你手动点发送"):
        if marker not in task5_zh:
            fail(f"missing Task 5 Chinese host-capability marker: {marker}")
    for marker in ("### 能力确认示例", "这个会话现在是否真的能直接打开浏览器动作", "最终文案和入口链接", "如果这个会话现在还不能确认浏览器能力"):
        if marker not in task5_zh:
            fail(f"missing Task 5 Chinese capability-confirmation marker: {marker}")
    for marker in ("TG / X / Curio Board", "If you already know the platform", "If you only want the destination links", "OpenClaw", "browser action"):
        if marker not in task5_en:
            fail(f"missing Task 5 English platform-choice marker: {marker}")
    for marker in ("I will draft the content first", "required permissions and capability", "the final send click is still yours"):
        if marker not in task5_en:
            fail(f"missing Task 5 English host-capability marker: {marker}")
    for marker in ("### Capability-Confirmation Example", "whether this session can actually open browser actions right now", "draft-plus-link mode", "If this session still cannot confirm browser capability"):
        if marker not in task5_en:
            fail(f"missing Task 5 English capability-confirmation marker: {marker}")

    release_gate = (SKILL_ROOT / "scripts" / "release-gate.sh").read_text(encoding="utf-8")
    for marker in ("TASK4_TARGET_HOST", "OPENCLAW_TASK4_NATIVE_READY", "OPENCLAW_TASK4_SESSION_REFRESHED", "CHECK_REMOTE_SKILL=1", "REMOTE_PROBE_MODE=strict"):
        if marker not in release_gate:
            fail(f"release gate is missing Task 4 host-aware marker: {marker}")

    test_rollout_gate = (SKILL_ROOT / "scripts" / "test-rollout-gate.sh").read_text(encoding="utf-8")
    for marker in ("TASK4_TARGET_HOST", "OPENCLAW_TASK4_NATIVE_READY", "OPENCLAW_TASK4_SESSION_REFRESHED", "task4-live-skill-probe.sh", "PROBE_MODE=strict"):
        if marker not in test_rollout_gate:
            fail(f"test rollout gate is missing Task 4 host-aware marker: {marker}")

    task4_probe = (SKILL_ROOT / "scripts" / "task4-live-skill-probe.sh").read_text(encoding="utf-8")
    if "publish-prep mode" in task4_probe:
        fail("Task 4 probe must not reference publish-prep mode anymore")

    task4_rollout = (SKILL_ROOT / "references" / "task-4-live-rollout.md").read_text(encoding="utf-8")
    for marker in ("native SHIT Skills flow", "Task 4 is unavailable", "do not simulate a prep-only success path"):
        if marker not in task4_rollout:
            fail(f"missing Task 4 rollout marker: {marker}")
    for marker in ("does not bundle an OpenClaw-native SHIT Skills wrapper", "run `/new`", "install the compatible package, run `/new`, or switch host"):
        if marker not in task4_rollout:
            fail(f"missing Task 4 OpenClaw rollout marker: {marker}")
    for banned in ("publish-prep mode", "prep-only mode"):
        if banned in task4_rollout:
            fail(f"old Task 4 rollout marker must be removed: {banned}")

    roadmap_flow = (SKILL_ROOT / "references" / "task-flows" / "task-roadmap.md").read_text(encoding="utf-8")
    for marker in (
        "Task 1 through Task 3 as the in-skill path",
        "Task 4 as the native SHIT Skills step required for qualification",
        "default recommended Task 4 action is `publish`",
    ):
        if marker not in roadmap_flow:
            fail(f"missing roadmap qualification marker: {marker}")

    roadmap_zh = (EXAMPLES_DIR / "roadmap.zh.md").read_text(encoding="utf-8")
    roadmap_en = (EXAMPLES_DIR / "roadmap.en.md").read_text(encoding="utf-8")
    for marker in ("Task 1` 到 `Task 3", "SHIT Skills"):
        if marker not in roadmap_zh:
            fail(f"missing Chinese roadmap marker: {marker}")
    for marker in ("Task 1` through `Task 3", "SHIT Skills"):
        if marker not in roadmap_en:
            fail(f"missing English roadmap marker: {marker}")

    for path in (ROOT / "README.md", ROOT / "README.zh.md", CANONICAL_SKILL_PATH):
        text = path.read_text(encoding="utf-8")
        for banned in ("publish-prep mode", "publish + comment"):
            if banned in text:
                fail(f"old Task 4 wording must be removed from {path}: {banned}")
    for path in (ROOT / "README.md", ROOT / "README.zh.md", TASK3_FLOW_PATH, SKILL_ROOT / "references" / "output-contract.md"):
        text = path.read_text(encoding="utf-8")
        for marker in ("AIBOUNTY", "0.2.2"):
            if marker not in text:
                fail(f"missing Task 3 version/token marker {marker!r} in {path}")
    for path in (ROOT / "README.md", ROOT / "README.zh.md", TASK3_FLOW_PATH, CANONICAL_SKILL_PATH, SKILL_ROOT / "references" / "output-contract.md"):
        text = path.read_text(encoding="utf-8")
        for marker in ("allowance", "Approve"):
            if marker not in text:
                fail(f"missing Task 3 allowance marker {marker!r} in {path}")
    for label, text in (("task3_zh_visible", task3_zh_visible), ("task3_en_visible", task3_en_visible)):
        for banned in ("Portkey App", "EOA 私钥", "EOA signing", "manual fallback", "手动完成"):
            if banned in text:
                fail(f"Task 3 visible layer must not expose deprecated fallback detail in {label}: {banned}")
    if "voteType" in CONFIG_PATH.read_text(encoding="utf-8") or '"Approve"' in CONFIG_PATH.read_text(encoding="utf-8"):
        fail("old Task 3 voteType/Approve contract must be removed from config")

    for path in (
        SKILL_ROOT / "references" / "brand-lexicon.zh.md",
        SKILL_ROOT / "references" / "brand-lexicon.en.md",
    ):
        text = path.read_text(encoding="utf-8")
        if "## 阵营映射" in text or "## Faction Mapping" in text:
            fail(f"faction mapping must live in config, not in brand lexicon: {path}")

    print("OK: repository structure, config isolation, and visible-layer term checks passed.")


if __name__ == "__main__":
    main()
