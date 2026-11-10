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
from cascade_cms.cmstypes import CascadeError

# Phase 1: List inbox messages
cascade.operations.listMessages()
messages_result = cascade.submit_requests()

if isinstance(messages_result, CascadeError):
    print(f"Failed to list messages: {messages_result.message}")
else:
    # Get the flat list of messages
    messages = messages_result.flat

    if messages:
        target_message = messages[0]

        # Phase 2: Mark the message as read, then delete it
        cascade.operations.markMessage(target_message)
        cascade.operations.deleteMessage(target_message)
        results = cascade.submit_requests()

        for res in results:
            if isinstance(res, CascadeError):
                print(f"Operation failed: {res.message}")
            else:
                print("Operation succeeded.")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import CascadeError, preference

# Phase 1: Read current user preferences
cascade.operations.readPreferences()
prefs_result = cascade.submit_requests()

if isinstance(prefs_result, CascadeError):
    print(f"Failed to read preferences: {prefs_result.message}")
else:
    # Phase 2: Update a specific preference
    new_pref = preference(name="dateFormat", value="YYYY-MM-DD")
    cascade.operations.editPreference(new_pref)
    edit_result = cascade.submit_requests()

    if isinstance(edit_result, CascadeError):
        print(f"Failed to update preference: {edit_result.message}")
    else:
        print("Preference updated successfully.")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.2 -->
