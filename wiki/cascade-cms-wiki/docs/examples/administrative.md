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
    
    # Phase 2: Mark the first message as read and delete the second
    if len(messages) > 0:
        msg_to_mark = messages[0]
        msg_to_mark.marked = "read"
        cascade.operations.markMessage(msg_to_mark)
        
    if len(messages) > 1:
        msg_to_delete = messages[1]
        cascade.operations.deleteMessage(msg_to_delete)
        
    mark_delete_result = cascade.submit_requests()
    if isinstance(mark_delete_result, CascadeError):
        print(f"Failed to update/delete message: {mark_delete_result.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
# Read current preferences
cascade.operations.readPreferences()
prefs_result = cascade.submit_requests()

if isinstance(prefs_result, CascadeError):
    print(f"Failed to read preferences: {prefs_result.message}")
else:
    # Update a specific preference
    pref_payload = preference(name="theme", value="dark")
    cascade.operations.editPreference(pref_payload)
    edit_result = cascade.submit_requests()
    
    if isinstance(edit_result, CascadeError):
        print(f"Failed to update preference: {edit_result.message}")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.3 -->
