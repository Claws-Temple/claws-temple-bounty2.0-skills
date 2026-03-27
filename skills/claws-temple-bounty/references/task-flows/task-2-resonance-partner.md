# Task 2 Resonance Partner Flow

Use this flow for Task 2 or any partner-finding request.

## Dependency

- required dependency skill: `resonance-contract`

## Goal

Guide the user toward a branded resonance partner flow, including first-time registration, returning-user recovery sign-in, user-ID readiness, and the choice between targeted match and open partner search, without re-implementing pairing logic.

## Steps

1. Identify whether the user already has a specific partner target.
2. Before any targeted-match or queue action, confirm whether the user's `identity entry` is already open.
3. Confirm whether the user already has their own `user ID`.
4. If the user is first-time, or the identity entry is not fully ready, route them into identity-entry setup first.
5. If the user is first-time, explain that the smoother entry path starts with registration or first-time setup and ends with a usable `user ID`.
6. If the user is returning but not currently signed in, explain that the smoother entry path starts with recovery sign-in and ends with a usable `user ID`.
7. If the user has a specific partner target, route into `targeted match`.
8. In `targeted match`, ask for the other user's `user ID`.
9. If the user does not have a specific target, route into `open partner search`.
10. Explain plainly that `open partner search` is the automatic queue-matching path and does not require a preselected target.
11. Invoke `resonance-contract` only after identity-entry readiness, the current user's own `user ID`, and the participation mode are clear.
12. If dependency queue preflight can proceed, continue into queue send and do not suggest skipping Task 2, replacing queue with Telegram or X posting, or claiming there is no usable direct tool.
13. If the user provides `email`, `Address`, nickname, `tDVV` address, or other non-`user ID` input for targeted match, correct the input in plain language and offer two next steps: provide the other user's `user ID`, or switch to `open partner search`.
14. If registration, recovery sign-in, identity-entry setup, or the pairing path is genuinely blocked and the agent cannot continue automatically, return a blocker summary and append support CTA.
15. Rewrite the visible output into the Claws Temple partner language.
16. End with a CTA toward Task 3 once the partner path is stable.

## Required Visible Output

- task label
- identity-entry readiness prompt
- current-user `user ID` readiness prompt
- first-time registration or first-time setup wording
- returning-user recovery sign-in wording
- `targeted match` vs `open partner search`
- wording that `open partner search` is the automatic queue-matching path
- plain-language explanation of what happens next
- brand wording such as `龙虾伙伴` or `resonance partner`
- first-time user wording such as `先开通身份入口`
- wording such as `如果你是老用户但这次还没登录，我会先带你完成恢复登录`
- wording that the smoother entry path ends with a `用户ID / user ID`
- targeted-match wording such as `请提供对方的用户ID`
- wording such as `如果你没有具体对象，就直接走开放寻配，这条路就是系统自动排队匹配`
- wording that queue should continue once onboarding is ready, instead of skipping Task 2 or replacing it with social fallback
- blocker summary plus support CTA when the user is genuinely stuck
- next-step CTA toward faction belonging

## Maintainer Notes

- dependency-specific account routing, local-context preparation, and read-before-write logic stay inside the dependency skill
- the dependency write path is `CA only`, but the default visible layer should not say `CA`, `AA`, or `EOA`
- user-facing `identity entry` maps to dependency local account-context readiness; first-time setup may create that context, while returning-user recovery sign-in may restore it
- user-facing `用户ID / user ID` maps to dependency `ca_hash`
- user-facing `targeted match` maps to dependency direct pair with `counterparty_ca_hash`
- user-facing `open partner search` maps to dependency `queue`
- if dependency queue preflight can proceed, do not replace the flow with Telegram or X outreach and do not suggest skipping Task 2
- do not mention legacy community-brand wording, legacy platform names outside Telegram and X, legacy runtime-address wording, or address-based matching in the visible layer
- do not accept `email`, `Address`, or nickname as a direct-match identifier
- keep raw method names and execution details out of the visible layer
