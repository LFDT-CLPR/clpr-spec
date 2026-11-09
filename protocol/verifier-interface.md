# Verifier Interface

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

A **verifier contract** checks the proofs that one ledger receives from another. This module defines its abstract interface: two functions, `verifyConfig` and `verifyBundle`, with their inputs, outputs and obligations. Each ledger binds this interface in its verifier API, written in the ledger's contract language ([ledgers](../ledgers/README.md); for example the [EVM verifier API](../ledgers/evm/verifier-api.md)). What a verifier checks inside a proof is defined by the proof scheme it implements.

## 1. Verifier contracts and trust anchors

CLPR does not depend on any particular proof system. The CLPR Service never interprets proof bytes; it passes them to the channel's verifier contract and acts on the verified content returned. Each channel is bound to one verifier contract when it is set up ([verifier binding](channel-setup.md#4-verifier-binding)).

**Statelessness.** Both functions MUST be read-only with respect to CLPR Service state, and the CLPR Service MUST invoke them so that they cannot modify its state. A verifier keeps no per-channel state. What changes over a channel's lifetime is passed in and returned:

- The **trust anchor** is the material a verifier needs to check proofs from the peer ledger, such as a ledger id or a validator set. Its content and encoding are defined by the proof scheme; to the CLPR Service it is opaque bytes. Its **trust anchor id** is an opaque identifier of it, also defined by the proof scheme.
- The CLPR Service stores `trust_anchor` and `trust_anchor_id` with the channel. They are set from `verifyConfig` at [channel setup](channel-setup.md#5-initial-peer-state) and changed only by bundle processing, from `verifyBundle` (Section 4). No administrative operation changes them.
- The constant data identifying the channel, its id and the peer's CLPR Service address, is passed as the [channel context](channel-setup.md#3-channel-context) `ctx`. It is the same on every call for a channel.

A verifier MAY keep global state that is not specific to any channel, such as a revocation list maintained by its administrator.

## 2. verifyConfig

```
verifyConfig(config_proof: bytes, channel_id: bytes32, endpoint_manifest_proof: bytes)
  → (ctx, chain_id, service_address, config_timestamp, throttles,
     initial_trust_anchor, initial_trust_anchor_id, endpoint_manifest)
```

The CLPR Service calls `verifyConfig` once, when it completes a channel ([registration](channel-setup.md#2-registration)).

Inputs:

| Input | Type | Meaning |
|---|---|---|
| `config_proof` | `bytes` | A proof of the peer's [ledger configuration](ledger-configuration.md#2-ledger-configuration), in the format of the proof scheme. |
| `channel_id` | `bytes32` | The id of the channel being set up. |
| `endpoint_manifest_proof` | `bytes` | A proof of the peer CLPR Service's endpoint manifest. Can be empty ([manifest proofs](endpoint-manifest.md#5-manifest-proofs)). |

Outputs:

| Output | Type | Meaning |
|---|---|---|
| `ctx` | `ChannelContext` | `channel_id` as given, and `service_address`. The CLPR Service stores it with the channel. It MAY instead build the same value from `channel_id` and `service_address`. |
| `chain_id` | `string` | The peer's chain id, from the configuration that `config_proof` carries. |
| `service_address` | `bytes` | The peer CLPR Service's address, from the configuration that `config_proof` carries. |
| `config_timestamp` | `timestamp` | The configuration's `timestamp`. Stored as the channel's peer configuration timestamp ([configuration propagation](ledger-configuration.md#5-configuration-propagation)). |
| `throttles` | `Throttles` | The configuration's throttles. Stored as the channel's peer throttles ([throttles](ledger-configuration.md#3-throttles)). |
| `initial_trust_anchor` | `bytes` | The channel's first trust anchor. Taken from the configuration's `initial_trust_anchor` when the peer publishes its signing authority there; otherwise derived by the verifier from other proof material in `config_proof`. Empty only when the proof scheme needs no trust anchor. |
| `initial_trust_anchor_id` | `bytes` | The identifier of `initial_trust_anchor`. Taken from the configuration when present, otherwise computed by the verifier. |
| `endpoint_manifest` | `EndpointManifest` | The proven manifest, with `version` ≥ 1, or no manifest (version 0, no endpoints) when `endpoint_manifest_proof` is empty. |

Obligations. `verifyConfig` MUST fail if:

- `config_proof` is not a valid proof of a ledger configuration under the proof scheme, or `endpoint_manifest_proof` is non-empty and is not a valid proof of a manifest;
- the proofs are not valid under the returned `initial_trust_anchor`;
- the manifest's `service_address` differs from the returned `service_address`, or a supplied manifest proof yields `version` 0;
- the trust anchor outputs violate the rule in Section 4.

It MUST NOT fail only because the manifest lists no endpoints. Which of these outputs a configuration proof authenticates is an open question ([OI-1](open-issues.md#oi-1-what-the-configuration-proof-must-authenticate)).

## 3. verifyBundle

```
verifyBundle(bundle: bytes, trust_anchor: bytes, ctx: ChannelContext)
  → (metadata, messages, last_message_id, last_message_running_hash,
     new_trust_anchor, new_trust_anchor_id, new_endpoint_manifest)
```

The CLPR Service calls `verifyBundle` for every bundle submitted on the channel ([bundle processing](channel-state-transitions.md#2-bundle-processing)).

Inputs:

| Input | Type | Meaning |
|---|---|---|
| `bundle` | `bytes` | The bundle, in the wire layout of the proof scheme. |
| `trust_anchor` | `bytes` | The trust anchor currently stored with the channel. |
| `ctx` | `ChannelContext` | The channel context stored with the channel. |

Outputs: the abstract bundle content, as defined in [bundle content](bundle.md#1-bundle-content). `new_endpoint_manifest` is absent when the bundle proves no manifest.

Obligations. The verifier:

- MUST verify the bundle as required by [proof requirements](bundle.md#4-proof-requirements), under `trust_anchor`, and bind it to `ctx.channel_id` and, where the source ledger can host more than one CLPR Service, to `ctx.service_address`.
- MUST take every field of `metadata` that it returns from the proven channel state, and `last_message_id` and `last_message_running_hash` from the proven queue entry of the last message.
- MUST return each message's payload bytes exactly as the bundle carries them, in id order.
- MUST fail if:
  - the proof is invalid;
  - the proven channel state or last message entry belongs to a channel other than `ctx.channel_id`;
  - a proven manifest's `service_address` differs from `ctx.service_address`;
  - messages are returned and `last_message_id ≥ metadata.next_message_id`;
  - messages are returned and the first id, `last_message_id − len(messages) + 1`, is not greater than the source's proven `acked_message_id`.
- MUST NOT return a `new_endpoint_manifest` with `version` 0.
- MUST return a non-empty `new_trust_anchor` only as Section 4 allows.
- SHOULD fail on malformed input before it performs expensive cryptographic operations.

The verifier does not check the running hash, the message ids against the destination's state, replay or response ordering. The CLPR Service performs those checks after the call ([bundle processing](channel-state-transitions.md#2-bundle-processing)).

## 4. Trust anchor changes

A non-empty `new_trust_anchor` returned by `verifyBundle` replaces the stored trust anchor. It is one of two kinds:

- A **trust anchor change** returns a `new_trust_anchor_id` that differs from the stored `trust_anchor_id`. It records a new signing authority, for example after a validator set change on the peer ledger, or another advance that the proof scheme defines, for example a later anchored epoch. The bundle is verifiable under the current `trust_anchor` and contains a proven commitment to the new trust anchor. When the signing authority changes, `verifyBundle` MUST return a trust anchor change. A bundle that makes a trust anchor change MAY carry no messages; it makes progress by the change itself ([progress](channel-state-transitions.md#3-progress)).
- A **trust anchor update** keeps the authority. A verifier MAY return one to update verifier-internal data that does not change which proofs it accepts, such as a cache. Its `new_trust_anchor_id` MUST equal the stored `trust_anchor_id`. An update alone does not make progress.

When the verifier returns neither, `new_trust_anchor` is empty and the stored trust anchor stays unchanged. A returned trust anchor that is not a proven successor MUST NOT change which proofs the verifier accepts.

The CLPR Service replaces `trust_anchor` and `trust_anchor_id` before it processes any message of the bundle, and verifies every later bundle under the new value. A verifier MUST accept a proof only from an authority included in the `trust_anchor` it is given, or from an authority proven within the same bundle to succeed one.

A verifier MAY accept several consecutive changes in one bundle, verifying each against the authority established by the previous one, and return only the last. The bundle MAY also carry messages proven under that last authority.

**Identifiers.** For both `verifyConfig` and `verifyBundle`, a trust anchor id MUST be non-empty if and only if its trust anchor is non-empty. The CLPR Service MUST reject verifier output that violates this rule: channel setup fails, or the bundle is rejected.

**Compatibility.** A source ledger can be used with CLPR only if, whenever its signing authority changes, a proof can be built that is verifiable by an authority in the current trust anchor and contains a proven commitment to the new authority.

The Protocol sets no deadline for submitting a trust anchor change. When a trust anchor holds a single authority, proofs from the previous authority stop verifying as soon as the change is accepted. Endpoint obligations for keeping the peer's trust anchor current are defined in [endpoint sync](endpoint-sync/README.md#5-endpoint-obligations); each proof scheme defines when its trust anchor changes.

## 5. Rejection

A verifier function signals rejection by failing; how a failure is expressed is defined by the ledger's verifier API. A function that fails returns no output.

- When `verifyConfig` fails, channel setup fails and no channel is created.
- When `verifyBundle` fails, the CLPR Service rejects the whole bundle. The channel's state does not change, and the channel's status is unaffected. The submitter bears the cost of the submission.

Each proof scheme lists every condition under which its verifier fails. Rejection is the only response to an invalid proof; a verifier does not report partial results.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
