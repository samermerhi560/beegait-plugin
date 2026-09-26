---
type: regex
target: last_message
flags: i
---
ALTER TABLE orders ADD COLUMN IF NOT EXISTS priority
