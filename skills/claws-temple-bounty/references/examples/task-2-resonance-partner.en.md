# Task 2 Example (English)

> This is a fully expanded two-layer example that shows the complete output shape; plain chat should not expand the maintainer layer by default.

## User Summary

You are at `Task 2: Resonance Pairing`.

Your Coordinate Card is already in place, so the next move is to find the kind of partner who completes your missing side.

Before we enter the actual pairing flow, I should first confirm two things:

- whether your `identity entry` is already open
- whether your own `user ID` is already ready

If this is your first time here, I will take you through the `smoother entry path` first. That is the default recommendation, and it ends with a usable `user ID` for the pairing flow.

Once your identity entry and user ID are ready, two paths are available:

- `Targeted match`: use this when you already know who you want to pair with, and provide the other user's `user ID`.
- `Open partner search`: use this when you want the system to help you find the right resonance partner.

If your identity entry is already open and your own user ID is ready, I can continue with either path now.
If this is your first time here, or your own user ID is still missing, I will take you through identity-entry setup before the pairing flow continues.

### Correction Example

If the user tries to use email, address, or a nickname inside `targeted match`, the reply should say:

`Targeted match now needs the other user's user ID, not an email, address, or nickname. If you already have that user ID, I can continue; if not, we should switch to open partner search.`

### Blocker Example

If identity-entry setup fails, the current user's user ID is still not ready, or the current host cannot continue the pairing path yet, the reply should say:

`The pairing flow cannot continue yet, so I am keeping you at the identity-entry and user-ID setup step for now. Once those prerequisites are ready, we can continue.`

- `→ If you're stuck here, join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) and share your current step, error, and key context so the community can help troubleshoot.`
- `→ You can also post on [X](https://x.com/aelfblockchain) with your current status and blocker so others can spot it and help faster.`

## Maintainer Details

- route: `task-2-resonance-partner`
- dependency_skill: `resonance-contract`
- dependency_contract: `CA only`
- user_id_mapping: `user-facing user ID = dependency ca_hash`
- targeted_match_field: `counterparty_ca_hash`
- open_partner_search_mode: `queue`
- output_style: `brand-layer`
