# EVM Family

> **Category:** Ledger Specification (EVM) · **Applies to:** v0.2 · **Revision:** 1

This document defines what every EVM ledger shares in CLPR: the verifier API, the application and connector interfaces, channel identity, registration signatures and endpoint certificates.

## 1. Members

The EVM family is the set of ledgers whose CLPR Service, verifier contracts, applications and connectors are EVM contracts. Members share the rules of this document.

| Ledger | Specification |
|---|---|
| Besu | [besu/README.md](../besu/README.md) |

Besu is the only member documented in v0.2.

## 2. Verifier API

Members use the [EVM verifier API](verifier-api.md).

## 3. Application and connector interfaces

An EVM CLPR Service calls applications and connectors through the interfaces below. Application and connector contracts MUST implement them with these exact signatures. Their semantics are defined in [Messaging](../../protocol/messaging.md) and [Connector setup](../../protocol/connector-setup.md); this section defines the EVM binding: when each function is called, with what gas, and how its outcome is read.

On an EVM ledger, an application's identity (the `sender` of a message it sends, and the `targetApplication` of a message addressed to it) is its 20-byte address.

The gas parameters named below are CLPR Service configuration ([Configuration parameters](../../blueprint/clpr-service.md#4-configuration-parameters)); charges are defined in [Channel economics](../../blueprint/channel-economics.md#1-execution-charges).

### 3.1 Applications

```solidity
interface IClprApplication {
    function onClprMessage(bytes32 channelId, bytes calldata sender, bytes calldata messageData)
        external
        returns (bytes memory responseData);

    function onClprResponse(bytes32 channelId, uint64 messageId, uint8 status, bytes calldata responseData)
        external;
}
```

| Function | Selector |
|---|---|
| `onClprMessage(bytes32,bytes,bytes)` | `0x2ab00809` |
| `onClprResponse(bytes32,uint64,uint8,bytes)` | `0x3b74550e` |

**`onClprMessage`** delivers a DATA message ([Delivery to the application](../../protocol/messaging.md#6-delivery-to-the-application)).
- It is called on the destination's target application. If `targetApplication` is not 20 bytes or has no code, it is not called and the reply status is APPLICATION_ERROR.
- The gas limit is the local `max_gas_per_message`, reduced to what the connector can pay for.
- An ABI-encoded `bytes` return gives the reply status SUCCESS, with that value as the reply data. A revert, or return data that is not an ABI-encoded `bytes`, gives APPLICATION_ERROR, with the raw revert or return data as the reply data.

**`onClprResponse`** delivers a REPLY ([Replies](../../protocol/messaging.md#7-replies)) to the application that sent the original DATA message.
- `messageId` is the id of that DATA message, and `status` is the reply status code ([schema](../../protocol/schema/README.md)).
- It is called only if the original `sender` is 20 bytes and has code, and the original message was not redacted. An account without code receives no callback.
- The gas limit is the local `max_gas_per_message`.
- The call is best-effort: a revert is ignored, and the reply remains delivered.

### 3.2 Connectors

```solidity
interface IClprConnector {
    function authorizeOutboundMessage(
        bytes32 channelId,
        bytes calldata targetApplication,
        bytes calldata sender,
        bytes calldata messageData
    ) external returns (bool authorized);

    function payForExecution(uint256 amount) external;

    function onInboundMessage(
        bytes32 channelId,
        uint64 messageId,
        bytes calldata sender,
        bytes calldata targetApplication,
        bytes calldata messageData
    ) external;
}
```

| Function | Selector |
|---|---|
| `authorizeOutboundMessage(bytes32,bytes,bytes,bytes)` | `0x38ac1abe` |
| `payForExecution(uint256)` | `0xad5d4293` |
| `onInboundMessage(bytes32,uint64,bytes,bytes,bytes)` | `0x6983ab54` |

**`authorizeOutboundMessage`** is the connector's [authorization of an outbound message](../../protocol/connector-setup.md#4-authorization-of-outbound-messages).
- The source CLPR Service calls it while enqueuing a message. The message is enqueued only if the call returns `true`; `false` or a revert rejects it.
- It is an ordinary call, so the connector MAY update its own state, for example to apply rate limits.

**`payForExecution`** collects an execution charge.
- The CLPR Service calls it on the destination connector for an inbound DATA message whose target application was called, and on the source connector for an inbound REPLY when `onClprResponse` was called. It is not called for a zero charge.
- The gas limit is `connectorPaymentGasLimit`. The call is skipped when the connector's balance is below `amount`. It is not called when the connector is no longer registered.
- The connector MUST transfer exactly `amount` wei to the caller during the call. A revert, an exhausted gas limit, a skipped call, or any other amount is a failed charge.
- A connector SHOULD accept this call only from the CLPR Service it is registered with.

**`onInboundMessage`** notifies the destination connector that an inbound DATA message has been processed.
- It is called once for each inbound DATA message whose connector is registered, after the charge if there is one, whether or not the charge succeeded. It is also called when the target application is not called.
- The gas limit is `connectorInboundGasStipend`. It is not called when that limit is 0, when the connector contract has no code, or when the reply status is CONNECTOR_UNDERFUNDED.
- The call is best-effort: a revert is ignored.

## 4. Channel identity

An EVM CLPR Service constrains the [channel id](../../protocol/channel-setup.md#1-channel-identity) to:

```
a := the local chain id as UTF-8 bytes
b := the peer chain id as UTF-8 bytes
if keccak256(a) ≤ keccak256(b) then (lo, hi) := (a, b) else (lo, hi) := (b, a)
channelId := keccak256(lo ‖ hi ‖ publicKey ‖ salt)
```

- `publicKey` is the 64-byte key revealed at completion ([§5](#5-registration-signatures)), and `salt` is 32 bytes chosen by the registrant.
- The peer chain id is the one returned by `verifyConfig`.
- The concatenation has no length prefixes. The comparison is between `keccak256` values as 256-bit unsigned integers.

At channel completion the CLPR Service MUST reject a channel id that differs from this derivation, and MUST reject an empty chain id. The derivation gives the same id on both ledgers, so a channel with an EVM ledger on either side uses this id on both. When both ledgers of a channel are EVM ledgers, the registrant uses the same `publicKey` and `salt` on both.

## 5. Registration signatures

Channel and connector registration reveal a public key and prove possession of it ([Channel setup §2](../../protocol/channel-setup.md#2-registration), [Connector setup §2](../../protocol/connector-setup.md#2-registration)). On an EVM ledger:

| Item | Value |
|---|---|
| Public key | 64 bytes: the uncompressed secp256k1 point `X ‖ Y`, without a prefix byte |
| Signature | 65 bytes `r ‖ s ‖ v`, with `v` 27 or 28 |
| Channel message | `d = keccak256(channelId ‖ serviceAddress)` |
| Connector message | `d = keccak256(connectorId ‖ serviceAddress)` |
| Signed digest | EIP-191: `keccak256("\x19Ethereum Signed Message:\n32" ‖ d)` |

`serviceAddress` is the 20-byte address of the CLPR Service on which the registration completes. The CLPR Service MUST recover the signer's address from the signed digest and MUST reject the registration unless it equals the last 20 bytes of `keccak256(publicKey)`.

## 6. Endpoint certificates

An EVM CLPR Service MAY validate a non-empty [`tls_certificate`](../../protocol/endpoint-manifest.md#1-endpoint) when an endpoint is registered or added to its local manifest. If it does, it MUST reject the endpoint unless the value is a DER-encoded X.509 certificate whose subject public key algorithm is `rsaEncryption` and whose RSA modulus is a DER INTEGER with at least 256 content bytes (about 2048 bits). The certificate's signature and validity period are not checked. An empty value is always accepted.
