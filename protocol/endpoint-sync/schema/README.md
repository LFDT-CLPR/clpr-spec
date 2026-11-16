# Endpoint Sync Schema

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

Machine-readable definitions for [endpoint sync](../README.md). The behavior is specified in the module; the encoding rules of the [Protocol schema](../../schema/README.md#2-encoding-rules) apply.

| File | Defines |
|---|---|
| [`clpr_endpoint_sync.proto`](clpr_endpoint_sync.proto) | `service ClprEndpointService` with `rpc sync(stream ClprSyncPayload) returns (stream ClprSyncPayload)`; messages `ClprSyncPayload`, `BundleRequest`, `BundleResponse` |

The file imports `ClprChannelStatus` from [`protocol/schema/clpr_channel_status.proto`](../../schema/clpr_channel_status.proto). Import paths are relative to the root of the specification repository.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
