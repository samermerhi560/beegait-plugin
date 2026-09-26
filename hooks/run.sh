#!/bin/sh
# Beegait plugin hook launcher (card MV2-11, the 🔍 review's send-back): Claude Code runs a hook's
# command through `sh -c` on macOS / Linux and Git Bash on Windows, and an exit code other than 0 or 2
# lets the tool call PROCEED — a hook whose interpreter is missing fails OPEN, silently. So the scripts
# are launched through this file: `python` first (a python.org install on Windows names only that),
# else `python3` (a stock Mac / Debian names only that); with neither, ONE loud stderr line and exit 1 —
# Claude Code shows it as a non-blocking error notice on every tool call, so the person learns at once
# that the belt is OFF instead of never. Stdin (the tool input JSON) passes through `exec` untouched.
script="$1"
if command -v python >/dev/null 2>&1; then
  exec python "$script"
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$script"
fi
echo "beegait hook: no python on PATH — the belt is OFF ($(basename "$script") did not run); install Python 3.10+ or the Beegait Runner" >&2
exit 1
