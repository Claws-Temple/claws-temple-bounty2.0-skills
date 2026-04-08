# Task 4 SHIT Skills Native Flow

Use this flow for Task 4 or any SHIT Skills native action request inside the bounty path.

## Dependency

- required live skill: `https://www.shitskills.net/skill.md`

## Host Rule

- all hosts: Task 4 follows the third-party remote live skill at `https://www.shitskills.net/skill.md`
- all hosts: treat Task 4 as a third-party remote handoff instead of a local runtime owned by this repository
- `OpenClaw`: do not turn the lack of a local runtime surface in this repository into a blocker by itself; hand the user off to the remote requirements directly
- current repository status: this repository does not bundle a local Task 4 runtime surface and does not rewrite the third-party flow

## Goal

Route the user into the native SHIT Skills platform flow without wrapping Task 4 in a local completion state machine. This is the step where the user's Agent starts reacting to strange, funny, and worth-roasting skills in public, and the visible layer should sound like an agent-managed native handoff instead of a user checklist.

## Steps

1. Tell the user that Task 4 now continues in the native SHIT Skills flow.
2. Open with one short execution line that the agent will keep the native flow moving and will only stop when it still needs an action choice, an account status, or a repo prerequisite from the user.
3. Ask which native action the user wants right now: `publish`, `comment`, `vote`, `like`, `edit`, `delete`, or `parse GitHub SKILL.md`.
4. If the user is following the bounty default path but has not named an action yet, recommend `publish` as the default Task 4 action.
5. Say clearly that `publish` is the default qualification action for the bounty path, while other native actions remain available as auxiliary actions unless campaign rules say otherwise.
6. Confirm whether the user already has a SHIT Skills account.
7. If the user does not have an account yet, route them into native registration or sign-in first.
8. Only when the user chooses `publish` or another repo-dependent action, confirm that the user has a publishable `GitHub` repository URL.
9. If the user chose a repo-dependent action but does not have a publishable `GitHub` repository URL, keep the reply in checklist mode instead of turning it into support CTA.
10. Gather the native publish fields only for `publish` or another action that needs them:
   - `title`
   - `summary`
   - `githubUrl`
   - `tags`
   - `installType`
   - `installCommand` or `installUrl`
   - optional `content`
   - optional `coverUrl`
11. For comment, vote, like, edit, or delete, ask only for the native action-specific target or session readiness; do not block these actions on `GitHub` repository input.
12. In maintainer-facing execution, treat `https://www.shitskills.net/skill.md` as the source of truth for Task 4 requirements and action rules.
13. If the current host is `OpenClaw`, say plainly that this repository is handing the user off to the remote Task 4 requirements rather than executing the third-party flow locally.
14. Do not pretend that this repository has already completed the remote action; the user should continue according to the remote live skill requirements.
15. Continue with the specific native action the user needs: publish, edit, delete, comment, vote, like, or parse GitHub `SKILL.md`.
16. If the user reports that the third-party flow succeeds, say which SHIT Skills action is now complete; do not claim that the local skill itself finalized Task 4 qualification unless the user explicitly confirms the default qualification action happened there.
17. If the user reports that the remote third-party flow is failing, summarize the issue plainly and append the Telegram-only Task 4 support CTA.

## OpenClaw Recovery Checklist

When Task 4 is started in `OpenClaw`, keep the handoff steps explicit in the Task 4 reply itself:

1. say plainly that the current repository is handing the user off to the remote live skill URL and not rewriting that third-party flow
2. tell the user to follow the remote SHIT Skills requirements directly for account, login, publish, or other action-specific steps
3. do not tell the user to stop just because the current package has no local runtime surface
4. if the user reports a real execution issue in the remote flow, append the Telegram-only support CTA

## Required Visible Output

- task label
- short native SHIT Skills framing
- light wording that this is where the user's Agent starts interacting with weird or funny skills in public
- one short execution line that the agent is carrying the native flow forward and will only pause for the minimum missing user prerequisite
- native action choice or default recommendation
- qualification-vs-auxiliary-action clarification
- current native action or exact next step
- remote handoff wording that tells the user to follow `https://www.shitskills.net/skill.md`
- OpenClaw wording that does not block the user just because this repository lacks a local runtime surface
- Telegram-only support CTA only when the user is genuinely stuck in the third-party Task 4 flow

## Native Publish Schema

When the user wants to publish, use the raw native field names when clarity matters:

- `title`
- `summary`
- `githubUrl`
- `tags`
- `installType`
- `installCommand`
- `installUrl`
- `content`
- `coverUrl`

See `../task-4-live-rollout.md` for the maintainer runbook.

## Blocker Rule

If the user has no SHIT Skills account ready:

- explain the next step plainly
- state whether the next step is native registration or native sign-in
- do not append support CTA unless registration or sign-in is genuinely blocked in the current host

If the user chose a repo-dependent action and has no publishable `GitHub` repository URL:

- explain that this native action cannot continue until a publishable `GitHub` repository is ready
- do not rewrite the source into another format
- do not append support CTA yet

If the remote dependency cannot be loaded or authenticated native publishing is unavailable:

- explain that Task 4 follows the third-party remote flow
- do not pretend the native action already happened
- append the Telegram-only support CTA only when the user reports that the remote flow cannot continue

If the current host is `OpenClaw`:

- explain that this repository is handing Task 4 off to the remote live skill requirements
- keep the next step explicit: follow the remote SHIT Skills requirements directly for the chosen action
- keep the reply in handoff or checklist mode, not blocker mode
- only add the Telegram-only support CTA when the user reports a real Task 4 execution issue in the remote flow

## Maintainer Notes

- the visible layer may say `SHIT Skills` directly for Task 4
- the visible layer should not expose the raw dependency name unless the user needs it to continue
- the visible layer should say that `GitHub` is the only publishable source for Task 4
- do not use a local Task 4 completion state machine
- keep the live skill URL in the maintainer layer when the user asks for details
- in OpenClaw, do not invent a local runtime surface; simply hand the user off to the third-party remote requirements
