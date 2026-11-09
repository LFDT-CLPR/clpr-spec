# Endpoint Sync

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

## 1. Purpose and roles

Endpoint sync is the protocol that CLPR Endpoints on two ledgers use to exchange bundles for a channel. It is the one concrete wire protocol of CLPR. Its messages are defined in [`schema/`](schema/README.md).

A **sync cycle** is one exchange between two endpoints, for one channel, in which each side can send the other one bundle. Each cycle has two roles:

| Role | Description |
|---|---|
| Initiator | Opens the stream to an endpoint chosen from the channel's peer manifest ([endpoint discovery](../endpoint-manifest.md#6-endpoint-discovery)). |
| Responder | Accepts the stream. |

Apart from who opens the stream, the two sides do the same things. Each side reports its own channel state in a `BundleRequest`, and answers the other side's request with a bundle built from its own ledger's state. In what follows, the **requestor** is the side whose `BundleRequest` is being answered, and the **sender** is the side that builds and sends the bundle. Each side is the requestor for one bundle and the sender for the other.

A side that receives a bundle submits it to the CLPR Service on its own ledger ([bundle submission](../../blueprint/clpr-service.md#5-bundle-submission)). The bundle takes effect only if the channel's verifier contract and [bundle processing](../channel-state-transitions.md#2-bundle-processing) accept it.

## 2. Transport

Every CLPR Endpoint that advertises a network address in its [endpoint](../endpoint-manifest.md#1-endpoint) entry MUST serve the method `sync` of the gRPC service `ClprEndpointService` ([§7](#7-schema)), at the full method name below, on that address and port. An endpoint that advertises no address only initiates. This service is separate from the ledger's transaction API.

| Item | Value |
|---|---|
| Service | `proto.ClprEndpointService` |
| Method | `sync`, bidirectional streaming |
| Full method name | `/proto.ClprEndpointService/sync` |
| Message, both directions | `ClprSyncPayload` |

- Every initiator MUST call `sync` at that full method name.
- An endpoint MAY expose other RPCs, on the same port or on other ports. They are not part of the protocol.
- An endpoint MUST configure its gRPC maximum message size so that it accepts a `ClprSyncPayload` whose `bundle_payload` is as large as its own ledger's `max_sync_bytes` ([throttles](../ledger-configuration.md#3-throttles)). The limit therefore exceeds `max_sync_bytes` by the size of the rest of the message: `channel_id`, a `BundleRequest`, and the protobuf field overhead.

**Transport security:**

- The server SHOULD serve TLS on the advertised port with a certificate that chains to a publicly trusted root. It MAY also accept plaintext on the same port. It MUST NOT request or require a client certificate.
- A client MUST attempt TLS first. It MAY fall back to plaintext if the TLS handshake fails. It MAY skip validation of the server's certificate chain and of the host name or IP address.
- No endpoint identity is derived from the transport. The integrity and authenticity of a bundle rest on its proof. A `BundleRequest` is an unproven hint.

## 3. Exchange

### 3.1 Messages

Every message on the stream is a `ClprSyncPayload`:

| Field | Meaning |
|---|---|
| `channel_id` | The channel the stream belongs to. |
| `bundle_request` | The sending side's `BundleRequest`. Optional. |
| `bundle_response` | A `BundleResponse` for the other side. Optional. |

`BundleRequest` describes the requestor's own state for the channel:

| Field | Meaning |
|---|---|
| `current_received_message_id` | The requestor's `received_message_id` ([shared channel state](../channel-setup.md#6-shared-channel-state)). The sender's message range starts after it ([§4](#4-message-range)). |
| `current_status` | The requestor's channel status ([channel status](../channel-state-transitions.md#1-channel-status)). |
| `current_trust_anchor_id` | The identifier of the trust anchor that the requestor's ledger stores for the channel ([trust anchors](../verifier-interface.md#1-verifier-contracts-and-trust-anchors), [§5.1](#51-trust-anchor-catch-up)). Its format is defined by the sender's proof scheme. |
| `current_endpoint_manifest_version` | The version of the sender's endpoint manifest that the requestor's ledger holds ([§5.2](#52-endpoint-manifest)). |

`BundleResponse` carries one bundle:

| Field | Meaning |
|---|---|
| `bundle_payload` | The bundle, in the wire layout of the sender's proof scheme ([Ledger Specifications](../../ledgers/README.md)). Opaque to endpoint sync. |

A `BundleRequest` is unproven. It only shapes the bundle that the sender builds, and it MUST NOT cause a state change on either ledger. The receiving ledger's [verifyBundle](../verifier-interface.md#3-verifybundle) and [bundle processing](../channel-state-transitions.md#2-bundle-processing) remain the only authorities on channel state.

### 3.2 Rules

- `channel_id` MUST be exactly 32 bytes, MUST be set on every message, and MUST be the same on every message of a stream. A side MUST NOT act on a message that breaks this rule, and MAY end the stream.
- In a cycle that proceeds, each side's first message (steps 1 and 2 of [§3.3](#33-sequence)) MUST carry its `BundleRequest`. Later messages MUST NOT carry one.
- A message with both `bundle_request` and `bundle_response` absent is a **terminal message**. It means that its sender has nothing further to send in this cycle.
- A `bundle_response` with an empty `bundle_payload` means no bundle, the same as an absent `bundle_response`.
- Each side MUST send at most one bundle per cycle.
- A responder that has no record of the channel, or whose channel is PENDING, MUST NOT send a bundle. It ends the stream, with a terminal message or a gRPC error status.
- A responder whose channel is CLOSED MAY send a bundle. Such a bundle reports CLOSED and lets a DRAINED peer reach CLOSED ([closing and draining](../channel-state-transitions.md#5-closing-and-draining)).

### 3.3 Sequence

| Step | From | Fields present | Content |
|---|---|---|---|
| 1 | Initiator | `channel_id`, `bundle_request` | The initiator's request. |
| 2 | Responder | `channel_id`, `bundle_request`, `bundle_response` if any | The responder's request, and the responder's bundle built for the request of step 1. |
| 3 | Initiator | `channel_id`, `bundle_response` if any | The initiator's bundle built for the request of step 2. A terminal message if there is no bundle. |
| 4 | Responder | `channel_id` | A terminal message. The cycle is complete. |

- If step 1 is a terminal message, the responder ends the stream without a reply.
- After step 3 the initiator closes its sending direction. If step 3 is a terminal message, the responder MAY end the stream without sending step 4.
- The underlying connection and TLS session MAY persist across cycles. Each cycle uses a new stream.

Submission is not part of the exchange. The stream does not wait for, or report, the result of submitting a bundle. A sender learns that its bundle was accepted from the requestor's next `BundleRequest`.

## 4. Message range

A bundle carries a **run**: a contiguous sequence of messages from the sender's outbound queue for the channel. The run is chosen as follows. `next_message_id` and `acked_message_id` are the sender's own values for the channel.

- The run MUST start at `current_received_message_id + 1`, using the requestor's `BundleRequest`.
- The run MUST NOT extend past `next_message_id − 1`.
- The run MUST respect the requestor's ledger throttles: at most `max_messages_per_bundle` messages, and a `bundle_payload` no larger than `max_sync_bytes` ([throttles](../ledger-configuration.md#3-throttles)).
- The run MAY end before `next_message_id − 1`. Such a bundle is a [partial bundle](../bundle.md#3-partial-bundles).
- If `current_received_message_id ≥ next_message_id`, the requestor claims messages the sender has not enqueued. The sender MAY then either start the run at `acked_message_id + 1` or send no messages.
- If `current_received_message_id = next_message_id − 1`, the run is empty. A bundle without messages can still make progress ([progress](../channel-state-transitions.md#3-progress)).

Because the request is unproven, a requestor that overstates `current_received_message_id` receives a bundle that its own ledger rejects for a gap. A requestor that reports a `current_received_message_id` below the sender's `acked_message_id` receives a bundle that its own verifier rejects ([partial bundles](../bundle.md#3-partial-bundles)).

## 5. Endpoint obligations

These obligations apply to CLPR Endpoints. A CLPR Service enforces only what the verifier contract returns.

### 5.1 Trust anchor catch-up

A **transition bundle** is a bundle that makes a [trust anchor change](../verifier-interface.md#4-trust-anchor-changes) for the requestor: it changes the trust anchor id. Any other bundle is a **normal bundle**.

1. The sender MUST NOT send a bundle that does not verify under the trust anchor identified by `current_trust_anchor_id`. If it can produce no such bundle, it sends none.
2. If no normal bundle verifies under that trust anchor because the trust anchor is behind the sender's ledger, the sender MUST send a transition bundle instead.
3. If the requestor's trust anchor is several changes behind, the sender sends transition bundles in order. Each one verifies under the trust anchor that the previous one installed. A proof scheme MAY carry several changes in one bundle. Catch-up takes one cycle per transition bundle; normal bundles resume once the requestor's trust anchor is current enough.

When a trust anchor changes, and how its identifier is formed, is defined by each proof scheme.

### 5.2 Endpoint manifest

If a request's `current_endpoint_manifest_version` is lower than the version of the sender's local endpoint manifest, the sender MUST include a [manifest proof](../endpoint-manifest.md#5-manifest-proofs) in any bundle it sends in reply to that request. It MAY send a bundle for this purpose alone.

### 5.3 Channel status

- A sender MUST NOT send a bundle to a requestor that reports CLOSED.
- An endpoint MUST NOT initiate a sync cycle for a channel that is PENDING or CLOSED on its own ledger.

There is no close notification: an endpoint does not initiate a cycle to report that its channel became CLOSED. A DRAINED peer learns of it from a bundle that a CLOSED responder sends in answer to the peer's request ([§3.2](#32-rules)). [Closing and draining](../channel-state-transitions.md#5-closing-and-draining) defines how each ledger reaches CLOSED.

## 6. Misbehavior

Misbehavior detection and enforcement are strictly local. Each endpoint detects and responds to misbehavior that it observes. There is no cross-ledger misbehavior reporting.

An endpoint MAY end a stream, and MAY stop or reduce syncing with a peer endpoint, when the peer:

- sends messages that break [§3.2](#32-rules) or exceed the gRPC message size limit;
- sends bundles that its ledger rejects; or
- keeps a stream open without completing the sequence of [§3.3](#33-sequence).

A ledger's rejection of a bundle MAY count toward such local thresholds.

## 7. Schema

[`schema/clpr_endpoint_sync.proto`](schema/clpr_endpoint_sync.proto) defines the service `ClprEndpointService` and the messages `ClprSyncPayload`, `BundleRequest` and `BundleResponse`. It imports `ClprChannelStatus` from the [Protocol schema](../schema/README.md). [`schema/README.md`](schema/README.md) describes the file.

The package name `proto`, the service name `ClprEndpointService` and the method name `sync` are wire-visible, because they form the full method name ([§2](#2-transport)). Message and enum names are not wire-visible; implementations MAY use other names.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
