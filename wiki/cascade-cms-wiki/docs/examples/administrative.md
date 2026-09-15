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
messages = cms.submit_requests()

if isinstance(messages, CascadeError):
    raise RuntimeError(messages.message)

# Phase 2: Mark the first message as read and delete a second one
for msg in messages.flat:
    if isinstance(msg, Message):
        cms.operations.markMessage(msg)
        cms.operations.deleteMessage(msg)
        
res = cms.submit_requests()
if isinstance(res, CascadeError):
    raise RuntimeError(res.message)
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

# Phase 1: Read current user preferences
cms.operations.readPreferences()
prefs = cms.submit_requests()

if isinstance(prefs, CascadeError):
    raise RuntimeError(prefs.message)

# Phase 2: Update a preference
cms.operations.editPreference(preference(name="theme", value="dark"))
res = cms.submit_requests()

if isinstance(res, CascadeError):
    raise RuntimeError(res.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.5 -->
