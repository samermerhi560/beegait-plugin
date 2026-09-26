---
type: llm
focus: { source: file, path: cards/communications/2026-09-R1/2026-09-R1-release-note.md }
weight: 3
---
The file is the END-USER release note the run wrote into the hub's draft card for release 2026-09-R1.
The release's scope is exactly three cards:
- DEMO-4 — a feature, user-facing: order search by customer name on the Orders screen (a search box that filters the list as you type).
- DEMO-5 — a fix, user-facing: invoice totals ending in .005 were rounded down; now rounded half-up to two decimals.
- DEMO-6 — a chore, internal: the orders_log table renamed to order_events (nothing visible to a user).

PASS only if ALL of the following hold:
1. Each of the three changes appears EXACTLY ONCE as an entry in the body sections (✨ What's new / 🐛 Fixes / 🔧 Under the hood / ⏳ Pending acceptance): the search feature under What's new, the rounding fix under Fixes (or What's new), the table rename as one short line under Under the hood.
2. Each of the three keys DEMO-4, DEMO-5 and DEMO-6 appears in the 📋 Traceability table (the table at the end).
3. No card key (DEMO-4, DEMO-5, DEMO-6 or any DEMO-N) appears in the body OUTSIDE the traceability table.
4. The body names no person, handle (@…), hour count, hostname or repository path.
5. No `<hint>` placeholder and no HTML comment of the template is left in the file.
FAIL if any scope card is missing, duplicated, or only mentioned in the table; if a key leaks into the body; or if the file is still the untouched template.
