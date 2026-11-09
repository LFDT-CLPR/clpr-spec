# EVM Verifier API

> **Category:** Ledger Specification (EVM) · **Applies to:** v0.2 · **Revision:** 1

This document defines the Solidity interface through which an EVM CLPR Service calls verifier contracts.

## 1. Scope

It binds the [verifier interface](../../protocol/verifier-interface.md) to the EVM. Every verifier contract deployed on a ledger of the [EVM family](README.md#1-members) MUST implement `IClprVerifier` as defined here, and the CLPR Service of such a ledger MUST call verifier contracts only through it. A verifier contract combines this API with one proof scheme of the source ledger, which defines the content of the proof bytes and of the trust anchor.

## 2. Functions

```solidity
interface IClprVerifier {
    function verifyConfig(
        bytes calldata configProofBytes,
        bytes32 channelId,
        bytes calldata endpointManifestProofBytes
    ) external view returns (
        bytes memory channelContext,
        string memory chainId,
        bytes memory serviceAddress,
        uint96 peerConfigNanos,
        Throttles memory throttles,
        bytes memory initialTrustAnchor,
        bytes memory initialTrustAnchorId,
        ClprEndpointManifest memory endpointManifest
    );

    function verifyBundle(
        bytes calldata proofBytes,
        bytes calldata trustAnchor,
        bytes calldata channelContext
    ) external view returns (
        QueueMetadata memory metadata,
        bytes[] memory messagePayloads,
        bytes memory newTrustAnchor,
        bytes memory newTrustAnchorId,
        ClprEndpointManifest memory newEndpointManifest
    );
}
```

| Function | Selector |
|---|---|
| `verifyConfig(bytes,bytes32,bytes)` | `0x65114df6` |
| `verifyBundle(bytes,bytes,bytes)` | `0x0fa8e7e7` |

### 2.1 verifyConfig

Implements [verifyConfig](../../protocol/verifier-interface.md#2-verifyconfig).

| Parameter or result | Abstract counterpart |
|---|---|
| `configProofBytes` | The configuration proof, in the layout of the proof scheme |
| `channelId` | The id of the channel being completed |
| `endpointManifestProofBytes` | The endpoint manifest proof, in the layout of the proof scheme; empty if none is supplied |
| `channelContext` | The channel context, encoded as in [§3.2](#32-channelcontext) |
| `chainId` | The peer's chain id |
| `serviceAddress` | The peer's service address |
| `peerConfigNanos` | The peer configuration's timestamp |
| `throttles` | The peer's throttles |
| `initialTrustAnchor` | The initial trust anchor |
| `initialTrustAnchorId` | The initial trust anchor's id |
| `endpointManifest` | The peer's endpoint manifest; version 0 when `endpointManifestProofBytes` is empty |

When `endpointManifestProofBytes` is non-empty, the verifier MUST return a manifest with version ≥ 1 and a `serviceAddress` equal to the returned `serviceAddress`, and MUST revert otherwise. It MUST NOT revert only because the manifest's endpoint list is empty.

### 2.2 verifyBundle

Implements [verifyBundle](../../protocol/verifier-interface.md#3-verifybundle).

| Parameter or result | Abstract counterpart |
|---|---|
| `proofBytes` | The bundle, in the wire layout of the proof scheme |
| `trustAnchor` | The trust anchor stored with the channel |
| `channelContext` | The channel context stored with the channel |
| `metadata` | The queue metadata, with the last message id and running hash ([§3.1](#31-structures)) |
| `messagePayloads` | The message payloads in id order, each the exact bytes the sender stored |
| `newTrustAnchor` | The new trust anchor; empty if the anchor is unchanged |
| `newTrustAnchorId` | The new trust anchor's id; empty if the anchor is unchanged |
| `newEndpointManifest` | The endpoint manifest carried by the bundle; version 0 if none |

## 3. Types and encodings

### 3.1 Structures

```solidity
struct QueueMetadata {
    uint64  nextMessageId;
    bytes32 sentRunningHash;
    uint64  receivedMessageId;
    bytes32 receivedRunningHash;
    uint8   state;                    // ChannelStatus
    uint64  endpointManifestVersion;
    uint64  lastMessageId;
    bytes32 lastMessageRunningHash;
}

struct Throttles {
    uint32 maxMessagesPerBundle;
    uint64 maxMessagePayloadBytes;
    uint64 maxGasPerMessage;
    uint32 maxQueueDepth;
    uint64 maxSyncBytes;
    uint32 maxLocalEndpoints;
    uint32 maxPeerEndpoints;
}

struct Endpoint {
    string ipAddress;
    uint32 port;
    bytes  tlsCertificate;
    bytes  accountId;
}

struct ClprEndpointManifest {
    uint64     version;
    bytes      serviceAddress;
    Endpoint[] endpoints;
}
```

The first six fields of `QueueMetadata` are the sender's proven [queue metadata](../../protocol/bundle.md#2-queue-metadata). `lastMessageId` and `lastMessageRunningHash` identify the bundle's last message ([partial bundles](../../protocol/bundle.md#3-partial-bundles)); both are zero when the bundle carries no messages. The trust anchor id is not part of queue metadata ([Bundle §2](../../protocol/bundle.md#2-queue-metadata)); a new trust anchor and its id are returned as `newTrustAnchor` and `newTrustAnchorId`.

`Throttles` carries the fields of the [throttles](../../protocol/ledger-configuration.md#3-throttles) in the same order. `maxMessagePayloadBytes` is widened to `uint64`; its value MUST fit the protocol's range.

`Endpoint` and `ClprEndpointManifest` carry the [endpoint and endpoint manifest](../../protocol/endpoint-manifest.md#1-endpoint) fields: `ipAddress` and `port` are the service endpoint.

### 3.2 ChannelContext

```
channelContext := channelId ‖ serviceAddress
```

`channelId` is 32 bytes and `serviceAddress` is the peer's service address, with no length prefix or padding (Solidity `abi.encodePacked`). A value shorter than 32 bytes is invalid. The `channelContext` returned by `verifyConfig` MUST equal this encoding of the `channelId` argument and the returned `serviceAddress`; a CLPR Service MAY compute it itself instead of storing the returned value.

### 3.3 Enumerations

`QueueMetadata.state` encodes the [channel status](../../protocol/channel-state-transitions.md#1-channel-status):

| Value | Status |
|---|---|
| 0 | PENDING |
| 1 | ACTIVE |
| 2 | PAUSED |
| 3 | CLOSING |
| 4 | DRAINED |
| 5 | CLOSED |

### 3.4 Scalars and absent values

| Value | Encoding |
|---|---|
| Chain id | `string`: the CAIP-2 identifier in UTF-8 |
| Service address | `bytes`: the ledger's native address (20 bytes for an EVM ledger) |
| Timestamp | `uint96`: nanoseconds since the Unix epoch (`seconds × 10^9 + nanos`) |
| Running hash | `bytes32` |
| Trust anchor, trust anchor id | `bytes`, opaque to the CLPR Service; the proof scheme defines them |

| Absent value | Convention |
|---|---|
| Unchanged trust anchor | `newTrustAnchor` and `newTrustAnchorId` are empty |
| No endpoint manifest | `version` is 0; the other manifest fields are ignored |
| No messages | `messagePayloads` is empty; `lastMessageId` and `lastMessageRunningHash` are 0 |

A trust anchor id is non-empty if and only if its trust anchor is non-empty ([Verifier interface §4](../../protocol/verifier-interface.md#4-trust-anchor-changes)).

## 4. Call semantics

- Both functions are `view`. A verifier contract MUST NOT modify state, and the CLPR Service MUST call it with `STATICCALL`. The gas the Service provides to a verifier call is a Service parameter ([Blueprint §4.2](../../blueprint/clpr-service.md#42-service-parameters)); an EVM CLPR Service MAY forward all available gas.
- A revert is a [rejection](../../protocol/verifier-interface.md#5-rejection). Return data that does not ABI-decode to the declared results is also a rejection.
- At channel completion the CLPR Service calls `verifyConfig` once and stores, with the channel, the verifier address, `initialTrustAnchor`, `initialTrustAnchorId` and `channelContext`. The verifier address does not change for the channel's life ([Channel setup §4](../../protocol/channel-setup.md#4-verifier-binding)).
- For every submitted bundle the CLPR Service calls `verifyBundle` with the stored trust anchor and channel context. It applies the result, including `newTrustAnchor` and `newTrustAnchorId`, as specified in [bundle processing](../../protocol/channel-state-transitions.md#2-bundle-processing) (Step 5 for the trust anchor).
