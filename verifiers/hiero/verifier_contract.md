# Hiero verifier contract

The shared [CLPR verifier interface](../../clpr-service-spec.md#31-verifier-contract-interface)
is transport independent. Hiero proof implementations may be native or Solidity;
a fixed precompile address is not part of the portable wire specification.

The Solidity implementation provides two independently selected profiles:

| Verifier | Authority | Bundle payload |
|---|---|---|
| `HieroVerifier` | Pinned ledger identity and WRAPS verification | Existing StateProof format |
| `HieroProvenanceVerifier` | Pinned hinTS VK, then signed successor authorizations | Versioned HieroProof envelope |

`HieroProvenanceVerifier` uses a separate hinTS V2 verification contract and EVM
BLS12-381 precompiles. Its wire format, crypto suite, authorization semantics,
bootstrap and mandatory rejection rules are defined in [proof_envelope.md](proof_envelope.md).
The companion `clpr-smart-contracts` implementation retains the legacy verifier;
it does not replace native precompiles or silently migrate existing channels.

`verifyBundle` returns proven channel data for state proofs. Provenance-only updates
return all-zero sync data with an empty message list and only a new anchor and
identifier. The service, not the verifier, persists this result.
It skips channel processing entirely for a validated authority-only update.

State proofs authenticate the channel and messages to a signed block root. The
verifier binds the channel to its stored context and any manifest to the remote
service address. The service then applies replay, running-hash, acknowledgment,
progress, and lifecycle rules. No such channel facts are implied by a key-only
signature chain.

`verifyConfig` establishes the context and initial authority. In the companion
Solidity profile the initial key is validated and pinned at deployment; the ordinary
configuration control payload is decoded, and an optional manifest proof is
verified under that pinned key. Configuration decoding alone is not cryptographic
state authentication. Channel-establishment governance must authenticate it.
