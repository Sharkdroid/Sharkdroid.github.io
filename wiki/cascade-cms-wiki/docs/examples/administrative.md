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
res = cascade.operations.listMessages().submit_requests()
if isinstance(res, CascadeError):
    raise RuntimeError(res.message)

messages = res.flat

# Phase 2: Mark the first message as read, then delete it
if messages:
    msg: Message = messages[0]
    
    # Mark message
    res = cascade.operations.markMessage(msg).submit_requests()
    if isinstance(res, CascadeError):
        raise RuntimeError(res.message)
        
    # Delete message
    res = cascade.operations.deleteMessage(msg).submit_requests()
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

# Read current user preferences
res = cascade.operations.readPreferences().submit_requests()
if isinstance(res, CascadeError):
    raise RuntimeError(res.message)

# Update a user preference
res = cascade.operations.editPreference(preference(name="theme", value="dark")).submit_requests()
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
