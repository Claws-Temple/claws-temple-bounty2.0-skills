# Task 4 SHIT Skills Native Flow

Use this flow for Task 4 or any SHIT Skills native action request inside the bounty path.

## Dependency

- required live skill: `https://www.shitskills.net/skill.md`

## Goal

Route the user into the native SHIT Skills platform flow without wrapping Task 4 in a local completion state machine.

## Steps

1. Tell the user that Task 4 now continues in the native SHIT Skills flow.
2. Confirm whether the user already has a SHIT Skills account.
3. If the user does not have an account yet, route them into native registration or sign-in first.
4. Confirm that the user has a publishable `GitHub` repository URL.
5. If the user does not have a publishable `GitHub` repository URL, stop with a blocker summary instead of inventing a substitute source.
6. Gather the native publish fields:
   - `title`
   - `summary`
   - `githubUrl`
   - `tags`
   - `installType`
   - `installCommand` or `installUrl`
   - optional `content`
   - optional `coverUrl`
7. In maintainer-facing execution, run the Task 4 live-skill preflight before relying on the native action.
8. Load the live SHIT Skills integration skill only when both remote preflight and local authenticated native publishing are available.
9. Continue with the specific native action the user needs: publish, edit, delete, comment, vote, like, or parse GitHub `SKILL.md`.
10. If the native action succeeds, say which SHIT Skills action is now complete; do not claim that the local skill itself finalized Task 4 qualification.
11. If the host cannot load the remote skill, the network path is unavailable, or authenticated native publishing is unavailable, stop with a hard blocker and support CTA.

## Required Visible Output

- task label
- short native SHIT Skills framing
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

- explain the blocker plainly
- state whether the next step is native registration or native sign-in
- if the user is genuinely stuck and cannot continue in the current host, append support CTA

If the user has no publishable `GitHub` repository URL:

- explain that Task 4 cannot continue until a publishable `GitHub` repository is ready
- do not rewrite the source into another format
- append support CTA

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
