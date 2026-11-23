# Besu Ledger Specifications

This directory holds the Ledger Specifications for Besu ledgers. Start with [ledger.md](ledger.md). Besu is a member of the [EVM family](../evm/README.md), whose directory holds its verifier API and its application and connector interfaces.

| File | Contents |
|---|---|
| [ledger.md](ledger.md) | Ledger identity, verifier API, proven storage layout, proof encoding, QBFT headers and seals, configuration-time manifest proof and registration signatures |
| [bundle-aggregation.md](bundle-aggregation.md) | How a Besu CLPR Endpoint gathers bundle content |
| [proof-schemes/qbft-epoch.md](proof-schemes/qbft-epoch.md) | The `qbft-epoch` proof scheme: validator sets from epoch boundary headers |
| [proof-schemes/qbft-header.md](proof-schemes/qbft-header.md) | The `qbft-header` proof scheme: validator sets from every block header |
| [proof-schemes/qbft-contract.md](proof-schemes/qbft-contract.md) | The `qbft-contract` proof scheme: validator sets from a validator contract's storage |
| [schema/](schema/README.md) | Encodings that the Besu proof schemes use |
