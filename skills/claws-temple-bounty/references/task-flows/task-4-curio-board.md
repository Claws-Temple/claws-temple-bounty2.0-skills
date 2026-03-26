# Task 4 Curio Board Flow

Use this flow for Task 4 or any publish-and-comment skill showcase request.

## Dependency

- required live skill: `https://www.shitskills.net/skill.md`

## Goal

Publish a branded curio from a supported source and then leave a follow-up comment.

## Steps

1. Confirm the user has a curio source to publish.
2. Accept any supported curio source:
   - `ClawHub` public page URL
   - `GitHub` repository URL
   - another public skill page URL
3. If title, summary, tags, or curio source are missing, gather them first.
4. In maintainer-facing execution, run the Task 4 live-skill preflight before relying on live publish.
5. Load the live SHIT Skills integration skill only when both remote preflight and local authenticated publishing are available.
6. Complete the publish step.
7. Complete the comment step on the same entry.
8. Return success only when both steps are complete.
9. If the host cannot load the remote skill or the network path is unavailable, switch to `publish-prep mode` instead of failing silently.

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
- `curio_source`
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
- if the user is genuinely stuck and cannot clear the prerequisite in the current host, append support CTA

If the remote dependency cannot be loaded:

- switch to `publish-prep mode`
- return the publish payload draft
- return the follow-up comment draft
- keep the output shape aligned with the fixed prep payload contract above
- tell the user that the remaining step is to run the live publish path in a supported host
- append support CTA when the user cannot continue automatically in the current host

## Maintainer Notes

- the visible layer should say `奇物志` or `Curio Board`
- the visible layer should not expose the raw dependency name
- the visible layer should not force GitHub-only wording when the user provides a `ClawHub` or other public skill source
- keep the live skill URL in the maintainer layer when the user asks for details
- for test rollouts, prefer graceful downgrade over hard failure when the remote skill probe is flaky
