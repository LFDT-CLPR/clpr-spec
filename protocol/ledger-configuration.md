# Ledger Configuration

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

Every ledger that runs a CLPR Service publishes a **ledger configuration**: its identity, the address of its CLPR Service, the limits it imposes on peers, and the material a verifier needs to start trusting it. This module defines that configuration and how changes to it reach the ledger's peers. Encodings are in [`schema/`](schema/README.md).

## 1. Ledger identity

A ledger is identified by a **chain id**: a CAIP-2 identifier of the form `namespace:reference` ([conventions](conventions.md#5-identifiers)), for example `hiero:mainnet` or `eip155:1`.

- Public networks SHOULD use a registered CAIP-2 namespace. Private networks MAY assign their own chain id.
- The chain id is not unique to one CLPR Service. A peer CLPR Service is identified by the pair (chain id, service address), where the service address is the `service_address` of its configuration (Section 2).
- The chain id is self-asserted. Any ledger can publish any chain id, and the Protocol does not authenticate it. Trust in a peer comes from the channel's verifier contract and trust anchor, not from the chain id ([overview](../clpr-overview.md#4-trust-model)).

## 2. Ledger configuration

`LedgerConfiguration` is the configuration a CLPR Service publishes. A ledger has exactly one current configuration.

| Field | Type | Meaning and constraints |
|---|---|---|
| `protocol_version` | `uint32` | The protocol version the CLPR Service implements (Section 4). |
| `chain_id` | `string` | The ledger's chain id (Section 1). |
| `service_address` | `bytes` | The on-ledger address of this ledger's CLPR Service: a contract address on EVM ledgers, a constant defined by the ledger on others ([Hiero](../ledgers/hiero/README.md#1-ledger-identity)). `verifyConfig` returns it so that the peer can build the [channel context](channel-setup.md#3-channel-context). |
| `timestamp` | `timestamp` | The consensus timestamp of the transaction that last changed the configuration. It strictly increases with every change. Its valid range is defined in [`schema/`](schema/clpr_ledger_configuration.proto). |
| `throttles` | `Throttles` | The limits this ledger imposes (Section 3). Required. |
| `endpoints` | `Endpoint[]` | **Deprecated.** Receivers MUST ignore it, whether or not it is populated. The endpoint set is the [endpoint manifest](endpoint-manifest.md). |
| `initial_trust_anchor` | `bytes` | The trust anchor with which a verifier starts trusting this ledger. A ledger whose proof schemes take the initial trust anchor from the configuration MUST populate it (for example [Hiero](../ledgers/hiero/proof-schemes/hints-wraps.md#9-configuration-and-manifest-proofs), where it is the ledger id). It is empty when the proof schemes derive the initial trust anchor from other proof material in the configuration proof. See [verifier interface](verifier-interface.md#2-verifyconfig). |
| `initial_trust_anchor_id` | `bytes` | An opaque identifier of `initial_trust_anchor`, in a format defined by the proof scheme. It MUST be non-empty if and only if `initial_trust_anchor` is non-empty. |

A ledger's configuration is changed only by its own CLPR Service administration ([Blueprint](../blueprint/clpr-service.md#2-administration)). Each change sets `timestamp` to the consensus time of the changing transaction.

## 3. Throttles

`Throttles` are the limits a ledger publishes in its configuration. They are ledger-wide: the same values apply to every peer and every channel, and each channel enforces them independently. The last column of the table below states which side applies each limit, and with which ledger's value. A receiving ledger checks its own limits during [bundle processing](channel-state-transitions.md#2-bundle-processing); it MAY also count a violation as misbehavior ([endpoint sync](endpoint-sync/README.md#6-misbehavior)).

Each ledger keeps, per channel, a copy of the **peer throttles**: set from `verifyConfig` at [channel setup](channel-setup.md#5-initial-peer-state) and replaced by each accepted ConfigUpdate (Section 5).

| Field | Type | Meaning | Which value applies |
|---|---|---|---|
| `max_messages_per_bundle` | `uint32` | Maximum number of messages in one bundle. | The sending endpoint MUST NOT exceed the peer's value. The receiving CLPR Service MUST reject a bundle that exceeds its own value. |
| `max_message_payload_bytes` | `uint32` | Maximum length of the `message_data` of a DATA message. It does not apply to other message types. | The source CLPR Service MUST reject, at enqueue, a message that exceeds the peer's value ([enqueue](messaging.md#5-enqueue)). The destination CLPR Service MUST reject a bundle containing a DATA message that exceeds its own value. |
| `max_gas_per_message` | `uint64` | Maximum gas, or equivalent execution budget, allocated to processing one message. | Each CLPR Service MUST apply its own value to the messages it processes. |
| `max_queue_depth` | `uint32` | Maximum number of messages in a channel's outbound queue that the peer has not acknowledged. When the queue is full, new messages are rejected. | Each CLPR Service MUST apply its own value to its own outbound queues ([enqueue](messaging.md#5-enqueue)). |
| `max_sync_bytes` | `uint64` | Maximum length of a bundle's proof bytes (the `bundle_payload` submitted to the CLPR Service). The endpoint sync envelope is not counted. | The sending endpoint MUST NOT exceed the peer's value. The receiving CLPR Service MUST reject a larger bundle. A receiving endpoint MAY discard a larger bundle without submitting it. |
| `max_local_endpoints` | `uint32` | Maximum number of endpoints in this ledger's [local manifest](endpoint-manifest.md#3-local-manifest). 0 means no limit. | Own value only. |
| `max_peer_endpoints` | `uint32` | Maximum number of endpoints this ledger keeps in a channel's [peer manifest](endpoint-manifest.md#4-peer-manifest). 0 means no limit. | Own value only. |

Constraints on a ledger's own configuration:

- `max_messages_per_bundle`, `max_message_payload_bytes`, `max_gas_per_message`, `max_queue_depth` and `max_sync_bytes` MUST be greater than zero.
- `max_sync_bytes` MUST be greater than `max_message_payload_bytes` plus the overhead of delivering one message: proof material, queue metadata and message framing. Otherwise a message of the maximum size can never be delivered and the channel stops. The overhead depends on the proof scheme.

Limits are published so that a peer is never penalized for a reason it cannot determine from the published configuration.

Default values are deployment choices ([Blueprint](../blueprint/clpr-service.md#4-configuration-parameters)).

## 4. Protocol version

The protocol version is a non-negative integer. It increases with every change to the Protocol that breaks interoperability. A CLPR Service implementing this version of the specification MUST set `protocol_version` to **1**.

- Both sides of a channel MUST use the same protocol version. Messaging between different protocol versions is not supported.
- A CLPR Service MUST reject a ConfigUpdate whose `configuration.protocol_version` differs from its own (Section 5.3).
- `verifyConfig` does not return the peer's protocol version, so channel setup does not check it ([OI-7](open-issues.md#oi-7-protocol-version-at-channel-setup)).
- A new CONTROL message type is introduced only with a new protocol version ([message types](messaging.md#1-message-types)).

A ledger that changes its protocol version propagates the new configuration to its peers (Section 5). A peer on a different version rejects the bundle that carries it, so messaging on that channel stops.

## 5. Configuration propagation

After a channel is set up, changes to a ledger's configuration reach the peer through the channel's own message queue, as a CONTROL message.

### 5.1 ConfigUpdate

`ConfigUpdate` is the only CONTROL message type in this version. CONTROL messages are defined in [message types](messaging.md#1-message-types).

| Field | Type | Meaning |
|---|---|---|
| `configuration` | `LedgerConfiguration` | The sender's full configuration at the time the ConfigUpdate was enqueued. |

A ConfigUpdate does not carry endpoint manifest changes; those travel in bundles ([peer manifest](endpoint-manifest.md#4-peer-manifest)).

### 5.2 Sending

Each channel records `last_config_timestamp`: the `timestamp` of the last configuration propagated on it. It is set to the consensus time of channel creation. A ConfigUpdate is **due** on a channel when its `last_config_timestamp` is less than the current configuration's `timestamp`.

- The CLPR Service MUST NOT enqueue a ConfigUpdate on a channel that is not ACTIVE. A PAUSED channel that a bundle resumes (Step 11 of [bundle processing](channel-state-transitions.md#2-bundle-processing)) is ACTIVE again at Step 12, so a due ConfigUpdate is enqueued in that bundle.
- When an application sends a DATA message on an ACTIVE channel on which a ConfigUpdate is due, the CLPR Service MUST enqueue the ConfigUpdate before the DATA message ([enqueue](messaging.md#5-enqueue) step 1).
- When the CLPR Service processes a bundle on a channel on which a ConfigUpdate is due, and the channel is ACTIVE at Step 12 of [bundle processing](channel-state-transitions.md#2-bundle-processing), it MUST enqueue the ConfigUpdate at that step.
- When it enqueues a ConfigUpdate, the CLPR Service sets the channel's `last_config_timestamp` to the configuration's `timestamp`.

How the CLPR Service finds the channels on which an update is due is a deployment choice ([Blueprint](../blueprint/clpr-service.md#14-enqueue)).

Because the ConfigUpdate occupies a position in the queue fixed by consensus, both ledgers agree on the point in the message stream at which the new configuration takes effect.

### 5.3 Receiving

When a bundle delivers a ConfigUpdate ([bundle processing](channel-state-transitions.md#2-bundle-processing)), the receiving CLPR Service MUST reject the whole bundle if:

- `configuration.protocol_version` differs from its own protocol version, or
- `configuration.timestamp` is not a valid timestamp ([`schema/`](schema/clpr_ledger_configuration.proto)), or
- `configuration.timestamp` is not strictly greater than the channel's stored peer configuration timestamp, as updated by any earlier ConfigUpdate in the same bundle.

Otherwise it replaces the channel's peer configuration timestamp and peer throttles with `configuration.timestamp` and `configuration.throttles`. It does not apply the other fields.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
