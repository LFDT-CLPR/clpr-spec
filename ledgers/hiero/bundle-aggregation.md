# Hiero Bundle Aggregation

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

This document defines how a Hiero CLPR Endpoint selects the content of a bundle for one channel during an [endpoint sync exchange](../../protocol/endpoint-sync.md#3-exchange). The selected content is encoded and proven by the proof scheme chosen for the channel ([Hiero §4](ledger.md#4-proof-schemes)): [`hints-wraps`](proof-schemes/hints-wraps.md) or [`hints`](proof-schemes/hints.md).

## 1. Inputs

| Input | Source |
|---|---|
| Peer's bundle request | The `BundleRequest` received from the peer in this exchange, if any: `current_received_message_id`, `current_status`, `current_trust_anchor_id`, `current_endpoint_manifest_version`. `current_trust_anchor_id` selects the proof scheme ([Hiero §4](ledger.md#4-proof-schemes)); for `hints` it also identifies the key from which a provenance chain starts ([`hints` §7](proof-schemes/hints.md#7-trust-anchor-changes)). |
| Peer's throttles | The peer's `max_messages_per_bundle` and `max_sync_bytes`, from the peer [configuration](../../protocol/ledger-configuration.md#3-throttles) stored with the channel |
| Local channel | The channel's `next_message_id`, `acked_message_id` and status |
| Local endpoint manifest version | The version of this ledger's [endpoint manifest](../../protocol/endpoint-manifest.md#3-local-manifest) |
| Peer's observed manifest version | The `endpoint_manifest_version` in the last bundle verified from the peer on this channel; used only when no request was received |
| Role | Initiator or responder of the exchange ([roles](../../protocol/endpoint-sync.md#1-purpose-and-roles)) |

The bundle request is unproven. It only shapes the bundle.

## 2. State read and finality

The CLPR Endpoint MUST read all bundle content from one **signed snapshot**: the state of the ledger at the start of a block whose root is signed directly by the ledger's threshold signature. It reads every proven item, and builds every path, from that one snapshot. It SHOULD use the latest signed snapshot.

- Only directly signed blocks yield a snapshot. A block that is final only because a later block was signed does not.
- The proven state is the block's **starting state**, not its ending state.
- A signed block is final: the proven state cannot be reverted.

If no snapshot exists, or the channel is not present in it, no bundle is built.

## 3. Message range and limits

The run of messages starts at `start`:

```
if a bundle request was received
   and request.current_received_message_id < channel.next_message_id then
    start := request.current_received_message_id + 1
else
    start := channel.acked_message_id + 1
```

The endpoint then adds messages `start, start + 1, …` in order, while all of the following hold. The run MUST be contiguous and MUST start at `start`.

1. Fewer than the peer's `max_messages_per_bundle` messages have been added.
2. The message id exists in the snapshot's queue for the channel. The run stops at the first missing id.
3. The encoded bundle, including this message, is at most the peer's `max_sync_bytes − 114` bytes. The 114 bytes are a fixed safety margin.
4. For a channel that uses the `hints` scheme, the bundle's state proof stays within the [limits](proof-schemes/hints.md#45-limits) of that scheme.

The first message that fails a condition, and every later one, is left for a later exchange. The encoded bundle MUST NOT exceed the peer's `max_sync_bytes`. If even the message at `start` does not fit within the size limit, the bundle carries no messages.

A requestor that misreports `current_received_message_id` is handled as in [Endpoint sync §4](../../protocol/endpoint-sync.md#4-message-range).

## 4. Manifest inclusion

The bundle includes this ledger's endpoint manifest if the peer's view of it is older than the local manifest:

```
if a bundle request was received then
    peer_version := request.current_endpoint_manifest_version
else
    peer_version := the peer's observed manifest version
include_manifest := local_manifest.version > peer_version
```

The manifest is the one in the snapshot. The endpoint MUST include it when `include_manifest` is true, except in a witness-form bundle of the `hints` scheme ([Endpoint sync §5.2](../../protocol/endpoint-sync.md#52-endpoint-manifest)).

## 5. When nothing is sent

The endpoint MUST NOT send a bundle on the channel in this exchange when either of the first two conditions below holds, and SHOULD NOT send one when the third holds:

| Condition | Applies to |
|---|---|
| No signed snapshot exists, or the channel is not in it | Both roles |
| The peer's request reports status CLOSED | Both roles |
| The bundle would carry no messages, no manifest and no trust anchor change, and the local channel is neither CLOSING nor DRAINED | Initiator |

A responder otherwise SHOULD send a bundle, even one with no messages. Such a bundle carries the channel's proven state, which acknowledges the peer's messages. An initiator whose channel is CLOSING or DRAINED SHOULD send a bundle, even with no messages, so the peer learns the proven status.

## 6. Producing `hints` bundles

For a channel that uses the [`hints`](proof-schemes/hints.md) scheme, the endpoint builds the bundle as follows:

- **Digest.** If the ledger's block digest is not SHA-256, no `hints` bundle is produced.
- **Rotation.** When the snapshot's signing key differs from the peer's anchor key, the bundle carries a provenance chain from the anchor key to the signing key, of 1 to 8 links.
- **Witness.** When the state-form bundle cannot be sent, because the chain needs more than 8 links or the bundle would exceed the peer's `max_sync_bytes` or the scheme's [limits](proof-schemes/hints.md#45-limits), the endpoint sends a witness-form bundle if it has a witness for a key 1 to 8 links from the anchor key, and nothing otherwise. The witness-form bundle advances the peer's anchor to that key; the state-form bundle follows in a later exchange.
- **Self-check.** The endpoint SHOULD verify each bundle locally against the peer's trust anchor before sending it.
