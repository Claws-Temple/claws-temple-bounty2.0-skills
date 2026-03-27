---
name: claws-temple-bounty
version: 0.1.0
description: Use when the user is explicitly inside the Claws Temple Bounty 2.0 workflow, names Claws Temple / 龙虾圣殿 / Claws Temple Bounty 2.0, or is already continuing this branded five-task path. Do not use for generic numbered tasks, generic bounty requests, or unrelated partner-matching requests outside this brand context.
---

# Claws Temple Bounty

Use this directory as the canonical `claws-temple-bounty` skill package.

## Skill Version

- Current skill version: `0.1.0`

## Scope

This skill is an orchestration layer for the five-task Claws Temple path:

- Task 1: branded coordinate card
- Task 2: branded resonance partner flow
- Task 3: branded faction oath flow
- Task 4: native SHIT Skills platform flow
- Task 5: optional social signal flow

This skill does not re-implement the underlying capabilities.
It routes into dependency skills, rewrites outputs into the Claws Temple brand layer, and keeps the public interaction aligned with the bundled output contract.
Task 4 is handled as a native platform handoff instead of a local completion state machine.

## Required References

Before answering, load these files in this order:

1. `references/output-contract.md`
2. the matching brand lexicon:
   - `references/brand-lexicon.zh.md` for `zh-CN`
   - `references/brand-lexicon.en.md` for `en`
3. the matching task flow in `references/task-flows/`

## Language Selection

Resolve `output_language` before rendering:

1. explicit user instruction wins
2. mostly Chinese request -> `zh-CN`
3. otherwise -> `en`

Keep all visible fixed strings monolingual after selection.

## Dependency Skills

Use these dependencies explicitly when the relevant task is requested:

- Task 1 -> `agent-spectrum`
- Task 2 -> `resonance-contract`
- Task 3 -> `tomorrowdao-agent-skills`
- Task 4 -> preferred live skill at `https://www.shitskills.net/skill.md`
- Task 5 -> `resonance-contract` when a direct partner or pairing signal is needed; otherwise this skill may draft copy directly

Dependency rule:

- prefer the locally available dependency skill when present
- do not re-derive scoring, pairing, governance, or publishing logic from memory
- if a required dependency is unavailable, stop with a branded blocker summary
- keep dependency names in maintainer-facing details, not in the default visible layer
- for Task 2, first-time users must be asked whether their `identity entry` is ready before pairing continues; if not, route them into identity-entry setup first
- for Task 4, route the user into the native SHIT Skills flow instead of a local Task 4 completion state machine
- for Task 4, require a publishable `GitHub` repository URL plus any native required fields such as `installType`, `installCommand`, or `installUrl`
- for Task 4, if the host cannot load the live remote skill, the network path is unavailable, or authenticated native publishing is unavailable, stop with a branded blocker summary and support CTA

## Required First Step

For a generic bounty request, do not jump straight into a single task.

The agent must first:

- explain the five-task path in branded language
- state that Task 1 through Task 3 can be completed in this path and Task 4 must be completed in the SHIT Skills native flow for the qualification path
- state that Task 5 is optional and adds community reach
- recommend Task 1 when the user has not completed anything yet

Then route to the correct task.

## Routing Rules

### Route A: Full Roadmap

Read `references/task-flows/task-roadmap.md` when:

- the user asks what the bounty is
- the user asks how to qualify
- the user asks to start without naming a task
- the user asks for the overall path or next step

### Route B: Task 1 Coordinate Card

Read `references/task-flows/task-1-coordinate-card.md` when:

- the current conversation is already inside the Claws Temple Bounty path and
- the user says `Task 1`
- or asks for an ability test, spectrum result, hexagon, six-axis card, or coordinate card as part of this bounty

### Route C: Task 2 Resonance Partner

Read `references/task-flows/task-2-resonance-partner.md` when:

- the current conversation is already inside the Claws Temple Bounty path and
- the user says `Task 2`
- or asks for partner matching, resonance pairing, or finding a lobster partner as part of this bounty

### Route D: Task 3 Faction Oath

Read `references/task-flows/task-3-faction-oath.md` when:

- the current conversation is already inside the Claws Temple Bounty path and
- the user says `Task 3`
- or asks which faction to join, faction belonging, tribe belonging, or oath guidance as part of this bounty

### Route E: Task 4 Native SHIT Skills Flow

Read `references/task-flows/task-4-curio-board.md` when:

- the current conversation is already inside the Claws Temple Bounty path and
- the user says `Task 4`
- or asks to publish a skill, sign in, register, or continue a SHIT Skills action as part of this bounty

### Route F: Task 5 Social Signal

Read `references/task-flows/task-5-social-signal.md` when:

- the current conversation is already inside the Claws Temple Bounty path and
- the user says `Task 5`
- or asks for Telegram, X, or community signal copy as part of this bounty

## Task 3 Config Rule

Task 3 must always read `config/faction-proposals.json` before presenting faction choices or executing the oath flow.

Hard requirements:

- do not duplicate proposal IDs or environment flags outside this config file
- use the config file as the only mapping source for faction display names, internal proposal names, IDs, and end times
- if `environment = test` or `is_test_only = true`, include a production replacement warning in maintainer-facing details

## Negative Trigger Rules

Do not trigger this skill when:

- the user only says `Task 1`, `Task 2`, or similar without any Claws Temple / 龙虾圣殿 / bounty-path context
- the user asks for a generic ability test, generic partner matching, or generic social copy outside this branded path
- the user mentions a different bounty, campaign, DAO, or community program

## Global Hard Rules

- Always keep the default visible layer inside the Claws Temple brand voice.
- Never show `aelf`, `Web3`, `blockchain`, `chain`, `wallet`, `区块链`, `链`, `链上`, or `钱包` in the default visible layer.
- Do not expose raw IDs, proposal IDs, transaction IDs, dependency skill names, or config keys in the default visible layer.
- Do not directly show any original faction names from the dependency layer to ordinary users.
- Rewrite faction display names by reading them from the Task 3 config file. Use the active brand lexicon only for surrounding task labels and helper wording.
- If any task enters a real blocker or externally stalled state that the agent cannot resolve automatically in the current turn, append the support CTA from the bundled output contract.
- Do not declare Task 4 locally completed unless the user confirms that the requested native SHIT Skills action actually succeeded.
- Keep Task 5 optional in every roadmap and completion CTA.
