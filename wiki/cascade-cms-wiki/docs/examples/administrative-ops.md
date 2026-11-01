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
from cascade_cms.cmstypes import Message

cms = CascadeCMS(url="...", username="...", password="...")

# Phase 1: List inbox messages
cms.operations.listMessages()
messages = cms.submit_requests()

if isinstance(messages, CascadeError):
    raise RuntimeError(messages.message)

for msg in messages.flat:
    print(f"Message from {msg.m_from}: {msg.m_subject}")

# Phase 2: Mark or delete specific messages using retrieved Message objects
target_msg = messages.flat[0]
cms.operations.markMessage(target_msg)
result = cms.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

cms.operations.deleteMessage(target_msg)
del_result = cms.submit_requests()

if isinstance(del_result, CascadeError):
    raise RuntimeError(del_result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS, CascadeError
from cascade_cms.cmstypes import preference

cms = CascadeCMS(url="...", username="...", password="...")

# Read current user preferences
cms.operations.readPreferences()
prefs = cms.submit_requests()

if isinstance(prefs, CascadeError):
    raise RuntimeError(prefs.message)

print(prefs.flat)

# Update a user preference
cms.operations.editPreference(preference(name="my-pref", value="new-value"))
result = cms.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.2 -->
