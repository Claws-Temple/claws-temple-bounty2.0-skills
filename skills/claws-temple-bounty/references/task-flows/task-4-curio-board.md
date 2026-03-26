# Task 4 Curio Board Flow

Use this flow for Task 4 or any publish-and-comment skill showcase request.

## Dependency

- required live skill: `https://www.shitskills.net/skill.md`

## Goal

Publish a branded curio and then leave a follow-up comment.

## Steps

1. Confirm the user has a skill or repository to publish.
2. If title, summary, tags, or GitHub URL are missing, gather them first.
3. In maintainer-facing execution, run the Task 4 live-skill preflight before relying on live publish.
4. Load the live SHIT Skills integration skill only when both remote preflight and local authenticated publishing are available.
5. Complete the publish step.
6. Complete the comment step on the same entry.
7. Return success only when both steps are complete.
8. If the host cannot load the remote skill or the network path is unavailable, switch to `publish-prep mode` instead of failing silently.

## Required Visible Output

- task label
- publish status
- comment status
- short Curio Board framing
- next-step CTA toward optional Task 5

## Publish-Prep Contract

When `publish-prep mode` is used, return a fixed prep payload shape:

- `title`
- `summary`
- `tags`
- `github_url`
- `publish_draft`
- `comment_draft`
- `remaining_live_step`

## Rollout Modes

- `test rollout`: the live-skill probe may warn and the task may stay in `publish-prep mode`; this is acceptable for a testing window
- `production rollout`: the live-skill probe must pass before Task 4 is treated as fully live

See `../task-4-live-rollout.md` for the maintainer runbook.

## Blocker Rule

If authenticated publishing is unavailable:

- explain the blocker plainly
- state the exact missing prerequisite
- do not pretend the publish step already happened
- keep the task in `publish-prep mode` for the current rollout window

If the remote dependency cannot be loaded:

- switch to `publish-prep mode`
- return the publish payload draft
- return the follow-up comment draft
- keep the output shape aligned with the fixed prep payload contract above
- tell the user that the remaining step is to run the live publish path in a supported host

## Maintainer Notes

- the visible layer should say `奇物志` or `Curio Board`
- the visible layer should not expose the raw dependency name
- keep the live skill URL in the maintainer layer when the user asks for details
- for test rollouts, prefer graceful downgrade over hard failure when the remote skill probe is flaky
