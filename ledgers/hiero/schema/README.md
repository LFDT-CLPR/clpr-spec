# Hiero Schema

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

The `.proto` files in this directory are the encodings of Hiero state that the Hiero proof schemes prove. The [encoding rules of the Protocol schema](../../../protocol/schema/README.md#2-encoding-rules) apply, except that each proof scheme states how its verifiers decode these messages, including which fields they ignore ([conventions §3](../../../protocol/conventions.md#3-abstract-data-structures)). Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_message_queue.proto`](clpr_message_queue.proto) | `ClprMessageKey`, `ClprMessageValue` | An outbound queue entry: [message identifiers and queue](../../../protocol/messaging.md#2-message-identifiers-and-queue), [running hash](../../../protocol/messaging.md#4-running-hash) |
| [`state_proof.proto`](state_proof.proto) | `StateProof`, `MerklePath`, `SiblingNode`, `TssSignedBlockProof` | A proof of state items under a signed block root ([`hints-wraps` §4](../proof-schemes/hints-wraps/README.md#4-wire-layout)) |
| [`clpr_channel.proto`](clpr_channel.proto) | `ClprChannel` | The channel record fields that verifiers read ([`hints-wraps` §4.2](../proof-schemes/hints-wraps/README.md#42-leaves)) |
| [`state_item.proto`](state_item.proto) | `StateItem`, `StateKey`, `StateValue`, `ProtoBytes` | A leaf of the state tree, with the members that CLPR proofs carry ([`hints-wraps` §4.2](../proof-schemes/hints-wraps/README.md#42-leaves)) |
| [`../proof-schemes/hints/schema/hiero_proof.proto`](../proof-schemes/hints/schema/hiero_proof.proto) | `HieroProof`, `HintsKeyProvenanceChain`, `HintsKeyProvenanceLink`, `HieroBlockWitness` | The envelope of the [`hints`](../proof-schemes/hints/README.md) scheme |
