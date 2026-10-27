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
from cascade_cms import CascadeCMS, CascadeError

# Phase 1: List inbox messages
cascade.operations.listMessages()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

messages = result.flat

# Phase 2: Mark read and delete selected messages
for msg in messages:
    cascade.operations.markMessage(msg)

cascade.operations.deleteMessage(messages[0])
results = cascade.submit_requests()

for res in (results if isinstance(results, list) else [results]):
    if isinstance(res, CascadeError):
        print(f"Operation failed: {res.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS, CascadeError, preference

# Read current user preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Update a specific preference
cascade.operations.editPreference(preference(name="dateFormat", value="yyyy-MM-dd"))
edit_result = cascade.submit_requests()

if isinstance(edit_result, CascadeError):
    raise RuntimeError(edit_result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.2 -->
