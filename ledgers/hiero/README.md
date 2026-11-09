# Hiero

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

This document defines how Hiero takes part in CLPR: its identity, its verifier API and built-in verifiers, its proof scheme, its registration signatures, and its application and connector interfaces.

## 1. Ledger identity

| Identifier | Value |
|---|---|
| Chain id | CAIP-2 `hiero:<network>`, for example `hiero:mainnet`. Set by the ledger's configuration. |
| Ledger id | 32 bytes: the hash of the ledger's genesis address book. It is fixed for the life of the ledger and does not change when the roster changes. |
| CLPR Service address | `0x000000000000000000000000000000000000016e` (20 bytes). This is the `service_address` of the ledger's configuration and endpoint manifest. |

A Hiero ledger hosts exactly one CLPR Service, at the address above. The ledger id therefore identifies both the ledger and its CLPR Service. It is the trust anchor of the [`hints-wraps`](proof-schemes/hints-wraps.md) proof scheme.

## 2. Verifier API

The Hiero CLPR Service calls verifier contracts through the [Hiero Verifier API](verifier-api.md). Every verifier contract used on a Hiero ledger, built-in or deployed, implements it.

## 3. Built-in verifiers

A channel's verifier contract on Hiero is either a built-in verifier or a deployed EVM contract that implements the [Hiero Verifier API](verifier-api.md). Built-in verifiers are system contracts at fixed addresses. They have no account record and need no deployment.

| Address | Verifies | Proof scheme |
|---|---|---|
| `0x…016e` | Bundles from Hiero ledgers | [Hiero `hints-wraps`](proof-schemes/hints-wraps.md) |
| `0x…016f` | Bundles from Besu ledgers | [Besu `qbft-epoch`](../besu/proof-schemes/qbft-epoch.md) |

The table lists the built-in verifiers for the ledgers covered by this specification.

`0x…016e` is also the address of the CLPR Service.

## 4. Proof schemes

A Hiero CLPR Endpoint produces bundles in one proof scheme:

| Scheme | Summary |
|---|---|
| [`hints-wraps`](proof-schemes/hints-wraps.md) | Merkle paths into the ledger's state, under a hinTS threshold signature on the block root, with a WRAPS proof that binds the signing key to the ledger id. |

The same scheme proves the ledger configuration and the endpoint manifest at channel setup. The ledger's configuration and manifest queries return these proofs ([`hints-wraps` §9.1](proof-schemes/hints-wraps.md#91-proofs)).

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
| Call kind | Static. The connector cannot change its own state during the call. |
| Gas | The connector call has a gas limit of 50,000. |
| Result | The message is authorized only if the call succeeds and its return data `r` has `len(r) ≥ 32` and `r[31] ≠ 0`. Any other outcome rejects the send. |

### 6.3 Application callbacks

The CLPR Service calls the application callbacks as ordinary contract calls during [bundle processing](../../protocol/channel-state-transitions.md#2-bundle-processing).

| Callback | Called on | Gas | Outcome |
|---|---|---|---|
| `onClprMessage(bytes32,bytes,bytes)` | The contract at `target_application`, for each DATA message delivered | The local `max_gas_per_message` | A call that succeeds gives SUCCESS. `message_reply_data` is the return data decoded as an ABI-encoded `bytes`, or empty if there is no return data. Return data that does not decode as `bytes` gives APPLICATION_ERROR, with empty reply data. A failed call gives APPLICATION_ERROR, with empty reply data. |
| `onClprResponse(bytes32,uint64,uint8,bytes)` | The original `sender`, for each REPLY received, if `sender` is not empty | The local `max_gas_per_message` | Best effort: a failed call is ignored, and the REPLY remains delivered. |

The connector is charged before `onClprMessage` is called ([execution charges](../../blueprint/channel-economics.md#1-execution-charges)). Hiero does not call `payForExecution` or `onInboundMessage`.
