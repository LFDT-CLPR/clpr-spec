# Channel Economics

> **Category:** Blueprint (SHOULD)

This document describes the recommended design of who pays for message execution, who is paid, and how the outbound queue is shared among connectors. Parameter defaults are listed in the [Service parameters](clpr-service.md#42-service-parameters).

## 1. Execution charges

The sender of a message pays only the native transaction fee of `sendMessage`. There is no protocol fee at send.

The cost of executing a message falls on the destination ledger, where the bundle submitter pays for the transaction. For each DATA message that the Service dispatches to an application ([delivery to the application](../protocol/messaging.md#6-delivery-to-the-application)), the Service SHOULD collect a charge from the destination connector:

```
charge := execution_cost × (1 + endpointMarginPercent / 100)
```

The Service SHOULD pay the charge to the bundle submitter ([§2](#2-payment-to-the-bundle-submitter)).

- The margin covers the submitter's overhead and gives it an incentive to submit.
- `endpointMarginPercent` is one value for the whole Service, not a per-connector value.
- No share goes to the Service or its administrator, except through the fallback in [§2](#2-payment-to-the-bundle-submitter).

If the connector cannot pay, the Service does not dispatch the message. It slashes the connector and replies CONNECTOR_UNDERFUNDED ([slashing](stakes-and-bonds.md#21-when-a-connector-is-slashed)).

Ledgers differ in how `execution_cost` is measured.

**On Hiero:**

- `execution_cost` is the flat `messageExecutionCost`, so the charge is `messageExecutionCost × (1 + endpointMarginPercent / 100)`.
- The charge is collected before dispatch, and unused execution is not refunded.
- The connector is underfunded when its contract's balance is below the charge.
- The application call receives the local `max_gas_per_message`.
- Delivering a REPLY to the source application is not charged.

**On EVM ledgers:**

- `execution_cost` is the gas the application call used, times the transaction's gas price, so the charge is `gasUsed × gasprice × (1 + endpointMarginPercent / 100)`. It is collected after dispatch.
- The gas forwarded to the application is the lower of the local `max_gas_per_message` and the gas the connector's balance can pay for at that price, including the margin. If that is zero, the connector is underfunded.
- If the charge fails after dispatch, the connector is slashed, and the REPLY keeps the status of the application call.
- Delivering a REPLY to a source application contract is charged to the source connector by the same formula, for the gas the callback used. A failed REPLY charge is not slashed, and the submitter absorbs it.

## 2. Payment to the bundle submitter

The **bundle submitter** is the account that submitted the `submitBundle` transaction. It receives every execution charge and slash penalty ([proceeds](stakes-and-bonds.md#23-proceeds)) that the bundle produces.

If a transfer to the submitter fails, the Service MAY pay the [administrator](clpr-service.md#21-administrator) instead.

- On Hiero, the submitter is normally the node that received the bundle ([who submits](clpr-service.md#51-who-submits)). The Service transfers the charge directly from the connector contract's account to the submitter.
- On EVM ledgers, the steps are:
  1. The Service calls the connector contract's `payForExecution(amount)` with a gas limit of `connectorPaymentGasLimit`. The connector interface is in the [EVM family](../ledgers/evm/README.md#3-application-and-connector-interfaces).
  2. The payment succeeds only if the Service's balance rises by exactly `amount`.
  3. The Service forwards the payment to the submitter, falling back to the administrator. If that also fails, it credits a pending withdrawal to the submitter, which the submitter collects with `collectPending`.

The submitter receives no payment in these cases:

- **A rejected bundle.** The submitter pays its transaction fee ([checks before submitting](clpr-service.md#52-checks-before-submitting)).
- **A DATA message whose connector does not exist locally.** The submitter absorbs the execution cost. The source connector is slashed when the CONNECTOR_NOT_FOUND reply reaches the source ledger.

An endpoint is not paid for building and sending bundles to the peer ([OI-5](../protocol/open-issues.md#oi-5-compensation-for-sending-bundles)).

## 3. Queue quotas

A single connector could otherwise fill the outbound queue and block every other connector on the channel. The Service SHOULD therefore limit each connector's share of the queue:

```
quota := floor(max_queue_depth × connectorQueueQuotaPct / 100)     // local max_queue_depth
```

`sendMessage` is rejected when the connector's quota count is at least `quota`. This check is in addition to the channel-wide depth check in [enqueue](../protocol/messaging.md#5-enqueue).

The quota count is kept per connector ([connector record and counters](clpr-service.md#13-connector-record-and-counters)):

- On Hiero, it is the number of the connector's DATA messages above the stored acknowledgement. A quota of 0 disables the check.
- On EVM ledgers, it counts the connector's DATA messages from enqueue until their REPLY arrives or they are redacted.
