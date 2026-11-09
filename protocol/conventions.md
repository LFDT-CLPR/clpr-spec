# Conventions

> **Category:** Protocol · **Version:** v0.2 · **Last changed:** v0.2

This module defines the notation used throughout the specification. It applies to the Protocol, the Ledger Specifications and the Blueprint.

## 1. Requirement keywords

**MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** follow [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). They have this meaning only when written in capitals.

| Document | Keywords used |
|---|---|
| Protocol and Ledger Specifications | MUST, SHOULD, MAY |
| Blueprint | SHOULD, MAY |
| Overview, open issues, notes marked non-normative | None |

## 2. Notation

| Notation | Meaning |
|---|---|
| `a ‖ b` | Concatenation of the byte strings `a` and `b`. |
| `SHA-256(x)`, `SHA-384(x)` | The SHA-256 and SHA-384 hash functions of FIPS 180-4, applied to the byte string `x`. |
| `keccak256(x)` | Keccak-256 with the original Keccak padding, as used by Ethereum. It is not FIPS 202 SHA3-256. |
| `H(x)` | A hash function, where the text names which one. |
| `len(x)` | The number of bytes in a byte string, or of elements in a list. |
| `x[i]` | Element or byte `i` of `x`. Indices start at 0 unless the text says otherwise. |
| `x[a:b]` | The half-open slice of `x`: bytes or elements `a` to `b − 1`, so `len(x[a:b]) = b − a`. `x[a:len(x)]` is the rest of `x` from `a`. This is the only slice notation. |
| `be(n, k)` | The `k`-byte big-endian encoding of the unsigned integer `n`. |
| `x.f` | Field `f` of the structure `x`. |
| `0x…` | A hexadecimal byte string or integer. |

## 3. Abstract data structures

The Protocol defines its data as **abstract data structures**: each structure has a name and a table of fields. For each field, the table gives its name, type, meaning and constraints. Structure names are written in PascalCase (`QueueMetadata`) and field names in snake_case (`next_message_id`). The order of fields in a table carries no meaning.

An abstract data structure does not define an encoding. Encodings are defined in one place each:

| What | Where encoded |
|---|---|
| Message payloads, ledger configuration, endpoint manifest and other data shared between ledgers | [`protocol/schema/`](schema/README.md) |
| Endpoint sync requests and responses | [`protocol/endpoint-sync/schema/`](endpoint-sync/schema/README.md) |
| Bundle wire layout, trust anchors and proofs | The proof scheme in the Ledger Specifications |
| Verifier call inputs and outputs | The destination ledger's verifier API |

Types:

| Type | Meaning |
|---|---|
| `bool` | True or false. |
| `uint8`, `uint32`, `uint64`, `uint96`, … | Unsigned integer of the given number of bits. |
| `string` | UTF-8 text. |
| `bytes` | Byte string of any length. Its content is opaque unless the text defines it. |
| `bytesN` (`bytes32`, …) | Byte string of exactly `N` bytes. |
| `timestamp` | A consensus time: seconds and nanoseconds since the Unix epoch. |
| `T[]` | Ordered list of values of type `T`. |
| `optional T` | A value of type `T`, or absent. The field's definition states whether an empty or zero value counts as absent. |
| Enumeration | A named set of values, written in capitals (`ACTIVE`, `DATA`). |
| Structure name | A nested structure. |

Interfaces, such as the [verifier interface](verifier-interface.md), are written as language-neutral function signatures over these types. Each ledger's Ledger Specifications bind them to the ledger's native constructs and keep their semantics.

**Interface signatures.** A signature is written `Name(a: T, …) → r: R`. Each parameter is given as `name: type`. `→` means "returns": it is followed by the result, or by a tuple `(r1, r2, …)` of several results, each named and, where the text gives one, typed.

**Strict decoding.** This rule applies to the structures encoded in [`protocol/schema/`](schema/README.md) and [`protocol/endpoint-sync/schema/`](endpoint-sync/schema/README.md): message payloads, the other data shared between ledgers, and endpoint sync messages. A receiver of such a structure MUST NOT silently ignore data it does not recognize. It MUST reject a structure that contains an unrecognized field, an unrecognized enumeration value or message type, or malformed content. Fields and values marked deprecated are recognized data and are handled as their definitions state. A reserved enumeration value is handled as the module that owns it defines (for example, [replies](messaging.md#7-replies)). The module that receives the structure defines what rejection affects.

A proof scheme defines its own decoding of bundles, trust anchors and proofs, including any of these structures that a proof contains. It states explicitly which fields and entries a verifier ignores.

## 4. Pseudocode

Algorithms are written in pseudocode. Pseudocode defines the result, not the implementation: an implementation MAY use any procedure that accepts the same inputs, produces the same outputs and rejects the same inputs.

| Construct | Meaning |
|---|---|
| `(a, b)` | A tuple: a fixed number of values, in order. |
| `[a, b]`, `[]` | A list of the given elements; the empty list. |
| `{a, b}` | A set of the given elements. |
| `Name { f = v, … }` | A structure of type `Name` with the given field values. |
| `empty` | The empty byte string or list. |
| `absent` | No value, for an `optional` field or result. |
| `x := e` | Assign the value of `e` to `x`. This is the only assignment form. |
| `(a, b) := e` | Assign the elements of the tuple `e` to `a` and `b`, in order. |
| `=`, `≠`, `<`, `≤`, `>`, `≥` | Comparison. `=` and `≠` compare byte strings, tuples and lists element by element, including their lengths. |
| `+`, `−`, `×`, `/`, `mod`, `a^b` | Arithmetic. `/` is exact division, `mod` the non-negative remainder, and `a^b` is `a` to the power `b`. |
| `floor(x)`, `ceil(x)`, `min(a, b)`, `max(a, b)` | Round down; round up; the smaller value; the larger value. |
| `x ∈ S`, `x ∉ S`, `S ∩ T`, `\|S\|` | Membership; non-membership; intersection; number of elements. They apply to sets and lists. |
| `and`, `or`, `not` | Boolean operators. |
| `append x to xs` | Add `x` to the end of the list `xs`. |
| `if c then … else …` | Conditional. `else if` chains conditions. |
| `for each x in xs` | Iterate over a list in order. |
| `for i from a to b` | Iterate over the integers `a` to `b`, inclusive. There is no iteration if `a > b`. |
| `function Name(args):` | Define the algorithm `Name` with the parameters `args`. Its body is the indented block that follows. `Name(args)` calls it. A result can be declared as in an [interface signature](#3-abstract-data-structures): `function Name(args) → r:`. |
| `return v` | End the algorithm with the result `v`. A tuple returns several values. |
| `decode T(x)` | Decode the bytes `x` as the structure `T`, in the encoding that [§3](#3-abstract-data-structures) assigns to `T`. A failure rejects. |
| `serialize(x)` | The bytes of the structure `x` in that encoding. |
| `reject "<reason>"` | End the algorithm with failure. The reason is informative; the error reported is ledger-specific. |
| `// …` | Comment. |

Indentation shows block structure: the lines indented under a `function`, `if`, `else` or `for` line form its block. Other operations are written as functions that the text defines, or in plain words. Arithmetic is exact. A decoding failure or an out-of-range access rejects, even where the pseudocode does not say so.

## 5. Identifiers

| Identifier | Form | Defined in |
|---|---|---|
| Chain id | CAIP-2 string | [Ledger configuration §1](ledger-configuration.md#1-ledger-identity) |
| Channel id | `bytes32`, identical on both ledgers | [Channel setup §1](channel-setup.md#1-channel-identity) |
| Connector id | `bytes32`, identical on both ledgers | [Connector setup §1](connector-setup.md#1-connector-identity) |
| Message id | `uint64`, per channel, starting at 1 | [Messaging §2](messaging.md#2-message-identifiers-and-queue) |
| Trust anchor id | `bytes`, defined by the proof scheme | [Verifier interface §1](verifier-interface.md#1-verifier-contracts-and-trust-anchors) |

A **chain id** is a [CAIP-2](https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-2.md) blockchain id, `namespace:reference`. Examples: `eip155:1`, `eip155:11155111`, `hiero:mainnet`.

A 32-byte id is compared as a byte string. It has no numeric value.

## History

| Version | Change |
|---|---|
| v0.2 | Established as the v0.2 baseline under CLIP-0001. No CLIPs integrated. |
