# beegait-plugin

The public mirror of the Beegait plugin for Claude Code — and for every agent that reads `.agents/skills`
through the skills.sh CLI. Mirrored from `plugins/beegait/` of the Beegait engine (a private repository)
at engine **v0.2.154** (`aea522c`), refreshed per release; the skills and the two manifests are GENERATED
there from the engine's builders, so nothing is hand-edited here — issues are welcome, pull requests are
folded into the engine.

## What it is — and what it is not

Ten skills — `progress`, `checkpoint`, `build-ai-card`, `implement-ai-card`, `build-functional-card`,
`ground-card`, `review-card`, `release-notes`, `user-guide`, `kb-curate` — each a thin sheet that runs
`maistro playbook <role>` at invocation: the engine serves the procedure for the Beegait project you stand
in, with the account's rules and the pack's guidance folded in. Plus the belt: three hooks that refuse a
force push, an edit inside a card's 📝 Request and an agent-set Done. It is NOT the product: the engine
serves every procedure and the Beegait board is where a manager writes the request, accepts the card and
dispatches a run to a runner — the skills alone plan nothing and decide nothing.

## Install

```
/plugin marketplace add samermerhi560/beegait-plugin      # Claude Code
/plugin install beegait@beegait

npx skills add samermerhi560/beegait-plugin -a claude-code -a codex -a cursor   # any agent, via skills.sh
```

In a Beegait project the per-project stubs are already there — they travel with the clone
(`maistro clone <hub-git-url>`). The one prerequisite is the engine on PATH, 0.2.154 or newer: the Beegait
Runner installs it and keeps it current. Every implement runs on your own machine through the Beegait
Runner — download it at https://app.beegait.ai (the trial's first step).

## Layout

- `plugins/beegait/` — the plugin: `.claude-plugin/plugin.json`, `skills/<role>/SKILL.md` × 10,
  `hooks/` (the belt), `evals/` (the `claude plugin eval` cases), `README.md`, `LICENSE`
- `.claude-plugin/marketplace.json` — the marketplace `beegait` whose one plugin is `./plugins/beegait`

## Licence

MIT — see `plugins/beegait/LICENSE`. The engine and the board are separate products under their own terms.
