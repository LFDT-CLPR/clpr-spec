# Besu Proof Scheme: QBFT Epoch

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

This proof scheme proves Besu CLPR Service state under QBFT seals, and follows validator changes at epoch boundaries.

## 1. Roles

| Role | Performed by |
|---|---|
| Bundle producer | The Besu CLPR Endpoint |
| Configuration and manifest proofs | The format is an open issue ([OI-2](../../../protocol/open-issues.md#oi-2-configuration-proof-format-for-the-qbft-epoch-scheme)) |
| Verifiers | A verifier contract for EVM ledgers; Hiero's built-in verifier |

## 2. Trust model

A bundle proves values in the CLPR Service's storage at a Besu block `H` ([proven storage layout](../README.md#3-proven-storage-layout)). `H` is final, because QBFT blocks are final when sealed.

The verifier accepts `H` if a quorum of the anchored validator set sealed it. The anchored set changes only at **epoch boundaries**: the blocks whose number is a multiple of the epoch length `L`. Each epoch boundary header lists the validator set, and its seals link it to the set before it. A bundle carries the boundary headers the verifier has not yet seen.

| Concept | Definition |
|---|---|
| Epoch length `L` | The QBFT epoch length of the Besu network, with `L > 0`. It is part of the scheme's configuration, fixed at channel setup. |
| Epoch of block `b` | `floor(b / L)` |
| Epoch boundary header of epoch `e` | The header of block `e × L` |
| Quorum | `ceil(2 × n / 3)` distinct seals from a set of `n` validators ([Besu §4.2](../README.md#42-qbft-headers-and-seals)) |

To forge a bundle an attacker must hold the keys of a quorum of the anchored set, or of a set reachable from it through sealed epoch boundary headers. The account proof pins the CLPR Service's code hash, so a Service whose code changes needs a new channel.

A validator change between boundaries takes effect for the verifier only at the next boundary. Until then, a header is accepted only if a quorum of the anchored set sealed it.

## 3. Proof material

In addition to the abstract bundle content, the endpoint collects:
- the RLP header of `H`;
- the epoch boundary headers after the peer's anchored epoch;
- an EIP-1186 proof, at `H`, of the CLPR Service account and of the channel's metadata slots, plus the last included message's running-hash slot when the bundle carries messages;
- when the bundle carries the endpoint manifest, a proof of the manifest commitment slot at `H`, and the committed manifest bytes.

## 4. Wire layout

The bundle is an RLP list of 5 items, or 7 when it carries the endpoint manifest.

| Index | Item | Encoding |
|---|---|---|
| 0 | Header of `H` | RLP list of 15 to 23 header fields |
| 1 | Epoch boundary headers | RLP list of headers, each an RLP list of 15 to 23 fields, in ascending block order; can be empty |
| 2 | Account proof | [Proof encoding](../README.md#34-proof-encoding) |
| 3 | Channel storage proof | 5 entries, or 6 when the bundle carries messages ([proof encoding](../README.md#34-proof-encoding)) |
| 4 | Bundle content | [Proof encoding](../README.md#34-proof-encoding) |
| 5 | Manifest storage proof | 7-item form only |
| 6 | Manifest preimage | 7-item form only |

Headers are encoded as in [Besu §4.2](../README.md#42-qbft-headers-and-seals).

## 5. Encoding algorithm

The pseudocode of this scheme uses the operations of [Besu §3.4](../README.md#34-proof-encoding) (`RLP`, `decode RLPList`), the header functions of [Besu §4.2](../README.md#42-qbft-headers-and-seals) (`headerAt`, `number`, `stateRoot`), and `serialize` ([Conventions §4](../../../protocol/conventions.md#4-pseudocode)).

The endpoint runs [bundle aggregation](../bundle-aggregation.md) at block `H`, then:

```
e_H := floor(number(H) / L)
if len(request.current_trust_anchor_id) = 8 then
    e_peer := the big-endian unsigned value of request.current_trust_anchor_id
else
    e_peer := e_H
if e_peer > e_H then send nothing

k := min(e_H − e_peer, maxHeaders)
epochHeaders := []
for j from 1 to k
    append headerAt((e_peer + j) × L) to epochHeaders

storageSlots := [base + 1, base + 2, base + 4, base + 5, base + 16]
if messages is not empty then
    append MessageHashSlot(channelId, id of the last message) to storageSlots
(accountProof, storageProof) := eth_getProof(serviceAddress, storageSlots, H)

content := serialize(ClprBundleContent { metadata = metadata, messages = messages })
items := [headerAt(H), epochHeaders, accountProof, storageProof, content]
if the manifest is included then
    manifestProof := eth_getProof(serviceAddress, [18], H)
    manifestPreimage := the encoded manifest whose keccak256 is the value of slot 18 at H
    append manifestProof and manifestPreimage to items
bundle := RLP(items)
```

- `base` and `MessageHashSlot` are defined in the [proven storage layout](../README.md#3-proven-storage-layout).
- `L` MUST equal the network's epoch length.
- `maxHeaders` is a producer parameter, at least 1.
- A verifier accepts messages with any number of boundary headers ([§6](#6-decode-and-verify-algorithm)). Which messages a producer includes when `k > 1` is set by [bundle aggregation §3](../bundle-aggregation.md#3-message-range-and-limits).
- Field 1 of the bundle content SHOULD hold the queue metadata of `H`. Verifiers ignore it.

**Catch-up limit.** When the peer is more than `maxHeaders` epochs behind, a bundle carries `maxHeaders` boundary headers and the peer catches up over several bundles. `H` stays the head block, so each such bundle is accepted only if a quorum of the set listed in its last boundary header sealed `H`. If the validator set changed in a later epoch beyond what that quorum tolerates, the bundle is rejected and the peer does not catch up. This limit is open issue [OI-6](../../../protocol/open-issues.md#oi-6-qbft-epoch-catch-up-across-a-validator-change).

## 6. Decode-and-verify algorithm

The trust anchor determines `(V, E, L, codeHash)` ([§7](#7-trust-anchor-changes)). The channel context is `channelId ‖ serviceAddress` ([EVM verifier API §3.2](../../evm/verifier-api.md#32-channelcontext)).

```
function verifyBundle(proof, anchor, ctx):
    (V, E, L, codeHash) := anchor
    if L = 0 then reject "invalid trust anchor"
    channelId := ctx[0:32]
    serviceAddress := ctx[32:len(ctx)]
    items := decode RLPList(proof)
    if len(items) ≠ 5 and len(items) ≠ 7 then reject "payload shape"

    epochHeaders := decode RLPList(items[1])
    for i from 0 to len(epochHeaders) − 1
        h := epochHeaders[i]
        if h does not have 15 to 23 fields then reject "header shape"
        if number(h) ≠ (E + i + 1) × L then reject "not the next epoch boundary"
        RequireQuorum(h, V)
        V := the validators listed in h's extraData
    E' := E + len(epochHeaders)

    header := items[0]
    if header does not have 15 to 23 fields then reject "header shape"
    if floor(number(header) / L) < E' then reject "header before the anchored epoch"
    RequireQuorum(header, V)

    if len(items) = 7 then
        (manifestProof, manifestPreimage) := (items[5], items[6])
    else
        (manifestProof, manifestPreimage) := (absent, absent)
    (metadata, payloads, manifest) := VerifyServiceState(stateRoot(header), codeHash,
            items[2], items[3], items[4], manifestProof, manifestPreimage, channelId, serviceAddress)

    if len(epochHeaders) > 0 then
        newAnchor := (V, E', L, codeHash)
        newAnchorId := be(E', 8)
    else
        newAnchor := empty
        newAnchorId := empty
    return (metadata, payloads, newAnchor, newAnchorId, manifest)
```

`RequireQuorum` is defined in [Besu §4.2](../README.md#42-qbft-headers-and-seals), and `VerifyServiceState` in [Besu §3.5](../README.md#35-verifying-the-clpr-service-state). The service address comes from the channel context, not from the anchor.

## 7. Trust anchor changes

**Contents.** The trust anchor's encoding is internal to the verifier contract and opaque to the protocol. Only the verifier that produced an anchor reads it. The scheme requires the anchor to determine:

| Content | Meaning |
|---|---|
| Validator set `V` | The validators listed in the header of the anchored epoch boundary |
| Epoch `E` | The anchored epoch |
| Epoch length `L` | Fixed at channel setup; `L > 0` |
| Code hash `codeHash` | The CLPR Service account's code hash; 0 disables the check |

**Id.** The trust anchor id is `be(E, 8)`. It is visible on the wire: the peer sends it as `current_trust_anchor_id` in its `BundleRequest`, and the producer uses it to choose the boundary headers ([§5](#5-encoding-algorithm)).

**Changes.** A bundle with `k ≥ 1` epoch boundary headers advances the anchor to the validator set of its last boundary header and to epoch `E + k`. `L` and `codeHash` do not change. A bundle without boundary headers returns an empty new anchor and id.

## 8. Rejection conditions

A verifier MUST reject the bundle when:

| Condition |
|---|
| The trust anchor or the channel context is malformed, or the anchor's epoch length `L` is 0. |
| The bundle is not an RLP list of 5 or 7 items. |
| A header is not an RLP list of 15 to 23 fields, or its `extraData` is not the five-item QBFT list. |
| Epoch boundary header `i` is not at block `(E + i + 1) × L`. |
| A header lists an empty validator set, has no seals, has a seal that is not 65 bytes or does not recover, or has fewer than `ceil(2 × n / 3)` distinct signers from the set it is checked against. |
| The epoch of the header of `H` is before `E + k`. |
| Any condition of [Besu §3.5](../README.md#35-verifying-the-clpr-service-state). |

## 9. Configuration and manifest proofs

### 9.1 Configuration proof

The layout of the qbft-epoch configuration proof is open issue **OI-2** ([Open issues](../../../protocol/open-issues.md#oi-2-configuration-proof-format-for-the-qbft-epoch-scheme)). This scheme does not define the layout. A verifier contract documents the layout it accepts.

Whatever its layout, `verifyConfig` MUST return:
- an initial trust anchor that determines `V`, `E`, `L` and `codeHash` as in [§7](#7-trust-anchor-changes), where `V` is the validator set listed in a sealed epoch boundary header of epoch `E`;
- an initial trust anchor id equal to `be(E, 8)`.

### 9.2 Manifest proof

The manifest proof is the [configuration-time manifest proof](../README.md#43-configuration-time-manifest-proof), checked against the initial validator set `V`. Its header MUST have 15 to 23 fields.
