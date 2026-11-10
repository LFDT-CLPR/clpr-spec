# Bundle

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

A **bundle** carries proven state of one side of a channel, the **source**, to the CLPR Service of the other side, the **destination**. This module defines the abstract content of a bundle and what a proof scheme proves about it (Section 4). The bundle's wire layout and proof material are defined by the source ledger's proof scheme; its delivery between endpoints by [endpoint sync](endpoint-sync/README.md); its processing by [channel state transitions](channel-state-transitions.md#2-bundle-processing).

## 1. Bundle content

The CLPR Service treats a bundle as opaque bytes. The channel's verifier contract decodes and verifies it ([verifier interface](verifier-interface.md#3-verifybundle)) and returns its **abstract bundle content**:

| Item | Type | Meaning |
|---|---|---|
| `metadata` | `QueueMetadata` | The source's proven queue state (Section 2). Every bundle MUST carry it. |
| `messages` | `bytes[]` | The payload bytes ([payload encoding](messaging.md#3-payload-encoding)) of a contiguous run of the source's outbound queue, in id order. Can be empty. |
| `last_message_id` | `uint64` | The id of the last message in `messages`, taken from its proven queue entry. 0 when `messages` is empty. |
| `last_message_running_hash` | `bytes32` | That entry's `running_hash_after_processing`. Not used when `messages` is empty. |
| `new_endpoint_manifest` | `optional EndpointManifest` | The source CLPR Service's current [endpoint manifest](endpoint-manifest.md#2-endpoint-manifest), when the bundle proves it. |
| `new_trust_anchor` | `bytes` | Empty when the stored trust anchor stays unchanged. A non-empty value replaces the stored trust anchor ([trust anchor changes](verifier-interface.md#4-trust-anchor-changes)). |
| `new_trust_anchor_id` | `bytes` | The identifier of `new_trust_anchor`. Empty if and only if `new_trust_anchor` is empty ([trust anchor changes](verifier-interface.md#4-trust-anchor-changes)). |

The messages carry the ids `last_message_id − len(messages) + 1` to `last_message_id`.

A bundle with no messages is valid. It can carry only an acknowledgement, a status change, a manifest or a trust anchor change, as long as it makes progress ([progress](channel-state-transitions.md#3-progress)).

## 2. Queue metadata

`QueueMetadata` is the source's channel state, as proven at the state the bundle's proof refers to. Every field that a verifier returns MUST come from that proven state.

| Field | Type | Meaning |
|---|---|---|
| `next_message_id` | `uint64` | The source's `next_message_id`: one more than the id of its latest outbound message. |
| `sent_running_hash` | `bytes32` | The source's `sent_running_hash`: the running hash after its latest outbound message. |
| `received_message_id` | `uint64` | The highest id of the destination's messages that the source has received and processed. The destination takes it as its acknowledgement ([acknowledgement](messaging.md#9-acknowledgement)). |
| `received_running_hash` | `bytes32` | The source's running hash over the messages it has received. Informational. |
| `status` | `ChannelStatus` | The source's channel status ([channel status](channel-state-transitions.md#1-channel-status)). |
| `endpoint_manifest_version` | `uint64` | The version of the destination's manifest that the source holds ([peer manifest](endpoint-manifest.md#4-peer-manifest)). Informational. A verifier need not return it. |

Informational fields MUST NOT cause a change of state at the destination. They inform the destination's endpoints.

The id of the trust anchor that the source holds for the destination is informational. It has no field in the queue metadata above, but the wire encoding keeps it as field 6 of `ClprQueueMetadata` ([schema](schema/clpr_bundle_content.proto)). Endpoints report it, unproven, in their sync requests ([exchange](endpoint-sync/README.md#31-messages)). A proof scheme MAY prove it. A verifier need not return it, and like the other informational fields it does not change state at the destination.

The queue counters these fields report are defined in [messaging](messaging.md#2-message-identifiers-and-queue).

## 3. Partial bundles

A bundle need not carry every message the source has not yet delivered. Its run of messages MAY end before the source's latest message, so `metadata.next_message_id` and `metadata.sent_running_hash` can run ahead of the bundle's messages:

- `last_message_id` and `last_message_running_hash` identify the end of the run. They come from the proven queue entry of the last message, not from `metadata`.
- `last_message_id < metadata.next_message_id` always holds.
- When `last_message_id = metadata.next_message_id − 1`, the bundle reaches the source's latest message, and `last_message_running_hash = metadata.sent_running_hash`.

The run is bounded by the destination's `max_messages_per_bundle` and `max_sync_bytes` ([throttles](ledger-configuration.md#3-throttles)). Where the run starts is defined in [message range](endpoint-sync/README.md#4-message-range). Two different lower bounds apply to its start:

- **Source side.** The first message has an id greater than the source's proven `acked_message_id`. A verifier rejects a bundle that breaks this bound ([verifyBundle](verifier-interface.md#3-verifybundle)).
- **Destination side.** The run can start with messages whose ids are at most the destination's `received_message_id`. The destination accepts such a bundle and skips those messages ([bundle processing](channel-state-transitions.md#2-bundle-processing) Step 6).

## 4. Proof requirements

A proof scheme defines how the abstract bundle content is proven ([CLIP-0001 §3.3](../clips/clip-0001.md#33-ledger-specifications)). Every proof scheme MUST prove, under the trust anchor the destination stores for the channel:

1. **Channel state:** the source channel state from which `metadata` and the source's `acked_message_id` are taken, for the channel `ctx.channel_id` of the [channel context](channel-setup.md#3-channel-context), and for the CLPR Service `ctx.service_address` where the source ledger can host more than one CLPR Service.
2. **Last message:** when `messages` is non-empty, the queue entry of `last_message_id` on the same channel: its id and its `running_hash_after_processing`.
3. **Endpoint manifest:** when present, the source CLPR Service's endpoint manifest, bound to `ctx.service_address` ([manifest proofs](endpoint-manifest.md#5-manifest-proofs)).
4. **Trust anchor change:** when the bundle makes a trust anchor change, a commitment to the new trust anchor, proven under the current trust anchor ([trust anchor changes](verifier-interface.md#4-trust-anchor-changes)).

Items 1 to 3 MUST be proven from one state of the source ledger.

The commitment level at which a verifier accepts that state is the verifier's choice. It can be final, safe, or an earlier and faster level, so channels with different latency and risk can connect the same ledgers. A verifier SHOULD accept only final or safe state. A channel whose verifier accepts state earlier than safe does so at its users' own risk: the proven state can be reverted after its messages are delivered.

A verifier MUST verify items 1 to 4 as they apply. The messages before the last one are bound by the running hash: the destination recomputes the chain over them and compares it with the proven `last_message_running_hash` ([running hash](messaging.md#4-running-hash)). A proof scheme MAY therefore omit individual proofs for them. If a scheme includes such proofs, a verifier MAY check them.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
