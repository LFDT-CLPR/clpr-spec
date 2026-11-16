@AGENTS.md

## Claude Code

- The procedures in AGENTS.md are skills in `.claude/skills/`. Run them as `/spec-lint`, `/spec-review`, `/clip-draft` and `/clip-integrate`.
- Plan before any change to normative text. Use plan mode and get the human's approval of the plan first.
- For reviews, use fresh subagents. Give them the diff and the files to read, not your own conclusions, so the review is independent.
- Commits are the human's. If asked to prepare one, use `git commit -s` and end the message with a `Co-Authored-By:` trailer naming the model.
