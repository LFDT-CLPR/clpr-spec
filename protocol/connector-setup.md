# Connector Setup

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

A **connector** authorizes the messages applications send on a channel and pays for their execution on the destination ledger. A connector is registered separately on each ledger of a channel. This module defines how a connector is identified and registered, what is required for it to carry messages, how it authorizes outbound messages, and how it is removed. Stakes and slashing are defined in the [Blueprint](../blueprint/stakes-and-bonds.md).

## 1. Connector identity

A connector is identified by a 32-byte **connector id**:

```
connector_id := keccak256(channel_id ‖ public_key ‖ salt)
```

| Input | Meaning |
|---|---|
| `channel_id` | The [channel id](channel-setup.md#1-channel-identity) of the channel the connector serves. |
| `public_key` | The operator's public key, in the ledger's encoding. |
| `salt` | A 32-byte value, by default 32 zero bytes. Different salts let one operator register several connectors on the same channel. |

The derivation is deterministic, so an operator who registers with the same public key encoding and salt on both ledgers of a channel obtains the same connector id on both. Because the channel id is an input, the connector id is scoped to one channel, and registering it on one channel reserves nothing on any other.

On each ledger, a connector is registered on exactly one channel and is identified by (`channel_id`, `connector_id`). A channel MAY have many connectors, and one key MAY be used to register connectors on many channels.

Each connector record on a ledger holds at least:

| Field | Meaning |
|---|---|
| `connector_contract` | The address of the connector's contract on this ledger, which implements the ledger's connector interface (for example [EVM](../ledgers/evm/README.md#3-application-and-connector-interfaces) and [Hiero](../ledgers/hiero/README.md#6-application-and-connector-interfaces)). |
| `admin` | The authority that can remove the connector (Section 5). |

Other connector state, including its stake, is defined in the [Blueprint](../blueprint/stakes-and-bonds.md#1-connector-stake).

## 2. Registration

A connector is registered on each ledger in two phases, commit and reveal. The commit phase reserves the connector without revealing the connector id or the key. Registration is open to any caller.

**Commit.** The operator computes

```
ownership_commitment := keccak256(connector_id ‖ public_key)
```

and calls `registerConnector(ownership_commitment)`. The CLPR Service records the commitment as pending.

**Reveal.** The operator calls `completeConnector`:

| Input | Type | Meaning |
|---|---|---|
| `channel_id` | `bytes32` | The channel the connector serves. |
| `connector_id` | `bytes32` | The connector id. |
| `public_key` | `bytes` | The operator's public key on this ledger. |
| `salt` | `bytes32` | The salt used in the connector id. |
| `signature` | `bytes` | A signature proving control of `public_key`. |
| `connector_contract` | `bytes` | The address of the connector contract on this ledger. |
| `admin` | `bytes` | The connector's admin authority. |

The message signed and the signature scheme are ledger-specific, and a ledger MAY require additional inputs, such as the stake. They are defined in each ledger's README under *Registration signatures* (for example [Hiero](../ledgers/hiero/README.md#5-registration-signatures) and [EVM](../ledgers/evm/README.md#5-registration-signatures)).

The CLPR Service MUST reject the call if any of these holds:

| Condition |
|---|
| `connector_id` ≠ `keccak256(channel_id ‖ public_key ‖ salt)`. |
| `keccak256(connector_id ‖ public_key)` is not a pending commitment. |
| No channel with `channel_id` exists on this ledger. |
| A connector with `connector_id` is already registered on the channel. |
| `signature` does not prove control of `public_key`. |
| `connector_contract` is not a contract deployed on this ledger. |
| The stake requirement of the deployment is not met ([Blueprint](../blueprint/stakes-and-bonds.md#1-connector-stake)). |

Otherwise it creates the connector record and the commitment is no longer pending.

## 3. Connectors on both ledgers

A connector carries messages only if it is registered on both ledgers, on the same channel and with the same connector id. On the source ledger, it authorizes outbound messages (Section 4). On the destination ledger, it pays for executing the messages it receives ([Blueprint](../blueprint/channel-economics.md#1-execution-charges)).

A DATA message carries the source connector's id ([message types](messaging.md#1-message-types)). The destination CLPR Service resolves the connector directly by (`channel_id`, `connector_id`); it makes no authorization call. If no such connector is registered on the destination, the CLPR Service MUST NOT deliver the message to the application and MUST answer it with a REPLY of status CONNECTOR_NOT_FOUND ([replies](messaging.md#7-replies)). The consequences for the source connector are defined in the [Blueprint](../blueprint/stakes-and-bonds.md#2-slashing-and-bans).

## 4. Authorization of outbound messages

An application that sends a DATA message names the channel and the connector ([enqueue](messaging.md#5-enqueue)). The source CLPR Service calls the connector contract's authorization function:

| Input | Meaning |
|---|---|
| `channel_id` | The channel. |
| `target_application` | The address of the destination application on the peer ledger. |
| `sender` | The address of the caller that sent the message. |
| `message_data` | The application payload. |

It returns one boolean, `authorized`.

- The CLPR Service MUST reject the send unless the call returns true. A failed call is treated as a rejection.
- The connector MAY apply any authorization logic, for example allow-lists or payment requirements. Whether it can change its own state during the call is ledger-specific; on Hiero it cannot ([Hiero](../ledgers/hiero/README.md#6-application-and-connector-interfaces)).
- The call MUST NOT modify CLPR Service state.
- By returning true, the connector commits that its counterpart on the destination ledger can pay for executing the message, and that it can itself cover the cost of handling the reply. This commitment is the basis for slashing ([Blueprint](../blueprint/stakes-and-bonds.md#2-slashing-and-bans)).

The concrete function signature and call semantics are part of each ledger's connector interface (for example [EVM](../ledgers/evm/README.md#3-application-and-connector-interfaces) and [Hiero](../ledgers/hiero/README.md#6-application-and-connector-interfaces)). The other checks on a send, and their order, are defined in [enqueue](messaging.md#5-enqueue).

## 5. Removal

A connector's admin MAY remove it from its channel on that ledger. The CLPR Service MUST refuse while the connector has **in-flight messages**: DATA messages sent through it on this ledger whose reply has not been received.

Removal affects only the ledger on which it is done. After removal, sends that name the connector are rejected, and DATA messages that name it and arrive on this ledger are answered with CONNECTOR_NOT_FOUND (Section 3). The return of the connector's stake is defined in the [Blueprint](../blueprint/stakes-and-bonds.md#1-connector-stake).

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
