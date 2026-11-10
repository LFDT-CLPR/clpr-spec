#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mechanical checks for the CLPR Specification repository.

Usage: python3 tools/spec_lint.py [repository root]

Prints one finding per line as `path:line: rule: message` and exits with
status 1 if there are findings, 0 otherwise. Uses the standard library only.

Rules:
  link        a relative link points to a missing file or heading anchor
  header      a Protocol module or Ledger Specification lacks its header,
              or a Protocol module lacks its History section
  blueprint   MUST appears in the Blueprint
  keyword     an RFC 2119 keyword appears in a non-normative document
  history     version, EAP, implementation-status or "not yet specified" wording
              appears in normative prose
  clips       clips/ holds a file other than CLIPs, the template and README
"""

import os
import re
import sys

SKIP_DIRS = {".git", ".idea", "node_modules", os.path.join("archive", "main"),
             os.path.join("archive", "eap-v0.2-source")}
NORMATIVE_DIRS = ("protocol", "ledgers", "blueprint")
NON_NORMATIVE = ("clpr-overview.md", os.path.join("protocol", "open-issues.md"))
KEYWORDS = re.compile(r"\b(MUST NOT|MUST|SHALL NOT|SHALL|SHOULD NOT|SHOULD|REQUIRED|RECOMMENDED|NOT RECOMMENDED|MAY|OPTIONAL)\b")
HISTORY = re.compile(r"\bv0\.\d|\bEAP\b|\bin this (version|revision)\b|\bnot yet (specified|defined|implemented|supported|produced|normative)\b|\bimplementations? (use|at)\b", re.IGNORECASE)
PROTOCOL_HEADER = re.compile(r"^> \*\*Category:\*\* Protocol · \*\*Version:\*\* v\d+\.\d+ · \*\*Last changed:\*\* v\d+\.\d+\s*$")
LEDGER_HEADER = re.compile(r"^> \*\*Category:\*\* Ledger Specification \([^)]+\) · \*\*Applies to:\*\* v\d+\.\d+ · \*\*Revision:\*\* \d+\s*$")
CLIP_FILE = re.compile(r"^clip-\d{4}\.md$")

findings = []


def report(path, line, rule, message):
    findings.append(f"{path}:{line}: {rule}: {message}")


def slug(text):
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # link text only
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def prose_lines(path):
    """Yield (line number, text) outside fenced code blocks."""
    in_code = False
    with open(path, encoding="utf-8") as f:
        for number, line in enumerate(f, 1):
            if line.lstrip().startswith("```"):
                in_code = not in_code
                continue
            if not in_code:
                yield number, line.rstrip("\n")


_anchor_cache = {}


def anchors(path):
    if path not in _anchor_cache:
        found, counts = set(), {}
        for _, line in prose_lines(path):
            m = re.match(r"^(#{1,6})\s+(.*)$", line)
            if m:
                s = slug(m.group(2))
                n = counts.get(s, 0)
                counts[s] = n + 1
                found.add(s if n == 0 else f"{s}-{n}")
        _anchor_cache[path] = found
    return _anchor_cache[path]


def markdown_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_DIRS and d not in SKIP_DIRS]
        for name in sorted(filenames):
            if name.endswith(".md"):
                yield os.path.normpath(os.path.join(rel_dir, name))


def strip_code_spans(line):
    return re.sub(r"`[^`]*`", "", line)


def check_links(root, rel):
    path = os.path.join(root, rel)
    for number, line in prose_lines(path):
        for m in re.finditer(r"\]\(([^)\s]+)\)", line):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target):
                continue
            file_part, _, fragment = target.partition("#")
            dest = os.path.normpath(os.path.join(os.path.dirname(path), file_part)) if file_part else path
            if not os.path.exists(dest):
                report(rel, number, "link", f"missing file: {target}")
            elif fragment and dest.endswith(".md") and fragment not in anchors(dest):
                report(rel, number, "link", f"missing anchor: {target}")


def check_headers(root, rel):
    lines = list(prose_lines(os.path.join(root, rel)))
    header = next((text for _, text in lines if text.startswith("> ")), "")
    top = rel.split(os.sep)[0]
    if top == "protocol" and rel != NON_NORMATIVE[1]:
        if not PROTOCOL_HEADER.match(header):
            report(rel, 1, "header", "missing or malformed Protocol module header")
        if not any(text == "## History" for _, text in lines):
            report(rel, 1, "header", "missing History section")
    elif top == "ledgers" and not LEDGER_HEADER.match(header):
        report(rel, 1, "header", "missing or malformed Ledger Specification header")


def check_wording(root, rel):
    top = rel.split(os.sep)[0]
    normative = top in NORMATIVE_DIRS and rel != NON_NORMATIVE[1]
    in_history = False
    for number, line in prose_lines(os.path.join(root, rel)):
        if line.startswith("## "):
            in_history = line == "## History"
        text = strip_code_spans(line)
        if rel in NON_NORMATIVE and KEYWORDS.search(text):
            report(rel, number, "keyword", f"RFC 2119 keyword in a non-normative document: {KEYWORDS.search(text).group(0)}")
        if top == "blueprint" and re.search(r"\bMUST\b", text):
            report(rel, number, "blueprint", "MUST in the Blueprint (use SHOULD or MAY)")
        if (normative or rel in NON_NORMATIVE) and not in_history and not line.startswith("> **Category:**"):
            m = HISTORY.search(text)
            if m:
                report(rel, number, "history", f"history or version wording in specification prose: '{m.group(0)}'")


def check_clips(root):
    clips = os.path.join(root, "clips")
    if not os.path.isdir(clips):
        return
    for name in sorted(os.listdir(clips)):
        if name.startswith("."):
            continue
        if not (CLIP_FILE.match(name) or name in ("clip-template.md", "README.md")):
            report(os.path.join("clips", name), 1, "clips", "unexpected file in clips/")


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
    for rel in markdown_files(root):
        check_links(root, rel)
        check_headers(root, rel)
        check_wording(root, rel)
    check_clips(root)
    for finding in findings:
        print(finding)
    print(f"spec_lint: {len(findings)} finding(s)", file=sys.stderr)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
