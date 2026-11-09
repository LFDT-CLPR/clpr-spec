# Besu Bundle Aggregation

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

This document defines how a Besu CLPR Endpoint gathers the [abstract bundle content](../../protocol/bundle.md#1-bundle-content) for one channel in answer to a peer's request. The proof scheme then proves and encodes it ([qbft-epoch](proof-schemes/qbft-epoch.md#5-encoding-algorithm)). Storage positions are those of the [proven storage layout](README.md#3-proven-storage-layout).

## 1. Inputs

The endpoint builds a bundle for channel `channelId` from the peer's `BundleRequest` ([Endpoint sync §3](../../protocol/endpoint-sync/README.md#3-exchange)). The peer fills it from its own record of the channel.

| Field | Meaning | Used for |
|---|---|---|
| `current_received_message_id` | The last message id the peer has received | Start of the message range |
| `current_status` | The peer's channel status | Skipping a closed peer |
| `current_trust_anchor_id` | The id of the trust anchor the peer holds for this ledger | Trust anchor catch-up, defined by the proof scheme |
| `current_endpoint_manifest_version` | The version of this ledger's endpoint manifest the peer holds | Manifest inclusion |

The endpoint also uses the peer's throttles held in the local channel record ([Ledger configuration §3](../../protocol/ledger-configuration.md#3-throttles)).

## 2. State read and finality

The endpoint reads the head block `H` at the `latest` block tag. QBFT blocks are final when sealed, so `H` is final. Every value of the bundle MUST be read at `H`: the channel record, the messages, the endpoint manifest and all proofs.

## 3. Message range and limits

```
c := the channel record at H
from := max(1, request.current_received_message_id + 1)
to   := c.next_message_id − 1
messages := the stored messages from, from + 1, …, to       // empty if from > to
n := min(len(messages), peer.max_messages_per_bundle)
messages := the first n of messages
```

- Each payload is the exact bytes stored in the message queue; the endpoint MUST NOT re-encode it.
- The endpoint MAY shorten the range from the end, to apply a lower local limit or a limit of the proof scheme.
- With the qbft-epoch scheme, when the bundle carries more than one epoch boundary header (`k > 1` in [qbft-epoch §5](proof-schemes/qbft-epoch.md#5-encoding-algorithm)), the endpoint SHOULD select no messages.
- If the encoded bundle would exceed the peer's `max_sync_bytes`, the endpoint shortens the range or sends nothing.

The range rules, including those for a requestor that misreports `current_received_message_id`, are in [Endpoint sync §4](../../protocol/endpoint-sync/README.md#4-message-range).

The queue metadata is the channel record's fields at `H` ([Bundle §2](../../protocol/bundle.md#2-queue-metadata)). When messages are included, the last message id and running hash are those of the last message selected.

## 4. Manifest inclusion

The endpoint includes the local endpoint manifest, read at `H`, if and only if:
- its version is greater than `request.current_endpoint_manifest_version`, and
- its service address is non-empty.

## 5. When nothing is sent

The endpoint MUST send an empty bundle payload when:
- `request.current_status` is CLOSED, or
- the channel has no record at `H`, or its status is PENDING.

It SHOULD send an empty bundle payload when the bundle would convey nothing, that is, when all of these hold:
- no messages are selected;
- the bundle carries no epoch boundary headers and no other material for a [trust anchor change](../../protocol/verifier-interface.md#4-trust-anchor-changes);
- no endpoint manifest is included ([§4](#4-manifest-inclusion));
- the local `received_message_id` is 0, so there is no acknowledgement to convey;
- the local status is neither CLOSING nor DRAINED.

It also sends an empty payload when it cannot assemble the proofs, and in the cases its proof scheme defines.
