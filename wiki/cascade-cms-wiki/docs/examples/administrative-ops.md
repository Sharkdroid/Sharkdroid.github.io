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
from cascade_cms.cmstypes import CascadeError

cascade = CascadeCMS("https://cascade.example.com", "username", "api-key")

# Phase 1: List inbox messages
cascade.operations.listMessages()
messages = cascade.submit_requests()

if isinstance(messages, CascadeError):
    print(f"Failed to list messages: {messages.message}")
else:
    # Phase 2: Mark or delete messages using retrieved Message objects
    for msg in messages.elements:
        cascade.operations.markMessage(msg)
        # or cascade.operations.deleteMessage(msg)
        
    result = cascade.submit_requests()
    if isinstance(result, CascadeError):
        print(f"Message operation failed: {result.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms import CascadeCMS
from cascade_cms.cmstypes import CascadeError, preference

cascade = CascadeCMS("https://cascade.example.com", "username", "api-key")

# Phase 1: Read current user preferences
cascade.operations.readPreferences()
prefs = cascade.submit_requests()

if isinstance(prefs, CascadeError):
    print(f"Failed to read preferences: {prefs.message}")
else:
    # Phase 2: Update a specific preference
    cascade.operations.editPreference(preference(name="theme", value="dark"))
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Failed to update preference: {result.message}")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.1 -->
