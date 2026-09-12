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
from cascade_cms.cmstypes import CascadeError, Message

client = CascadeCMS("https://cascade.example.com", "user", "pass")

# Phase 1: Retrieve inbox messages
client.operations.listMessages()
result = client.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Assume we select the first message from the inbox list
messages = result.flat
if messages:
    msg: Message = messages[0]
    
    # Phase 2: Mark the message as read, then delete it
    client.operations.markMessage(msg)
    client.operations.deleteMessage(msg)
    
    mark_result = client.submit_requests()
    if isinstance(mark_result, CascadeError):
        raise RuntimeError(mark_result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError, preference

client = CascadeCMS("https://cascade.example.com", "user", "pass")

# Read current user preferences
client.operations.readPreferences()
result = client.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Update a single user preference
client.operations.editPreference(preference(name="defaultView", value="grid"))
update_result = client.submit_requests()

if isinstance(update_result, CascadeError):
    raise RuntimeError(update_result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.5 -->
