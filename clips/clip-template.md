---
clip: <number assigned by an Editor>
title: <short title>
authors: <names>
status: Draft
discussion: <issue URL>
base-release: <version this CLIP is written against, e.g. v0.2>
target-release: unscheduled       # or the version, once Scheduled
modules:                          # every Protocol module this CLIP changes
  - protocol/<module>.md
ledger-impact:                    # Ledger Specifications that must change with it
  - ledgers/<ledger>/<document>.md
requires: []                      # other CLIPs this one depends on
supersedes: []
superseded-by:
created: YYYY-MM-DD
---

# CLIP-NNNN: <title>

<!--
Fill in every section. Sections marked Optional may be removed. The process
is defined in CLIP-0001, Sections 6 and 7. Delete these comments before
submitting.
-->

## 1. Abstract

<!-- A short summary of the problem and the proposed change. -->

## 2. Problem

<!-- What is wrong, missing, or limiting in the current specification. Cite the
modules and sections of the base release. -->

## 3. Approaches considered

<!-- The range of possible approaches, briefly, and the drawbacks of each one
not chosen. End with the requirements an adequate solution must meet. -->

### Requirements

## 4. Proposed solution

<!-- The solution in full, showing how it meets each requirement in Section 3. -->

## 5. Specification changes

<!-- The changes to the specification text, organized by module. Integration
applies exactly these changes (CLIP-0001, Section 7.1). List Ledger
Specification changes under ledger-impact. -->

### protocol/<module>.md

## 6. Compatibility and migration

<!-- The effect on implementations, on Ledger Specifications, and on existing
channels, and how to move from the base release to the new version. -->

## 7. Security considerations

## 8. Implementation advice

<!-- Optional. Suggested schedule, reference implementations, or practical notes. -->

## 9. Open issues

<!-- Unresolved questions. Required while in Draft; resolved before Last Call. -->

## 10. References

<!-- Optional. -->
