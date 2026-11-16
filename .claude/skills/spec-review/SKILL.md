---
name: spec-review
description: Independent review of a change to the CLPR Specification, graded by severity, with no edits. Checks normative strength, category placement, consistency with other modules, duplication, CLIP fidelity and whether the text reads as a whole. Use when asked to review a PR, branch, diff or set of files.
disable-model-invocation: true
---

# spec-review

Produces a review report for a human. It never edits the specification.

## Inputs

Ask for any that are missing:
- **The change:** a PR number, a branch compared with its base, or a list of files.
- **The intent:** the CLIP, issue or request the change implements, if any.

## Steps

1. **Collect the change.** Get the diff, for example `git diff <base>...<branch> -- protocol ledgers blueprint clpr-overview.md`. List each changed file and its category.
2. **Run the mechanical checks** with `python3 tools/spec_lint.py`, and include its findings in the report.
3. **Review independently.** Where the agent supports subagents, give each reviewer below the diff, the intent and the files to read, but not your own opinion of the change. Otherwise, do the passes yourself one at a time. Each pass uses [review-checklist.md](review-checklist.md):
   - **A. Normative strength and category.** Every keyword change, new or removed requirement, and the category each rule now sits in.
   - **B. Consistency.** Cross-module contradictions, duplicated statements of one rule, broken references and terminology drift.
   - **C. Fidelity.** Whether the change does what its CLIP or issue says, no more and no less. If an implementation is named as the reference, also compare with it.
   - **D. Editorial.** Readability, the writing rules in [AGENTS.md](../../../AGENTS.md#writing-the-specification), and the reads-as-a-whole rule.
4. **Verify every finding** against the text yourself before reporting it. Drop findings you cannot show with a quotation.
5. **Grade** each finding:

   | Grade | Meaning |
   |---|---|
   | S1 Critical | A normative rule removed, inverted or contradicted so that interoperability, safety or trust changes |
   | S2 Significant | A requirement's strength or scope changed, or an algorithm, encoding, field or state transition differs |
   | S3 Omission | A requirement, definition or reference missing or only partly present |
   | S4 Misleading | The facts are right, but the wording, framing, placement or category misleads |

6. **Write the report.** Give the counts by grade, then a table sorted from S1 down with these columns: id, grade, file and section, quotation, what is wrong, suggested fix. End with what the review did not cover.

## Limits

- Do not edit any file. The human decides which findings to act on.
- Security weaknesses found during review go to the human only, never into the report if it will be posted publicly.
