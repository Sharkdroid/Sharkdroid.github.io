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
wrapper.operations.listMessages()
results = wrapper.submit_requests()
messages_result = results[0]

if isinstance(messages_result, CascadeError):
    raise RuntimeError(messages_result.message)

# Assume we want to mark the first message read and delete the second
messages = messages_result.flat

if messages:
    # Phase 2: Mark read and delete selected messages
    wrapper.operations.markMessage(messages[0])
    wrapper.operations.deleteMessage(messages[1])
    action_results = wrapper.submit_requests()

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
from cascade_cms.cmstypes import CascadeError, preference

# Phase 1: Read current user preferences
wrapper.operations.readPreferences()
results = wrapper.submit_requests()
prefs_result = results[0]

if isinstance(prefs_result, CascadeError):
    raise RuntimeError(prefs_result.message)

# Phase 2: Update a user preference
wrapper.operations.editPreference(preference(name="theme", value="dark"))
edit_results = wrapper.submit_requests()

if isinstance(edit_results[0], CascadeError):
    raise RuntimeError(edit_results[0].message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.5 -->
