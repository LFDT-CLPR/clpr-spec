# Besu Schema

This directory holds the encodings that the Besu proof schemes use. The [Protocol schema](../../../protocol/schema.md#1-scope) states the encoding rules that apply to them. Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_bundle_content.proto`](clpr_bundle_content.proto) | `ClprQueueMetadata` | [Queue metadata](../../../protocol/bundle.md#2-queue-metadata). Field 6, `trust_anchor_id`, is the informational trust anchor id of that section. |
| | `ClprBundleContent` | [Bundle content](../../../protocol/bundle.md#1-bundle-content), as the Besu wire layout carries it ([proof encoding](../ledger.md#34-proof-encoding)) |
| [`clpr_qbft_ledger_configuration_payload.proto`](clpr_qbft_ledger_configuration_payload.proto) | `ClprQbftLedgerConfigurationPayload`, `QbftContractModeValidatorSource`, `BlockHeader`, `StorageProofEntry` | The protobuf form of a configuration proof ([qbft-header §9.1](../proof-schemes/qbft-header.md#91-configuration-proof), [qbft-contract §9.1](../proof-schemes/qbft-contract.md#91-configuration-proof)) |
