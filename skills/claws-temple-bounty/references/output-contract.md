# Claws Temple Bounty Output Contract

Version: `0.2.4`

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

Task-specific exception:

- Task 2 replies may include the fully resolved current user's own `user ID` because the user needs a direct confirmation that queue readiness is already in place.
- Task 3 completed replies may include the mined-success `txId` because the user must repost it into Telegram as their confirmation number.

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

## CTA Classification

Resolve `cta_type` before rendering blocker or close-out replies:

- `support`
  - a real blocker, externally stalled state, or host/runtime limitation means the agent cannot continue automatically in the current turn
  - examples: dependency self-heal already failed, missing authenticated publish capability, identity-entry setup failure, missing config, remote live-skill outage, host capability gap, or rehearsal-only limits that block real submission
- `none`
  - the agent can still continue by collecting missing user input
  - the issue is only a light routing correction or an unfinished user choice
  - the user is waiting, but not genuinely stuck yet

Hard rules:

- append support CTA only when `cta_type = support`
- do not mix support CTA with ordinary success or next-task CTA in the same close
- support replies must show `Telegram first, then X`

## Dependency Self-Heal Rules

For Task 1 through Task 3, treat `missing dependency` and `dependency version below minimum` as self-heal cases before any blocker reply.

Required order:

1. try automatic install, refresh, or upgrade first
2. if the host cannot do that automatically, give explicit install or upgrade guidance
3. only append support CTA after self-heal or guidance still cannot unblock the task

Known local sources for self-heal:

- `agent-spectrum` -> `/Users/huangzongzhe/workspace/vibeCoding/agent-spectrum-skill/skills/agent-spectrum`
- `resonance-contract` -> `/Users/huangzongzhe/workspace/vibeCoding/agent-resonance-skill/skills/resonance-contract`
- `tomorrowdao-agent-skills` -> `/Users/huangzongzhe/workspace/TomorrowDAOProject/tomorrowDAO-skill`

## Support CTA Strings

Use these strings when `cta_type = support`.

### `zh-CN`

- `→ 如果这里卡住了，欢迎到 [Telegram 群](https://t.me/+tChFhfxgU6AzYjJl) 贴出你当前的步骤、报错和关键信息，我们可以一起帮你排查。`
- `→ 也可以去 [X / Twitter](https://x.com/aelfblockchain) 发帖求助，带上你当前的状态和卡点，方便社区更快看到并协助你。`

### `en`

- `→ If you're stuck here, join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) and share your current step, error, and key context so the community can help troubleshoot.`
- `→ You can also post on [X](https://x.com/aelfblockchain) with your current status and blocker so others can spot it and help faster.`

## Task Framing Rules

### Roadmap Replies

- state that Task 1 through Task 3 can be completed in this path
- state that Task 4 must be completed in the SHIT Skills native flow for the qualification path
- state that the default recommended Task 4 action is `publish`
- state that the current repository still routes Task 3 through a testing or rehearsal record path and that production will switch later
- state that Task 5 is optional
- recommend Task 1 first if no progress is known

### Task 1 Replies

- show a coordinate card
- translate faction or type wording into the selected brand language
- if the dependency skill is missing or below the required runnable state, try dependency self-heal first
- if the host cannot auto-install or auto-upgrade, give explicit install guidance before any support CTA
- if dependency self-heal or the scoring run still cannot continue, explain the blocker and append support CTA
- end with a CTA toward Task 2

### Task 2 Replies

- explain whether the user is looking for `targeted match` or `open partner search`
- confirm whether the user's `identity entry` is already open before moving into pairing
- confirm whether the user is already signed in; if not, route returning users into recovery sign-in before pairing
- if the user is first-time, explain that the smoother identity-entry path starts with sign-up or first-time setup before the pairing flow and ends with a usable `user ID`
- if the user is returning but not currently signed in, explain that the smoother identity-entry path starts with recovery sign-in before the pairing flow and ends with a usable `user ID`
- if identity entry and sign-in are ready, auto-resolve the current user's own `user ID` instead of asking the user to type it manually
- once the current user's `user ID` resolves, show the full value in the visible layer as the Task 2 queue-readiness confirmation
- if the user chooses `targeted match`, ask for the other user's `user ID`
- if the user does not already have a concrete partner, explain that `open partner search` is the automatic queue-matching path and does not need a preselected target
- if `resonance-contract` is missing or below `3.0.1`, try dependency self-heal first
- if the host cannot auto-install or auto-upgrade `resonance-contract`, give explicit install or upgrade guidance before any support CTA
- if dependency queue preflight can proceed, continue into the formal queue path and do not suggest skipping Task 2 or replacing queue with social posting
- treat the Task 2 path as stable enough for Task 3 once the queue join is active or the direct pair submission has been sent
- if the user provides `email`, `Address`, nickname, `tDVV` address, or another non-`user ID` input for targeted match, correct the input naturally and offer `provide the other user's user ID` or `switch to open partner search`
- keep `CA only`, `counterparty_ca_hash`, and `queue` inside maintainer-facing details; the default visible layer should say `user ID`
- do not tell the user to look in legacy community-brand wording, extra platform names outside Telegram and X, or any address-based source; if the user is stuck, point them to the clickable Telegram / X links instead
- if registration, recovery sign-in, user-ID auto-resolution, dependency self-heal, identity-entry setup, or the pairing path is externally blocked and the user cannot continue automatically, translate the blocker into `身份入口 / 用户ID 未准备好` style wording and append support CTA
- end with a CTA toward Task 3 when the path is stable

### Task 3 Replies

- present only branded faction names in the visible layer
- distinguish the stage clearly:
  - `selected`
  - `waiting for tokens`
  - `ready to oath`
  - `submitted`
  - `completed`
- say which stage the user is in and what is still missing
- before vote submission, verify that `tomorrowdao-agent-skills >= 0.2.0` and the configured generic token-balance tool are available
- if `tomorrowdao-agent-skills` is missing or below `0.2.0`, try dependency self-heal first
- if the host cannot auto-install or auto-upgrade `tomorrowdao-agent-skills`, give explicit install or upgrade guidance before any support CTA
- before vote submission, verify that the user's `AIBOUNTY` balance is at least the configured vote amount
- if the user's balance is below the configured vote amount, move to `waiting for tokens` and suggest either returning after Task 2 pairing succeeds or inviting friends to pair
- treat `waiting for tokens` as a normal unmet-threshold state with `cta_type = none`; do not append support CTA unless the balance check itself is externally blocked
- when the current signer path is `CA` or another delegated-spend route, verify that the configured generic token-allowance tool is available and check the current `AIBOUNTY` allowance against the current vote contract
- when the allowance is below the configured vote amount, explain in the visible layer that one more authorization step is needed, send one `Approve` step first, and only then retry the actual vote
- keep approval tx details in maintainer-facing details unless the user explicitly asks; the `completed` close should still use the final vote `txId`
- use `submitted` after the final vote has been sent but before mined-success receipt confirmation is available
- in `submitted`, explain that the oath is waiting for final public-record confirmation and keep `cta_type = none` unless monitoring itself is externally blocked
- only move to `completed` after the vote returns a mined-success `txId`
- in `completed`, include the `txId`, the Telegram group CTA, the fixed Telegram post template, and the two-week extra 20 Token reminder
- if the current mapping is rehearsal-only, say clearly in the visible layer that this is a testing or rehearsal record and that production will later switch to the formal record
- if the mapping exists but the current environment cannot continue the oath flow, the allowance step cannot be completed, or the dependency contract is missing, explain the blocker and append support CTA

### Task 4 Replies

- state clearly that the user is entering the native SHIT Skills flow
- ask which native action the user wants right now
- if the user is following the bounty default path and has not chosen an action yet, recommend `publish`
- say clearly that `publish` is the default qualification action in the bounty path, while other native actions are auxiliary unless campaign rules say otherwise
- ask whether the user already has a SHIT Skills account; if not, route them into registration or sign-in first
- require a publishable `GitHub repo URL` only when the chosen native action actually needs it
- gather the native publish fields only when the chosen native action actually needs them:
  - `title`
  - `summary`
  - `githubUrl`
  - `tags`
  - `installType`
  - `installCommand` or `installUrl`
  - optional `content`
  - optional `coverUrl`
- allow native platform actions such as publish, edit, delete, comment, vote, like, and parse GitHub `SKILL.md`
- do not use a local `prepared / published / commented / completed` stage model for Task 4
- do not claim that the local bounty skill itself has completed Task 4; only say which SHIT Skills native action is ready, blocked, or confirmed
- if the user chose a repo-dependent action but does not have a publishable `GitHub repo URL`, explain that the action is still missing a prerequisite and keep `cta_type = none`
- if registration or sign-in is the next normal step, keep `cta_type = none`
- if registration, sign-in, authenticated publishing, or live remote loading is truly blocked, explain the blocker plainly and append support CTA

### Task 5 Replies

- present Task 5 as optional
- frame it as reach or community impact, not as a blocker
- if the user explicitly wants to send the signal now but the platform or current context blocks that action, append support CTA

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
