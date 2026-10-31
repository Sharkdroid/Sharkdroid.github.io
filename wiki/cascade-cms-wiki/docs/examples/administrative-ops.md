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

async with CascadeCMS("https://cascade.example.com", "user", "pass") as cascade:
    # Phase 1: List inbox messages
    cascade.operations.listMessages()
    result = await cascade.submit_requests()

    if isinstance(result, CascadeError):
        raise RuntimeError(result.message)

    messages = result.elements

    # Phase 2: Mark or delete selected messages
    for msg in messages:
        cascade.operations.markMessage(msg)
    
    # Or delete a specific message
    if messages:
        cascade.operations.deleteMessage(messages[0])

    delete_result = await cascade.submit_requests()
    if isinstance(delete_result, CascadeError):
        raise RuntimeError(delete_result.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS, CascadeError, preference

async with CascadeCMS("https://cascade.example.com", "user", "pass") as cascade:
    # Read current preferences
    cascade.operations.readPreferences()
    result = await cascade.submit_requests()

    if isinstance(result, CascadeError):
        raise RuntimeError(result.message)

    # Update a preference
    cascade.operations.editPreference(preference(name="dateFormat", value="yyyy-MM-dd"))
    edit_result = await cascade.submit_requests()

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
