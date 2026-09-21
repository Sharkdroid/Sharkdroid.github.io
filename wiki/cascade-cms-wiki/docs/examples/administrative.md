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
from cascade_cms import CascadeCMSRestDriver, CascadeError

driver = CascadeCMSRestDriver(...)

# Phase 1: List inbox messages
driver.operations.listMessages()
messages = driver.submit_requests()

if isinstance(messages, CascadeError):
    raise RuntimeError(messages.message)

# Select a message to update and delete
msg = messages.elements[0]

# Phase 2: Mark message and delete message
driver.operations.markMessage(msg)
driver.operations.deleteMessage(msg)
results = driver.submit_requests()

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
from cascade_cms import CascadeCMSRestDriver, CascadeError, preference

driver = CascadeCMSRestDriver(...)

# Read current preferences
driver.operations.readPreferences()
prefs = driver.submit_requests()

if isinstance(prefs, CascadeError):
    raise RuntimeError(prefs.message)

# Edit a preference
driver.operations.editPreference(preference(name="theme", value="dark"))
result = driver.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.6 -->
