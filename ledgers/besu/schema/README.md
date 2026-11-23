# Besu Schema

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

The `.proto` files in this directory are the encodings that the Besu proof schemes use. The [encoding rules of the Protocol schema](../../../protocol/schema/README.md#2-encoding-rules) apply, except that each proof scheme states how its verifiers decode these messages, including which fields they ignore ([conventions §3](../../../protocol/conventions.md#3-abstract-data-structures)). Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_bundle_content.proto`](clpr_bundle_content.proto) | `ClprQueueMetadata` | [Queue metadata](../../../protocol/bundle.md#2-queue-metadata). Field 6, `trust_anchor_id`, is the informational trust anchor id of that section. |
| | `ClprBundleContent` | [Bundle content](../../../protocol/bundle.md#1-bundle-content), as the Besu wire layout carries it ([proof encoding](../README.md#34-proof-encoding)) |
| [`clpr_qbft_ledger_configuration_payload.proto`](clpr_qbft_ledger_configuration_payload.proto) | `ClprQbftLedgerConfigurationPayload`, `QbftContractModeValidatorSource`, `BlockHeader`, `StorageProofEntry` | The protobuf form of a configuration proof ([qbft-header §9.1](../proof-schemes/qbft-header.md#91-configuration-proof), [qbft-contract §9.1](../proof-schemes/qbft-contract.md#91-configuration-proof)) |
