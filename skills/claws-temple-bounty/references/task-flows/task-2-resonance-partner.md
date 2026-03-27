# Task 2 Resonance Partner Flow

Use this flow for Task 2 or any partner-finding request.

## Dependency

- required dependency skill: `resonance-contract`

## Goal

Guide the user toward a branded resonance partner flow, including first-time registration, returning-user recovery sign-in, auto-resolving the current user's own user ID, and the choice between targeted match and open partner search, without re-implementing pairing logic.

## Steps

1. Identify whether the user already has a specific partner target.
2. Before any targeted-match or queue action, ask the user in direct language whether this is the first time here or whether they have already used the identity entry before.
3. Confirm whether the user is already signed in this time; if the user is returning but not currently signed in, route them into recovery sign-in first.
4. If the user is first-time, or the identity entry is not fully ready, route them into identity-entry setup first.
5. If the user is first-time, explain that the smoother entry path starts with registration or first-time setup and ends with a usable `user ID`.
6. If the user is returning but not currently signed in, explain that the smoother entry path starts with recovery sign-in and ends with a usable `user ID`.
7. If `resonance-contract` is missing or below `3.0.1`, first try the bundled self-heal helper `../../scripts/self-heal-local-dependency.sh resonance-contract`.
8. If that helper cannot run in the current host, try to install, refresh, or upgrade the dependency from `/Users/huangzongzhe/workspace/vibeCoding/agent-resonance-skill/skills/resonance-contract`.
9. If the current host still cannot auto-install or auto-upgrade the dependency, return explicit install or upgrade guidance before any support CTA.
10. Once identity entry and sign-in are ready, auto-resolve the current user's own `user ID` from the dependency context instead of asking the user to type it manually.
11. If that user-ID resolution succeeds, show the full resolved current-user `user ID` in the visible layer so the queue path can be confirmed.
12. If that user-ID resolution fails, keep the user in the identity-entry or recovery branch and do not ask the user to paste their own `user ID`.
13. If the user has a specific partner target, route into `targeted match`.
14. In `targeted match`, ask for the other user's `user ID`.
15. If the user does not have a specific target, route into `open partner search`.
16. Explain plainly that `open partner search` is the automatic queue-matching path and does not require a preselected target.
17. Invoke `resonance-contract` only after identity-entry readiness, sign-in readiness, the auto-resolved current-user `user ID`, and the participation mode are clear.
18. If dependency queue preflight can proceed, continue into queue send and do not suggest skipping Task 2, replacing queue with Telegram or X posting, or claiming there is no usable direct tool.
19. Treat the Task 2 path as stable enough for the Task 3 handoff when either the direct pair submission has been sent or the queue join is active. Do not promise that a real partner has already been found unless the dependency flow actually returned that result.
20. If the user provides `email`, `Address`, nickname, `tDVV` address, or other non-`user ID` input for targeted match, correct the input in plain language and offer two next steps: provide the other user's `user ID`, or switch to `open partner search`.
21. If registration, recovery sign-in, dependency self-heal, identity-entry setup, or the pairing path is genuinely blocked and the agent cannot continue automatically, return a blocker summary and append support CTA.
22. Rewrite the visible output into the Claws Temple partner language.
23. End with a CTA toward Task 3 once the partner path is stable.

## Required Visible Output

- task label
- identity-entry readiness prompt
- sign-in or recovery prompt
- first-time registration or first-time setup wording
- returning-user recovery sign-in wording
- wording that asks in direct user language whether this is the first time here or a returning-but-not-signed-in visit
- visible confirmation that the current user's `user ID` was auto-resolved
- `targeted match` vs `open partner search`
- wording that `open partner search` is the automatic queue-matching path
- plain-language explanation of what happens next
- brand wording such as `龙虾伙伴` or `resonance partner`
- first-time user wording such as `先开通身份入口`
- wording such as `如果你是老用户但这次还没登录，我会先带你完成恢复登录`
- wording that the smoother entry path ends with a `用户ID / user ID`
- wording such as `我会先自动解析你当前的用户ID，不需要你自己手动填写`
- wording such as `已解析到你的用户ID`
- targeted-match wording such as `请提供对方的用户ID`
- wording such as `如果你没有具体对象，就直接走开放寻配，这条路就是系统自动排队匹配`
- wording such as `只要开放寻配已经正式入队，或指定匹配请求已经发出，我就会把 Task 2 视为路径已稳定，可以继续 Task 3`
- wording that Task 2 can hand off to Task 3 once the pairing path is stable, without falsely claiming a partner is already found
- wording that queue should continue once onboarding is ready, instead of skipping Task 2 or replacing it with social fallback
- blocker summary plus support CTA when the user is genuinely stuck
- next-step CTA toward faction belonging

## Maintainer Notes

- dependency-specific account routing, local-context preparation, and read-before-write logic stay inside the dependency skill
- the dependency write path is `CA only`, but the default visible layer should not say `CA`, `AA`, or `EOA`
- user-facing `identity entry` maps to dependency local account-context readiness; first-time setup may create that context, while returning-user recovery sign-in may restore it
- the current user's own `用户ID / user ID` should be auto-resolved from dependency context once onboarding is ready; the user should not be asked to type it manually for queue participation
- user-facing `用户ID / user ID` maps to dependency `ca_hash`
- user-facing `targeted match` maps to dependency direct pair with `counterparty_ca_hash`
- user-facing `open partner search` maps to dependency `queue`
- if dependency queue preflight can proceed, do not replace the flow with Telegram or X outreach and do not suggest skipping Task 2
- do not mention legacy community-brand wording, legacy platform names outside Telegram and X, legacy runtime-address wording, or address-based matching in the visible layer
- do not accept `email`, `Address`, or nickname as a direct-match identifier
- keep raw method names and execution details out of the visible layer
