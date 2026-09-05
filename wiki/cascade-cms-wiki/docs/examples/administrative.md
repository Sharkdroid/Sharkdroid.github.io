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
    print(f"Failed to list messages: {result.message}")
else:
    # result is a ListElements container containing Message objects
    messages = result.flat

    # Phase 2: Mark the first message as read and delete another
    if messages:
        msg_to_read = messages[0]
        msg_to_read.marked = "read"

        cascade.operations.markMessage(msg_to_read)
        res_mark = cascade.submit_requests()

        if isinstance(res_mark, CascadeError):
            print(f"Failed to mark message: {res_mark.message}")

        if len(messages) > 1:
            msg_to_delete = messages[1]
            cascade.operations.deleteMessage(msg_to_delete)
            res_delete = cascade.submit_requests()

            if isinstance(res_delete, CascadeError):
                print(f"Failed to delete message: {res_delete.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
# Step 1: Read current user preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Failed to read preferences: {result.message}")
else:
    # Step 2: Update a user preference
    cascade.operations.editPreference(preference(name="ui_theme", value="dark"))
    res_edit = cascade.submit_requests()

    if isinstance(res_edit, CascadeError):
        print(f"Failed to update preference: {res_edit.message}")
    else:
        print("Preference updated successfully.")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.3 -->
