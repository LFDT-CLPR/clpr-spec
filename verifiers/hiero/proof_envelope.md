# Hiero proof envelope, version 1

This is an opt-in proof profile for a verifier whose trust anchor is a particular
hinTS verification key (VK). It supports authenticated successor authorization
without a recursive WRAPS proof. It does not change the ledger-ID/WRAPS profile.
A channel's verifier determines its profile; receivers MUST NOT infer the profile
from attacker-supplied proof bytes or fall back to another profile on failure.

## Placement and encoding

`ClprBundleContent.bundle_payload` remains opaque and unchanged. Its contents for
this profile are the serialized `HieroProof` in [hiero_proof.proto](hiero_proof.proto).
The envelope belongs beside `StateProof` in HAPI's `block/stream` package, with the
provenance messages in the same schema. This PR specifies the proposed HAPI
addition; publication in HAPI and endpoint construction are separate integrations.
`StateProof`, its signed block proof, and the outer CLPR transport are not redefined.

Version 1 requires `format_version = 1`, followed by exactly one nonempty payload.
The envelope and provenance messages MUST use ascending field order, shortest
uint32 varints, and exactly the fields defined here. Duplicate singular fields,
unknown fields, duplicate/conflicting payload arms, missing required fields,
truncation, overflow, and trailing data MUST be rejected. Repeated links retain
order. These restrictions are stricter than a generic protobuf parser: a generated
`oneof` parser alone does not enforce them. StateProof's existing encoding rules
continue to apply inside the state-proof arm. Future extensions use a new envelope
version; unknown versions MUST fail closed, with no retry as a bare StateProof.

## Key-provenance payload

`initial_verification_key` MUST equal the channel's current raw VK byte for byte.
There MUST be between 1 and 8 links, in forward order. For each link:

1. Validate the successor VK's canonical encoding, group membership, and supported
   power-of-two domain. This checks key shape, not the internal consistency of its
   commitments or the security of its CRS; see the authority assumption below.
2. Verify `signature` under the preceding VK over **exactly the raw bytes** of
   `next_verification_key`. Do not hash, prefix, ABI-encode, or append epoch IDs.
3. Require signers' authenticated weight to be strictly greater than one third of
   the preceding key's total weight (aBFT threshold). Weight at exactly one third
   MUST fail. The aggregate must prove the selected parties' weight, not merely a
   BLS pairing under a caller-supplied aggregate public key.
4. Reject the successor if it equals any VK already in this bundle, including the
   initial VK. Then use it as the authority for the following link.

The V1 crypto suite is hiero-cryptography 3.23.0's hinTS V2: a 1,096-byte uncompressed
VK and a 1,248-byte aggregate signature, with the library's canonical scalar and
point encodings and V2 Fiat–Shamir domains. Other encodings/suites require a new
version. A verifier MUST validate all links before returning any update.

Key validation does not establish that the domain size agrees with the `Z`
commitment, that `W` commits to the stated total weight, or that the CRS was
constructed securely with its trapdoor assumptions satisfied. The predecessor's
strictly-greater-than-one-third authorization of the exact successor bytes is the
basis for trusting those properties. The initially pinned key requires the same
properties to be established out of band.

Success returns all-zero channel sync data, no messages, no manifest, no message
anchor, the final raw VK as `new_trust_anchor`, and its 32-byte
Keccak-256 digest as `new_trust_anchor_id`. The CLPR service commits only these two
authority fields, atomically. The identifier is a cache/routing hint; it is not an
epoch counter, signature target, or independent source of authority.

Endpoints may split longer chains into batches of at most eight links, additionally
bounded by receiver `max_sync_bytes` and execution gas. They MUST begin each batch
at the receiver's actual current VK, and reread it after a competing update. A
stale or already applied batch fails the initial-key comparison. Do not concatenate
state proofs to this payload; submit a state-proof bundle after catch-up. Eight
links is a wire ceiling, not a guaranteed feasible transaction size: execution
cost depends on the target chain's precompile pricing and transaction gas cap.
Endpoints MUST estimate the complete service transaction, including calldata,
and choose smaller batches when needed.

## Signed authorization is sufficient

Acceptance means **the predecessor signing authority authorized this successor**.
It does not prove that the source network adopted the candidate roster, that an
epoch number advanced, that this is the latest key, or that no competing candidate
was authorized. Signatures collected before roster adoption are sufficient under
this profile. Epoch/construction IDs and the provenance queue's inclusion in source
state are not authenticated by these raw-VK signatures.

Endpoints SHOULD source chains from the consensus node's adopted
`HINTS_KEY_PROVENANCE` queue and retain that evidence, rather than assembling them
from raw proof votes. The queue appends a link with adoption, while proof votes
can expose the same valid authorization before adoption. This endpoint policy
improves availability; queue inclusion is not an on-chain security predicate.

`submitBundle` is permissionless. Any third party that obtains a valid candidate
authorization can advance the channel, even if the configured endpoints follow
only the adopted queue. Multiple valid authorizations can form branches; a
verifier holding one successor need not accept a sibling. A third party can thus
strand the channel on an unadopted or abandoned branch from which no usable
successor or state proof is available. There is no administrative re-anchor or
rollback path. Recovery for new traffic requires a new channel using a verifier
pinned to an independently authenticated current key.

Closing the old channel does not bypass this problem: `CLOSING` drains only as
peer acknowledgments and required responses arrive, and `DRAINED` can close only
when every outbound message is acknowledged. If the stranded anchor prevents
those proofs, closure and in-flight message accounting can remain blocked
indefinitely. A channel with no outstanding drain or acknowledgment obligations
can still close. A new channel does not settle the old channel's obligations.

A source signing authority must not authorize a backward edge, reuse an old key
as a successor, or endorse an unsafe candidate. The service stores only its
current anchor, so the within-bundle cycle check cannot detect historical cycles
across separate transactions. Requiring proof of adoption, chronological
monotonicity, uniqueness, administrative re-anchoring, or forced closure would
change this profile or the service's trust/lifecycle policy.

## State-proof payload

Verify the unchanged StateProof's Merkle paths using SHA-384 and authenticate the
48-byte block root with hinTS under the **current stored VK**. The block-signature acceptance
threshold is strictly greater than one third of the stored key's total weight,
with authenticated signer weight and exact-one-third rejection, just as for
provenance links. This is a verifier policy, not a claim that the source network
uses the same collection threshold: network configuration, native-library
defaults, and HAPI descriptions may require higher fractions. The VK does not
encode a threshold. This policy relies on fewer than one third of the weight
being Byzantine and on honest signers signing only valid block roots; exceeding
one third then includes honest weight. Changing this threshold requires an
explicit profile change, not inference from proof bytes.

This state-proof arm supports SHA-384-configured sources only; SHA-256 requires
a different profile. The leaf bindings, domain bytes, and source construction
references are in [Hiero state proofs](state_proof.md).

V1 accepts a block signature of
`VK (1096 bytes) || hinTS signature (1248 bytes)`, or the native 13,712-byte combined
TSS representation whose first 2,344 bytes are that prefix. In the latter form the
remaining 11,368 WRAPS bytes are not authority evidence in this profile; the
prefix VK MUST still match the stored anchor exactly. No arbitrary suffix lengths
are permitted. Endpoints MUST normalize any other composite signature
representation to the 2,344-byte compact form, preserving the exact VK and hinTS
aggregate bytes. All required paths must converge to the authenticated block root;
the proven channel identity must match the channel context, and carried endpoint
manifests must match its remote service address.

Success returns ordinary proven channel data, whose `next_message_id` is at least 1,
and messages. It returns no trust-anchor change. A state-proof bundle with no messages
still requires actual channel-state evidence; it is distinct from provenance-only
absence. Normal CLPR replay, running-hash, ack, progress and status rules apply.

## Compatibility and bootstrap

Select and trust the initial VK out of band when configuring the verifier/channel.
A key supplied only by an untrusted bundle cannot bootstrap itself. A pinned-key
verifier may decode the usual configuration control payload and seed the anchor
from its deployment configuration; decoding that payload does not make it a state
proof. Channel-establishment governance retains responsibility for that config.
Every new channel established through this verifier starts from its deployment's
pinned initial key, even if older channels have already advanced. Catch-up cost
therefore grows with rotations since that pin. Operators SHOULD periodically
deploy a verifier pinned to an independently authenticated recent VK for new
channels; this does not re-anchor existing channels.

An optional config-time manifest proof must use the state-proof envelope and the
pinned initial key. It cannot use a provenance chain to reach a later key during
configuration. A current manifest proof signed only by a later key is therefore
unusable at setup under an older pin. Either configure with a verifier pinned to
a suitable current key, or omit the optional manifest proof, catch up after
channel creation, and then prove the manifest in a state-proof bundle.

The shared verifier interface is unchanged: an authority-only result is marked by
all-zero channel sync data and a successor authority. This does not migrate existing
channels from ledger-ID anchors to VK anchors, or change the native CLPR precompile
ABI automatically.

## Required conformance cases

- Five successive native-library-signed links advance E−5 to E; E verifies a later
  state proof. The same chain split into batches yields the same final key.
- Wrong initial key, missing/reordered/forged links, self/cyclic links, exact-one-third
  weight, malformed keys/signatures, >8 links, and stale replay are rejected.
- Unknown versions, legacy bare proofs, conflicting arms, nonminimal varints,
  duplicates, truncation and trailing bytes are rejected without fallback.
- An invalid final link leaves the original anchor unchanged.
- Authority-only updates on ACTIVE, PAUSED, CLOSING and DRAINED channels preserve
  all queue/ack counters and hashes, messages, configuration, manifests, status,
  and application effects. They do not auto-resume or close a channel.
- A result with `next_message_id` of zero and nonempty channel data/messages/manifest,
  an empty successor, empty successor ID, or unchanged authority is rejected by the service.
