# Hiero Ledger Specifications

This directory holds the Ledger Specifications for Hiero ledgers. Start with [ledger.md](ledger.md).

| File | Contents |
|---|---|
| [ledger.md](ledger.md) | Ledger identity, verifier API, built-in verifiers, proof schemes, registration signatures, application and connector interfaces, endpoint manifest and CLPR Service operations |
| [verifier-api.md](verifier-api.md) | The verifier API through which the Hiero CLPR Service calls verifier contracts |
| [bundle-aggregation.md](bundle-aggregation.md) | How a Hiero CLPR Endpoint gathers bundle content and produces bundles |
| [proof-schemes/hints-wraps.md](proof-schemes/hints-wraps.md) | The `hints-wraps` proof scheme, verified on Hiero ledgers |
| [proof-schemes/hints.md](proof-schemes/hints.md) | The `hints` proof scheme, verified on EVM ledgers |
| [schema/](schema/README.md) | Encodings of the Hiero state that the proof schemes prove, and the envelope of the `hints` scheme |
