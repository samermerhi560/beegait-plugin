---
type: regex
target: { source: file, path: cards/core/greeting/demo-1.md }
flags: m
match: not_contains
---
^\s*status: Done\s*$
