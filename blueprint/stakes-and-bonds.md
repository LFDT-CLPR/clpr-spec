# Stakes and Bonds

> **Category:** Blueprint (SHOULD)

This document describes the recommended design of the stake that a connector locks against misbehavior, the slashing of that stake, and the bond an endpoint posts at registration. Stakes and bonds are local to each ledger and never cross the wire. Parameter defaults are listed in the [Service parameters](clpr-service.md#42-service-parameters).

## 1. Connector stake

A connector posts its **locked stake** when it completes registration ([connector registration](../protocol/connector-setup.md#2-registration)). The Service holds the stake. Slashing reduces it ([§2](#2-slashing-and-bans)), and the Service returns the remainder when the connector is removed.

The stake is separate from the funds that pay for execution. Execution charges are paid from the connector contract's own balance ([execution charges](channel-economics.md#1-execution-charges)).

- **Minimum stake.** The Service SHOULD reject a registration whose stake is below `minLockedStake`.
- **Sizing.** The stake backs the connector's commitment that its counterpart on the peer ledger exists and can pay for execution ([connectors on both ledgers](../protocol/connector-setup.md#3-connectors-on-both-ledgers)). It SHOULD cover the losses the connector can cause to submitters on its ledger. How to calibrate it is an open issue ([OI-6](../protocol/open-issues.md#oi-6-calibration-of-the-connector-stake)).
- **Removal.** The connector admin removes the connector, and the Service returns the remaining stake to a recipient the admin names. Removal is refused while the connector has messages in flight ([removal](../protocol/connector-setup.md#5-removal)).

Ledger notes:

- On Hiero:
  - The stake is transferred from the registering account to a dedicated escrow account.
  - Removal requires the signatures of both the connector admin and the stake recipient.
  - There is no top-up.
- On EVM ledgers:
  - The stake is the value sent with `completeConnector` and is held by the Service contract.
  - Any account can add stake with `topUpConnectorStake`.

## 2. Slashing and bans

### 2.1 When a connector is slashed

Slashing happens on both ledgers, independently. Each ledger compensates the submitter of the bundle that exposed the failure on that ledger.

| Ledger | Event | Action |
|---|---|---|
| Destination | DATA message for a connector that does not exist locally | No slash, because there is no connector. The submitter absorbs the cost. The Service replies CONNECTOR_NOT_FOUND |
| Destination | DATA message whose connector cannot pay the execution charge | The local connector is slashed. The Service replies CONNECTOR_UNDERFUNDED and does not dispatch the message |
| Source | REPLY with status CONNECTOR_NOT_FOUND or CONNECTOR_UNDERFUNDED | The source connector that authorized the DATA message is slashed |
| Source | REPLY with status SUCCESS or APPLICATION_ERROR | No slash |

An underfunded connector is therefore slashed twice: once on the destination ledger and once on the source ledger when the REPLY arrives.

When a connector cannot pay depends on each ledger's charge model ([execution charges](channel-economics.md#1-execution-charges)).

### 2.2 Penalty

Each slash increments the connector's `slash_count`. Penalties escalate geometrically:

```
if slash_count + 1 ≥ slashBanThreshold then
    penalty := locked_stake                       // ban
    remove the connector
else
    penalty := min(slashBasePenalty × slashMultiplier^slash_count, locked_stake)
    locked_stake := locked_stake − penalty
    slash_count  := slash_count + 1
```

A **ban** removes the connector from the channel and forfeits all of its remaining stake. A banned connector can no longer authorize messages or pay for execution on that channel.

On EVM ledgers, a connector whose stake reaches zero is also banned.

### 2.3 Proceeds

The penalty is paid to the submitter of the bundle being processed. This is the same recipient as execution charges, with the same fallback ([payment flow](channel-economics.md#2-payment-to-the-bundle-submitter)).

On Hiero, the penalty is paid from the escrow account and capped at that account's balance.

## 3. Endpoint bond

On a ledger with endpoint registration ([registration and admission](clpr-service.md#32-registration-and-admission)), each registering endpoint posts a **bond**. The bond makes throwaway registrations costly. It is a signal of commitment, not a security deposit sized against attacks.

- The bond SHOULD be at least `minEndpointBond`.
- The Service is the bond's sole custodian. It SHOULD return the bond in full when the endpoint leaves, by any path: self-removal, administrator removal, or rejection of a pending registration.
- Endpoint bonds are never slashed. A misbehaving endpoint is removed, and its bond is refunded. Slashing applies only to connectors.
- The bond plays no part in bundle submission or in the payment of submitters.

On EVM ledgers, a returned bond is credited to the registrant's pending withdrawals, which the registrant collects with `collectPending`. Hiero has no endpoint bond, because its manifest is derived from the node roster ([roster-derived manifest](clpr-service.md#33-roster-derived-manifest)).
