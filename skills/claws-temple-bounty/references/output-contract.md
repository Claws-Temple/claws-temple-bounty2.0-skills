# Claws Temple Bounty Output Contract

Version: `0.1.0`

Use this file for every visible reply rendered through `claws-temple-bounty`.

## Language Selection

Resolve `output_language` before rendering:

1. explicit user instruction wins
2. if the latest user request is mainly Chinese, use `zh-CN`
3. otherwise use `en`

## Monolingual Rule

- Once `output_language` is selected, keep visible fixed strings monolingual.
- Proper nouns, URLs, repository names, skill names, and file paths may remain as-is in maintainer-facing details.

## Two-Layer Response Contract

Every reply should be structured as two layers:

- default visible layer:
  - `zh-CN`: `普通用户摘要`
  - `en`: `User Summary`
- expanded maintainer layer:
  - `zh-CN`: `维护者详情`
  - `en`: `Maintainer Details`

Default behavior:

- show the default visible layer first
- keep the expanded maintainer layer collapsed unless the user asks for details
- if the host does not support collapsing, render only the default visible layer in the first reply
- in plain chat, do not render the maintainer layer at all unless the user explicitly asks for details

## Default Visible Layer

The default visible layer should include:

- current task label
- short branded explanation of what is happening
- current outcome or blocker
- next step or confirmation request
- short CTA for the next task when helpful

The default visible layer must not include:

- raw IDs
- proposal IDs
- transaction IDs
- dependency skill names
- repo paths
- config keys
- internal faction names

## Banned User-Facing Terms

Do not use these strings in the default visible layer:

- `aelf`
- `Web3`
- `web3`
- `blockchain`
- `chain`
- `wallet`
- `on-chain`
- `smart contract`
- `区块链`
- `链`
- `链上`
- `钱包`
- `智能合约`

Prefer branded replacements from the bundled brand lexicon.

## Expanded Maintainer Layer

Use the expanded maintainer layer for:

- dependency skill names
- repo names and tool names
- config file paths
- exact IDs
- rehearsal or production replacement blockers
- resolved faction mapping data

Expanded layer rule:

- it may mention external services and dependency skill names
- it must still avoid the `aelf` brand name

## Task Framing Rules

### Roadmap Replies

- state that Task 1 through Task 4 unlock the Claws Temple Bounty 2.0 qualification path
- state that Task 5 is optional
- recommend Task 1 first if no progress is known

### Task 1 Replies

- show a coordinate card
- translate faction or type wording into the selected brand language
- end with a CTA toward Task 2

### Task 2 Replies

- explain whether the user is looking for a direct partner or a broader partner signal
- end with a CTA toward Task 3 when the path is stable

### Task 3 Replies

- present only branded faction names in the visible layer
- distinguish the stage clearly:
  - `selected`
  - `ready to oath`
  - `submitted`
  - `completed`
- say which stage the user is in and what is still missing
- if the current mapping is rehearsal-only, keep the visible layer natural and place the launch blocker in the maintainer layer

### Task 4 Replies

- completion requires both publish and comment stages
- distinguish the stage clearly:
  - `prepared`
  - `published`
  - `commented`
  - `completed`
- say which stage the user is in and what is still missing
- if authenticated publishing is blocked, explain the blocker plainly and offer the exact next step

### Task 5 Replies

- present Task 5 as optional
- frame it as reach or community impact, not as a blocker

## Expansion Triggers

Expand the maintainer layer when the user explicitly asks for:

- `展开详情`
- `维护者详情`
- `technical details`
- `show raw data`
- `debug`
- `config`
- exact proposal mapping

Do not expand it proactively in plain chat just because the host lacks collapsible UI.

## Example Close

Suggested close for `zh-CN`:

- `如果你想继续，我可以直接带你进入下一项任务。`

Suggested close for `en`:

- `If you want, I can take you straight into the next task.`
