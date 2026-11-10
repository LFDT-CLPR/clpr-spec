---
name: clip-draft
description: Draft a CLPR Improvement Proposal (CLIP) from an idea, issue or discussion, using clips/clip-template.md and the rules of CLIP-0001 §6. Use when someone wants to propose a change to Protocol behavior.
disable-model-invocation: true
---

# clip-draft

Writes a CLIP draft for a human author. The author owns the proposal; the agent drafts and asks.

## Inputs

Ask for any that are missing:
- the problem, and the issue or discussion it comes from;
- the author's name, or names, for `authors`;
- the base release, the final version the CLIP is written against (see `README.md`);
- any approach the author already prefers.

## Steps

1. **Check the vehicle.** Only Protocol behavior needs a CLIP ([CLIP-0001 §5.2](../../../clips/clip-0001.md#52-what-each-change-needs)). If the change is errata, editorial, Blueprint or Ledger Specification only, say so and stop.
2. **Read the base text.** Read every module the change could touch, the related open issues in [protocol/open-issues.md](../../../protocol/open-issues.md), and existing CLIPs in `clips/` that it may depend on, supersede or conflict with.
3. **Copy the template.** Copy [clips/clip-template.md](../../../clips/clip-template.md) to a working file outside `clips/`, for example `clip-draft-<short-title>.md` at the repository root. Do not add the file to `clips/` or choose a number; an Editor does both ([CLIP-0001 §6.4](../../../clips/clip-0001.md#64-lifecycle)).
4. **Fill the front matter** as [CLIP-0001 §6.3](../../../clips/clip-0001.md#63-front-matter) defines:
   - `status: Draft`, `target-release: unscheduled`, and `clip:` left for the Editor;
   - `modules`: every Protocol module the change edits;
   - `ledger-impact`: every Ledger Specification document that must change with it.
5. **Write the sections in order** ([CLIP-0001 §6.2](../../../clips/clip-0001.md#62-structure)):
   - Abstract.
   - Problem, citing the current text by section.
   - Approaches considered, each with its drawback, ending with the requirements.
   - Proposed solution.
   - Specification changes, organized by module. Write them as the exact text the modules will contain, reading as a whole, with no "changed from" wording.
   - Compatibility and migration, for implementations, Ledger Specifications and existing channels.
   - Security considerations, stated as properties and rules. Do not describe how an existing implementation can be attacked.
   - Open issues: every question you could not settle, for the author.
6. **Check it:**
   - every requirement in the Specification changes uses RFC 2119 keywords at the strength the author intends;
   - every module listed is changed, and no unlisted module is;
   - the change does not contradict a module it does not list.
7. **Hand it back.** Give the path of the draft and a list of the decisions the author must make. Do not commit unless asked.

## Limits

- Do not change specification files. A draft CLIP proposes text; integration applies it later (`clip-integrate`).
- Do not choose between options the author has not decided. Present them under Approaches considered or Open issues.
