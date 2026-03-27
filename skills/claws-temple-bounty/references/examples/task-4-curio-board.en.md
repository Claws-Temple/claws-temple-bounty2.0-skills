# Task 4 Example (English)

> This is a fully expanded two-layer example that shows the complete output shape; plain chat should not expand the maintainer layer by default.

## User Summary

You are at `Task 4: SHIT Skills Native Flow`.

This task no longer uses a local completion stage model. I take you directly into the native `SHIT Skills` flow instead.

I first confirm two things:

1. whether you already have a `SHIT Skills` account
2. whether you already have a publishable `GitHub repo URL`

If you do not have an account yet, I route you into native registration or sign-in first.  
If you do not have a publishable `GitHub repo URL`, Task 4 cannot continue yet.

Before native publish, I also collect these fields:

- `title`
- `summary`
- `githubUrl`
- `tags`
- `installType`
- `installCommand` or `installUrl`
- optional `content`
- optional `coverUrl`

I do not wrap Task 4 in old local stage labels anymore.  
I only tell you which `SHIT Skills` native action is ready, blocked, or complete.

### Native Action Samples

- `register account`: no account yet, so email OTP + password registration comes first.
- `sign in`: an account exists, but the current host still needs a working sign-in session.
- `publish`: the account and `GitHub repo URL` are ready, so we can continue with the native publish fields.
- `comment / vote / like / edit / delete`: continue the corresponding native platform action.
- `parse GitHub SKILL.md`: use the native parser flow to fill in content.

### Blocker Example

If the user has no publishable `GitHub repo URL`, or the current host cannot complete native `SHIT Skills` sign-in or publish, the reply should say:

`Task 4 cannot continue yet because the native flow needs a publishable GitHub repo and a working SHIT Skills sign-in session. Once those prerequisites are ready, I can continue the native publish action.`

- `→ If you're stuck here, join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) and share your current step, error, and key context so the community can help troubleshoot.`
- `→ You can also post on [X](https://x.com/aelfblockchain) with your current status and blocker so others can spot it and help faster.`

## Maintainer Details

- route: `task-4-curio-board`
- live_dependency: `https://www.shitskills.net/skill.md`
- native_publish_required_fields: `title`, `summary`, `githubUrl`, `tags`, `installType`, `installCommand|installUrl`
