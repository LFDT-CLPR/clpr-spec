# Messaging

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

This module defines the messages a channel carries, the outbound queue that holds them, the running hash that secures the queue, and the rules for sending, delivering, answering and acknowledging messages. How a bundle carries messages to the peer, and how the receiving CLPR Service processes it, is defined in [bundle](bundle.md) and [channel state transitions](channel-state-transitions.md#2-bundle-processing).

## 1. Message types

A message's content is a `MessagePayload`: exactly one of the following types.

| Type | Content | Produced by | Answered by a REPLY |
|---|---|---|---|
| DATA | Application content (`DataMessage`) | An application, through `sendMessage` (Section 5) | Yes, exactly one (Section 7) |
| REPLY | The outcome of one DATA message (`ReplyMessage`) | The destination CLPR Service, when it processes a DATA message | No |
| CONTROL | Protocol management (`ControlMessage`) | The CLPR Service | No |
| REDACTED | **Deprecated.** Replaces the payload of a redacted DATA message (Section 10) | The sender's CLPR Service | Yes, with status REDACTED |

`DataMessage`:

| Field | Type | Meaning and constraints |
|---|---|---|
| `connector_id` | `bytes32` | The connector that authorized the message ([connector identity](connector-setup.md#1-connector-identity)). The destination resolves it to its own connector with the same id on the same channel. |
| `target_application` | `bytes` | The address of the destination application on the peer ledger. |
| `sender` | `bytes` | The address of the caller of `sendMessage` on the source ledger. Set by the source CLPR Service, never by the caller. |
| `message_data` | `bytes` | Opaque application data. Its length is limited by `max_message_payload_bytes` ([throttles](ledger-configuration.md#3-throttles)). |

`ReplyMessage`:

| Field | Type | Meaning and constraints |
|---|---|---|
| `message_id` | `uint64` | The id of the DATA message this REPLY answers, in the outbound queue of the ledger that sent the DATA message. |
| `status` | `ReplyStatus` | The outcome (Section 7). |
| `message_reply_data` | `bytes` | The application's response data. Empty when the status is CONNECTOR_NOT_FOUND, CONNECTOR_UNDERFUNDED or REDACTED. |

`ControlMessage` holds exactly one control message type. The only type in this version is `ConfigUpdate` ([configuration propagation](ledger-configuration.md#5-configuration-propagation)). A CONTROL message involves no connector, is not delivered to any application and is not answered. A receiver MUST reject a bundle that contains a CONTROL message with no control message type set or with an unknown type.

`RedactedMessage` (deprecated):

| Field | Type | Meaning and constraints |
|---|---|---|
| `message_hash` | `bytes32` | `SHA-256` of the payload bytes (Section 3) of the DATA message it replaces. |
| `sender` | `bytes` | Optional. The `sender` of the replaced DATA message. |

## 2. Message identifiers and queue

Each side of a channel has one **outbound queue**. Every message the side sends, of any type, is appended to it and receives a **message id**: a `uint64` that starts at 1 and increases by 1 with each message. DATA, REPLY and CONTROL messages share this one sequence. A message is identified by `(channel_id, message_id)`. Message ids of the two sides are independent.

A queue entry holds:

| Field | Type | Meaning |
|---|---|---|
| `payload` | `MessagePayload` | The message (Section 1). |
| `running_hash_after_processing` | `bytes32` | The running hash after this message (Section 4). |

Each side keeps these queue counters as part of the [shared channel state](channel-setup.md#6-shared-channel-state):

| Counter | Meaning | Initial value |
|---|---|---|
| `next_message_id` | The id the next outbound message will receive. | 1 |
| `sent_running_hash` | The running hash after the latest outbound message. | 32 zero bytes |
| `acked_message_id` | The highest outbound id the peer has acknowledged: the peer's proven `received_message_id` (Section 9). | 0 |
| `received_message_id` | The highest id of the peer's messages this side has received and processed. | 0 |
| `received_running_hash` | The running hash after the message `received_message_id`. | 32 zero bytes |

Messages are received in id order, with no gaps, and each message is processed exactly once ([bundle processing](channel-state-transitions.md#2-bundle-processing)).

## 3. Payload encoding

The **payload bytes** of a message are the encoding of its `MessagePayload` defined in [`schema/`](schema/README.md). The running hash (Section 4) is computed over these bytes, so the payload bytes stored in the sender's queue MUST reach the receiving CLPR Service unchanged. Endpoints and verifiers therefore copy them byte for byte; decoding and re-encoding can change them. The receiver hashes the bytes it receives and decodes them under [strict decoding](conventions.md#3-abstract-data-structures); a payload that fails to decode rejects the bundle. Because the encoding is not canonical, the open questions this raises are recorded as [OI-1](open-issues.md#oi-1-message-encoding-in-the-running-hash).

## 4. Running hash

Each outbound queue has a **running hash**: a hash chain over the payload bytes of its messages, in id order. With `p[k]` the payload bytes of message `k`:

```
h[0] := 32 zero bytes
h[k] := SHA-256(h[k − 1] ‖ SHA-256(p[k]))
```

`h[k]` is stored as `running_hash_after_processing` of message `k`. The sender's `sent_running_hash` is `h[k]` of its latest message `k`. The receiver recomputes the chain from its `received_running_hash` over each message it receives, and accepts the messages only if the result equals the proven running hash of the bundle's last message ([bundle processing](channel-state-transitions.md#2-bundle-processing)). Both sides MUST start the chain at 32 zero bytes.

## 5. Enqueue

An application sends a DATA message by calling `sendMessage` on its CLPR Service. Any caller can call it.

```
sendMessage(channel_id: bytes32, connector_id: bytes32,
            target_application: bytes, message_data: bytes) → message_id: uint64
```

The CLPR Service MUST reject the call, with no change to state, if any of the following holds:

| # | Condition |
|---|---|
| 1 | No channel `channel_id` exists, or its status is not ACTIVE ([channel status](channel-state-transitions.md#1-channel-status)). |
| 2 | No connector `connector_id` is registered on the channel. |
| 3 | The connector does not authorize the message ([authorization](connector-setup.md#4-authorization-of-outbound-messages)). |
| 4 | `len(message_data)` exceeds the peer's `max_message_payload_bytes` ([throttles](ledger-configuration.md#3-throttles)). |
| 5 | The outbound queue already holds the local `max_queue_depth` or more messages that the peer has not acknowledged (`next_message_id − 1 − acked_message_id`) ([throttles](ledger-configuration.md#3-throttles)). |

A CLPR Service MAY apply further limits, such as per-connector queue quotas ([Blueprint](../blueprint/channel-economics.md#3-queue-quotas)).

Otherwise the CLPR Service:

1. Enqueues a pending ConfigUpdate first, if one is due ([configuration propagation](ledger-configuration.md#5-configuration-propagation)).
2. Builds the DATA message with `connector_id`, `target_application`, `message_data`, and `sender` set to the caller's address.
3. Appends it to the outbound queue with id `next_message_id`, computes its running hash (Section 4), sets `sent_running_hash` to that hash and increments `next_message_id`.
4. Returns the message id. The application uses it to match the eventual REPLY.

The CLPR Service appends REPLY and CONTROL messages to the outbound queue in the same way (step 3).

## 6. Delivery to the application

When the destination CLPR Service processes a DATA message ([bundle processing](channel-state-transitions.md#2-bundle-processing)), it:

1. Resolves `connector_id` to the connector with that id on the channel. If none exists, the outcome is CONNECTOR_NOT_FOUND ([connectors on both ledgers](connector-setup.md#3-connectors-on-both-ledgers)).
2. Applies its charging policy to the connector ([Blueprint](../blueprint/channel-economics.md#1-execution-charges)). If the connector cannot pay, the outcome is CONNECTOR_UNDERFUNDED.
3. Otherwise invokes `target_application` with the channel id, `sender` and `message_data`, with an execution budget of at most the local `max_gas_per_message`. If the invocation succeeds, the outcome is SUCCESS and the application's return data becomes `message_reply_data`. If the target is not an application, or the invocation fails, the outcome is APPLICATION_ERROR.

When the source CLPR Service processes a REPLY, it delivers `message_id`, `status` and `message_reply_data` to the application that sent the DATA message (its `sender`). Delivery is best effort: a failure of the application, or a `sender` that cannot be invoked, does not affect processing of the REPLY.

The callback interface, return convention and budget mechanics are defined by each ledger ([EVM](../ledgers/evm/README.md#3-application-and-connector-interfaces), [Hiero](../ledgers/hiero/README.md#6-application-and-connector-interfaces)). Data from another ledger is untrusted input to the application ([Blueprint §6.5](../blueprint/clpr-service.md#65-application-payloads)).

## 7. Replies

Every DATA message receives **exactly one REPLY**. The destination CLPR Service MUST enqueue the REPLY for a DATA message while processing the bundle that delivers that DATA message, before it processes the next message.

`ReplyStatus`:

| Status | Meaning |
|---|---|
| SUCCESS | The application processed the message. |
| APPLICATION_ERROR | The application failed, or the target is not an application. The connector is not at fault. |
| CONNECTOR_NOT_FOUND | No connector with the message's `connector_id` exists on the channel at the destination. |
| CONNECTOR_UNDERFUNDED | The destination connector could not pay for execution. |
| REDACTED | **Deprecated.** Answers a REDACTED message (Section 10). |
| CHANNEL_CLOSED | **Deprecated.** SHOULD NOT be produced. A receiver MUST accept it. |

The encoding reserves one further status value ([schema](schema/clpr_message.proto)). A CLPR Service MUST NOT produce it. A receiver MAY accept a REPLY that carries it, with no penalty to the connector, instead of rejecting the bundle under strict decoding.

On receiving a REPLY, the source CLPR Service applies its charging and slashing policy according to the status ([Blueprint](../blueprint/stakes-and-bonds.md#2-slashing-and-bans)). CONNECTOR_NOT_FOUND and CONNECTOR_UNDERFUNDED are attributable to the source connector; the other statuses are not.

## 8. Response ordering

Because each side processes the peer's messages in id order and answers each DATA message as it processes it, REPLY messages arrive in the order of the DATA messages they answer.

The source CLPR Service MUST check every REPLY it receives: its `message_id` MUST be the id of the **oldest unanswered DATA message** in its outbound queue. The walk over the outbound queue skips REPLY and CONTROL messages; a DATA message whose payload was replaced by a REDACTED message is still a DATA message. The first REPLY on a channel answers the first DATA message, which need not have id 1, because a CONTROL message can precede it.

A REPLY that does not match is a **response ordering violation**. It shows that the peer's outbound queue is inconsistent. Its handling is defined in [pause and resume](channel-state-transitions.md#6-pause-and-resume).

A receiver MAY also treat as a response ordering violation a bundle after which it has received the peer's latest message while a DATA message the peer has acknowledged is still unanswered. The peer's latest message has been received when `last_message_id`, or the receiver's `received_message_id` if the bundle has no messages, equals `metadata.next_message_id − 1` ([partial bundles](bundle.md#3-partial-bundles)).

## 9. Acknowledgement

`acked_message_id` is the highest id of this side's outbound messages that the peer has acknowledged. It advances only from proven queue metadata: on each accepted bundle,

```
acked_message_id := metadata.received_message_id
```

subject to the checks in [bundle processing](channel-state-transitions.md#2-bundle-processing).

When `acked_message_id` advances, the CLPR Service deletes the acknowledged REPLY and CONTROL messages from its outbound queue; they require nothing further. It keeps acknowledged DATA messages until their REPLY arrives, because response ordering (Section 8) is checked against them. A DATA message is deleted when its REPLY is processed.

## 10. Redaction (deprecated)

Redaction is **deprecated**. A CLPR Service SHOULD NOT redact messages.

Redaction replaces the payload of a DATA message that the peer has not yet acknowledged with a `RedactedMessage` whose `message_hash` is `SHA-256` of the original payload bytes. The queue entry keeps its id and its `running_hash_after_processing`.

A receiver that accepts a REDACTED message uses its `message_hash` in place of `SHA-256(p[k])` when it computes the running hash (Section 4). It does not deliver the message to any application; it answers it with a REPLY whose status is REDACTED. A receiver MAY instead reject a bundle that contains a REDACTED message. A receiver MUST accept a REPLY with status REDACTED; it carries no penalty.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
