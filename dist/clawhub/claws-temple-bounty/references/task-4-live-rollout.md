# Task 4 Live Rollout Runbook

Use this file for maintainer-facing rollout and incident handling for the external Task 4 live skill.

## Goal

Keep Task 4 clearly available or unavailable as a native SHIT Skills flow, without falling back to a local prep-only success path.

For `OpenClaw`, the preferred runtime surface is a locally installed or ClawHub-installed native dependency.
Treat the remote `skill.md` probe as a non-OpenClaw compatibility path unless OpenClaw explicitly confirms that remote loading is supported in the current environment.
Current repository status: this package does not bundle an OpenClaw-native SHIT Skills wrapper for Task 4, so OpenClaw rollout depends on a separately installed compatible native package or confirmed host-native action support outside this repo.

## Rollout Modes

- `test rollout`
  - run `scripts/test-rollout-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe must pass
  - for OpenClaw, the usable native dependency must already be locally available, the session must be refreshed after install, and native action support must be confirmed
  - authenticated native publish must be available
  - if either prerequisite is missing, Task 4 is unavailable for that window
  - Tasks 1, 2, 3, and 5 may continue normally
- `production rollout`
  - run `scripts/release-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe must pass
  - for OpenClaw, the usable native dependency must already be locally available, the session must be refreshed after install, and native action support must be confirmed
  - authenticated native publish must be available
  - only then treat Task 4 as available

## Preflight Checklist

Before announcing a live Task 4 window:

1. run `python3 scripts/validate_skill_repo.py`
2. run `bash scripts/smoke-check.sh`
3. if the target host is not `OpenClaw`, run `bash scripts/task4-live-skill-probe.sh`
4. if the target host is `OpenClaw`, confirm that the usable native dependency is locally installed or available through ClawHub-managed install state
5. if the target host is `OpenClaw`, confirm whether the native runtime comes from an operator-installed compatible package or host-native action support outside this repo; do not imply this repository already bundles it
6. if the target host is `OpenClaw`, confirm a fresh `/new` session after install before reopening Task 4
7. if the target host is `OpenClaw`, set `OPENCLAW_TASK4_NATIVE_READY=1` and `OPENCLAW_TASK4_SESSION_REFRESHED=1` before using the rollout gate scripts
8. confirm the current host supports the chosen native action path
9. confirm the current host has authenticated native publishing available

## Availability Matrix

- remote probe fails
  - status: `unavailable`
  - action: close the current non-OpenClaw Task 4 window
  - user promise: explain the blocker and send the support CTA
- OpenClaw native dependency missing
  - status: `blocked`
  - action: stop the current OpenClaw Task 4 attempt
  - user promise: explain the exact missing native dependency or account prerequisite plainly, say when this repository version does not bundle that runtime, and keep the next step concrete: install the compatible package, run `/new`, or switch host
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
3. tell testers exactly which native dependency or account prerequisite is still missing
4. if the missing piece is the runtime package itself, say explicitly that this repository does not bundle it and that operators must install a compatible package first
