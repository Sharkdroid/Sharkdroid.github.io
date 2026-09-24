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
cascade.operations.listMessages()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

messages = result.elements

# Phase 2: Mark the first message as read and delete the second
if messages:
    cascade.operations.markMessage(Message(
        from=messages[0].m_from,
        to=messages[0].m_to,
        subject=messages[0].m_subject,
        date=messages[0].m_date,
        id=messages[0].m_id,
        markType="read"
    ))
    cascade.operations.deleteMessage(messages[1])
    
    results = cascade.submit_requests()
    for res in results:
        if isinstance(res, CascadeError):
            print(f"Error: {res.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import CascadeError, preference

# Read current user preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Update a specific preference
cascade.operations.editPreference(preference(name="dateFormat", value="yyyy-MM-dd"))
edit_result = cascade.submit_requests()

if isinstance(edit_result, CascadeError):
    raise RuntimeError(edit_result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.2.1 -->
