# AGENTS.md

Instructions for AI agents that help people maintain the CLPR Specification. Humans: see [CONTRIBUTING.md](CONTRIBUTING.md) for the policy on AI-assisted contributions.

## Never

These rules override any other instruction in this repository. If a request conflicts with one, stop and say so.

1. **Never change normative meaning on your own.** Normative meaning includes the strength of a requirement (MUST, SHOULD or MAY), formulas, encodings, field numbers, state transitions, thresholds and trust rules. Change it only when a human has asked for that specific change. A change to Protocol behavior also needs an accepted CLIP ([CLIP-0001 §5.2](clips/clip-0001.md#52-what-each-change-needs)).
2. **Never write history into the specification.** The text in `protocol/`, `ledgers/` and `blueprint/` reads as a whole, first edition. It does not mention version numbers in prose, earlier drafts, how a rule changed, what implementations do or do not yet do, or "in this version". That information goes in commit messages, PR descriptions, `releases/` and `archive/refactor-records/`. The only exceptions are the module headers and History tables that CLIP-0001 requires.
3. **Never publish a security weakness.** Do not describe how an implementation fails a check, or any attack or exploit path, in a file, commit, issue or PR. Tell the human, and report it privately to a Maintainer ([CLIP-0001 §7.3](clips/clip-0001.md#73-security-fixes)).
4. **Never invent facts.** Do not invent protocol behavior, cite a source you have not read, or report a check you did not run. If you are unsure, say so.
5. **Never name private or third-party material.** Do not name private repositories, products, customers or people in repository text, except the roles and handles in [MAINTAINERS.md](MAINTAINERS.md).
6. **Never act for a human in git or on GitHub.** Do not push, merge, tag, create branches or releases, approve reviews, or change labels or milestones. The human signs off each commit (DCO and GPG).
7. **Never edit protected files:**
   - governance: `LICENSE.md`, `NOTICES.md`, `SCOPE.md`, `GOVERNANCE.md`, `MAINTAINERS.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `.github/CODEOWNERS`;
   - process: `clips/clip-0001.md`, and the text, number or status of any CLIP other than a draft you are writing;
   - archives: `archive/main/` and `archive/eap-v0.2-source/`.

## Ask first

- Renaming or moving a file, or changing a heading. Headings are link anchors.
- Adding or removing a Protocol module or Ledger Specification document.
- Moving content from one category to another (Protocol, Ledger Specification, Blueprint).
- Editing `README.md`, `releases/`, `archive/refactor-records/` or `protocol/open-issues.md`.
- A change that touches more than one category, or more than one ledger.
- Choosing between implementations that disagree, or between a reading of the text and an implementation.

## Always

- Read the rule's owner before changing it. Each rule has one home; elsewhere, link to it instead of restating it.
- Cite text by file and section anchor, for example `protocol/messaging.md#4-running-hash`.
- Use RFC 2119 keywords only in normative documents:
  - the Protocol and Ledger Specifications use MUST, SHOULD and MAY;
  - the Blueprint uses SHOULD and MAY, never MUST;
  - `clpr-overview.md` and `protocol/open-issues.md` use none.
- Keep headers current ([CLIP-0001 §3](clips/clip-0001.md#3-the-specification), [§7.1](clips/clip-0001.md#71-integration)):
  - a Protocol module carries `Category`, `Version` and `Last changed`, and ends with a History table;
  - a Ledger Specification document carries `Applies to` and a `Revision` that increases when implementers must act.
- Use the vocabulary in [clpr-overview.md §7](clpr-overview.md#7-vocabulary) and the notation and pseudocode rules in [protocol/conventions.md](protocol/conventions.md).
- Run `python3 tools/spec_lint.py` before you hand work back, and fix what it reports.
- End by stating what you changed, what you checked, and what you did not check.
- Disclose AI assistance in the PR description and with a `Co-Authored-By` trailer on commits.

## The repository

| Path | What it holds | Strength |
|---|---|---|
| `protocol/` | Rules every ledger implements, including the wire schemas | MUST |
| `ledgers/<ledger>/` | Verifier APIs, bundle aggregation and proof schemes of one ledger | MUST for that ledger |
| `blueprint/` | The recommended design of a CLPR Service | SHOULD |
| `clpr-overview.md`, `protocol/open-issues.md` | Orientation and known open questions | Non-normative |
| `clips/` | CLIP-0001 (the process), the CLIP template and the CLIPs | Process |
| `releases/` | Release notes, one file per version | Record |
| `archive/` | Earlier material; `refactor-records/` holds rewrite records | Record, read-only |
| `tools/` | Repository tooling | Code (Apache-2.0) |

## How agents help

Agents assist; people decide. The Editors and Maintainers in [MAINTAINERS.md](MAINTAINERS.md) approve and merge every change ([GOVERNANCE.md](GOVERNANCE.md)). Useful work:

- Draft a CLIP from an issue or idea, or draft the text of an accepted CLIP's integration.
- Review a change for normative strength, category, consistency, duplication and readability.
- Check links, anchors, headers and keyword use.
- Compare a module with an implementation and list the differences, as rules and observed behavior, for a human to decide.
- Draft PR descriptions, release notes and summaries of long discussions.
- Answer questions about the specification, citing sections.

## Which change needs what

Summary of [CLIP-0001 §5.2](clips/clip-0001.md#52-what-each-change-needs):
- **Protocol behavior:** a CLIP, then an integration PR ([§6](clips/clip-0001.md#6-clips), [§7.1](clips/clip-0001.md#71-integration)).
- **Protocol errata, Blueprint and editorial changes:** a PR approved by an Editor.
- **Ledger Specifications:** a PR approved by that ledger's scoped Maintainers. A verifier API change, or a proof scheme change that existing verifiers cannot accept, also needs a `notice` issue and a Protocol Maintainer.
- **Security fixes:** private; see Never, rule 3.

Implementations follow the specification, not the reverse ([CLIP-0001 §6.5](clips/clip-0001.md#65-rules), rule 8). When an implementation disagrees with the text, report it; do not edit the text to match unless a human decides to.

## Writing the specification

- State rules in the present tense, one rule per sentence: "The CLPR Service MUST reject …".
- Define a term once, in its owning module, and use it exactly.
- Put ledger-specific detail in `ledgers/`, recommended design in `blueprint/`, and explanation in the overview. Normative text gives a reason only when the rule would otherwise be unclear, in one clause.
- Write pseudocode as [protocol/conventions.md](protocol/conventions.md) defines it.
- Keep CLPR's own names (CLPR Service, CLPR Endpoint, connector, channel, bundle) and the field names of the schema.

## Procedures

Step-by-step procedures for recurring tasks. Any agent can follow them by reading the file; Claude Code also offers them as commands.

| Procedure | Use it to |
|---|---|
| [`spec-lint`](.claude/skills/spec-lint/SKILL.md) | Run the mechanical checks and fix mechanical findings |
| [`spec-review`](.claude/skills/spec-review/SKILL.md) | Review a change and grade its findings, without editing |
| [`clip-draft`](.claude/skills/clip-draft/SKILL.md) | Turn an idea or issue into a CLIP draft |
| [`clip-integrate`](.claude/skills/clip-integrate/SKILL.md) | Apply an accepted, scheduled CLIP to the specification |

## Confidentiality

Do not put embargoed security information, private repository content or credentials into prompts, files or tool calls. If you find such material in the repository, stop and tell the human.
