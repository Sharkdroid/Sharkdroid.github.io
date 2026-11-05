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
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError

cms = CascadeCMS(url="...", username="...", password="...")

# Phase 1: List inbox messages
cms.operations.listMessages()
messages_result = cms.submit_requests()

if isinstance(messages_result, CascadeError):
    raise RuntimeError(messages_result.message)

# Assume we found a message to process
message = messages_result.flat[0]

# Phase 2: Mark read and delete the message
cms.operations.markMessage(message)
cms.operations.deleteMessage(message)
results = cms.submit_requests()
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError, preference

cms = CascadeCMS(url="...", username="...", password="...")

# Read current preferences
cms.operations.readPreferences()
prefs_result = cms.submit_requests()

if isinstance(prefs_result, CascadeError):
    raise RuntimeError(prefs_result.message)

# Update a user preference
cms.operations.editPreference(preference(name="my-pref", value="new-value"))
edit_result = cms.submit_requests()

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
