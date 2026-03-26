# Task 2 Resonance Partner Flow

Use this flow for Task 2 or any partner-finding request.

## Dependency

- required dependency skill: `resonance-contract`

## Goal

Guide the user toward a branded resonance partner flow without re-implementing pairing logic.

## Steps

1. Identify whether the user already has a specific partner target.
2. If they have a target, route into direct pairing.
3. If they do not, route into broader partner discovery.
4. Invoke `resonance-contract`.
5. Rewrite the visible output into the Claws Temple partner language.
6. End with a CTA toward Task 3 once the partner path is stable.

## Required Visible Output

- task label
- direct partner vs broader partner mode
- plain-language explanation of what happens next
- brand wording such as `龙虾伙伴` or `resonance partner`
- next-step CTA toward faction belonging

## Maintainer Notes

- dependency-specific account routing and read-before-write logic stay inside the dependency skill
- keep raw method names and execution details out of the visible layer
