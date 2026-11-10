# CLPR ADR Guide

This document governs Architecture Decision Records (ADRs) for the CLPR protocol specification: what
a committed ADR must look like, and the process for producing one. It is written for both human
stakeholders (implementers, domain experts, decision-makers) and AI agents assisting in ADR
development, and applies to every ADR in this directory.

## 1. Repository Convention

ADRs are named `YYYY-MM-DD-short-title.md`, dated so they sort chronologically. Only final-form
ADRs are committed. Working material used to produce an ADR — notes, drafts, ontology breakdowns —
may be committed on PR drafts, but are never merged into the main branch.

## 2. The ADR Final Form

A final ADR consists of an Abstract followed by five numbered sections and two optional appendices.

### 2.1 Abstract

Positioned at the top of the document, before Section 1. States the need for the ADR — the
problem(s) motivating it — briefly, then an enumeration led by "**Changes in this ADR:**". Each entry
is a single short sentence that could be a changelog top-line — a high-level fact a stakeholder would
recognize, not an implementation detail (no field names, signatures, or mechanism).

**Tone and style:** declarative, concise. Drafted last, after Section 3 is stable, so the enumeration
matches the finished content.

### 2.2 Section 1: Problem Description

Each discrete problem area the ADR addresses gets its own subsection, establishing the ADR's scope. A
problem statement identifies the current behavior, why it is inadequate, and the concrete consequence.

**Tone and style:** factual and direct. States what is wrong or missing. Does not discuss solutions.

### 2.3 Section 2: Options Considered and Non-Goals

Options Considered subsection presents the major alternative solutions that were considered and rejected, 
motivating the accepted solution.  This is not an exhaustive list or low level description of 
design decisions, but provides high level or fundamental architectural considerations. Written as prose,
one alternative-and-rejection per topic.

The Non-Goals subsection details considerations that are explicitly left out of the ADR as out of scope 
or in the domain of a different ADR. Written as a bulleted list, one non-goal per bullet — each is a
discrete, parallel exclusion, and should read as one at a glance, unlike Options Considered's connected
narrative.

**Tone and style:** comparative and rationale-bearing. The purpose of this section is to motivate the 
fundamental solution architecture in section 3.

### 2.4 Section 3: The Solution

The complete, accepted solution: new or changed data structures, new or changed methods, new or
changed actor behavior. This section is the specification itself. Organization is chosen per ADR to
suit the content — top-down (problem → actors/roles → methods → state changes), bottom-up (data
structures → methods that modify them → actors that invoke the methods), or another structure —
using subsections and subsubsections freely for complex content.

Every new or changed data structure is presented in the base spec's own notation for its kind. Two
kinds of data structure, presented differently:

- **On-the-wire** (anything traversing sync between endpoints) is **literal protobuf**:
  `message X { type field = N; }`. The protobuf is the wire format, and every implementation matches
  it exactly.
- **On-chain and local service state** (records held in contract or node state) is a **platform-neutral
  struct**: `field : type // comment`, no field numbers, no `message` wrapper. This is an example, not
  a literal mandate — each platform adapts the concrete representation (integer widths, storage layout)
  to its own native format when implemented.

**Tone and style:** declarative and complete, presenting the design as if for the first time, with no
history. No alternatives, no rationale, no comparison to prior behavior, no metaphor or analogy. Uses
RFC-2119 keywords (MUST, MUST NOT, SHOULD, MAY) consistent with the base spec's convention. Concise
and precise — exact field, method, and section references rather than paraphrase. Written for domain
experts; does not re-explain established terminology.

### 2.5 Section 4: Why This Is The Right Solution

Argues that Section 3 resolves Section 1's problems better than the specification's current behavior
does — a thematic, topic-level contrast with the existing specification, not a line-by-line diff.
This is where the comparison excluded from Section 3 belongs. Omit when Sections 1 and 3 already make
that case clear on their own.

**Tone and style:** comparative and argumentative. Before/after language belongs here.

### 2.6 Section 5: Testing

The tests needed to verify a correct implementation: happy-path capability tests, required failure
scenarios, and edge cases likely to be implemented incorrectly.

**Tone and style:** a plain enumerated list, brief per item.

### 2.7 Appendix A: Patching the Spec

Literal file-and-line-number references for every change this ADR requires in the existing
specification text. Optional, and not useful until the ADR's design is stable — attempting it earlier
is a distraction. Line references go stale as the spec text is edited elsewhere; they are accurate as
of the commit that used this ADR to patch the spec, or as of this ADR's own commit if that precedes
integration. No further staleness convention is maintained.

**Tone and style:** reference tables and lists, minimal prose.

### 2.8 Appendix B: Implementation Notes

Recommendations for turning the ADR into implementation work: breakdown into discrete epics or
issues, platform- or language-specific notes. Omit when the implementation path is straightforward
enough that no breakdown or platform-specific notes are needed.

**Tone and style:** advisory, plain.

## 3. The ADR Development Lifecycle

### 3.1 Scope the Problem

Establish what needs to change and the boundary of the effort before any solutioning begins.

### 3.2 Order and Work the Decisions

Work through the problem from the most fundamental, design-impacting decisions to the smallest,
settling each before moving to the next.

### 3.3 Maintain a Scratch Working Record

Capture decisions in a temporary document as they are made. It does not need to resemble an ADR — its
only requirements are that it is durable and diffable, so the design's evolution through discussion
can be tracked. Named `scratch-<topic>.md`, kept in this directory, never committed.

### 3.4 Build and Stabilize an Ontology

Once the solution has taken shape, produce a breakdown of the actors, their operations, the data
structures those operations affect, and the state changes each operation causes. Review the
breakdown, resolve any gaps or inconsistencies it surfaces, and rebuild. Repeat until the review finds
nothing further. Only a stable ontology is a sufficient basis for drafting.

### 3.5 Draft the Final ADR

Write the final form from the stabilized ontology and scratch notes, following the structure and
tone and style defined in §2.

### 3.6 Review and Commit

The draft is reviewed before commit. Once committed, scratch materials are discarded — they are not
part of the historical record.
