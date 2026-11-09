# Open Issues

> **Non-normative.** This document is not a Protocol module, so it carries no version header or History.

This document lists known open design questions in v0.2. The modules each issue affects state the v0.2 rules; nothing here changes them. Resolving an issue that changes Protocol behavior requires a CLIP ([CLIP-0001 §5.2](../clips/clip-0001.md#52-what-each-change-needs)).

## OI-1. What the configuration proof must authenticate

**Problem.** When a channel is opened, `verifyConfig` returns the peer's chain id, CLPR Service address, configuration timestamp, throttles, initial trust anchor and trust anchor id, and endpoint manifest ([Verifier interface §2](verifier-interface.md#2-verifyconfig)). The channel stores them as its initial peer state ([Channel setup §5](channel-setup.md#5-initial-peer-state)). The Protocol does not state which of these values the configuration proof must authenticate against the peer ledger's committed state, and which a verifier can accept as supplied. The initial trust anchor raises a further question: a proof can only be checked against an anchor that is already trusted, so unless the verifier fixes the expected anchor itself, the initial anchor is accepted on first use and must be checked out of band.

**Current behavior.** The Protocol leaves this to each proof scheme. Channel users rely on the registrant's choice of verifier and on their own checks of the channel ([Overview §4](../clpr-overview.md#4-trust-model)).

**Options.**
1. The Protocol states, for each value `verifyConfig` returns, whether the configuration proof must authenticate it. Each proof scheme's configuration proof section states how its proof does so.
2. Values that cannot be proven at setup, at least the initial trust anchor, become explicit inputs to channel registration, recorded with the channel so that users can check them.
3. A verifier contract is deployed for one peer ledger with the expected trust anchor fixed at deployment, and `verifyConfig` proves against it.

**Affected modules.** [Verifier interface §2](verifier-interface.md#2-verifyconfig), [Channel setup §5](channel-setup.md#5-initial-peer-state), [Ledger configuration §2](ledger-configuration.md#2-ledger-configuration), the configuration proof section of every proof scheme, and each ledger's verifier API.

## OI-2. Configuration proof format for the QBFT epoch scheme

**Problem.** Opening a channel whose verifier uses the [QBFT epoch](../ledgers/besu/proof-schemes/qbft-epoch.md) scheme requires a configuration proof of the Besu ledger. Two incompatible forms exist:
- a protobuf structure holding the block header that carries the validator set, the ledger configuration, a current block header, and account and storage proofs for the CLPR Service;
- an RLP list of ten items holding a validator, the service address, the chain id, the configuration timestamp, the throttles, a block header and the epoch length.

A variant of the first form, with an added epoch length field, is returned by an optional endpoint query that the specification does not define. A strict decoder of the first form rejects it.

**Current behavior.** Verifiers accept one form or the other. No production component produces a configuration proof in either form. [QBFT epoch §9](../ledgers/besu/proof-schemes/qbft-epoch.md#9-configuration-and-manifest-proofs) describes the situation; neither form is normative.

**Options.**
1. Specify one form in the QBFT epoch scheme, and require producers and verifiers to conform.
2. Define a ledger-independent configuration proof structure in the Protocol, which each proof scheme fills with its own proof material.

**Affected modules.** [QBFT epoch §9](../ledgers/besu/proof-schemes/qbft-epoch.md#9-configuration-and-manifest-proofs), [Verifier interface §2](verifier-interface.md#2-verifyconfig), and, for option 2, the configuration proof section of every proof scheme.

## OI-3. Messages left without replies when a channel cannot drain

**Problem.** A channel PAUSED by a response ordering violation stays PAUSED until the peer corrects its replies, and a channel closed from PAUSED cannot drain until then ([Channel state transitions §5–6](channel-state-transitions.md#5-closing-and-draining)). If the peer never corrects them, or the channel was closed because its verifier is no longer trusted, DATA messages sent on it might never receive a REPLY. Applications cannot learn the outcome of those messages within the protocol, and a connector with messages in flight cannot be removed ([Connector setup §5](connector-setup.md#5-removal)).

**Current behavior.** The channel stays PAUSED or CLOSING indefinitely. Applications reconcile the affected messages out of band. The recovery scenarios are in [CLPR Service §7](../blueprint/clpr-service.md#7-recovery-scenarios).

**Options.**
1. Keep out-of-band reconciliation, and define standard queries that list a channel's messages without replies.
2. A forced close by the CLPR Service administrator that ends the channel without draining and resolves each message in flight locally, for example with the deprecated CHANNEL_CLOSED reply status ([Messaging §7](messaging.md#7-replies)).
3. Move undelivered messages and pending replies to a new channel to the same peer.

**Affected modules.** [Channel state transitions](channel-state-transitions.md), [Messaging §7](messaging.md#7-replies), [Connector setup §5](connector-setup.md#5-removal), [CLPR Service §2 and §7](../blueprint/clpr-service.md#2-administration).

## OI-4. Compensation for sending bundles

**Problem.** A CLPR Endpoint is paid only for bundles it submits to its own ledger ([Channel economics §2](../blueprint/channel-economics.md#2-payment-to-the-bundle-submitter)). Building proofs and serving bundles to the peer is unpaid. An endpoint can therefore receive without sending and leave the sending work to others. On a ledger that mostly sends and rarely receives, the margin earned on received messages might not pay for endpoint participation.

**Current behavior.** Endpoints prefer peers that deliver bundles to them ([CLPR Service §5](../blueprint/clpr-service.md#5-bundle-submission)), so endpoints that never send find fewer peers. Nothing else compensates sending.

**Options.**
1. Keep peer preference as the only mitigation.
2. Pay the sending endpoint a share of the destination charge. Bundles would then have to identify the sending endpoint in proven form.

**Affected modules.** [Channel economics](../blueprint/channel-economics.md), [CLPR Service §5](../blueprint/clpr-service.md#5-bundle-submission), and, for option 2, [Bundle §1](bundle.md#1-bundle-content) and [Endpoint sync](endpoint-sync/README.md).

## OI-5. Calibration of the connector stake

**Problem.** A connector's locked stake has to cover the worst-case losses its messages can cause: on the destination, the execution cost of messages that arrive while it is underfunded; on the source, the penalties for failure replies ([Stakes and bonds §1](../blueprint/stakes-and-bonds.md#1-connector-stake)). If the stake is too small, a connector can authorize a burst of messages that costs endpoints more than slashing recovers. v0.2 sets no method for choosing the minimum stake.

**Current behavior.** Each CLPR Service enforces a configured minimum stake. The minimum is not derived from the connector's possible exposure.

**Options.**
1. Derive the minimum stake from the throttles that bound exposure, such as queue depth and maximum gas per message, and from the execution price.
2. Limit each connector's messages in flight so that their worst-case cost stays within its stake.

**Affected modules.** [Stakes and bonds §1–2](../blueprint/stakes-and-bonds.md#1-connector-stake), [Channel economics §3](../blueprint/channel-economics.md#3-queue-quotas), [Ledger configuration §3](ledger-configuration.md#3-throttles).

## OI-6. QBFT epoch catch-up across a validator change

**Problem.** A bundle of the [QBFT epoch](../ledgers/besu/proof-schemes/qbft-epoch.md) scheme carries at most `maxHeaders` epoch boundary headers ([QBFT epoch §5](../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm)). Its block header must be sealed by a quorum of the validator set listed in the last boundary header it carries, or, with none, of the set in the trust anchor ([QBFT epoch §6](../ledgers/besu/proof-schemes/qbft-epoch.md#6-decode-and-verify-algorithm)). When the peer's trust anchor is more than `maxHeaders` epochs behind and the bundle proves state at the latest block, that block lies in a later epoch than the last boundary header. If the validator set changed in between by more than quorum overlap tolerates, the verifier rejects the bundle and the trust anchor does not advance, so the peer cannot catch up.

**Current behavior.** The scheme does not constrain the bundle's block when it carries fewer boundary headers than the peer needs. Catch-up over several bundles succeeds only if the set listed in the last boundary header carried reaches a quorum among the signers of the bundle's block.

**Options.**
1. When a bundle carries fewer boundary headers than the peer needs, the producer proves state at a block of the last boundary header's epoch.
2. Remove the per-bundle limit, so that a bundle carries every boundary header the peer needs, within the peer's `max_sync_bytes`.
3. Allow a bundle that carries only boundary headers and advances the trust anchor without proving queue state.

**Affected modules.** [QBFT epoch §5–7](../ledgers/besu/proof-schemes/qbft-epoch.md#5-encoding-algorithm), [Besu bundle aggregation](../ledgers/besu/bundle-aggregation.md), and, for option 3, [Bundle §1](bundle.md#1-bundle-content) and [Verifier interface §3](verifier-interface.md#3-verifybundle).

## OI-7. Protocol version at channel setup

**Problem.** Both sides of a channel must use the same protocol version ([Ledger configuration §4](ledger-configuration.md#4-protocol-version)). `verifyConfig` does not return the peer's protocol version ([Verifier interface §2](verifier-interface.md#2-verifyconfig)), so a channel can be opened between CLPR Services on different versions. The mismatch is detected only when a ConfigUpdate from the peer arrives and is rejected ([Ledger configuration §5.3](ledger-configuration.md#53-receiving)).

**Current behavior.** Channel setup does not check the peer's protocol version.

**Options.**
1. `verifyConfig` returns the peer's protocol version, and channel setup rejects a version different from the local one.
2. Keep detection at the first ConfigUpdate.

**Affected modules.** [Ledger configuration §4](ledger-configuration.md#4-protocol-version), [Verifier interface §2](verifier-interface.md#2-verifyconfig), [Channel setup §5](channel-setup.md#5-initial-peer-state), and each ledger's verifier API.

## OI-8. hinTS and WRAPS verification parameters

**Problem.** The hinTS with WRAPS proof scheme describes the signature layout, the encodings of curve points and the checks a verifier performs ([hinTS with WRAPS §4.4](../ledgers/hiero/proof-schemes/hints-wraps.md#44-block-signature) and [§6](../ledgers/hiero/proof-schemes/hints-wraps.md#6-decode-and-verify-algorithm)). It does not give the WRAPS verification key, the Poseidon parameters or the full hinTS verification steps. Without them, a verifier for this scheme cannot be built from the specification alone.

**Current behavior.** Verifiers of this scheme take these parameters from the cryptographic library that produces the proofs.

**Options.**
1. Specify the parameters and the hinTS verification steps in a later revision of the scheme. This is a Ledger Specification change and needs no new specification version.
2. Reference a published specification of hinTS and WRAPS that defines them.

**Affected modules.** [hinTS with WRAPS](../ledgers/hiero/proof-schemes/hints-wraps.md).
