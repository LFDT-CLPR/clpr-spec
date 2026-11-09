# Hiero Verifier API

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

## 1. Scope

This document is the Hiero binding of the Protocol's [verifier interface](../../protocol/verifier-interface.md). The Hiero CLPR Service calls every verifier contract, built-in or deployed, as an EVM contract with the two functions below, and decodes their results with the ABI types in [§3](#3-types-and-encodings).

The function selectors and inputs are the same as those of the [EVM Verifier API](../evm/verifier-api.md). The `verifyBundle` return type is different, and the two are not interchangeable: a verifier written for one is decoded incorrectly by the other.

This binding does not fully conform to the Protocol. [§5](#5-conformance) states where its return type cannot express the Protocol's bundle content.

## 2. Functions

```text
function verifyConfig(
    bytes   configProof,
    bytes32 channelId,
    bytes   endpointManifestProof
) returns (VerifiedConfig);

function verifyBundle(
    bytes bundlePayload,
    bytes trustAnchor,
    bytes channelContext
) returns (VerifiedBundle);
```

| Function | Selector input | Called when | Inputs |
|---|---|---|---|
| `verifyConfig` | `verifyConfig(bytes,bytes32,bytes)` | The reveal step of [channel registration](../../protocol/channel-setup.md#2-registration) | The peer's configuration proof, the channel id, and the peer's endpoint manifest proof (can be empty), as supplied by the registrant |
| `verifyBundle` | `verifyBundle(bytes,bytes,bytes)` | Each bundle submission on the channel | The bundle payload as submitted, and the channel's stored trust anchor and channel context |

These are ABI signatures, not Solidity source. Arguments and return values use the standard Solidity ABI encoding. Each selector is the first 4 bytes of the `keccak256` of the selector input.

`channelContext` is the [channel context](../../protocol/channel-setup.md#3-channel-context) encoded as `channel_id ‖ service_address`: the 32-byte channel id followed by the raw bytes of the peer's CLPR Service address, with no padding or length prefix.

## 3. Types and encodings

### 3.1 verifyConfig return

```text
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

struct EndpointManifest {
    uint64     version;
    bytes      serviceAddress;
    Endpoint[] endpoints;
}

// VerifiedConfig: the return tuple of verifyConfig
(
    bytes            channelContext,
    string           chainId,
    bytes            serviceAddress,
    uint96           timestampNanos,
    Throttles        throttles,
    bytes            initialTrustAnchor,
    bytes            initialTrustAnchorId,
    EndpointManifest endpointManifest
)
```

The members carry the proven [ledger configuration](../../protocol/ledger-configuration.md#2-ledger-configuration) of the peer and its proven [endpoint manifest](../../protocol/endpoint-manifest.md#2-endpoint-manifest):

| Member | Meaning |
|---|---|
| `channelContext` | MUST equal `channelId ‖ serviceAddress`. The CLPR Service computes the channel context itself from those two values. |
| `chainId`, `serviceAddress` | The configuration's chain id and CLPR Service address |
| `timestampNanos` | The configuration's timestamp, in nanoseconds since the Unix epoch |
| `throttles` | The configuration's [throttles](../../protocol/ledger-configuration.md#3-throttles). Each value MUST fit the range of the Protocol field. |
| `initialTrustAnchor`, `initialTrustAnchorId` | The trust anchor and trust anchor id to store with the channel |
| `endpointManifest` | The peer's endpoint manifest; absent when `version = 0` |

### 3.2 verifyBundle return

```text
// Queue metadata: 6 fields
struct Metadata {
    uint64  nextMessageId;
    bytes32 sentRunningHash;
    uint64  receivedMessageId;
    bytes32 receivedRunningHash;
    uint8   status;
    uint64  endpointManifestVersion;
}

// VerifiedBundle: the return tuple of verifyBundle
(
    Metadata         metadata,
    bytes[]          payloads,
    bytes            newTrustAnchor,
    bytes            newTrustAnchorId,
    EndpointManifest newEndpointManifest
)
```

The tuple carries no last-message fields. The bundle's last message is encoded in `nextMessageId` and `sentRunningHash`. The members map to the abstract [bundle content](../../protocol/bundle.md#1-bundle-content) as follows:

| Abstract content | ABI member |
|---|---|
| Last message id | `nextMessageId − 1` |
| Last message running hash | `sentRunningHash` |
| Sender's `next_message_id` | Not conveyed when the bundle carries messages. When it carries none, `nextMessageId`. |
| Sender's `sent_running_hash` | Not conveyed when the bundle carries messages. When it carries none, `sentRunningHash`. |
| `received_message_id`, `received_running_hash` | `receivedMessageId`, `receivedRunningHash` |
| `status` | `status`: the channel status number (PENDING 0, ACTIVE 1, PAUSED 2, CLOSING 3, DRAINED 4, CLOSED 5) |
| `endpoint_manifest_version` | `endpointManifestVersion` |
| Message payloads | `payloads`: each a serialized message payload as defined in the [Protocol schema](../../protocol/schema/README.md), in ascending message id order |
| New trust anchor and trust anchor id | `newTrustAnchor`, `newTrustAnchorId` |
| New endpoint manifest | `newEndpointManifest` |

The tuple does not carry the source's `trust_anchor_id` ([queue metadata](../../protocol/bundle.md#2-queue-metadata)).

A verifier MUST therefore set:

- when the bundle carries messages: `nextMessageId` = last message id + 1, and `sentRunningHash` = the last message's running hash;
- when it carries none: `nextMessageId` and `sentRunningHash` = the sender's proven `next_message_id` and `sent_running_hash`.

The CLPR Service takes the bundle's first message id as `nextMessageId − n`, where `n` is the number of payloads.

### 3.3 Absent and empty values

| Value | Meaning |
|---|---|
| `metadata.nextMessageId = 0` | Queue metadata is absent. The other metadata members are ignored. The ABI can express this, but the Protocol requires queue metadata in every bundle ([bundle content](../../protocol/bundle.md#1-bundle-content)). The Hiero CLPR Service accepts such a result only when `payloads` is empty and it carries a new trust anchor or a manifest newer than the one stored with the channel. This is a local extension. |
| `EndpointManifest.version = 0` | No manifest. The other manifest members are ignored. |
| `newTrustAnchor` empty | The trust anchor is unchanged. `newTrustAnchorId` MUST be empty if and only if `newTrustAnchor` is empty. |

## 4. Call semantics

| Aspect | Rule |
|---|---|
| Target | The channel's verifier contract: a built-in verifier ([list](README.md#3-built-in-verifiers)) or a deployed contract. The verifier is fixed when the channel is created. |
| Call kind | An ordinary contract call, made by the CLPR Service. A verifier MUST NOT modify CLPR Service state ([verifier interface §1](../../protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors)). |
| Gas | The CLPR Service supplies a fixed gas limit to each call, set by its verifier gas limit [service parameter](../../blueprint/clpr-service.md#42-service-parameters). |
| Payer | The call is made on behalf of the payer of the transaction that triggered it: the channel registrant for `verifyConfig`, the bundle submitter for `verifyBundle`. No separate fee is charged for the call. |
| Result | The call succeeds only if it completes without reverting, returns a non-empty result, and the result decodes as the return type above. Each element of `payloads` MUST decode as a message payload. |
| Failure | Any other outcome is a verification failure. For `verifyConfig` the registration fails with `CLPR_VERIFIER_CONFIG_FAILED`. For `verifyBundle` the submission fails with `CLPR_BUNDLE_VERIFICATION_FAILED`, and the bundle has no effect on the channel. |

The [verifier interface](../../protocol/verifier-interface.md) defines what the CLPR Service does with a successful result.

## 5. Conformance

This binding does not fully conform to the [verifier interface](../../protocol/verifier-interface.md#3-verifybundle). The `verifyBundle` return can describe only a bundle whose last message is `nextMessageId − 1`. It cannot convey both the sender's real `next_message_id` and the bundle's last message when they differ, and it does not carry `last_message_id` or `last_message_running_hash` separately. Two consequences follow:

- **Partial bundles.** A [partial bundle](../../protocol/bundle.md#3-partial-bundles) ends before the sender's last queued message. Through this binding it appears to end at the sender's `next_message_id − 1`. A verifier that returns the sender's real `next_message_id` and `sent_running_hash` for a partial bundle makes the CLPR Service compute the wrong first message id and running hash, and the bundle is rejected.
- **Bundles without messages.** Through this binding such a bundle is accepted only if the sender's `next_message_id − 1` equals the receiver's `received_message_id`.
