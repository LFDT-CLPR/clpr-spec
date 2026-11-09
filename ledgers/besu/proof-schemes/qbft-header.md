# Besu Proof Scheme: QBFT Header

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

This proof scheme proves Besu CLPR Service state under QBFT seals, and follows validator changes header by header.

## 1. Status

| Role | Implemented by |
|---|---|
| Producer | None in v0.2 |
| Verifiers | A verifier contract for EVM ledgers |

## 2. Trust model

This scheme is for Besu networks whose block headers list the validator set (QBFT block-header validator selection). A bundle proves values in the CLPR Service's storage at a final block `H` ([proven storage layout](../README.md#3-proven-storage-layout)).

The verifier trusts a validator set `T`. It follows changes to the set through **hops**: headers of the blocks between the anchored block and `H` at which the listed set changes. Besu applies at most one validator change per block, so each accepted header moves the trusted set by at most one member, and it is accepted only if enough members of the trusted set sealed it (header rule below).

**Header rule.** A header listing the set `L_h` is accepted against the trusted set `T`, with `n = |T|` and `q = ceil(2 × n / 3)`, when all of these hold:

1. **One change at most.** `L_h` equals `T`, or `T` with one member added, or `T` with one member removed.
2. **Trust link.** The number of distinct members of `T` that sealed the header is at least:

   | Change | Required signers from `T` |
   |---|---|
   | None | `q` |
   | One member removed | `max(q − 1, 1)` |
   | One member added, and the added member sealed | `max(q − 1, 1)` |
   | One member added, and the added member did not seal | `q` |

3. **Own quorum.** At least `ceil(2 × |L_h| / 3)` distinct members of `L_h` sealed the header.

When `L_h` equals `T` the rule is `RequireQuorum(header, T)` ([Besu §4.2](../README.md#42-qbft-headers-and-seals)).

To forge a bundle an attacker must hold the keys of a quorum of the trusted set, or move the set one member at a time with almost a quorum of trusted keys at each step. Sets of one or two validators have no fault tolerance. The account proof pins the CLPR Service's code hash, so a Service whose code changes needs a new channel.

## 3. Proof material

In addition to the abstract bundle content, a producer collects:
- the RLP header of `H`;
- the member list of the anchored set, and the headers of every block after the anchored block and before `H` whose listed set differs from the previous block's;
- the proofs of the CLPR Service state, as in [qbft-epoch §3](qbft-epoch.md#3-proof-material).

## 4. Wire layout

The bundle is an RLP list of 5 items, or 7 when it carries the endpoint manifest. It is at least 2 bytes long.

| Index | Item | Encoding |
|---|---|---|
| 0 | Header of `H` | RLP list of 15 to 22 header fields |
| 1 | Validator source | RLP list `[trustedSet, hops]` |
| 2 | Account proof | [Proof encoding](../README.md#34-proof-encoding) |
| 3 | Channel storage proof | [Proof encoding](../README.md#34-proof-encoding) |
| 4 | Bundle content | [Proof encoding](../README.md#34-proof-encoding) |
| 5 | Manifest storage proof | 7-item form only |
| 6 | Manifest preimage | 7-item form only |

| Field of item 1 | Encoding |
|---|---|
| `trustedSet` | RLP list of at most 256 non-zero 20-byte addresses: the members of the anchored set, in any order. The empty list means "the set listed in the header of `H`". |
| `hops` | RLP list of headers, each an RLP list of at least 15 fields, in strictly ascending block order; can be empty |

## 5. Encoding algorithm

The pseudocode of this scheme uses the operations of [Besu §3.4](../README.md#34-proof-encoding) (`RLP`, `decode RLPList`) and the header functions of [Besu §4.2](../README.md#42-qbft-headers-and-seals) (`headerAt`, `number`, `stateRoot`).

```
A := the anchored block number (the peer's trust anchor id)
T := the validator set listed in the header of block A
hops := the headers of blocks b with A < b and b < number(H) whose listed set differs from
        block b − 1's, in ascending order
if T equals the set listed in H then trustedSet := [] else trustedSet := the members of T
items := [headerAt(H), [trustedSet, hops], accountProof, storageProof, content]
if the manifest is included then
    append manifestProof and manifestPreimage to items
bundle := RLP(items)
```

`number(H)` MUST be greater than `A`. The state proofs, content and manifest items are built as in [qbft-epoch §5](qbft-epoch.md#5-encoding-algorithm).

## 6. Decode-and-verify algorithm

The trust anchor determines `(T, codeHash, A)` ([§7](#7-trust-anchor-changes)).

```
function AcceptHeader(h, T):                     // the header rule of section 2
    L_h := the distinct validators listed in h's extraData
    if len(L_h) = 0 or len(T) = 0 or len(L_h) > 256 or len(T) > 256 then
        reject "validator set size"
    added := the members of L_h that are not in T
    removed := the members of T that are not in L_h
    if len(added) + len(removed) = 0 then
        RequireQuorum(h, T)
        return L_h
    if len(added) + len(removed) > 1 then reject "too many set changes"
    S := Signers(h)
    q := Quorum(len(T))
    if len(added) = 1 and added[0] is not in S then required := q
    else required := max(q − 1, 1)
    if the number of members of T in S < required then reject "trust link not reached"
    if the number of members of L_h in S < Quorum(len(L_h)) then reject "quorum not reached"
    return L_h

function verifyBundle(proof, anchor, ctx):
    (T, codeHash, A) := anchor
    channelId := ctx[0:32]
    serviceAddress := ctx[32:len(ctx)]
    if len(proof) < 2 then reject "payload shape"
    items := decode RLPList(proof)
    if len(items) ≠ 5 and len(items) ≠ 7 then reject "payload shape"
    header := items[0]
    if header does not have 15 to 22 fields then reject "header shape"
    listedNow := the distinct validators listed in header's extraData

    source := decode RLPList(items[1])
    if len(source) ≠ 2 then reject "validator source shape"
    (trustedSet, hops) := (source[0], source[1])
    if len(trustedSet) = 0 then candidate := listedNow
    else candidate := the distinct members of trustedSet
    if candidate ≠ T then reject "wrong trusted set"

    current := T
    last := A
    for each hop in hops
        if hop has fewer than 15 fields then reject "header shape"
        if number(hop) ≤ last then reject "hops not ascending"
        current := AcceptHeader(hop, current)
        last := number(hop)
    if number(header) ≤ last then reject "header not after the walk"
    AcceptHeader(header, current)

    if len(items) = 7 then
        (manifestProof, manifestPreimage) := (items[5], items[6])
    else
        (manifestProof, manifestPreimage) := (absent, absent)
    (metadata, payloads, manifest) := VerifyServiceState(stateRoot(header), codeHash,
            items[2], items[3], items[4], manifestProof, manifestPreimage, channelId, serviceAddress)

    if listedNow ≠ T or len(hops) > 0 then
        newAnchor := (listedNow, codeHash, number(header))
        newAnchorId := be(number(header), 8)
    else
        newAnchor := empty
        newAnchorId := empty
    return (metadata, payloads, newAnchor, newAnchorId, manifest)
```

`Signers`, `Quorum` and `RequireQuorum` are defined in [Besu §4.2](../README.md#42-qbft-headers-and-seals), and `VerifyServiceState` in [Besu §3.5](../README.md#35-verifying-the-clpr-service-state). Sets are lists of distinct addresses, compared without regard to order.

## 7. Trust anchor changes

**Contents.** The trust anchor's encoding is internal to the verifier contract. The scheme requires it to determine:

| Content | Meaning |
|---|---|
| Trusted set `T` | The validator set listed in the header of block `A`. The anchor MAY hold a commitment to `T`; the bundle then supplies `T`'s members. |
| Code hash `codeHash` | The CLPR Service account's code hash; 0 disables the check |
| Anchored block `A` | The block at which `T` was last confirmed |

**Id.** The trust anchor id is `be(A, 8)`.

**Changes.** When the set listed in the header of `H` differs from `T`, or the bundle carries at least one hop, the new anchor is `(set listed in H, codeHash, number(H))`, with id `be(number(H), 8)`. Otherwise the new anchor and id are empty.

## 8. Rejection conditions

A verifier MUST reject the bundle when:

| Condition |
|---|
| The trust anchor or the channel context is malformed. |
| The bundle is shorter than 2 bytes, or is not an RLP list of 5 or 7 items. |
| The header of `H` does not have 15 to 22 fields, or a hop has fewer than 15 fields. |
| A header's `extraData` is not the five-item QBFT list, or its validator list holds an item that is not a non-zero 20-byte address. |
| Item 1 is not a list of exactly 2 items, or `trustedSet` holds an item that is not a non-zero 20-byte address, or more than 256 items. |
| The members supplied for the trusted set are not exactly `T`. |
| A hop's number is not greater than the previous hop's, or than `A` for the first hop. |
| The number of `H` is not greater than the last hop's, or than `A` when there are no hops. |
| A header fails the header rule: a set is empty or has more than 256 members, the sets differ by more than one member, the trust link or own quorum is not reached, there are no seals, or a seal is not 65 bytes or does not recover. |
| Any condition of [Besu §3.5](../README.md#35-verifying-the-clpr-service-state). |

## 9. Configuration and manifest proofs

### 9.1 Configuration proof

The configuration proof is an RLP list of 6 items. Items 0 to 4 are shared with [qbft-contract](qbft-contract.md#91-configuration-proof).

| Index | Item | Encoding |
|---|---|---|
| 0 | Service address | Byte string |
| 1 | Chain id | Byte string, UTF-8 |
| 2 | Configuration timestamp | Scalar: nanoseconds since the Unix epoch |
| 3 | Throttles | RLP list of 5 or 7 scalars, in the order of [`Throttles`](../../evm/verifier-api.md#31-structures); with 5, the two endpoint limits are 0 |
| 4 | Descriptor | Byte string holding RLP `[mode, codeHash]`, with `mode` 0 |
| 5 | Header | RLP list of at least 15 header fields |

A producer MUST encode scalars that fit the field types of the corresponding `verifyConfig` results. A verifier MAY reject or truncate a larger value.

```
function verifyConfig(config, channelId, manifestProof):
    if len(config) = 0 then reject "payload shape"
    items := decode RLPList(config)
    if len(items) ≠ 6 then reject "payload shape"
    descriptor := decode RLPList(items[4])
    if len(descriptor) ≠ 2 then reject "descriptor shape"
    (mode, codeHash) := (descriptor[0], descriptor[1])
    if mode ≠ 0 then reject "unknown validator mode"
    header := items[5]
    V := the distinct validators listed in header's extraData
    RequireQuorum(header, V)
    anchor := (V, codeHash, number(header))
    anchorId := be(number(header), 8)
    manifest := ConfigurationTimeManifest(manifestProof, V, items[0])
    return (channelId ‖ items[0], items[1], items[0], items[2], items[3], anchor, anchorId, manifest)
```

The configuration proof establishes the initial validator set: the set the configuration header lists, checked against that header's own seals. Other `verifyConfig` outputs are registration inputs; which outputs a configuration proof must authenticate is open issue [OI-2](../../../protocol/open-issues.md#oi-2-what-the-configuration-proof-must-authenticate).

A verifier MUST reject the configuration proof when it is empty, is not an RLP list of 6 items, has a header with fewer than 15 fields, has a throttles list of other than 5 or 7 items, has a descriptor that is not a 2-item list with mode 0, or when the header fails `RequireQuorum` against its own set.

### 9.2 Manifest proof

The manifest proof is the [configuration-time manifest proof](../README.md#43-configuration-time-manifest-proof), checked against the initial validator set. Its header MUST have at least 15 fields.
