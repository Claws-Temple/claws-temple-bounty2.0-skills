[中文](README.zh.md)

# Claws Temple Bounty 2.0 Skill

This repository packages a multi-host orchestration skill for `Claws Temple Bounty 2.0`.

It guides the full five-task path:

1. Generate a branded coordinate card.
2. Complete Resonance Pairing and find a resonance partner.
3. Complete the Faction Oath.
4. Enter the native SHIT Skills flow and complete the platform action you need.
5. Optionally send a social signal for wider community matching.

## What This Skill Does

- keeps all user-facing replies inside the `Claws Temple / 龙虾圣殿` brand layer
- supports both `zh-CN` and `en`
- routes explicit bounty-path requests into the correct next task
- orchestrates existing dependency skills instead of re-implementing them
- checks whether first-time users need identity-entry setup before Task 2 pairing continues
- routes Task 4 into the native SHIT Skills flow with `GitHub` as the only publishable source
- collects native Task 4 fields such as `installType`, `installCommand`, and `installUrl` when needed
- uses a single faction config file for the current Task 3 rehearsal setup
- keeps Task 5 optional and non-blocking

## Host Layout

- Codex / OpenAI / OpenClaw: `skills/claws-temple-bounty/`
- Claude Code: `.claude/skills/claws-temple-bounty/SKILL.md`
- OpenCode: `.opencode/skills/claws-temple-bounty/SKILL.md`
- Cursor: `.cursor/rules/claws-temple-bounty.mdc`

## Repository Structure

- `skills/claws-temple-bounty/`: canonical skill package
- `skills/claws-temple-bounty/agents/openai.yaml`: OpenAI/Codex metadata
- `.claude/skills/claws-temple-bounty/`: Claude wrapper
- `.opencode/skills/claws-temple-bounty/`: OpenCode wrapper
- `.cursor/rules/claws-temple-bounty.mdc`: Cursor rule wrapper
- `AGENTS.md`: workspace routing hints

## Quick Install

### Codex / OpenAI / OpenClaw

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/claws-temple-bounty "${CODEX_HOME:-$HOME/.codex}/skills/claws-temple-bounty"
```

Verify:

- Ask the host to run: `Use $claws-temple-bounty to show the Claws Temple Bounty roadmap.`

### Claude Code

Open this repository as the workspace and use:

- `.claude/skills/claws-temple-bounty/SKILL.md`

Enable and verify:

- Keep this repository as the active workspace so the wrapper can resolve the canonical relative path.
- Ask for: `Show me the Claws Temple Bounty roadmap and recommend the next task.`

### OpenCode

Use:

- `.opencode/skills/claws-temple-bounty/SKILL.md`

Enable and verify:

- Open this repository as the active workspace.
- Ask for: `Start the Claws Temple Bounty path and explain Task 1 to Task 5.`

### Cursor

Use either of:

- `AGENTS.md` at the workspace root
- `.cursor/rules/claws-temple-bounty.mdc`

Enable and verify:

- Open this repository in Cursor so the rule file and canonical package live in the same workspace.
- Ask for: `Continue the Claws Temple Bounty path from Task 2 into Task 3.`

## Required Dependencies

- Local skill: `agent-spectrum`
- Local skill: `resonance-contract`
- Local skill: `tomorrowdao-agent-skills`
- Remote live skill for Task 4: `https://www.shitskills.net/skill.md`

If you want dependency preflight to fail hard instead of warning, run smoke check with `STRICT_DEPS=1`.

## Dependency Bootstrap

Before treating this skill as runnable, verify that the three local dependency skills are already present under `$CODEX_HOME/skills`.

```bash
ls "${CODEX_HOME:-$HOME/.codex}/skills"
```

If any dependency is missing, the current repo-level smoke check can still pass in warning mode, but Task 1-3 will stop with a blocker at runtime.

## Usage

```text
Use $claws-temple-bounty to guide this user through the next Claws Temple Bounty task.
```

```text
Use $claws-temple-bounty to start from Task 1 and return a branded coordinate card.
```

```text
Use $claws-temple-bounty to help this user finish the Faction Oath flow in English.
```

```text
Use $claws-temple-bounty to continue from Task 2 and take this user into Task 3.
```

```text
Use $claws-temple-bounty to help this user finish only Task 4 and tell them exactly what is still missing.
```

## Qualification Note

Task 1 through Task 3 can be completed inside this skill.
Task 4 must be completed in the native `SHIT Skills` flow for the `Claws Temple Bounty 2.0` qualification path.
Task 5 is optional and adds community reach.

## Maintainer Note

Task 3 currently ships with rehearsal-only faction mapping.
Before any production launch, replace `skills/claws-temple-bounty/config/faction-proposals.json`.
Task 4 live publish also depends on network reachability to `https://www.shitskills.net/skill.md`.

## Task 4 Rollout Plan

- Testing window:
  - run `bash skills/claws-temple-bounty/scripts/test-rollout-gate.sh`
  - require the Task 4 live-skill probe to pass
  - if probe or native auth publish is unavailable, treat Task 4 as unavailable for that window
- Production window:
  - run `bash skills/claws-temple-bounty/scripts/release-gate.sh`
  - require Task 4 live-skill probe and native auth publish to pass before treating Task 4 as available

Maintainer runbook:

- `skills/claws-temple-bounty/references/task-4-live-rollout.md`

## Validation

```bash
python3 scripts/validate_skill_repo.py
```

## Smoke Check

```bash
bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

Optional stricter variants:

```bash
STRICT_DEPS=1 bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

```bash
CHECK_REMOTE_SKILL=1 bash skills/claws-temple-bounty/scripts/smoke-check.sh
```

Hard release gate:

```bash
bash skills/claws-temple-bounty/scripts/release-gate.sh
```

Testing rollout gate:

```bash
bash skills/claws-temple-bounty/scripts/test-rollout-gate.sh
```
