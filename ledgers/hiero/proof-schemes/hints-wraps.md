# Hiero Proof Scheme: hinTS with WRAPS

> **Category:** Ledger Specification (Hiero) · **Applies to:** v0.2 · **Revision:** 1

This proof scheme proves Hiero state with Merkle paths under a hinTS threshold signature that WRAPS binds to the ledger id.

## 1. Status

| Role | Implemented by |
|---|---|
| Producer | The Hiero CLPR Endpoint. It produces bundles, configuration proofs and endpoint manifest proofs in this scheme. |
| Verifiers | On Hiero, the built-in verifier at `0x…016e` ([built-in verifiers](../README.md#3-built-in-verifiers)). On EVM ledgers, a verifier contract. |

## 2. Trust model

**What is proven.** A bundle proves that, at the start of a block signed by the Hiero ledger with ledger id `L`, the ledger's state contained:

- the sender's channel record, which holds the sender's [queue metadata](../../../protocol/bundle.md#2-queue-metadata);
- the outbound queue entries of the bundle's messages, each with its payload and its running hash;
- optionally, the ledger's endpoint manifest.

Each item is a leaf of the ledger's state tree. A SHA-384 Merkle path links each leaf to the block root, and the block root is signed by the ledger.

**Signature.** The block root is signed with a hinTS threshold signature (BLS12-381). A signature is valid only if the signing nodes hold **more than 1/2 of the consensus weight** of the roster that the hinTS verification key commits to.

**Binding to the ledger.** Each signature carries a WRAPS proof (a recursive proof over BN254). It proves that the hinTS verification key descends, through the chain of roster changes, from the genesis roster whose hash is the ledger id. Roster changes therefore need no change of trust anchor.

**Binding to the CLPR Service and channel.** A Hiero ledger has one CLPR Service, and only that Service writes the state items above. The ledger id therefore identifies the Service. The verifier binds the bundle to the channel by checking the proven channel id against the channel context.

**Finality.** A signed block is final, so a proven state cannot be reverted.

**Attacker.** To forge a bundle, an attacker must do one of the following:

- obtain signatures from more than 1/2 of the weight of a roster of ledger `L`;
- forge a WRAPS proof, by corrupting the chain of roster changes from the genesis roster or by breaking the proof system;
- break SHA-384, or the hinTS or WRAPS cryptographic assumptions.

The [configuration proof](#9-configuration-and-manifest-proofs) is verified against a ledger id that the verifier holds independently of the proof. Which configuration values it must authenticate is open issue [OI-1](../../../protocol/open-issues.md#oi-1-what-the-configuration-proof-must-authenticate).

## 3. Proof material

In addition to the abstract bundle content, the CLPR Endpoint collects, from the signed snapshot ([state read](../bundle-aggregation.md#2-state-read-and-finality)):

| Material | Description |
|---|---|
| State-tree paths | For each proven leaf, the sibling hashes from the leaf to the root of the block's starting state |
| Block-root extension | The five sibling hashes that link the starting-state root to the block root ([§5.2](#52-block-root-extension)) |
| Block signature | The ledger's signature on the block root: hinTS verification key, hinTS signature and WRAPS proof |

## 4. Wire layout

### 4.1 Bundle

A bundle payload is a serialized `StateProof` protobuf message, with no envelope or version byte. Configuration proofs and manifest proofs use the same message ([§9](#9-configuration-and-manifest-proofs)).

```proto
message StateProof {
  repeated MerklePath paths = 1;
  oneof proof {
    TssSignedBlockProof signed_block_proof = 2;
  }
}

message MerklePath {
  repeated SiblingNode siblings = 1;   // from the leaf towards the root
  uint32 next_path_index = 2;
  oneof content {
    bytes hash = 3;
    bytes state_item_leaf = 4;
    bytes block_item_leaf = 5;
    bytes timestamp_leaf = 6;
  }
}

message SiblingNode {
  bool is_left = 1;
  bytes hash = 2;
}

message TssSignedBlockProof {
  bytes block_signature = 1;
}
```

A producer MUST build a bundle as follows:

- Every path is an **independent** path from one leaf to the block root. Its `content` is `state_item_leaf`, and `next_path_index = 0xFFFFFFFF`. The other content kinds are not used.
- The paths are in this order: one channel leaf; the manifest leaf, if present; then one leaf per message, in ascending and contiguous message id order. The last path is the bundle's last message.
- `signed_block_proof` is present.

### 4.2 Leaves

A leaf is a serialized `StateItem`:

```proto
message StateItem {
  StateKey key = 2;
  StateValue value = 3;
}
```

`StateKey` and `StateValue` are each a protobuf `oneof` over the ledger's state items. The field number identifies the item. A verifier identifies a leaf by the first tag of its `StateValue` bytes, `field_number × 8 + 2` (protobuf wire type 2):

| State item | Field | `StateValue` tag | `StateKey` | `StateValue` content |
|---|---|---|---|---|
| Ledger configuration (singleton) | 59 | 474 | `singleton = 59` (field 1) | `ClprLedgerConfiguration` |
| Channel | 60 | 482 | field 60: `ProtoBytes { bytes value = 1; }` holding the channel id | `ClprChannel` |
| Outbound queue entry | 62 | 498 | field 62: `ClprMessageKey` | `ClprMessageValue` |
| Endpoint manifest (singleton) | 66 | 530 | `singleton = 66` (field 1) | `ClprEndpointManifest` |

`ClprLedgerConfiguration`, `ClprEndpointManifest`, `ClprMessageKey` and `ClprMessageValue` are defined in the [Protocol schema](../../../protocol/schema/README.md).

`ClprChannel` is a Hiero state message with fields numbered 1 to 20. The fields a verifier reads are:

| Field | Number | Type |
|---|---|---|
| `channel_id` | 1 | `bytes` (32) |
| `status` | 7 | channel status enum (PENDING 0 … CLOSED 5) |
| `next_message_id` | 8 | `uint64` |
| `acked_message_id` | 9 | `uint64` |
| `sent_running_hash` | 10 | `bytes` (32) |
| `received_message_id` | 11 | `uint64` |
| `received_running_hash` | 12 | `bytes` (32) |
| `endpoint_manifest_version` | 20 | `uint64` |

### 4.3 Hashing

All Merkle hashes are SHA-384 (48 bytes), with a one-byte domain prefix:

| Node | Hash |
|---|---|
| Leaf | `SHA-384(0x00 ‖ state_item_leaf)` |
| Node with one child `c` | `SHA-384(0x01 ‖ c)` |
| Node with children `l`, `r` | `SHA-384(0x02 ‖ l ‖ r)` |

A path folds its siblings from the leaf upwards:

| Sibling | Step |
|---|---|
| `hash` empty | Single-child node: `h := SHA-384(0x01 ‖ h)` |
| `is_left = true` | `h := SHA-384(0x02 ‖ hash ‖ h)` |
| `is_left = false` | `h := SHA-384(0x02 ‖ h ‖ hash)` |

A single-child node is encoded inside the path as a sibling with an empty hash. Paths are not split at single-child nodes.

### 4.4 Block signature

`block_signature`, written `sig` below, is exactly **3432 bytes**:

| Bytes | Part |
|---|---|
| `sig[0:1096]` | `vk`: hinTS verification key |
| `sig[1096:2728]` | `hs`: hinTS aggregate signature |
| `sig[2728:3432]` | `wp`: WRAPS proof (704 bytes) |

The parts use these encodings:

| Element | Encoding |
|---|---|
| BLS12-381 and BN254 scalar | 32 bytes, little-endian |
| BLS12-381 G1 point | 96 bytes, uncompressed: `x ‖ y`, each coordinate 48 bytes, big-endian |
| BLS12-381 G2 point | 192 bytes, uncompressed: `x.c1 ‖ x.c0 ‖ y.c1 ‖ y.c0`, each 48 bytes, big-endian, where a coordinate is `c0 + c1 × u` |
| BN254 G1 point | 32 bytes, compressed: `x`, little-endian. In the last byte, bit 7 is set if `y` is the larger of its two possible values and bit 6 marks the point at infinity. |
| BN254 G2 point | 64 bytes, compressed: `x.c0 ‖ x.c1`, each 32 bytes, little-endian, with the flags of a BN254 G1 point in the last byte |

In a BLS12-381 point, the three most significant bits of the first byte are flag bits. They are zero for a point other than the point at infinity. The hinTS key and signature use BLS12-381 elements; the WRAPS proof uses BN254 elements.

The parts of the hinTS verification key and signature that the verifier reads directly:

| Part | Bytes | Content |
|---|---|---|
| Verification key | `vk[0:8]` | `n`, the number of key slots: `uint64`, little-endian. MUST be a power of two from 2 to 2^32 inclusive. |
| Verification key | `vk[8:40]` | `total_weight`: BLS12-381 scalar |
| Signature | `hs[0:96]` | Aggregate public key: G1 point |
| Signature | `hs[96:128]` | `aggregate_weight`: BLS12-381 scalar |
| Signature | `hs[128:320]` | Aggregate BLS signature: G2 point |

The remaining bytes of the key and signature are the commitments and openings of the hinTS protocol. In the WRAPS proof, the initial state `z_0[0]` is `wp[40:72]` and the current state `z_i[1]` is `wp[144:176]`, each a BN254 scalar.

### 4.5 Limits

The scheme sets no maximum number of paths or bundle size. A verifier MAY bound the number of paths, or the gas, it accepts. A receiving deployment then sets its throttles within that bound ([configuration parameters](../../../blueprint/clpr-service.md#4-configuration-parameters)).

### 4.6 Decoding

This scheme defines how a verifier decodes its own messages: `StateProof`, `MerklePath`, `SiblingNode`, `TssSignedBlockProof`, `StateItem`, `StateKey`, `StateValue` and `ClprChannel`. In a bundle, a verifier ignores:

1. a path whose `content` is not `state_item_leaf`;
2. the `next_path_index` of every path;
3. a leaf whose `StateValue` tag is not 482, 498 or 530;
4. every channel leaf and manifest leaf except the last of each;
5. the fields of `ClprChannel` with numbers 1 to 20 that are not listed in [§4.2](#42-leaves);
6. the block-root extension siblings, which it folds like any other sibling without interpreting them.

A verifier MAY instead reject a bundle that contains a path as in item 1, a `next_path_index` other than `0xFFFFFFFF`, a leaf as in item 3, or more than one channel leaf or manifest leaf. It MAY reject an unknown field in the messages of this scheme, and a `ClprChannel` field with a number outside 1 to 20. A configuration or manifest proof is read only through its first path ([§9.2](#92-verification)).

The Protocol schema messages carried in leaves (`ClprLedgerConfiguration`, `ClprEndpointManifest`, `ClprMessageKey`, `ClprMessageValue` and the payload it contains) are decoded under the Protocol's [strict decoding](../../../protocol/conventions.md#3-abstract-data-structures) rule.

## 5. Encoding algorithm

### 5.1 Bundle

The CLPR Endpoint builds a bundle from the content selected by [bundle aggregation](../bundle-aggregation.md). `StateTreeSiblings(snapshot, key)` returns the siblings from the leaf to the root of the snapshot's starting state, encoded as in [§4.3](#43-hashing), and `BlockRootExtension` is defined in [§5.2](#52-block-root-extension). All values are read from the snapshot.

```
snapshot := the signed snapshot
ext := BlockRootExtension(snapshot)                       // §5.2

function LeafPath(key, value) → path:
    siblings := StateTreeSiblings(snapshot, key)
    for each s in ext
        append s to siblings
    return MerklePath {
        state_item_leaf = serialize(StateItem { key = key, value = value }),
        siblings        = siblings,
        next_path_index = 0xFFFFFFFF
    }

paths := [LeafPath(channel key, channel record)]
if include_manifest then
    append LeafPath(singleton 66, endpoint manifest) to paths
for id from start to last                                 // the run selected by bundle aggregation
    append LeafPath(ClprMessageKey { channel_id = channel_id, message_id = id }, queue entry id) to paths

bundle := serialize(StateProof {
    paths              = paths,
    signed_block_proof = TssSignedBlockProof { block_signature = snapshot.signature }
})
```

### 5.2 Block-root extension

Five siblings, appended in this order to every path, extend the starting-state root to the block root:

| # | `hash` | `is_left` |
|---|---|---|
| 1 | The block's consensus-header subtree root | `false` |
| 2 | `SHA-384(0x02 ‖ previous_block_hash ‖ previous_block_roots_hash)` | `true` |
| 3 | The block tree's root of branches 5–8 | `false` |
| 4 | The block tree's root of reserved branches 9–16 | `false` |
| 5 | `SHA-384(0x00 ‖ serialize(Timestamp { seconds = s, nanos = ns }))` | `true` |

`Timestamp` is the protobuf message `Timestamp { int64 seconds = 1; int32 nanos = 2; }`, and `s` and `ns` are the seconds and nanoseconds of the block timestamp.

The result of folding is the block root hash, the 48-byte value the ledger signs.

## 6. Decode-and-verify algorithm

The verifier receives the bundle payload, the channel's trust anchor (the ledger id, [§7](#7-trust-anchor-changes)) and the channel context. A verifier bound at deployment to one ledger id uses that id instead of the trust anchor. The channel context `ctx` is passed as the bytes `channel_id ‖ service_address`, the encoding both verifier APIs use ([Hiero](../verifier-api.md#2-functions), [EVM](../../evm/verifier-api.md#32-channelcontext)).

A verifier MUST verify the paths of the channel leaf, the manifest leaf it returns and the last message leaf. It MAY verify the paths of the other message leaves. Those messages are bound by the last message's running hash, which the CLPR Service checks ([running hash](../../../protocol/messaging.md#4-running-hash)). A verifier that checks the other message leaves MUST reject the bundle if one fails ([§8](#8-rejection-conditions), condition 8). Such a verifier MAY order the message leaves by `message_id` instead of by path; it then takes the last message and the payloads in that order.

A verifier MUST NOT return a manifest with version 0. It either treats a manifest leaf with version 0 as absent, as the pseudocode does, or rejects the bundle.

The pseudocode uses these functions:

- `decode T(x)` ([pseudocode](../../../protocol/conventions.md#4-pseudocode)) decodes the bytes `x` as the message `T`, as defined in [§4.6](#46-decoding).
- `FirstTag(x)` is the first field tag of the protobuf bytes `x`; `Content(x)` is the bytes of that field. For a `StateKey` or `StateValue`, `Content` is the selected state item.
- `le(x)` is the unsigned integer whose little-endian encoding is `x`.
- `PayloadBytes(v)` is the bytes of field 1 (`payload`) of the `ClprMessageValue` `v`, exactly as they appear in the leaf.
- `HintsVerify(vk, hs, root)` verifies the signature by the hinTS protocol:
  - the key and signature lengths are 1096 and 1632 bytes, the root is 48 bytes, and `n` is valid ([§4.4](#44-block-signature));
  - the aggregate public key and `aggregate_weight` are the aggregate key and total weight of a subset of the key slots committed in `vk`, shown by the signature's KZG openings, with the Fiat–Shamir domain tag `HINTS_SIG_BLS12381:FIAT_SHAMIR`;
  - the aggregate BLS signature is valid for `root` under the aggregate public key, hashing to G2 with the domain tag `BLS_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_POP_`.
- `WrapsVerify(wp, ledger_id, vk)` verifies the WRAPS proof under the scheme's fixed WRAPS verification key, and requires `z_0[0] = le(ledger_id)` and `z_i[1] = Poseidon(vk)`.

The full hinTS and WRAPS verification parameters (the WRAPS verification key, the Poseidon parameters and the full hinTS verification steps) are not yet specified in this revision ([OI-8](../../../protocol/open-issues.md#oi-8-hints-and-wraps-verification-parameters)).

```
function PathRoot(path) → root:
    h := SHA-384(0x00 ‖ path.state_item_leaf)
    for each s in path.siblings
        if len(s.hash) = 0 then
            h := SHA-384(0x01 ‖ h)
        else if s.is_left then
            h := SHA-384(0x02 ‖ s.hash ‖ h)
        else
            h := SHA-384(0x02 ‖ h ‖ s.hash)
    return h

function VerifyBlockSignature(ledger_id, sig, root):
    if len(sig) ≠ 3432 then reject "block signature length"
    vk := sig[0:1096]
    hs := sig[1096:2728]
    wp := sig[2728:3432]
    if not WrapsVerify(wp, ledger_id, vk) then reject "WRAPS proof"
    total := le(vk[8:40])
    agg := le(hs[96:128])
    if 2 × agg ≤ total then reject "signers hold at most 1/2 of the weight"
    if not HintsVerify(vk, hs, root) then reject "hinTS signature"

function VerifyBundle(payload, trust_anchor, ctx)
        → (metadata, messages, last_message_id, last_message_running_hash,
           new_trust_anchor, new_trust_anchor_id, new_endpoint_manifest):
    if the verifier is bound to a ledger id B then
        ledger_id := B
    else
        ledger_id := trust_anchor
    if len(ledger_id) ≠ 32 then reject "ledger id"
    if len(ctx) < 32 then reject "channel context"
    channel_id := ctx[0:32]
    service_address := ctx[32:len(ctx)]

    sp := decode StateProof(payload)
    if sp.signed_block_proof is absent then reject "no block signature"

    channel := absent
    manifest := absent
    leaves := []
    for each p in sp.paths
        if p.content is state_item_leaf then
            item := decode StateItem(p.state_item_leaf)
            tag := FirstTag(item.value)
            if tag = 482 then
                channel_path := p
                channel := decode ClprChannel(Content(item.value))
            else if tag = 498 then
                key := decode ClprMessageKey(Content(item.key))
                value := decode ClprMessageValue(Content(item.value))
                append (p, key, value) to leaves
            else if tag = 530 then
                manifest_path := p
                manifest := decode ClprEndpointManifest(Content(item.value))

    if channel = absent then reject "no channel leaf"
    root := PathRoot(channel_path)
    VerifyBlockSignature(ledger_id, sp.signed_block_proof.block_signature, root)
    if channel.channel_id ≠ channel_id then reject "channel mismatch"

    if manifest ≠ absent and manifest.version = 0 then
        manifest := absent                    // a verifier MAY instead reject "manifest version"
    if manifest ≠ absent then
        if PathRoot(manifest_path) ≠ root then reject "manifest path"
        if manifest.service_address ≠ service_address then reject "manifest service address"

    messages := []
    last_id := 0
    last_hash := empty
    if len(leaves) > 0 then
        (last_path, last_key, last_value) := leaves[len(leaves) − 1]
        if PathRoot(last_path) ≠ root then reject "last message path"
        if last_key.channel_id ≠ channel_id then reject "message of another channel"
        last_id := last_key.message_id
        last_hash := last_value.running_hash_after_processing
        first_id := last_id − len(leaves) + 1
        if first_id ≤ channel.acked_message_id then reject "first message not after acked_message_id"
        if last_id ≥ channel.next_message_id then reject "last message id not below next_message_id"
        // Optional: for i from 0 to len(leaves) − 2, check leaves[i] as in §8, condition 8.
        for each leaf in leaves
            (p, key, value) := leaf
            append PayloadBytes(value) to messages

    metadata := QueueMetadata {
        next_message_id           = channel.next_message_id,
        sent_running_hash         = channel.sent_running_hash,
        received_message_id       = channel.received_message_id,
        received_running_hash     = channel.received_running_hash,
        status                    = channel.status,
        endpoint_manifest_version = channel.endpoint_manifest_version
    }
    // A verifier bound to one ledger id MAY return a trust anchor update in place of the two empty values (§7).
    return (metadata, messages, last_id, last_hash, empty, empty, manifest)
```

Every value the verifier returns comes from the proof. Nothing is taken from unproven input. The messages are in path order, which is ascending message id order. The source's `trust_anchor_id` is not returned ([queue metadata](../../../protocol/bundle.md#2-queue-metadata)).

The verifier API of the destination ledger defines how this content is returned: the [Hiero Verifier API](../verifier-api.md) or the [EVM Verifier API](../../evm/verifier-api.md).

## 7. Trust anchor changes

| Item | Value |
|---|---|
| Trust anchor | The 32-byte ledger id of the peer ledger |
| Trust anchor id | The ledger id |
| Set | At channel setup: the ledger id against which the configuration proof was verified ([§9](#9-configuration-and-manifest-proofs)) |
| Changes | Never. The ledger id is fixed, and the WRAPS proof in each signature covers roster changes. This scheme defines no ledger-id succession. |

A verifier of this scheme reports no trust anchor change. Except for the trust anchor update below, `new_trust_anchor` and `new_trust_anchor_id` are empty.

A verifier MAY keep an internal cache hint, for example the hash of a hinTS verification key whose WRAPS proof it has already verified, so that it can skip repeated work. A verifier bound at deployment to a single ledger id MAY return such a hint as `new_trust_anchor`, to be stored with the channel and passed back on later calls: a [trust anchor update](../../../protocol/verifier-interface.md#4-trust-anchor-changes). In that case `new_trust_anchor_id` MUST be the ledger id. A hint never changes the trust anchor's meaning: the verifier MUST verify every signature against the ledger id, and a hint MUST NOT change whether a bundle is accepted. A verifier that reads the ledger id from the trust anchor MUST NOT return a hint.

## 8. Rejection conditions

The verifier MUST reject the bundle when:

| # | Condition |
|---|---|
| 1 | The ledger id (the trust anchor, or the verifier's bound ledger id) is not 32 bytes, or the channel context is shorter than 32 bytes. |
| 2 | The payload does not decode as a `StateProof`, or has no `signed_block_proof`. |
| 3 | The block signature is not 3432 bytes, the WRAPS proof does not verify for the ledger id and the hinTS verification key, `n` is not a power of two from 2 to 2^32, the signers' weight is not more than 1/2 of the total weight, or the hinTS signature does not verify for the block root. |
| 4 | There is no channel leaf, or its `channel_id` differs from the channel context. |
| 5 | A manifest leaf with a version other than 0 is present, and its path does not fold to the block root or its `service_address` differs from the channel context. |
| 6 | Messages are present and the last message path does not fold to the block root, or its key names another channel. |
| 7 | Messages are present and the first message id is not greater than the channel's `acked_message_id`, or the last message id is not below the channel's `next_message_id`. |
| 8 | The verifier checks the other message leaves, and a path does not fold to the block root, a key names another channel, or the message ids, in ascending order, are not the contiguous run from the first message id to the last. |
| 9 | A leaf that the verifier reads does not decode as [§4.6](#46-decoding) requires, or a proven value cannot be represented in the verifier API's return types. |

The verifier MAY also reject the bundle in the cases [§4.6](#46-decoding) allows, when the message leaves are not in ascending id order by path, and when a manifest leaf has version 0 ([§6](#6-decode-and-verify-algorithm)).

## 9. Configuration and manifest proofs

### 9.1 Proofs

At channel setup the registrant supplies a configuration proof and an endpoint manifest proof of the peer Hiero ledger. Each is a serialized `StateProof` ([§4.1](#41-bundle)). A producer MUST build each with exactly one path, as in [§5.1](#51-bundle) for one leaf:

| Proof | Leaf |
|---|---|
| Configuration proof | The ledger configuration singleton (field 59, tag 474) |
| Manifest proof | The endpoint manifest singleton (field 66, tag 530) |

A Hiero ledger's queries for its ledger configuration and its endpoint manifest return the value together with such a proof, made from the latest signed snapshot. The configuration in the response is the current one and can differ from the proven value; `verifyConfig` returns the proven value. The two proofs can come from different blocks. The manifest proof can be empty.

### 9.2 Verification

The verifier MUST verify the configuration proof against a ledger id that it holds independently of the proof, for example one fixed when the verifier is deployed. It returns that id as the initial trust anchor.

```
function VerifyConfig(config_proof, channel_id, manifest_proof)
        → (ctx, chain_id, service_address, config_timestamp, throttles,
           initial_trust_anchor, initial_trust_anchor_id, endpoint_manifest):
    ledger_id := the ledger id the verifier holds for the peer ledger

    sp := decode StateProof(config_proof)
    if len(sp.paths) = 0 then reject "no path"
    p := sp.paths[0]
    if p.content is not state_item_leaf then reject "no state item leaf"
    item := decode StateItem(p.state_item_leaf)
    if FirstTag(item.value) ≠ 474 then reject "not the ledger configuration"
    config := decode ClprLedgerConfiguration(Content(item.value))
    if config.initial_trust_anchor ≠ ledger_id then reject "wrong ledger"
    if sp.signed_block_proof is absent then reject "no block signature"
    VerifyBlockSignature(ledger_id, sp.signed_block_proof.block_signature, PathRoot(p))

    if manifest_proof = empty then
        manifest := ClprEndpointManifest { version = 0 }
    else
        mp := decode StateProof(manifest_proof)
        if len(mp.paths) = 0 then reject "no path"
        q := mp.paths[0]
        if q.content is not state_item_leaf then reject "no state item leaf"
        mitem := decode StateItem(q.state_item_leaf)
        if FirstTag(mitem.value) ≠ 530 then reject "not the endpoint manifest"
        manifest := decode ClprEndpointManifest(Content(mitem.value))
        if mp.signed_block_proof is absent then reject "no block signature"
        VerifyBlockSignature(ledger_id, mp.signed_block_proof.block_signature, PathRoot(q))
        if manifest.version < 1 then reject "manifest version"
        if manifest.service_address ≠ config.service_address then
            reject "manifest service address"

    return (channel_id ‖ config.service_address, config.chain_id, config.service_address,
            config.timestamp, config.throttles, ledger_id, ledger_id, manifest)
```

A verifier MAY reject a configuration or manifest proof with more than one path. The rejection conditions of [§8](#8-rejection-conditions) that concern decoding and the block signature apply to both proofs.
