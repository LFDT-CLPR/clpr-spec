---
name: spec-lint
description: Run the CLPR Specification's mechanical checks (links, anchors, module headers and History sections, RFC 2119 keyword placement, history wording in normative text, contents of clips/) and fix only mechanical findings. Use after any edit to the specification, before handing work back.
---

# spec-lint

Runs `tools/spec_lint.py` and resolves what it reports, without changing what the specification requires.

## Steps

1. From the repository root, run `python3 tools/spec_lint.py`. It prints `path:line: rule: message` and exits 1 if there are findings.
2. Fix each finding by its rule:

   | Rule | Fix |
   |---|---|
   | `link` | Point the link at the existing file or heading. Find the heading's anchor with GitHub's rule: lower case, punctuation removed, spaces become `-`, and a repeated heading gets `-1`, `-2`. Never rename a heading to make a link work; ask first. |
   | `header` | Restore the header line in the form the other files in the same directory use. Add a missing History table only if the module is new; ask the human what its row says. |
   | `blueprint` | Report it to the human. Turning a Blueprint MUST into SHOULD, or moving the rule into the Protocol, is a normative decision. |
   | `keyword` | Rephrase the non-normative sentence without the keyword, keeping its meaning. If it states a real requirement, report it: the requirement belongs in a module. |
   | `history` | Rewrite the sentence so that it states the rule as it is, with no version, draft, implementation or "not yet" wording. Move the historical fact to the PR description or `releases/` if it matters, and tell the human. |
   | `clips` | Report it. Only Editors add files to `clips/`. |

3. Rerun the script until it reports no findings, or until only findings that need a human decision remain.
4. Report the result: the findings fixed, the findings left for the human with the reason for each, and the final output of the script.

## Limits

- Fix mechanical problems only. If a fix would change what a sentence requires, permits or forbids, stop and ask.
- The script does not check meaning, consistency between modules, or whether a rule is correct. Use `spec-review` for that.
