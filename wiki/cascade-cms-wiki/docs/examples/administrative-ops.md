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

# 1. List inbox messages
cascade.operations.listMessages()
results = cascade.submit_requests()
messages_result = results[0]

if isinstance(messages_result, CascadeError):
    print(f"Failed to list messages: {messages_result.message}")
else:
    # flat returns a list of Message objects
    inbox = messages_result.flat
    if inbox:
        msg = inbox[0]
        
        # 2. Mark the message as read/unread and then delete it
        cascade.operations.markMessage(msg)
        cascade.operations.deleteMessage(msg)
        action_results = cascade.submit_requests()
        
        for res in action_results:
            if isinstance(res, CascadeError):
                print(f"Operation failed: {res.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS, CascadeError, preference

# 1. Read current preferences
cascade.operations.readPreferences()
results = cascade.submit_requests()
pref_result = results[0]

if isinstance(pref_result, CascadeError):
    print(f"Failed to read preferences: {pref_result.message}")
else:
    # 2. Update a preference
    cascade.operations.editPreference(preference(name="example_pref", value="new_value"))
    edit_results = cascade.submit_requests()
    
    if isinstance(edit_results[0], CascadeError):
        print(f"Failed to update preference: {edit_results[0].message}")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.2 -->
