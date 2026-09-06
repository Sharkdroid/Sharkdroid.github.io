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
# Phase 1: List inbox messages
cascade.operations.listMessages()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Error listing messages: {result.message}")
else:
    # Phase 2: Mark or delete a message using a retrieved Message object
    messages = result.flat
    if messages:
        msg = messages[0]
        # Mark as read
        cascade.operations.markMessage(msg)
        res1 = cascade.submit_requests()
        if isinstance(res1, CascadeError):
            print(f"Error marking message: {res1.message}")

        # Or delete the message
        cascade.operations.deleteMessage(msg)
        res2 = cascade.submit_requests()
        if isinstance(res2, CascadeError):
            print(f"Error deleting message: {res2.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
# Read current user preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Error reading preferences: {result.message}")
else:
    # Update a user preference
    pref = preference(name="somePreferenceName", value="new-value")
    cascade.operations.editPreference(pref)
    edit_result = cascade.submit_requests()
    if isinstance(edit_result, CascadeError):
        print(f"Error updating preference: {edit_result.message}")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.3 -->
