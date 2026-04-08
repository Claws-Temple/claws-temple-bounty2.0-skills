# Task 4 Live Rollout Runbook

Use this file for maintainer-facing rollout and incident handling for the external Task 4 live skill handoff.

## Goal

Keep Task 4 clearly framed as a third-party remote handoff, without pretending the current repository owns that execution surface.

For `OpenClaw`, do not turn the lack of a local runtime surface into a repository blocker by itself.
Treat the remote `skill.md` as the third-party source of truth for Task 4 requirements across hosts.
Current repository status: this package does not bundle a local Task 4 runtime surface; it only hands users off to `https://www.shitskills.net/skill.md`.

## Rollout Modes

- `test rollout`
  - run `scripts/test-rollout-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe may be checked as a maintainer signal
  - for OpenClaw, keep Task 4 as an external handoff and do not fail this repository just because no local runtime surface exists
  - authenticated native publish belongs to the third-party flow, not to this repository package
  - Tasks 1, 2, 3, and 5 may continue normally
- `production rollout`
  - run `scripts/release-gate.sh`
  - local dependencies must pass
  - for non-OpenClaw hosts, remote Task 4 probe may be checked as a maintainer signal
  - for OpenClaw, keep Task 4 as an external handoff and do not fail this repository just because no local runtime surface exists
  - only then treat the repository handoff text as healthy; the third-party execution itself remains outside this package

## Preflight Checklist

Before announcing a live Task 4 window:

1. run `python3 scripts/validate_skill_repo.py`
2. run `bash scripts/smoke-check.sh`
3. optionally run `bash scripts/task4-live-skill-probe.sh` as a maintainer signal for the third-party remote flow
4. if the target host is `OpenClaw`, confirm that Task 4 is presented as a remote handoff instead of a local blocker
5. confirm the current host supports the chosen action path only when you are actively testing the third-party flow itself
6. if the user reports trouble in the third-party flow, direct them to Telegram support only, with the exact step and error

## Availability Matrix

- remote probe fails
  - status: `third_party_warning`
  - action: keep the repository handoff text available and warn maintainers that the third-party live flow may be unhealthy
  - user promise: tell the user to follow the remote requirements and use Telegram if they hit a real Task 4 execution issue
- OpenClaw local runtime missing
  - status: `expected_handoff`
  - action: do not stop the user because of this repository package; hand them off to the remote live skill requirements
  - user promise: explain that Task 4 continues according to the third-party remote skill and that this repository is not rewriting it locally
- remote probe passes but auth publish is unavailable
  - status: `third_party_warning`
  - action: keep the repository handoff text available
  - user promise: explain that the issue lives in the third-party flow and send the Telegram-only Task 4 support note only when the user asks for help with that failure
- native action succeeds
  - status: `native action complete`
  - action: report the completed SHIT Skills action without claiming local bounty-state completion

## Test Window Guidance

For a testing window, publish this rule to maintainers:

- Task 4 remains a third-party handoff even when the remote probe or authenticated publish path fails
- do not simulate a prep-only success path
- Tasks 1, 2, 3, and 5 may continue testing even while Task 4 is unavailable

## Incident Handling

If the remote live skill becomes unstable during testing:

1. rerun `scripts/task4-live-skill-probe.sh`
2. if it still fails, tell maintainers that the third-party Task 4 flow may be unstable
3. tell testers that Task 4 still follows the remote requirements and that Telegram support is the only escalation path for execution issues
4. rerun the probe before you announce that the third-party flow looks healthy again

If the current target host is `OpenClaw`:

1. do not stop the user just because this repository has no local runtime surface
2. tell testers that this repository only hands Task 4 off to the remote live skill
3. tell users to follow the remote SHIT Skills requirements directly
4. if the user reports a real execution issue, route them to Telegram support with the exact step and error
