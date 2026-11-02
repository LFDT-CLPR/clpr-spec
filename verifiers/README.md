# CLPR Verifier Specifications

Each subdirectory here documents the verifier specification for one chain. A verifier is the on-chain component that authenticates state proofs submitted by a remote relay and advances the trust anchor for a Channel.

## Interface

The normative interface is in [the CLPR service specification](../clpr-service-spec.md#31-verifier-contract-interface).
`verifyConfig` establishes the channel context and authority. `verifyBundle` returns
proven channel data and messages, or an authority-only update marked by all-zero
channel sync data and a successor authority.

Verification is stateless. Only the service applies returned authority and channel
changes. See [HieroProof V1](hiero/proof_envelope.md) for the opt-in key-provenance
profile, its proposed HAPI schema, and the authorization-versus-adoption distinction.

## Directory layout

Each chain directory provides these core documents and may add profile-specific schemas or references:

| File | Contents |
|------|----------|
| `state_proof.md` | Wire format of the proof bytes passed to `verifyBundle` (and `verifyConfig`). Covers cryptographic primitives, proof structure, construction on the relay side, and verification steps on-chain. |
| `verifier_contract.md` | The `IClprVerifier` implementation: what `verifyConfig` and `verifyBundle` validate, inputs and outputs, and the implementation reference. |
| `trust_anchor.md` | Binary layout of the trust anchor, how it is seeded at channel setup, and the full rotation lifecycle — detection, bundle inclusion, and on-chain update. |

## Chains

| Chain | Directory | Trust anchor type | Status |
|-------|-----------|-------------------|--------|
| Hiero | `hiero/` | Ledger ID/WRAPS, or explicitly trusted hinTS VK | Key-provenance extension proposed |
| QBFT (Besu) | `qbft/` | ABI-encoded validator + epoch | Production |

Hiero additionally contains `proof_envelope.md` (the normative V1 profile) and
`hiero_proof.proto` (its proposed HAPI schema). Its core documents link to those
shared definitions rather than duplicate the wire and authorization rules.

## Exceptions

A verifier must authenticate successor authority with a state-proven commitment
([proof system compatibility requirement](../clpr-service-spec.md#proof-system-compatibility-requirement))
unless its rule is listed here. A listed rule applies only to Channels whose verifier implements
it, and its specification states the trust assumptions, the failure modes, and any irreversible
loss of liveness or settlement it permits.

| Rule | Verifier | Specification |
|------|----------|---------------|
| Hiero V1 signed successor authorization | `HieroProvenanceVerifier` | [proof_envelope.md](hiero/proof_envelope.md) |

## Recommended topics

### `state_proof.md`
1. **Overview** — what this chain's state proof scheme proves and its role in bundle verification
2. **Cryptographic primitives** — hash functions, signature schemes, curve parameters
3. **Wire format** — exact binary/protobuf/RLP structure of the `proofBytes` argument passed to `verifyBundle`
4. **Storage layout** — which slots or state leaves are proven and how their addresses are derived
5. **Proof construction** — relay-side steps: what RPC calls are made, how the proof is assembled
6. **Proof verification** — on-chain verifier steps: what the contract checks and in what order

### `verifier_contract.md`
1. **Overview** — what chain authority this verifier authenticates
2. **verifyConfig** — inputs, validation steps, outputs (including `initialTrustAnchor`)
3. **verifyBundle** — inputs, validation steps, outputs (including `newTrustAnchor`)
4. **Implementation reference** — Solidity source path and, where applicable, native precompile address

### `trust_anchor.md`
1. **Overview** — what signing authority the trust anchor represents for this chain
2. **Wire format** — byte-level layout with field names, types, and sizes
3. **Initial anchor derivation** — how `verifyConfig` seeds the trust anchor at channel setup from the config proof
4. **Rotation lifecycle**
   - *Detection* — what on-chain event signals rotation; how the relay observes it
   - *Bundle inclusion* — what rotation data is carried in the bundle payload
   - *On-chain update* — how `verifyBundle` validates and returns `newTrustAnchor`
5. **Security properties** — what guarantees the trust anchor provides and its failure modes

## Adding a new chain

1. Create a subdirectory named after the chain (lowercase, no spaces).
2. Add `state_proof.md`, `verifier_contract.md`, and `trust_anchor.md` covering the topics above. Profile-specific schemas and shared normative documents may supply details through explicit links.
3. Implement `IClprVerifier` in `clpr-smart-contracts/src/verifiers/<chain>/`.
4. Register the verifier address in the `ClprService` deployment for the target network.
5. Add an inbound `BundlePayloadCodec` in `clpr-relay` if the chain can act as a remote peer.
6. Add the chain to the table above with its trust anchor type and status.

Key questions to answer in each file:
- **state_proof.md**: What cryptographic commitment scheme does the chain use? What storage slots or state leaves are proven? How does the relay construct the proof, and how does the verifier check it?
- **verifier_contract.md**: What does `verifyConfig` authenticate? What does `verifyBundle` authenticate? What invariants must hold for a proof to be accepted?
- **trust_anchor.md**: What authority does the trust anchor represent? How is it seeded? What event on the remote chain triggers rotation, and how does the relay detect and carry the rotation through?
