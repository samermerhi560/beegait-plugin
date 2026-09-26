#!/bin/sh
# Beegait plugin eval (card MV2-12): every case starts from the SAME scratch hub, built into the run's
# workspace (the cwd) by ../_setup_hub.py — `python` first, else `python3` (the launcher idiom of hooks/run.sh).
here="$(cd "$(dirname "$0")" && pwd)"
setup="$here/../_setup_hub.py"
if command -v python >/dev/null 2>&1; then exec python "$setup" "$PWD"; fi
if command -v python3 >/dev/null 2>&1; then exec python3 "$setup" "$PWD"; fi
echo "beegait evals: no python on PATH — the scratch hub was not built (see plugins/beegait/evals/README.md)" >&2
exit 1
