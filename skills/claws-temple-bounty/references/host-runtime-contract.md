# Host Runtime Contract

Use this file before any dependency-heavy task in `claws-temple-bounty`.

## Goal

Keep one canonical package usable across Codex, OpenClaw, ClawHub, Claude, OpenCode, and Cursor without pretending that every host has the same runtime powers.

## Shared Skill Root Search Order

Use this exact lookup order before you decide where a dependency should be discovered or installed.

- `CLAWS_TEMPLE_SKILLS_HOME`
- `<workspace>/skills`
- `<workspace>/.agents/skills`
- `~/.agents/skills`
- `~/.openclaw/skills`
- `${CODEX_HOME:-$HOME/.codex}/skills`

## Runtime Axes

Resolve these four axes before you choose a dependency path:

1. `skill roots`
   - use the shared skill-root search order above
2. `session freshness`
   - in OpenClaw, newly installed or upgraded skills normally become active on the next new session
   - after install or upgrade guidance, tell the user to start a new session with `/new`
3. `repo shell capability`
   - helper mode is available only when the current host can actually execute bundled repo scripts with the required local toolchain
   - do not infer helper mode just from the host name
4. `browser/native-action capability`
   - only mention direct browser or native-action continuation when the current turn has already confirmed that capability
   - host name alone is not enough

## Dependency Expansion Rule

OpenClaw and similar hosts may expose only an available-skills list in the prompt.
Do not assume dependency skills were already expanded into context.
When Task 1, Task 2, or Task 3 needs a dependency result, read the dependency package explicitly.

## Fail-Closed Rule

If a task needs a current-turn dependency result and the result does not exist yet:

- do not improvise the business result from memory
- do not collapse the dependency path into a local summary
- return only one of:
  - dependency preflight
  - install or upgrade guidance
  - host-capability blocker
  - dependency blocker

Task-specific consequences:

- Task 1: no dependency result means no hexagon, no coordinate card, no type, and no faction mapping
- Task 2: no current-turn resolved `user ID` means no queue-ready claim
- Task 3: no verified helper prerequisites means no helper-mode promise
- Task 4: no OpenClaw native dependency means no promise that the remote live skill can run there
- Task 5: no confirmed browser capability means draft-first only

This is the repo-wide `fail-closed` baseline: when the runtime proof is missing, the skill must stop at preflight, guidance, or blocker output instead of improvising a fake success path.

## Host-Specific Defaults

- Codex / OpenAI:
  - repo shell helpers are often available
  - `${CODEX_HOME:-$HOME/.codex}/skills` remains the compatibility fallback
- OpenClaw:
  - prefer workspace or managed skill roots over `.codex`
  - prefer local or ClawHub-installed native dependencies over remote `skill.md` assumptions
  - after install or upgrade, remind the user to `/new`
- ClawHub bundle:
  - treat this package as a distribution copy, not the canonical editing surface
