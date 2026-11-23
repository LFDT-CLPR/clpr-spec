# Ledger Specifications

This directory holds the Ledger Specifications. They continue the specification at the level of one ledger: how bundle content is gathered from it, how it is proven and laid out on the wire, how it is verified on another ledger, and how a ledger's CLPR Service calls verifier contracts. Each ledger has its own directory, and ledgers that share an execution environment also share a family directory. Each document carries its own revision number.

## Ledgers

| Ledger | Specification | Verifier API | Bundle aggregation |
|---|---|---|---|
| [Hiero](hiero/README.md) | [hiero/ledger.md](hiero/ledger.md) | [hiero/verifier-api.md](hiero/verifier-api.md) | [hiero/bundle-aggregation.md](hiero/bundle-aggregation.md) |
| [Besu](besu/README.md) | [besu/ledger.md](besu/ledger.md) | [evm/verifier-api.md](evm/verifier-api.md) (EVM family) | [besu/bundle-aggregation.md](besu/bundle-aggregation.md) |

## Families

| Family | Members | Shared documents |
|---|---|---|
| [EVM](evm/README.md) | Besu | [Verifier API](evm/verifier-api.md); [evm/ledger-family.md](evm/ledger-family.md): CLPR Service interface, application and connector interfaces, channel identity, registration signatures, registration-time certificate check |

## Proof schemes

| Source ledger | Scheme | Trust anchor | Verified by |
|---|---|---|---|
| Hiero | [hints-wraps](hiero/proof-schemes/hints-wraps.md) | The ledger id | Hiero built-in verifier `0x…016e` |
| Hiero | [hints](hiero/proof-schemes/hints.md) | The hash of the current hinTS verification key, which changes with the roster | EVM verifier contract |
| Besu | [qbft-epoch](besu/proof-schemes/qbft-epoch.md) | The validator set of an anchored epoch | EVM verifier contract |
| Besu | [qbft-header](besu/proof-schemes/qbft-header.md) | A trusted validator set | EVM verifier contract; Hiero built-in verifier `0x…016f` |
| Besu | [qbft-contract](besu/proof-schemes/qbft-contract.md) | A trusted validator set | EVM verifier contract; Hiero built-in verifier `0x…016f` |

A verifier contract combines one proof scheme of the source ledger with the verifier API of the destination ledger.

## Schemas

A ledger's `schema/` directory holds the encodings that its proof schemes use, such as [Besu](besu/schema/README.md) and [Hiero](hiero/schema/README.md). [`schema/`](schema/README.md) holds the endpoint manifest encoding, which the proof schemes of more than one ledger prove. The [Protocol schema](../protocol/schema.md#1-scope) states the encoding rules that apply to all of them.
