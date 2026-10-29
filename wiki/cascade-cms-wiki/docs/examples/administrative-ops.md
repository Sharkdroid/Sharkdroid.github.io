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
list_result = cascade.operations.listMessages().submit_requests()
if isinstance(list_result, CascadeError):
    raise RuntimeError(list_result.message)

messages = list_result.flat

# Phase 2: Mark read and delete selected messages
for message in messages:
    cascade.operations.markMessage(message)
    cascade.operations.deleteMessage(message)

results = cascade.operations.submit_requests()
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
read_result = cascade.operations.readPreferences().submit_requests()
if isinstance(read_result, CascadeError):
    raise RuntimeError(read_result.message)

# Update a user preference
pref_payload = preference(name="somePreferenceName", value="new_value")
edit_result = cascade.operations.editPreference(pref_payload).submit_requests()
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
