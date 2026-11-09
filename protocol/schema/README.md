# Protocol Schema

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

## 1. Scope

The `.proto` files in this directory are the normative encodings of the data that CLPR carries between ledgers: message payloads, ledger configuration, endpoints and endpoint manifests, queue metadata, bundle content and channel status. The Protocol modules define what each structure means; these files define its bytes. The messages of [endpoint sync](../endpoint-sync/README.md) are defined separately, in [`endpoint-sync/schema/`](../endpoint-sync/schema/README.md).

## 2. Encoding rules

- The definitions use `proto3` syntax. Implementations MUST serialize them with the standard protobuf binary encoding.
- Receivers apply [strict decoding](../conventions.md#3-abstract-data-structures).
- Field numbers, field types and enum values are fixed. Deprecated fields and values remain part of the wire format; receivers handle them as [strict decoding](../conventions.md#3-abstract-data-structures) states.
- Message names, enum names and the package name `clpr.v0_2` are not wire-visible. Implementations MAY use other names.
- **Canonical encoding.** A message payload (`ClprMessagePayload` and every message it contains, including the `ClprLedgerConfiguration` of a ConfigUpdate) MUST be serialized in the canonical encoding:
  - fields appear in ascending field-number order; a non-repeated field appears at most once, and a repeated field has one record per element, in list order;
  - a scalar, `bytes`, `string` or enum field that holds its default value (zero, empty, or the enum value 0) is omitted;
  - a message-typed field, and the selected member of a `oneof`, is present exactly when it is set, even if its content is empty;
  - every varint, including tags and length prefixes, uses the fewest bytes;
  - no unknown fields appear.

  The running hash covers these bytes ([payload encoding](../messaging.md#3-payload-encoding), [running hash](../messaging.md#4-running-hash)). A payload therefore has exactly one valid encoding, and any ledger can recompute the running hash from the decoded payload.

## 3. Files

Import paths are relative to the root of the specification repository.

| File | Messages and enums | Meaning |
|---|---|---|
| [`clpr_message.proto`](clpr_message.proto) | `ClprMessagePayload` (oneof: DATA, REPLY, CONTROL, REDACTED) | [Message types](../messaging.md#1-message-types) |
| | `ClprMessage` (DATA) | [Message types](../messaging.md#1-message-types) |
| | `ClprMessageReply` (REPLY), `ClprMessageReplyStatus` | [Replies](../messaging.md#7-replies) |
| | `ClprControlMessage` (CONTROL), `ClprConfigUpdate` | [Configuration propagation](../ledger-configuration.md#5-configuration-propagation) |
| | `ClprRedactedMessage` (REDACTED, deprecated) | [Redaction](../messaging.md#10-redaction-deprecated) |
| | `ClprMessageKey`, `ClprMessageValue` | [Message identifiers and queue](../messaging.md#2-message-identifiers-and-queue), [running hash](../messaging.md#4-running-hash) |
| [`clpr_ledger_configuration.proto`](clpr_ledger_configuration.proto) | `ClprLedgerConfiguration`, `Timestamp` | [Ledger configuration](../ledger-configuration.md#2-ledger-configuration) |
| | `ClprThrottles` | [Throttles](../ledger-configuration.md#3-throttles) |
| [`clpr_endpoint_manifest.proto`](clpr_endpoint_manifest.proto) | `ClprEndpoint`, `ClprServiceEndpoint` | [Endpoint](../endpoint-manifest.md#1-endpoint) |
| | `ClprEndpointManifest` | [Endpoint manifest](../endpoint-manifest.md#2-endpoint-manifest) |
| [`clpr_bundle_content.proto`](clpr_bundle_content.proto) | `ClprQueueMetadata` | [Queue metadata](../bundle.md#2-queue-metadata) |
| | `ClprBundleContent` | [Bundle content](../bundle.md#1-bundle-content); used only where a proof scheme's wire layout includes it |
| [`clpr_channel_status.proto`](clpr_channel_status.proto) | `ClprChannelStatus` | [Channel status](../channel-state-transitions.md#1-channel-status) |

Deprecated fields and values are marked `deprecated = true`.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
