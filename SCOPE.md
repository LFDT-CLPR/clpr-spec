# Scope

The scope of this Working Group is the **CLPR Specification**: a protocol for trusted messaging between independent blockchains and distributed ledgers that have smart contract and state proof capability.

The Specification consists of:

1. **Protocol:** the requirements that every CLPR implementation, on every ledger, must meet to interoperate. This includes the abstract data structures, the state transitions of channels and messages, the abstract bundle content and verifier interface, and the endpoint sync wire protocol between CLPR Endpoints.
2. **Ledger Specifications:** the requirements for interoperating with a particular ledger or family of ledgers. This includes verifier APIs, bundle aggregation, and proof schemes: how bundle content is gathered from a ledger, proven, encoded, and verified on another ledger.
3. **Blueprint:** recommended designs for building a CLPR deployment, such as the design of the CLPR Service and its internal state, stakes and bonds, and channel economics.

These categories are defined in [CLIP-0001](clips/clip-0001.md), Section 3. The Specification also includes the CLPR Improvement Proposals (CLIPs) and the process documents that govern its development.

Any changes of Scope are not retroactive.
