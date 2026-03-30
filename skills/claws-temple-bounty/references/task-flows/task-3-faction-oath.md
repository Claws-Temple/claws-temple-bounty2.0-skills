# Task 3 Faction Oath Flow

Use this flow for Task 3 or any faction belonging request.

## Dependency

- required dependency skill: `tomorrowdao-agent-skills`

## Required Config

Always read `../../config/faction-proposals.json` before rendering the faction list or executing an oath flow.

## Goal

Present four branded factions, map the selected faction to the current rehearsal config, keep the whole oath flow inside a `CA-only + AI-only` execution path, verify the user can fund the vote with 2 AIBOUNTY, complete any required approval step automatically, and close the flow only after a mined-success vote tx plus Telegram follow-up.

## Steps

1. Read the faction config file.
2. Present the four branded factions with one-line positioning.
3. If the user has not chosen, help them pick one in brand language.
4. Map the branded choice to the config entry.
5. Run a rehearsal-safe preflight:
   - confirm the selected faction entry exists
   - confirm the dependency invocation contract exists in the config file
   - confirm the dependency minimum version exists and is `0.2.0` or above
   - confirm the required proposal id is present
   - confirm the proposal end time is still in the future
6. Resolve the current signer or address before any token check or vote attempt.
7. Accept only a usable `CA` signer for Task 3 writes. If the current context is not `CA`-ready, stop with a branded blocker instead of switching to another signer route.
8. If the `CA` signer exists but the keystore password is missing, ask the user for the `CA keystore` password only once and then continue automatically.
9. If `tomorrowdao-agent-skills` is missing or below the configured minimum version, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh tomorrowdao-agent-skills`.
10. If that helper cannot run in the current host, use the portable source catalog in `../../config/dependency-sources.json` and return explicit install or upgrade guidance with the repo URL and env override name.
11. If the current host still cannot auto-install or auto-upgrade the dependency, return explicit install or upgrade guidance before any support CTA.
12. Check that the installed dependency version is at least the configured minimum version.
13. Check that the configured generic token-balance tool and generic token-allowance tool are available.
14. Query the configured vote token balance with the configured token symbol.
15. If the balance is below the configured vote amount, stop before vote submission and move the user to `waiting for tokens`.
16. In `waiting for tokens`, tell the user to return after Task 2 pairing succeeds or invite friends to pair so they can build toward the required 2 AIBOUNTY.
17. Treat `waiting for tokens` as a normal unmet-threshold state, not as a support CTA state, unless the token-balance check itself is externally blocked.
18. Query the current allowance for the vote token against the current vote contract before sending the vote.
19. If the allowance is below the configured vote amount, send `Approve` first through the available `CA` write path.
20. Retry `Approve` at most 3 times using bounded backoff `3s -> 8s -> 15s`. After each attempt or timeout, re-check allowance before deciding whether another approval attempt is still necessary.
21. If allowance is already sufficient after an `Approve` timeout or uncertain receipt, continue into `Vote` instead of repeating authorization blindly.
22. Keep the visible layer natural during the allowance step. Tell the user that one more authorization step is being completed before the oath can be sent, but keep raw contract path and approval tx details in the maintainer layer unless the user asks.
23. Invoke the actual vote only after the mapping, dependency checks, token-balance precheck, and any required approval step all pass; use the exact vote payload contract from the config file.
24. If `Vote` returns a timeout, validation failure, or another uncertain send result, re-check proposal availability, allowance, and `proposal my-info` before retrying.
25. Retry `Vote` at most 3 times using bounded backoff `3s -> 8s -> 15s`.
26. If `proposal my-info` already shows that the vote state changed but the final receipt is not confirmed yet, move the user to `submitted` and continue polling for final confirmation.
27. Once the final vote is sent but before a mined-success receipt is available, move the user to `submitted`.
28. In `submitted`, tell the user that the oath has been sent and is waiting for final confirmation in the public record. Do not move to `completed` yet, and do not append support CTA unless receipt monitoring itself is externally blocked.
29. Treat the oath as successful only when the final vote returns a mined-success `txId` from `TxReceipt`.
30. In the success close, show the final vote `txId`, tell the user to join the configured Telegram group, and render the fixed Telegram post template with `{faction_name}` and `{txId}` filled in.
31. If the config is marked as rehearsal-only, say clearly in the visible layer that the current oath record is a testing or rehearsal record and that the formal record will switch in the production launch.

## Required Visible Output

- task label
- the four branded faction names
- one-line faction thesis per faction
- current stage or selection prompt
- token-precheck outcome when relevant
- allowance or authorization outcome when relevant
- password request wording when the `CA` keystore password is missing
- automatic retry wording when authorization or vote confirmation is still being reconciled
- submitted-state waiting explanation when relevant
- blocker summary plus support CTA when the oath cannot continue automatically
- `txId` plus Telegram follow-up template after success
- next step after the oath

## Faction Display Mapping

Load the branded faction names from `../../config/faction-proposals.json`.
Use the matching brand lexicon only for task labels, helper wording, and close-out phrasing.

## Maintainer Notes

- only the config file may carry exact proposal IDs and end times
- use the exact dependency invocation contract from `config/faction-proposals.json` instead of repeating invocation parameters in this file
- use the config file for the dependency minimum version, token symbol, vote amount, generic token-balance tool, generic token-allowance tool, and Telegram success template
- `task3_execution_policy = ca_only_ai_completion`
- `task3_password_policy = ask_once_for_ca_keystore_password`
- `task3_retry_policy = bounded_ca_retries_with_state_reconciliation`
- do not present `Portkey App`, `EOA`, `ManagerForwardCall`, or manual route choices in the visible layer
- when the current signer path is `CA`, the fastest unblock is inside this skill: read allowance, send `Approve` through the existing `CA` write path, reconcile allowance state, then retry the `Vote`
- the spender for the allowance check and approval must be the current vote contract address from the dependency runtime, not a new hardcoded visible-layer constant
- if `environment = test` or `is_test_only = true`, mention the production blocker in the maintainer layer
- do not repeat raw IDs in any other reference file
