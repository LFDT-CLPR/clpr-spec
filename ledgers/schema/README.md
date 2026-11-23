# Shared Ledger Schema

> **Category:** Ledger Specification (index) · **Applies to:** v0.2 · **Revision:** 1

The `.proto` files in this directory encode ledger state that more than one ledger's proof schemes prove to peers. The Protocol modules define what each structure means; these files define its bytes. The [encoding rules of the Protocol schema](../../protocol/schema/README.md#2-encoding-rules) apply, except that each proof scheme states how its verifiers decode these messages, including which fields they ignore ([conventions §3](../../protocol/conventions.md#3-abstract-data-structures)). Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_endpoint_manifest.proto`](clpr_endpoint_manifest.proto) | `ClprEndpoint`, `ClprServiceEndpoint` | [Endpoint](../../protocol/endpoint-manifest.md#1-endpoint) |
| | `ClprEndpointManifest` | [Endpoint manifest](../../protocol/endpoint-manifest.md#2-endpoint-manifest) |
