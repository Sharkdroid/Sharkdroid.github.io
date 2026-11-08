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

async with CascadeCMS() as cascade:
    # Phase 1: List inbox messages
    cascade.operations.listMessages()
    results = await cascade.submit_requests()
    messages_result = results[0]

    if isinstance(messages_result, CascadeError):
        raise RuntimeError(messages_result.message)

    # Assume we find a message to mark and another to delete
    inbox = messages_result.flat
    if inbox:
        target_msg = inbox[0]

        # Phase 2: Mark message read state and delete a message
        cascade.operations.markMessage(target_msg)
        cascade.operations.deleteMessage(target_msg)
        action_results = await cascade.submit_requests()

        for res in action_results:
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

async with CascadeCMS() as cascade:
    # Read current user preferences
    cascade.operations.readPreferences()
    results = await cascade.submit_requests()
    prefs_result = results[0]

    if isinstance(prefs_result, CascadeError):
        raise RuntimeError(prefs_result.message)

    # Update a user preference
    cascade.operations.editPreference(preference(name="theme", value="dark"))
    edit_results = await cascade.submit_requests()
    edit_result = edit_results[0]

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
