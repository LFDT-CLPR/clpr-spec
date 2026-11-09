# Besu

> **Category:** Ledger Specification (Besu) · **Applies to:** v0.2 · **Revision:** 1

This document defines how Besu takes part in CLPR: its identity, its verifier API, the CLPR Service state its proofs cover, and its proof schemes.

## 1. Ledger identity

Besu is an EVM ledger that reaches consensus with QBFT. QBFT has no forks, so a block is final as soon as it is sealed.

| Item | Value |
|---|---|
| Chain id | CAIP-2 `eip155:<chain id>`, where `<chain id>` is the network's EIP-155 chain id in decimal, for example `eip155:1337` |
| Service address | The 20-byte address of the CLPR Service contract |
| Family | [EVM](../evm/README.md) |

## 2. Verifier API

Besu is a member of the EVM family. Its CLPR Service calls verifier contracts through the [EVM verifier API](../evm/verifier-api.md), and its applications and connectors implement the [EVM application and connector interfaces](../evm/README.md#3-application-and-connector-interfaces).

## 3. Proven storage layout

Besu proof schemes prove values held in the storage of the CLPR Service contract, at the service address. This section is shared by every Besu proof scheme.

A storage slot number and a storage word are 256-bit unsigned integers: `slot + k` is integer addition, and a `keccak256` value used as a slot is read as a big-endian integer.

### 3.1 Service slots

| Slot | Content | Proven by |
|---|---|---|
| 1 | Message queues: a mapping from channel id to a mapping from message id to the stored message | The last message's running hash ([§3.3](#33-message-running-hash)) |
| 15 | Channels: a mapping from channel id to the channel record | Queue metadata ([§3.2](#32-channel-record)) |
| 18 | Endpoint manifest commitment: `keccak256` of the encoded local endpoint manifest | Manifest proofs ([§3.5](#35-verifying-the-clpr-service-state)) |
| 25 | Service address, as a Solidity `bytes` value | The protobuf qbft-epoch configuration proof layout ([OI-3](../../protocol/open-issues.md#oi-3-configuration-proof-format-for-the-qbft-epoch-scheme)) |

The manifest commitment is `keccak256(m)`, where `m` is the [protocol encoding](../../protocol/schema/README.md) of the CLPR Service's current local [endpoint manifest](../../protocol/endpoint-manifest.md#3-local-manifest), with default values omitted. The CLPR Service recomputes it whenever the manifest version or the service address changes.

Slot 25 holds a 20-byte service address `a` in the short `bytes` layout: the word is `a × 2^96 + 0x28`, with `a` read as a big-endian integer and `0x28` twice the length.

### 3.2 Channel record

The record of channel `channelId` starts at slot `base = keccak256(channelId ‖ be(15, 32))`. Verifiers prove five of its slots. Fields are packed into a slot's word from bit 0, the least significant bit:

| Slot | Bits (inclusive) | Field |
|---|---|---|
| `base + 1` | 0–159 | Verifier address |
| `base + 1` | 160–167 | `status` (`uint8`) |
| `base + 1` | 168–231 | `next_message_id` (`uint64`) |
| `base + 2` | 0–63 | `acked_message_id` (`uint64`) |
| `base + 2` | 64–127 | `received_message_id` (`uint64`) |
| `base + 2` | 128–191 | Reply cursor (`uint64`) |
| `base + 4` | 0–255 | `sent_running_hash` (`bytes32`) |
| `base + 5` | 0–255 | `received_running_hash` (`bytes32`) |
| `base + 16` | 0–63 | `endpoint_manifest_version` (`uint64`) |

`status` uses the values of the [ChannelStatus encoding](../evm/verifier-api.md#33-enumerations). The fields are defined in [Channel setup §6](../../protocol/channel-setup.md#6-shared-channel-state), except the reply cursor ([Blueprint §1.5](../../blueprint/clpr-service.md#15-reply-and-acknowledgement-bookkeeping)).

### 3.3 Message running hash

The running hash after message `id` of channel `channelId` is held at:

```
function MessageHashSlot(channelId, id):
    queueBase := keccak256(channelId ‖ be(1, 32))
    return keccak256(be(id, 32) ‖ queueBase) + 1
```

### 3.4 Proof encoding

All proofs are EIP-1186 Merkle-Patricia proofs, as returned by `eth_getProof`, encoded in RLP.

| Item | Encoding |
|---|---|
| Account proof | An RLP list of byte strings: the trie nodes from the state root to the leaf for `keccak256(serviceAddress)`. The leaf value is the RLP list `[nonce, balance, storageRoot, codeHash]`. |
| Storage proof | An RLP list of entries. Each entry is a two-item RLP list `[slot, nodes]`: `slot` is a byte string of at most 32 bytes holding the slot number big-endian (leading zeros MAY be omitted), and `nodes` is an RLP list of byte strings, the trie nodes from the storage root to the leaf for `keccak256(be(slot, 32))`. An entry carries no value: the value is read from the proof. |
| Bundle content | A byte string holding the protobuf `ClprBundleContent` ([schema](../../protocol/schema/README.md)): field 1 is the queue metadata, field 2 (repeated) the message payloads in id order. A verifier reads only field 2 and ignores field 1. It MUST reject content that is not a well-formed protobuf encoding, and MAY reject content that holds other fields. |
| Manifest storage proof | A storage proof with one entry, for slot 18. |
| Manifest preimage | A byte string holding the protobuf `ClprEndpointManifest` exactly as committed in slot 18. |

Trie nodes are referenced by their `keccak256` hash. A verifier MAY reject a proof in which a node embeds a child node of fewer than 32 bytes instead of referencing it by hash.

A producer MUST put the five channel slots in the order of [§3.2](#32-channel-record), followed by the message slot when one is present. It MUST copy the message payloads byte for byte from the message queue, because the running hash covers those exact bytes. The manifest preimage MUST be the encoding whose `keccak256` is the value of slot 18 ([§3.1](#31-service-slots)).

The pseudocode of this document and of the Besu proof schemes writes decoding as `decode T(x)` and encoding as `serialize(x)` ([Conventions §4](../../protocol/conventions.md#4-pseudocode)), and uses these operations:
- `RLP(x)` is the RLP encoding of `x`, a byte string or a list of such values.
- `decode RLPList(x)` yields the items of the RLP list `x`, in order, each a byte string or a list. `x` is a byte string holding the list's encoding, or an item of an enclosing list, as the wire layout specifies. Anything else rejects.

### 3.5 Verifying the CLPR Service state

Every Besu proof scheme first authenticates a block's `stateRoot` and a code hash `codeHash`, in its own way. It then runs `VerifyServiceState`, which proves the CLPR Service's account and storage under that root.

```
function StorageValue(entries, storageRoot, slot) → value:      // a 256-bit integer
    e := the entry in entries whose slot equals slot
    if there is no such entry then reject "slot not proven"
    leaf := the MPT walk of e.nodes from storageRoot along keccak256(be(slot, 32))
    if the walk does not hash-chain from storageRoot then reject "invalid storage proof"
    if the key is absent from the trie then return 0
    return the RLP scalar inside the leaf's byte string

function VerifyServiceState(stateRoot, codeHash, accountProof, storageProof, content,
                            manifestProof, manifestPreimage, channelId, serviceAddress):
    // manifestProof and manifestPreimage are absent when the bundle carries no manifest
    if len(serviceAddress) ≠ 20 then reject "service address length"
    account := the MPT walk of accountProof from stateRoot along keccak256(serviceAddress)
    if the walk does not hash-chain from stateRoot then reject "invalid account proof"
    if the key is absent then reject "account absent"
    fields := decode RLPList(account)
    if len(fields) ≠ 4 then reject "account shape"
    (nonce, balance, storageRoot, accountCodeHash) := (fields[0], fields[1], fields[2], fields[3])
    if codeHash ≠ 0 and accountCodeHash ≠ codeHash then reject "code hash mismatch"

    payloads := the field-2 values of decode ClprBundleContent(content), in order
    count := len(payloads)

    entries := decode RLPList(storageProof)
    if len(entries) ≠ 5 and len(entries) ≠ 6 then reject "storage proof shape"
    for each e in entries
        if e is not a 2-item list [slot, nodes] as in §3.4 then reject "storage proof entry"
    base := keccak256(channelId ‖ be(15, 32))
    for each k in [1, 2, 4, 5, 16]
        w[k] := StorageValue(entries, storageRoot, base + k)
    m.status                    := floor(w[1] / 2^160) mod 2^8
    m.next_message_id           := floor(w[1] / 2^168) mod 2^64
    acked                       := w[2] mod 2^64
    m.received_message_id       := floor(w[2] / 2^64) mod 2^64
    m.sent_running_hash         := w[4]
    m.received_running_hash     := w[5]
    m.endpoint_manifest_version := w[16] mod 2^64
    m.last_message_id := 0
    m.last_message_running_hash := 0

    if count > 0 then
        if len(entries) = 5 then
            if acked + count ≥ m.next_message_id then reject "bundle starts at or before acked"
            m.last_message_id := m.next_message_id − 1
            m.last_message_running_hash := m.sent_running_hash
        else
            s := the slot of the last entry whose slot is not base + 1, 2, 4, 5 or 16
            m.last_message_id := the id with acked + count ≤ id and id ≤ m.next_message_id − 1
                                 and MessageHashSlot(channelId, id) = s
            if there is no such id then reject "last message slot not found"
            m.last_message_running_hash := StorageValue(entries, storageRoot, s)

    manifest := absent                                    // reported as version 0
    if manifestProof is present then
        commitment := StorageValue(decode RLPList(manifestProof), storageRoot, 18)
        if keccak256(manifestPreimage) ≠ commitment then reject "manifest commitment mismatch"
        manifest := decode ClprEndpointManifest(manifestPreimage)
        if manifest.version = 0 then reject "manifest version 0"
        if manifest.service_address ≠ serviceAddress then reject "manifest service address mismatch"

    return (m, payloads, manifest)
```

The queue metadata MUST come from the proven slots. A verifier MUST NOT use the queue metadata in field 1 of the bundle content, which is unproven. The payloads are unproven bytes; the CLPR Service binds them to the proven `last_message_running_hash` by the [running hash](../../protocol/messaging.md#4-running-hash) check during [bundle processing](../../protocol/channel-state-transitions.md#2-bundle-processing).

A message-less bundle with six entries is accepted; its sixth entry is ignored.

The rejection conditions of this section are the `reject` statements of `StorageValue` and `VerifyServiceState`, and failure to decode the bundle content or the manifest preimage.

## 4. Proof schemes

### 4.1 Schemes and status

| Scheme | Validator set source | Producer | Verifiers |
|---|---|---|---|
| [qbft-epoch](proof-schemes/qbft-epoch.md) | Epoch boundary headers | Besu CLPR Endpoint | EVM verifier contract; Hiero built-in verifier |
| [qbft-header](proof-schemes/qbft-header.md) | Every block header | None in v0.2 | EVM verifier contract |
| [qbft-contract](proof-schemes/qbft-contract.md) | A validator contract's storage | None in v0.2 | EVM verifier contract |

A channel uses one scheme for its life. A Besu network that changes how it selects validators needs new channels.

### 4.2 QBFT headers and seals

A block header is the RLP list of its fields in Besu's canonical order, including the fields added by later forks. Each scheme sets its own bounds on the number of header fields. Verifiers read three fields:

| Index | Field |
|---|---|
| 3 | `stateRoot` |
| 8 | `number` |
| 12 | `extraData` |

For a header `h`, `stateRoot(h)` is field 3 and `number(h)` is field 8, read as an unsigned integer. `headerAt(b)` is the header of block `b`, given as a block or by its number, as an RLP list of fields. For a block `b`, `number(b)` and `stateRoot(b)` are those of `headerAt(b)`.

`extraData` is a byte string holding the RLP list `[vanity, validators, vote, round, committedSeals]`, exactly five items. `validators` is an RLP list of 20-byte non-zero addresses: the validator set the header lists. `committedSeals` is an RLP list of 65-byte seals.

```
function SealHash(header):
    (vanity, validators, vote, round, seals) := the five items of decode RLPList(header[12])
    sealing := header with field 12 replaced by RLP([vanity, validators, vote, round, []])
    return keccak256(RLP(sealing))

function Signers(header) → signers:           // a list of distinct addresses
    h := SealHash(header)
    signers := []
    for each seal in the committedSeals of header
        if len(seal) ≠ 65 then reject "seal length"
        (r, s, v) := (seal[0:32], seal[32:64], seal[64])    // v is 0 or 1; 27 and 28 are accepted
        signer := the address recovered from (h, r, s, v)
        if recovery fails then reject "seal recovery failed"
        if signer is not in signers then append signer to signers
    return signers

function Quorum(n):
    return ceil(2 × n / 3)

function RequireQuorum(header, V):            // V is a list of distinct addresses
    if len(V) = 0 then reject "empty validator set"
    if the committedSeals of header are empty then reject "no seals"
    if the number of members of V in Signers(header) < Quorum(len(V)) then reject "quorum not reached"
```

Signers outside `V` are not counted, and a signer that sealed more than once counts once. A verifier MAY stop recovering seals once every count it needs is reached; a seal it has not examined does not cause rejection. The seal hash contains no chain id: the validator keys identify the chain.

### 4.3 Configuration-time manifest proof

The `endpointManifestProofBytes` argument of [verifyConfig](../evm/verifier-api.md#21-verifyconfig) is, in every Besu scheme, empty or an RLP list of 4 items:

| Index | Item |
|---|---|
| 0 | A block header, within the scheme's header field bounds |
| 1 | Account proof of the service address under that header's `stateRoot` |
| 2 | Manifest storage proof: one entry, for slot 18 |
| 3 | Manifest preimage |

Items 1 to 3 use the [proof encoding](#34-proof-encoding). Given the initial validator set `V` that the configuration proof establishes, the verifier MUST:
1. `RequireQuorum(header, V)`;
2. verify the account proof under the header's `stateRoot`; the code hash is not checked;
3. prove slot 18 and require `keccak256(preimage)` to equal its value;
4. require the decoded manifest's version to be at least 1, and its service address to equal the configuration's service address.

An empty argument yields a manifest with version 0. The schemes' pseudocode calls this check `ConfigurationTimeManifest(manifestProof, V, serviceAddress)`.

## 5. Registration signatures

Channel and connector registration signatures on Besu are those of the [EVM family](../evm/README.md#5-registration-signatures).
