# Channel Setup

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

A **channel** connects a CLPR Service on one ledger with a CLPR Service on another. It exists as a pair of records, one on each ledger, joined by a shared channel id. This module defines how the two records are created, what each holds about the peer, and which channel state the peer proves or consumes.

## 1. Channel identity

A **channel id** is a 32-byte value, chosen by the registrant (for example at random). The same channel id is used on both ledgers; it is what ties the two records of a channel together. Within one CLPR Service, a channel id identifies at most one channel.

- A ledger MAY constrain how a channel id is derived. Because the id is identical on both ledgers, the registrant MUST choose an id that satisfies the constraints of both. EVM ledgers derive the channel id; see [EVM](../ledgers/evm/README.md).
- The Protocol does not derive the channel id from a key. The registrant MAY use a different key pair on each ledger, of a type that ledger supports, unless the two ledgers' constraints on the id require the same key (for example, a channel between two EVM ledgers).
- Several channels MAY connect the same pair of CLPR Services. Each has its own channel id, verifier contract and message queues, and is independent of the others.

## 2. Registration

A channel is registered on each ledger in two phases, commit and reveal. The commit phase reserves the channel on both ledgers without revealing the channel id or the key; the reveal phase creates the channel. Registration is open to any caller. The registrant has no authority over the channel once it exists: its key serves only to coordinate registration across the two ledgers, and on EVM ledgers to derive the channel id.

The **ownership commitment** binds a channel id to the registrant's key on one ledger:

```
ownership_commitment := keccak256(channel_id ‖ public_key)
```

`public_key` is the registrant's public key on that ledger, in that ledger's encoding.

The registrant:

1. Chooses a channel id (Section 1) and, on each ledger, a key pair.
2. Calls `registerChannel` on both ledgers.
3. Obtains, from each ledger, a proof of its ledger configuration and a proof of its local endpoint manifest. How these are obtained is ledger-specific ([ledgers](../ledgers/README.md)).
4. Calls `completeChannel` on each ledger with the other ledger's proofs and a verifier contract for the other ledger (Section 4).

### 2.1 `registerChannel`

| Input | Type | Meaning |
|---|---|---|
| `ownership_commitment` | `bytes32` | The ownership commitment for this ledger. |

The CLPR Service records the commitment as pending. Registering a commitment that is already pending has no further effect. A pending commitment for which no channel exists yet is the channel's PENDING status ([channel status](channel-state-transitions.md#1-channel-status)).

### 2.2 `completeChannel`

| Input | Type | Meaning |
|---|---|---|
| `channel_id` | `bytes32` | The channel id. |
| `public_key` | `bytes` | The registrant's public key on this ledger. |
| `signature` | `bytes` | A signature proving control of `public_key`. |
| `verifier_contract` | `bytes` | The address of the verifier contract for the peer ledger (Section 4). |
| `config_proof` | `bytes` | A proof of the peer's `LedgerConfiguration`. |
| `endpoint_manifest_proof` | `optional bytes` | A proof of the peer's local endpoint manifest ([manifest proofs](endpoint-manifest.md#5-manifest-proofs)); empty when absent. |

The message signed, the signature scheme and the key encoding are ledger-specific, and a ledger MAY require additional inputs for its own rules. These are defined in each ledger's README under *Registration signatures* (for example [Hiero](../ledgers/hiero/README.md#5-registration-signatures) and [EVM](../ledgers/evm/README.md#5-registration-signatures)).

The CLPR Service MUST reject the call if any of these holds:

| Condition |
|---|
| `keccak256(channel_id ‖ public_key)` is not a pending commitment. |
| A channel with `channel_id` already exists. |
| `signature` does not prove control of `public_key`. |
| `channel_id` does not satisfy a constraint this ledger places on it (Section 1). |
| `verifier_contract` is not a verifier (Section 4). |
| `verifyConfig(config_proof, channel_id, endpoint_manifest_proof)` fails ([verifier interface](verifier-interface.md#2-verifyconfig)). |
| The returned configuration has no throttles, or its timestamp is not valid ([`schema/`](schema/clpr_ledger_configuration.proto)). |

Otherwise it creates the channel with status ACTIVE, the channel context (Section 3), the verifier binding (Section 4), the initial peer state (Section 5) and the initial shared state (Section 6). How the Service stores or removes the commitment afterwards is a deployment choice ([Blueprint](../blueprint/clpr-service.md#1-structure-and-internal-state)).

## 3. Channel context

`ChannelContext` holds the constant data that identifies a channel to its verifier contract.

| Field | Type | Meaning |
|---|---|---|
| `channel_id` | `bytes32` | The channel id. |
| `service_address` | `bytes` | The address of the peer CLPR Service, from the `service_address` of the peer configuration returned by `verifyConfig`. |

The CLPR Service builds the channel context at `completeChannel` and stores it with the channel. It never changes. The Service passes it unchanged to every `verifyBundle` call for the channel ([verifier interface](verifier-interface.md#3-verifybundle)). Its encoding in a ledger's verifier API is defined there (for example [EVM](../ledgers/evm/verifier-api.md#32-channelcontext)).

## 4. Verifier binding

The verifier contract is named in `completeChannel`. It is either a contract deployed on the local ledger that implements the ledger's verifier API ([ledgers](../ledgers/README.md)), or a verifier provided by the ledger itself (for example [Hiero](../ledgers/hiero/README.md#3-built-in-verifiers)). The CLPR Service MUST reject an address at which there is neither a deployed contract nor a ledger-provided verifier.

The verifier binding is fixed for the life of the channel; no operation changes it. If the peer ledger's proof scheme changes so that the verifier can no longer verify its bundles, a new channel with a new verifier is needed. Applications can therefore evaluate a channel's verifier once.

## 5. Initial peer state

At `completeChannel`, the CLPR Service sets the channel's view of the peer from the outputs of `verifyConfig`. It MUST take these values only from the values returned by a successful `verifyConfig` call ([verifier interface](verifier-interface.md#2-verifyconfig)). Which of them the configuration proof must authenticate is an open issue ([OI-1](open-issues.md#oi-1-what-the-configuration-proof-must-authenticate)).

| Channel state | Initial value |
|---|---|
| Peer chain id | The returned `chain_id`. |
| Channel context | `channel_id` and the returned `service_address` (Section 3). |
| Peer configuration timestamp | The returned configuration timestamp. |
| Peer throttles | The returned throttles ([throttles](ledger-configuration.md#3-throttles)). |
| Trust anchor | The returned initial trust anchor. |
| Trust anchor id | The returned initial trust anchor id. |
| Peer manifest | The returned manifest, truncated as defined in [peer manifest](endpoint-manifest.md#4-peer-manifest). No manifest (version 0) if no manifest proof was supplied. |
| `endpoint_manifest_version` | The version of the returned manifest. |

The trust anchor and its id are stored with the channel and change only as defined in [verifier interface](verifier-interface.md#4-trust-anchor-changes). Later changes to the peer configuration arrive as ConfigUpdate messages ([configuration propagation](ledger-configuration.md#5-configuration-propagation)).

## 6. Shared channel state

The fields below are the channel state that the peer proves or consumes. Which of them the peer's verifier proves, and how each reaches the peer, is defined in [queue metadata](bundle.md#2-queue-metadata) and [proof requirements](bundle.md#4-proof-requirements). The structure is logical; how each ledger stores and proves it is ledger-specific (for example [Besu](../ledgers/besu/README.md#3-proven-storage-layout)). All other channel state is internal to the CLPR Service ([Blueprint](../blueprint/clpr-service.md#1-structure-and-internal-state)).

| Field | Type | Meaning | Initial value |
|---|---|---|---|
| `channel_id` | `bytes32` | The channel id (Section 1). | From `completeChannel`. |
| `status` | `ChannelStatus` | The channel's status ([channel status](channel-state-transitions.md#1-channel-status)). | ACTIVE |
| `endpoint_manifest_version` | `uint64` | The version of this side's copy of the peer's manifest ([peer manifest](endpoint-manifest.md#4-peer-manifest)). | Section 5 |
| `trust_anchor_id` | `bytes` | The identifier of the trust anchor this side holds for the peer ([trust anchors](verifier-interface.md#1-verifier-contracts-and-trust-anchors)). | Section 5 |

The shared channel state also holds the queue counters `next_message_id`, `sent_running_hash`, `acked_message_id`, `received_message_id` and `received_running_hash`, which are defined, with their initial values, in [message identifiers and queue](messaging.md#2-message-identifiers-and-queue). The messages in the channel's outbound queue are also proven to the peer.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
