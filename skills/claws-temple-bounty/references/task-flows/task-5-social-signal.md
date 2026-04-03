# Task 5 Social Signal Flow

Use this flow for Task 5 or any optional public signal request.

## Dependency

- use `resonance-contract` when a structured pairing handoff is needed
- otherwise direct drafting inside this skill is acceptable

## Goal

Help the user send a public signal on Telegram, X, or the Curio Board without treating this task as mandatory. This is the step where more partners can finally spot the user's Agent. The visible layer should first frame the agent as the drafter, and only promise direct send when the current host really has the required permissions and capability.

## Steps

1. Remind the user this task is optional.
2. Ask which platform the user wants if the platform is still unknown.
3. Draft a short branded signal.
4. If the user already has a coordinate card or faction result, fold that into the signal.
5. Whenever the visible layer mentions sending now on `Telegram` or `X`, first add one short boundary line: the agent drafts first, direct send continues only if the current host really has the required permissions and capability, and otherwise the final send click belongs to the user.
6. Treat browser capability as confirmed only when the current turn already has one of these signals: a successful browser or native action in this session, an exposed host capability marker or tool manifest, or an explicit user confirmation that this exact session can open browser actions.
7. If the user wants to send now on `Telegram` or `X` but browser capability is not confirmed yet, ask for that confirmation in one short step or keep the reply in draft-plus-link mode; do not hint browser action yet.
8. The confirmation question should stay concrete: `Can this exact session open browser actions right now?` If the answer is unknown or negative, stay in draft-plus-link mode and keep the final send click with the user.
9. If the current host is `OpenClaw`, the user already chose `Telegram` or `X`, the user explicitly wants to send now, and the current turn already confirmed browser capability, add one short visible-layer hint that browser action can be used directly in `OpenClaw` after that host-capability caveat.
10. Do not mention browser action before the user has chosen a platform, when the user only wants draft copy, or in hosts other than `OpenClaw`.
11. If the user explicitly wants to send the signal now but the current context blocks that action, return a blocker summary and append support CTA.
12. End with a community-reach framing instead of a blocker framing when the signal path is otherwise healthy.

## Platform Templates

- `TG`: slightly longer, conversational, may use 2 short paragraphs and a clear reply CTA; when practical, point the user to the clickable `Telegram group` link
- `X`: one compact post, keep it within a short single-post format; when practical, point the user to the clickable `X` link
- `Curio Board`: slightly more descriptive, may mention what kind of resonance partner the user wants
- `OpenClaw host hint`: when the user already chose `TG` or `X`, wants to send now, and browser capability is confirmed in the current turn, the visible layer may say that browser action can be used directly in `OpenClaw`

Each platform draft should include:

- current coordinate or direction
- what kind of partner or response the user wants
- one direct CTA

## Required Visible Output

- task label
- optional-task reminder
- post copy or signal draft
- host-capability boundary wording whenever the user wants to send now on `TG` or `X`
- one short capability-confirmation step or draft-first fallback when browser capability is not yet confirmed
- clickable platform links when the user asks where to post
- OpenClaw browser-action hint only when the platform is already chosen and the user wants to send now
- recommended CTA
- blocker summary plus support CTA only when the user is genuinely stuck on sending

## Maintainer Notes

- keep this task clearly separated from the main qualification path
- do not imply that Task 5 is required for unlock
- keep browser-action wording host-aware: `OpenClaw` only, `Telegram` or `X` only, only when the user explicitly wants to send now, and only when browser capability is already confirmed
- treat browser capability confirmation as same-turn evidence only: successful browser or native action, exposed capability marker or tool manifest, or explicit user confirmation for the current session
- when browser capability is not confirmed, use one explicit confirmation question or stay in draft-plus-link mode; avoid vague wording like `maybe the host can do it`
- never imply guaranteed auto-posting; the safe default is draft first, then direct send only when the host can really do it
