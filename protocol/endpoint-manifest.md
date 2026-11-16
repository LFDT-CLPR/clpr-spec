# Endpoint Manifest

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

The **endpoint manifest** is the on-ledger list of the CLPR Endpoints that serve a CLPR Service. Each CLPR Service maintains its own manifest, and each channel holds a proven copy of the peer's manifest. Endpoints find each other only through these manifests. Encodings are in [`schema/`](schema/README.md).

## 1. Endpoint

`Endpoint` describes one CLPR Endpoint.

| Field | Type | Meaning and constraints |
|---|---|---|
| `service_endpoint` | `optional ServiceEndpoint` | Where the endpoint accepts [endpoint sync](endpoint-sync/README.md) connections. An endpoint whose `service_endpoint` is absent, or has an empty `ip_address`, only initiates syncs, for example on a private network. |
| `tls_certificate` | `optional bytes` | The endpoint's TLS CA certificate: a DER-encoded X.509 certificate with an ECDSA P-384 key; empty when absent. Peers use it to authenticate the endpoint in mutual TLS; an empty value means the endpoint serves plaintext ([transport](endpoint-sync/README.md#2-transport)). An empty value is always accepted. A CLPR Service MAY validate a non-empty value when an endpoint is registered (for example [EVM](../ledgers/evm/README.md#6-endpoint-certificates)). |
| `account_id` | `optional bytes` | The ledger-specific account identifier of the endpoint's operator; empty when absent. It is not used by the network. |

`ServiceEndpoint`:

| Field | Type | Meaning and constraints |
|---|---|---|
| `ip_address` | `string` | A numeric IPv4 or IPv6 address, or empty (Section 1). DNS host names are not allowed. |
| `port` | `uint32` | The TCP port, at most 65535. |

## 2. Endpoint manifest

`EndpointManifest` is the endpoint set of one CLPR Service. It is scoped to the Service, not to a channel: every endpoint in it serves all of the Service's channels.

| Field | Type | Meaning and constraints |
|---|---|---|
| `version` | `uint64` | The manifest version. It starts at 1 and increases by exactly 1 with each change to the endpoint set; a change applied as one batch counts once. It has no relation to any other version number. |
| `service_address` | `bytes` | The address of the CLPR Service the manifest belongs to, equal to the `service_address` of its [ledger configuration](ledger-configuration.md#2-ledger-configuration). It binds the manifest to that Service. |
| `endpoints` | `Endpoint[]` | The current endpoint set, in an order defined by the Service. It MAY be empty: a manifest with `version` ≥ 1 and no endpoints is valid. |

A valid manifest has `version` ≥ 1. The value `version` = 0 with no endpoints denotes **no manifest**. It appears only in a channel's peer manifest before a proven manifest has been installed (Section 4), and as a verifier output when no manifest was proven.

## 3. Local manifest

Each CLPR Service maintains one **local manifest**: the `EndpointManifest` of its own endpoints. It is Service state, separate from the ledger configuration (the configuration's deprecated `endpoints` field is not the manifest).

- The local manifest's `version` increases as defined in Section 2 whenever its endpoint set changes.
- The number of endpoints MUST NOT exceed the ledger's `max_local_endpoints` when that is non-zero ([throttles](ledger-configuration.md#3-throttles)).
- Any caller MAY read the current local manifest. It is part of the Service state that the ledger's proof schemes can prove to peers (Section 5).

How endpoints are admitted to and removed from the local manifest is a deployment choice ([Blueprint](../blueprint/clpr-service.md#3-endpoint-admission)).

## 4. Peer manifest

Each channel holds a copy of the peer CLPR Service's manifest, the **peer manifest**, together with `endpoint_manifest_version`, the version of that copy. The version is part of the [shared channel state](channel-setup.md#6-shared-channel-state), so the peer learns how current its copy on this ledger is.

**Installation.** The peer manifest is first set at [channel setup](channel-setup.md#5-initial-peer-state) from the manifest returned by `verifyConfig`. If no manifest proof was supplied, it starts as no manifest (version 0).

**Update.** When a bundle's verified content includes a manifest whose `version` is greater than the channel's `endpoint_manifest_version`, the CLPR Service MUST replace the peer manifest with it as a whole and set `endpoint_manifest_version` to its version. A manifest whose version is not greater is ignored; it does not cause the bundle to be rejected. The point in bundle processing at which this happens is defined in [bundle processing](channel-state-transitions.md#2-bundle-processing).

**Truncation.** When a manifest is installed or updated and its endpoint list is longer than the local `max_peer_endpoints` (when non-zero), the CLPR Service keeps only the first `max_peer_endpoints` endpoints, in manifest order. The stored version is the manifest's version.

**Empty manifest.** A peer manifest with no endpoints is valid, and channel setup MUST NOT fail only because the peer's manifest is empty. While a channel's peer manifest has no endpoints, its local endpoints cannot initiate syncs and depend on the peer's endpoints to initiate them. If neither side lists an endpoint, the channel makes progress only when someone submits bundles directly; bundle submission is open to any caller.

## 5. Manifest proofs

A Service's local manifest reaches its peers only as proven content, in two ways:

1. **At channel setup.** `completeChannel` takes an optional manifest proof, which is passed to `verifyConfig` ([registration](channel-setup.md#2-registration)). The registrant SHOULD supply it. The proof MUST be verifiable against the initial trust anchor established by the same `verifyConfig` call. When it is empty, the channel starts with no manifest and installs the peer manifest from the first bundle that carries one.
2. **In bundles.** A bundle MAY carry a proof of the source Service's current local manifest ([bundle content](bundle.md#1-bundle-content)). An endpoint includes one when the peer's copy is older than the local manifest, as reported in sync requests and in the peer's queue metadata ([endpoint obligations](endpoint-sync/README.md#5-endpoint-obligations)). The receiving Service applies the update rule of Section 4.

At channel setup the verifier MUST reject a manifest whose `service_address` differs from the returned `service_address`, and a supplied manifest proof that yields `version` 0 ([verifyConfig](verifier-interface.md#2-verifyconfig)). In a bundle it MUST reject a manifest whose `service_address` differs from the `service_address` of the channel context, and MUST NOT return a manifest with `version` 0 ([verifyBundle](verifier-interface.md#3-verifybundle)). How each ledger's manifest is proven is defined by its proof schemes ([ledgers](../ledgers/README.md)).

## 6. Endpoint discovery

A channel's peer manifest is the only source of peer endpoints that this specification defines. A CLPR Endpoint chooses which peer endpoints to contact from it ([Blueprint](../blueprint/clpr-service.md#53-peer-selection)) and contacts them through [endpoint sync](endpoint-sync/README.md). An endpoint that only initiates syncs (Section 1) cannot be contacted.

Other means of discovery are outside this specification. An implementation MAY use them, since any caller can submit a bundle.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
