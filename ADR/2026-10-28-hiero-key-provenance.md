# Explicit Hiero key provenance and absent channel state

Status: proposed.

A peer whose trusted hinTS key is several rotations behind needs to advance trust
before it can verify a current block signature. The CN provenance queue supplies
predecessor signatures over successor VK bytes; these signatures do not include a
channel-state proof or prove adoption of the candidate roster.

We select signed successor authorization as sufficient for this opt-in verifier
profile. Requiring adoption would require additional evidence beyond those
signatures. The decision deliberately accepts the candidate-branch and key-reuse
consequences documented in the normative [HieroProof V1 profile](../verifiers/hiero/proof_envelope.md).
This is a named exception to CLPR's default requirement for state-proven successor
authority; it does not relax the other verifier profiles.

Submission is permissionless: an unrelated party may submit a valid authorization
published in a proof vote before adoption, despite endpoints following the adopted
provenance queue. Selecting an unadopted or abandoned branch can irreversibly strand
the receiver. No administrative re-anchor or force-close mechanism is introduced.
Unacknowledged outbound messages and required responses prevent normal drain/close
progress when no acceptable peer proof can arrive; message accounting may remain
locked. A new channel pinned to a recent authenticated key restores future traffic,
not settlement of the old channel's obligations.

Both provenance and block-state signatures use strictly greater than one third
of the pinned key's weight. This relies on fewer than one third Byzantine weight
and honest signers endorsing only valid successors/block roots; it does not assert
that the network's signature collection threshold is also one third.

A versioned HieroProof envelope selects unchanged StateProof bytes or a bounded
key-provenance chain. The envelope is specified beside StateProof in HAPI rather
than in the ledger-neutral CLPR transport or in the consensus node's state queue.
This repo owns the protocol definition; the proposed proto is ready for a separate
HAPI publication. The existing WRAPS/ledger-ID verifier remains a separate profile.

Authority-only results are marked by all-zero channel sync data together with a
successor authority, not by an extra verifier return. `next_message_id` is initialized to 1 and the replay defense
rejects a value below `received_message_id + 1`, so no accepted state-bearing
result is all-zero. The service writes only the anchor and ID, returning before
channel processing. A state-bearing empty-message bundle still follows the normal
path. A state proof that decodes to all-zero sync data and carries a changed
successor is treated as authority-only; without a changed successor it is rejected.

The verifier interface and shared storage layout are unchanged. No automatic
anchor-profile migration or claim of roster adoption is introduced. Endpoints must implement the envelope, retain
rotation evidence, and submit state proofs separately after catch-up.
