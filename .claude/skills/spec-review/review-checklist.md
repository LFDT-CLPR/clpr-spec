# Review checklist

## A. Normative strength and category

- Every added, removed or changed MUST, SHOULD or MAY is listed, with the request that asked for it. An unrequested change of strength is at least S2.
- A Protocol behavior change has an accepted CLIP behind it ([CLIP-0001 §5.2](../../../clips/clip-0001.md#52-what-each-change-needs)).
- Each rule sits in the right category:
  - **Protocol:** what every ledger must do to interoperate.
  - **Ledger Specification:** what one ledger's verifier API, bundle aggregation or proof scheme requires.
  - **Blueprint:** a recommended design, with no MUST.
- A rule moved into the Blueprint loses its force. Flag it unless the request said so.
- Non-normative documents (`clpr-overview.md`, `protocol/open-issues.md`) contain no keywords and no requirements.

## B. Consistency

- The rule is stated once, in its owning module. Other places link to it.
- No other module, ledger document or Blueprint section now contradicts the change. Search for the field, term or function name across the tree.
- Pseudocode and prose agree, and the pseudocode follows [protocol/conventions.md](../../../protocol/conventions.md).
- Schema changes in `protocol/schema/` or `protocol/endpoint-sync/schema/` match the prose: field numbers, types and deprecation marks.
- Terms are used as [clpr-overview.md §7](../../../clpr-overview.md#7-vocabulary) defines them.
- Every changed heading still matches the links to it (`tools/spec_lint.py` checks this).

## C. Fidelity

- Every module the CLIP lists under `modules` and `ledger-impact` is changed, and nothing else.
- Each changed Protocol module has its `Last changed` updated and a History row naming the CLIP ([CLIP-0001 §7.1](../../../clips/clip-0001.md#71-integration)).
- Each Ledger Specification document that changed in a way implementers must act on has its `Revision` increased.
- `releases/` reflects the change when the version's release notes exist.

## D. Editorial and reads as a whole

- No version numbers, earlier drafts, "now", "no longer", "not yet specified", or implementation status appear in `protocol/`, `ledgers/` or `blueprint/` prose.
- Rules are stated in the present tense, one per sentence, with defined terms.
- Explanation belongs in the overview or the CLIP, not in normative text, unless one clause is needed for clarity.
- No security weakness, private name or unverifiable claim appears.
