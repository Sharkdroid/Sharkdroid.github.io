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
from cascade_cms.cmstypes import CascadeError

# Phase 1: List inbox messages
cascade.operations.listMessages()
messages = cascade.submit_requests()

if isinstance(messages, CascadeError):
    raise RuntimeError(messages.message)

# Pick a message from the list elements
message = messages.flat[0]

# Phase 2: Mark as read and then delete
cascade.operations.markMessage(message)
cascade.operations.deleteMessage(message)
results = cascade.submit_requests()

for res in results:
    if isinstance(res, CascadeError):
        raise RuntimeError(res.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import CascadeError, preference

# Read current preferences
cascade.operations.readPreferences()
prefs = cascade.submit_requests()

if isinstance(prefs, CascadeError):
    raise RuntimeError(prefs.message)

# Update a user preference
cascade.operations.editPreference(preference(name="pref_name", value="new_value"))
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.1 -->
