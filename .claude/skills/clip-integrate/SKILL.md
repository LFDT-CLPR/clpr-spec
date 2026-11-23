---
name: clip-integrate
description: Integrate an accepted and scheduled CLIP into the CLPR Specification, as CLIP-0001 §7.1 defines - edit the listed modules and ledger documents, update headers, History tables and revisions, and prepare the integration PR for an Editor. Use only when a human asks to integrate a named CLIP.
disable-model-invocation: true
---

# clip-integrate

Applies one CLIP's specification changes to the text, in a single change set for one integration PR.

## Preconditions

Check all of these before editing, and stop if any fails:
- The CLIP is in `clips/` with `status: Scheduled` and a `target-release` that is the version open on `main` ([CLIP-0001 §6.4](../../../clips/clip-0001.md#64-lifecycle), [§7.2](../../../clips/clip-0001.md#72-releasing-a-version)).
- Every CLIP named under `requires` is already integrated.
- The CLIP's `base-release` matches the current text. If the modules have changed since, list the conflicts for the human ([CLIP-0001 §6.5](../../../clips/clip-0001.md#65-rules), rule 4).

## Steps

1. **Read the CLIP fully,** especially its sections 5 (Specification changes) and 6 (Compatibility and migration), and every module it lists.
2. **Edit each module** listed under `modules` so that it contains the text section 5 defines.
   - The result reads as a whole: integrate the new rules into the existing structure, with no "this CLIP changes" or version wording in the prose.
   - Keep each rule in one place, and update every link to a heading you had to change. Ask before renaming a heading.
   - If the CLIP text is ambiguous or conflicts with a module, stop and ask. Do not resolve it yourself.
3. **Update each changed Protocol module's header and History** ([CLIP-0001 §7.1](../../../clips/clip-0001.md#71-integration)):
   - set `Last changed` to the target version;
   - add a History row: the version, and the CLIP number with a one-line summary of the change.
4. **Apply the Ledger Specification changes** listed under `ledger-impact`. Increase a document's `Revision` when implementers must act on the change. Tell the human which ledgers' scoped Maintainers must review it.
5. **Update the release notes** for the target version in `releases/`, if the file exists: list the CLIP and the modules it changed. Ask before creating the file.
6. **Prepare the status change.** Draft the CLIP's front-matter edit to `status: Integrated`. An Editor decides when to apply it.
7. **Check the result:**
   - run `python3 tools/spec_lint.py` until it is clean;
   - search the tree for the terms, fields and functions the CLIP touches, to catch places that still state the old rule;
   - run `spec-review` on the change, or ask the human to.
8. **Hand it back.** List every file changed, each header and History update, the open questions, and the review findings, and draft the PR description, naming the CLIP and its milestone.

## Limits

- Integrate one CLIP per change set. A version never contains part of a CLIP ([CLIP-0001 §6.5](../../../clips/clip-0001.md#65-rules), rule 5).
- Do not merge, label, or change the milestone. Do not apply the status change without an Editor's decision.
