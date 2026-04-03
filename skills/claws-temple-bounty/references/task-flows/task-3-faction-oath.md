# Task 3 Faction Oath Flow

Use this flow for Task 3 or any faction belonging request.

## Dependency

- required dependency skill: `tomorrowdao-agent-skills`
- required dependency skill: `portkey-ca-agent-skills`

## Required Config

Always read `../../config/faction-proposals.json` before rendering the faction list or executing an oath flow.

## Goal

Present four branded factions, map the selected faction to the current formal config, keep the whole oath flow inside a `CA-only + AI-only` execution path, verify the user can fund the vote with 2 AIBOUNTY, derive exact `Approve` and normalized `Vote` payloads through TomorrowDAO simulate, execute real writes through Portkey CA forward transport, and close the flow only after a mined-success vote tx plus Telegram follow-up. The visible layer should sound like agent-managed execution status, not like a manual user runbook.

## Preferred Helper

Use helper mode only when the current host can really satisfy all helper prerequisites.

Helper prerequisites:

- repo shell access to this package
- `bash`
- `python3`
- `bun`
- dependency skill roots for `tomorrowdao-agent-skills` and `portkey-ca-agent-skills`
- local CA context that the helper can read

When helper mode is available, prefer the bundled single-entry helper:

- `../../scripts/task3-oath-executor.sh`

Helper contract:

- required input: `--faction`
- optional input: `--login-email`, `--keystore-file`, `--password`
- machine statuses: `password_required`, `waiting_for_tokens`, `submitted`, `completed`, `blocked`
- process contract: `password_required`, `waiting_for_tokens`, `submitted`, and `completed` must still return structured JSON with exit code `0`; only hard blockers should return a non-zero exit
- helper responsibility: dependency preflight, keystore discovery, manager-sync check, balance check, allowance check, `Approve`, `Vote`, bounded retries, and reconciliation

Routing rule:

- call the helper first only when helper mode is available
- translate the helper status into the branded visible layer
- if helper mode is unavailable because the host cannot satisfy helper prerequisites, surface that as a host-capability blocker or fall back to the lower-level dependency-tool choreography below when that lower-level path is actually available
- the bundled helper itself does not auto-run lower-level choreography; it returns a structured blocker so the host can choose between `switch host`, `repair dependency or toolchain`, `wait for local CA readiness`, or direct dependency-tool choreography
- only fall back to the lower-level dependency-tool choreography below when the helper truly cannot run in the current host

## Steps

1. Read the faction config file.
2. Present the four branded factions with one-line positioning.
3. If the user has not chosen, help them pick one in brand language.
4. Map the branded choice to the config entry.
5. If helper mode is available, call `../../scripts/task3-oath-executor.sh` with the selected faction and any current CA profile hints, then use its returned status as the primary maintainer-facing execution result.
6. If the helper returns `password_required`, ask for the `CA keystore` password only once and then continue through the same helper.
7. If the helper returns `waiting_for_tokens`, keep the user in that normal waiting state instead of expanding the lower-level contract path.
8. If the helper returns `submitted`, keep the user in the public-record waiting state and continue confirmation polling instead of declaring failure.
9. If the helper returns `completed`, require its final vote `txId` and success payload for the branded close.
10. If helper mode is unavailable because the host cannot satisfy helper prerequisites, stop with a host-capability blocker or fall back to the lower-level contract below only when that path is actually available.
11. Only if the helper cannot run in the current host, fall back to the lower-level contract below.
12. When helper mode is unavailable, name the exact missing prerequisite in visible language, such as missing repo shell, missing `bash` / `python3` / `bun`, unresolved dependency roots, or missing local `CA` context.
13. Turn that helper blocker into one explicit recovery branch:
   - missing repo shell or missing `bash` / `python3` / `bun` -> `switch host` or repair the local toolchain
   - unresolved dependency roots or dependency version mismatch -> run dependency self-heal or install or upgrade guidance first
   - missing local `CA` context or keystore metadata -> recover local identity context first
   - direct dependency-tool choreography is host-managed and may continue only when the host already exposes that lower-level path; the bundled helper itself does not perform this fallback
14. Run a formal preflight:
   - confirm the selected faction entry exists
   - confirm the dependency invocation contract exists in the config file
   - confirm the TomorrowDAO dependency minimum version exists and is `0.2.2` or above
   - confirm the Portkey CA write dependency minimum version exists and is `2.3.0` or above
   - confirm the required proposal id is present
   - confirm the proposal end time is still in the future
13. Resolve the current signer or address before any token check or vote attempt.
14. Accept only a usable `CA` signer for Task 3 writes. If the current context is not `CA`-ready, stop with a branded blocker instead of switching to another signer route.
15. If the `CA` signer exists but the keystore password is missing, ask the user for the `CA keystore` password only once and then continue automatically.
16. If the current `CA` context unlocks a manager key, treat that key as part of the verified `CA` write path only; do not reinterpret it as permission for direct target-contract send.
17. If `tomorrowdao-agent-skills` is missing or below the configured minimum version, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh tomorrowdao-agent-skills`.
18. If `portkey-ca-agent-skills` is missing or below the configured CA write minimum version, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh portkey-ca-agent-skills`.
19. If that helper cannot run in the current host, use the portable source catalog in `../../config/dependency-sources.json` and return explicit install or upgrade guidance with the repo URL, any `clawhub_slug`, and the env override name.
20. If the current host still cannot auto-install or auto-upgrade either dependency, return explicit install or upgrade guidance before any support CTA.
21. Check that the installed TomorrowDAO and Portkey dependency versions both satisfy the config minimums.
22. Check that the configured generic token-balance tool, generic token-allowance tool, TomorrowDAO token-approve tool, and Portkey CA forward-call tool are available.
23. Query the configured vote token balance with the configured token symbol.
24. If the balance is below the configured vote amount, stop before vote submission and move the user to `waiting for tokens`.
25. In `waiting for tokens`, tell the user to return after Task 2 pairing succeeds or invite friends to pair so they can build toward the required 2 AIBOUNTY.
26. Treat `waiting for tokens` as a normal unmet-threshold state, not as a support CTA state, unless the token-balance check itself is externally blocked.
27. Query the current allowance for the vote token against the current vote contract before sending the vote.
28. If the allowance is below the configured vote amount, first call `tomorrowdao_token_approve --mode simulate` and use its exact `contractAddress`, `methodName`, and `args` as the approval payload source.
29. Send the actual `Approve` through `portkey_forward_call`, and once one Portkey CA forward transport has already succeeded for `Approve`, keep that same verified CA forward transport as the preferred path for the final `Vote`.
30. Retry `Approve` at most 3 times using bounded backoff `3s -> 8s -> 15s`. After each attempt or timeout, re-check allowance before deciding whether another approval attempt is still necessary.
31. If allowance is already sufficient after an `Approve` timeout or uncertain receipt, continue into `Vote` instead of repeating authorization blindly.
32. Do not blindly mix a successful Portkey CA forward approval transport with a different direct vote transport. If another path is attempted and returns `NODEVALIDATIONFAILED` with `Insufficient allowance` while allowance is already sufficient, treat that as a transport mismatch and switch back to the same verified CA forward transport used by `Approve`.
33. Keep the visible layer natural during the allowance step. Tell the user that one more authorization step is being completed before the oath can be sent, but keep raw contract path and approval tx details in the maintainer layer unless the user asks.
34. Invoke `tomorrowdao_dao_vote --mode simulate` after the mapping, dependency checks, token-balance precheck, and any required approval step all pass; use the exact dependency-tool vote payload contract from the config file and do not reinterpret `proposalId` there as a raw contract ABI field name.
35. Use the normalized `tomorrowdao_dao_vote --mode simulate` result as the only source for the final `Vote` contract address and final `votingItemId` payload, then send that exact payload through `portkey_forward_call`.
36. For `Vote`, prefer mined receipt first, then recent address-transaction recovery, and only then `proposal my-info` as the final auxiliary confirmation source.
37. Use the configured `tx_recovery` source from `../../config/faction-proposals.json` to recover a missing `Vote txId` from recent address transactions when the send path is uncertain.
38. If TomorrowDAO direct send returns `SIGNER_CA_DIRECT_SEND_FORBIDDEN`, treat that as expected CA-routing evidence and continue through the explicit Portkey CA forward transport instead of stopping.
39. If `Vote` returns a timeout, validation failure, `Voter already voted`, or another uncertain send result, re-check mined receipt, recent address transactions, and then `proposal my-info` when available before retrying.
40. Retry `Vote` at most 3 times using bounded backoff `3s -> 8s -> 15s`.
41. If the receipt or logs already show that the vote state changed but the final confirmation is not settled yet, move the user to `submitted` and continue polling for final confirmation.
42. If recent address-transaction recovery shows more than one plausible `Vote` candidate, or if `proposal my-info` shows the vote state change but the final `txId` is still not correlated, keep the user in `submitted` and continue polling instead of declaring failure.
43. Once the final vote is sent but before a mined-success receipt is available, move the user to `submitted`.
44. In `submitted`, tell the user that the oath has been sent and is waiting for final confirmation in the public record. Do not move to `completed` yet, and do not append support CTA unless receipt monitoring itself is externally blocked.
45. Treat the oath as successful only when the final vote returns a mined-success `txId` from `TxReceipt`.
46. In the success close, show the final vote `txId`, tell the user to join the configured Telegram group, add one short capability boundary line that says the user should manually join the group and send the prepared message if the current agent cannot directly operate Telegram, give the separate bonus or discussion reminder from the config, and then render the fixed Telegram post template with `{faction_name}` and `{txId}` filled in.
47. If the config is marked as production, present the result as the formal faction oath record and do not mention testing, rehearsal, or a later record replacement.

## Required Visible Output

- task label
- the four branded faction names
- one-line faction thesis per faction
- one short execution line that checks, authorization, submission, and confirmation are being advanced automatically by the agent
- current stage or selection prompt
- host-capability blocker wording when helper mode is unavailable in the current host
- explicit missing helper prerequisite plus the next recovery action when helper mode is unavailable
- token-precheck outcome when relevant
- allowance or authorization outcome when relevant
- password request wording when the `CA` keystore password is missing
- automatic retry wording when authorization or vote confirmation is still being reconciled
- submitted-state waiting explanation when relevant
- blocker summary plus support CTA when the oath cannot continue automatically
- `txId` plus Telegram follow-up prompt, capability boundary line when needed, and template after success
- next step after the oath

## Faction Display Mapping

Load the branded faction names from `../../config/faction-proposals.json`.
Use the matching brand lexicon only for task labels, helper wording, and close-out phrasing.

## Maintainer Notes

- only the config file may carry exact proposal IDs and end times
- use the exact dependency invocation contract from `config/faction-proposals.json` instead of repeating invocation parameters in this file
- use the config file for the TomorrowDAO dependency minimum version, the Portkey CA write minimum version, token symbol, vote amount, generic token-balance tool, generic token-allowance tool, TomorrowDAO token-approve tool, Telegram success template, and separate Telegram bonus note
- when helper mode is available, prefer the bundled helper `../../scripts/task3-oath-executor.sh` as the first execution surface for Task 3; it collapses preflight, `Approve`, `Vote`, and reconciliation into one maintainer-facing call
- if the helper returns `password_required`, `waiting_for_tokens`, `submitted`, `completed`, or `blocked`, treat that machine status as the primary execution truth and translate it into the branded visible layer instead of re-deriving state from memory
- if the helper cannot run because the host lacks repo shell, local toolchain, dependency roots, or local CA context, treat that as helper-mode unavailability rather than pretending helper mode already advanced the write path
- `task3_execution_policy = ca_only_ai_completion`
- `task3_password_policy = ask_once_for_ca_keystore_password`
- `task3_retry_policy = bounded_ca_retries_with_state_reconciliation`
- `CA` keystore unlock may expose the manager key, but that manager key alone still must not authorize direct target-contract send
- `proposalId` in the config vote payload is the dependency-tool input alias for the configured vote tool, not a promise about the raw contract ABI field name
- if an implementation ever has to bypass the dependency tool, it must reproduce the dependency normalization from `proposalId` to the underlying `votingItemId` before any raw contract packing or forwarding
- once `CA` is selected, env or private-key fallback must not continue the write path if they would become direct target-contract send
- if TomorrowDAO direct send for a resolved `CA` signer returns `SIGNER_CA_DIRECT_SEND_FORBIDDEN`, continue with the explicit Portkey CA forward transport instead of stopping
- stop with an unsupported `CA` transport blocker only if the explicit Portkey CA forward transport is unavailable or cannot continue automatically
- do not present `Portkey App`, `EOA`, `ManagerForwardCall`, or manual route choices in the visible layer
- when the current signer path is `CA`, the fastest unblock is inside this skill: read allowance, derive `Approve` and `Vote` payloads through TomorrowDAO simulate, then send both writes through the same verified `CA` write transport, implemented here as the same verified Portkey CA forward transport
- if a different vote path returns `NODEVALIDATIONFAILED` with `Insufficient allowance` after allowance is already sufficient, treat that as a transport mismatch instead of a real allowance failure
- use `proposal my-info` as the last auxiliary reconciliation helper, not as the only source of truth for vote-state confirmation
- prefer the configured `tx_recovery` provider to recover a missing `Vote txId` before falling back to `proposal my-info`
- the spender for the allowance check and approval must be the current vote contract address from the dependency runtime, not a new hardcoded visible-layer constant
- if `environment = production` and `is_test_only = false`, the visible layer should treat the selected mapping as the final formal record for Task 3
- do not repeat raw IDs in any other reference file
