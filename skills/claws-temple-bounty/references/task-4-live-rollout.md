# Task 4 Live Rollout Runbook

Use this file for maintainer-facing rollout and incident handling for the external Task 4 live skill.

## Goal

Keep Task 4 clearly available or unavailable as a native SHIT Skills flow, without falling back to a local prep-only success path.

For `OpenClaw`, do not assume the remote `skill.md` probe is usable in this repository package.
Treat the remote `skill.md` probe as a non-OpenClaw compatibility path unless a future OpenClaw-local runtime surface is explicitly added and documented.
Current repository status: this package does not bundle an OpenClaw-local Task 4 runtime surface; it only references the remote live skill at `https://www.shitskills.net/skill.md`.

## Rollout Modes

- `test rollout`
  - run `scripts/test-rollout-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe must pass
  - for OpenClaw, keep Task 4 unavailable in this repository until an explicit local runtime surface exists
  - authenticated native publish must be available
  - if either prerequisite is missing, Task 4 is unavailable for that window
  - Tasks 1, 2, 3, and 5 may continue normally
- `production rollout`
  - run `scripts/release-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe must pass
  - for OpenClaw, keep Task 4 unavailable in this repository until an explicit local runtime surface exists
  - authenticated native publish must be available
  - only then treat Task 4 as available

## Preflight Checklist

Before announcing a live Task 4 window:

1. run `python3 scripts/validate_skill_repo.py`
2. run `bash skills/claws-temple-bounty/scripts/smoke-check.sh`
3. if the target host is not `OpenClaw`, run `bash skills/claws-temple-bounty/scripts/task4-live-skill-probe.sh`
4. if the target host is `OpenClaw`, treat Task 4 as closed in this repository package and direct users to a non-OpenClaw host for the live skill path
5. confirm the current host supports the chosen native action path
6. confirm the current host has authenticated native publishing available

## Availability Matrix

- remote probe fails
  - status: `unavailable`
  - action: close the current non-OpenClaw Task 4 window
  - user promise: explain the blocker and send the support CTA
- OpenClaw repository runtime missing
  - status: `blocked`
  - action: stop the current OpenClaw Task 4 attempt
  - user promise: explain that this repository only exposes the remote live skill for Task 4, does not ship an OpenClaw-local runtime, and therefore the next concrete step is to switch host or wait for a future runtime release
- remote probe passes but auth publish is unavailable
  - status: `blocked`
  - action: stop the current Task 4 attempt
  - user promise: explain the missing prerequisite plainly and send the support CTA
- native action succeeds
  - status: `native action complete`
  - action: report the completed SHIT Skills action without claiming local bounty-state completion

## Test Window Guidance

For a testing window, publish this rule to maintainers:

- Task 4 must be treated as unavailable when the remote probe or authenticated publish path fails
- do not simulate a prep-only success path
- Tasks 1, 2, 3, and 5 may continue testing even while Task 4 is unavailable

## Incident Handling

If the remote live skill becomes unstable during testing:

1. rerun `scripts/task4-live-skill-probe.sh`
2. if it still fails, keep the current Task 4 window closed
3. tell testers that Task 4 is unavailable until the native flow is healthy again
4. rerun the probe before reopening Task 4

If the current target host is `OpenClaw` and the native dependency is still missing:

1. keep the current Task 4 window closed in OpenClaw
2. do not pretend that the remote URL can replace the native dependency there
3. tell testers that this repository only has the remote live skill for Task 4 and no OpenClaw-local runtime
4. route testing and production use back to a non-OpenClaw host until a future runtime is published
