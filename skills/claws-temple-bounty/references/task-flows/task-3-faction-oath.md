# Task 3 Faction Oath Flow

Use this flow for Task 3 or any faction belonging request.

## Dependency

- required dependency skill: `tomorrowdao-agent-skills`

## Required Config

Always read `../../config/faction-proposals.json` before rendering the faction list or executing an oath flow.

## Goal

Present four branded factions, map the selected faction to the current rehearsal config, verify the user can fund the vote with 2 AIBOUNTY, add a one-time approval step when the current signer path still has insufficient allowance, and close the flow only after a mined-success vote tx plus Telegram follow-up.

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
7. If `tomorrowdao-agent-skills` is missing or below the configured minimum version, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh tomorrowdao-agent-skills`.
8. If that helper cannot run in the current host, try to install, refresh, or upgrade the dependency from `/Users/huangzongzhe/workspace/TomorrowDAOProject/tomorrowDAO-skill`.
9. If the current host still cannot auto-install or auto-upgrade the dependency, return explicit install or upgrade guidance before any support CTA.
10. Check that the installed dependency version is at least the configured minimum version.
11. Check that the configured generic token-balance tool and generic token-allowance tool are available.
12. Query the configured vote token balance with the configured token symbol.
13. If the balance is below the configured vote amount, stop before vote submission and move the user to `waiting for tokens`.
14. In `waiting for tokens`, tell the user to return after Task 2 pairing succeeds or invite friends to pair so they can build toward the required 2 AIBOUNTY.
15. Treat `waiting for tokens` as a normal unmet-threshold state, not as a support CTA state, unless the token-balance check itself is externally blocked.
16. If the current signer path resolves to a `CA` account or another delegated-spend route, query the current allowance for the vote token against the current vote contract before sending the vote.
17. If the allowance is below the configured vote amount, send one `Approve` transaction for at least the configured vote amount through the available `CA` write path and wait for mined success.
18. Keep the visible layer natural during the allowance step. Tell the user that one more authorization step is being completed before the oath can be sent, but keep the raw contract path and approval tx details in the maintainer layer unless the user asks.
19. Invoke the actual vote only after the mapping, dependency checks, token-balance precheck, and any required approval step all pass; use the exact vote payload contract from the config file.
20. Once the final vote is sent but before a mined-success receipt is available, move the user to `submitted`.
21. In `submitted`, tell the user that the oath has been sent and is waiting for final confirmation in the public record. Do not move to `completed` yet, and do not append support CTA unless receipt monitoring itself is externally blocked.
22. Treat the oath as successful only when the final vote returns a mined-success `txId` from `TxReceipt`.
23. In the success close, show the final vote `txId`, tell the user to join the configured Telegram group, and render the fixed Telegram post template with `{faction_name}` and `{txId}` filled in.
24. If the config is marked as rehearsal-only, say clearly in the visible layer that the current oath record is a testing or rehearsal record and that the formal record will switch in the production launch.

## Required Visible Output

- task label
- the four branded faction names
- one-line faction thesis per faction
- current stage or selection prompt
- token-precheck outcome when relevant
- allowance or authorization outcome when relevant
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
- when the current signer path is `CA`, the fastest unblock is inside this skill: read allowance, send one `Approve` through the existing `CA` write path, then retry the `Vote`
- the spender for the allowance check and approval must be the current vote contract address from the dependency runtime, not a new hardcoded visible-layer constant
- if `environment = test` or `is_test_only = true`, mention the production blocker in the maintainer layer
- do not repeat raw IDs in any other reference file
