# Ledger Specifications

> **Category:** Ledger Specification (index) · **Applies to:** v0.2 · **Revision:** 1

This index lists the Ledger Specifications. They continue the specification at the level of one ledger: how bundle content is gathered from it, how it is proven and laid out on the wire, how it is verified on another ledger, and how a ledger's CLPR Service calls verifier contracts. Each document carries its own revision number.

## Ledgers

| Ledger | Specification | Verifier API | Bundle aggregation |
|---|---|---|---|
| Hiero | [hiero/README.md](hiero/README.md) | [hiero/verifier-api.md](hiero/verifier-api.md) | [hiero/bundle-aggregation.md](hiero/bundle-aggregation.md) |
| Besu | [besu/README.md](besu/README.md) | [evm/verifier-api.md](evm/verifier-api.md) (EVM family) | [besu/bundle-aggregation.md](besu/bundle-aggregation.md) |

## Families

| Family | Members | Shared documents |
|---|---|---|
| [EVM](evm/README.md) | Besu | [Verifier API](evm/verifier-api.md); application and connector interfaces; channel identity; registration signatures; endpoint certificates |

## Proof schemes

| Source ledger | Scheme | Producer | Verifiers |
|---|---|---|---|
| Hiero | [hints-wraps](hiero/proof-schemes/hints-wraps.md) | Hiero CLPR Endpoint | Hiero built-in verifier; EVM verifier contract |
| Besu | [qbft-epoch](besu/proof-schemes/qbft-epoch.md) | Besu CLPR Endpoint | EVM verifier contract; Hiero built-in verifier |
| Besu | [qbft-header](besu/proof-schemes/qbft-header.md) | None in v0.2 | EVM verifier contract |
| Besu | [qbft-contract](besu/proof-schemes/qbft-contract.md) | None in v0.2 | EVM verifier contract |

A verifier contract combines one proof scheme of the source ledger with the verifier API of the destination ledger.
