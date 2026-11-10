# CLPR Overview

> **Non-normative.**

## 1. Purpose

CLPR, the Cross Ledger Protocol, passes messages between independent ledgers. Messages are delivered asynchronously and in order. A message carries arbitrary bytes, such as a contract call, an asset transfer or oracle data.

CLPR adds no intermediary network, bridge validator set or token. Each ledger verifies the other ledger's state proofs directly, so users trust only the two ledgers involved and the verifier that checks the proofs ([§4](#4-trust-model)). Incentives and penalties are paid in each ledger's native token, through connectors.

## 2. Major parts

| Part | What it is | Defined in |
|---|---|---|
| **Ledger** | A distributed ledger with smart contracts and state proofs. It runs at least one CLPR Service (exactly one on Hiero). | [Ledgers](ledgers/README.md) |
| **CLPR Service** | The component that implements CLPR on a ledger and holds its CLPR state: a native service on Hiero, a smart contract on EVM ledgers. | [CLPR Service](blueprint/clpr-service.md) |
| **Channel** | A connection between the CLPR Services of two ledgers, with the same id on both. Each side has an outbound queue and a verifier contract. Several channels can connect the same ledgers. | [Channel setup](protocol/channel-setup.md) |
| **Verifier contract** | A stateless contract, fixed when a channel is opened, that checks the peer ledger's proofs. | [Verifier interface](protocol/verifier-interface.md) |
| **Message** | One unit of communication on a channel: application data, a reply, or a control message. | [Messaging](protocol/messaging.md) |
| **Bundle** | The proven state of one side of a channel, usually with a contiguous run of messages from its outbound queue. | [Bundle](protocol/bundle.md) |
| **CLPR Endpoint** | A node that exchanges bundles with endpoints of the peer ledger and submits received bundles to its own ledger. | [Endpoint sync](protocol/endpoint-sync/README.md) |
| **Connector** | An economic actor on both ledgers of a channel. It authorizes messages on the source ledger and pays for their execution on the destination. Its stake can be slashed. | [Connector setup](protocol/connector-setup.md) |
| **Application** | A contract that sends and receives messages through the CLPR Service. | [Messaging §6](protocol/messaging.md#6-delivery-to-the-application) |

Each ledger publishes a **ledger configuration** (chain id, CLPR Service address, protocol version and throttles) and an **endpoint manifest** listing its CLPR Endpoints. Peers learn both through proofs, when a channel is opened and later in bundles. Endpoints communicate over gRPC; shared data is encoded in protobuf.

The parts form four layers: **network** (ledgers, CLPR Services, channels, verifier contracts, endpoints), **messaging** (messages, running hash, bundles), **payment and routing** (connectors) and **application**.

## 3. Message flow

A message from an application on ledger A to an application on ledger B:

1. The application on A calls the CLPR Service with the channel, the connector, the target application and the data.
2. The Service asks the connector to authorize the message; by authorizing, the connector commits to pay for its execution on B. The Service then appends a DATA message to the channel's outbound queue, gives it the next message id, and extends the queue's running hash.
3. A CLPR Endpoint of either ledger opens an endpoint sync session with an endpoint of the other. Each side tells the other the last message it has received, and receives a bundle of the messages after it.
4. An endpoint of B submits the bundle to B in an ordinary transaction.
5. B's CLPR Service passes the bundle and the channel's stored trust anchor to the channel's verifier contract, which checks the proof and returns the messages and the sender's queue metadata. The Service checks the message ids and the running hash itself.
6. For each DATA message, the Service checks that the connector exists on B and can pay. It calls the target application with a gas limit, charges the connector for the execution plus a margin, paid to the bundle submitter, and appends a REPLY to its own outbound queue.
7. A later sync carries the REPLY to A, and A's Service delivers it to the sending application. Some ledgers also charge the connector on A for that delivery ([Channel economics §1](blueprint/channel-economics.md#1-execution-charges)). The queue metadata in each bundle also acknowledges the messages its sender has received.

Every DATA message receives exactly one REPLY, in the order of the original messages. If the connector on B is missing or cannot pay, B replies with a failure instead of calling the application, and the connector's stake is slashed. Repeated failures lead to a ban from the channel ([Stakes and bonds §2](blueprint/stakes-and-bonds.md#2-slashing-and-bans)).

CONTROL messages travel in the same queues and carry configuration updates to the peer.

## 4. Trust model

An application that sends a message through CLPR trusts:

1. its own ledger's consensus;
2. its ledger's CLPR Service;
3. the channel's verifier contract, to accept only proofs of state the peer ledger committed;
4. the peer ledger's consensus and CLPR Service;
5. the remote application.

**Channels are permissionless.** Anyone can open a channel with any verifier contract. A channel is only as trustworthy as its verifier, and its existence does not show that its peer is the intended ledger, because chain ids are self-asserted. Applications therefore check a channel, its verifier and the finality it accepts before using it. The CLPR Service's own checks of message ids, running hash and reply order catch verifier bugs, not a compromised verifier.

**Connectors** cannot forge or alter messages. A connector can refuse to pay, which makes messages fail on the destination; its stake is slashed for that.

**CLPR Endpoints** cannot forge messages either, because every bundle is proven. Availability needs at least one honest endpoint on each side; without one, messages stall.

**No confidentiality.** CLPR provides integrity and authenticity. Payloads are stored in plaintext on both ledgers.

Recommendations for applications and deployments are in [CLPR Service §6](blueprint/clpr-service.md#6-security-considerations).

## 5. Roles

| Role | Does | Trust duty | Economic participation |
|---|---|---|---|
| **End user** | Uses applications built on CLPR | Vets the application | Bears application-level risk |
| **Application developer** | Deploys the application on both ledgers; chooses channels and connectors; handles replies | Vets channels and connectors | Pays connectors, under the connector's own terms |
| **Connector operator** | Registers and funds a connector on both ledgers of a channel; often opens the channel | Vets the verifier contract before staking on the channel | Funds execution; posts a slashable stake |
| **Verifier developer** | Publishes verifier contracts for a proof scheme; has no on-ledger identity | Correctness of the verification | None in the protocol |
| **Endpoint operator** | Runs CLPR Endpoints, which sync with peers and submit bundles | Serves all channels of its ledger | Pays transaction fees; earns the margin on executed messages |
| **CLPR Service administrator** | Configures the CLPR Service, admits endpoints where admission is curated, closes channels | Acts when a channel is compromised | None |

On Hiero, every consensus node is a CLPR Endpoint. On EVM ledgers, endpoints register and are admitted by the administrator. Endpoints are neither bonded nor slashed. The administrator cannot open channels or register connectors. Charges and penalties go to the bundle submitter ([Channel economics §2](blueprint/channel-economics.md#2-payment-to-the-bundle-submitter)).

Each role vets those it depends on, in proportion to the value it puts at risk. To open a route, a verifier developer publishes a verifier; a connector operator vets it, opens the channel and registers a connector on both ledgers; an application developer vets the channel and connector. To withdraw, a connector operator stops authorizing messages, waits until its messages in flight are answered, and removes the connector on both ledgers ([Connector setup §5](protocol/connector-setup.md#5-removal)).

Adding a ledger needs no change to the Protocol or to other ledgers: its contributors write its Ledger Specifications, deploy a CLPR Service, and publish verifier contracts for its proof schemes.

## 6. How the specification is organized

The normative content is in three categories, defined in [CLIP-0001 §3](clips/clip-0001.md#3-the-specification): the **Protocol**, required of every implementation; the **Ledger Specifications**, required of anyone interoperating with that ledger; and the **Blueprint**, recommended for individual deployments.

| Topic | Where |
|---|---|
| Notation, types, identifiers | [protocol/conventions.md](protocol/conventions.md) |
| Ledger identity, configuration, throttles | [protocol/ledger-configuration.md](protocol/ledger-configuration.md) |
| Endpoint manifest | [protocol/endpoint-manifest.md](protocol/endpoint-manifest.md) |
| Opening a channel | [protocol/channel-setup.md](protocol/channel-setup.md) |
| Connectors | [protocol/connector-setup.md](protocol/connector-setup.md) |
| Messages, running hash, replies, acknowledgements | [protocol/messaging.md](protocol/messaging.md) |
| Bundle content | [protocol/bundle.md](protocol/bundle.md) |
| Verifier contracts and trust anchors | [protocol/verifier-interface.md](protocol/verifier-interface.md) |
| Channel status and bundle processing | [protocol/channel-state-transitions.md](protocol/channel-state-transitions.md) |
| Communication between endpoints | [protocol/endpoint-sync/](protocol/endpoint-sync/README.md) |
| Encodings of shared data | [protocol/schema/](protocol/schema/README.md) |
| Known open design questions | [protocol/open-issues.md](protocol/open-issues.md) |
| Ledgers, verifier APIs and proof schemes | [ledgers/](ledgers/README.md) |
| CLPR Service design and administration | [blueprint/clpr-service.md](blueprint/clpr-service.md) |
| Connector stakes and slashing | [blueprint/stakes-and-bonds.md](blueprint/stakes-and-bonds.md) |
| Execution charges and queue quotas | [blueprint/channel-economics.md](blueprint/channel-economics.md) |
| Versions and how the specification changes | [clips/clip-0001.md](clips/clip-0001.md) |
| Design rationale of v0.2 (design document and ADRs of the EAP v0.2 text) | [archive/eap-v0.2-source/](archive/eap-v0.2-source/README.md) |

## 7. Vocabulary

Terms other than the [major parts](#2-major-parts):

| Term | Definition | Defined in |
|---|---|---|
| Source ledger, destination ledger | The ledger a message is sent from, and the ledger it is sent to. | — |
| Peer ledger | The other ledger of a channel. | — |
| State proof | A proof that data is part of a ledger's committed state. | — |
| Chain id | The CAIP-2 identifier a ledger claims for itself. | [Ledger configuration §1](protocol/ledger-configuration.md#1-ledger-identity) |
| Ledger configuration | The data a ledger publishes about itself to peers. | [Ledger configuration §2](protocol/ledger-configuration.md#2-ledger-configuration) |
| Throttles | Capacity limits a ledger publishes in its configuration. | [Ledger configuration §3](protocol/ledger-configuration.md#3-throttles) |
| Endpoint manifest | The proven list of a ledger's CLPR Endpoints. | [Endpoint manifest §2](protocol/endpoint-manifest.md#2-endpoint-manifest) |
| Channel id | The 32-byte id of a channel, the same on both ledgers. | [Channel setup §1](protocol/channel-setup.md#1-channel-identity) |
| Channel context | The constant channel data passed to every verifier call. | [Channel setup §3](protocol/channel-setup.md#3-channel-context) |
| Channel status | PENDING, ACTIVE, PAUSED, CLOSING, DRAINED or CLOSED. | [Channel state transitions §1](protocol/channel-state-transitions.md#1-channel-status) |
| Message type | DATA, REPLY, CONTROL or REDACTED. | [Messaging §1](protocol/messaging.md#1-message-types) |
| Message id | The position of a message in its channel's outbound queue. | [Messaging §2](protocol/messaging.md#2-message-identifiers-and-queue) |
| Running hash | A hash chain over a queue's messages, which the receiver recomputes. | [Messaging §4](protocol/messaging.md#4-running-hash) |
| Reply | The REPLY message that reports the outcome of a DATA message. | [Messaging §7](protocol/messaging.md#7-replies) |
| Acknowledgement | A ledger's proven statement that it received messages; transport-level, unlike a reply. | [Messaging §9](protocol/messaging.md#9-acknowledgement) |
| Queue metadata | The sender's proven queue position, carried in every bundle. | [Bundle §2](protocol/bundle.md#2-queue-metadata) |
| Partial bundle | A bundle that ends before the sender's last queued message. | [Bundle §3](protocol/bundle.md#3-partial-bundles) |
| Trust anchor | The data, stored with the channel, against which the verifier checks proofs. | [Verifier interface §1](protocol/verifier-interface.md#1-verifier-contracts-and-trust-anchors) |
| Endpoint sync | The protocol CLPR Endpoints use to exchange bundles. | [Endpoint sync §1](protocol/endpoint-sync/README.md#1-purpose-and-roles) |
| Verifier API | A ledger's concrete binding of the verifier interface. | [Ledgers](ledgers/README.md) |
| Proof scheme | What is proven about bundle content, how, and how it is verified. | [Ledgers](ledgers/README.md) |
| Bundle aggregation | How an endpoint gathers bundle content from its ledger's state. | [Ledgers](ledgers/README.md) |
| Execution charge, margin | What a connector pays for executing a message, and the share paid on top to the bundle submitter. | [Channel economics §1](blueprint/channel-economics.md#1-execution-charges) |
| Stake, slashing | A connector's locked funds, and their forfeiture for failed messages. | [Stakes and bonds](blueprint/stakes-and-bonds.md) |

## 8. Application patterns

Applications are asynchronous: a send returns before the destination executes, and the outcome arrives later as a reply. When several channels connect the same ledgers, for example with verifiers that accept different finality, the application chooses one at send time. Lower finality gives lower latency and a risk of reorganization. The specification recommends final or safe state; a channel whose verifier accepts anything earlier is used at its users' own risk ([§4](#4-trust-model), [proof requirements](protocol/bundle.md#4-proof-requirements)).

Patterns built on CLPR messages include remote contract calls through proxy contracts; escrow, mint, then burn; and two-phase commit across ledgers.
