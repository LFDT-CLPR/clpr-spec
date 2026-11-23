# Hiero Proof Scheme: hinTS

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

This proof scheme proves Hiero state with Merkle paths under a hinTS threshold signature, and follows the ledger's hinTS verification key as the roster changes. It shares its state paths, leaves and hashing with [hinTS with WRAPS](../hints-wraps/README.md), and carries no WRAPS proof.

## 1. Roles

| Role | Performed by |
|---|---|
| Producer | The Hiero CLPR Endpoint. It produces bundles in this scheme for channels whose peer holds a trust anchor of this scheme ([Hiero §4](../../README.md#4-proof-schemes)). |
| Verifiers | A verifier contract for EVM ledgers. |

## 2. Trust model

**What is proven.** A bundle proves that, at the start of a block signed under a hinTS verification key that the channel trusts, the ledger's state contained the items listed in [`hints-wraps` §2](../hints-wraps/README.md#2-trust-model): the sender's channel record, the outbound queue entries of the bundle's messages and, optionally, the endpoint manifest. Each item is a leaf of the state tree, linked to the block root by a SHA-256 Merkle path.

**Signature.** The block root is signed with a hinTS threshold signature (BLS12-381). A signature is valid only if the signing nodes hold **more than 1/2 of the consensus weight** of the roster that the hinTS verification key commits to.

**Binding to the ledger.** The trust anchor holds the hash of one hinTS verification key. The key changes when the roster changes. A bundle signed under a later key carries a **provenance chain**: each key in it is signed by its predecessor, with more than 1/2 of the predecessor's weight, starting from the key the channel trusts.

**Initial key.** The initial key is the key that signed the configuration proof ([§9](#9-configuration-and-manifest-proofs)). The registrant therefore chooses the authority the channel starts from, and channel users trust that choice ([OI-1](../../../../protocol/open-issues.md#oi-1-what-the-configuration-proof-must-authenticate)). The verifier ignores the configuration's `initial_trust_anchor` and `initial_trust_anchor_id`. The configuration proof therefore binds the `chain_id`, `service_address` and throttles that `verifyConfig` returns to the key that signed it, not to a particular Hiero ledger.

**Binding to the CLPR Service and channel.** As in [`hints-wraps` §2](../hints-wraps/README.md#2-trust-model): the ledger's one CLPR Service writes the proven items, and the verifier checks the proven channel id against the channel context.

**Finality.** A signed block is final, so a proven state cannot be reverted.

**Attacker.** To make a channel accept state that the Hiero ledger did not sign, an attacker must do one of the following:

- obtain signatures from more than 1/2 of the weight of a roster whose key the channel trusts, or that a chain from it reaches;
- be the registrant of the channel, who chooses the initial key;
- break SHA-256, keccak256, or the hinTS cryptographic assumptions.

## 3. Proof material

In addition to the abstract bundle content, the CLPR Endpoint collects, from the signed snapshot ([state read](../../bundle-aggregation.md#2-state-read-and-finality)):

| Material | Description |
|---|---|
| State-tree paths and block-root extension | As in [`hints-wraps` §3](../hints-wraps/README.md#3-proof-material) |
| Compact block signature | The hinTS verification key and hinTS signature of the ledger's signature on the block root |
| Provenance chain | When the signing key differs from the peer's anchor key: the keys from the anchor key to the signing key, each with its predecessor's signature over it |
| Block witness | In the witness form only: a block signed by the last key of the chain ([§4.4](#44-block-witness)) |

## 4. Wire layout

### 4.1 Envelope

Every proof of this scheme is a serialized `HieroProof` ([schema](schema/hiero_proof.proto)). It takes one of two forms:

| Form | Fields | Use |
|---|---|---|
| State form | `format_version`, `state_proof`, and optionally `key_provenance` | Bundles that prove ledger state, and configuration and manifest proofs |
| Witness form | `format_version`, `key_provenance`, `block_witness` | Bundles that only move the trust anchor to a later key |

The encoding is strict:

- `format_version` MUST be 1.
- Fields appear in ascending field-number order, each at most once. Every varint uses the fewest bytes.
- A field that is present is not empty. There are no unknown fields and no bytes after the last field.
- These rules also apply inside `HintsKeyProvenanceChain`, `HintsKeyProvenanceLink` and `HieroBlockWitness`.

### 4.2 State proof and signature

`state_proof` is a `StateProof` ([Hiero schema](../../schema/README.md)). A producer builds it by the producer rules of [`hints-wraps` §4.1](../hints-wraps/README.md#41-bundle), which fix the paths and their order and require `signed_block_proof`, with the leaves of [`hints-wraps` §4.2](../hints-wraps/README.md#42-leaves). The `StateProof` is carried inside the `HieroProof` envelope (Section 4.1), for bundles and for configuration and manifest proofs alike. The differences from `hints-wraps` are:

- All hashes are SHA-256 ([`hints-wraps` §4.3](../hints-wraps/README.md#43-hashing) with `D` = SHA-256). The block root is 32 bytes.
- `block_signature`, written `sig`, is exactly **2344 bytes**: `vk = sig[0:1096]`, the hinTS verification key, followed by `hs = sig[1096:2344]`, the hinTS signature. Their encodings are those of [`hints-wraps` §4.4](../hints-wraps/README.md#44-block-signature).

### 4.3 Provenance chain

`key_provenance` is a `HintsKeyProvenanceChain`:

- `initial_verification_key` is the receiver's current key, 1096 bytes.
- `links` holds 1 to 8 links, in adoption order. Each link holds `next_verification_key`, 1096 bytes, and `signature`, 1248 bytes: the predecessor's hinTS signature over the 1096 bytes of `next_verification_key`. The predecessor of the first link is `initial_verification_key`.
- No key appears twice in a chain, counting `initial_verification_key`.

The last key of the chain is the **signing key** of the proof.

### 4.4 Block witness

`block_witness` is a `HieroBlockWitness`:

| Field | Content |
|---|---|
| `timestamp` | The block timestamp: the canonical protobuf encoding of `Timestamp { int64 seconds = 1; int32 nanos = 2; }`, 1 to 16 bytes, with `seconds` non-negative and `nanos` below 10^9 |
| `sibling_hash` | 32 bytes: the right sibling of the timestamp leaf at the block root |
| `signature` | 1248 bytes: the signing key's hinTS signature over the block root |

The block root is `SHA-256(0x02 ‖ SHA-256(0x00 ‖ timestamp) ‖ sibling_hash)`: the timestamp leaf is the left child of the block root ([`hints-wraps` §5.2](../hints-wraps/README.md#52-block-root-extension)).

A witness is ordered by its **witness time** `(seconds × 2^32) + nanos`.

### 4.5 Limits

A `state_proof` carries at most 64 paths, and each path at most 64 siblings. A producer MUST stay within these limits. A verifier MAY reject a proof that exceeds them.

### 4.6 Decoding

A verifier decodes `HieroProof` and its nested messages under the strict encoding of [§4.1](#41-envelope). It decodes `state_proof` as [`hints-wraps` §4.6](../hints-wraps/README.md#46-decoding) defines, and ignores what that section lets a verifier ignore.

## 5. Encoding algorithm

The CLPR Endpoint builds the state proof as in [`hints-wraps` §5](../hints-wraps/README.md#5-encoding-algorithm), on a ledger whose block digest is SHA-256, and replaces its block signature with the signature's first 2344 bytes. Then:

```
anchor_key := the key whose keccak256 hash the peer's trust anchor holds
signer := sig[0:1096]
if signer = anchor_key then
    proof := HieroProof { format_version = 1, state_proof = sp }
else
    chain := the provenance chain from anchor_key to signer         // 1 to 8 links
    proof := HieroProof { format_version = 1, state_proof = sp, key_provenance = chain }
bundle := serialize(proof)
```

When no such state-form bundle can be sent, because the chain needs more than 8 links or the bundle would exceed a limit, the endpoint sends a witness-form bundle instead, if it has a witness for a key 1 to 8 links from `anchor_key`. It carries the chain to that key and the witness. Otherwise it sends nothing. Bundle aggregation states when each form is sent ([Hiero bundle aggregation §6](../../bundle-aggregation.md#6-producing-hints-bundles)).

## 6. Decode-and-verify algorithm

The verifier receives the bundle, the channel's trust anchor ([§7](#7-trust-anchor-changes)) and the channel context `ctx = channel_id ‖ service_address`.

The pseudocode uses `HintsVerify(vk, hs, message)` of [`hints-wraps` §6](../hints-wraps/README.md#6-decode-and-verify-algorithm), applied to `message` in place of the block root, and these functions:

```
function VerifyCompactSignature(sig, root, key_hash):
    if len(sig) ≠ 2344 then reject "block signature length"
    vk := sig[0:1096]
    hs := sig[1096:2344]
    if keccak256(vk) ≠ key_hash then reject "untrusted key"
    if 2 × le(hs[96:128]) ≤ le(vk[8:40]) then reject "signers hold at most 1/2 of the weight"
    if not HintsVerify(vk, hs, root) then reject "hinTS signature"

function Advance(key_hash, chain) → (last_hash, last_key):
    key := chain.initial_verification_key
    if len(key) ≠ 1096 or keccak256(key) ≠ key_hash then reject "chain does not start at the anchor"
    if len(chain.links) = 0 or len(chain.links) > 8 then reject "chain length"
    seen := [keccak256(key)]
    for each link in chain.links
        next := link.next_verification_key
        if keccak256(next) ∈ seen then reject "repeated key"
        append keccak256(next) to seen
        if next is not a well-formed hinTS verification key then reject "invalid key"
        VerifyCompactSignature(key ‖ link.signature, next, keccak256(key))
        key := next
    return (keccak256(key), key)

function VerifyBundle(payload, trust_anchor, ctx)
        → (metadata, messages, last_message_id, last_message_running_hash,
           new_trust_anchor, new_trust_anchor_id, new_endpoint_manifest):
    if len(trust_anchor) ≠ 64 then reject "trust anchor"
    key_hash := trust_anchor[0:32]
    checkpoint := the unsigned integer whose big-endian encoding is trust_anchor[32:64]
    proof := decode HieroProof(payload)
    if proof is in neither the state form nor the witness form then reject "proof form"

    if proof is in the witness form then
        w := proof.block_witness
        if WitnessTime(w.timestamp) ≤ checkpoint then reject "stale witness"
        (last_hash, last_key) := Advance(key_hash, proof.key_provenance)
        root := SHA-256(0x02 ‖ SHA-256(0x00 ‖ w.timestamp) ‖ w.sibling_hash)
        VerifyCompactSignature(last_key ‖ w.signature, root, last_hash)
        return (absent, [], 0, empty,
                last_hash ‖ be(WitnessTime(w.timestamp), 32), 0x01 ‖ last_hash, absent)

    new_anchor := empty
    new_anchor_id := empty
    if proof.key_provenance is present then
        (key_hash, last_key) := Advance(key_hash, proof.key_provenance)
        new_anchor := key_hash ‖ be(checkpoint, 32)
        new_anchor_id := 0x01 ‖ key_hash
    (metadata, messages, last_id, last_hash, manifest) :=
        the steps of hints-wraps §6 from "if len(ctx) < 32" onward, applied to
        payload := proof.state_proof, with D = SHA-256 (a hash of another length is rejected)
        and VerifyCompactSignature(sig, root, key_hash) in place of VerifyBlockSignature
    return (metadata, messages, last_id, last_hash, new_anchor, new_anchor_id, manifest)
```

- `VerifyCompactSignature(key ‖ link.signature, next, …)` verifies a link: the predecessor `key` signs the 1096 bytes of `next`.
- `WitnessTime(t)` is the witness time of [§4.4](#44-block-witness).
- `be(x, 32)` is the 32-byte big-endian encoding of `x`, and `le(x)` the unsigned integer whose little-endian encoding is `x`.
- A key is well formed when it is 1096 bytes, `n` is valid ([`hints-wraps` §4.4](../hints-wraps/README.md#44-block-signature)), its `total_weight` is not zero, its generator points `vk[40:136]`, `vk[136:328]` and `vk[328:520]` are not the point at infinity, and every point it holds is a canonically encoded point of the prime-order subgroup of its group.

A verifier MUST verify the last message's path and check that its key names the channel `channel_id`, as in [`hints-wraps` §6](../hints-wraps/README.md#6-decode-and-verify-algorithm).

## 7. Trust anchor changes

| Item | Value |
|---|---|
| Trust anchor | 64 bytes: `keccak256(vk) ‖ be(checkpoint, 32)`, where `vk` is the key the channel trusts and `checkpoint` is the witness time of the last witness the channel accepted, or 0 |
| Trust anchor id | 33 bytes: `0x01 ‖ keccak256(vk)` |
| Set | At channel setup: the key that signed the configuration proof, with checkpoint 0 ([§9](#9-configuration-and-manifest-proofs)) |
| Changes | A state-form proof with a provenance chain moves the anchor to the chain's last key and keeps the checkpoint. A witness-form proof moves it to the chain's last key and sets the checkpoint to the witness time. |

A chain never repeats the anchor key, so every change of anchor changes the trust anchor id: each is a [trust anchor change](../../../../protocol/verifier-interface.md#4-trust-anchor-changes). A witness-form bundle carries no messages, no queue metadata and no manifest, and proves no ledger state; it cannot carry a manifest proof ([endpoint obligations](../../../../protocol/endpoint-sync/README.md#52-endpoint-manifest)).

The first byte of the trust anchor id, `0x01`, identifies this scheme to the producer ([Hiero §4](../../README.md#4-proof-schemes)).

## 8. Rejection conditions

The verifier MUST reject the bundle when:

| # | Condition |
|---|---|
| 1 | The trust anchor is not 64 bytes, or a state-form proof is given a channel context shorter than 32 bytes. |
| 2 | The payload is not a `HieroProof` in the state form or the witness form under the strict encoding of [§4.1](#41-envelope), or its `format_version` is not 1. |
| 3 | A provenance chain does not start at the anchor key, has no links or more than 8, repeats a key, holds a malformed key, or has a link whose signature does not verify under its predecessor. |
| 4 | A block witness is malformed, its witness time is not greater than the anchor's checkpoint, or its signature does not verify under the chain's last key. |
| 5 | The block signature is not 2344 bytes, its key does not hash to the signing key hash, the signers' weight is not more than 1/2 of the total weight, or the hinTS signature does not verify for the block root. |
| 6 | A hash is not 32 bytes, or a state proof exceeds the limits of [§4.5](#45-limits) and the verifier applies them. |
| 7 | Any condition of [`hints-wraps` §8](../hints-wraps/README.md#8-rejection-conditions) other than 3 and the ledger id part of 1. |

## 9. Configuration and manifest proofs

### 9.1 Proofs

A configuration proof is a `HieroProof` in the state form with no `key_provenance`. Its `state_proof` holds the ledger configuration leaf, as in [`hints-wraps` §9.1](../hints-wraps/README.md#91-proofs). A manifest proof is a `HieroProof` in the state form with no `key_provenance`, whose `state_proof` holds the endpoint manifest leaf.

A registrant makes them from the `hints-wraps` proofs that the ledger's queries return ([Hiero §4](../../README.md#4-proof-schemes)): it replaces the block signature with its first 2344 bytes and wraps the `StateProof` as `HieroProof { format_version = 1, state_proof = … }`. This requires a ledger whose block digest is SHA-256.

### 9.2 Verification

```
function VerifyConfig(config_proof, channel_id, manifest_proof)
        → (ctx, chain_id, service_address, config_timestamp, throttles,
           initial_trust_anchor, initial_trust_anchor_id, endpoint_manifest):
    proof := decode HieroProof(config_proof)
    if proof is not in the state form or proof.key_provenance is present then reject "config proof form"
    sp := proof.state_proof
    vk := sp.signed_block_proof.block_signature[0:1096]
    if vk is not a well-formed hinTS verification key then reject "invalid key"
    key_hash := keccak256(vk)
    p := the first path of sp
    if p.content is not state_item_leaf then reject "no state item leaf"
    root := PathRoot(p), with D = SHA-256                          // hints-wraps §6
    VerifyCompactSignature(sp.signed_block_proof.block_signature, root, key_hash)
    config := the ledger configuration leaf of p                   // tag 474, as in hints-wraps §9.2
    if manifest_proof = empty then
        manifest := ClprEndpointManifest { version = 0 }
    else
        manifest := the endpoint manifest leaf of the state-form manifest_proof, whose
                    signature VerifyCompactSignature checks under key_hash
        if manifest.version = 0 then reject "manifest version"
        if manifest.service_address ≠ config.service_address then reject "manifest service address"
    return (channel_id ‖ config.service_address, config.chain_id, config.service_address,
            config.timestamp, config.throttles,
            key_hash ‖ be(0, 32), 0x01 ‖ key_hash, manifest)
```

The configuration proof establishes the initial key: the key that signed it. Which other values the configuration proof must authenticate is open issue [OI-1](../../../../protocol/open-issues.md#oi-1-what-the-configuration-proof-must-authenticate).

A verifier MUST reject the configuration proof when it is not in the state form, carries a provenance chain, holds a malformed key, holds no configuration leaf, or fails the checks of `VerifyCompactSignature`; and the manifest proof when it is not in the state form, carries a provenance chain, is signed under another key, or proves a manifest that has version 0 or names another service address.
