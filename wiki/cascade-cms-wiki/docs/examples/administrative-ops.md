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
    list_result = await cascade.submit_requests()

    if isinstance(list_result, CascadeError):
        raise RuntimeError(list_result.message)

    # Assume we pick the first message from elements
    messages = list_result.flat
    if messages:
        msg = messages[0]

        # Phase 2: Mark message read and then delete it
        cascade.operations.markMessage(msg)
        cascade.operations.deleteMessage(msg)
        results = await cascade.submit_requests()

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
from cascade_cms import CascadeCMS, CascadeError, preference

async with CascadeCMS("https://cascade.example.com", "user", "pass") as cascade:
    # Read current user preferences
    cascade.operations.readPreferences()
    prefs_result = await cascade.submit_requests()

    if isinstance(prefs_result, CascadeError):
        raise RuntimeError(prefs_result.message)

    # Update a single preference
    cascade.operations.editPreference(preference(name="myPreference", value="newValue"))
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
