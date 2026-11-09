# Coverage Matrix

## Purpose

This record accounts for every item of the EAP v0.2 specification text (archived in [`archive/eap-v0.2-source/`](../eap-v0.2-source/README.md)) in the rewritten v0.2 specification. For each item it gives the file and section that now holds it, or the reason it is not carried. An item was dropped only when no v0.2 implementation implements it. There is one table per source document: [`clpr-service-spec.md`](../eap-v0.2-source/clpr-service-spec.md), [`clpr-service.md`](../eap-v0.2-source/clpr-service.md) and the [verifier documents](../eap-v0.2-source/verifiers/README.md). Rows are grouped under the section headings of the archived document, in document order. Row numbers run within each table. Where an item is stated in several places, the first link is the main one.

## Legend

| Status | Meaning |
|---|---|
| `specified` | Specified normatively in the Protocol or a Ledger Specification. |
| `overview` | Described in the [overview](../../clpr-overview.md); not normative. |
| `blueprint` | Described in the [Blueprint](../../blueprint/clpr-service.md), the recommended Service design. |
| `open issue OI-n` | Recorded as an [open issue](../../protocol/open-issues.md). |
| `merged` | Restates another row; the Location names that row. |
| `archived` | Rationale, history or a superseded design; it remains only in `archive/`. |
| `dropped: not implemented` | Not implemented in v0.2, and therefore not carried. |
| `removed: reference only` | The text only named a product; nothing is carried. |

## `clpr-service-spec.md`

| # | Item | Status | Location in v0.2 |
|---|---|---|---|
| | **[CLPR Protocol Specification](../eap-v0.2-source/clpr-service-spec.md#clpr-protocol-specification)** | | |
| 1 | Scope of the specification; platform APIs left to ledger specifications | overview | [clpr-overview.md §6](../../clpr-overview.md#6-how-the-specification-is-organized) |
| 2 | Pointer to the companion design document | archived | Reference to a document that the new layout replaces; archive only |
| | **[Notation](../eap-v0.2-source/clpr-service-spec.md#notation)** | | |
| 3 | Requirement keywords follow RFC 2119 | specified | [protocol/conventions.md §1](../../protocol/conventions.md#1-requirement-keywords) |
| 4 | Protobuf definitions use proto3 syntax | specified | [protocol/schema/README.md §2](../../protocol/schema/README.md#2-encoding-rules) |
| 5 | `bytes` fields are opaque unless defined | specified | [protocol/conventions.md §2](../../protocol/conventions.md#2-notation), [§3](../../protocol/conventions.md#3-abstract-data-structures) |
| 6 | Pseudo-API signatures are language-neutral and bound by each ledger | specified | [protocol/conventions.md §3](../../protocol/conventions.md#3-abstract-data-structures) |
| | **[1. Protobuf Definitions](../eap-v0.2-source/clpr-service-spec.md#1-protobuf-definitions)** | | |
| 7 | Standard protobuf encoding is required | specified | [protocol/schema/README.md §2](../../protocol/schema/README.md#2-encoding-rules) |
| 8 | Messages with unrecognized fields are rejected | specified | [protocol/schema/README.md §2](../../protocol/schema/README.md#2-encoding-rules); [protocol/conventions.md §3](../../protocol/conventions.md#3-abstract-data-structures) |
| 9 | Field numbers are fixed; deprecated fields and values stay on the wire and are accepted | specified | [protocol/schema/README.md §2](../../protocol/schema/README.md#2-encoding-rules); [protocol/conventions.md §3](../../protocol/conventions.md#3-abstract-data-structures) |
| | **[1.1 Ledger Identity and Configuration](../eap-v0.2-source/clpr-service-spec.md#11-ledger-identity-and-configuration)** | | |
| 10 | Protobuf package declaration | specified | [protocol/endpoint-sync/schema/clpr_endpoint_sync.proto](../../protocol/endpoint-sync/schema/clpr_endpoint_sync.proto); [protocol/endpoint-sync/README.md §7](../../protocol/endpoint-sync/README.md#7-schema) |
| 11 | `ClprLedgerConfiguration` structure and field numbers | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration); [protocol/schema/clpr_ledger_configuration.proto](../../protocol/schema/clpr_ledger_configuration.proto) |
| 12 | Configurations with an unrecognized protocol version are rejected | specified | [protocol/ledger-configuration.md §4](../../protocol/ledger-configuration.md#4-protocol-version); [protocol/open-issues.md OI-8](../../protocol/open-issues.md#oi-8-protocol-version-at-channel-setup) |
| 13 | Chain id uses CAIP-2 format | specified | [protocol/ledger-configuration.md §1](../../protocol/ledger-configuration.md#1-ledger-identity); [protocol/conventions.md §5](../../protocol/conventions.md#5-identifiers) |
| 14 | `service_address` is the on-ledger address of the CLPR Service | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration) |
| 15 | Configuration `timestamp` is the consensus time of the last change and increases monotonically | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration), [§5.3](../../protocol/ledger-configuration.md#53-receiving) |
| 16 | Deprecated `endpoints` field of the configuration is ignored | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 17 | Initial trust anchor is taken from the proven configuration or derived from a separate proof | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration); [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig) |
| 18 | `initial_trust_anchor_id` is non-empty exactly when the initial trust anchor is non-empty | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration) |
| 19 | `Timestamp` structure defined locally | specified | [protocol/schema/clpr_ledger_configuration.proto](../../protocol/schema/clpr_ledger_configuration.proto) |
| 20 | Valid ranges of `seconds` and `nanos` | specified | [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 21 | Single nanosecond integer representation of timestamps on EVM ledgers | blueprint | [blueprint/clpr-service.md §1.1](../../blueprint/clpr-service.md#11-channel-record); [ledgers/evm/verifier-api.md §3.4](../../ledgers/evm/verifier-api.md#34-scalars-and-absent-values) |
| 22 | `ClprThrottles` structure and field numbers | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/schema/README.md](../../protocol/schema/README.md); [ledgers/evm/verifier-api.md §3.1](../../ledgers/evm/verifier-api.md#31-structures) |
| 23 | Throttles are ledger-wide, advertised to peers and enforced per channel | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 24 | `max_messages_per_bundle` throttle | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 25 | `max_message_payload_bytes` throttle, checked at enqueue and at bundle processing | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 26 | `max_gas_per_message` throttle | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 27 | `max_queue_depth` throttle | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 28 | `max_sync_bytes` throttle; larger sync messages are rejected | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 29 | `max_sync_bytes` must exceed one maximal message plus overhead | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 30 | `max_local_endpoints` throttle | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest); [blueprint/clpr-service.md §3.1](../../blueprint/clpr-service.md#31-common-rules) |
| 31 | `max_peer_endpoints` throttle; first N peer endpoints are cached | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| | **[1.2 Endpoint Identity](../eap-v0.2-source/clpr-service-spec.md#12-endpoint-identity)** | | |
| 32 | `ClprEndpoint` structure | specified | [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 33 | Endpoint `tls_certificate` is optional and carries no identity | specified | [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint) |
| 34 | Endpoint `account_id` is optional and informational | specified | [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint) |
| 35 | `ServiceEndpoint` structure (numeric IP address and port) | specified | [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 36 | `ClprEndpointManifest` structure, separate from the configuration | specified | [protocol/endpoint-manifest.md §2](../../protocol/endpoint-manifest.md#2-endpoint-manifest); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 37 | Manifest version starts at 1 and increases on every change | specified | [protocol/endpoint-manifest.md §2](../../protocol/endpoint-manifest.md#2-endpoint-manifest) |
| 38 | Verifier rejects a manifest whose service address differs from the channel's peer service | specified | [protocol/endpoint-manifest.md §5](../../protocol/endpoint-manifest.md#5-manifest-proofs); [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle) |
| 39 | A manifest with no endpoints is valid | specified | [protocol/endpoint-manifest.md §2](../../protocol/endpoint-manifest.md#2-endpoint-manifest) |
| | **[1.3 Control Messages](../eap-v0.2-source/clpr-service-spec.md#13-control-messages)** | | |
| 40 | `ClprControlMessage` structure; control messages are not dispatched and get no reply | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/ledger-configuration.md §5.1](../../protocol/ledger-configuration.md#51-configupdate); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 41 | A control message of unknown type causes rejection of the bundle | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/ledger-configuration.md §4](../../protocol/ledger-configuration.md#4-protocol-version) |
| 42 | `ClprConfigUpdate` structure | specified | [protocol/ledger-configuration.md §5.1](../../protocol/ledger-configuration.md#51-configupdate); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 43 | Configuration changes are enqueued lazily on each channel's next interaction | specified | [protocol/ledger-configuration.md §5.2](../../protocol/ledger-configuration.md#52-sending); [blueprint/clpr-service.md §1.4](../../blueprint/clpr-service.md#14-enqueue) |
| 44 | Receiver accepts a configuration update only with a strictly newer timestamp | specified | [protocol/ledger-configuration.md §5.3](../../protocol/ledger-configuration.md#53-receiving) |
| | **[1.4 Message Queue](../eap-v0.2-source/clpr-service-spec.md#14-message-queue)** | | |
| 45 | `ClprMessageKey` structure (32-byte channel id, message id) | specified | [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 46 | `ClprMessageValue` structure and running hash definition | specified | [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue), [§4](../../protocol/messaging.md#4-running-hash); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 47 | `ClprMessagePayload` variants (data, reply, control, deprecated redacted) | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types), [§2](../../protocol/messaging.md#2-message-identifiers-and-queue); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 48 | Deprecated `ClprRedactedMessage` structure | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types), [§10](../../protocol/messaging.md#10-redaction-deprecated); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 49 | `ClprMessage` structure | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 50 | `connector_id` derivation and resolution by channel and connector id | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 51 | `sender` is stamped by the CLPR Service at enqueue | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types), [§5](../../protocol/messaging.md#5-enqueue) |
| 52 | `ClprMessageReplyStatus` values and their slashing effect | specified | [protocol/messaging.md §7](../../protocol/messaging.md#7-replies); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 53 | `ClprMessageReply` structure | specified | [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 54 | Every data message produces exactly one reply, in order | specified | [protocol/messaging.md §7](../../protocol/messaging.md#7-replies), [§8](../../protocol/messaging.md#8-response-ordering) |
| | **[1.5 Sync Protocol](../eap-v0.2-source/clpr-service-spec.md#15-sync-protocol)** | | |
| 55 | A sync cycle is a bidirectional stream scoped to one channel | specified | [protocol/endpoint-sync/README.md §1](../../protocol/endpoint-sync/README.md#1-purpose-and-roles), [§3](../../protocol/endpoint-sync/README.md#3-exchange) |
| 56 | `ClprSyncPayload` structure | specified | [protocol/endpoint-sync/README.md §3.1](../../protocol/endpoint-sync/README.md#31-messages), [§3.2](../../protocol/endpoint-sync/README.md#32-rules), [§7](../../protocol/endpoint-sync/README.md#7-schema); [protocol/endpoint-sync/schema/README.md](../../protocol/endpoint-sync/schema/README.md) |
| 57 | `BundleRequest` structure | specified | [protocol/endpoint-sync/README.md §3.1](../../protocol/endpoint-sync/README.md#31-messages); [protocol/endpoint-sync/schema/README.md](../../protocol/endpoint-sync/schema/README.md) |
| 58 | Bundle requests are unproven hints and cause no state change | specified | [protocol/endpoint-sync/README.md §3.1](../../protocol/endpoint-sync/README.md#31-messages) |
| 59 | `BundleResponse` structure | specified | [protocol/endpoint-sync/README.md §3.1](../../protocol/endpoint-sync/README.md#31-messages); [protocol/endpoint-sync/schema/README.md](../../protocol/endpoint-sync/schema/README.md) |
| 60 | `ClprChannelStatus` values | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 61 | `ClprQueueMetadata` structure | specified | [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata); [protocol/schema/README.md](../../protocol/schema/README.md) |
| 62 | Queue metadata comes from the sender's proven channel state; a bundle may be a prefix | specified | [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata), [§3](../../protocol/bundle.md#3-partial-bundles) |
| 63 | Peer's `received_message_id` updates the local acknowledged id | specified | [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata); [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| 64 | `received_running_hash` is available for cross-checking | specified | [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 65 | Metadata trust anchor id and manifest version are informational only | specified | [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 66 | Message range of a bundle and its start rule | specified | [protocol/endpoint-sync/README.md §4](../../protocol/endpoint-sync/README.md#4-message-range); [ledgers/hiero/bundle-aggregation.md §3](../../ledgers/hiero/bundle-aggregation.md#3-message-range-and-limits); [ledgers/besu/bundle-aggregation.md §3](../../ledgers/besu/bundle-aggregation.md#3-message-range-and-limits) |
| 67 | An overstated request yields a bundle the requestor rejects | specified | [protocol/endpoint-sync/README.md §4](../../protocol/endpoint-sync/README.md#4-message-range) |
| 68 | The last message of a bundle need not be the sender's latest | specified | [protocol/bundle.md §3](../../protocol/bundle.md#3-partial-bundles) |
| 69 | Earlier messages are secured by the last message's running hash | specified | [protocol/bundle.md §4](../../protocol/bundle.md#4-proof-requirements) |
| | **[gRPC Endpoint Service](../eap-v0.2-source/clpr-service-spec.md#grpc-endpoint-service)** | | |
| 70 | Every endpoint exposes the gRPC endpoint service sized for `max_sync_bytes` | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 71 | The endpoint service is served on one advertised address and port | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 72 | Fixed gRPC method path for `sync` | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 73 | Server-side TLS rules; no client certificate | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 74 | Client-side TLS rules and plaintext fallback | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 75 | No endpoint identity from transport; integrity rests on state proofs | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 76 | `ClprEndpointService` gRPC service definition | specified | [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport); [protocol/endpoint-sync/schema/README.md](../../protocol/endpoint-sync/schema/README.md) |
| 77 | One stream is one sync cycle; closing and connection reuse | specified | [protocol/endpoint-sync/README.md §3.2](../../protocol/endpoint-sync/README.md#32-rules), [§3.3](../../protocol/endpoint-sync/README.md#33-sequence) |
| | **[1.6 Misbehavior Detection (Local Only)](../eap-v0.2-source/clpr-service-spec.md#16-misbehavior-detection-local-only)** | | |
| 78 | Misbehavior detection is local only | specified | [protocol/endpoint-sync/README.md §6](../../protocol/endpoint-sync/README.md#6-misbehavior) |
| | **[2. On-Ledger State Model](../eap-v0.2-source/clpr-service-spec.md#2-on-ledger-state-model)** | | |
| 79 | On-ledger state that every implementation maintains | specified | [protocol/channel-setup.md §6](../../protocol/channel-setup.md#6-shared-channel-state); [blueprint/clpr-service.md §1](../../blueprint/clpr-service.md#1-structure-and-internal-state) |
| 80 | Connector and endpoint-bond data never crosses the wire; amount widths are ledger-specific | blueprint | [blueprint/clpr-service.md §1](../../blueprint/clpr-service.md#1-structure-and-internal-state); [blueprint/stakes-and-bonds.md](../../blueprint/stakes-and-bonds.md) |
| | **[2.1 Channel](../eap-v0.2-source/clpr-service-spec.md#21-channel)** | | |
| 81 | Channel id: 32 bytes, chosen by the registrant, not derived from a key | specified | [protocol/channel-setup.md §1](../../protocol/channel-setup.md#1-channel-identity); [ledgers/evm/README.md §4](../../ledgers/evm/README.md#4-channel-identity) |
| 82 | Commit-reveal registration with ownership commitment | specified | [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| 83 | The channel is one logical structure; storage layout is free | specified | [protocol/channel-setup.md §6](../../protocol/channel-setup.md#6-shared-channel-state) |
| 84 | `Channel` record fields | specified | [protocol/channel-setup.md §6](../../protocol/channel-setup.md#6-shared-channel-state); [blueprint/clpr-service.md §1.1](../../blueprint/clpr-service.md#11-channel-record) |
| 85 | Verifier contract is immutable after registration; fingerprint is informational | specified | [protocol/channel-setup.md §4](../../protocol/channel-setup.md#4-verifier-binding); [blueprint/clpr-service.md §1.1](../../blueprint/clpr-service.md#11-channel-record) |
| 86 | Channel trust anchor: initialization and update path | specified | [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors), [§4](../../protocol/verifier-interface.md#4-trust-anchor-changes); [ledgers/hiero/README.md §1](../../ledgers/hiero/README.md#1-ledger-identity), [§3](../../ledgers/hiero/README.md#3-built-in-verifiers) |
| 87 | Channel trust anchor id: initialization and update | specified | [protocol/channel-setup.md §5](../../protocol/channel-setup.md#5-initial-peer-state); [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 88 | Channel context is set at completion and immutable | specified | [protocol/channel-setup.md §3](../../protocol/channel-setup.md#3-channel-context) |
| 89 | Last configuration timestamp drives lazy configuration updates | specified | [protocol/ledger-configuration.md §5.2](../../protocol/ledger-configuration.md#52-sending); [blueprint/clpr-service.md §1.4](../../blueprint/clpr-service.md#14-enqueue) |
| 90 | Initial values of channel counters and hashes | specified | [protocol/channel-setup.md §5](../../protocol/channel-setup.md#5-initial-peer-state), [§6](../../protocol/channel-setup.md#6-shared-channel-state); [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue), [§8](../../protocol/messaging.md#8-response-ordering) |
| 91 | Peer manifest cached on the channel and its initialization | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest); [protocol/channel-setup.md §5](../../protocol/channel-setup.md#5-initial-peer-state) |
| 92 | Queue entries are stored separately, keyed by channel and message id | specified | [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue) |
| | **[2.1.1 Channel Status Transitions](../eap-v0.2-source/clpr-service-spec.md#211-channel-status-transitions)** | | |
| 93 | Transition to PENDING on registration | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status), [§4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 94 | Transition PENDING to ACTIVE on completion | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 95 | Administrator close of a PENDING channel deletes it | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions); [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 96 | Transition ACTIVE to PAUSED on a response ordering violation | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions), [§6](../../protocol/channel-state-transitions.md#6-pause-and-resume); [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering) |
| 97 | Transition ACTIVE to CLOSING | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 98 | Transition PAUSED to ACTIVE on correct ordering | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 99 | Transition PAUSED to CLOSING | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions), [§6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 100 | Transition CLOSING to DRAINED | specified | [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 101 | Transition DRAINED to CLOSED by bundle | specified | [protocol/channel-state-transitions.md §2 Step 14](../../protocol/channel-state-transitions.md#2-bundle-processing), [§4](../../protocol/channel-state-transitions.md#4-status-transitions), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 102 | Transition DRAINED to CLOSED by administrator | blueprint | [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 103 | PENDING: no messages, bundles or sync | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status) |
| 104 | ACTIVE: bundles processed normally | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status) |
| 105 | PAUSED: behavior and resumption | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status), [§6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 106 | CLOSING: behavior | specified | [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 107 | DRAINED: behavior | specified | [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining); [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 108 | CLOSED: all bundles rejected | specified | [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| | **[2.1.2 Bundle Progress Criteria](../eap-v0.2-source/clpr-service-spec.md#212-bundle-progress-criteria)** | | |
| 109 | A bundle must make progress; endpoints do not submit bundles without progress | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress); [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| 110 | Progress criterion: new messages | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 111 | Progress criterion: trust anchor change | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 112 | Progress criterion: newer manifest | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 113 | Progress criterion: new acknowledgement | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 114 | Progress criterion: peer status moves the channel to CLOSING | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 115 | Progress criterion: channel becomes DRAINED | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 116 | Progress criterion: channel becomes CLOSED | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 117 | Endpoint progress pre-check against its cached view of the destination | blueprint | [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| 118 | Service progress check on actual values; endpoint pre-check is the primary gate | specified | [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing); [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| | **[2.2 Connector](../eap-v0.2-source/clpr-service-spec.md#22-connector)** | | |
| 119 | A connector is registered on a channel and has a counterpart on the peer | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity), [§3](../../protocol/connector-setup.md#3-connectors-on-both-ledgers) |
| 120 | Connector id derivation with optional salt | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 121 | `Connector` record fields | blueprint | [blueprint/clpr-service.md §1.3](../../blueprint/clpr-service.md#13-connector-record-and-counters); [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake) |
| 122 | Connectors keyed by channel and connector id; authorization call on send | specified | [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages); [ledgers/evm/README.md §3.2](../../ledgers/evm/README.md#32-connectors) |
| 123 | Dispatch resolves the connector id directly; no address translation | specified | [protocol/connector-setup.md §3](../../protocol/connector-setup.md#3-connectors-on-both-ledgers) |
| 124 | Connector must be registered on both ledgers | specified | [protocol/connector-setup.md §3](../../protocol/connector-setup.md#3-connectors-on-both-ledgers) |
| 125 | Connector and channel relationship is many-to-many | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| | **[2.3 Endpoint Bond](../eap-v0.2-source/clpr-service-spec.md#23-endpoint-bond)** | | |
| 126 | Endpoint bond on permissionless ledgers | blueprint | [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond) |
| | **[2.4 Endpoint Manifest](../eap-v0.2-source/clpr-service-spec.md#24-endpoint-manifest)** | | |
| 127 | Local manifest kept by the Service; each channel caches the peer's | specified | [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest) |
| | **[2.4.1 Local Endpoint Manifest](../eap-v0.2-source/clpr-service-spec.md#241-local-endpoint-manifest)** | | |
| 128 | Local manifest entry fields | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission) |
| 129 | Registrant account need not be the bundle submitter | blueprint | [blueprint/clpr-service.md §3.1](../../blueprint/clpr-service.md#31-common-rules), [§3.2](../../blueprint/clpr-service.md#32-registration-and-admission) |
| 130 | Local manifest population: roster-derived or two-step admission | specified | [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest); [blueprint/clpr-service.md §3](../../blueprint/clpr-service.md#3-endpoint-admission) |
| | **[2.4.2 Peer Manifest (on-ledger, per Channel)](../eap-v0.2-source/clpr-service-spec.md#242-peer-manifest-on-ledger-per-channel)** | | |
| 131 | Peer manifest stored on the channel; no separate version field | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest); [protocol/channel-setup.md §6](../../protocol/channel-setup.md#6-shared-channel-state) |
| 132 | Peer manifest at completion: version rules and truncation | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest), [§5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 133 | Peer manifest refresh replaces it atomically | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 134 | Empty manifest does not block channel completion | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 135 | Supplemental off-chain endpoint discovery | specified | [protocol/endpoint-manifest.md §6](../../protocol/endpoint-manifest.md#6-endpoint-discovery) |
| | **[3. Verification Interfaces](../eap-v0.2-source/clpr-service-spec.md#3-verification-interfaces)** | | |
| 136 | CLPR is proof-system-agnostic; the Service does not interpret proofs | specified | [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| | **[3.1 Verifier Contract Interface](../eap-v0.2-source/clpr-service-spec.md#31-verifier-contract-interface)** | | |
| 137 | Every verifier implements two methods; ledgers define the ABI | specified | [protocol/verifier-interface.md](../../protocol/verifier-interface.md); [ledgers/evm/verifier-api.md §1–2](../../ledgers/evm/verifier-api.md#1-scope) |
| 138 | Verifier methods are read-only with respect to Service state | specified | [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors); [ledgers/evm/verifier-api.md §4](../../ledgers/evm/verifier-api.md#4-call-semantics) |
| 139 | `ChannelContext` structure | specified | [protocol/channel-setup.md §3](../../protocol/channel-setup.md#3-channel-context); [ledgers/evm/verifier-api.md §3.2](../../ledgers/evm/verifier-api.md#32-channelcontext) |
| 140 | Verifier binds the proof to the peer service address in the channel context | specified | [ledgers/besu/README.md §3.5](../../ledgers/besu/README.md#35-verifying-the-clpr-service-state); [ledgers/hiero/proof-schemes/hints-wraps.md §2](../../ledgers/hiero/proof-schemes/hints-wraps.md#2-trust-model) |
| 141 | `verifyConfig` signature and outputs | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [ledgers/evm/verifier-api.md §2](../../ledgers/evm/verifier-api.md#2-functions) |
| 142 | Manifest proof is verified against the initial trust anchor | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [protocol/endpoint-manifest.md §5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 143 | Channel context returned by `verifyConfig` and stored on the channel | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [protocol/channel-setup.md §3](../../protocol/channel-setup.md#3-channel-context) |
| 144 | Peer configuration timestamp output | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [ledgers/evm/verifier-api.md §2.1](../../ledgers/evm/verifier-api.md#21-verifyconfig), [§3.4](../../ledgers/evm/verifier-api.md#34-scalars-and-absent-values) |
| 145 | Peer throttles output, stored and enforced | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 146 | Initial trust anchor output | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig) |
| 147 | Initial trust anchor id output | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig), [§4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 148 | Endpoint manifest output of `verifyConfig` | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig) |
| 149 | `verifyConfig` rejection conditions | specified | [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig); [ledgers/evm/verifier-api.md §2.1](../../ledgers/evm/verifier-api.md#21-verifyconfig) |
| 150 | `verifyBundle` signature and outputs | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle); [protocol/bundle.md §1](../../protocol/bundle.md#1-bundle-content); [ledgers/evm/verifier-api.md §2.2](../../ledgers/evm/verifier-api.md#22-verifybundle), [§3.1](../../ledgers/evm/verifier-api.md#31-structures) |
| 151 | Verifier binds the bundle to the trust anchor and channel context | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle); [protocol/bundle.md §4](../../protocol/bundle.md#4-proof-requirements) |
| 152 | `trust_anchor` input of `verifyBundle` | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle) |
| 153 | Channel context input is the same on every call | specified | [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors); [protocol/channel-setup.md §3](../../protocol/channel-setup.md#3-channel-context) |
| 154 | Every queue metadata field comes from proven channel state | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle); [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 155 | `last_message_id` comes from the proven queue entry | specified | [protocol/bundle.md §1](../../protocol/bundle.md#1-bundle-content); [ledgers/besu/README.md §3.5](../../ledgers/besu/README.md#35-verifying-the-clpr-service-state); [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle), [§6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| 156 | `last_message_running_hash` comes from the proven queue entry | specified | [protocol/bundle.md §1](../../protocol/bundle.md#1-bundle-content) |
| 157 | `new_trust_anchor` output must be proven under the current anchor | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes); [ledgers/hiero/proof-schemes/hints-wraps.md §7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes) |
| 158 | `new_trust_anchor_id` is non-empty exactly when the new anchor is | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 159 | `new_endpoint_manifest` output | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle); [ledgers/evm/verifier-api.md §3.4](../../ledgers/evm/verifier-api.md#34-scalars-and-absent-values) |
| 160 | `verifyBundle` rejection conditions | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle) |
| 161 | Verifiers fail fast on malformed input | specified | [protocol/verifier-interface.md §3](../../protocol/verifier-interface.md#3-verifybundle) |
| | **[3.2 Endpoint Trust Anchor Rotation Obligations](../eap-v0.2-source/clpr-service-spec.md#32-endpoint-trust-anchor-rotation-obligations)** | | |
| 162 | Trust anchor obligations apply to endpoints; the Service enforces verifier output | specified | [protocol/endpoint-sync/README.md §5](../../protocol/endpoint-sync/README.md#5-endpoint-obligations) |
| | **[Per-channel obligation](../eap-v0.2-source/clpr-service-spec.md#per-channel-obligation)** | | |
| 163 | Endpoint keeps the peer's anchor current; requests report the anchor id | specified | [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| 164 | Trust anchor check by the endpoint in each sync cycle | specified | [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| 165 | Endpoint history of seen trust anchor ids | dropped: not implemented | Not implemented in v0.2 |
| 166 | Endpoint cache from anchor id to anchor bytes | dropped: not implemented | Not implemented in v0.2 |
| | **[Triggering](../eap-v0.2-source/clpr-service-spec.md#triggering)** | | |
| 167 | Triggers for a trust anchor transition | specified | [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| | **[Transition bundle](../eap-v0.2-source/clpr-service-spec.md#transition-bundle)** | | |
| 168 | Transition bundle definition | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes); [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up); [ledgers/besu/proof-schemes/qbft-epoch.md §7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes) |
| | **[Timing depends on trust anchor encoding](../eap-v0.2-source/clpr-service-spec.md#timing-depends-on-trust-anchor-encoding)** | | |
| 169 | No protocol deadline for anchor transitions | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 170 | Single-authority anchor encoding and its timing | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 171 | Window anchor encoding with current and next authorities | dropped: not implemented | Not implemented in v0.2; candidate for a later revision |
| | **[Proof system compatibility requirement](../eap-v0.2-source/clpr-service-spec.md#proof-system-compatibility-requirement)** | | |
| 172 | Proof systems must allow a proof that commits to the next authority | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| | **[Catch-up across multiple missed rotations](../eap-v0.2-source/clpr-service-spec.md#catch-up-across-multiple-missed-rotations)** | | |
| 173 | Catch-up across several missed anchor changes | specified | [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up); [ledgers/besu/proof-schemes/qbft-epoch.md §5](../../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm), [§7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes) |
| 174 | Several anchor changes may be batched in one payload | specified | [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| | **[3.3 Connector Authorization Interface](../eap-v0.2-source/clpr-service-spec.md#33-connector-authorization-interface)** | | |
| 175 | Connector authorization interface | specified | [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages); [ledgers/hiero/README.md §6.2](../../ledgers/hiero/README.md#62-connector-authorization); [ledgers/evm/README.md §3.2](../../ledgers/evm/README.md#32-connectors) |
| 176 | Authorization is a commitment that is the basis for slashing | specified | [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages); [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 177 | Authorization has no side effects on Service state | specified | [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages); [ledgers/hiero/README.md §6.2](../../ledgers/hiero/README.md#62-connector-authorization); [ledgers/evm/README.md §3.2](../../ledgers/evm/README.md#32-connectors) |
| 178 | `message_size` authorization parameter | dropped: not implemented | Not implemented in v0.2 |
| | **[3.4 Endpoint Close-Notification Obligation](../eap-v0.2-source/clpr-service-spec.md#34-endpoint-close-notification-obligation)** | | |
| 179 | Close notification bundle sent on reaching CLOSED | dropped: not implemented | Not implemented in v0.2; the specification states that there is no close notification |
| 180 | Close notification retry and administrator fallback | specified | [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining); [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel), [§7 R7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 181 | Peer handling of a close notification | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 182 | Peer already CLOSED: rejection confirms closure | specified | [protocol/endpoint-sync/README.md §5.3](../../protocol/endpoint-sync/README.md#53-channel-status); [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 183 | Close notification satisfies a progress criterion | specified | [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| | **[4.1 Running Hash Computation](../eap-v0.2-source/clpr-service-spec.md#41-running-hash-computation)** | | |
| 184 | Running hash formula over the serialized payload | specified | [protocol/messaging.md §3](../../protocol/messaging.md#3-payload-encoding), [§4](../../protocol/messaging.md#4-running-hash); [protocol/open-issues.md OI-1](../../protocol/open-issues.md#oi-1-message-encoding-in-the-running-hash) |
| 185 | Both running hashes start at 32 zero bytes | specified | [protocol/messaging.md §4](../../protocol/messaging.md#4-running-hash) |
| 186 | Hash algorithm rationale and upgrade path | archived | Rationale; archive only |
| | **[4.2 Bundle Verification Algorithm](../eap-v0.2-source/clpr-service-spec.md#42-bundle-verification-algorithm)** | | |
| 187 | Bundle processing: call `verifyBundle`; failure rejects the bundle | specified | [protocol/channel-state-transitions.md §2 Steps 1–2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 188 | Bundle processing: reject a bundle without progress | specified | [protocol/channel-state-transitions.md §2 Step 4](../../protocol/channel-state-transitions.md#2-bundle-processing), [§3](../../protocol/channel-state-transitions.md#3-progress) |
| 189 | Anchor-only and manifest-only bundles are valid | specified | [protocol/bundle.md §1](../../protocol/bundle.md#1-bundle-content); [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress) |
| 190 | Bundle processing: apply a newer peer manifest | specified | [protocol/channel-state-transitions.md §2 Step 5](../../protocol/channel-state-transitions.md#2-bundle-processing); [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 191 | Bundle processing: apply a new trust anchor before any message | specified | [protocol/channel-state-transitions.md §2 Step 5](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 192 | Bundle processing: message count and payload size limits | specified | [protocol/channel-state-transitions.md §2 Step 3](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 193 | Bundle processing: metadata next id bound | specified | [protocol/channel-state-transitions.md §2 Step 6](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 194 | Bundle processing: last message id bounds | specified | [protocol/channel-state-transitions.md §2 Step 6](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 195 | Bundle processing: no gap before the first message | specified | [protocol/channel-state-transitions.md §2 Step 6](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 196 | Bundle processing: contiguous ids; already received messages skipped | specified | [protocol/channel-state-transitions.md §2 Step 6](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 197 | Bundle processing: running hash check against the proven last hash | specified | [protocol/channel-state-transitions.md §2 Step 7](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 198 | Bundle processing: running hash check when all messages are skipped | specified | [protocol/channel-state-transitions.md §2 Step 7](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 199 | Bundle processing: running hash check for a bundle with no messages | specified | [protocol/channel-state-transitions.md §2 Step 7](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 200 | Bundle processing: acknowledgement bounds | specified | [protocol/channel-state-transitions.md §2 Step 8](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 201 | Bundle processing: apply acknowledgement and delete acknowledged entries | specified | [protocol/channel-state-transitions.md §2 Step 10](../../protocol/channel-state-transitions.md#2-bundle-processing); [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| 202 | Bundle processing: peer status moves the channel to CLOSING | specified | [protocol/channel-state-transitions.md §2 Step 14](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 203 | Bundle processing: lazy configuration update before dispatch | specified | [protocol/channel-state-transitions.md §2 Step 12](../../protocol/channel-state-transitions.md#2-bundle-processing); [protocol/ledger-configuration.md §5.2](../../protocol/ledger-configuration.md#52-sending) |
| 204 | Configuration updates carry throttles and protocol version only | specified | [protocol/ledger-configuration.md §5.1](../../protocol/ledger-configuration.md#51-configupdate), [§5.3](../../protocol/ledger-configuration.md#53-receiving) |
| 205 | Dispatch of control messages | specified | [protocol/channel-state-transitions.md §2 Dispatch](../../protocol/channel-state-transitions.md#2-bundle-processing); [protocol/ledger-configuration.md §5.3](../../protocol/ledger-configuration.md#53-receiving) |
| 206 | Dispatch of data messages and charging of the connector | specified | [protocol/messaging.md §6](../../protocol/messaging.md#6-delivery-to-the-application); [blueprint/channel-economics.md §1](../../blueprint/channel-economics.md#1-execution-charges), [§2](../../blueprint/channel-economics.md#2-payment-to-the-bundle-submitter) |
| 207 | Delivery of replies and charging | specified | [protocol/messaging.md §7](../../protocol/messaging.md#7-replies); [blueprint/channel-economics.md §1](../../blueprint/channel-economics.md#1-execution-charges) |
| 208 | One message's failure does not stop the rest | specified | [protocol/channel-state-transitions.md §2 Dispatch](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 209 | Bundle processing: CLOSING to DRAINED | specified | [protocol/channel-state-transitions.md §2 Step 14](../../protocol/channel-state-transitions.md#2-bundle-processing), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 210 | Bundle processing: DRAINED to CLOSED | specified | [protocol/channel-state-transitions.md §2 Step 14](../../protocol/channel-state-transitions.md#2-bundle-processing), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| | **[4.3 Message Enqueue Algorithm](../eap-v0.2-source/clpr-service-spec.md#43-message-enqueue-algorithm)** | | |
| 211 | Enqueue: channel must be ACTIVE | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 212 | Enqueue: lazy configuration update first | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue); [protocol/ledger-configuration.md §5.2](../../protocol/ledger-configuration.md#52-sending) |
| 213 | Enqueue: connector must exist | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 214 | Enqueue: connector must authorize | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue); [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages) |
| 215 | Enqueue: payload size limit of the destination | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 216 | Enqueue: queue depth limit | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue); [blueprint/channel-economics.md §3](../../blueprint/channel-economics.md#3-queue-quotas) |
| 217 | Enqueue: build message, update hash and counters | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue); [blueprint/clpr-service.md §1.4](../../blueprint/clpr-service.md#14-enqueue) |
| | **[4.4 Message Lifecycle](../eap-v0.2-source/clpr-service-spec.md#44-message-lifecycle)** | | |
| 218 | Replies are deleted when acknowledged | specified | [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| 219 | Control messages are deleted when acknowledged | specified | [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| 220 | Data messages are kept until their reply arrives | specified | [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| | **[4.5 Response Ordering Verification](../eap-v0.2-source/clpr-service-spec.md#45-response-ordering-verification)** | | |
| 221 | Response ordering: a reply must answer the oldest unanswered data message | specified | [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering) |
| 222 | Matched reply: deliver to the application and delete the entry | specified | [protocol/channel-state-transitions.md §2 Dispatch](../../protocol/channel-state-transitions.md#2-bundle-processing); [protocol/messaging.md §6](../../protocol/messaging.md#6-delivery-to-the-application) |
| 223 | Ordering violation: effects on the channel | specified | [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 224 | First reply must answer message 1 | specified | [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering); [blueprint/clpr-service.md §1.5](../../blueprint/clpr-service.md#15-reply-and-acknowledgement-bookkeeping) |
| 225 | Recovery from PAUSED | specified | [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 226 | Failed bundles change no state; PAUSED is only for ordering violations | specified | [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume); [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering) |
| | **[4.6 Slashing Decision](../eap-v0.2-source/clpr-service-spec.md#46-slashing-decision)** | | |
| 227 | Slashing is two-sided; each side compensates its own submitter | blueprint | [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 228 | Destination-side charges and penalties | blueprint | [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed); [blueprint/channel-economics.md §1](../../blueprint/channel-economics.md#1-execution-charges) |
| 229 | Source-side penalties by reply status | blueprint | [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed); [protocol/messaging.md §7](../../protocol/messaging.md#7-replies), [§10](../../protocol/messaging.md#10-redaction-deprecated) |
| 230 | Escalating penalties; ledgers define the slashing schedule | blueprint | [blueprint/stakes-and-bonds.md §2.2](../../blueprint/stakes-and-bonds.md#22-penalty); [blueprint/clpr-service.md §4.2](../../blueprint/clpr-service.md#42-service-parameters) |
| 231 | Stake must cover worst-case exposure; ledgers define the minimum stake | blueprint | [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake) |
| | **[5.1 Channel Registration](../eap-v0.2-source/clpr-service-spec.md#51-channel-registration)** | | |
| 232 | Channel creation is permissionless commit-reveal | merged | Same as row 82; [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| | **[5.1.1 Anti-Squatting Rationale](../eap-v0.2-source/clpr-service-spec.md#511-anti-squatting-rationale)** | | |
| 233 | Anti-squatting rationale | archived | Rationale; archive only |
| | **[5.1.2 Phase 1 — Claim (`registerChannel`)](../eap-v0.2-source/clpr-service-spec.md#512-phase-1--claim-registerchannel)** | | |
| 234 | Claim phase: registrant steps | specified | [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| 235 | Claim phase: Service steps | specified | [protocol/channel-setup.md §2.1](../../protocol/channel-setup.md#21-registerchannel) |
| | **[5.1.3 Phase 2 — Reveal (`completeChannel`)](../eap-v0.2-source/clpr-service-spec.md#513-phase-2--reveal-completechannel)** | | |
| 236 | Reveal phase: registrant steps and inputs | specified | [protocol/channel-setup.md §2.2](../../protocol/channel-setup.md#22-completechannel); [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures); [ledgers/evm/README.md §4–5](../../ledgers/evm/README.md#4-channel-identity) |
| 237 | Reveal phase: commitment and signature checks | specified | [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures); [ledgers/evm/README.md §5](../../ledgers/evm/README.md#5-registration-signatures) |
| 238 | Reveal phase: configuration is proven by `verifyConfig` | specified | [protocol/channel-setup.md §2.2](../../protocol/channel-setup.md#22-completechannel), [§5](../../protocol/channel-setup.md#5-initial-peer-state) |
| 239 | Reveal phase: store context, trust anchor and id | specified | [protocol/channel-setup.md §5](../../protocol/channel-setup.md#5-initial-peer-state); [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| 240 | Reveal phase: store the truncated peer manifest | specified | [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 241 | Reveal phase: channel becomes ACTIVE and the commitment is removed | specified | [protocol/channel-setup.md §2.2](../../protocol/channel-setup.md#22-completechannel); [blueprint/clpr-service.md §1.1](../../blueprint/clpr-service.md#11-channel-record) |
| 242 | A PENDING channel cannot message, submit bundles or sync | merged | Same as row 103; [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status); [protocol/endpoint-sync/README.md §5.3](../../protocol/endpoint-sync/README.md#53-channel-status) |
| | **[5.1.4 Admin Cleanup](../eap-v0.2-source/clpr-service-spec.md#514-admin-cleanup)** | | |
| 243 | Administrator cleanup of PENDING channels | merged | Same as row 248; [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| | **[5.1.5 Verifier Immutability](../eap-v0.2-source/clpr-service-spec.md#515-verifier-immutability)** | | |
| 244 | Verifier is fixed at registration | specified | [protocol/channel-setup.md §4](../../protocol/channel-setup.md#4-verifier-binding) |
| | **[5.2 Endpoint Discovery](../eap-v0.2-source/clpr-service-spec.md#52-endpoint-discovery)** | | |
| 245 | Local manifest is authoritative; two-step or automatic admission | merged | Same as row 127; [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest); [blueprint/clpr-service.md §3](../../blueprint/clpr-service.md#3-endpoint-admission) |
| 246 | Peer manifest version propagation and public manifest query | specified | [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest), [§5](../../protocol/endpoint-manifest.md#5-manifest-proofs); [protocol/endpoint-sync/README.md §5.2](../../protocol/endpoint-sync/README.md#52-endpoint-manifest) |
| 247 | Endpoints prefer peers that reciprocate | blueprint | [blueprint/clpr-service.md §5.3](../../blueprint/clpr-service.md#53-peer-selection) |
| | **[5.3 Administrative Operations](../eap-v0.2-source/clpr-service-spec.md#53-administrative-operations)** | | |
| 248 | Administrator close: valid states and effects | blueprint | [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 249 | Administrator updates the local configuration; propagated lazily | blueprint | [blueprint/clpr-service.md §2.4](../../blueprint/clpr-service.md#24-configuration-updates); [protocol/ledger-configuration.md §5](../../protocol/ledger-configuration.md#5-configuration-propagation) |
| | **[6. Pseudo-API Reference](../eap-v0.2-source/clpr-service-spec.md#6-pseudo-api-reference)** | | |
| 250 | Required pseudo-API operations; authenticated callers | blueprint | [blueprint/clpr-service.md §2.2](../../blueprint/clpr-service.md#22-operations) |
| | **[6.1 Configuration Management](../eap-v0.2-source/clpr-service-spec.md#61-configuration-management)** | | |
| 251 | `setLedgerConfiguration` operation | blueprint | [blueprint/clpr-service.md §2.4](../../blueprint/clpr-service.md#24-configuration-updates) |
| 252 | `getLedgerConfiguration` operation | blueprint | [blueprint/clpr-service.md §2.7](../../blueprint/clpr-service.md#27-queries) |
| | **[6.2 Channel Management](../eap-v0.2-source/clpr-service-spec.md#62-channel-management)** | | |
| 253 | `registerChannel` operation | merged | Same as row 235; [protocol/channel-setup.md §2.1](../../protocol/channel-setup.md#21-registerchannel) |
| 254 | `completeChannel` operation | specified | [protocol/channel-setup.md §2.2](../../protocol/channel-setup.md#22-completechannel); [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors); [protocol/endpoint-manifest.md §5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 255 | `closeChannel` operation | blueprint | [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 256 | Queue-depth query | blueprint | [blueprint/clpr-service.md §2.7](../../blueprint/clpr-service.md#27-queries) |
| | **[6.3 Connector Management](../eap-v0.2-source/clpr-service-spec.md#63-connector-management)** | | |
| 257 | Connector registration is commit-reveal; same id on every ledger | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity), [§2](../../protocol/connector-setup.md#2-registration) |
| 258 | `registerConnector` operation | specified | [protocol/connector-setup.md §2](../../protocol/connector-setup.md#2-registration) |
| 259 | `completeConnector` operation | specified | [protocol/connector-setup.md §2](../../protocol/connector-setup.md#2-registration); [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake) |
| 260 | `topUpConnector` operation | blueprint | [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake); [blueprint/clpr-service.md §2.2](../../blueprint/clpr-service.md#22-operations) |
| 261 | `withdrawConnectorBalance` operation | dropped: not implemented | Not implemented in v0.2; connectors hold no separate balance |
| 262 | `removeConnector` operation and in-flight rule | specified | [protocol/connector-setup.md §5](../../protocol/connector-setup.md#5-removal); [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake) |
| 263 | `getConnector` query | blueprint | [blueprint/clpr-service.md §2.7](../../blueprint/clpr-service.md#27-queries) |
| 264 | `deriveConnectorId` helper | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity); [blueprint/clpr-service.md §2.7](../../blueprint/clpr-service.md#27-queries) |
| 265 | Hiero connector completion signature over the built-in service address | specified | [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures) |
| | **[6.4 Messaging](../eap-v0.2-source/clpr-service-spec.md#64-messaging)** | | |
| 266 | `sendMessage` operation | specified | [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 267 | `submitBundle` operation | blueprint | [blueprint/clpr-service.md §5.1](../../blueprint/clpr-service.md#51-who-submits); [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 268 | Deprecated `redactMessage` operation | specified | [protocol/messaging.md §10](../../protocol/messaging.md#10-redaction-deprecated); [blueprint/clpr-service.md §2.6](../../blueprint/clpr-service.md#26-redaction) |
| | **[6.5 Endpoint Management](../eap-v0.2-source/clpr-service-spec.md#65-endpoint-management)** | | |
| 269 | Endpoint-management operations on permissionless ledgers | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission), [§3.3](../../blueprint/clpr-service.md#33-roster-derived-manifest) |
| 270 | Optional endpoint certificate validation | specified | [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint); [ledgers/evm/README.md §6](../../ledgers/evm/README.md#6-endpoint-certificates); [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission) |
| 271 | Admitted endpoints serve all channels; endpoint bond is never slashed | blueprint | [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond); [blueprint/clpr-service.md §3.1](../../blueprint/clpr-service.md#31-common-rules) |
| 272 | `registerEndpoint` operation | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission); [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond) |
| 273 | `addEndpoint` operation | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission) |
| 274 | `removeEndpoint` operation | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission); [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond) |
| 275 | `updateEndpointManifest` operation | blueprint | [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission) |
| 276 | `getEndpointManifest` operation | specified | [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest); [blueprint/clpr-service.md §2.7](../../blueprint/clpr-service.md#27-queries) |
| | **[Application Delivery](../eap-v0.2-source/clpr-service-spec.md#application-delivery)** | | |
| 277 | Application delivery is ledger-specific; ledgers define callbacks and gas | specified | [protocol/messaging.md §6](../../protocol/messaging.md#6-delivery-to-the-application); [ledgers/evm/README.md §3](../../ledgers/evm/README.md#3-application-and-connector-interfaces); [ledgers/hiero/README.md §6](../../ledgers/hiero/README.md#6-application-and-connector-interfaces) |
| | **[6.6 Misbehavior Detection](../eap-v0.2-source/clpr-service-spec.md#66-misbehavior-detection)** | | |
| 278 | Misbehavior detection is local only | merged | Same as row 78; [protocol/endpoint-sync/README.md §6](../../protocol/endpoint-sync/README.md#6-misbehavior) |
| | **[7. Configuration Parameters](../eap-v0.2-source/clpr-service-spec.md#7-configuration-parameters)** | | |
| 279 | Service enable flag (kill switch) | blueprint | [blueprint/clpr-service.md §2.3](../../blueprint/clpr-service.md#23-initialization-and-kill-switch), [§4.2](../../blueprint/clpr-service.md#42-service-parameters) |
| 280 | Queue depth parameter | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [blueprint/clpr-service.md §4.1](../../blueprint/clpr-service.md#41-throttles) |
| 281 | Message payload size parameter | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [blueprint/clpr-service.md §4.1](../../blueprint/clpr-service.md#41-throttles) |
| 282 | Messages-per-bundle parameter sized to ledger limits | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [blueprint/clpr-service.md §4.1](../../blueprint/clpr-service.md#41-throttles) |
| 283 | Gas-per-message parameter | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [blueprint/clpr-service.md §4.1](../../blueprint/clpr-service.md#41-throttles) |
| 284 | Sync size parameter | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/channel-state-transitions.md §2 Step 1](../../protocol/channel-state-transitions.md#2-bundle-processing); [blueprint/clpr-service.md §4.1](../../blueprint/clpr-service.md#41-throttles) |
| 285 | Per-channel enforcement of published throttles | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| | **[8.1 Protocol Strictness](../eap-v0.2-source/clpr-service-spec.md#81-protocol-strictness)** | | |
| 286 | Protocol strictness: receivers reject limit violations | specified | [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/endpoint-sync/README.md §6](../../protocol/endpoint-sync/README.md#6-misbehavior) |
| 287 | Unknown fields, types or malformed metadata are rejected; deprecated items are recognized | specified | [protocol/conventions.md §3](../../protocol/conventions.md#3-abstract-data-structures) |
| | **[8.2 Trust Model](../eap-v0.2-source/clpr-service-spec.md#82-trust-model)** | | |
| 288 | Trust model: verifier, peer proofs and both Services | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model); [blueprint/clpr-service.md §6.1](../../blueprint/clpr-service.md#61-verifier-choice) |
| | **[8.3 Reorg Risk](../eap-v0.2-source/clpr-service-spec.md#83-reorg-risk)** | | |
| 289 | Reorganization risk and finality choice | blueprint | [blueprint/clpr-service.md §6.2](../../blueprint/clpr-service.md#62-finality) |
| | **[8.4 Endpoint Sybil Resistance](../eap-v0.2-source/clpr-service-spec.md#84-endpoint-sybil-resistance)** | | |
| 290 | Endpoint Sybil resistance by administrator curation and bond | blueprint | [blueprint/clpr-service.md §6.3](../../blueprint/clpr-service.md#63-endpoint-admission) |
| | **[8.5 Reentrancy](../eap-v0.2-source/clpr-service-spec.md#85-reentrancy)** | | |
| 291 | Guard state-modifying functions against reentrancy | blueprint | [blueprint/clpr-service.md §6.4](../../blueprint/clpr-service.md#64-reentrancy-and-external-calls) |
| | **[8.6 Untrusted Payloads](../eap-v0.2-source/clpr-service-spec.md#86-untrusted-payloads)** | | |
| 292 | Applications treat payloads as untrusted | blueprint | [blueprint/clpr-service.md §6.5](../../blueprint/clpr-service.md#65-application-payloads); [protocol/messaging.md §6](../../protocol/messaging.md#6-delivery-to-the-application) |
| | **[8.7 No Confidentiality](../eap-v0.2-source/clpr-service-spec.md#87-no-confidentiality)** | | |
| 293 | No confidentiality; applications encrypt | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model); [blueprint/clpr-service.md §6.5](../../blueprint/clpr-service.md#65-application-payloads) |
| | **[8.8 Upgradeable Verifier Contracts](../eap-v0.2-source/clpr-service-spec.md#88-upgradeable-verifier-contracts)** | | |
| 294 | Upgradeable verifier contracts | blueprint | [blueprint/clpr-service.md §6.1](../../blueprint/clpr-service.md#61-verifier-choice) |
| | **[8.9 Upgradeable CLPR Service Contracts](../eap-v0.2-source/clpr-service-spec.md#89-upgradeable-clpr-service-contracts)** | | |
| 295 | Upgradeable Service contracts: storage-layout coordination | blueprint | [blueprint/clpr-service.md §6.6](../../blueprint/clpr-service.md#66-service-upgrades) |
| | **[8.10 Endpoint Pre-Funding](../eap-v0.2-source/clpr-service-spec.md#810-endpoint-pre-funding)** | | |
| 296 | Endpoint operators pre-fund submission accounts | blueprint | [blueprint/clpr-service.md §5.1](../../blueprint/clpr-service.md#51-who-submits) |
| | **[8.11 Queue Monopolization](../eap-v0.2-source/clpr-service-spec.md#811-queue-monopolization)** | | |
| 297 | Queue monopolization and its mitigations | blueprint | [blueprint/channel-economics.md §3](../../blueprint/channel-economics.md#3-queue-quotas); [blueprint/clpr-service.md §6.7](../../blueprint/clpr-service.md#67-queue-monopolization) |
| | **[9. Recovery Scenarios](../eap-v0.2-source/clpr-service-spec.md#9-recovery-scenarios)** | | |
| 298 | Recovery: endpoints changed during a partition | blueprint | [blueprint/clpr-service.md §7 R1](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 299 | Recovery: proof format upgrade | blueprint | [blueprint/clpr-service.md §7 R2](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 300 | Recovery: endpoints changed, format unchanged | blueprint | [blueprint/clpr-service.md §7 R1](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 301 | Recovery: endpoints and format changed | blueprint | [blueprint/clpr-service.md §7 R3](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 302 | Recovery: verifier compromised | blueprint | [blueprint/clpr-service.md §7 R4](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 303 | Recovery: peer queue corrupted | blueprint | [blueprint/clpr-service.md §7 R5](../../blueprint/clpr-service.md#7-recovery-scenarios); [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 304 | Recovery: network partition | blueprint | [blueprint/clpr-service.md §7 R6](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 305 | Recovery: peer ledger down | blueprint | [blueprint/clpr-service.md §7 R6](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 306 | Recovery: endpoints of both sides changed | blueprint | [blueprint/clpr-service.md §7 R1](../../blueprint/clpr-service.md#7-recovery-scenarios) |

## `clpr-service.md`

| # | Item | Status | Location in v0.2 |
|---|---|---|---|
| | **[1. Executive Summary](../eap-v0.2-source/clpr-service.md#1-executive-summary)** | | |
| 1 | CLPR purpose: asynchronous messaging on native finality and state proofs | overview | [clpr-overview.md §1](../../clpr-overview.md#1-purpose) |
| 2 | Arbitrary payloads; one honest endpoint per ledger suffices | overview | [clpr-overview.md §1](../../clpr-overview.md#1-purpose), [§4](../../clpr-overview.md#4-trust-model) |
| 3 | No new token; incentives through connectors | overview | [clpr-overview.md §1](../../clpr-overview.md#1-purpose) |
| | **[Why CLPR](../eap-v0.2-source/clpr-service.md#why-clpr)** | | |
| 4 | Motivation bullets | archived | Motivational text; archive only |
| | **[2. Core Concepts and Terminology](../eap-v0.2-source/clpr-service.md#2-core-concepts-and-terminology)** | | |
| 5 | Ledgers communicate directly; users trust only the two ledgers | overview | [clpr-overview.md §1](../../clpr-overview.md#1-purpose), [§4](../../clpr-overview.md#4-trust-model) |
| 6 | Naming note for the ledger family | removed: reference only | Naming note only |
| | **[2.1 Common Terminology](../eap-v0.2-source/clpr-service.md#21-common-terminology)** | | |
| 7 | Glossary of terms | overview | [clpr-overview.md §7](../../clpr-overview.md#7-vocabulary) |
| | **[2.2 High-Level Message Flow](../eap-v0.2-source/clpr-service.md#22-high-level-message-flow)** | | |
| 8 | High-level message flow | overview | [clpr-overview.md §3](../../clpr-overview.md#3-message-flow) |
| | **[2.3 Trust Model](../eap-v0.2-source/clpr-service.md#23-trust-model)** | | |
| 9 | Trust chain from local consensus to remote application | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model) |
| 10 | Permissionless channels: trust depends on the verifier | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model) |
| 11 | Connectors cannot forge messages but may refuse to pay | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model) |
| 12 | Availability needs one honest endpoint per side | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model) |
| | **[2.4 Participant Roles](../eap-v0.2-source/clpr-service.md#24-participant-roles)** | | |
| 13 | Participant roles and the vetting chain | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[Trust Chain](../eap-v0.2-source/clpr-service.md#trust-chain)** | | |
| 14 | Infrastructure roles: Service administrator and endpoint operator | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| 15 | Economic exposure drives vetting | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[Role Summary](../eap-v0.2-source/clpr-service.md#role-summary)** | | |
| 16 | Role summary table | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[Role Descriptions](../eap-v0.2-source/clpr-service.md#role-descriptions)** | | |
| 17 | Role descriptions per ledger | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[3. Architecture](../eap-v0.2-source/clpr-service.md#3-architecture)** | | |
| 18 | Four architectural layers | overview | [clpr-overview.md §2](../../clpr-overview.md#2-major-parts) |
| 19 | Network layer: gRPC, protobuf, verifier contracts | overview | [clpr-overview.md §2](../../clpr-overview.md#2-major-parts) |
| 20 | Note on an encoding-format review | archived | Superseded note; the encoding question is open issue OI-1 |
| | **[3.1.0 The CLPR Service](../eap-v0.2-source/clpr-service.md#310-the-clpr-service)** | | |
| 21 | The CLPR Service holds all CLPR state and logic | overview | [clpr-overview.md §2](../../clpr-overview.md#2-major-parts) |
| 22 | State owned by the Service | merged | Same as `clpr-service-spec.md` row 79; [blueprint/clpr-service.md §1](../../blueprint/clpr-service.md#1-structure-and-internal-state) |
| 23 | Provable state on Hiero and on EVM ledgers | specified | [ledgers/hiero/README.md §4](../../ledgers/hiero/README.md#4-proof-schemes); [ledgers/besu/README.md §3.4](../../ledgers/besu/README.md#34-proof-encoding) |
| | **[3.1.1 Ledger Identity and Configuration](../eap-v0.2-source/clpr-service.md#311-ledger-identity-and-configuration)** | | |
| 24 | Configuration fields | merged | Same as `clpr-service-spec.md` row 11; [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration) |
| 25 | Only the Service administrator updates the local configuration | merged | Same as `clpr-service-spec.md` row 251; [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration); [blueprint/clpr-service.md §2.4](../../blueprint/clpr-service.md#24-configuration-updates) |
| 26 | Chain id format; a peer is identified by chain id and service address | specified | [protocol/ledger-configuration.md §1](../../protocol/ledger-configuration.md#1-ledger-identity) |
| 27 | Chain id examples | specified | [protocol/conventions.md §5](../../protocol/conventions.md#5-identifiers) |
| 28 | Registered CAIP-2 namespaces for public networks | specified | [protocol/ledger-configuration.md §1](../../protocol/ledger-configuration.md#1-ledger-identity) |
| 29 | Anyone can claim a chain id; applications verify the channel | specified | [protocol/ledger-configuration.md §1](../../protocol/ledger-configuration.md#1-ledger-identity) |
| 30 | Protocol version rules | merged | Same as `clpr-service-spec.md` row 12; [protocol/ledger-configuration.md §4](../../protocol/ledger-configuration.md#4-protocol-version); [protocol/open-issues.md OI-8](../../protocol/open-issues.md#oi-8-protocol-version-at-channel-setup) |
| 31 | A new protocol version propagates by configuration update | specified | [protocol/ledger-configuration.md §4](../../protocol/ledger-configuration.md#4-protocol-version) |
| 32 | Configuration timestamp is consensus time and monotonic | merged | Same as `clpr-service-spec.md` row 15; [protocol/ledger-configuration.md §2](../../protocol/ledger-configuration.md#2-ledger-configuration) |
| 33 | Messages-per-bundle throttle | merged | Same as `clpr-service-spec.md` row 24; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 34 | Message payload size throttle | merged | Same as `clpr-service-spec.md` row 25; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 35 | Gas-per-message throttle | merged | Same as `clpr-service-spec.md` row 26; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 36 | Sync size throttle and its lower bound | merged | Same as `clpr-service-spec.md` row 28; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 37 | Queue depth throttle | merged | Same as `clpr-service-spec.md` row 27; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles) |
| 38 | Local endpoints throttle | merged | Same as `clpr-service-spec.md` row 30; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest) |
| 39 | Peer endpoints throttle | merged | Same as `clpr-service-spec.md` row 31; [protocol/ledger-configuration.md §3](../../protocol/ledger-configuration.md#3-throttles); [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 40 | Strictness: reject violations and unknown data | merged | Same as `clpr-service-spec.md` row 287; [protocol/conventions.md §3](../../protocol/conventions.md#3-abstract-data-structures) |
| | **[3.1.2 Endpoint Manifest](../eap-v0.2-source/clpr-service.md#312-endpoint-manifest)** | | |
| 41 | Manifest version and service address | merged | Same as `clpr-service-spec.md` row 37; [protocol/endpoint-manifest.md §2](../../protocol/endpoint-manifest.md#2-endpoint-manifest), [§5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 42 | An endpoint has an optional service endpoint | merged | Same as `clpr-service-spec.md` row 32; [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint) |
| 43 | Local manifest admission and endpoint bond | merged | Same as `clpr-service-spec.md` row 245; [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest); [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond) |
| 44 | Peer manifest per channel | merged | Same as `clpr-service-spec.md` row 131; [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 45 | Public manifest query and proof construction | merged | Same as `clpr-service-spec.md` row 246; [protocol/endpoint-manifest.md §3](../../protocol/endpoint-manifest.md#3-local-manifest), [§5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 46 | Channel creation with a manifest proof | merged | Same as `clpr-service-spec.md` row 132; [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest), [§5](../../protocol/endpoint-manifest.md#5-manifest-proofs) |
| 47 | Manifest update propagation | merged | Same as `clpr-service-spec.md` row 133; [protocol/endpoint-manifest.md §4](../../protocol/endpoint-manifest.md#4-peer-manifest) |
| 48 | Supplemental discovery protocols | merged | Same as `clpr-service-spec.md` row 135; [protocol/endpoint-manifest.md §6](../../protocol/endpoint-manifest.md#6-endpoint-discovery) |
| 49 | Endpoint reciprocity | merged | Same as `clpr-service-spec.md` row 247; [blueprint/clpr-service.md §5.3](../../blueprint/clpr-service.md#53-peer-selection) |
| 50 | Hiero manifest derived from the consensus roster | blueprint | [blueprint/clpr-service.md §3.3](../../blueprint/clpr-service.md#33-roster-derived-manifest) |
| 51 | Endpoint registration with bond on EVM ledgers | merged | Same as `clpr-service-spec.md` row 272; [blueprint/clpr-service.md §3.2](../../blueprint/clpr-service.md#32-registration-and-admission); [blueprint/stakes-and-bonds.md §3](../../blueprint/stakes-and-bonds.md#3-endpoint-bond) |
| 52 | Endpoint Sybil resistance | merged | Same as `clpr-service-spec.md` row 290; [blueprint/clpr-service.md §6.3](../../blueprint/clpr-service.md#63-endpoint-admission) |
| | **[3.1.3 Establishing and Updating Channels](../eap-v0.2-source/clpr-service.md#313-establishing-and-updating-channels)** | | |
| 53 | Channel creation summary | merged | Same as `clpr-service-spec.md` row 232; [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| 54 | Registration sequence diagram | merged | Same as `clpr-service-spec.md` row 234; [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| 55 | Channel id, commitment and signature scheme | merged | Same as `clpr-service-spec.md` row 81; [protocol/channel-setup.md §1](../../protocol/channel-setup.md#1-channel-identity), [§2](../../protocol/channel-setup.md#2-registration); [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures) |
| 56 | Anti-squatting | merged | Same as `clpr-service-spec.md` row 233; [protocol/channel-setup.md §2](../../protocol/channel-setup.md#2-registration) |
| 57 | Claim and reveal narrative | merged | Same as `clpr-service-spec.md` row 236; [protocol/channel-setup.md §2.2](../../protocol/channel-setup.md#22-completechannel), [§4](../../protocol/channel-setup.md#4-verifier-binding); [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures) |
| 58 | Future post-quantum commitment hash | archived | Future design note; archive only |
| 59 | Later peer configuration changes travel by configuration update | merged | Same as `clpr-service-spec.md` row 249; [protocol/ledger-configuration.md §5](../../protocol/ledger-configuration.md#5-configuration-propagation) |
| 60 | Several channels to the same peer | specified | [protocol/channel-setup.md §1](../../protocol/channel-setup.md#1-channel-identity) |
| 61 | PENDING status description | merged | Same as `clpr-service-spec.md` row 103; [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status) |
| 62 | ACTIVE status description | merged | Same as `clpr-service-spec.md` row 104; [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status), [§4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 63 | PAUSED status description | merged | Same as `clpr-service-spec.md` row 105; [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| 64 | CLOSING status description | merged | Same as `clpr-service-spec.md` row 106; [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining); [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 65 | DRAINED status description | merged | Same as `clpr-service-spec.md` row 107; [protocol/channel-state-transitions.md §5](../../protocol/channel-state-transitions.md#5-closing-and-draining); [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 66 | CLOSED status description | merged | Same as `clpr-service-spec.md` row 108; [protocol/channel-state-transitions.md §1](../../protocol/channel-state-transitions.md#1-channel-status), [§5](../../protocol/channel-state-transitions.md#5-closing-and-draining) |
| 67 | Status transition table | merged | Same as `clpr-service-spec.md` row 93; [protocol/channel-state-transitions.md §4](../../protocol/channel-state-transitions.md#4-status-transitions) |
| 68 | Only the Service administrator closes channels | merged | Same as `clpr-service-spec.md` row 248; [blueprint/clpr-service.md §2.5](../../blueprint/clpr-service.md#25-closing-a-channel) |
| 69 | Verifier immutability | merged | Same as `clpr-service-spec.md` row 244; [protocol/channel-setup.md §4](../../protocol/channel-setup.md#4-verifier-binding) |
| | **[3.1.4 Endpoint Communication Protocol](../eap-v0.2-source/clpr-service.md#314-endpoint-communication-protocol)** | | |
| 70 | Endpoint runs a gRPC server; sync cycle per channel | merged | Same as `clpr-service-spec.md` row 55; [protocol/endpoint-sync/README.md §1](../../protocol/endpoint-sync/README.md#1-purpose-and-roles) |
| 71 | Transport rules: single port, TLS, no client certificate | merged | Same as `clpr-service-spec.md` row 73; [protocol/endpoint-sync/README.md §2](../../protocol/endpoint-sync/README.md#2-transport) |
| 72 | Sync cycle steps | merged | Same as `clpr-service-spec.md` row 77; [protocol/endpoint-sync/README.md §3](../../protocol/endpoint-sync/README.md#3-exchange) |
| 73 | Bundle requests are unproven | merged | Same as `clpr-service-spec.md` row 58; [protocol/endpoint-sync/README.md §3](../../protocol/endpoint-sync/README.md#3-exchange) |
| 74 | Bundle responses are verified locally before submission | merged | Same as `clpr-service-spec.md` row 55; [protocol/endpoint-sync/README.md §1](../../protocol/endpoint-sync/README.md#1-purpose-and-roles) |
| 75 | Proof bytes are opaque | merged | Same as `clpr-service-spec.md` row 136; [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| 76 | Endpoints verify bundles locally before submitting | blueprint | [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| 77 | Bundle response content: proof, proven queue metadata and messages | merged | Same as `clpr-service-spec.md` row 62; [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 78 | Queue metadata carries acknowledgements | merged | Same as `clpr-service-spec.md` row 63; [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 79 | Two-phase sync sequence diagram | merged | Same as `clpr-service-spec.md` row 77; [protocol/endpoint-sync/README.md §3](../../protocol/endpoint-sync/README.md#3-exchange) |
| 80 | Private networks omit service endpoints and initiate sync | merged | Same as `clpr-service-spec.md` row 32; [protocol/endpoint-manifest.md §1](../../protocol/endpoint-manifest.md#1-endpoint) |
| | **[3.1.5 Verifier Contracts](../eap-v0.2-source/clpr-service.md#315-verifier-contracts)** | | |
| 81 | Verifier as a contract or a built-in | specified | [protocol/channel-setup.md §4](../../protocol/channel-setup.md#4-verifier-binding); [ledgers/hiero/README.md §3](../../ledgers/hiero/README.md#3-built-in-verifiers); [ledgers/evm/verifier-api.md §1](../../ledgers/evm/verifier-api.md#1-scope) |
| 82 | `verifyConfig` description | merged | Same as `clpr-service-spec.md` row 141; [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig) |
| 83 | `verifyBundle` description with an earlier output list | archived | Superseded interface description; archive only |
| 84 | Verifier internals are its own concern | merged | Same as `clpr-service-spec.md` row 138; [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| 85 | Trust anchor is opaque and changes only through `verifyBundle` | merged | Same as `clpr-service-spec.md` row 86; [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| 86 | Service never inspects the trust anchor | merged | Same as `clpr-service-spec.md` row 136; [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| 87 | Empty trust anchor | merged | Same as `clpr-service-spec.md` row 86; [protocol/verifier-interface.md §2](../../protocol/verifier-interface.md#2-verifyconfig) |
| 88 | Anchor changes travel in the bundle proof, not the queue | merged | Same as `clpr-service-spec.md` row 168; [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 89 | Endpoint trust anchor loop | merged | Same as `clpr-service-spec.md` row 164; [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| 90 | Endpoint history of seen trust anchor ids | merged | Same as `clpr-service-spec.md` row 165 (not implemented) |
| 91 | Endpoint cache from anchor id to anchor bytes | merged | Same as `clpr-service-spec.md` row 166 (not implemented) |
| 92 | Triggers for anchor transitions | merged | Same as `clpr-service-spec.md` row 167; [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| 93 | Transition bundle construction | merged | Same as `clpr-service-spec.md` row 168; [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 94 | Single-authority and window encodings | merged | Same as `clpr-service-spec.md` row 170; [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 95 | Window encoding for frequent rotations | merged | Same as `clpr-service-spec.md` row 171 (not implemented) |
| 96 | Catch-up and batching of anchor changes | merged | Same as `clpr-service-spec.md` row 173; [protocol/endpoint-sync/README.md §5.1](../../protocol/endpoint-sync/README.md#51-trust-anchor-catch-up) |
| 97 | A new anchor must be committed in the proof verified under the current anchor | merged | Same as `clpr-service-spec.md` row 157; [protocol/verifier-interface.md §4](../../protocol/verifier-interface.md#4-trust-anchor-changes) |
| 98 | Anchor-only bundles are valid | merged | Same as `clpr-service-spec.md` row 189; [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress); [protocol/bundle.md §1](../../protocol/bundle.md#1-bundle-content) |
| 99 | Hiero trust anchor is the ledger id | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes); [ledgers/hiero/README.md §3](../../ledgers/hiero/README.md#3-built-in-verifiers) |
| 100 | Trust anchor of a ledger outside the v0.2 scope | archived | Ledger outside the v0.2 scope; archive only |
| 101 | QBFT trust anchor derived from the validator set | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes); [ledgers/besu/proof-schemes/qbft-header.md §7](../../ledgers/besu/proof-schemes/qbft-header.md#7-trust-anchor-changes); [ledgers/besu/proof-schemes/qbft-contract.md §7](../../ledgers/besu/proof-schemes/qbft-contract.md#7-trust-anchor-changes) |
| 102 | CLPR trusts verifier output | overview | [clpr-overview.md §4](../../clpr-overview.md#4-trust-model) |
| 103 | Finality and reorganization | merged | Same as `clpr-service-spec.md` row 289; [blueprint/clpr-service.md §6.2](../../blueprint/clpr-service.md#62-finality) |
| 104 | Adding a ledger | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles), [§6](../../clpr-overview.md#6-how-the-specification-is-organized) |
| 105 | Verifier examples per proof scheme | specified | [ledgers/README.md](../../ledgers/README.md) |
| 106 | Upgradeable verifier proxies | merged | Same as `clpr-service-spec.md` row 294; [blueprint/clpr-service.md §6.1](../../blueprint/clpr-service.md#61-verifier-choice) |
| 107 | Ledger-specific verifier documents are out of scope | archived | Statement about the earlier document structure; archive only |
| | **[3.1.6 Misbehavior Detection](../eap-v0.2-source/clpr-service.md#316-misbehavior-detection)** | | |
| 108 | Misbehavior detection is local only | merged | Same as `clpr-service-spec.md` row 78; [protocol/endpoint-sync/README.md §6](../../protocol/endpoint-sync/README.md#6-misbehavior) |
| | **[3.2 Messaging Layer](../eap-v0.2-source/clpr-service.md#32-messaging-layer)** | | |
| 109 | Three message classes share one queue per channel | merged | Same as `clpr-service-spec.md` row 40; [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types), [§2](../../protocol/messaging.md#2-message-identifiers-and-queue) |
| | **[3.2.1 Channel Queue Data](../eap-v0.2-source/clpr-service.md#321-channel-queue-data)** | | |
| 110 | Channel queue data | merged | Same as `clpr-service-spec.md` row 84; [protocol/channel-setup.md §6](../../protocol/channel-setup.md#6-shared-channel-state); [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue) |
| 111 | In-flight window bounded by queue depth | merged | Same as `clpr-service-spec.md` row 216; [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| | **[3.2.2 Message Storage](../eap-v0.2-source/clpr-service.md#322-message-storage)** | | |
| 112 | Queue key description | archived | Superseded wording; archive only |
| 113 | One intermixed stream with a shared hash chain | merged | Same as `clpr-service-spec.md` row 47; [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types), [§2](../../protocol/messaging.md#2-message-identifiers-and-queue) |
| 114 | Running hash formula | merged | Same as `clpr-service-spec.md` row 184; [protocol/messaging.md §4](../../protocol/messaging.md#4-running-hash); [protocol/open-issues.md OI-1](../../protocol/open-issues.md#oi-1-message-encoding-in-the-running-hash) |
| 115 | Queued entry: payload and running hash | merged | Same as `clpr-service-spec.md` row 46; [protocol/messaging.md §2](../../protocol/messaging.md#2-message-identifiers-and-queue) |
| 116 | Eager configuration-update description | archived | Superseded by lazy configuration updates; archive only |
| 117 | Unknown control type rejects the bundle | merged | Same as `clpr-service-spec.md` row 41; [protocol/messaging.md §1](../../protocol/messaging.md#1-message-types); [protocol/ledger-configuration.md §4](../../protocol/ledger-configuration.md#4-protocol-version) |
| 118 | Last message hash must match the proven value | merged | Same as `clpr-service-spec.md` row 197; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 119 | Queue storage on Hiero and EVM ledgers | merged | Same as `clpr-service-spec.md` row 92; [blueprint/clpr-service.md §1](../../blueprint/clpr-service.md#1-structure-and-internal-state), [§1.2](../../blueprint/clpr-service.md#12-message-queue) |
| | **[3.2.3 Bundle Transport](../eap-v0.2-source/clpr-service.md#323-bundle-transport)** | | |
| 120 | Bundle definition | overview | [clpr-overview.md §2](../../clpr-overview.md#2-major-parts) |
| 121 | Bundle start rule | merged | Same as `clpr-service-spec.md` row 66; [protocol/endpoint-sync/README.md §4](../../protocol/endpoint-sync/README.md#4-message-range) |
| 122 | Bundle size limited by the peer's throttles | merged | Same as `clpr-service-spec.md` row 66; [protocol/endpoint-sync/README.md §4](../../protocol/endpoint-sync/README.md#4-message-range) |
| 123 | Received bundle is submitted as a transaction | merged | Same as `clpr-service-spec.md` row 267; [blueprint/clpr-service.md §5.1](../../blueprint/clpr-service.md#51-who-submits) |
| 124 | Acknowledgements flow in the same sync | merged | Same as `clpr-service-spec.md` row 63; [protocol/bundle.md §2](../../protocol/bundle.md#2-queue-metadata) |
| 125 | Close notification obligation | merged | Same as `clpr-service-spec.md` row 179 (not implemented) |
| | **[3.2.4 Bundle Progress Criteria](../eap-v0.2-source/clpr-service.md#324-bundle-progress-criteria)** | | |
| 126 | Progress criteria | merged | Same as `clpr-service-spec.md` row 109; [protocol/channel-state-transitions.md §3](../../protocol/channel-state-transitions.md#3-progress); [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| 127 | Endpoint progress pre-check | merged | Same as `clpr-service-spec.md` row 117; [blueprint/clpr-service.md §5.2](../../blueprint/clpr-service.md#52-checks-before-submitting) |
| 128 | Close-notification exemption wording | archived | Superseded wording; archive only |
| | **[3.2.5 Bundle Verification](../eap-v0.2-source/clpr-service.md#325-bundle-verification)** | | |
| 129 | Bundle verification sequence diagram | archived | Superseded diagram; archive only |
| 130 | Verifier failure rejects the bundle; fail fast | merged | Same as `clpr-service-spec.md` row 187; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 131 | Progress check after the verifier | merged | Same as `clpr-service-spec.md` row 188; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 132 | Manifest update | merged | Same as `clpr-service-spec.md` row 190; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 133 | Atomic anchor replacement; manifest before anchor | merged | Same as `clpr-service-spec.md` row 191; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 134 | Replay defense by contiguous ids | merged | Same as `clpr-service-spec.md` row 195; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 135 | Running hash check of the bundle | merged | Same as `clpr-service-spec.md` row 197; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 136 | Acknowledgement bounds | merged | Same as `clpr-service-spec.md` row 200; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 137 | Dispatch in order | merged | Same as `clpr-service-spec.md` row 205; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| | **[3.2.6 Bundle Size and Throughput Limits](../eap-v0.2-source/clpr-service.md#326-bundle-size-and-throughput-limits)** | | |
| 138 | Bundle-size sizing example | archived | Illustrative example; archive only |
| 139 | Ledger-specific throttle rationale | archived | Rationale; archive only |
| 140 | Payload size limit on both sides | merged | Same as `clpr-service-spec.md` row 215; [protocol/messaging.md §5](../../protocol/messaging.md#5-enqueue) |
| 141 | Per-channel throttle wording | archived | Superseded wording; throttles are ledger-wide; archive only |
| | **[3.2.7 Message Lifecycle](../eap-v0.2-source/clpr-service.md#327-message-lifecycle)** | | |
| 142 | Message lifecycle | merged | Same as `clpr-service-spec.md` row 220; [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| | **[3.2.8 Response Ordering and Correlation](../eap-v0.2-source/clpr-service.md#328-response-ordering-and-correlation)** | | |
| 143 | Acknowledgement versus reply | overview | [clpr-overview.md §7](../../clpr-overview.md#7-vocabulary) |
| 144 | Replies in originating order | merged | Same as `clpr-service-spec.md` row 54; [protocol/messaging.md §7](../../protocol/messaging.md#7-replies) |
| 145 | Reply correlation by message id | merged | Same as `clpr-service-spec.md` row 221; [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering) |
| 146 | Mixed bundles processed in order | merged | Same as `clpr-service-spec.md` row 205; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 147 | Reply matching walk | merged | Same as `clpr-service-spec.md` row 221; [protocol/messaging.md §8](../../protocol/messaging.md#8-response-ordering) |
| 148 | Replies deleted when acknowledged | merged | Same as `clpr-service-spec.md` row 218; [protocol/messaging.md §9](../../protocol/messaging.md#9-acknowledgement) |
| 149 | Worked example of reply matching | archived | Illustrative example; archive only |
| 150 | Ordering violation rationale | archived | Superseded wording; archive only |
| 151 | Bad bundles rejected with no state change | merged | Same as `clpr-service-spec.md` row 226; [protocol/channel-state-transitions.md §6](../../protocol/channel-state-transitions.md#6-pause-and-resume) |
| | **[3.3 Payment & Routing Layer](../eap-v0.2-source/clpr-service.md#33-payment--routing-layer)** | | |
| 152 | Payment and routing layer introduces connectors | overview | [clpr-overview.md §2](../../clpr-overview.md#2-major-parts) |
| 153 | Happy-path and failure-path diagram | overview | [clpr-overview.md §3](../../clpr-overview.md#3-message-flow) |
| | **[3.3.1 Connectors](../eap-v0.2-source/clpr-service.md#331-connectors)** | | |
| 154 | Connector contract and its parameters | merged | Same as `clpr-service-spec.md` row 121; [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity); [blueprint/clpr-service.md §1.3](../../blueprint/clpr-service.md#13-connector-record-and-counters) |
| 155 | Connector on both ledgers; many-to-many | merged | Same as `clpr-service-spec.md` row 124; [protocol/connector-setup.md §3](../../protocol/connector-setup.md#3-connectors-on-both-ledgers) |
| 156 | Connector id derivation | merged | Same as `clpr-service-spec.md` row 120; [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 157 | Connector commit-reveal | merged | Same as `clpr-service-spec.md` row 259; [protocol/connector-setup.md §2](../../protocol/connector-setup.md#2-registration); [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures) |
| 158 | Per-channel connector scoping | specified | [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 159 | Connector index by channel and connector id | merged | Same as `clpr-service-spec.md` row 122; [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 160 | Many-to-many relationship | merged | Same as `clpr-service-spec.md` row 125; [protocol/connector-setup.md §1](../../protocol/connector-setup.md#1-connector-identity) |
| 161 | Hiero connector signature address | merged | Same as `clpr-service-spec.md` row 265; [ledgers/hiero/README.md §5](../../ledgers/hiero/README.md#5-registration-signatures) |
| | **[3.3.2 Sending a Message](../eap-v0.2-source/clpr-service.md#332-sending-a-message)** | | |
| 162 | Sender names the destination | archived | Superseded wording; archive only |
| 163 | Connector authorization logic | merged | Same as `clpr-service-spec.md` row 175; [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages) |
| 164 | Sender pays only the transaction fee | blueprint | [blueprint/channel-economics.md §1](../../blueprint/channel-economics.md#1-execution-charges) |
| 165 | Authorization is a commitment | merged | Same as `clpr-service-spec.md` row 176; [protocol/connector-setup.md §4](../../protocol/connector-setup.md#4-authorization-of-outbound-messages) |
| | **[3.3.3 Receiving, Routing, and Paying](../eap-v0.2-source/clpr-service.md#333-receiving-routing-and-paying)** | | |
| 166 | Control messages processed directly | merged | Same as `clpr-service-spec.md` row 205; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 167 | Data messages charged to the connector | merged | Same as `clpr-service-spec.md` row 206; [blueprint/channel-economics.md §1](../../blueprint/channel-economics.md#1-execution-charges) |
| 168 | Dispatch and reply generation | merged | Same as `clpr-service-spec.md` row 206; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 169 | Missing or underfunded connector | merged | Same as `clpr-service-spec.md` row 228; [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 170 | Reentrancy protection and callback gas | merged | Same as `clpr-service-spec.md` row 291; [blueprint/clpr-service.md §6.4](../../blueprint/clpr-service.md#64-reentrancy-and-external-calls) |
| 171 | Reply charging | merged | Same as `clpr-service-spec.md` row 229; [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 172 | Per-message failure isolation | merged | Same as `clpr-service-spec.md` row 208; [protocol/channel-state-transitions.md §2](../../protocol/channel-state-transitions.md#2-bundle-processing) |
| 173 | Untrusted payloads | merged | Same as `clpr-service-spec.md` row 292; [blueprint/clpr-service.md §6.5](../../blueprint/clpr-service.md#65-application-payloads) |
| 174 | No confidentiality | merged | Same as `clpr-service-spec.md` row 293; [blueprint/clpr-service.md §6.5](../../blueprint/clpr-service.md#65-application-payloads) |
| | **[3.3.4 Failure Consequences and Slashing](../eap-v0.2-source/clpr-service.md#334-failure-consequences-and-slashing)** | | |
| 175 | Which reply statuses slash | merged | Same as `clpr-service-spec.md` row 229; [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 176 | Destination-side penalty | merged | Same as `clpr-service-spec.md` row 228; [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 177 | Source-side penalty | merged | Same as `clpr-service-spec.md` row 229; [blueprint/stakes-and-bonds.md §2.1](../../blueprint/stakes-and-bonds.md#21-when-a-connector-is-slashed) |
| 178 | Escalation and bans | merged | Same as `clpr-service-spec.md` row 230; [blueprint/stakes-and-bonds.md §2.2](../../blueprint/stakes-and-bonds.md#22-penalty) |
| 179 | Compensation asymmetry | archived | Acknowledged limitation; rationale only; archive only |
| 180 | Stake-to-exposure invariant | merged | Same as `clpr-service-spec.md` row 231; [blueprint/stakes-and-bonds.md §1](../../blueprint/stakes-and-bonds.md#1-connector-stake); [protocol/open-issues.md OI-6](../../protocol/open-issues.md#oi-6-calibration-of-the-connector-stake) |
| 181 | Receive-side economics and the free-rider problem | open issue OI-5 | [protocol/open-issues.md OI-5](../../protocol/open-issues.md#oi-5-compensation-for-sending-bundles) |
| | **[3.3.5 Open Economic Design Issues](../eap-v0.2-source/clpr-service.md#335-open-economic-design-issues)** | | |
| 182 | Queue monopolization | merged | Same as `clpr-service-spec.md` row 297; [blueprint/channel-economics.md §3](../../blueprint/channel-economics.md#3-queue-quotas); [blueprint/clpr-service.md §6.7](../../blueprint/clpr-service.md#67-queue-monopolization) |
| | **[3.4 Application Layer](../eap-v0.2-source/clpr-service.md#34-application-layer)** | | |
| 183 | Application layer placeholder | removed: reference only | Placeholder that named products only |
| 184 | Channel choice by commitment level | overview | [clpr-overview.md §8](../../clpr-overview.md#8-application-patterns), [§4](../../clpr-overview.md#4-trust-model) |
| | **[3.4.1 Remote Smart Contract Call](../eap-v0.2-source/clpr-service.md#341-remote-smart-contract-call)** | | |
| 185 | Remote contract call pattern | overview | [clpr-overview.md §8](../../clpr-overview.md#8-application-patterns) |
| | **[3.4.2 Escrow, Mint, then Burn](../eap-v0.2-source/clpr-service.md#342-escrow-mint-then-burn)** | | |
| 186 | Escrow, mint, then burn pattern | overview | [clpr-overview.md §8](../../clpr-overview.md#8-application-patterns) |
| | **[3.4.3 N-Ledger Atomic Swap (2PC)](../eap-v0.2-source/clpr-service.md#343-n-ledger-atomic-swap-2pc)** | | |
| 187 | Atomic swap across ledgers pattern | overview | [clpr-overview.md §8](../../clpr-overview.md#8-application-patterns) |
| | **[3.4.4 Native Hiero Asset Management](../eap-v0.2-source/clpr-service.md#344-native-hiero-asset-management)** | | |
| 188 | Native asset management placeholder | removed: reference only | Placeholder that named a product only |
| | **[4.1 End User](../eap-v0.2-source/clpr-service.md#41-end-user)** | | |
| 189 | End user role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[4.2 Application Developer](../eap-v0.2-source/clpr-service.md#42-application-developer)** | | |
| 190 | Application developer role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[4.3 Connector Operator](../eap-v0.2-source/clpr-service.md#43-connector-operator)** | | |
| 191 | Connector operator role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles); [protocol/connector-setup.md §5](../../protocol/connector-setup.md#5-removal) |
| | **[4.4 Verifier Developer](../eap-v0.2-source/clpr-service.md#44-verifier-developer)** | | |
| 192 | Verifier developer role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[4.5 Endpoint Operator](../eap-v0.2-source/clpr-service.md#45-endpoint-operator)** | | |
| 193 | Endpoint operator role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[4.6 CLPR Service Admin](../eap-v0.2-source/clpr-service.md#46-clpr-service-admin)** | | |
| 194 | Service administrator role | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[Setting Up a New Cross-Ledger Route](../eap-v0.2-source/clpr-service.md#setting-up-a-new-cross-ledger-route)** | | |
| 195 | Scenario: opening a route | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles) |
| | **[Proof Format Upgrade](../eap-v0.2-source/clpr-service.md#proof-format-upgrade)** | | |
| 196 | Scenario: proof format upgrade | merged | Same as `clpr-service-spec.md` row 299; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| | **[Responding to a Compromised Verifier](../eap-v0.2-source/clpr-service.md#responding-to-a-compromised-verifier)** | | |
| 197 | Scenario: compromised verifier | merged | Same as `clpr-service-spec.md` row 302; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| | **[Connector Withdrawal Under Load](../eap-v0.2-source/clpr-service.md#connector-withdrawal-under-load)** | | |
| 198 | Scenario: connector withdrawal | overview | [clpr-overview.md §5](../../clpr-overview.md#5-roles); [protocol/connector-setup.md §5](../../protocol/connector-setup.md#5-removal) |
| | **[5. Recovery Scenarios](../eap-v0.2-source/clpr-service.md#5-recovery-scenarios)** | | |
| 199 | Recovery scenario R1 | merged | Same as `clpr-service-spec.md` row 298; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 200 | Recovery scenario R2 | merged | Same as `clpr-service-spec.md` row 299; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 201 | Recovery scenario R3 | merged | Same as `clpr-service-spec.md` row 300; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 202 | Recovery scenario R4 | merged | Same as `clpr-service-spec.md` row 301; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 203 | Recovery scenario R5 | merged | Same as `clpr-service-spec.md` row 302; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 204 | Recovery scenario R6 | merged | Same as `clpr-service-spec.md` row 303; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 205 | Recovery scenario R7 | merged | Same as `clpr-service-spec.md` row 304; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 206 | Recovery scenario R8 | merged | Same as `clpr-service-spec.md` row 305; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 207 | Recovery scenario R9 | merged | Same as `clpr-service-spec.md` row 306; [blueprint/clpr-service.md §7](../../blueprint/clpr-service.md#7-recovery-scenarios) |
| 208 | Messages left unresolved when a channel cannot drain | open issue OI-4 | [protocol/open-issues.md OI-4](../../protocol/open-issues.md#oi-4-messages-left-without-replies-when-a-channel-cannot-drain) |
| | **[6.1 Risks](../eap-v0.2-source/clpr-service.md#61-risks)** | | |
| 209 | Project risks | archived | Project-management content; archive only |

## Verifier documents

The verifier documents are [`verifiers/README.md`](../eap-v0.2-source/verifiers/README.md) and the Hiero and QBFT documents under [`verifiers/`](../eap-v0.2-source/verifiers/README.md). Their content is now in the [Ledger Specifications](../../ledgers/README.md).

| # | Item | Status | Location in v0.2 |
|---|---|---|---|
| | **[verifiers/README.md: Interface](../eap-v0.2-source/verifiers/README.md#interface)** | | |
| 1 | EVM verifier interface signatures | specified | [ledgers/evm/verifier-api.md §2](../../ledgers/evm/verifier-api.md#2-functions) |
| 2 | `verifyConfig` once at setup, `verifyBundle` on every bundle; both read-only | specified | [ledgers/evm/verifier-api.md §4](../../ledgers/evm/verifier-api.md#4-call-semantics); [protocol/verifier-interface.md §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| | **[verifiers/README.md: Directory layout](../eap-v0.2-source/verifiers/README.md#directory-layout)** | | |
| 3 | Per-ledger three-file document layout | archived | Document layout replaced by the Ledger Specifications; archive only |
| | **[verifiers/README.md: Chains](../eap-v0.2-source/verifiers/README.md#chains)** | | |
| 4 | Table of ledgers and trust anchor types | specified | [ledgers/README.md](../../ledgers/README.md) |
| | **[verifiers/README.md: Standard file outlines](../eap-v0.2-source/verifiers/README.md#standard-file-outlines)** | | |
| 5 | Standard outlines of the per-ledger files | archived | Document outlines replaced by the proof-scheme structure; archive only |
| | **[verifiers/README.md: Adding a new chain](../eap-v0.2-source/verifiers/README.md#adding-a-new-chain)** | | |
| 6 | Steps for adding a ledger's verifier | archived | Contribution process; archive only |
| | **[verifiers/hiero/state_proof.md: Overview](../eap-v0.2-source/verifiers/hiero/state_proof.md#overview)** | | |
| 7 | Hiero proofs authenticate a signed state snapshot with the channel and message leaves | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §2](../../ledgers/hiero/proof-schemes/hints-wraps.md#2-trust-model), [§4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle) |
| | **[verifiers/hiero/state_proof.md: Cryptographic primitives](../eap-v0.2-source/verifiers/hiero/state_proof.md#cryptographic-primitives)** | | |
| 8 | Hiero cryptographic primitives (SHA-384 Merkle tree, hinTS, WRAPS) | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §2](../../ledgers/hiero/proof-schemes/hints-wraps.md#2-trust-model), [§4.4](../../ledgers/hiero/proof-schemes/hints-wraps.md#44-block-signature); [protocol/open-issues.md OI-9](../../protocol/open-issues.md#oi-9-hints-and-wraps-verification-parameters) |
| | **[verifiers/hiero/state_proof.md: SHA-384 Merkle domain prefixes](../eap-v0.2-source/verifiers/hiero/state_proof.md#sha-384-merkle-domain-prefixes)** | | |
| 9 | Merkle domain-separation prefixes | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.3](../../ledgers/hiero/proof-schemes/hints-wraps.md#43-hashing) |
| | **[verifiers/hiero/state_proof.md: Wire format](../eap-v0.2-source/verifiers/hiero/state_proof.md#wire-format)** | | |
| 10 | Hiero `StateProof` structure | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle) |
| 11 | Hiero block proof structure | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle) |
| 12 | Hiero Merkle leaf proof structure | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle) |
| 13 | Hiero Merkle path structure | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle), [§4.3](../../ledgers/hiero/proof-schemes/hints-wraps.md#43-hashing) |
| 14 | The serialized state proof is the opaque payload | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#41-bundle) |
| | **[verifiers/hiero/state_proof.md: Storage layout](../eap-v0.2-source/verifiers/hiero/state_proof.md#storage-layout)** | | |
| 15 | Hiero proven leaves and their tags | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#42-leaves) |
| 16 | Hiero leaf addressing | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §4.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#42-leaves) |
| 17 | Hiero block root composition | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §5.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#52-block-root-extension) |
| | **[verifiers/hiero/state_proof.md: Proof construction](../eap-v0.2-source/verifiers/hiero/state_proof.md#proof-construction)** | | |
| 18 | Hiero proof construction | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §5.1](../../ledgers/hiero/proof-schemes/hints-wraps.md#51-bundle); [ledgers/hiero/bundle-aggregation.md §2](../../ledgers/hiero/bundle-aggregation.md#2-state-read-and-finality) |
| | **[verifiers/hiero/state_proof.md: Proof verification](../eap-v0.2-source/verifiers/hiero/state_proof.md#proof-verification)** | | |
| 19 | Hiero proof verification steps | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| 20 | Verification is read-only; outputs come only from the proof | merged | Same as row 2; [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| | **[verifiers/hiero/trust_anchor.md: Overview](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#overview)** | | |
| 21 | Hiero trust anchor is the ledger id and binds the channel to one network | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §2](../../ledgers/hiero/proof-schemes/hints-wraps.md#2-trust-model), [§7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes); [ledgers/hiero/README.md §1](../../ledgers/hiero/README.md#1-ledger-identity) |
| 22 | Hiero trust anchor does not change | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes) |
| | **[verifiers/hiero/trust_anchor.md: Wire format](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#wire-format)** | | |
| 23 | Hiero trust anchor encoding and empty anchor id | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes), [§9.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#92-verification) |
| 24 | Hiero ledger id at setup and afterwards | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §7](../../ledgers/hiero/proof-schemes/hints-wraps.md#7-trust-anchor-changes), [§9.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#92-verification) |
| | **[verifiers/hiero/trust_anchor.md: Initial anchor derivation](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#initial-anchor-derivation)** | | |
| 25 | Hiero initial anchor derivation at setup | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §9.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#92-verification); [protocol/open-issues.md OI-2](../../protocol/open-issues.md#oi-2-what-the-configuration-proof-must-authenticate) |
| 26 | After setup the stored ledger id governs verification | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| | **[verifiers/hiero/trust_anchor.md: Detection](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#detection)** | | |
| 27 | Detection of a ledger id change | archived | Not applicable: the ledger id does not change; archive only |
| | **[verifiers/hiero/trust_anchor.md: Bundle inclusion](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#bundle-inclusion)** | | |
| 28 | Planned anchor change in bundles | archived | Superseded design; archive only |
| | **[verifiers/hiero/trust_anchor.md: On-chain update](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#on-chain-update)** | | |
| 29 | Planned on-chain anchor update | archived | Superseded design; archive only |
| | **[verifiers/hiero/trust_anchor.md: Security properties](../eap-v0.2-source/verifiers/hiero/trust_anchor.md#security-properties)** | | |
| 30 | Hiero trust anchor security properties | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §2](../../ledgers/hiero/proof-schemes/hints-wraps.md#2-trust-model); [protocol/open-issues.md OI-2](../../protocol/open-issues.md#oi-2-what-the-configuration-proof-must-authenticate) |
| | **[verifiers/hiero/verifier_contract.md: Overview](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#overview)** | | |
| 31 | Hiero verifier delegates to the built-in verifier | specified | [ledgers/hiero/README.md §3](../../ledgers/hiero/README.md#3-built-in-verifiers); [ledgers/hiero/verifier-api.md §1](../../ledgers/hiero/verifier-api.md#1-scope) |
| | **[verifiers/hiero/verifier_contract.md: Inputs](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#inputs)** | | |
| 32 | Hiero `verifyConfig` inputs | specified | [ledgers/evm/verifier-api.md §2.1](../../ledgers/evm/verifier-api.md#21-verifyconfig) |
| | **[verifiers/hiero/verifier_contract.md: Validation steps](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#validation-steps)** | | |
| 33 | Hiero `verifyConfig` checks | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §9.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#92-verification) |
| | **[verifiers/hiero/verifier_contract.md: Outputs](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#outputs)** | | |
| 34 | Hiero `verifyConfig` outputs and channel context | specified | [ledgers/evm/verifier-api.md §3.2](../../ledgers/evm/verifier-api.md#32-channelcontext); [ledgers/hiero/proof-schemes/hints-wraps.md §9.2](../../ledgers/hiero/proof-schemes/hints-wraps.md#92-verification) |
| | **[verifiers/hiero/verifier_contract.md: Inputs](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#inputs-1)** | | |
| 35 | Hiero `verifyBundle` inputs | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| | **[verifiers/hiero/verifier_contract.md: Validation steps](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#validation-steps-1)** | | |
| 36 | Hiero `verifyBundle` steps | specified | [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm), [§8](../../ledgers/hiero/proof-schemes/hints-wraps.md#8-rejection-conditions) |
| | **[verifiers/hiero/verifier_contract.md: Outputs](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#outputs-1)** | | |
| 37 | Hiero `verifyBundle` outputs | specified | [ledgers/evm/verifier-api.md §3.1](../../ledgers/evm/verifier-api.md#31-structures); [ledgers/hiero/proof-schemes/hints-wraps.md §6](../../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm) |
| | **[verifiers/hiero/verifier_contract.md: Implementation reference](../eap-v0.2-source/verifiers/hiero/verifier_contract.md#implementation-reference)** | | |
| 38 | Implementation reference table | archived | Implementation reference; not specification content; archive only |
| | **[verifiers/qbft/state_proof.md: Overview](../eap-v0.2-source/verifiers/qbft/state_proof.md#overview)** | | |
| 39 | QBFT proof: account and storage proofs with block headers | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §3](../../ledgers/besu/proof-schemes/qbft-epoch.md#3-proof-material); [ledgers/besu/proof-schemes/qbft-header.md §3](../../ledgers/besu/proof-schemes/qbft-header.md#3-proof-material); [ledgers/besu/proof-schemes/qbft-contract.md §3](../../ledgers/besu/proof-schemes/qbft-contract.md#3-proof-material); [ledgers/besu/README.md §3.4](../../ledgers/besu/README.md#34-proof-encoding) |
| | **[verifiers/qbft/state_proof.md: Cryptographic primitives](../eap-v0.2-source/verifiers/qbft/state_proof.md#cryptographic-primitives)** | | |
| 40 | QBFT cryptographic primitives | specified | [ledgers/besu/README.md §3.4](../../ledgers/besu/README.md#34-proof-encoding), [§4.2](../../ledgers/besu/README.md#42-qbft-headers-and-seals) |
| | **[verifiers/qbft/state_proof.md: Wire format](../eap-v0.2-source/verifiers/qbft/state_proof.md#wire-format)** | | |
| 41 | QBFT proof layout | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §4](../../ledgers/besu/proof-schemes/qbft-epoch.md#4-wire-layout) |
| 42 | Block header field order | specified | [ledgers/besu/README.md §4.2](../../ledgers/besu/README.md#42-qbft-headers-and-seals); [ledgers/besu/proof-schemes/qbft-epoch.md §4](../../ledgers/besu/proof-schemes/qbft-epoch.md#4-wire-layout) |
| 43 | QBFT bundle content | specified | [ledgers/besu/README.md §3.4](../../ledgers/besu/README.md#34-proof-encoding), [§3.5](../../ledgers/besu/README.md#35-verifying-the-clpr-service-state); [ledgers/besu/proof-schemes/qbft-epoch.md §5](../../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm) |
| | **[verifiers/qbft/state_proof.md: Storage layout](../eap-v0.2-source/verifiers/qbft/state_proof.md#storage-layout)** | | |
| 44 | Proven storage slots of the CLPR Service | specified | [ledgers/besu/README.md §3.1–3.3](../../ledgers/besu/README.md#31-service-slots) |
| 45 | Proven configuration slot | specified | [ledgers/besu/README.md §3.1](../../ledgers/besu/README.md#31-service-slots) |
| | **[verifiers/qbft/state_proof.md: Proof construction](../eap-v0.2-source/verifiers/qbft/state_proof.md#proof-construction)** | | |
| 46 | QBFT proof construction | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §5](../../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm); [ledgers/besu/bundle-aggregation.md §3](../../ledgers/besu/bundle-aggregation.md#3-message-range-and-limits) |
| | **[verifiers/qbft/state_proof.md: Proof verification](../eap-v0.2-source/verifiers/qbft/state_proof.md#proof-verification)** | | |
| 47 | QBFT proof verification steps | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §6](../../ledgers/besu/proof-schemes/qbft-epoch.md#6-decode-and-verify-algorithm) |
| | **[verifiers/qbft/trust_anchor.md: Overview](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#overview)** | | |
| 48 | QBFT trust anchor: validator set and Service identity | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §2](../../ledgers/besu/proof-schemes/qbft-epoch.md#2-trust-model), [§7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes); [ledgers/besu/proof-schemes/qbft-header.md §2](../../ledgers/besu/proof-schemes/qbft-header.md#2-trust-model), [§7](../../ledgers/besu/proof-schemes/qbft-header.md#7-trust-anchor-changes); [ledgers/besu/proof-schemes/qbft-contract.md §2](../../ledgers/besu/proof-schemes/qbft-contract.md#2-trust-model), [§7](../../ledgers/besu/proof-schemes/qbft-contract.md#7-trust-anchor-changes) |
| | **[verifiers/qbft/trust_anchor.md: Wire format](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#wire-format)** | | |
| 49 | QBFT trust anchor encoding | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes) |
| 50 | QBFT trust anchor id encoding | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes) |
| | **[verifiers/qbft/trust_anchor.md: Initial anchor derivation](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#initial-anchor-derivation)** | | |
| 51 | QBFT initial anchor derivation | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §9.1](../../ledgers/besu/proof-schemes/qbft-epoch.md#91-configuration-proof); [protocol/open-issues.md OI-3](../../protocol/open-issues.md#oi-3-configuration-proof-format-for-the-qbft-epoch-scheme) |
| | **[verifiers/qbft/trust_anchor.md: Detection](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#detection)** | | |
| 52 | Detection of a validator change by epoch | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §5](../../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm) |
| | **[verifiers/qbft/trust_anchor.md: Bundle inclusion](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#bundle-inclusion)** | | |
| 53 | Inclusion of epoch headers in a bundle | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §5](../../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm) |
| | **[verifiers/qbft/trust_anchor.md: On-chain update](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#on-chain-update)** | | |
| 54 | QBFT on-chain anchor update | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §6](../../ledgers/besu/proof-schemes/qbft-epoch.md#6-decode-and-verify-algorithm), [§7](../../ledgers/besu/proof-schemes/qbft-epoch.md#7-trust-anchor-changes) |
| | **[verifiers/qbft/trust_anchor.md: Security properties](../eap-v0.2-source/verifiers/qbft/trust_anchor.md#security-properties)** | | |
| 55 | QBFT trust anchor security properties | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §2](../../ledgers/besu/proof-schemes/qbft-epoch.md#2-trust-model) |
| | **[verifiers/qbft/verifier_contract.md: Overview](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#overview)** | | |
| 56 | QBFT verifier overview | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §9.1](../../ledgers/besu/proof-schemes/qbft-epoch.md#91-configuration-proof) |
| | **[verifiers/qbft/verifier_contract.md: Inputs](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#inputs)** | | |
| 57 | QBFT `verifyConfig` inputs | specified | [ledgers/evm/verifier-api.md §2](../../ledgers/evm/verifier-api.md#2-functions); [ledgers/besu/proof-schemes/qbft-epoch.md §9](../../ledgers/besu/proof-schemes/qbft-epoch.md#9-configuration-and-manifest-proofs) |
| | **[verifiers/qbft/verifier_contract.md: Validation steps](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#validation-steps)** | | |
| 58 | QBFT `verifyConfig` steps | open issue OI-3 | [ledgers/besu/proof-schemes/qbft-epoch.md §9.1](../../ledgers/besu/proof-schemes/qbft-epoch.md#91-configuration-proof); [protocol/open-issues.md OI-3](../../protocol/open-issues.md#oi-3-configuration-proof-format-for-the-qbft-epoch-scheme) |
| | **[verifiers/qbft/verifier_contract.md: Outputs](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#outputs)** | | |
| 59 | QBFT `verifyConfig` outputs | specified | [ledgers/evm/verifier-api.md §2.1](../../ledgers/evm/verifier-api.md#21-verifyconfig), [§3.2](../../ledgers/evm/verifier-api.md#32-channelcontext); [ledgers/besu/proof-schemes/qbft-epoch.md §9.1](../../ledgers/besu/proof-schemes/qbft-epoch.md#91-configuration-proof) |
| | **[verifiers/qbft/verifier_contract.md: Inputs](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#inputs-1)** | | |
| 60 | QBFT `verifyBundle` inputs | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §6](../../ledgers/besu/proof-schemes/qbft-epoch.md#6-decode-and-verify-algorithm) |
| | **[verifiers/qbft/verifier_contract.md: Validation steps](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#validation-steps-1)** | | |
| 61 | QBFT `verifyBundle` steps | specified | [ledgers/besu/proof-schemes/qbft-epoch.md §6](../../ledgers/besu/proof-schemes/qbft-epoch.md#6-decode-and-verify-algorithm); [ledgers/besu/README.md §4.2](../../ledgers/besu/README.md#42-qbft-headers-and-seals) |
| | **[verifiers/qbft/verifier_contract.md: Outputs](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#outputs-1)** | | |
| 62 | QBFT `verifyBundle` outputs | specified | [ledgers/evm/verifier-api.md §2](../../ledgers/evm/verifier-api.md#2-functions), [§3.1](../../ledgers/evm/verifier-api.md#31-structures) |
| | **[verifiers/qbft/verifier_contract.md: Implementation reference](../eap-v0.2-source/verifiers/qbft/verifier_contract.md#implementation-reference)** | | |
| 63 | Implementation reference table | archived | Implementation reference; not specification content; archive only |

## Summary

| Status | `clpr-service-spec.md` | `clpr-service.md` | Verifier documents | Total |
|---|---|---|---|---|
| specified | 240 | 12 | 53 | 305 |
| overview | 3 | 36 | 0 | 39 |
| blueprint | 48 | 3 | 0 | 51 |
| open issue | 0 | 2 | 1 | 3 |
| merged | 6 | 135 | 1 | 142 |
| archived | 3 | 18 | 8 | 29 |
| dropped: not implemented | 6 | 0 | 0 | 6 |
| removed: reference only | 0 | 3 | 0 | 3 |
| **Total** | **306** | **209** | **63** | **578** |

Open issue rows: OI-3 (1), OI-4 (1), OI-5 (1).
