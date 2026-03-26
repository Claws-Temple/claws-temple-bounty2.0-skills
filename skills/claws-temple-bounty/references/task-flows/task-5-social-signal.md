# Task 5 Social Signal Flow

Use this flow for Task 5 or any optional public signal request.

## Dependency

- use `resonance-contract` when a structured pairing handoff is needed
- otherwise direct drafting inside this skill is acceptable

## Goal

Help the user send a public signal on Telegram, X, or the Curio Board without treating this task as mandatory.

## Steps

1. Remind the user this task is optional.
2. Ask which platform the user wants if the platform is still unknown.
3. Draft a short branded signal.
4. If the user already has a coordinate card or faction result, fold that into the signal.
5. If the user explicitly wants to send the signal now but the current context blocks that action, return a blocker summary and append support CTA.
6. End with a community-reach framing instead of a blocker framing when the signal path is otherwise healthy.

## Platform Templates

- `TG`: slightly longer, conversational, may use 2 short paragraphs and a clear reply CTA
- `X`: one compact post, keep it within a short single-post format
- `Curio Board`: slightly more descriptive, may mention what kind of resonance partner the user wants

Each platform draft should include:

- current coordinate or direction
- what kind of partner or response the user wants
- one direct CTA

## Required Visible Output

- task label
- optional-task reminder
- post copy or signal draft
- recommended CTA
- blocker summary plus support CTA only when the user is genuinely stuck on sending

## Maintainer Notes

- keep this task clearly separated from the main qualification path
- do not imply that Task 5 is required for unlock
