# Task 2 Resonance Partner Flow

Use this flow for Task 2 or any partner-finding request.

## Dependency

- required dependency skill: `resonance-contract`

## Goal

Guide the user toward a branded resonance partner flow, including first-time identity-entry onboarding, without re-implementing pairing logic.

## Steps

1. Identify whether the user already has a specific partner target.
2. If they have a target, route into direct pairing.
3. If they do not, route into broader partner discovery.
4. Before any pairing or queue action, confirm whether the user's `identity entry` is already prepared.
5. If the user is first-time or not prepared yet, route them into identity-entry setup first.
6. Recommend the smoother entry path when the user has no strong preference.
7. Invoke `resonance-contract` only after identity-entry readiness and participation mode are clear.
8. Rewrite the visible output into the Claws Temple partner language.
9. End with a CTA toward Task 3 once the partner path is stable.

## Required Visible Output

- task label
- identity-entry readiness or setup prompt
- direct partner vs broader partner mode
- plain-language explanation of what happens next
- brand wording such as `龙虾伙伴` or `resonance partner`
- first-time user wording such as `先开通身份入口`
- next-step CTA toward faction belonging

## Maintainer Notes

- dependency-specific account routing, local-context preparation, and read-before-write logic stay inside the dependency skill
- keep raw method names and execution details out of the visible layer
