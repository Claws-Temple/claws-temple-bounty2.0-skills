# Task 3 Example (English)

> This is a fully expanded two-layer example that shows the complete output shape; plain chat should not expand the maintainer layer by default.

## User Summary

You are at `Task 3: Faction Belonging`.

The four branded factions are:

- `The Imprints`: memory, witness, and lasting marks
- `The Crucibles`: sovereignty, heat, and self-built foundations
- `The Metamorphs`: evolution, mutation, and new forms
- `The Sentinels`: balance, structure, and shared continuity

If your coordinate card leans toward history and memory, `The Imprints` is a natural fit.
Current stage: `selected`, not completed yet.
If you want, I can take your choice and continue the oath flow now.

### Stage Samples

- `selected`: the user has chosen a faction, but the oath has not started yet.
- `waiting for tokens`: the faction is chosen, but the user still does not meet the 2 AIBOUNTY requirement for the vote.
- `ready to oath`: mapping, version, timing, and token prechecks are complete; if this path still needs one authorization step, that approval happens first and then the actual oath submission continues.
- `submitted`: the oath has been sent and is waiting to settle into the public record.
- `completed`: the oath transaction has succeeded and the user now has the `txId` they must report in Telegram.

### Blocker Example

If the direction is already chosen but the user does not yet have 2 AIBOUNTY, the reply should say:

`Your direction is already locked in, but you do not yet meet the 2 AIBOUNTY requirement for the oath vote. I am keeping you in the waiting-for-tokens stage for now. You can return after Task 2 pairing succeeds, or invite friends to pair so you can build toward the required tokens.`

- `→ If you're stuck here, join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) and share your current step, error, and key context so the community can help troubleshoot.`
- `→ You can also post on [X](https://x.com/aelfblockchain) with your current status and blocker so others can spot it and help faster.`

### Approval Example

If the user already has enough `AIBOUNTY` but this path still needs one vote authorization step, the reply should say:

`You already meet the 2 AIBOUNTY requirement for the faction oath, but this path still needs one final authorization step. I will complete that approval first, and then continue with the actual oath vote.`

### Success Example

If the oath transaction already succeeded and returned a `txId`, the reply should say:

`Your faction oath has succeeded and your current reference is txid-1234. Join the [Telegram group](https://t.me/+tChFhfxgU6AzYjJl) now and send the message below. There is also an extra 20 Token claim in two weeks, and any questions can go straight into the group.`

If this path included a prior approval step, the reply should also remind the user:

`If an approval step happened just before this, the number you should post in Telegram is still the final oath txid-1234, not the approval tx id.`

Telegram post template:

`I am with The Sentinels, reference txid-1234. I have completed Claws Temple Task 3. There is an extra 20 Token claim in two weeks, and I am happy to discuss any questions in the group.`

## Maintainer Details

- route: `task-3-faction-oath`
- config_path: `skills/claws-temple-bounty/config/faction-proposals.json`
- active_environment: `test`
- dependency_min_version: `0.2.0`
- ca_vote_path: `allowance precheck -> Approve if needed -> Vote`
- launch_blocker: `Replace all rehearsal faction-hall and faction proposal records before production launch.`
