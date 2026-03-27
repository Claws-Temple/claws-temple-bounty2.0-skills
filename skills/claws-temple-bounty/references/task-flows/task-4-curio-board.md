# Task 4 SHIT Skills Native Flow

Use this flow for Task 4 or any SHIT Skills native action request inside the bounty path.

## Dependency

- required live skill: `https://www.shitskills.net/skill.md`

## Goal

Route the user into the native SHIT Skills platform flow without wrapping Task 4 in a local completion state machine.

## Steps

1. Tell the user that Task 4 now continues in the native SHIT Skills flow.
2. Ask which native action the user wants right now: `publish`, `comment`, `vote`, `like`, `edit`, `delete`, or `parse GitHub SKILL.md`.
3. If the user is following the bounty default path but has not named an action yet, recommend `publish` as the default Task 4 action.
4. Say clearly that `publish` is the default qualification action for the bounty path, while other native actions remain available as auxiliary actions unless campaign rules say otherwise.
5. Confirm whether the user already has a SHIT Skills account.
6. If the user does not have an account yet, route them into native registration or sign-in first.
7. Only when the user chooses `publish` or another repo-dependent action, confirm that the user has a publishable `GitHub` repository URL.
8. If the user chose a repo-dependent action but does not have a publishable `GitHub` repository URL, keep the reply in checklist mode instead of turning it into support CTA.
9. Gather the native publish fields only for `publish` or another action that needs them:
   - `title`
   - `summary`
   - `githubUrl`
   - `tags`
   - `installType`
   - `installCommand` or `installUrl`
   - optional `content`
   - optional `coverUrl`
10. For comment, vote, like, edit, or delete, ask only for the native action-specific target or session readiness; do not block these actions on `GitHub` repository input.
11. In maintainer-facing execution, run the Task 4 live-skill preflight before relying on the native action.
12. Load the live SHIT Skills integration skill only when both remote preflight and the required authenticated native action path are available.
13. Continue with the specific native action the user needs: publish, edit, delete, comment, vote, like, or parse GitHub `SKILL.md`.
14. If the native action succeeds, say which SHIT Skills action is now complete; do not claim that the local skill itself finalized Task 4 qualification unless the user explicitly completed the default qualification action.
15. If the host cannot load the remote skill, the network path is unavailable, or the required authenticated native action is unavailable, stop with a hard blocker and support CTA.

## Required Visible Output

- task label
- short native SHIT Skills framing
- native action choice or default recommendation
- qualification-vs-auxiliary-action clarification
- current native action, blocker, or exact next step
- support CTA when the user is genuinely stuck

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

- stop with a hard failure for the current Task 4 attempt
- do not draft a prep payload
- do not pretend the native action already happened
- append support CTA when the user cannot continue automatically in the current host

## Maintainer Notes

- the visible layer may say `SHIT Skills` directly for Task 4
- the visible layer should not expose the raw dependency name unless the user needs it to continue
- the visible layer should say that `GitHub` is the only publishable source for Task 4
- do not use a local Task 4 completion state machine
- keep the live skill URL in the maintainer layer when the user asks for details
