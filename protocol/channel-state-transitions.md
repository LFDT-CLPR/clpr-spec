# Channel State Transitions

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

This module defines a channel's status values, the algorithm by which a CLPR Service processes a bundle and changes the channel's state, and the rules for closing and pausing a channel. The structures it acts on are defined in [messaging](messaging.md), [bundle](bundle.md) and [verifier interface](verifier-interface.md).

## 1. Channel status

Each side of a channel has a status, a value of the enumeration `ChannelStatus`. It is part of the [shared channel state](channel-setup.md#6-shared-channel-state): the peer learns it from the `status` field of [queue metadata](bundle.md#2-queue-metadata).

| Status | Meaning | `sendMessage` | Bundles |
|---|---|---|---|
| PENDING | The channel id is claimed by a registered commitment, and the channel is not yet complete ([registration](channel-setup.md#2-registration)). No channel record exists. | Rejected | Rejected |
| ACTIVE | Normal operation. | Accepted | Processed |
| PAUSED | The peer has violated response ordering (Section 6). | Rejected | Processed |
| CLOSING | The channel is closing. Outbound DATA messages are being answered (Section 5). | Rejected | Processed |
| DRAINED | Every DATA message this side sent has been answered. The peer's remaining messages are still processed (Section 5). | Rejected | Processed |
| CLOSED | Terminal. No further processing. | Rejected | Rejected |

## 2. Bundle processing

Any caller can submit a bundle to the CLPR Service:

```
submitBundle(channel_id: bytes32, bundle: bytes)
```

The CLPR Service processes it with the algorithm below. Processing is atomic: when a step rejects the bundle, every effect of the earlier steps is discarded and the channel is unchanged. A rejected submission costs the submitter its transaction fee; whether a rejection is also treated as misbehavior is local ([Blueprint](../blueprint/clpr-service.md#5-bundle-submission)).

In the pseudocode, `C` is the channel, `T` the ledger's **own** [throttles](ledger-configuration.md#3-throttles), and `md` the returned queue metadata.

```
// Step 1. Pre-checks
if no channel channel_id exists then reject "channel not found"      // includes PENDING
C := the channel channel_id
if C.status = CLOSED then reject "channel closed"
if len(bundle) > T.max_sync_bytes then reject "bundle too large"

// Step 2. Verify
call C.verifier.verifyBundle(bundle, C.trust_anchor, C.channel_context)
if the call fails then reject "verification failed"
(md, msgs, last_id, last_hash, new_anchor, new_anchor_id, new_manifest) := its outputs
if (new_anchor = empty) ≠ (new_anchor_id = empty) then reject "invalid trust anchor id"
n := len(msgs)

// Step 3. Limits
if n > T.max_messages_per_bundle then reject "too many messages"
for each p in msgs
    m := decode MessagePayload(p)
    if m is a DATA message and len(m.message_data) > T.max_message_payload_bytes then
        reject "payload too large"

// Step 4. Progress
if no progress criterion of Section 3 holds then reject "no progress"

// Step 5. Manifest and trust anchor
if new_manifest is present and new_manifest.version > C.endpoint_manifest_version then
    install new_manifest as the peer manifest
if new_anchor ≠ empty then
    C.trust_anchor := new_anchor
    C.trust_anchor_id := new_anchor_id

// Step 6. Replay defense
if md.next_message_id < C.received_message_id + 1 then reject "replay"
if n > 0 then
    if last_id < n or last_id ≥ md.next_message_id then reject "invalid message range"
    if last_id < C.received_message_id or last_id > C.received_message_id + n then
        reject "message gap"
// msgs[i] has id last_id − n + 1 + i
new := the messages of msgs whose id > C.received_message_id, in id order

// Step 7. Running hash
h := C.received_running_hash
for each p in new
    h := SHA-256(h ‖ SHA-256(p))
if n > 0 and h ≠ last_hash then reject "running hash mismatch"
if n = 0 and md.next_message_id = C.received_message_id + 1
        and md.sent_running_hash ≠ C.received_running_hash then
    reject "running hash mismatch"

// Step 8. Acknowledgement check
if md.received_message_id < C.acked_message_id
        or md.received_message_id > C.next_message_id − 1 then
    reject "invalid acknowledgement"

// Step 9. Response ordering
if new violates response ordering then
    if C.status = ACTIVE then C.status := PAUSED
    return                                   // no message is processed (Section 6)

// Step 10. Acknowledgement
C.acked_message_id := md.received_message_id
delete the REPLY and CONTROL messages with id ≤ C.acked_message_id from the outbound queue

// Step 11. Auto-resume
if C.status = PAUSED then C.status := ACTIVE

// Step 12. Configuration propagation
if C.status = ACTIVE and a ConfigUpdate is due then
    enqueue the ConfigUpdate

// Step 13. Dispatch
for each p in new
    dispatch p
if new is not empty then
    C.received_message_id := last_id
    C.received_running_hash := h

// Step 14. Status
if C.status = ACTIVE and md.status is one of CLOSING, DRAINED, CLOSED then
    C.status := CLOSING
if C.status = CLOSING and the outbound queue holds no DATA message then
    C.status := DRAINED
if C.status = DRAINED and md.status is one of DRAINED, CLOSED
        and C.acked_message_id ≥ C.next_message_id − 1
        and C.received_message_id ≥ md.next_message_id − 1 then
    C.status := CLOSED
```

Notes on the steps:

- **Step 1.** A PENDING channel has no record, so its bundles are rejected as for an unknown channel.
- **Step 2.** The verifier is invoked as defined in [verifier interface](verifier-interface.md#3-verifybundle). The trust anchor id rule is [verifier interface §4](verifier-interface.md#4-trust-anchor-changes).
- **Step 3.** The count includes messages the channel has already received. The payload limit applies only to the `message_data` of DATA messages.
- **Step 5.** The manifest update is defined in [peer manifest](endpoint-manifest.md#4-peer-manifest). The new manifest and the new trust anchor take effect before any message of the bundle is processed, so every message is attributed to the authority that proved it.
- **Step 6.** A bundle can start with messages the channel has already received; they are skipped by every later step. A bundle cannot skip a message: Step 6 rejects a gap.
- **Step 7.** The running hash is defined in [messaging §4](messaging.md#4-running-hash); `p` is a message's payload bytes. For a REDACTED message, see [messaging §10](messaging.md#10-redaction-deprecated). When every message is skipped, `h` is the stored `received_running_hash`, and Step 7 rejects the bundle unless it equals `last_hash`.
- **Step 8.** An acknowledgement that moves backwards, or that acknowledges a message that was never sent, is rejected.
- **Step 9.** Response ordering is defined in [messaging §8](messaging.md#8-response-ordering). It is checked over all of `new` before any message is dispatched. The effects of a violation are defined in Section 6.
- **Step 10.** The acknowledgement rule is [messaging §9](messaging.md#9-acknowledgement).
- **Step 12.** The rules for when a ConfigUpdate is due and when it is enqueued are in [configuration propagation](ledger-configuration.md#52-sending). It is enqueued before any message that the dispatch enqueues. A channel that the peer's status moves to CLOSING in this bundle still receives it.
- **Step 14.** The checks run in order, so one bundle can apply several transitions. A CLPR Service MAY instead apply the first transition, ACTIVE to CLOSING, after Step 12 and before Step 13. The bundle's messages are dispatched in either case.

**Dispatch.** Each message in `new` is processed by type:

| Type | Processing |
|---|---|
| CONTROL | Apply it as defined in [configuration propagation](ledger-configuration.md#53-receiving). Reject the bundle if that check fails, or if the control message type is not set or is unknown ([message types](messaging.md#1-message-types)). No REPLY. |
| DATA | Deliver it ([delivery](messaging.md#6-delivery-to-the-application)). Enqueue one REPLY with `message_id` set to the DATA message's id and the outcome as `status`. |
| REPLY | Deliver it to the sender of the answered DATA message ([delivery](messaging.md#6-delivery-to-the-application)) and delete that DATA message from the outbound queue. The CLPR Service applies its charging and slashing policy ([replies](messaging.md#7-replies)). |
| REDACTED | Enqueue one REPLY with status REDACTED and empty `message_reply_data` ([redaction](messaging.md#10-redaction-deprecated)). |

A failure of a connector or an application affects only the REPLY of that message; the other messages are processed normally. A payload that fails [strict decoding](conventions.md#3-abstract-data-structures) rejects the whole bundle.

## 3. Progress

A bundle **makes progress** if at least one of the following criteria holds. The CLPR Service MUST reject a bundle that meets none of them (Step 4). The criteria are evaluated against the channel's state before the bundle.

| # | Criterion | Holds when |
|---|---|---|
| 1 | New messages | `n > 0` and `last_id > C.received_message_id` |
| 2 | [Trust anchor change](verifier-interface.md#4-trust-anchor-changes) | `new_anchor` is non-empty and `new_anchor_id ≠ C.trust_anchor_id` |
| 3 | Manifest update | `new_manifest` is present and `new_manifest.version > C.endpoint_manifest_version` |
| 4 | Acknowledgement | `md.received_message_id > C.acked_message_id` |
| 5a | Peer closing | `C.status` is ACTIVE or PAUSED, and `md.status` is CLOSING, DRAINED or CLOSED |
| 5b | Drain | `C.status = CLOSING`, and every DATA message in the outbound queue is answered by a REPLY among the bundle's new messages |
| 5c | Close | `C.status = DRAINED`; `md.status` is DRAINED or CLOSED; `max(C.acked_message_id, md.received_message_id) ≥ C.next_message_id − 1`; and `C.received_message_id ≥ md.next_message_id − 1` |

A bundle for a CLOSED channel is rejected by Step 1, not for lack of progress. CLPR Endpoints SHOULD NOT submit bundles that make no progress ([Blueprint](../blueprint/clpr-service.md#5-bundle-submission)).

## 4. Status transitions

| From | To | Trigger | Condition |
|---|---|---|---|
| (none) | PENDING | `registerChannel` | [Registration](channel-setup.md#2-registration) |
| PENDING | ACTIVE | `completeChannel` | [Registration](channel-setup.md#2-registration) |
| PENDING | (none) | Administration | The claim is removed ([Blueprint](../blueprint/clpr-service.md#2-administration)). |
| ACTIVE | PAUSED | Bundle, Step 9 | A response ordering violation. |
| PAUSED | ACTIVE | Bundle, Step 11 | A bundle accepted without a response ordering violation. |
| ACTIVE | CLOSING | Bundle, Step 14 | `md.status` is CLOSING, DRAINED or CLOSED. |
| ACTIVE, PAUSED | CLOSING | Administration | Close ([Blueprint](../blueprint/clpr-service.md#2-administration)). The channel continues to DRAINED in the same step if its outbound queue holds no DATA message. |
| CLOSING | DRAINED | Bundle, Step 14 | The outbound queue holds no DATA message. |
| DRAINED | CLOSED | Bundle, Step 14 | `md.status` is DRAINED or CLOSED, and `C.acked_message_id ≥ C.next_message_id − 1`, and `C.received_message_id ≥ md.next_message_id − 1`. |
| DRAINED | CLOSED | Administration | Recovery close ([Blueprint](../blueprint/clpr-service.md#2-administration)). |

No other transition is permitted. A bundle reaches CLOSING from PAUSED by first resuming to ACTIVE. Administrative transitions are local to one ledger; the peer observes their result through `md.status`.

## 5. Closing and draining

Closing takes both sides of a channel through CLOSING and DRAINED to CLOSED, so that every DATA message sent on the channel is delivered and answered before either side stops.

**CLOSING.** A side enters CLOSING by administrative close or when a bundle shows that the peer is closing. Applications can no longer send. Bundles are processed normally: the peer's DATA messages are delivered and answered, REPLY messages are delivered, and acknowledgements advance. No ConfigUpdate is enqueued. The side becomes DRAINED when its outbound queue holds no DATA message, that is, when every DATA message it sent has been acknowledged and answered. REPLY messages it generated for the peer can still be unacknowledged.

**DRAINED.** Bundles are still processed: the peer can still be draining, so its DATA messages are delivered and answered, and the REPLY messages are added to the outbound queue. The side becomes CLOSED when a bundle shows that:

1. the peer is DRAINED or CLOSED;
2. the peer has acknowledged every message of this side (`C.acked_message_id ≥ C.next_message_id − 1`); and
3. this side has received every message in the peer's proven queue (`C.received_message_id ≥ md.next_message_id − 1`).

Condition 3 is needed because a bundle can end before the peer's latest message ([partial bundles](bundle.md#3-partial-bundles)): the peer's status alone does not show that its REPLY messages to this side have arrived.

**CLOSED.** Terminal. Every bundle and every `sendMessage` call is rejected. CLPR Endpoints no longer start sync cycles for the channel. As responders they MAY still send a bundle that reports CLOSED, which lets a DRAINED peer reach CLOSED ([rules](endpoint-sync/README.md#32-rules)).

There is no close notification. A bundle whose `md.status` is CLOSED is processed like any other: it moves an ACTIVE or PAUSED side to CLOSING, and a DRAINED side to CLOSED when the conditions above hold. If no such bundle reaches a DRAINED side, the recovery path is administrative ([Blueprint](../blueprint/clpr-service.md#25-closing-a-channel)).

## 6. Pause and resume

PAUSED is reserved for **response ordering violations** ([messaging §8](messaging.md#8-response-ordering)). A violation shows that the peer's outbound queue is inconsistent; it cannot be repaired by resending. A bundle that fails verification or any other check of Section 2 is rejected and does not change the channel's status.

When a bundle contains a response ordering violation (Step 9):

- No message of the bundle is processed: nothing is dispatched, and `received_message_id` and `received_running_hash` do not change.
- An ACTIVE channel becomes PAUSED. Any other status is unchanged.
- The manifest and trust anchor replacements of Step 5 take effect. The CLPR Service MAY also apply the acknowledgement of Step 10.
- On a CLOSING or DRAINED channel, the CLPR Service MAY reject the bundle instead.

While PAUSED, applications cannot send, and queued outbound messages continue to sync to the peer. A bundle with a violation is processed only up to Step 9. The first bundle accepted without a violation returns the channel to ACTIVE (Step 11) and is then processed normally. This requires the peer to correct its outbound queue.

The administrator can close a PAUSED channel ([Blueprint](../blueprint/clpr-service.md#25-closing-a-channel)). It then becomes CLOSING, and it cannot drain until the peer's REPLY messages arrive in order. DATA messages on a channel that never drains remain without a REPLY ([OI-4](open-issues.md#oi-4-messages-left-without-replies-when-a-channel-cannot-drain)).

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
