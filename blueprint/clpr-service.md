# CLPR Service

> **Category:** Blueprint (SHOULD)

This document describes the recommended design of a CLPR Service beyond the shared channel state. A deployment can depart from it without affecting interoperability. Notes beginning "On Hiero" or "On EVM ledgers" record ledger-specific choices.

## 1. Structure and internal state

A CLPR Service SHOULD keep the following stores. Their physical layout is defined per ledger. On EVM ledgers, the parts that peers prove are fixed by the [proven storage layout](../ledgers/besu/README.md#3-proven-storage-layout).

| Store | Key | Content |
|---|---|---|
| Ledger configuration | — | The local [ledger configuration](../protocol/ledger-configuration.md#2-ledger-configuration) |
| Economic configuration | — | The non-throttle parameters of [§4](#4-configuration-parameters) |
| Local endpoint manifest | — | The [local manifest](../protocol/endpoint-manifest.md#3-local-manifest) and its admission state ([§3](#3-endpoint-admission)) |
| Channel commitments | commitment | Registered channel commitments ([channel registration](../protocol/channel-setup.md#2-registration)) |
| Channels | channel id | Channel records ([§1.1](#11-channel-record)) |
| Message queue | (channel id, message id) | Queued messages ([§1.2](#12-message-queue)) |
| Connector commitments | commitment | Registered connector commitments ([connector registration](../protocol/connector-setup.md#2-registration)) |
| Connectors | (channel id, connector id) | Connector records and counters ([§1.3](#13-connector-record-and-counters)) |

Connector and stake data never cross the wire. Amounts are `uint64` on Hiero and `uint256` on EVM ledgers.

On EVM ledgers, the Service also keeps pending withdrawals, keyed by account ([payment flow](channel-economics.md#2-payment-to-the-bundle-submitter)). On Hiero, it also keeps the state of an open manifest construction ([§3.3](#33-roster-derived-manifest)).

### 1.1 Channel record

A channel record holds the [shared channel state](../protocol/channel-setup.md#6-shared-channel-state), the [verifier binding](../protocol/channel-setup.md#4-verifier-binding), the [channel context](../protocol/channel-setup.md#3-channel-context), the trust anchor and its id ([verifier contracts and trust anchors](../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors)), and the [peer manifest](../protocol/endpoint-manifest.md#4-peer-manifest). It SHOULD also hold these local fields:

| Field | Type | Meaning |
|---|---|---|
| `chain_id` | `string` | The peer's CAIP-2 chain id, from `verifyConfig` |
| `peer_config_timestamp` | `timestamp` | Timestamp of the last peer configuration applied ([configuration propagation](../protocol/ledger-configuration.md#5-configuration-propagation)) |
| `peer_throttles` | `Throttles` | The peer's throttles from that configuration, used for send-side limits ([enqueue](../protocol/messaging.md#5-enqueue)) |
| `last_config_timestamp` | `timestamp` | Timestamp of the last local configuration propagated on this channel ([sending](../protocol/ledger-configuration.md#52-sending)) |
| `verifier_fingerprint` | `bytes32` | Code hash of the verifier contract at completion |
| `ownership_commitment` | `bytes32` | The commitment the channel was completed with |

At completion, the peer fields are set from `verifyConfig`.

- On Hiero, a completed channel's commitment stays registered.
- On EVM ledgers, the commitment is deleted at completion, and the verifier code hash is emitted at completion rather than stored. The record also holds the channel `salt` ([EVM channel identity](../ledgers/evm/README.md#4-channel-identity)), the peer's service address, and the bookkeeping of [§1.5](#15-reply-and-acknowledgement-bookkeeping). Timestamps are stored as one `uint96` count of nanoseconds since the Unix epoch and converted only at the wire boundary.

### 1.2 Message queue

Each queue entry holds the message payload ([payload encoding](../protocol/messaging.md#3-payload-encoding)) and the running hash after that message ([running hash](../protocol/messaging.md#4-running-hash)). Entries are retained and deleted as [acknowledgement](../protocol/messaging.md#9-acknowledgement) specifies.

On EVM ledgers, each entry also records the connector id of a DATA message. This lets the Service attribute the REPLY to the connector even after the DATA payload is redacted.

### 1.3 Connector record and counters

| Field | Meaning |
|---|---|
| `connector_id` | The connector id ([connector identity](../protocol/connector-setup.md#1-connector-identity)) |
| `channel_id` | The channel the connector serves |
| `connector_contract` | The connector's contract on this ledger ([authorization](../protocol/connector-setup.md#4-authorization-of-outbound-messages)) |
| `admin` | The authority that can remove the connector |
| `locked_stake` | Stake held against misbehavior ([connector stake](stakes-and-bonds.md#1-connector-stake)) |
| `slash_count` | Number of slashes applied so far ([slashing](stakes-and-bonds.md#2-slashing-and-bans)) |

The record has no balance. A connector pays execution charges from its contract's own balance ([execution charges](channel-economics.md#1-execution-charges)).

The Service SHOULD keep, per connector:

- An **in-flight count**: the DATA messages sent through the connector whose REPLY has not been processed. Removal requires it to be zero ([removal](../protocol/connector-setup.md#5-removal)).
- A **quota count**, as defined in [queue quotas](channel-economics.md#3-queue-quotas).

On Hiero, the in-flight count is a field of the connector record, and the quota count is computed from the queue. On EVM ledgers, both are counters keyed by channel and connector.

### 1.4 Enqueue

The checks on `sendMessage` are specified in [enqueue](../protocol/messaging.md#5-enqueue); their order is local. The Service MAY also reject a message that, alone in a bundle, would exceed the peer's `max_sync_bytes`. On EVM ledgers, it rejects a message when `len(message_data) + 32 + len(target_application) + 20 + 32,768` exceeds the peer's `max_sync_bytes`, where 32,768 bytes is the worst-case bundle overhead.

**Lazy configuration propagation.** The Service SHOULD store a configuration update ([§2.4](#24-configuration-updates)) once, and check whether a ConfigUpdate is due on a channel only when that channel next enqueues a message or processes a bundle ([sending](../protocol/ledger-configuration.md#52-sending)). An update then costs the same however many channels exist.

### 1.5 Reply and acknowledgement bookkeeping

Each REPLY matches the oldest outbound DATA message that has no REPLY yet ([response ordering](../protocol/messaging.md#8-response-ordering)). The Service SHOULD keep a reply cursor: the id of that message, advanced past CONTROL and REPLY entries. It SHOULD also keep the id of the last DATA message enqueued. Every DATA message is answered once the cursor passes that id, which is the CLOSING → DRAINED check.

On Hiero, the Service instead walks the retained entries above its stored acknowledgement. It caps that acknowledgement, as local bookkeeping, at the last DATA message whose REPLY has been processed, and a bundle with an out-of-order REPLY leaves it unchanged. On EVM ledgers, the stored acknowledgement is the peer's `received_message_id` ([acknowledgement](../protocol/messaging.md#9-acknowledgement)).

## 2. Administration

### 2.1 Administrator

Privileged operations are performed by the Service administrator: on Hiero, the ledger's privileged system accounts; on EVM ledgers, the owner of the Service contract.

### 2.2 Operations

A Service SHOULD offer the following operations. Each ledger maps them to its own constructs.

| Operation | Caller | Specified in |
|---|---|---|
| `registerChannel`, `completeChannel` | any | [Channel registration](../protocol/channel-setup.md#2-registration) |
| `closeChannel` | administrator | [§2.5](#25-closing-a-channel) |
| `registerConnector`, `completeConnector` | any | [Connector registration](../protocol/connector-setup.md#2-registration) |
| `removeConnector` | connector admin | [Removal](../protocol/connector-setup.md#5-removal), [connector stake](stakes-and-bonds.md#1-connector-stake) |
| `topUpConnectorStake` | any | [Connector stake](stakes-and-bonds.md#1-connector-stake) (EVM ledgers) |
| `sendMessage` | any | [Enqueue](../protocol/messaging.md#5-enqueue) |
| `submitBundle` | any | [Bundle processing](../protocol/channel-state-transitions.md#2-bundle-processing), [§5](#5-bundle-submission) |
| `redactMessage` | administrator | [§2.6](#26-redaction) (deprecated) |
| enable or disable | administrator | [§2.3](#23-initialization-and-kill-switch) |
| `updateLedgerConfiguration` | administrator | [§2.4](#24-configuration-updates) |
| `updateEconomicConfiguration` | administrator | [§2.4](#24-configuration-updates) (EVM ledgers) |
| `registerEndpoint`, `addEndpoint`, `removeEndpoint`, `updateEndpointManifest` | see §3.2 | [§3.2](#32-registration-and-admission) |
| `getLedgerConfiguration`, `getEndpointManifest`, queue and connector queries | any | [§2.7](#27-queries) |
| `collectPending` | any | [Payment flow](channel-economics.md#2-payment-to-the-bundle-submitter) (EVM ledgers) |

### 2.3 Initialization and kill switch

**Initialization** sets the chain id, protocol version, service address, throttles and economic parameters, and creates the local manifest at version 1 with no endpoints. The chain id and protocol version do not change afterwards. On Hiero, the ledger creates this state itself; on EVM ledgers, the administrator initializes the deployed Service once.

**Kill switch.** The Service SHOULD have an enable flag, checked on every call. While it is off, the Service SHOULD reject every operation except those that initialize and re-enable it. On Hiero, the flag is on by default; on EVM ledgers, it is off until the administrator enables it after initialization.

### 2.4 Configuration updates

`updateLedgerConfiguration` replaces the local throttles and keeps the chain id and protocol version. It sets the configuration's timestamp to the consensus time of the update. Channels receive the change lazily ([§1.4](#14-enqueue)).

The Service SHOULD reject an update that violates the constraints of [throttles](../protocol/ledger-configuration.md#3-throttles).

- On Hiero, the per-message overhead used in the `max_sync_bytes` check is 65,536 bytes, and an update is rejected unless its service address is empty or the Service's own.
- On EVM ledgers, the update also sets the service address and the configuration's trust anchor fields. It is rejected if only one of the anchor and its id is set. Because consensus time is the block time, the administrator SHOULD apply at most one configuration update per block, so that each update has a later timestamp.

**Economic parameters** are the parameters in [§4.2](#42-service-parameters). On Hiero, they are network properties, changed through the ledger's network configuration. On EVM ledgers, the administrator changes them with `updateEconomicConfiguration`, which enforces the bounds in [§4.2](#42-service-parameters).

### 2.5 Closing a channel

`closeChannel` lets the administrator shut a channel down. Its effect depends on the channel status:

| Status | Effect |
|---|---|
| PENDING (registered commitment, not completed) | The commitment is removed |
| ACTIVE, PAUSED | → CLOSING. In the same step → DRAINED if no DATA message remains in the outbound queue ([closing and draining](../protocol/channel-state-transitions.md#5-closing-and-draining)) |
| DRAINED | → CLOSED, only if `acked_message_id ≥ next_message_id − 1`; otherwise rejected |
| CLOSING, CLOSED | Rejected |

The DRAINED → CLOSED path is the recovery when no bundle from the peer will close the channel. Because every outbound message is acknowledged, nothing is abandoned.

### 2.6 Redaction

`redactMessage` is deprecated and SHOULD NOT be used ([redaction](../protocol/messaging.md#10-redaction-deprecated)). It accepts only a DATA message that is not yet redacted and whose id is above `acked_message_id` and below `next_message_id`. It replaces the payload with its redacted form and keeps the message id and running hash.

On Hiero, redaction is allowed in any channel status. On EVM ledgers, it decrements the connector's quota count ([queue quotas](channel-economics.md#3-queue-quotas)).

### 2.7 Queries

The Service SHOULD offer these read operations to any caller. None of them is part of [endpoint sync](../protocol/endpoint-sync/README.md).

| Query | Returns |
|---|---|
| `getLedgerConfiguration` | The local [ledger configuration](../protocol/ledger-configuration.md#2-ledger-configuration) |
| `getEndpointManifest` | The [local manifest](../protocol/endpoint-manifest.md#3-local-manifest) |
| Queue state | A channel's queue state: on Hiero, the received and acknowledged ids; on EVM ledgers, the queue depth and `max_queue_depth` |
| `getConnector` | A connector's record ([§1.3](#13-connector-record-and-counters)) |
| `deriveConnectorId` | The [connector id](../protocol/connector-setup.md#1-connector-identity) for given inputs (MAY be offered) |

On Hiero, the configuration and manifest responses also carry a state proof of the returned value ([configuration and manifest proofs](../ledgers/hiero/proof-schemes/hints-wraps.md#9-configuration-and-manifest-proofs)).

## 3. Endpoint admission

This section covers how endpoints enter and leave the [local manifest](../protocol/endpoint-manifest.md#3-local-manifest).

### 3.1 Common rules

- Only admitted endpoints appear in the manifest.
- The manifest version starts at 1 ([endpoint manifest](../protocol/endpoint-manifest.md#2-endpoint-manifest)) and increases by exactly 1 for each change, or batch of changes, to the set of admitted endpoints.
- Admission SHOULD NOT exceed `max_local_endpoints` (0 means no limit).
- An admitted endpoint serves every channel of the Service.
- Manifest membership is unrelated to bundle submission ([§5](#5-bundle-submission)).

### 3.2 Registration and admission

Ledgers where any party can offer an endpoint, such as EVM ledgers, SHOULD use a two-step model. An endpoint registers, and the administrator admits it. Endpoints are not bonded ([endpoints](stakes-and-bonds.md#3-endpoints)).

The Service keeps one entry per registrant account:

| Field | Meaning |
|---|---|
| `endpoint` | The endpoint data ([endpoint](../protocol/endpoint-manifest.md#1-endpoint)) |
| `status` | `PENDING` (registered) or `LIVE` (admitted) |

The registrant account is the caller of `registerEndpoint`. It is unique among entries. It need not be the account that submits bundles.

| Operation | Caller | Effect | Version |
|---|---|---|---|
| `registerEndpoint(endpoint)` | any | Creates a PENDING entry. Rejected if an entry exists. The Service MAY validate the endpoint data, for example the certificate check of the [EVM family](../ledgers/evm/README.md#6-endpoint-certificates) | Unchanged |
| `addEndpoint(registrant, endpoint)` | administrator | Promotes a PENDING entry, using its registered data. With no entry, adds `endpoint` directly. Rejected if the entry is already LIVE or the manifest is full | +1 |
| `removeEndpoint(registrant)` | registrant or administrator | Removes the entry | +1 if the entry was LIVE |
| `updateEndpointManifest(add, remove)` | administrator | Applies a batch atomically. Removals come first and skip unknown accounts. Additions follow `addEndpoint` and skip entries already LIVE. Rejected if the result would exceed `max_local_endpoints` | +1 once, if anything changed |

### 3.3 Roster-derived manifest

On a ledger whose consensus nodes are its endpoints, the Service MAY derive the manifest from the node roster instead, with no administrator operations. Hiero does this:

1. Each node publishes its own endpoint (network address, TLS certificate, and node account) in a node-only transaction, at startup if it is absent from the manifest.
2. A publication from a roster node whose endpoint is not in the manifest opens a **construction** for the next version, targeting the active roster, with a deadline `manifestGracePeriod` away.
3. While a construction is open, the Service gathers publications from target nodes. A later publication from the same node replaces the earlier one.
4. The construction closes when every target has published. Otherwise, at the deadline it is extended by `manifestGraceExtension`, up to `manifestMaxGraceExtensions` times, and then closed regardless.
5. On close, the manifest becomes exactly the gathered endpoints. Its version increases by 1 if the endpoint list changed and is unchanged otherwise.
6. When a network upgrade changes the roster's composition, a new construction for the new roster replaces any open one.

A change in node weights alone does not change the manifest. A misbehaving node is removed through the ledger's own governance of the roster.

## 4. Configuration parameters

### 4.1 Throttles

The meaning of each throttle is defined in [throttles](../protocol/ledger-configuration.md#3-throttles). Recommended defaults:

| Throttle | Hiero | EVM ledgers |
|---|---|---|
| `max_queue_depth` | 10,000 | 1,000 |
| `max_message_payload_bytes` | 65,536 | 1,024 |
| `max_messages_per_bundle` | 1,000 | 100 |
| `max_gas_per_message` | min(15,000,000, the ledger's maximum gas per transaction) | 1,000,000 |
| `max_sync_bytes` | 4,194,304 | 1,048,576 |
| `max_local_endpoints` | 0 (no limit) | 0 (no limit) |
| `max_peer_endpoints` | 0 (no limit) | 0 (no limit) |

`max_messages_per_bundle` SHOULD be small enough that a full bundle fits the ledger's transaction size and execution limits ([§5.4](#54-bundle-size-for-evm-receivers-of-hiero-bundles)).

### 4.2 Service parameters

Amounts are in the ledger's smallest currency unit: 10⁻⁸ of a whole token on Hiero, and wei on EVM ledgers. "—" means the parameter does not exist on that ledger. Parameter names are informative; each ledger binds its own.

| Parameter | Hiero | EVM ledgers | Meaning |
|---|---|---|---|
| enabled | true | false | Kill switch ([§2.3](#23-initialization-and-kill-switch)) |
| `minLockedStake` | 100,000,000 | 10¹⁷ | Minimum connector stake ([connector stake](stakes-and-bonds.md#1-connector-stake)) |
| `slashBasePenalty` | 10,000,000 | 10¹⁶ | Base penalty ([slashing](stakes-and-bonds.md#2-slashing-and-bans)) |
| `slashMultiplier` | 2 | 2 | Penalty multiplier per earlier slash |
| `slashBanThreshold` | 5 | 5 | Slash count at which a connector is banned |
| `messageExecutionCost` | 1,000,000 | — (not used) | Flat execution charge per DATA message ([execution charges](channel-economics.md#1-execution-charges)) |
| `endpointMarginPercent` | 10 | 10 | Margin added to execution charges |
| `connectorQueueQuotaPct` | 50 | 50 (below 100) | Per-connector share of `max_queue_depth` ([queue quotas](channel-economics.md#3-queue-quotas)) |
| `connectorPaymentGasLimit` | — | 200,000 (minimum 50,000) | Gas for the connector's payment call |
| `connectorInboundGasStipend` | — | 500,000 | Gas for the connector's inbound-message notification ([§6.4](#64-reentrancy-and-external-calls)) |
| `maxChannels`, `maxConnectors` | — | 0 (no limit) | Caps on channel and connector counts |
| `verifierGasLimit` | 300,000 | all available gas | Gas given to a verifier call |
| `manifestGracePeriod` | 300 s | — | Construction deadline ([§3.3](#33-roster-derived-manifest)) |
| `manifestGraceExtension` | 300 s | — | Length of each extension |
| `manifestMaxGraceExtensions` | 2 | — | Maximum number of extensions |

## 5. Bundle submission

### 5.1 Who submits

Any account can call `submitBundle`. An endpoint that receives a bundle during sync submits it to its own ledger. The submitter pays the transaction fee and receives the execution charges ([payment flow](channel-economics.md#2-payment-to-the-bundle-submitter)) and slash proceeds ([slashing](stakes-and-bonds.md#2-slashing-and-bans)) that the bundle produces.

On Hiero, the receiving node submits a node transaction paid by its node account, and skips empty payloads. On EVM ledgers, the endpoint signs with its own account.

Endpoint operators SHOULD pre-fund their submitting accounts for transaction fees, which the charges paid during processing cannot cover.

### 5.2 Checks before submitting

An endpoint SHOULD NOT submit a bundle that the Service would reject. A rejected bundle still costs the submitter its transaction fee.

- **Progress.** The endpoint SHOULD evaluate the [progress criteria](../protocol/channel-state-transitions.md#3-progress) against its last known view of the destination channel: the received message id, the trust anchor id, and the manifest version the peer reported. If no criterion holds, it does not submit.
- **Verification.** The endpoint SHOULD check that the bundle verifies and processes before submitting it, for example by a read-only preview of the submission.

On Hiero, the receiving node submits without verifying the bundle; the sending node verifies its own proof before sending. When a node sends nothing is defined in [Hiero bundle aggregation §5](../ledgers/hiero/bundle-aggregation.md#5-when-nothing-is-sent).

On EVM ledgers, the endpoint previews every submission against pending state and skips any bundle that would revert.

### 5.3 Peer selection

An endpoint SHOULD choose sync peers from the peer manifest at random, weighted toward peers that have delivered useful bundles. It SHOULD prefer peers that reciprocate. The weighting is the endpoint's own local choice; the Service keeps no endpoint reputation.

### 5.4 Bundle size for EVM receivers of Hiero bundles

Verifying a Hiero bundle on an EVM ledger is expensive, and the cost grows with the number of messages. The verifier also accepts at most 64 proof paths: one for the channel, one for the manifest when included, and one per message.

An EVM ledger that receives bundles from Hiero SHOULD set `max_messages_per_bundle` so that a full bundle stays within the path limit and within the ledger's per-transaction gas limit. On a ledger with a low per-transaction gas cap, a bundle can carry only a few messages.

A Hiero network can produce verifiable bundles only after its WRAPS proof setup has completed ([hinTS with WRAPS](../ledgers/hiero/proof-schemes/hints-wraps.md)).

## 6. Security considerations

### 6.1 Verifier choice

Channel creation is permissionless, and there is no allow-list of verifiers. A malicious or faulty verifier can return fabricated bundle content and compromise the channel. Before using a channel, an application SHOULD evaluate its verifier contract, including whether it is upgradeable and who controls the upgrades.

### 6.2 Finality

For a peer ledger without instant finality, a verifier SHOULD accept only final or safe state ([proof requirements](../protocol/bundle.md#4-proof-requirements)). A verifier MAY accept earlier state for lower latency; the channel's users then bear the risk that the state is reverted. How an endpoint reads state is set by each ledger's bundle aggregation (for example, [Besu state read and finality](../ledgers/besu/bundle-aggregation.md#2-state-read-and-finality)).

### 6.3 Endpoint admission

On ledgers with endpoint registration, the defense against Sybil endpoints is administrator curation ([§3.2](#32-registration-and-admission)). Endpoints are not bonded or slashed ([endpoints](stakes-and-bonds.md#3-endpoints)), and the Service keeps no endpoint reputation. The administrator MAY evict misbehaving endpoints ([§3.2](#32-registration-and-admission)), and the transaction fee deters the submission of stale manifest bundles. Curation places full trust in the administrator, including trust that it will not empty the manifest. Endpoints SHOULD randomize peer selection ([§5.3](#53-peer-selection)).

### 6.4 Reentrancy and external calls

Dispatching a message hands control to another contract. The Service SHOULD:

- guard its state-changing entry points against reentrancy, and
- complete its own state changes, including debiting charges, before making an external call.

Calls to connector notification callbacks SHOULD carry a fixed gas limit (`connectorInboundGasStipend`). A failed callback SHOULD NOT block message processing.

### 6.5 Application payloads

CLPR provides authenticity and integrity but not confidentiality. Payloads are stored on both ledgers in plaintext.

- Applications SHOULD treat every cross-ledger payload as untrusted input.
- Applications that need confidentiality SHOULD encrypt payloads themselves.

### 6.6 Service upgrades

On EVM ledgers, peers prove the Service's state by its [proven storage layout](../ledgers/besu/README.md#3-proven-storage-layout). An upgrade that changes the layout breaks bundle production and verification. It SHOULD be coordinated with endpoint operators and verifier deployments, or deployed as a new Service.

### 6.7 Queue monopolization

Per-connector quotas keep one connector from filling a channel's queue ([queue quotas](channel-economics.md#3-queue-quotas)).

## 7. Recovery scenarios

| # | Scenario | Recovery | Result |
|---|---|---|---|
| R1 | Peer endpoints rotated (during a partition, or on both sides at once) | Anyone obtains from the peer ledger a bundle that carries the peer's current manifest and submits it with `submitBundle`. The peer manifest is replaced and sync resumes | Works |
| R2 | Peer changes its proof format | Register a new channel with a new verifier and migrate applications; the administrator closes the old channel | New channel |
| R3 | R1 and R2 together | R2, then R1 on the new channel | New channel |
| R4 | Verifier compromised or broken | The administrator closes the channel; register a new channel with a correct verifier | New channel; messages in flight can be lost ([OI-3](../protocol/open-issues.md#oi-3-messages-left-without-replies-when-a-channel-cannot-drain)) |
| R5 | Peer's queue state corrupted | The channel pauses, and resumes when the peer's replies are ordered again ([pause and resume](../protocol/channel-state-transitions.md#6-pause-and-resume)). The administrator can close it; it drains once the peer is fixed | Works once the peer recovers |
| R6 | Partition with unchanged endpoints, or peer ledger down | Messages queue up to `max_queue_depth`, then `sendMessage` is rejected. Sync resumes when the peer is reachable; message ids and running hashes keep delivery exact | Works |
| R7 | A DRAINED side receives no bundle with status CLOSED | The administrator closes the channel ([§2.5](#25-closing-a-channel)) | Closed |

Recovery R1 depends on every bundle carrying queue metadata ([bundle content](../protocol/bundle.md#1-bundle-content)).
