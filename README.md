# beegait — the Claude Code plugin

The ten Beegait procedures as generic skills (`/beegait:progress`, `/beegait:implement-ai-card <KEY>` …)
plus the Claude-side belt: three deterministic hooks that refuse what a tired session forgets.

## What it is — and what it is not

The plugin IS the belt (the three hooks) and the funnel (one install, the ten commands on every project
of the machine). It is NOT the product: the engine serves every procedure (`maistro playbook <role>`,
the account's rules and the pack's guidance folded in) and the Beegait board (app.beegait.ai) is where
a manager writes the request, accepts the card and dispatches a run to a runner — the skills alone plan
nothing and decide nothing.

## Install — three lines

1. **In a Beegait project** — nothing: the per-project stubs travel with the clone (`maistro clone <hub-git-url>`).
2. **Claude Code** — `/plugin install beegait@claude-community` (the Claude plugin directory, listed
   since 2026-09-29; Claude Code's `claude-community` copy of it is refreshed by Anthropic in batches — until
   it carries Beegait, install straight from this mirror: `/plugin marketplace add samermerhi560/beegait-plugin`
   then `/plugin install beegait@beegait`).
3. **Any agent** — `npx skills add https://skills.sh/p/17gXDTH7ymcrvLMl -a claude-code -a codex -a cursor` (the
   skills.sh pack, read from this mirror's `main`; `npx skills add samermerhi560/beegait-plugin` is the same ten).

Every implement runs on your own machine through the Beegait Runner — download it at https://app.beegait.ai
(the trial's first step). The full page: [`docs/install-skills.md`](../../docs/install-skills.md).

The plugin needs the engine on PATH, 0.2.154 or newer (the door taught `playbook` at 0.2.149, the funnel
line at 0.2.154): the Beegait Runner installs it and keeps it current; the pip package lands on PyPI as
`beegait-engine` with the first public release (until then the two names on PyPI are placeholders) and a Python 3.10+ on PATH as `python` or `python3` for the hooks
(`hooks/run.sh` picks one; with neither, every tool call shows one notice that the belt is OFF — Claude
Code lets a tool call proceed on any hook exit but 2, so the launcher says it loudly rather than never).
Open a Beegait project folder
(a folder holding `maistro.yml`, or any folder under it) and invoke a skill: the engine resolves the
project from the working directory and serves the procedure. Outside a project folder the skill
answers `no Beegait project here`, lists the projects of this machine and says how to get one
(`maistro clone <hub-git-url>`).

## Skills

`progress` · `checkpoint` · `build-ai-card` · `implement-ai-card` · `build-functional-card` ·
`ground-card` · `release-notes` · `kb-curate` · `user-guide` · `review-card` — each SKILL.md injects
`maistro playbook <role>` at invocation, so the procedure is always the current engine's. The
per-project stubs a hub carries (`.claude/skills/<role>-<project>`, emitted by `maistro agent
install`) do the same with `--project <id>`; they travel with the clone at zero install. This plugin
is the belt (the hooks) and the funnel (one install, every project of the machine).

## What the plugin runs, sends and fetches

It runs two things, both on your machine: `maistro playbook <role>` (the Beegait engine's command-line
tool, installed separately) when a skill is invoked, and the three hook scripts below (standard-library
Python, reading the tool input on stdin). It sends nothing anywhere, fetches nothing, opens no network
connection, reads no credential and changes no permission setting; the engine it calls talks to the
Beegait cloud only when this machine's runner is paired, on the engine's own terms. The hooks are launched
by name through `hooks/run.sh`, whose exec lines are literal paths from `${CLAUDE_PLUGIN_ROOT}`.

## Hooks (`hooks/hooks.json`, `PreToolUse`)

| Script | Matcher | Refuses (exit 2) |
|---|---|---|
| `no_force_push.py` | `Bash` | `git push` with `--force`, `--force-with-lease`, `--force-if-includes`, `-f` or a `+refspec` — the account's Security rule |
| `no_request_edit.py` | `Edit\|Write\|MultiEdit` | an edit whose `old_string` lies inside a card's `## 📝 Request` section, or a Write that changes it — the manager's verbatim words |
| `no_agent_done.py` | `Edit\|Write\|MultiEdit` | a write that puts a closed-stage status (`Done`, the hub's `lifecycle` synonyms and closed statuses) on a card — the manager accepts on the board |

Each script reads the tool input on stdin, decides in milliseconds, never touches the network, and
exits 0 on anything unexpected — a broken hook must never block a session by accident. Claude Code runs
the command through `sh -c` on macOS / Linux and Git Bash on Windows (PowerShell only where Git Bash is
missing — there the launcher does not run and the belt is off).

**Limits, said plainly.** The belt guards the Edit / Write / MultiEdit and Bash tools of a Claude Code
session. It does not see a status set through the engine's own CLI (`maistro card set-status <NODE>
--status Closed` — a node override, a manager's door; a leaf is refused there by the engine itself), and
the engine's post-run done guard (`core/agentdone.py`) lets a card pass when the run appended a
manager-style `ACCEPTED →` line — the belt is against the tired session, not a malicious one. The
closed vocabulary the Done hook knows is the hub's `maistro.yml` `lifecycle` block plus the built-in
synonyms; a pack's own closed status the hub does not restate is caught by the engine's guard, not here.
The plugin is **MIT** (`LICENSE` here; both manifests read ONE constant, `playbooks.PLUGIN_LICENSE`) —
Samer's call of 2026-09-26 (card MV2-13): the skills are thin sheets that call the engine, every rival set
is MIT, the moat is the engine and the board, which stay under the repo's Elastic 2.0. The namespace is
`beegait`. The engine repository is private; this folder is mirrored publicly, at the mirror's ROOT with a
one-plugin marketplace, at https://github.com/samermerhi560/beegait-plugin (refreshed per release —
`python tools/publish_plugin.py <mirror clone>`, then commit + push there), and that mirror is what the
listings point at: the directory follows its `main` and pins each version itself.

## Evals (`evals/`)

What an agent DOES with a skill, graded (card MV2-12): `claude plugin eval plugins/beegait --scaffold …` runs
24 cases with and without the plugin — the DB gate held, To Test never Done, a 📝 Request untouched, a release
note covering its scope, one should-trigger and one near-miss prompt per skill — every case starting from the
scratch hub `evals/_setup_hub.py` builds. Real tokens; the engine gate's `full` tier runs it only under
`MAISTRO_PLUGIN_EVAL=1`. `evals/README.md` has the layout, the run lines and the CLI's rules of the road. The
evals live in the engine repository only: the public mirror and the listed plugin carry no `evals/` folder
(test scaffolding reads as plugin behaviour to the directory's scanner).

## Regenerating

The skills and the two manifests are GENERATED from the engine's builders (`playbooks.plugin_skill`):
`python tools/build_plugin.py` rewrites them, `--check` refuses a stale tree (the engine gate's
`plugin` step). Hand-edit only `hooks/`, `evals/`, and this file.

---

Copyright (c) 2026 PHX ITS UG (haftungsbeschränkt), Holzkirchen, Germany. Beegait™ is a trade mark of
PHX ITS UG (haftungsbeschränkt) (EUTM 019419407).
