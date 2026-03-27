# Task 3 Faction Oath Flow

Use this flow for Task 3 or any faction belonging request.

## Dependency

- required dependency skill: `tomorrowdao-agent-skills`

## Required Config

Always read `../../config/faction-proposals.json` before rendering the faction list or executing an oath flow.

## Goal

Present four branded factions, map the selected faction to the current rehearsal config, verify the user can fund the vote with 2 AIBOUNTY, and close the flow only after a mined-success tx plus Telegram follow-up.

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
7. Check that the installed dependency version is at least the configured minimum version.
8. Check that the configured generic token-balance tool is available.
9. Query the configured vote token balance with the configured token symbol.
10. If the balance is below the configured vote amount, stop before vote submission and move the user to `waiting for tokens`.
11. In `waiting for tokens`, tell the user to return after Task 2 pairing succeeds or invite friends to pair so they can build toward the required 2 AIBOUNTY.
12. Invoke the dependency skill only after the mapping, dependency checks, and token-balance precheck all pass; use the exact vote payload contract from the config file.
13. Treat the vote as successful only when a mined-success `txId` is returned from `TxReceipt`.
14. In the success close, show the `txId`, tell the user to join the configured Telegram group, and render the fixed Telegram post template with `{faction_name}` and `{txId}` filled in.
15. If the config is marked as rehearsal-only, keep the visible layer natural and place the production replacement blocker in the maintainer layer.

## Required Visible Output

- task label
- the four branded faction names
- one-line faction thesis per faction
- current stage or selection prompt
- token-precheck outcome when relevant
- blocker summary plus support CTA when the oath cannot continue automatically
- `txId` plus Telegram follow-up template after success
- next step after the oath

## Faction Display Mapping

Load the branded faction names from `../../config/faction-proposals.json`.
Use the matching brand lexicon only for task labels, helper wording, and close-out phrasing.

## Maintainer Notes

- only the config file may carry exact proposal IDs and end times
- use the exact dependency invocation contract from `config/faction-proposals.json` instead of repeating invocation parameters in this file
- use the config file for the dependency minimum version, token symbol, vote amount, generic token-balance tool, and Telegram success template
- if `environment = test` or `is_test_only = true`, mention the production blocker in the maintainer layer
- do not repeat raw IDs in any other reference file
