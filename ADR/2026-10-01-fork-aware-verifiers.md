# Fork-Aware Verifiers

Every ledger CLPR connects to will upgrade. Ethereum ships a named fork most years, OP Stack chains ship
hardforks on a timetable, and Cosmos chains upgrade by governance. Today a verifier pins the peer ledger's fork
parameters and proof layout when it is deployed, and `verifier_contract` is immutable after registration. The
first upgrade after a Channel opens therefore stops the Channel for good. This ADR defines one standard way
for every verifier, CLPR Service and endpoint to follow upgrades of the peer ledger: no single party can change
what a Channel accepts as proof, no message is lost or reordered, and an unhandled upgrade stalls a Channel
safely instead of breaking it.

**Changes in this ADR:**
- Upgrades of the source ledger are sorted into parameter, layout and semantic changes, each with its own authority.
- Every upgrade needs an armed fork profile before a verifier accepts proofs from it; verifiers fail closed.
- Fork parameters the source consensus signs are learned from proofs, never set by an administrator.
- A fork profile is armed only by dual control: proven announcement by the source ledger and timelocked registration by the destination.
- Profiles are submitted by a direct state proof, `submitForkProfile`, independent of message delivery.
- `ClprLedgerConfiguration` gains `fork_profiles`, sent only to peers at `protocol_version` 2 or higher.
- A new `ClprChannelSuccession` control message moves a Channel to a new verifier, carrying undelivered messages by proof.
- Verifiers report upgrade conditions with typed reverts after consensus verification; endpoints treat them as a safe stall.
- Endpoints publish fork readiness, and mainnet profiles need testnet evidence first.

---

## 1. Problem

### 1.1 Verifiers pin fork parameters that the peer ledger changes

A verifier checks consensus signatures, and those signatures usually commit to a fork identifier. On Ethereum
the sync committee signs over `compute_domain(DOMAIN_SYNC_COMMITTEE, fork_version, genesis_validators_root)`.
The reference Ethereum verifier stores `fork_version` in its trust anchor and never changes it. At the next fork
every signature check fails and the Channel stops accepting bundles.

### 1.2 Verifiers hard-code proof layouts that forks move

State proofs walk fixed paths. The reference Ethereum verifier proves the execution `state_root` at a fixed SSZ
generalized index in the block body, and the next sync committee at generalized index 87 of a 64-leaf
`BeaconState`. Deneb deepened the execution payload and Electra deepened `BeaconState`. Each such change breaks
every proof that crosses it. A verifier cannot detect a moved field by itself: an old generalized index still
yields a valid Merkle branch, but to a different field.

### 1.3 A stalled Channel with rotating signers dies

On ledgers whose signing authority rotates, a Channel must keep verifying bundles to follow the rotation. An
Ethereum sync committee serves one period of about 27 hours. If bundles are rejected for longer than that, the
trust anchor's committee no longer signs anything, and no later bundle can be verified under the Channel's trust.

### 1.4 Replacing a verifier loses queue position

The only way to adopt new verification logic today is a new Channel, with no way to carry queue position across.
Messages in flight on the old Channel are stranded, which breaks CLPR's ordered, exactly-once delivery.

### 1.5 A failing fork looks like a failing endpoint

A bundle rejected because of an upgrade reverts with the same generic errors as a forged bundle. Endpoints cannot
tell "the peer ledger forked and we are not ready" from "this proof is bad", so operators learn about forks from
stalled Channels.

---

## 2. Options Considered and Non-Goals

### Options Considered

**Upgradeable verifiers (proxy pattern).** A replaceable implementation fixes every upgrade, but gives one key
the power to change what the Channel accepts as proof. Rejected.

**Administrator-updated parameters.** An owner could update fork versions and generalized indices in place. A wrong
generalized index can point a proof at attacker-influenced data, such as 32 bytes of Ethereum block graffiti read
as a state root. One party must never be able to do this alone. Rejected as the only mechanism; kept as one half
of dual control (§3.4).

**Fork announcements delivered as queued messages.** The source ledger could announce profiles in its ConfigUpdate
and let verifiers pick them up from delivered bundles. An announcement made or enqueued late can then only be
delivered by post-fork bundles, which fail for lack of that same profile. Rejected in favour of a direct state
proof (§3.5).

**Pre-computing future forks.** Verifiers may ship with profiles for forks that are final at deployment, but most
forks are not. Rejected as a mechanism.

### Non-Goals

- Chain reorganisations. Finality and reorg safety are each verifier's own trust model.
- Upgrades of the local CLPR Service or the local ledger, covered by `protocol_version` and each platform's process.
- Choosing timelock values for particular deployments. §3.4 gives the minimum rule.
- Changes of a ledger's chain identifier. A new CAIP-2 identifier is a new peer ledger and needs a new Channel.

---

## 3. The Solution

### 3.1 Upgrade classes

Each upgrade of the source ledger is described by the most demanding class that applies to it.

| Class | What changes | Authenticated by | Needs |
| --- | --- | --- | --- |
| **A. Parameter** | Values the source consensus signs or commits to: fork identifiers, signing domains, validator sets | The source consensus, through the proof | A profile (§3.3), usually of kind UNCHANGED |
| **B. Layout** | Where proven data sits: generalized indices, trie paths, field positions, depths | Dual control over a fork profile | A profile of kind LAYOUT |
| **C. Semantic** | Verification logic: signature scheme, consensus protocol, commitment scheme, proof chain structure | New verifier code, under dual control | Channel succession (§3.7) |

A layout change that the verifier's profile format cannot express, for example a data structure removed from
the proof path, is Class C. Examples: Ethereum Gloas (EIP-7732) removes the execution payload from the block body
and is Class C for the reference Ethereum verifier; a move to Verkle or binary state trees is Class C; a
post-quantum signature scheme is Class C.

### 3.2 Fork identity and evidence

Each verifier family defines:

- `fork_id`: the bytes that name one fork of the source ledger (Ethereum: the 4-byte fork version).
- Fork evidence: how a verified proof shows which fork produced it (Ethereum: the fork version the sync committee
  signed under, and `BeaconState.fork` proven from the attested header's state root).

A verifier MUST establish a proof's `fork_id` from fork evidence that is authenticated by the source consensus.
It MUST NOT take a `fork_id` from the relayer unless the consensus proof confirms it. For Ethereum the relayer
states the version and signing slot; the aggregate signature only verifies under the version the committee
actually used, and the state proof shows `fork.previous_version`, `fork.current_version` and `fork.epoch`.

### 3.3 Fork profiles

A fork profile tells a verifier how to read proofs produced from one fork onward.

```protobuf
// Describes how to verify the source ledger's proofs from one fork onward.
message ClprForkProfile {
  // Family-defined fork identity. Ethereum: the 4-byte fork version.
  bytes fork_id = 1;

  // fork_id of the fork this one directly follows. MUST differ from fork_id.
  bytes predecessor_fork_id = 2;

  // Family-defined activation point, e.g. an 8-byte big-endian Ethereum epoch.
  bytes activation = 3;

  // UNCHANGED: proofs use the predecessor's layout; `layout` is empty.
  // LAYOUT: proofs use `layout`.
  ClprForkProfileKind kind = 4;

  // Family-defined layout descriptor. Its first byte is the descriptor format
  // version; a verifier MUST reject formats it does not implement.
  bytes layout = 5;
}

enum ClprForkProfileKind {
  UNCHANGED = 0;
  LAYOUT = 1;
}
```

`profile_hash = SHA-256(chain_id ‖ serialized ClprForkProfile)`, where `chain_id` is the source ledger's CAIP-2
identifier. The hash binds each profile to one source ledger.

Verifiers fail closed. A verifier MUST accept a proof only if the proof's `fork_id` is the fork recorded in the
trust anchor, or a fork with an armed profile. There is at most one armed profile per `fork_id` per Channel.

### 3.4 Arming a profile: dual control

A profile is **armed** for a Channel when all of these hold:

1. **Announced by the source.** The source ledger's CLPR Service holds the profile in its configuration. The
   destination learns this from a state proof of that configuration (§3.5), verified under the Channel's current
   trust anchor.
2. **Registered by the destination.** The destination CLPR Service's admin registered `profile_hash` for this
   Channel at least `T` ago and has not withdrawn it. `T` MUST be at least 7 days unless §3.6's emergency rule applies.
3. **Chained.** `predecessor_fork_id` is the fork recorded in the trust anchor, or the `fork_id` of a profile
   already armed on this Channel. Forks cannot be skipped or reordered, and a Channel that missed several forks
   catches up by arming each in turn.
4. **Unique.** No other profile with the same `fork_id` is armed on this Channel.
5. **Fresh.** The proven configuration's `timestamp` is at or after the registration time, and at or after the
   newest configuration `timestamp` any earlier `verifyForkProfile` call on this Channel proved. The trust anchor
   records that newest timestamp, so profile proofs never move backwards. A source veto therefore takes effect
   against every later proof.

Neither party can arm a profile alone. Either party can veto it before activation: the source by removing it
from its configuration, the destination by withdrawing the registration. After activation an armed profile is
permanent, because proofs already accepted under it cannot be un-accepted. The registering admin SHOULD be
independent of the source ledger's CLPR Service admin. A deployment where one organisation holds both roles MUST
say so, because dual control then reduces to that organisation.

Armed profiles are stored in the trust anchor (§3.8), so later changes to either configuration never alter an
armed profile.

### 3.5 Submitting a profile by state proof

Arming never depends on message delivery. The CLPR Service gains:

```
// Permissionless. Arms a fork profile for a Channel if §3.4 holds.
function submitForkProfile(bytes channel_id, bytes profile_proof)

// Destination admin only. Registers or withdraws a profile hash for a Channel.
function registerForkProfile(bytes channel_id, bytes profile_hash)
function withdrawForkProfile(bytes channel_id, bytes profile_hash)
```

The verifier interface gains:

```
// Verifies that the source ledger's configuration, at a state the current trust
// anchor can verify, contains `profile`. Returns the trust anchor with the
// profile recorded as armed.
//
// MUST revert if the proof does not verify under trust_anchor, if the profile is
// not in the proven configuration, or if §3.4 conditions 3 or 4 fail.
function verifyForkProfile(bytes trust_anchor, ChannelContext ctx, bytes profile_proof,
                           ClprForkProfile profile)
  returns (bytes new_trust_anchor, bytes new_trust_anchor_id)
```

`submitForkProfile` checks the registration and its age (§3.4 condition 2), calls `verifyForkProfile`, and stores
the returned trust anchor exactly as a bundle would. The proof is made against source state from before the fork,
so it verifies under the Channel's pre-fork trust even after the fork has happened, as long as the anchor's
signers can still sign (§3.6).

The source ledger announces profiles in its configuration:

```protobuf
message ClprLedgerConfiguration {
  // Protocol version. Implementations MUST reject configurations with
  // an unrecognized protocol_version. This ADR introduces version 2.
  uint32 protocol_version = 1;
  string chain_id = 2;
  bytes service_address = 3;
  Timestamp timestamp = 4;
  ClprThrottles throttles = 5;
  bytes initial_trust_anchor = 6;
  bytes initial_trust_anchor_id = 7;

  // Fork profiles for this ledger's own proofs: the current fork and announced
  // upcoming forks, in succession order. Present only when protocol_version >= 2.
  repeated ClprForkProfile fork_profiles = 8;
}
```

Each Channel runs at `channel_protocol_version = min(local protocol_version, peer protocol_version)`, recomputed
whenever either configuration changes. ConfigUpdates on a Channel are encoded at that version: a ledger at version 2
sends a peer at version 1 a version-1 ConfigUpdate without field 8, so upgrading one side never breaks the other.

### 3.6 Deadlines and emergencies

For a source family whose signers rotate, a profile MUST be armed before its fork's activation. After the last
pre-fork signer set expires, nothing can be verified under the Channel's trust, and the only recovery is Channel
succession with a fresh trust anchor (§3.7). Verifiers MUST keep accepting proofs of pre-fork state, including
signer rotations, after activation, so bundles already in flight are not lost.

An upgrade announced less than `T` before its activation is an emergency. The destination admin MAY register with
a shorter timelock `T_e` of at least 24 hours, and the Channel MUST emit `ClprEmergencyFork(channel_id, fork_id)`
when that registration is made, so applications can react before it arms. `verifyForkProfile` MUST check the
profile's `activation` against the fork evidence of the proofs it accepts (for Ethereum, the proven `fork.epoch`),
so neither admin can shorten the delay by announcing an early activation. If even `T_e` cannot be met, the Channel stalls (§3.9) and recovers by succession.

### 3.7 Class C: Channel succession

A semantic upgrade needs a new verifier and so a new Channel. Succession hands the predecessor's stream to the
successor without depending on the predecessor still working.

```protobuf
message ClprControlMessage {
  oneof payload {
    ClprConfigUpdate config_update = 1;
    ClprChannelSuccession channel_succession = 2;
  }
}

// Enqueued by the source CLPR Service on the predecessor Channel.
message ClprChannelSuccession {
  bytes successor_channel_id = 1;
  // The last message id the predecessor carries. Later messages use the successor.
  uint64 last_message_id = 2;
}
```

Channel state gains:

```
successor_channel_id : bytes   // empty unless a successor is linked
predecessor_channel_id : bytes // empty unless this Channel succeeds another
predecessor_last_message_id : uint64
```

Rules:

- **Pinned successor.** The destination admin registers the successor with
  `registerSuccessor(predecessor_id, successor_id, verifier_code_hash, anchor_hash)`, where
  `anchor_hash = H(initial_trust_anchor ‖ channel_context)` of the successor. The registration must be at least `T`
  old before the successor is linked, and `completeChannel` for the successor MUST produce exactly that verifier
  code hash and anchor hash. Whoever creates the successor therefore cannot choose its signers or its verifier.
- **Link by proof, not by queue.** The source Service records `ClprChannelSuccession` in the predecessor Channel's
  own state. The destination links the two Channels when the successor's verifier proves that record from the
  source ledger's storage. The record is never queued on the predecessor, so a predecessor that can no longer
  verify anything can still be succeeded.
- After recording the succession, the source Service MUST refuse `sendMessage` on the predecessor.
- **Hand-off by proof.** The successor's bundles MAY carry the predecessor's undelivered messages, from the
  predecessor's `received_message_id + 1` to `last_message_id`, proven from the source ledger's storage of the
  predecessor queue by the successor's verifier.
- The destination Service MUST deliver the predecessor's messages, by whichever Channel proves them first, before
  any successor Data Message, and MUST deliver each message id exactly once across both Channels. Once
  `last_message_id` is delivered, the predecessor moves to `DRAINED`.
- **Replies settle on the predecessor.** A Response to a handed-off message carries `(predecessor_id, message_id)`
  and travels on the successor; the source Service settles it against the predecessor's queue and connector
  escrow, so the predecessor can reach `CLOSED`.
- **Opt-in with a deadline.** Applications follow a succession by calling `followSuccession(channel_id)`. Messages
  for an application that has not opted in are held per application, not in the shared stream, so they never
  block other applications. After a deadline `D` (default 7 days) the Service answers each held Data Message
  with a failure Response `SUCCESSION_NOT_FOLLOWED`.
- `successorOf(channel_id)` returns the linked successor, if any.

### 3.8 Trust anchor contents

A fork-aware trust anchor carries, in its verifier-defined encoding:

```
current_fork_id   : bytes     // latest fork, by predecessor order, of any accepted proof; never moves back
previous_fork_id  : bytes     // kept so pre-fork proofs still verify after activation
armed_profiles    : list of { profile_hash : bytes, fork_id : bytes, activation : bytes, layout : bytes }
```

`trust_anchor_id` MUST change whenever the anchor's verification behaviour changes, so endpoints and the Service
can tell anchors apart. It is `H(signer_set_id ‖ current_fork_id ‖ H(armed_profiles))`, where `signer_set_id` is the
family's existing identifier (Ethereum: the sync committee period).

### 3.9 A fork the verifier cannot handle is a safe stall

Verifiers MUST report upgrade conditions with these typed reverts, and only after the consensus proof itself has
verified, so a bad bundle cannot hide behind them:

```
error ClprForkUnsupported(bytes fork_id)   // proof is from a fork with no armed profile
error ClprForkBoundary(bytes fork_id)      // proof straddles a fork boundary; retry with a later proof
error ClprForkLayoutUnsupported(uint8 format)  // armed profile uses a descriptor format this verifier lacks
```

A revert changes no state. Queues keep their order, and the Channel resumes when a profile is armed or a successor
takes over. Endpoints:

- MUST NOT treat these reverts as peer misbehavior or count them towards reputation or slashing.
- MUST back off exponentially on `ClprForkUnsupported`, capped at 10 minutes, and retry `ClprForkBoundary` with the
  next available proof.
- MUST raise an operator alert naming the Channel and `fork_id`.

### 3.10 Fork readiness

- Every endpoint MUST publish `clpr_fork_readiness{channel, fork_id, activation}` per Channel and upcoming fork:
  0 no profile, 1 announced, 2 registered, 3 armed.
- Endpoints SHOULD read the source ledger's published fork schedule (Appendix B) at least daily, and MUST alert 30
  days and 7 days before an activation whose readiness is below 3.
- A destination SHOULD register a mainnet profile only after the same verifier code, with that profile, has
  verified bundles captured from the source ledger's public testnet after its fork. Those captures are the
  profile's conformance vectors.

---

## 4. Testing

**Parameters and identity**
- A bundle signed under the next fork version, with proven `previous_version` equal to the anchor's fork and an
  armed profile, is accepted and returns an anchor with a new `trust_anchor_id`.
- The same bundle without an armed profile reverts with `ClprForkUnsupported`, and only after its signature verifies.
- A signature under a version with no chain to the anchor's fork is rejected.
- A boundary bundle reverts with `ClprForkBoundary`, and the next bundle succeeds.
- A Channel that missed two forks arms both profiles in order and then accepts proofs from the newer fork.

**Arming**
- Announced but unregistered, registered but unannounced, and registered for less than `T`: none arm.
- A second profile for an armed `fork_id`, or a profile whose `fork_id` equals its predecessor, is refused.
- A profile submitted by state proof after activation arms if the anchor's signers can still sign.
- A profile hash from another chain_id is refused.
- Withdrawal before activation prevents arming; withdrawal after arming has no effect.

**Deadlines and succession**
- Pre-fork signer rotations still verify after activation.
- Succession with an unregistered successor verifier is refused.
- The successor delivers the predecessor's undelivered messages by proof while the predecessor is stalled, each
  exactly once, before its own Data Messages.
- `sendMessage` on a predecessor with a succession enqueued is refused.
- An application that has not opted in receives nothing from the successor.

**Compatibility and endpoints**
- A version-1 peer never receives field 8 or the succession variant.
- Typed fork reverts do not reduce peer reputation, trigger backoff and alert.
- The readiness metric moves 0 → 1 → 2 → 3 as a profile is announced, registered and armed.

---

## Appendix A: Patching the Spec

To be completed once the design is accepted. Known changes:

- §1.1 `ClprLedgerConfiguration`: add field 8 and the `protocol_version` 2 note.
- §1.3 `ClprControlMessage`: add `channel_succession`; the text around spec lines 1122-1123, which limits
  ConfigUpdate to throttles, must also allow `fork_profiles`.
- Channel state: add the succession fields of §3.7.
- Verifier interface: add `verifyForkProfile`.
- Service interface: add `submitForkProfile`, `registerForkProfile`, `withdrawForkProfile`, `registerSuccessor`,
  `followSuccession` and `successorOf`.
- Response messages: add the optional predecessor reference for handed-off messages, and the
  `SUCCESSION_NOT_FOLLOWED` status.

## Appendix B: Implementation Notes

### B.1 Fork identity and evidence by family

| Source family | `fork_id` | Fork evidence | Typical Class B change | Typical Class C change | Published schedule |
| --- | --- | --- | --- | --- | --- |
| Ethereum beacon, Gnosis | 4-byte fork version | Signing domain; `BeaconState.fork` at generalized indices 268, 269, 270 (64-leaf state) | `BeaconState` or body depth and field positions | Gloas body change, state-tree change | `/eth/v1/config/fork_schedule` |
| OP Stack | Hardfork activation timestamp | L2 block timestamp, proven through L1 | Output root or predeploy storage layout | Proof system change | Superchain registry |
| Arbitrum Nitro | ArbOS version | ArbOS version in L2 state | Assertion or state layout | Proof system change | ArbOS releases |
| CometBFT | `header.version` block and app version | Validator-signed header | Store key layout | Signature scheme change | `x/upgrade` plans |
| Besu QBFT | Milestone block number | Header RLP shape at the milestone | New header fields | Consensus change | Genesis milestones |
| Hiero | Block proof format version | TSS-signed block proof | State proof path | Signature scheme change | Release notes |

Every family other than Ethereum needs confirmation by its verifier's authors before its first profile.

### B.2 Ethereum reference

- The relayer supplies the fork version and signing slot. The verifier builds the domain from them and verifies
  the aggregate signature, then proves `BeaconState.fork` at generalized index 67 of the attested state (the
  branch covers leaves 268 to 271). `current_version` must equal the signing version, and must equal either the
  anchor's `current_fork_id` or an armed profile's `fork_id`.
- Layout descriptor format 1: the generalized index of the execution `state_root` in the body, the generalized
  index of `next_sync_committee` in the state, and the generalized index of `fork` in the state.
- Gloas (EIP-7732) is Class C for format 1, because the execution payload leaves the block body.

### B.3 Contract size

The EVM Service's `BundleLogic` has about 1.7 KB of headroom. The new Service functions belong in a separate
`ForkLogic` module, following the existing logic-module pattern, and profile decoding in a shared library
contract used by all fork-aware verifiers. Hand-off delivery and the exactly-once cursor across two Channels sit
on the bundle path, so their decoding belongs in `BundleDecodeHelper`, and `BundleLogic` may need to be split.

### B.4 Cost

A fork evidence check adds one SSZ branch of 8 SHA-256 hashes, under 10,000 gas on the EVM. `submitForkProfile` is
one extra transaction per fork per Channel.
