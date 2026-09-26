"""Beegait plugin hook — PreToolUse on Edit | Write | MultiEdit: never edit inside a card's
📝 Request section (card MV2-11).

The 📝 Request is the manager's verbatim words (MV2-REQUEST-FIDELITY): agents write BELOW it
(`## 🤖 Reading back`, the technical sections). The engine restores a rewritten block AFTER
an agent run and refuses it at the API; this hook refuses the edit BEFORE it lands on a
Claude Code session, where the Edit tool writes the file directly.

The block's law mirrors the engine's `core/request.py` (kept in sync by hand — stdlib
only here): from a line starting `## 📝 Request` to the `## 🤖 Reading back` heading, else
the next `## ` heading, else the end of the file. A card = a `.md` file under `cards/`
that is not under `cards/_files/`.

Refused (exit 2 + one stderr sentence): an Edit / MultiEdit whose `old_string` matches
anywhere inside the block; a Write whose content changes or drops the existing block.
Allowed: everything else — an edit below the block, a new card file, a non-card file.
Anything unexpected exits 0 — a broken hook must never block a session by accident.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUEST_RE = re.compile(r"(?m)^## 📝 Request\b[^\n]*$")
READBACK_RE = re.compile(r"(?m)^## 🤖 Reading back\s*$")
NEXT_H2_RE = re.compile(r"(?m)^## ")
MESSAGE = ("the 📝 Request section of {name} is the manager's verbatim words — an agent never "
           "edits inside it (write below it, under ## 🤖 Reading back or the technical "
           "sections); the engine refuses and restores it after a run anyway.")


def is_card(path: str) -> bool:
    p = str(path or "").replace("\\", "/")
    return p.endswith(".md") and "/cards/" in p and "/cards/_files/" not in p


def request_span(text: str) -> tuple[int, int] | None:
    m = REQUEST_RE.search(text or "")
    if not m:
        return None
    rb = READBACK_RE.search(text, m.end())
    if rb:
        return m.start(), rb.start()
    nxt = NEXT_H2_RE.search(text, m.end())
    return m.start(), (nxt.start() if nxt else len(text))


def edit_touches_block(text: str, old: str) -> bool:
    """True when ANY occurrence of `old` overlaps the 📝 block (a non-unique old_string
    fails the tool anyway; the conservative answer is the refusal)."""
    span = request_span(text)
    if span is None or not old:
        return False
    start, end = span
    pos = text.find(old)
    while pos != -1:
        if pos < end and pos + len(old) > start:
            return True
        pos = text.find(old, pos + 1)
    return False


def write_changes_block(text: str, content: str) -> bool:
    span = request_span(text)
    if span is None:
        return False
    before = text[span[0]:span[1]].rstrip("\n")
    new_span = request_span(content)
    if new_span is None:
        return True
    return content[new_span[0]:new_span[1]].rstrip("\n") != before


def refused(tool: str, tool_input: dict) -> bool:
    path = str(tool_input.get("file_path") or "")
    if not is_card(path):
        return False
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return False                     # a new card: nothing to protect yet
    if tool == "Edit":
        return edit_touches_block(text, str(tool_input.get("old_string") or ""))
    if tool == "MultiEdit":
        return any(edit_touches_block(text, str((e or {}).get("old_string") or ""))
                   for e in (tool_input.get("edits") or []))
    if tool == "Write":
        return write_changes_block(text, str(tool_input.get("content") or ""))
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
        tool = str(data.get("tool_name") or "")
        tool_input = data.get("tool_input") or {}
        if tool in ("Edit", "Write", "MultiEdit") and refused(tool, tool_input):
            name = Path(str(tool_input.get("file_path") or "")).name
            print(MESSAGE.format(name=name), file=sys.stderr)
            return 2
        return 0
    except Exception:  # broad-ok: never block by accident
        return 0


if __name__ == "__main__":
    sys.exit(main())
