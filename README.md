# CLPR Specification

CLPR is a cross-ledger protocol for trusted messaging between independent blockchains and distributed ledgers that have smart contract and state proof capability. This repository holds the CLPR Specification. It is developed under the [Community Specification License 1.0](LICENSE.md) and governed by [CLIP-0001](clips/clip-0001.md).

## Versions

| Version | State | Where |
|---|---|---|
| **v0.2** | **Final** | Branch `release/v0.2`, tag `v0.2` |
| **v0.3** | **Open** | `main` |

Implementations target a final version, never `main` ([CLIP-0001 §6.5](clips/clip-0001.md#65-rules)). The changes in each version are listed in [`releases/`](releases/). See [v0.2](releases/v0.2.md).

## How to read the specification

Start with the [overview](clpr-overview.md). It describes the parts of CLPR and how they fit together, and defines its vocabulary. The normative text is divided into three categories ([CLIP-0001 §3](clips/clip-0001.md#3-the-specification)):

| Category | Level | Contents |
|---|---|---|
| [Protocol](protocol/) | MUST | Interoperability across all ledgers |
| [Ledger Specifications](ledgers/README.md) | MUST for one ledger | Verifier APIs, bundle aggregation and proof schemes |
| [Blueprint](blueprint/) | SHOULD | Recommended design of a CLPR deployment |

**Protocol modules**

| Module | Topic |
|---|---|
| [Conventions](protocol/conventions.md) | Notation, abstract data structures, pseudocode |
| [Ledger configuration](protocol/ledger-configuration.md) | Ledger identity, configuration, throttles, protocol version |
| [Endpoint manifest](protocol/endpoint-manifest.md) | CLPR Endpoints and how peers learn them |
| [Channel setup](protocol/channel-setup.md) | Registering a channel and binding its verifier |
| [Connector setup](protocol/connector-setup.md) | Registering connectors |
| [Messaging](protocol/messaging.md) | Messages, queues, running hash, replies, acknowledgement |
| [Bundle](protocol/bundle.md) | Abstract bundle content |
| [Verifier interface](protocol/verifier-interface.md) | Abstract, stateless verifier interface and trust anchors |
| [Channel state transitions](protocol/channel-state-transitions.md) | Bundle processing and channel status |
| [Endpoint sync](protocol/endpoint-sync/README.md) | The wire protocol between CLPR Endpoints |
| [Schema](protocol/schema/README.md) | Encodings of payloads and data structures |

[Open issues](protocol/open-issues.md) lists known problems in the Protocol that a future version may address. It is non-normative.

**Ledger Specifications:** [Hiero](ledgers/hiero/README.md), [Besu](ledgers/besu/README.md), and the [EVM family](ledgers/evm/README.md). See the [index](ledgers/README.md).

**Blueprint:** [CLPR Service](blueprint/clpr-service.md), [stakes and bonds](blueprint/stakes-and-bonds.md), [channel economics](blueprint/channel-economics.md).

## Changing the specification

Changes to Protocol behavior are made through CLPR Improvement Proposals ([CLIPs](clips/README.md)). Other changes are made by pull request. [CLIP-0001](clips/clip-0001.md) defines which change needs which approval. See [CONTRIBUTING.md](CONTRIBUTING.md), [GOVERNANCE.md](GOVERNANCE.md) and [MAINTAINERS.md](MAINTAINERS.md). AI agents follow [AGENTS.md](AGENTS.md), and `python3 tools/spec_lint.py` runs the repository's mechanical checks.

## Archive

[`archive/`](archive/) holds earlier material, kept for reference only:
- `archive/main/`: the specification and design records before CLIP-0001.
- `archive/eap-v0.2-source/`: the EAP v0.2 text that this specification was rewritten from.
- `archive/refactor-records/`: the [coverage matrix](archive/refactor-records/coverage-matrix.md) and the [implementation discrepancies](archive/refactor-records/implementation-discrepancies.md) of that rewrite.
