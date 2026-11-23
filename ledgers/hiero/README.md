# Hiero

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

This document defines how Hiero takes part in CLPR: its identity, its verifier API and built-in verifiers, its proof schemes, its registration signatures, its application and connector interfaces, its endpoint manifest and its CLPR Service operations.

## 1. Ledger identity

| Identifier | Value |
|---|---|
| Chain id | CAIP-2 `eip155:<chain id>`, where `<chain id>` is the network's EVM chain id in decimal, for example `eip155:295`. Set by the ledger's configuration. |
| Ledger id | 64 bytes: the hash of the ledger's genesis address book (32 bytes) followed by the hash of its genesis hinTS verification key (32 bytes). It is fixed for the life of the ledger and does not change when the roster changes. |
| CLPR Service address | `0x000000000000000000000000000000000000016e` (20 bytes). This is the `service_address` of the ledger's configuration and endpoint manifest. |

A Hiero ledger hosts exactly one CLPR Service, at the address above. The ledger id therefore identifies both the ledger and its CLPR Service. It is the trust anchor of the [`hints-wraps`](proof-schemes/hints-wraps/README.md) proof scheme. The [`hints`](proof-schemes/hints/README.md) proof scheme anchors to the ledger's current hinTS verification key, which changes with the roster.

The ledger configuration is created at genesis with no trust anchor and a placeholder timestamp. The first administrative configuration update after the ledger id exists sets `initial_trust_anchor` and `initial_trust_anchor_id` to the ledger id, and `timestamp` to the consensus time of that update. Until then, a channel that uses the `hints-wraps` scheme cannot be completed with this ledger as its peer.

Every consensus node of a Hiero ledger is a CLPR Endpoint. The ledger's endpoint manifest is derived from its node roster, with no administrator operations (Section 7). It is created at version 1 with no endpoints and is filled as the nodes publish their endpoints.

## 2. Verifier API

The Hiero CLPR Service calls verifier contracts through the [Hiero Verifier API](verifier-api.md). Every verifier contract used on a Hiero ledger, built-in or deployed, implements it.

## 3. Built-in verifiers

A channel's verifier contract on Hiero is either a built-in verifier or a deployed EVM contract that implements the [Hiero Verifier API](verifier-api.md). Built-in verifiers are system contracts at fixed addresses. They have no account record and need no deployment.

| Address | Verifies | Proof scheme |
|---|---|---|
| `0x…016e` | Bundles from Hiero ledgers | [Hiero `hints-wraps`](proof-schemes/hints-wraps/README.md) |
| `0x…016f` | Bundles from Besu ledgers | [Besu `qbft-header`](../besu/proof-schemes/qbft-header.md) and [`qbft-contract`](../besu/proof-schemes/qbft-contract.md), with the protobuf configuration proof form ([qbft-header §9.1](../besu/proof-schemes/qbft-header.md#91-configuration-proof)) |

The table lists the built-in verifiers for the ledgers covered by this specification.

`0x…016e` is also the address of the CLPR Service.

## 4. Proof schemes

A Hiero CLPR Endpoint produces bundles in two proof schemes:

| Scheme | Destinations | Summary |
|---|---|---|
| [`hints-wraps`](proof-schemes/hints-wraps/README.md) | Hiero ledgers | A bare `StateProof`: Merkle paths into the ledger's state, under a hinTS threshold signature on the block root, with a WRAPS proof that binds the signing key to the ledger id. The trust anchor is the ledger id. |
| [`hints`](proof-schemes/hints/README.md) | EVM ledgers | A `HieroProof` envelope: the same Merkle paths under a compact hinTS signature, with no WRAPS proof. The trust anchor is the current hinTS verification key, which rotates with the roster. |

**Selection.** For each channel, the endpoint produces `hints` bundles when the peer's `current_trust_anchor_id` is 33 bytes beginning with `0x01` ([`hints` §7](proof-schemes/hints/README.md#7-trust-anchor-changes)), and `hints-wraps` bundles otherwise.

**Configuration and manifest proofs.** The ledger's configuration and manifest queries return `hints-wraps` proofs ([`hints-wraps` §9.1](proof-schemes/hints-wraps/README.md#91-proofs)). A registrant opening a channel to an EVM ledger supplies them to the EVM verifier in the state form of the `hints` envelope ([`hints` §9](proof-schemes/hints/README.md#9-configuration-and-manifest-proofs)).

The [bundle aggregation](bundle-aggregation.md) document defines how a Hiero CLPR Endpoint selects bundle content.

## 5. Registration signatures

The reveal steps of [channel registration](../../protocol/channel-setup.md#2-registration) and [connector registration](../../protocol/connector-setup.md#2-registration) each carry a signature by the registrant's key. The reveal carries a `signature_scheme` input that selects one of two schemes:

| `signature_scheme` | Public key | Signature |
|---|---|---|
| 0: ECDSA secp256k1 | 64 bytes: uncompressed `x ‖ y`, without the `0x04` prefix | 64 bytes: `r ‖ s` |
| 1: Ed25519 | 32 bytes | 64 bytes |

The CLPR Service MUST reject a reveal whose public key or signature length does not match the selected scheme.

The public key bytes above are also the bytes used in the commitment and identifier derivations of those modules.

The signed message is a 32-byte digest:

| Registration | Signed digest |
|---|---|
| Channel | `keccak256(channel_id)` |
| Connector | `keccak256(connector_id ‖ 0x000000000000000000000000000000000000016e)`, where the second part is the 20-byte CLPR Service address |

The digest is signed as is. There is no prefix (such as an EIP-191 prefix) and no further hashing: ECDSA signs the digest directly, and Ed25519 signs the 32 digest bytes as its message. The CLPR Service MUST reject a reveal whose signature does not verify under the given public key.

## 6. Application and connector interfaces

Applications and connectors on Hiero are EVM contracts. The callbacks have the signatures and selectors of the [EVM interfaces](../evm/README.md#3-application-and-connector-interfaces); this section defines how Hiero calls them. Their semantics are defined in [Messaging](../../protocol/messaging.md) and [Connector setup](../../protocol/connector-setup.md). An application's identity, as `sender` or `target_application`, is its 20-byte EVM address.

The CLPR Service makes the connector authorization call and the application callbacks from the CLPR Service address `0x…016e`: in each of them, the caller (`msg.sender`) is that address.

### 6.1 Sending a message

An application sends a DATA message by calling the CLPR Service at `0x000000000000000000000000000000000000016e`:

```text
function sendMessage(
    bytes32 channelId,
    bytes32 connectorId,
    bytes   targetApplication,
    bytes   messageData
) returns (uint64 messageId);
```

| Aspect | Rule |
|---|---|
| Selector input | `sendMessage(bytes32,bytes32,bytes,bytes)` |
| `sender` | The caller's address (`msg.sender`) as seen by the CLPR Service at `0x…016e`. |
| Result | The id assigned to the message ([enqueue](../../protocol/messaging.md#5-enqueue)). If the send is rejected, the call reverts. |
| Gas | The call costs the caller a fixed 100,000 gas. |
| Call kind | It cannot be called from a static call. |

### 6.2 Connector authorization

During `sendMessage`, the CLPR Service calls `authorizeOutboundMessage(bytes32,bytes,bytes,bytes)` on the connector contract named by `connectorId` ([authorization of outbound messages](../../protocol/connector-setup.md#4-authorization-of-outbound-messages)).

| Aspect | Rule |
|---|---|
| Call kind | An ordinary call. The connector MAY change its own state. |
| Gas | The connector call has a gas limit of 50,000. |
| Result | The message is authorized only if the call succeeds and its return data `r` has `len(r) ≥ 32` and `r[31] ≠ 0`. Any other outcome rejects the send. |

### 6.3 Application callbacks

The CLPR Service calls the application callbacks as ordinary contract calls during [bundle processing](../../protocol/channel-state-transitions.md#2-bundle-processing).

| Callback | Called on | Gas | Outcome |
|---|---|---|---|
| `onClprMessage(bytes32,bytes,bytes)` | The contract at `target_application`, for each DATA message delivered | `min(max_gas_per_message, floor(g / c))`, where `g` is the transaction's remaining gas and `c` the number of `onClprMessage` and `onClprResponse` calls still to be made in the bundle. A budget of 0 gives APPLICATION_ERROR, with no call and no charge. | A call that succeeds gives SUCCESS. `message_reply_data` is the return data decoded as an ABI-encoded `bytes`, or empty if there is no return data. Return data that does not decode as `bytes` gives APPLICATION_ERROR, with empty reply data. A failed call gives APPLICATION_ERROR, with empty reply data. Response data that would make the REPLY exceed the peer's `max_message_payload_bytes` gives APPLICATION_ERROR, with empty reply data ([throttles](../../protocol/ledger-configuration.md#3-throttles)). |
| `onClprResponse(bytes32,uint64,uint8,bytes)` | The original `sender`, for each REPLY received, if `sender` is not empty | `min(max_gas_per_message, floor(g / c))`, as for `onClprMessage` | Called only if the source connector can prepay its gas; otherwise it is skipped. Best effort: a failed or skipped call is ignored, and the REPLY remains delivered. |

The connector is charged as defined in [execution charges](../../blueprint/channel-economics.md#1-execution-charges). Hiero does not call `payForExecution` or `onInboundMessage`.

## 7. Endpoint manifest

The endpoint manifest of a Hiero ledger is derived from its node roster, with no administrator operations:

1. Each node publishes its own endpoint (network address, TLS certificate, and node account) in a node-only transaction, at startup if it is absent from the manifest.
2. A publication from a roster node whose endpoint is not in the manifest opens a **construction** for the next version, targeting the active roster, with a deadline `manifestGracePeriod` away.
3. While a construction is open, the Service gathers publications from target nodes. A later publication from the same node replaces the earlier one.
4. The construction closes when every target has published. Otherwise, at the deadline it is extended by `manifestGraceExtension`, up to `manifestMaxGraceExtensions` times, and then closed regardless.
5. On close, the manifest becomes exactly the gathered endpoints. Its version increases by 1 if the endpoint list changed and is unchanged otherwise.
6. When a network upgrade changes the roster's composition, a new construction for the new roster replaces any open one.

A change in node weights alone does not change the manifest. A misbehaving node is removed through the ledger's own governance of the roster.

Each node serves [endpoint sync](../../protocol/endpoint-sync/README.md) on the ports of its gRPC API. A node with a TLS certificate publishes that certificate as its `tls_certificate` and its TLS API port as its `port`; a node without one publishes an empty certificate and its plaintext API port.

## 8. CLPR Service operations

The Hiero CLPR Service exposes the Protocol's operations as transactions and queries of the ledger's API. `ContractID`, `AccountID` and `Key` are the ledger's standard API types.

```proto
enum ClprSignatureScheme {
  ECDSA_SECP256K1 = 0;                          // Section 5
  ED25519 = 1;
}

message ClprRegisterChannelTransactionBody {
  bytes ownership_commitment = 1;
}

message ClprCompleteChannelTransactionBody {
  bytes channel_id = 1;
  bytes public_key = 2;
  bytes signature = 3;
  ClprSignatureScheme signature_scheme = 4;
  ContractID verifier_contract = 5;
  bytes config_proof_bytes = 6;
  bytes endpoint_manifest_proof_bytes = 7;
}

message ClprCloseChannelTransactionBody {
  bytes channel_id = 1;
  bytes ownership_commitment = 2;               // identifies a PENDING channel
}

message ClprRegisterConnectorTransactionBody {
  bytes commitment = 1;
  bytes channel_id = 2;                         // an existing channel
}

message ClprCompleteConnectorTransactionBody {
  bytes connector_id = 1;
  bytes public_key = 2;
  bytes signature = 3;
  ClprSignatureScheme signature_scheme = 4;
  bytes salt = 5;
  bytes channel_id = 6;
  ContractID connector_contract = 7;
  Key admin_key = 8;
  uint64 locked_stake = 9;
}

message ClprDeregisterConnectorTransactionBody {
  bytes channel_id = 1;
  bytes connector_id = 2;
  AccountID stake_recipient = 3;
}

message ClprSubmitBundleTransactionBody {
  bytes channel_id = 1;
  bytes bundle_payload = 2;
}

message ClprUpdateLedgerConfigurationTransactionBody {
  ClprLedgerConfiguration configuration = 1;
}
```

| Operation | Meaning |
|---|---|
| `registerChannel`, `completeChannel` | The commit and reveal of [channel registration](../../protocol/channel-setup.md#2-registration). |
| `closeChannel` | [Administrative close](../../protocol/channel-state-transitions.md#5-closing-and-draining), or removal of a PENDING channel by its commitment. Privileged. |
| `registerConnector`, `completeConnector` | The commit and reveal of [connector registration](../../protocol/connector-setup.md#2-registration). `registerConnector` requires `channel_id`, 32 bytes, and the Hiero CLPR Service rejects it unless that channel exists. `locked_stake` is the connector's stake. |
| `deregisterConnector` | [Connector removal](../../protocol/connector-setup.md#5-removal). The remaining stake goes to `stake_recipient`. |
| `submitBundle` | [Bundle processing](../../protocol/channel-state-transitions.md#2-bundle-processing). |
| `updateLedgerConfiguration` | A change to the [ledger configuration](../../protocol/ledger-configuration.md#2-ledger-configuration). Privileged. |
| `getLedgerConfiguration`, `getEndpointManifest` | Queries that return the current configuration or local manifest, together with a `hints-wraps` state proof of it (Section 4). |
| Endpoint publication | A node-only transaction by which a node publishes its own endpoint (Section 7). |

Privileged operations are accepted only from the ledger's designated administrative accounts.
