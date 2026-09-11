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
    # result is a ListElements instance; .flat gives a list of Message items
    messages = result.flat

    # Phase 2: Mark the first message as read and delete the second
    if len(messages) >= 2:
        msg_to_mark = messages[0]
        msg_to_mark.marked = "read"
        cascade.operations.markMessage(msg_to_mark)

        cascade.operations.deleteMessage(messages[1])
        
        batch_result = cascade.submit_requests()
        if isinstance(batch_result, CascadeError):
            print(f"Error in batch update: {batch_result.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
# Read current preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Error reading preferences: {result.message}")
else:
    # Update a user preference
    pref_payload = preference(name="editor-mode", value="advanced")
    cascade.operations.editPreference(pref_payload)
    
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
