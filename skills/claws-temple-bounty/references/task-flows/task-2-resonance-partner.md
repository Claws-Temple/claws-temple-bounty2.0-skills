# Task 2 Resonance Partner Flow

Use this flow for Task 2 or any partner-finding request.

## Dependency

- required dependency skill: `resonance-contract`

## Goal

Guide the user toward a branded resonance partner flow, including first-time identity-entry onboarding, user-ID readiness, and the choice between targeted match and open partner search, without re-implementing pairing logic.

## Steps

1. Identify whether the user already has a specific partner target.
2. Before any targeted-match or queue action, confirm whether the user's `identity entry` is already open.
3. Confirm whether the user already has their own `user ID`.
4. If the user is first-time, or the identity entry is not fully ready, route them into identity-entry setup first.
5. Recommend the smoother entry path when the user has no strong preference, and explain that it ends with a usable `user ID`.
6. If the user has a specific partner target, route into `targeted match`.
7. In `targeted match`, ask for the other user's `user ID`.
8. If the user does not have a specific target, route into `open partner search`.
9. Explain plainly that `open partner search` is the automatic queue-matching path and does not require a preselected target.
10. If the user provides `email`, `Address`, nickname, `tDVV` address, or other non-`user ID` input for targeted match, correct the input in plain language and offer two next steps: provide the other user's `user ID`, or switch to `open partner search`.
11. Invoke `resonance-contract` only after identity-entry readiness, the current user's own `user ID`, and the participation mode are clear.
12. If identity-entry setup or the pairing path is blocked and the agent cannot continue automatically, return a blocker summary and append support CTA.
13. Rewrite the visible output into the Claws Temple partner language.
14. End with a CTA toward Task 3 once the partner path is stable.

## Required Visible Output

- task label
- identity-entry readiness prompt
- current-user `user ID` readiness prompt
- `targeted match` vs `open partner search`
- wording that `open partner search` is the automatic queue-matching path
- plain-language explanation of what happens next
- brand wording such as `龙虾伙伴` or `resonance partner`
- first-time user wording such as `先开通身份入口`
- wording that the smoother entry path ends with a `用户ID / user ID`
- targeted-match wording such as `请提供对方的用户ID`
- wording such as `如果你没有具体对象，就直接走开放寻配，这条路就是系统自动排队匹配`
- blocker summary plus support CTA when the user is genuinely stuck
- next-step CTA toward faction belonging

## Maintainer Notes

- dependency-specific account routing, local-context preparation, and read-before-write logic stay inside the dependency skill
- the dependency write path is `CA only`, but the default visible layer should not say `CA`, `AA`, or `EOA`
- user-facing `用户ID / user ID` maps to dependency `ca_hash`
- user-facing `targeted match` maps to dependency direct pair with `counterparty_ca_hash`
- user-facing `open partner search` maps to dependency `queue`
- do not mention legacy community-brand wording, legacy platform names outside Telegram and X, legacy runtime-address wording, or address-based matching in the visible layer
- do not accept `email`, `Address`, or nickname as a direct-match identifier
- keep raw method names and execution details out of the visible layer
