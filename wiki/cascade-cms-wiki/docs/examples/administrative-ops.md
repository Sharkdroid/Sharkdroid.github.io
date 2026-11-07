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

# 1. List inbox messages
cascade.operations.listMessages()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Failed to list messages: {result.message}")
else:
    messages = result.elements
    # Find a specific message to act upon
    target_msg = next((m for m in messages if isinstance(m, Message)), None)
    
    if target_msg:
        # 2. Mark message as read
        target_msg.marked = "read"
        cascade.operations.markMessage(target_msg)
        
        # Or delete a message
        # cascade.operations.deleteMessage(target_msg)
        
        write_result = cascade.submit_requests()
        if isinstance(write_result, CascadeError):
            print(f"Failed to update message: {write_result.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.cmstypes import CascadeError, preference

# 1. Read current preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    print(f"Failed to read preferences: {result.message}")
else:
    # 2. Edit a single preference
    pref_payload = preference(name="editor", value="source")
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

<!-- synthesized-for: 3.9.2 -->
