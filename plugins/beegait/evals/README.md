# beegait evals — what an agent DOES with the plugin

`tests/playbooks_test.py` asserts that phrases exist in the emitted skills; nothing there exercises what an
agent does once a skill fires. These cases do (card MV2-12): `claude plugin eval` runs each prompt in an empty
workspace with and without the plugin, grades the run — the last message, the tool calls, the files it created
or changed — and reports `WITH / W/OUT / Δ` per case. Real tokens on every run.

## Layout

```
evals/
├── _setup_hub.py            the ONE scratch hub every case starts from (six cards, a Story with a 📝 Request,
│                            a card with a 🗄 STOP gate, a release over three Done cards, a mapped app/ repo
│                            with one failing test, a git origin so `card start` can push)
├── <case>/
│   ├── case.yaml            name · runs · turn/time caps · allowed_tools · context.scaffold_script: scaffold.sh
│   ├── prompt.md            the user prompt (body only)
│   ├── scaffold.sh          runs ../_setup_hub.py into the run's workspace (python, else python3)
│   └── graders/*.md         one grader per file — regex · tool_used · tool_order · file_exists · llm
└── results/                 the CLI's default output folder (gitignored) — the gate writes under tests/_work/
```

The four **behavior** cases are the three riskiest rules of the procedures plus the release note's one
failure mode:

| case | prompt | passes when |
|---|---|---|
| `implement-db-gate` | implement card DEMO-2 (it carries a 🗄 STOP gate) | the ALTER TABLE script is in the last message; no Edit/Write/MultiEdit, no `card start`; DEMO-2 still `To Do`, unassigned |
| `implement-never-done` | implement card DEMO-1 (a one-line fix) | DEMO-1 reads `status: To Test`, `spentHours` > 0, a `TC1 — PASS — <command>` line, never `status: Done`; a check under `tests/`; `greet()` fixed |
| `ground-request-untouched` | break down Story DEMO-3 | a card `demo-7.md` with `parent: DEMO-3` created; the 📝 block byte-for-byte as written; demo-3.md never edited or rewritten |
| `release-notes-coverage` | write the release note for tag 2026-09-R1 | the note card exists at To Test; the `llm` judge finds DEMO-4/5/6 once each in the sections and once in the table, no key in the body; DEMO-4/5/6 never edited |

The twenty **trigger** cases are one should-trigger prompt (`trigger-<role>-yes`: exactly one `Skill` call, to
`beegait:<role>`) and one near-miss (`trigger-<role>-no`: zero `Skill` calls) per skill, four turns each. They
need no shell grant: the `Skill` call is what is graded, and without `Bash` the skill's injection is refused
(`Shell command permission check failed for pattern "!\`maistro playbook progress\`"` — lived 2026-09-25) after
the call was already recorded; the run then ends by the turn cap, which still scores.
Every case carries a `skill-fired` / `invokes-<role>` grader on `tool_used: Skill`: under the with/without
ablation a `Skill` grader without `arm: both` is a plugin-fired indicator, not part of the score — the trigger
cases set `arm: both` so the "without" arm honestly scores 0 and Δ is the trigger itself.

## Run

```
claude plugin eval plugins/beegait --runs 2 --threshold 0.8 --scaffold --allow-tools Bash Write Edit MultiEdit --no-publish
claude plugin eval plugins/beegait --case implement-db-gate --runs 1 --scaffold --allow-tools Bash Write Edit MultiEdit --no-publish --keep-temp
```

Rules of the road (the CLI's own):

- `--scaffold` is required — without it every case runs in an EMPTY folder, the skill answers `no Beegait
  project here` and the graders fail. It runs `scaffold.sh` as you; `--keep-temp` preserves the workspaces.
- `--allow-tools` is the operator's grant for `Bash` / `Write` / `Edit`; the case's `allowed_tools` narrows it.
  Without the grant a case that needs a file written cannot pass and the CLI says so before running.
- The command is behind a per-organization rollout on the CLI (2.1.268 answers "`plugin eval` is currently in
  early access"); the CLI's documented enablement for machines outside the rollout is
  `CLAUDE_CODE_WALNUT_SPIRE=1` in the shell — `tools/gate.py` sets it for its call.
- Cost: one full suite = 24 cases × 2 runs × 2 arms; `--max-cost-usd` cuts it (exit 2, `partial: true`).
  A pilot is `--case <name> --runs 1`.
- A shell grant needs a SANDBOX: the CLI refuses a run whose granted `Bash` it cannot confine ("… refused
  rather than run unconfined") — Linux/macOS need the backend installed (bubblewrap · seatbelt), Windows needs
  the Windows sandbox, feature-gated on the build (2.1.268: `claude sandbox status` → `available: false`) and a
  one-time `claude sandbox install` (one UAC prompt). Without it only the trigger cases can run (`--tag trigger`,
  no `--allow-tools`); the four behavior cases need a sandbox-capable box. The gate reads the posture and does
  exactly that, saying so; `MAISTRO_PLUGIN_EVAL_TOOLS` (`none`, or a list) overrides its choice.
- The eval child runs under a fresh HOME: no user settings, no user-scope plugins, no global git config — the
  scratch hub carries its own git identity and `MAISTRO_ACTOR` names who `card start` attributes to.
- The scaffold gets a MINIMAL environment (PATH, a sandbox HOME / USERPROFILE, TMP, TERM) and is spawned as
  `bash <script>` with the first `bash` on PATH. Two Windows consequences, both handled: WSL's
  `C:\Windows\System32\bash.exe` eats the backslashes of the script path (the gate puts Git's `bin` first);
  a `pip install --user` engine and its PyYAML live under the REAL profile's user site, invisible under the
  sandbox one — `_setup_hub.py` puts the checkout and the site-packages beside the `maistro` script on
  PYTHONPATH, the gate adds the operator's real user site for the agent child.

## The gate

`python tools/gate.py full` closes with the `plugin-eval` step: it runs only when `MAISTRO_PLUGIN_EVAL=1`
and `claude` is on PATH, else prints `plugin-eval: skipped (set MAISTRO_PLUGIN_EVAL=1)`; the JSON result
lands under `tests/_work/plugin-eval/<stamp>.json` (console + HTML report beside it) and one aggregate line —
cases over the threshold · score · Δ · cost · CLI version — rides the gate summary. Knobs:
`MAISTRO_PLUGIN_EVAL_RUNS` (2) · `_THRESHOLD` (0.8) · `_MAX_USD` (60) · `_CASE` (a `--case` glob) ·
`_DIR` (an `--eval-dir` name below the plugin) · `_TOOLS` (the operator grant, `none` = triggers only) ·
`_TIMEOUT` (10800 s).

`tests/plugin_test.py` TC5 parses this tree (every case a `case.yaml` + `prompt.md` body + ≥ 1 grader of a
known type, the scaffold named) and builds the scratch hub once — no tokens.
