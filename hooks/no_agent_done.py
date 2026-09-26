"""Beegait plugin hook — PreToolUse on Edit | Write | MultiEdit: an agent never sets Done
(card MV2-11).

An implementation ends at To Test; the manager accepts from the board — the served
procedures say so in prose, the engine's done guard (`core/agentdone.py`) reverts it after
a run. This hook refuses the write BEFORE it lands on a Claude Code session.

What is refused (exit 2 + one stderr sentence): an Edit / Write / MultiEdit on a card file
(a `.md` under `cards/`, not under `cards/_files/`) whose RESULT puts a closed-stage status
on the card's `status:` line while the file's current status is not closed (a Done card's
other fields stay editable; a new card born Done is refused too).

The closed vocabulary: the engine's built-in synonyms (done · closed · complete · completed)
plus, when the hub's `maistro.yml` is found above the card and PyYAML imports, its
`lifecycle.synonyms.done` list and every `lifecycle.statuses` / `lifecycle.types.*.statuses`
entry whose stage is `done` / `closed` (name + aliases). A pack's own closed status that the
hub does not restate is NOT known here — the engine's guard behind this hook knows it.
Anything unexpected exits 0 — a broken hook must never block a session by accident.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

BUILTIN_CLOSED = {"done", "closed", "complete", "completed"}
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.S)
_STATUS_RE = re.compile(r"(?m)^[ \t]+status:[ \t]*(.*?)[ \t]*$")
MESSAGE = ("an agent never sets Done — {name}: status → {status!r} refused. End the card at "
           "To Test (the served procedure's last step); the manager accepts on the board.")


def is_card(path: str) -> bool:
    p = str(path or "").replace("\\", "/")
    return p.endswith(".md") and "/cards/" in p and "/cards/_files/" not in p


def status_of(text: str) -> str:
    """The card's `status:` (the first indented `status:` line of the frontmatter — the
    `card:` mapping's), unquoted, lower-cased; "" when absent."""
    m = _FM_RE.match(text or "")
    if not m:
        return ""
    s = _STATUS_RE.search(m.group(1))
    if not s:
        return ""
    return s.group(1).strip().strip("\"'").strip().lower()


def hub_of(path: Path) -> Path | None:
    for base in [path.parent, *path.parent.parents]:
        if (base / "maistro.yml").is_file():
            return base
    return None


def closed_names(card_path: Path) -> set:
    names = set(BUILTIN_CLOSED)
    hub = hub_of(card_path)
    if hub is None:
        return names
    try:
        import yaml
        data = yaml.safe_load((hub / "maistro.yml").read_text(encoding="utf-8")) or {}
    except Exception:  # broad-ok: no PyYAML / an unreadable file → the built-ins
        return names
    life = data.get("lifecycle") if isinstance(data, dict) else None
    if not isinstance(life, dict):
        return names
    syn = (life.get("synonyms") or {}).get("done") if isinstance(life.get("synonyms"), dict) else None
    for s in (syn or []):
        names.add(str(s).strip().lower())
    tables = [life.get("statuses") or []]
    for t in (life.get("types") or {}).values() if isinstance(life.get("types"), dict) else []:
        tables.append((t or {}).get("statuses") or [])
    for table in tables:
        for entry in table:
            if not isinstance(entry, dict):
                continue
            if str(entry.get("stage") or "").strip().lower() in ("done", "closed"):
                names.add(str(entry.get("name") or "").strip().lower())
                for a in entry.get("aliases") or []:
                    names.add(str(a).strip().lower())
    names.discard("")
    return names


def result_text(tool: str, tool_input: dict, text: str) -> str | None:
    """The file as the tool would leave it; None when the edit cannot apply (the tool
    fails on its own — nothing to judge)."""
    if tool == "Write":
        return str(tool_input.get("content") or "")
    edits = ([{"old_string": tool_input.get("old_string"), "new_string": tool_input.get("new_string"),
               "replace_all": tool_input.get("replace_all")}]
             if tool == "Edit" else list(tool_input.get("edits") or []))
    out = text
    for e in edits:
        old, new = str((e or {}).get("old_string") or ""), str((e or {}).get("new_string") or "")
        if not old or old not in out:
            return None
        out = out.replace(old, new) if (e or {}).get("replace_all") else out.replace(old, new, 1)
    return out


def refused(tool: str, tool_input: dict) -> str:
    """The refused status, "" when the write passes."""
    path = str(tool_input.get("file_path") or "")
    if not is_card(path):
        return ""
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError:
        text = ""                                    # a new card
    if tool != "Write" and not text:
        return ""
    after = result_text(tool, tool_input, text)
    if after is None:
        return ""
    closed = closed_names(p)
    before_s, after_s = status_of(text), status_of(after)
    if after_s in closed and before_s not in closed:
        return after_s
    return ""


def main() -> int:
    try:
        data = json.load(sys.stdin)
        tool = str(data.get("tool_name") or "")
        tool_input = data.get("tool_input") or {}
        if tool in ("Edit", "Write", "MultiEdit"):
            hit = refused(tool, tool_input)
            if hit:
                print(MESSAGE.format(name=Path(str(tool_input.get("file_path") or "")).name,
                                     status=hit), file=sys.stderr)
                return 2
        return 0
    except Exception:  # broad-ok: never block by accident
        return 0


if __name__ == "__main__":
    sys.exit(main())
