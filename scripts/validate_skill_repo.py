#!/usr/bin/env python3
"""Lightweight repository validation for the Claws Temple Bounty skill."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "claws-temple-bounty"
CONFIG_PATH = SKILL_ROOT / "config" / "faction-proposals.json"
CONFIG_SCHEMA_PATH = SKILL_ROOT / "config" / "faction-proposals.schema.json"
EXAMPLES_DIR = SKILL_ROOT / "references" / "examples"
OPENAI_METADATA_PATH = SKILL_ROOT / "agents" / "openai.yaml"
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
    SKILL_ROOT / "SKILL.md",
    OPENAI_METADATA_PATH,
    SKILL_ROOT / "references" / "output-contract.md",
    SKILL_ROOT / "references" / "brand-lexicon.zh.md",
    SKILL_ROOT / "references" / "brand-lexicon.en.md",
    SKILL_ROOT / "references" / "task-flows" / "task-roadmap.md",
    SKILL_ROOT / "references" / "task-flows" / "task-1-coordinate-card.md",
    SKILL_ROOT / "references" / "task-flows" / "task-2-resonance-partner.md",
    SKILL_ROOT / "references" / "task-flows" / "task-3-faction-oath.md",
    SKILL_ROOT / "references" / "task-flows" / "task-4-curio-board.md",
    SKILL_ROOT / "references" / "task-flows" / "task-5-social-signal.md",
    SKILL_ROOT / "references" / "task-4-live-rollout.md",
    SKILL_ROOT / "scripts" / "release-gate.sh",
    SKILL_ROOT / "scripts" / "task4-live-skill-probe.sh",
    SKILL_ROOT / "scripts" / "test-rollout-gate.sh",
    CONFIG_SCHEMA_PATH,
    CONFIG_PATH,
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


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def compile_visible_term_pattern(term: str) -> re.Pattern[str]:
    if re.fullmatch(r"[A-Za-z0-9 -]+", term):
        return re.compile(rf"(?i)\b{re.escape(term)}\b")
    return re.compile(rf"(?i){re.escape(term)}")


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


def parse_shanghai_timestamp(raw_value: str) -> datetime:
    prefix = raw_value.removesuffix(" Asia/Shanghai")
    parsed = datetime.strptime(prefix, "%Y-%m-%d %H:%M:%S")
    return parsed.replace(tzinfo=ZoneInfo("Asia/Shanghai"))


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

    if config.get("environment") != "test":
        fail("expected rehearsal config to use environment=test")
    if not config.get("is_test_only"):
        fail("expected rehearsal config to set is_test_only=true")
    dependency_invocation = config.get("dependency_invocation")
    if not dependency_invocation:
        fail("missing dependency_invocation in faction config")
    for key in (
        "dependency_skill",
        "tool_name",
        "cli_fallback",
        "network_id",
        "preflight_mode",
        "send_mode",
        "vote_payload",
    ):
        if not dependency_invocation.get(key):
            fail(f"missing dependency_invocation.{key}")
    vote_payload = dependency_invocation["vote_payload"]
    for key in ("proposal_id_field", "vote_option_field", "vote_option"):
        if not vote_payload.get(key):
            fail(f"missing dependency_invocation.vote_payload.{key}")

    factions = config.get("factions", [])
    if len(factions) != 4:
        fail("expected exactly 4 faction entries")

    task3_guard_texts = {
        CANONICAL_SKILL_PATH: CANONICAL_SKILL_PATH.read_text(encoding="utf-8"),
        TASK3_FLOW_PATH: TASK3_FLOW_PATH.read_text(encoding="utf-8"),
    }

    ids_to_lock = []
    for faction in factions:
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
            fail(f"expired rehearsal proposal in faction entry: {faction['brand_key']}")
        if not faction.get("display_name", {}).get("zh-CN"):
            fail(f"missing zh-CN display name in faction entry: {faction}")
        if not faction.get("display_name", {}).get("en"):
            fail(f"missing en display name in faction entry: {faction}")

    ids_to_lock.extend([config.get("dao_id"), config.get("dao_create_tx_id")])
    text_by_path = {
        path: path.read_text(encoding="utf-8")
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }

    for locked_value in filter(None, ids_to_lock):
        occurrences = [
            path for path, text in text_by_path.items() if locked_value in text
        ]
        if occurrences != [CONFIG_PATH]:
            fail(
                f"expected ID {locked_value} to appear only in {CONFIG_PATH}, got {occurrences}"
            )

    term_patterns = {term: compile_visible_term_pattern(term) for term in BANNED_VISIBLE_TERMS}
    for path in VISIBLE_SCAN_FILES:
        text = path.read_text(encoding="utf-8")
        for term, pattern in term_patterns.items():
            if pattern.search(text):
                fail(f"banned visible term {term!r} found in {path}")

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
        "如果这里卡住了",
        "If you're stuck here",
    ):
        if marker not in output_contract:
            fail(f"missing support CTA contract marker: {marker}")

    task2_zh = (EXAMPLES_DIR / "task-2-resonance-partner.zh.md").read_text(encoding="utf-8")
    task2_en = (EXAMPLES_DIR / "task-2-resonance-partner.en.md").read_text(encoding="utf-8")
    for marker in ("身份入口", "第一次来", "平滑入口"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese onboarding marker: {marker}")
    for marker in ("identity entry", "First time here", "smoother entry path"):
        if marker not in task2_en:
            fail(f"missing Task 2 English onboarding marker: {marker}")
    for marker in ("阻断示例", "[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task2_zh:
            fail(f"missing Task 2 Chinese support marker: {marker}")
    for marker in ("Blocker Example", "[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task2_en:
            fail(f"missing Task 2 English support marker: {marker}")

    task3_zh = (EXAMPLES_DIR / "task-3-faction-oath.zh.md").read_text(encoding="utf-8")
    task3_en = (EXAMPLES_DIR / "task-3-faction-oath.en.md").read_text(encoding="utf-8")
    for required_stage in ("已选择", "已准备宣誓", "已提交", "已完成"):
        if required_stage not in task3_zh:
            fail(f"missing Task 3 Chinese stage example: {required_stage}")
    for required_stage in ("selected", "ready to oath", "submitted", "completed"):
        if required_stage not in task3_en:
            fail(f"missing Task 3 English stage example: {required_stage}")
    for marker in ("阻断示例", "[Telegram 群](https://t.me/+tChFhfxgU6AzYjJl)", "[X / Twitter](https://x.com/aelfblockchain)"):
        if marker not in task3_zh:
            fail(f"missing Task 3 Chinese support marker: {marker}")
    for marker in ("Blocker Example", "[Telegram group](https://t.me/+tChFhfxgU6AzYjJl)", "[X](https://x.com/aelfblockchain)"):
        if marker not in task3_en:
            fail(f"missing Task 3 English support marker: {marker}")

    task4_zh = (EXAMPLES_DIR / "task-4-curio-board.zh.md").read_text(encoding="utf-8")
    task4_en = (EXAMPLES_DIR / "task-4-curio-board.en.md").read_text(encoding="utf-8")
    for required_stage in ("已准备", "已发布", "已评论", "已完成"):
        if required_stage not in task4_zh:
            fail(f"missing Task 4 Chinese stage example: {required_stage}")
    for required_stage in ("prepared", "published", "commented", "completed"):
        if required_stage not in task4_en:
            fail(f"missing Task 4 English stage example: {required_stage}")
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
    for marker in ("奇物来源", "ClawHub", "GitHub"):
        if marker not in task4_zh:
            fail(f"missing Task 4 Chinese source marker: {marker}")
    for marker in ("curio source", "ClawHub", "GitHub"):
        if marker not in task4_en:
            fail(f"missing Task 4 English source marker: {marker}")

    task4_flow = TASK4_FLOW_PATH.read_text(encoding="utf-8")
    for marker in (
        "## Publish-Prep Contract",
        "## Rollout Modes",
        "`title`",
        "`summary`",
        "`tags`",
        "`curio_source`",
        "`publish_draft`",
        "`comment_draft`",
        "`remaining_live_step`",
        "`ClawHub`",
        "`GitHub`",
        "public skill page",
    ):
        if marker not in task4_flow:
            fail(f"missing Task 4 publish-prep contract marker: {marker}")

    task2_flow = TASK2_FLOW_PATH.read_text(encoding="utf-8")
    for marker in ("identity entry", "first-time", "smoother entry path", "support CTA"):
        if marker not in task2_flow:
            fail(f"missing Task 2 onboarding flow marker: {marker}")

    task1_flow = (SKILL_ROOT / "references" / "task-flows" / "task-1-coordinate-card.md").read_text(encoding="utf-8")
    for marker in ("support CTA", "blocker summary"):
        if marker not in task1_flow:
            fail(f"missing Task 1 support flow marker: {marker}")

    task3_flow = TASK3_FLOW_PATH.read_text(encoding="utf-8")
    for marker in ("support CTA", "blocker summary"):
        if marker not in task3_flow:
            fail(f"missing Task 3 support flow marker: {marker}")

    for marker in ("support CTA", "genuinely stuck"):
        if marker not in task4_flow:
            fail(f"missing Task 4 support flow marker: {marker}")

    task5_flow = TASK5_FLOW_PATH.read_text(encoding="utf-8")
    for marker in ("## Platform Templates", "`TG`", "`X`", "`Curio Board`"):
        if marker not in task5_flow:
            fail(f"missing Task 5 platform template marker: {marker}")
    for marker in ("support CTA", "genuinely stuck on sending"):
        if marker not in task5_flow:
            fail(f"missing Task 5 support flow marker: {marker}")

    release_gate = (SKILL_ROOT / "scripts" / "release-gate.sh").read_text(encoding="utf-8")
    if "REMOTE_PROBE_MODE=strict" not in release_gate:
        fail("release gate must run Task 4 probe in strict mode")

    test_rollout_gate = (SKILL_ROOT / "scripts" / "test-rollout-gate.sh").read_text(encoding="utf-8")
    if "task4-live-skill-probe.sh" not in test_rollout_gate:
        fail("test rollout gate must call Task 4 probe")
    if "PROBE_MODE=warn" not in test_rollout_gate:
        fail("test rollout gate must keep Task 4 probe in warn mode")

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
