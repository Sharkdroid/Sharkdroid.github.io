# Administrative Operations: Messages & Preferences

These operations don't touch CMS assets — they manage the current user's
inbox and account preferences. They're grouped separately from the main
patterns doc because they're a self-contained feature area, not part of the
asset read/write/search workflow.

Both examples follow the same wrapper → operations → `submit_requests()`
skeleton as the main patterns, just applied to two unrelated features.

---

## Messages: list, mark, delete

```python
from cascade_cms.cmstypes import CascadeError, Message

# Phase 1: List inbox messages
driver.operations.listMessages()
result = driver.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

messages = result.flat

# Phase 2: Mark or delete selected messages
for msg in messages:
    if msg.marked == "unread":
        driver.operations.markMessage(msg)
    else:
        driver.operations.deleteMessage(msg)

action_result = driver.submit_requests()
if isinstance(action_result, CascadeError):
    raise RuntimeError(action_result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import CascadeError, preference

# Read current preferences
driver.operations.readPreferences()
result = driver.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Update a specific user preference
driver.operations.editPreference(preference(name="dateFormat", value="yyyy-MM-dd"))
edit_result = driver.submit_requests()

if isinstance(edit_result, CascadeError):
    raise RuntimeError(edit_result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.5 -->
