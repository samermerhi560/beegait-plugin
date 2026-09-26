#!/bin/sh
# Beegait plugin hook launcher (card MV2-11, the 🔍 review's send-back; card MV2-13, the directory's scan):
# Claude Code runs a hook's command through `sh -c` on macOS / Linux and Git Bash on Windows, and an exit
# code other than 0 or 2 lets the tool call PROCEED — a hook whose interpreter is missing fails OPEN,
# silently. So the scripts are launched through this file: `python` first (a python.org install on
# Windows names only that), else `python3` (a stock Mac / Debian names only that); with neither, ONE loud
# stderr line and exit 1 — Claude Code shows it as a non-blocking error notice on every tool call, so the
# person learns at once that the belt is OFF instead of never. Stdin (the tool input JSON) passes through
# `exec` untouched. The plugin directory's scanner refuses a command assembled from a variable at run
# time, so the guard is chosen by NAME and every exec line is literal: the interpreter, then the script
# from ${CLAUDE_PLUGIN_ROOT} — the one variable the directory allows, exported by Claude Code to every
# hook process. Without it the belt is OFF and says so (exit 1 — never 2: a missing variable must not
# block the session).
[ -n "${CLAUDE_PLUGIN_ROOT}" ] || { echo "beegait hook: CLAUDE_PLUGIN_ROOT is unset — the belt is OFF ($1 did not run)" >&2; exit 1; }
case "$1" in
  no_force_push)
    command -v python  >/dev/null 2>&1 && exec python  "${CLAUDE_PLUGIN_ROOT}/hooks/no_force_push.py"
    command -v python3 >/dev/null 2>&1 && exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/no_force_push.py"
    ;;
  no_request_edit)
    command -v python  >/dev/null 2>&1 && exec python  "${CLAUDE_PLUGIN_ROOT}/hooks/no_request_edit.py"
    command -v python3 >/dev/null 2>&1 && exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/no_request_edit.py"
    ;;
  no_agent_done)
    command -v python  >/dev/null 2>&1 && exec python  "${CLAUDE_PLUGIN_ROOT}/hooks/no_agent_done.py"
    command -v python3 >/dev/null 2>&1 && exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/no_agent_done.py"
    ;;
  *)
    echo "beegait hook: unknown guard '$1' — the belt is OFF for this call" >&2
    exit 1
    ;;
esac
echo "beegait hook: no python on PATH — the belt is OFF ($1.py did not run); install Python 3.10+ or the Beegait Runner" >&2
exit 1
