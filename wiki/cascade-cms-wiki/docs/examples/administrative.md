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

client = CascadeCMS()

# Phase 1: Retrieve inbox messages
client.operations.listMessages()
result = client.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

messages = result.flat

# Phase 2: Mark the first message as read and delete the second
if len(messages) > 0:
    client.operations.markMessage(messages[0])
if len(messages) > 1:
    client.operations.deleteMessage(messages[1])

action_result = client.submit_requests()

if isinstance(action_result, CascadeError):
    raise RuntimeError(action_result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError, preference

client = CascadeCMS()

# Phase 1: Read current user preferences
client.operations.readPreferences()
result = client.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Phase 2: Update a specific preference
client.operations.editPreference(preference(name="dateFormat", value="yyyy-MM-dd"))
edit_result = client.submit_requests()

if isinstance(edit_result, CascadeError):
    raise RuntimeError(edit_result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.3 -->
