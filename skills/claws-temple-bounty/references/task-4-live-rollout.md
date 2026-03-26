# Task 4 Live Rollout Runbook

Use this file for maintainer-facing rollout and incident handling for the external Task 4 live skill.

## Goal

Keep Task 4 usable even when the external live skill is unstable, while preserving a stricter production gate for full live publish.

## Rollout Modes

- `test rollout`
  - run `scripts/test-rollout-gate.sh`
  - local dependencies must pass
  - remote Task 4 probe may warn
  - if the probe warns or authenticated publish is unavailable, keep Task 4 in `publish-prep mode`
  - Tasks 1, 2, 3, and 5 may continue normally
- `production rollout`
  - run `scripts/release-gate.sh`
  - local dependencies must pass
  - remote Task 4 probe must pass
  - authenticated publish must be available
  - only then treat Task 4 as fully live

## Preflight Checklist

Before announcing a live Task 4 window:

1. run `python3 scripts/validate_skill_repo.py`
2. run `bash skills/claws-temple-bounty/scripts/smoke-check.sh`
3. run `bash skills/claws-temple-bounty/scripts/task4-live-skill-probe.sh`
4. confirm the current host supports live remote skill loading
5. confirm the current host has authenticated publishing available

## Fallback Matrix

- remote probe fails
  - status: `prepared`
  - action: switch to `publish-prep mode`
  - user promise: publish copy and comment draft are still delivered
- remote probe passes but auth publish is unavailable
  - status: `prepared`
  - action: keep the live step pending
  - user promise: explain the missing prerequisite plainly
- publish succeeds but comment is still pending
  - status: `published`
  - action: resume only the comment step
- comment succeeds after publish
  - status: `completed`
  - action: offer Task 5 CTA

## Test Window Guidance

For a testing window, publish this rule to maintainers:

- Task 4 may be evaluated in `publish-prep mode`
- do not mark Task 4 as complete unless both live publish and comment actually succeed
- if the probe is flaky, continue collecting test feedback on the prep flow instead of blocking all testing

## Incident Handling

If the remote live skill becomes unstable during testing:

1. rerun `scripts/task4-live-skill-probe.sh`
2. if it still fails, switch the current window to prep-only mode
3. tell testers that Task 4 remains testable, but only at the `prepared` stage
4. rerun the probe before reopening full live publish
