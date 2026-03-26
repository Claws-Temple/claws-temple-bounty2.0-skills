# Task 4 Example (English)

> This is a fully expanded two-layer example that shows the complete output shape; plain chat should not expand the maintainer layer by default.

## User Summary

You are at `Task 4: Curio Board`.

This task has two required steps:

1. Publish your curio.
2. Leave a follow-up comment on the same entry so the discussion actually starts.

Current status:

- `publish`: `prepared`
- `comment`: `waiting`

If you already have the GitHub URL, title, summary, and tags, I can move straight into the publish path.
If not, I can prepare the full publish copy first.
If we are only preparing copy, the current stage is `prepared`, not completed yet; Task 4 is only complete after both publish and comment are done.

### Stage Samples

- `prepared`: the copy, tags, and link are ready, but nothing has been published yet.
- `published`: the entry is live, but the follow-up comment is still missing.
- `commented`: the comment is done and the flow is waiting for final completion confirmation.
- `completed`: both publish and comment are done.

### Blocker Example

If the current host cannot load the live skill, or authenticated publishing is unavailable, the reply should say:

`The task is still only at the prepared stage. I can draft the publish copy and comment now, but the actual live publish step still needs a supported host.`

## Maintainer Details

- route: `task-4-curio-board`
- live_dependency: `https://www.shitskills.net/skill.md`
- completion_rule: `publish + comment`
