# Task 1 Example (English)

> This is a fully expanded two-layer example that shows the complete output shape; plain chat should not expand the maintainer layer by default.

## User Summary

You have completed `Task 1: Coordinate Reading`.

```text
┌──────────────────────────────────────────────┐
│  Claws Temple · Coordinate Card              │
│                                              │
│  Memory Axis     ████████░░  8               │
│  Reasoning Axis  ███████░░░  7               │
│  Generation Axis █████████░  9               │
│  Autonomy Axis   ██████░░░░  6               │
│  System Axis     ███████░░░  7               │
│  Mutation Axis   ████████░░  8               │
│                                              │
│  Type: Creation-Mutation                     │
│  Faction lean: The Metamorphs                │
│  Next move: find the partner who completes   │
│  your missing side                           │
└──────────────────────────────────────────────┘
```

If you want, I can take you straight into `Task 2: Resonance Pairing`.

### Blocker Example

If the current environment is missing the Task 1 dependency, the default order should be self-heal first, not immediate Telegram / X fallback:

`The coordinate-reading dependency is still missing, so I will first try to install or activate it for you.`

If the current host cannot do that automatically, the reply should first give explicit install guidance:

`This host cannot auto-install that dependency yet. I will first give you concrete install or upgrade guidance, including the default repo URL and the optional local override, and then we can continue the coordinate reading.`

Only after install or activation still fails should the reply turn into a real blocker:

`The coordinate reading is still blocked by the dependency state. I already tried the dependency self-heal path first, but it still cannot continue from here.`

- `→ If you're stuck here, join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) and share your current step, error, and key context so the community can help troubleshoot.`
- `→ You can also post on [X](https://x.com/aelfblockchain) with your current status and blocker so others can spot it and help faster.`

## Maintainer Details

- dependency_skill: `agent-spectrum`
- route: `task-1-coordinate-card`
- rewritten_output: `brand-layer`
- dependency_source_catalog: `../../config/dependency-sources.json`
- default_repo_url: `https://github.com/aelf-hzz780/agent-spectrum-skill`
- env_override: `CLAWS_TEMPLE_AGENT_SPECTRUM_SOURCE`
