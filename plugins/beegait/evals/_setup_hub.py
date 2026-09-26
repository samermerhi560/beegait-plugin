"""Beegait plugin evals (card MV2-12, Story MV2-4) — the ONE scratch hub every case starts from.

    python _setup_hub.py [<dir>]      # builds the hub INTO <dir> (default: the cwd — the eval run's workspace)

`claude plugin eval` runs each case in an empty workspace; with `--scaffold` the case's `scaffold.sh`
calls this script, so the four behavior cases and the twenty trigger cases all see the SAME state — the
playbooks_test shape (one section, a few cards), grown to what the cases need:

  maistro.yml   project `demo` / code DEMO, one section `core`, `workspace.code_repos` → `app/`
  DEMO-1  task   To Do   "Fix the greeting" — trivial: app/greet.py returns 'Hello World', the test wants 'Hello, World!'
  DEMO-2  task   To Do   "Order priority" — carries a 🗄 Database STOP gate (the implement presents it and stops)
  DEMO-3  story  Draft   "Nightly orders export" — a 📝 Request VERBATIM (ground never edits a byte of it)
  DEMO-4  task   Done    feature · user-facing (order search by customer) — finished 2026-09-20
  DEMO-5  task   Done    fix · user-facing (invoice rounding) — finished 2026-09-21
  DEMO-6  task   Done    chore · internal (the orders log table renamed) — finished 2026-09-22
  releases/2026-09-R1   the release object over the three Done cards (window 2026-09-15 → 2026-09-25)
  docs/   execution-plan.md (the index every procedure reads first) + rules/account.md (the account rules)
  app/    the mapped code repo — its own git repo; tests/test_greet.py FAILS today, tests/test_orders.py passes
  git     the hub is a repo on `main` with a bare origin (`_origin.git`, ignored) so `card start` commits AND pushes

Exit 0 + one summary line, exit 1 with the reason. A non-empty <dir> is refused — never wiped.
Stdlib only; needs `maistro` on PATH (else `python -m maistro`) and `git`.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RELEASE_TAG = "2026-09-R1"
STORY_KEY = "DEMO-3"
CARD_KEYS = ("DEMO-1", "DEMO-2", "DEMO-3", "DEMO-4", "DEMO-5", "DEMO-6")
NEXT_KEY = "DEMO-7"                       # what `card new` mints next — the ground case's first child
NOTE_CARD = f"cards/communications/{RELEASE_TAG}/{RELEASE_TAG}-release-note.md"   # `release draft` creates it

MAISTRO_YML = """maistro: 1
project: { id: demo, name: Demo, code: DEMO, language: en }
sections:
  - { name: core, title: Core, aliases: [a] }
workspace:
  code_repos:
    - { name: app, path: app }
"""

GITIGNORE = "app/\n_origin.git/\n"

EXECUTION_PLAN = """# Demo — execution plan (the index)

The hub of the `app/` repo (mapped in `maistro.yml` → `workspace.code_repos`): one section, **Core**.
Read this page first, then only what a card links.

## The code, one line each

- `app/greet.py` — `greet()`: the product greeting (the string the Home screen shows).
- `app/orders.py` — the `Order` model, `load_orders()` over the `orders` table (a stub list here) and `search()`.
- `app/invoices.py` — `invoice_total()`: the 2-decimal rounding of an invoice.
- `app/tests/` — plain-python tests, no framework: `python app/tests/<name>.py` from the hub root, exit 0 = pass, they print `OK`.

## Runtime testing

A card's ✅ TCn is PASS only with the command AND its output produced in the session, recorded on the card as
`TCn — PASS — <command> → <one output line>`. The hub's own regression checks live under `tests/`
(one script per card, exit 0/1, its check labels = the card's TCn).

## Patterns

- A schema change is a numbered, guarded SQL script under `app/sql/` — the USER runs it (the card's 🗄 STOP gate),
  never the agent.
- A fix is the smallest change that makes the failing test pass — never a reformat of the file around it.
"""

ACCOUNT_RULES = """---
rules:
  level: account
  security:
    set_by: "the demo manager"
    set_at: "2026-09-01"
  coding:
    set_by: "the demo manager"
    set_at: "2026-09-01"
---

# Rules of the account

> Every agent run on every project of the account reads these rules.

## Security

- Never commit a secret, a token, a password or a `.env` file, and never print one in a log, a card or a reply.
- Never push to the main branch outside the card's own start commit, and never force-push.

## Coding conventions

- Follow the repository's existing formatting, naming and structure; never reformat code the card does not touch.
- One change per card — no drive-by refactors.
- Every change carries its test before the card moves to To Test.
- Write log lines and code comments in the language of the card.
"""

TASK_HEAD = """---
card:
  key: {key}
  epic: Core
  story: {story}
  task: {task}
  summary: "{summary}"
  issueType: Task
  layer: {layer}
  dependsOn: []
  status: {status}
  assignee: "{assignee}"
  labels: []
  components: []
  entities: []
  estimate: {estimate}
  estimateHours: {hours}
{extra}jira:
  project: ""
  epicName: Core
  parentStory: ""
---

# [{key}] {task}

> **Core** › **{story}**
> Read first: `docs/execution-plan.md` (the index) + `app/README.md` (how the tests run).
"""

DEMO_1 = TASK_HEAD.format(
    key="DEMO-1", story="Greeting", task="Fix the greeting",
    summary="Fix the greeting: greet() must return 'Hello, World!' — app/tests/test_greet.py fails today",
    layer="backend", status="To Do", assignee="", estimate="S", hours="0.5", extra="") + """
## Summary

The mapped repo `app/` greets from `greet()` in `app/greet.py`, which returns `Hello World` today; the test
`app/tests/test_greet.py` expects `Hello, World!` (the comma and the exclamation mark the product copy asks
for) and FAILS. This card fixes that one return value — nothing else in the repo changes — and proves it with
the existing test. No schema, no new file under `app/`.

## 🔧 Technical steps

1. `app/greet.py` — `greet()` returns `"Hello, World!"` (the exact string `app/tests/test_greet.py` asserts).
2. Run `python app/tests/test_greet.py` from the hub root — it prints `OK` and exits 0 (it exits 1 today).

## ✅ Test cases

1. **TC1** — `python app/tests/test_greet.py` exits 0 and prints `OK`.

## Progress log

- 2026-09-24 — authored by the demo manager.
"""

DEMO_2 = TASK_HEAD.format(
    key="DEMO-2", story="Orders", task="Order priority",
    summary="Order priority: a priority column on the orders table (a 🗄 STOP gate) and the field on the Order model",
    layer="database", status="To Do", assignee="", estimate="M", hours="2.0", extra="") + """
## Summary

Orders have no priority today: `app/orders.py` builds `Order(id, customer, total)` from the `orders` table and
the ops team cannot rank the picking queue. This card adds a `priority` column (integer, default 0) and the
matching field on the model. The column is a schema change — the script below is run by the USER first.

## 🗄 Database — STOP gate

**STOP: schema scripts are run by the USER, never automatically.** Scripts are idempotent + guarded,
saved in the code repo, and numbered.

```sql
-- app/sql/001_orders_priority.sql — guarded, idempotent
ALTER TABLE orders ADD COLUMN IF NOT EXISTS priority integer NOT NULL DEFAULT 0;
```

## 🔧 Technical steps

1. `app/sql/001_orders_priority.sql` — the script above, saved in the repo.
2. `app/orders.py` — `Order` gains `priority: int = 0`; `load_orders()` reads the fourth column of every row.
3. `app/tests/test_orders.py` — one more assertion: every loaded order has `priority == 0` by default.

## ✅ Test cases

1. **TC1** — `python app/tests/test_orders.py` exits 0 and prints `OK` with the priority assertion in place.

## Progress log

- 2026-09-24 — authored by the demo manager.
"""

DEMO_3 = """---
card:
  key: DEMO-3
  type: story
  parent: ""
  epic: Core
  story: Nightly orders export
  task: Nightly orders export
  summary: Nightly orders export
  layer: functional
  grounding: functional
  dependsOn: []
  status: Draft
  assignee: ""
  labels: []
jira:
  project: ""
  epicName: Core
  parentStory: ""
---

# [DEMO-3] Nightly orders export

> **Core** › 📖 **STORY** — a business-level node: no hours, no developer status;
> its state and progress are derived from its children (technical cards).
> The 📝 Request section is the manager's VERBATIM words — no agent may edit it, ever
> (the engine refuses and restores an agent edit); 🤖 Reading back is the team's
> restatement; 🎯 / ✅ / 🖼 / 💠 are PM-owned.

## 📝 Request — as written by Sam, 2026-09-23

we need a nightly export of the orders to a csv file on the shared drive,
the ops team reads it every morning at 7. also the file name shoud carry the date

**Attachments:**
- _none_

## 🤖 Reading back

_none yet — the agent's restatement of the request goes here; the request above is never edited_

## ✅ Acceptance (business)

- Every morning the ops team finds yesterday's orders as one CSV file on the shared drive, its name carrying the date.

## Progress log
- _2026-09-23 — Story created by Sam (verbatim request)_
"""

# the 📝 block of DEMO-3 exactly as written — the ground case's grader compares the file against it
REQUEST_BLOCK = DEMO_3[DEMO_3.index("## 📝 Request"):DEMO_3.index("## 🤖 Reading back")]

DONE_EXTRA = '  progress: 100\n  spentHours: {spent}\n  changeKind: "{kind}"\n  userFacing: "{facing}"\n'

DEMO_4 = TASK_HEAD.format(
    key="DEMO-4", story="Orders", task="Order search by customer name",
    summary="Order search by customer name: search() on the Orders screen filters the list by a customer substring",
    layer="frontend", status="Done", assignee="demo-dev", estimate="M", hours="2.0",
    extra=DONE_EXTRA.format(spent="1.5", kind="feature", facing="yes")) + """
## Summary

The Orders screen listed every order and the ops team scrolled for a customer. This card added `search(customer)`
in `app/orders.py` (a case-insensitive substring match on the customer name) and the search box above the list on
the Orders screen: typing filters the list as you type, an empty box shows every order again.

## 🔧 Technical steps

1. `app/orders.py` — `search(customer)` over `load_orders()`.
2. The Orders screen — the search box wired to it (the list re-renders on every keystroke).

## ✅ Test cases

1. **TC1** — `python app/tests/test_orders.py` → `OK` (`search("acme")` returns the one Acme order).

## Progress log

- 2026-09-18 — authored by the demo manager.
- _2026-09-19 — → **In Progress** by demo-dev (implement start)_
- 2026-09-20 — TC1 — PASS — `python app/tests/test_orders.py` → `OK`.
- _2026-09-20 — → **To Test** by demo-dev (1.5h)_
- _2026-09-21 — ACCEPTED → **Done** by Sam (board)_
"""

DEMO_5 = TASK_HEAD.format(
    key="DEMO-5", story="Invoices", task="Invoice total rounding",
    summary="Invoice total rounding: a total ending in .005 rounded DOWN on the invoice; now half-up to two decimals",
    layer="backend", status="Done", assignee="demo-dev", estimate="S", hours="1.0",
    extra=DONE_EXTRA.format(spent="0.5", kind="fix", facing="yes")) + """
## Summary

`invoice_total()` in `app/invoices.py` used Python's banker's rounding, so an invoice whose lines summed to
12.345 showed 12.34 while the customer's own sum said 12.35 — a support ticket a week. The fix rounds half-up
to two decimals with `decimal`; the invoice screen shows the same total as the customer's calculator.

## 🔧 Technical steps

1. `app/invoices.py` — `invoice_total()` rounds with `Decimal.quantize(ROUND_HALF_UP)`.

## ✅ Test cases

1. **TC1** — `python app/tests/test_invoices.py` → `OK` (12.345 → 12.35).

## Progress log

- 2026-09-19 — authored by the demo manager.
- _2026-09-21 — → **In Progress** by demo-dev (implement start)_
- 2026-09-21 — TC1 — PASS — `python app/tests/test_invoices.py` → `OK`.
- _2026-09-21 — → **To Test** by demo-dev (0.5h)_
- _2026-09-22 — ACCEPTED → **Done** by Sam (board)_
"""

DEMO_6 = TASK_HEAD.format(
    key="DEMO-6", story="Orders", task="Rename the orders_log table to order_events",
    summary="Rename the orders_log table to order_events (a migration + its two readers) — an internal clean-up, nothing visible",
    layer="database", status="Done", assignee="demo-dev", estimate="S", hours="1.0",
    extra=DONE_EXTRA.format(spent="1.0", kind="chore", facing="no")) + """
## Summary

The `orders_log` table held order EVENTS (status changes), and every new reader mis-read the name. This card
renamed it to `order_events` with a guarded migration and updated its two readers in `app/orders.py`; no screen,
no API field changed.

## 🔧 Technical steps

1. `app/sql/000_order_events.sql` — `ALTER TABLE orders_log RENAME TO order_events` (guarded).
2. `app/orders.py` — the two readers name the new table.

## ✅ Test cases

1. **TC1** — `python app/tests/test_orders.py` → `OK` after the rename.

## Progress log

- 2026-09-20 — authored by the demo manager.
- _2026-09-22 — → **In Progress** by demo-dev (implement start)_
- 2026-09-22 — TC1 — PASS — `python app/tests/test_orders.py` → `OK`.
- _2026-09-22 — → **To Test** by demo-dev (1.0h)_
- _2026-09-23 — ACCEPTED → **Done** by Sam (board)_
"""

APP_README = """# app — the demo's mapped code repo

Plain Python, no framework. Tests are scripts: `python tests/<name>.py` from this folder, or
`python app/tests/<name>.py` from the hub root — exit 0 and `OK` on pass, exit 1 and a `FAIL …` line otherwise.
`tests/test_greet.py` fails today (card DEMO-1); `tests/test_orders.py` and `tests/test_invoices.py` pass.
"""

APP_GREET = '''"""The product greeting shown on the Home screen."""


def greet() -> str:
    return "Hello World"
'''

APP_ORDERS = '''"""Orders: the model, the reader over the `orders` table (a stub list here — no database in the demo)
and the customer search of the Orders screen (card DEMO-4)."""
from __future__ import annotations

from dataclasses import dataclass

ROWS = [(1, "Acme", 120.0), (2, "Globex", 75.5)]


@dataclass
class Order:
    id: int
    customer: str
    total: float


def load_orders() -> list[Order]:
    return [Order(*r) for r in ROWS]


def search(customer: str) -> list[Order]:
    q = customer.lower()
    return [o for o in load_orders() if q in o.customer.lower()]
'''

APP_INVOICES = '''"""Invoices: the total of an invoice's lines, rounded half-up to two decimals (card DEMO-5)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def invoice_total(lines: list[float]) -> float:
    total = sum((Decimal(str(x)) for x in lines), Decimal("0"))
    return float(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
'''

TEST_HEAD = '''import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
'''

APP_TEST_GREET = TEST_HEAD + '''from greet import greet  # noqa: E402

if greet() != "Hello, World!":
    print(f"FAIL greet() -> {greet()!r}, expected 'Hello, World!'")
    sys.exit(1)
print("OK")
'''

APP_TEST_ORDERS = TEST_HEAD + '''from orders import load_orders, search  # noqa: E402

orders = load_orders()
if len(orders) != 2 or orders[0].customer != "Acme":
    print(f"FAIL load_orders() -> {orders!r}")
    sys.exit(1)
if [o.id for o in search("acme")] != [1] or search("") != orders:
    print("FAIL search()")
    sys.exit(1)
print("OK")
'''

APP_TEST_INVOICES = TEST_HEAD + '''from invoices import invoice_total  # noqa: E402

if invoice_total([10.0, 2.345]) != 12.35 or invoice_total([]) != 0.0:
    print(f"FAIL invoice_total([10.0, 2.345]) -> {invoice_total([10.0, 2.345])!r}, expected 12.35")
    sys.exit(1)
print("OK")
'''

FILES = {
    "maistro.yml": MAISTRO_YML,
    ".gitignore": GITIGNORE,
    "docs/execution-plan.md": EXECUTION_PLAN,
    "docs/rules/account.md": ACCOUNT_RULES,
    "cards/core/greeting/demo-1.md": DEMO_1,
    "cards/core/orders/demo-2.md": DEMO_2,
    "cards/core/nightly-orders-export/demo-3.md": DEMO_3,
    "cards/core/orders/demo-4.md": DEMO_4,
    "cards/core/invoices/demo-5.md": DEMO_5,
    "cards/core/orders/demo-6.md": DEMO_6,
    "app/README.md": APP_README,
    "app/greet.py": APP_GREET,
    "app/orders.py": APP_ORDERS,
    "app/invoices.py": APP_INVOICES,
    "app/tests/test_greet.py": APP_TEST_GREET,
    "app/tests/test_orders.py": APP_TEST_ORDERS,
    "app/tests/test_invoices.py": APP_TEST_INVOICES,
}


def _run(args: list[str], cwd: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(args, cwd=str(cwd), env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} (in {cwd}) exited {r.returncode}: "
                           f"{(r.stderr or r.stdout).strip()[-600:]}")
    return r


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return _run(["git", *args], repo)


def _engine_root() -> Path | None:
    """The engine source checkout this evals tree sits in (plugins/beegait/evals/ → the repo root), else None."""
    root = Path(__file__).resolve().parents[3]
    return root if (root / "maistro" / "__init__.py").is_file() else None


def _user_site_dirs() -> list[str]:
    """The site-packages of a `pip install --user` engine, derived from the `maistro` console script on PATH —
    `%APPDATA%\\Python\\Python3X\\{Scripts,site-packages}` on Windows, `~/.local/{bin,lib/python3.X/site-packages}`
    on POSIX. The eval runner hands the scaffold a MINIMAL environment whose HOME / USERPROFILE point at a sandbox
    home, so Python's own user site resolves THERE and every user-site package (the engine, PyYAML) is invisible
    (lived 2026-09-25: `No module named 'maistro'`, then `No module named 'yaml'`); PATH is passed through, so the
    script's location is the one trace of the real profile — the shell-folder API expands the sandbox profile too."""
    exe = shutil.which("maistro")
    if not exe:
        return []
    scripts = Path(exe).resolve().parent
    cands = [scripts.parent / "site-packages", *sorted(scripts.parent.glob("lib/python3*/site-packages"))]
    return [str(c) for c in cands if c.is_dir()]


def _maistro_env() -> dict:
    """The env of every `maistro` call here: the engine root first on PYTHONPATH when this tree sits inside a
    source checkout (the tree under test, never an installed copy), then the user site of `_user_site_dirs`."""
    env = {**os.environ, "MAISTRO_ACTOR": "demo-manager"}
    root = _engine_root()
    parts = ([str(root)] if root is not None else []) + _user_site_dirs()
    if env.get("PYTHONPATH"):
        parts.append(env["PYTHONPATH"])
    if parts:
        env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def _maistro_argv() -> list[str]:
    """`python -m maistro` from a source checkout (the interpreter running this script sees PYTHONPATH), else
    the `maistro` console script on PATH."""
    if _engine_root() is not None:
        return [sys.executable, "-m", "maistro"]
    exe = shutil.which("maistro")
    return [exe] if exe else [sys.executable, "-m", "maistro"]


def _init_repo(repo: Path, message: str) -> None:
    """A repo on `main` with a repo-local identity (the eval child runs under a fresh HOME — no global
    git config there — and the hub's own identity is what `card start` commits as)."""
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "--local", "user.name", "demo-dev")
    _git(repo, "config", "--local", "user.email", "demo-dev@example.test")
    _git(repo, "config", "--local", "core.autocrlf", "false")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)


def build(target: Path) -> str:
    target = target.resolve()
    if target.exists() and any(target.iterdir()):
        raise RuntimeError(f"{target} is not empty — the scratch hub is built into an EMPTY folder, never over one")
    for rel, text in FILES.items():
        p = target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    _init_repo(target / "app", "seed: the demo app")
    env = _maistro_env()
    m = _maistro_argv() + ["--hub", str(target)]
    _run(m + ["build"], target, env)                                   # the dashboards exist before the run
    _run(m + ["release", "new", RELEASE_TAG, "--since", "2026-09-15", "--until", "2026-09-25",
              "--lane", "done", "--title", "September release"], target, env)
    _init_repo(target, "seed: the demo hub")
    bare = target / "_origin.git"
    _git(target, "init", "-q", "--bare", str(bare))
    _git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(target, "remote", "add", "origin", "file:///" + bare.as_posix().lstrip("/"))
    _git(target, "push", "-q", "-u", "origin", "main")
    return (f"scratch hub built in {target}: {len(CARD_KEYS)} cards (Story {STORY_KEY}, next key {NEXT_KEY}), "
            f"release {RELEASE_TAG}, app/ with one failing test, origin = _origin.git")


def main(argv: list[str]) -> int:
    target = Path(argv[1]) if len(argv) > 1 else Path.cwd()
    try:
        print(build(target))
    except (RuntimeError, OSError) as e:
        print(f"_setup_hub: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
