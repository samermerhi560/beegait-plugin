"""Beegait plugin hook — PreToolUse on Bash: never force-push (card MV2-11).

The account's Security rule (docs/rules/account.md, set by the account's managers): "never
push to the main branch outside the card's own start commit, and never force-push". The
served procedures say it in prose; this hook makes it deterministic on Claude Code.

Protocol: Claude Code writes the hook JSON on stdin ({tool_name, tool_input: {command}});
exit 2 + one stderr sentence REFUSES the tool call (the sentence reaches the model), exit 0
lets it through. Stdlib only, no network, no engine import, decides in milliseconds.
Anything unexpected exits 0 — a broken hook must never block a session by accident.

What counts as a force push: a `git … push …` segment of the command (split on && · || · ;
· | · newlines) carrying `--force`, `--force-with-lease[=…]`, `--force-if-includes`, a
short flag group with `f` (`-f`, `-fu`), or a `+refspec` (the force form of a refspec).
"""
from __future__ import annotations

import json
import re
import shlex
import sys

FORCE_FLAGS = ("--force", "--force-with-lease", "--force-if-includes")
MESSAGE = ("account rule: never force-push (docs/rules/account.md — set by the account's "
           "managers). Refused: {cmd}. Pull with --rebase and push again, or ask a manager.")
_SEGMENT_RE = re.compile(r"&&|\|\||;|\||\r?\n")


def is_force_push(command: str) -> bool:
    for seg in _SEGMENT_RE.split(command or ""):
        try:
            toks = shlex.split(seg, posix=True)
        except ValueError:
            toks = seg.split()
        if "git" not in toks:
            continue
        rest = toks[toks.index("git") + 1:]
        if "push" not in rest:
            continue
        for t in rest[rest.index("push") + 1:]:
            if t in FORCE_FLAGS or t.startswith("--force-with-lease=") \
                    or t.startswith("--force-if-includes="):
                return True
            if t.startswith("-") and not t.startswith("--") and "f" in t[1:]:
                return True                              # -f · -fu · -uf
            if t.startswith("+") and len(t) > 1:
                return True                              # +main — a forced refspec
    return False


def main() -> int:
    try:
        data = json.load(sys.stdin)
        if str(data.get("tool_name") or "") != "Bash":
            return 0
        cmd = str((data.get("tool_input") or {}).get("command") or "")
        if is_force_push(cmd):
            print(MESSAGE.format(cmd=" ".join(cmd.split())[:160]), file=sys.stderr)
            return 2
        return 0
    except Exception:  # broad-ok: never block by accident
        return 0


if __name__ == "__main__":
    sys.exit(main())
