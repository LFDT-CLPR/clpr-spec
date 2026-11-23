# Shared Ledger Schema

This directory holds the encodings that the proof schemes of more than one ledger use. The [Protocol schema](../../protocol/schema.md#1-scope) states the encoding rules that apply to them. Import paths are relative to the root of the specification repository.

| File | Messages | Meaning |
|---|---|---|
| [`clpr_endpoint_manifest.proto`](clpr_endpoint_manifest.proto) | `ClprEndpoint`, `ClprServiceEndpoint` | [Endpoint](../../protocol/endpoint-manifest.md#1-endpoint) |
| | `ClprEndpointManifest` | [Endpoint manifest](../../protocol/endpoint-manifest.md#2-endpoint-manifest) |
