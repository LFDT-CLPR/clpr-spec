# Besu Proof Scheme: QBFT Contract

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

This proof scheme proves Besu CLPR Service state under QBFT seals, and follows validator changes through a validator contract's storage.

## 1. Status

| Role | Implemented by |
|---|---|
| Producer | None in v0.2 |
| Verifiers | A verifier contract for EVM ledgers |

## 2. Trust model

This scheme is for Besu networks that keep the validator set in a **validator contract** (QBFT contract validator selection): an array of addresses in the contract's storage. A bundle proves values in the CLPR Service's storage at a final block `H` ([proven storage layout](../README.md#3-proven-storage-layout)).

The validators of block `N` are the set held by the validator contract in the state of block `N − 1`. The verifier trusts a set `T` and follows changes through **hops**: the blocks at which the set changes. A hop is sealed by the outgoing set, and its state holds the incoming set. A hop is accepted only if a quorum of the current set sealed it; the set proven in its state then becomes current. Any number of members can change at one hop.

The trust anchor pins the validator contract's address, its array slot and its code hash, so a bundle cannot read the set from another contract or another slot. To forge a bundle an attacker must hold the keys of a quorum of the trusted set, or of a set reachable from it through sealed hops. The account proof pins the CLPR Service's code hash, so a Service whose code changes needs a new channel.

## 3. Proof material

In addition to the abstract bundle content, a producer collects:
- the RLP header of `H`;
- the member list of the anchored set;
- for every block after the anchored block and before `H` whose state changes the validator contract's array: its header and a proof of the array in its state;
- a proof of the validator contract's array in the state of `H`;
- the proofs of the CLPR Service state, as in [qbft-epoch §3](qbft-epoch.md#3-proof-material).

## 4. Wire layout

The bundle is an RLP list of 5 items, or 7 when it carries the endpoint manifest. It is at least 2 bytes long.

| Index | Item | Encoding |
|---|---|---|
| 0 | Header of `H` | RLP list of 15 to 22 header fields |
| 1 | Validator source | RLP list `[trustedSet, hops, contractProof]` |
| 2 | Account proof | [Proof encoding](../README.md#34-proof-encoding) |
| 3 | Channel storage proof | [Proof encoding](../README.md#34-proof-encoding) |
| 4 | Bundle content | [Proof encoding](../README.md#34-proof-encoding) |
| 5 | Manifest storage proof | 7-item form only |
| 6 | Manifest preimage | 7-item form only |

| Field of item 1 | Encoding |
|---|---|
| `trustedSet` | RLP list of at most 256 non-zero 20-byte addresses: the members of the anchored set, in any order |
| `hops` | RLP list of hops in strictly ascending block order; each hop is the RLP list `[header, contractProof]`, the header having at least 15 fields; can be empty |
| `contractProof` | The validator contract proof for the state of `H` |

A **validator contract proof** is a byte string holding the RLP list `[validatorContract, accountProof, arraySlot, storageProof]`:

| Index | Item | Encoding |
|---|---|---|
| 0 | `validatorContract` | 20-byte address |
| 1 | `accountProof` | Account proof of `validatorContract` ([proof encoding](../README.md#34-proof-encoding)) |
| 2 | `arraySlot` | 32-byte slot of the validator array |
| 3 | `storageProof` | Storage proof of the array length slot and of every element slot; at most 257 entries |

The array has the Solidity dynamic-array layout: its length `N` is at `arraySlot`, and element `i` (from 0) is at slot `keccak256(arraySlot) + i` ([Besu §3](../README.md#3-proven-storage-layout)), holding an address in its low 160 bits.

## 5. Encoding algorithm

The pseudocode of this scheme uses the operations of [Besu §3.4](../README.md#34-proof-encoding) (`RLP`, `decode RLPList`) and the header functions of [Besu §4.2](../README.md#42-qbft-headers-and-seals) (`headerAt`, `number`, `stateRoot`).

```
function ContractProof(b):                       // the validator contract proof for the state of block b
    (accountProof, storageProof) := proofs at b of validatorContract and of the slots
                                    arraySlot and keccak256(arraySlot) + i for i from 0 to N − 1
    return RLP([validatorContract, accountProof, arraySlot, storageProof])       // a byte string

A := the anchored block number (the peer's trust anchor id)
trustedSet := the members of the anchored set
hops := []
for b from A + 1 to number(H) − 1
    if the state of b holds a different validator array than the state of b − 1 then
        append [headerAt(b), ContractProof(b)] to hops
contractProof := ContractProof(number(H))
items := [headerAt(H), [trustedSet, hops, contractProof], accountProof, storageProof, content]
if the manifest is included then
    append manifestProof and manifestPreimage to items
bundle := RLP(items)
```

`validatorContract` and `arraySlot` are those of the anchor, and `N` is the array length at `b`.

`number(H)` MUST be greater than `A`. The state proofs, content and manifest items are built as in [qbft-epoch §5](qbft-epoch.md#5-encoding-algorithm).

## 6. Decode-and-verify algorithm

The trust anchor determines `(T, codeHash, validatorContract, arraySlot, A, validatorCodeHash)` ([§7](#7-trust-anchor-changes)).

```
function ResolveSet(proofBytes, stateRoot, validatorContract, arraySlot) → (set, codeHash):
    p := decode RLPList(proofBytes)
    if len(p) ≠ 4 then reject "invalid proof shape"
    (c, accountProof, s, storageProof) := (p[0], p[1], p[2], p[3])
    if c ≠ validatorContract then reject "wrong validator contract"
    if s ≠ arraySlot then reject "wrong array slot"
    (storageRoot, codeHash) := the account of c, proven by accountProof under stateRoot
    entries := decode RLPList(storageProof)
    if len(entries) > 257 then reject "too many storage entries"
    N := StorageValue(entries, storageRoot, arraySlot)
    if N = 0 or N > 256 then reject "validator set size"
    members := []
    for i from 0 to N − 1
        member := StorageValue(entries, storageRoot, keccak256(arraySlot) + i) mod 2^160
        if member = 0 then reject "zero validator"
        if member ∈ members then reject "duplicate validator"
        append member to members
    return (members, codeHash)

function PinnedSet(proofBytes, stateRoot, validatorContract, arraySlot, validatorCodeHash) → set:
    (set, codeHash) := ResolveSet(proofBytes, stateRoot, validatorContract, arraySlot)
    if codeHash ≠ validatorCodeHash then reject "wrong validator code hash"
    return set

function verifyBundle(proof, anchor, ctx):
    (T, codeHash, validatorContract, arraySlot, A, validatorCodeHash) := anchor
    channelId := ctx[0:32]
    serviceAddress := ctx[32:len(ctx)]
    if len(proof) < 2 then reject "payload shape"
    items := decode RLPList(proof)
    if len(items) ≠ 5 and len(items) ≠ 7 then reject "payload shape"
    header := items[0]
    if header does not have 15 to 22 fields then reject "header shape"

    source := decode RLPList(items[1])
    if len(source) ≠ 3 then reject "validator source shape"
    (trustedSet, hops, contractProof) := (source[0], source[1], source[2])
    if the distinct members of trustedSet ≠ T then reject "wrong trusted set"

    current := T
    last := A
    for each hop in hops
        hp := decode RLPList(hop)
        if len(hp) ≠ 2 then reject "hop shape"
        (hopHeader, hopProof) := (hp[0], hp[1])
        if hopHeader has fewer than 15 fields then reject "header shape"
        if number(hopHeader) ≤ last then reject "hops not ascending"
        RequireQuorum(hopHeader, current)
        current := PinnedSet(hopProof, stateRoot(hopHeader), validatorContract, arraySlot, validatorCodeHash)
        last := number(hopHeader)
    if number(header) ≤ last then reject "header not after the walk"
    RequireQuorum(header, current)
    next := PinnedSet(contractProof, stateRoot(header), validatorContract, arraySlot, validatorCodeHash)

    if len(items) = 7 then
        (manifestProof, manifestPreimage) := (items[5], items[6])
    else
        (manifestProof, manifestPreimage) := (absent, absent)
    (metadata, payloads, manifest) := VerifyServiceState(stateRoot(header), codeHash,
            items[2], items[3], items[4], manifestProof, manifestPreimage, channelId, serviceAddress)

    if next ≠ T or len(hops) > 0 then
        newAnchor := (next, codeHash, validatorContract, arraySlot, number(header), validatorCodeHash)
        newAnchorId := be(number(header), 8)
    else
        newAnchor := empty
        newAnchorId := empty
    return (metadata, payloads, newAnchor, newAnchorId, manifest)
```

`StorageValue` and `VerifyServiceState` are defined in [Besu §3.5](../README.md#35-verifying-the-clpr-service-state), and `RequireQuorum` in [Besu §4.2](../README.md#42-qbft-headers-and-seals). The account proof in `ResolveSet` is walked as in `VerifyServiceState`, and an absent account is rejected. Sets are lists of distinct addresses, compared without regard to order.

## 7. Trust anchor changes

**Contents.** The trust anchor's encoding is internal to the verifier contract. The scheme requires it to determine:

| Content | Meaning |
|---|---|
| Trusted set `T` | The validator set confirmed at block `A`. The anchor MAY hold a commitment to `T`; the bundle then supplies `T`'s members. |
| Code hash `codeHash` | The CLPR Service account's code hash; 0 disables the check |
| `validatorContract`, `arraySlot` | Where the validator set is held |
| `validatorCodeHash` | The validator contract's code hash |
| Anchored block `A` | The block at which `T` was last confirmed |

**Id.** The trust anchor id is `be(A, 8)`.

**Changes.** When the set proven in the state of `H` differs from `T`, or the bundle carries at least one hop, the new anchor has `T` replaced by the set proven in the state of `H` and `A` by `number(H)`, with id `be(number(H), 8)`. The other contents do not change. Otherwise the new anchor and id are empty.

## 8. Rejection conditions

A verifier MUST reject the bundle when:

| Condition |
|---|
| The trust anchor or the channel context is malformed. |
| The bundle is shorter than 2 bytes, or is not an RLP list of 5 or 7 items. |
| The header of `H` does not have 15 to 22 fields, or a hop header has fewer than 15 fields. |
| Item 1 is not a list of exactly 3 items, or a hop is not a list of exactly 2 items. |
| `trustedSet` holds an item that is not a non-zero 20-byte address, or more than 256 items, or its members are not exactly `T`. |
| A hop's number is not greater than the previous hop's, or than `A` for the first hop. |
| The number of `H` is not greater than the last hop's, or than `A` when there are no hops. |
| A hop header or the header of `H` fails `RequireQuorum` against the current set. |
| A validator contract proof is not a byte string holding a 4-item list, names another contract or array slot, has an invalid or absent account, has more than 257 storage entries, proves a length of 0 or more than 256, a zero member or duplicate members, or a code hash other than `validatorCodeHash`. |
| Any condition of [Besu §3.5](../README.md#35-verifying-the-clpr-service-state). |

## 9. Configuration and manifest proofs

### 9.1 Configuration proof

The configuration proof is an RLP list of 7 items. Items 0 to 3 are those of [qbft-header](qbft-header.md#91-configuration-proof).

| Index | Item | Encoding |
|---|---|---|
| 0–3 | Service address, chain id, configuration timestamp, throttles | As in qbft-header |
| 4 | Descriptor | Byte string holding RLP `[mode, serviceAddress, codeHash, validatorContract, arraySlot]`, with `mode` 1. `serviceAddress` is ignored by verifiers; a producer SHOULD set it to item 0. |
| 5 | Validator contract proof | As in [§4](#4-wire-layout), for the state of the header's block |
| 6 | Header | RLP list of at least 15 header fields |

```
function verifyConfig(config, channelId, manifestProof):
    if len(config) = 0 then reject "payload shape"
    items := decode RLPList(config)
    if len(items) ≠ 7 then reject "payload shape"
    descriptor := decode RLPList(items[4])
    if len(descriptor) ≠ 5 then reject "descriptor shape"
    (mode, ignored, codeHash, validatorContract, arraySlot) :=
            (descriptor[0], descriptor[1], descriptor[2], descriptor[3], descriptor[4])
    if mode ≠ 1 then reject "unknown validator mode"
    header := items[6]
    (V, validatorCodeHash) := ResolveSet(items[5], stateRoot(header), validatorContract, arraySlot)
    RequireQuorum(header, V)
    anchor := (V, codeHash, validatorContract, arraySlot, number(header), validatorCodeHash)
    anchorId := be(number(header), 8)
    manifest := ConfigurationTimeManifest(manifestProof, V, items[0])
    return (channelId ‖ items[0], items[1], items[0], items[2], items[3], anchor, anchorId, manifest)
```

The configuration proof establishes the initial validator set, proven from the validator contract's storage in the configuration header's state and checked against that header's seals, and the validator contract's code hash, taken from its proven account. Other `verifyConfig` outputs are registration inputs; which outputs a configuration proof must authenticate is open issue [OI-2](../../../protocol/open-issues.md#oi-2-what-the-configuration-proof-must-authenticate).

The configuration header SHOULD be a block whose state does not change the validator array. Its seals are checked against the set proven in its own state, so a header whose block changes the set is checked against the new set and can be rejected.

A verifier MUST reject the configuration proof when it is empty, is not an RLP list of 7 items, has a header with fewer than 15 fields, has a throttles list of other than 5 or 7 items, has a descriptor that is not a 5-item list with mode 1, has a validator contract proof that fails `ResolveSet`, or when the header fails `RequireQuorum` against the proven set.

### 9.2 Manifest proof

The manifest proof is the [configuration-time manifest proof](../README.md#43-configuration-time-manifest-proof), checked against the initial validator set. Its header MUST have at least 15 fields.
