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

client = CascadeCMS("https://cascade.example.com", "username", "password")

# Phase 1: List inbox messages
client.operations.listMessages()
messages = client.submit_requests()

if isinstance(messages, CascadeError):
    raise RuntimeError(messages.message)

# Phase 2: Mark the first message as read and delete the second message
if messages.elements:
    first_msg = messages.elements[0]
    second_msg = messages.elements[1] if len(messages.elements) > 1 else None

    if isinstance(first_msg, Message):
        client.operations.markMessage(first_msg)
    if second_msg and isinstance(second_msg, Message):
        client.operations.deleteMessage(second_msg)

    result = client.submit_requests()
    if isinstance(result, CascadeError):
        raise RuntimeError(result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError, preference

client = CascadeCMS("https://cascade.example.com", "username", "password")

# Call 1: Read current user preferences
client.operations.readPreferences()
prefs = client.submit_requests()

if isinstance(prefs, CascadeError):
    raise RuntimeError(prefs.message)

# Call 2: Update a preference using the preference payload
client.operations.editPreference(preference(name="emailNotifications", value="true"))
result = client.submit_requests()

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
