# Task 3 Faction Oath Flow

Use this flow for Task 3 or any faction belonging request.

## Dependency

- required dependency skill: `tomorrowdao-agent-skills`

## Required Config

Always read `../../config/faction-proposals.json` before rendering the faction list or executing an oath flow.

## Goal

Present four branded factions, map the selected faction to the current rehearsal config, and keep the visible layer free of internal naming.

## Steps

1. Read the faction config file.
2. Present the four branded factions with one-line positioning.
3. If the user has not chosen, help them pick one in brand language.
4. Map the branded choice to the config entry.
5. Run a rehearsal-safe preflight:
   - confirm the selected faction entry exists
   - confirm the dependency invocation contract exists in the config file
   - confirm the required proposal id is present
   - confirm the proposal end time is still in the future
6. Invoke the dependency skill only after the mapping is confirmed and use the exact invocation contract from the config file.
7. If the config is marked as rehearsal-only, keep the visible layer natural and place the production replacement blocker in the maintainer layer.

## Required Visible Output

- task label
- the four branded faction names
- one-line faction thesis per faction
- selected faction or selection prompt
- next step after the oath

## Faction Display Mapping

Load the branded faction names from `../../config/faction-proposals.json`.
Use the matching brand lexicon only for task labels, helper wording, and close-out phrasing.

## Maintainer Notes

- only the config file may carry exact proposal IDs and end times
- use the exact dependency invocation contract from `config/faction-proposals.json` instead of repeating invocation parameters in this file
- if `environment = test` or `is_test_only = true`, mention the production blocker in the maintainer layer
- do not repeat raw IDs in any other reference file
