# Claws Temple Bounty Workspace Instructions

This repository packages the `claws-temple-bounty` skill for multiple agent hosts.

## Canonical Sources

- `skills/claws-temple-bounty/SKILL.md`: canonical skill entrypoint
- `skills/claws-temple-bounty/agents/openai.yaml`: OpenAI/Codex metadata
- `skills/claws-temple-bounty/references/output-contract.md`: reply contract
- `skills/claws-temple-bounty/references/brand-lexicon.zh.md`: Chinese brand lexicon
- `skills/claws-temple-bounty/references/brand-lexicon.en.md`: English brand lexicon
- `skills/claws-temple-bounty/references/task-flows/`: task routing and workflow guides
- `skills/claws-temple-bounty/references/examples/`: branded output examples
- `skills/claws-temple-bounty/config/faction-proposals.json`: single source of truth for Task 3 test mapping

## When To Apply

Apply this workflow when the user asks for:

- `Claws Temple Bounty` or `龙虾圣殿 Bounty 2.0`
- Task 1 to Task 5
- the next step inside this bounty path
- coordinate card, hexagon, six-axis, or ability test flows inside this bounty path
- resonance partner or partner matching flows inside this bounty path
- faction oath, faction choice, or tribe/faction belonging inside this bounty path
- SHIT Skills publishing and comment follow-up in the branded `Curio Board / 奇物志` framing inside this bounty path
- optional social signal or community matching follow-up after the main bounty path

Do not apply this workflow for generic numbered tasks, generic bounty requests, or unrelated partner-matching flows outside the Claws Temple path.

## Operating Rule

Load `skills/claws-temple-bounty/SKILL.md` and follow the canonical package exactly.
Do not re-derive the workflow from this `AGENTS.md`.

## Compatibility Layout

- Codex / OpenAI / OpenClaw: `skills/claws-temple-bounty/`
- Claude Code: `.claude/skills/claws-temple-bounty/SKILL.md`
- OpenCode: `.opencode/skills/claws-temple-bounty/SKILL.md`
- Cursor: `.cursor/rules/claws-temple-bounty.mdc` and this root `AGENTS.md`
