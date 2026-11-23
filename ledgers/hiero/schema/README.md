# Hiero Schema

This directory holds the encodings of the Hiero state that the Hiero proof schemes prove, and the envelope of the `hints` scheme. The [Protocol schema](../../../protocol/schema.md#1-scope) states the encoding rules that apply to them. Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_message_queue.proto`](clpr_message_queue.proto) | `ClprMessageKey`, `ClprMessageValue` | An outbound queue entry: [message identifiers and queue](../../../protocol/messaging.md#2-message-identifiers-and-queue), [running hash](../../../protocol/messaging.md#4-running-hash) |
| [`state_proof.proto`](state_proof.proto) | `StateProof`, `MerklePath`, `SiblingNode`, `TssSignedBlockProof` | A proof of state items under a signed block root ([`hints-wraps` §4](../proof-schemes/hints-wraps.md#4-wire-layout)) |
| [`clpr_channel.proto`](clpr_channel.proto) | `ClprChannel` | The channel record fields that verifiers read ([`hints-wraps` §4.2](../proof-schemes/hints-wraps.md#42-leaves)) |
| [`state_item.proto`](state_item.proto) | `StateItem`, `StateKey`, `StateValue`, `ProtoBytes` | A leaf of the state tree, with the members that CLPR proofs carry ([`hints-wraps` §4.2](../proof-schemes/hints-wraps.md#42-leaves)) |
| [`hiero_proof.proto`](hiero_proof.proto) | `HieroProof`, `HintsKeyProvenanceChain`, `HintsKeyProvenanceLink`, `HieroBlockWitness` | The envelope of the [`hints`](../proof-schemes/hints.md) scheme |
