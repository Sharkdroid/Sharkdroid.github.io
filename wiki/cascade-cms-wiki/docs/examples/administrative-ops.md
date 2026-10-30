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

# 1. Retrieve inbox messages
driver = CascadeCMS(url="...", username="...", password="...")
list_chain = driver.operations.listMessages()
messages_result = driver.submit_requests()

if isinstance(messages_result, CascadeError):
    raise RuntimeError(messages_result.message)

messages = messages_result.flat  # list[Message]

# 2. Mark the first message as read and delete another
if messages:
    target_msg = messages[0]
    target_msg.marked = "read"

    driver.operations.markMessage(target_msg)
    driver.operations.deleteMessage(target_msg)
    action_results = driver.submit_requests()

    for res in (action_results if isinstance(action_results, list) else [action_results]):
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

# 1. Read current user preferences
driver = CascadeCMS(url="...", username="...", password="...")
driver.operations.readPreferences()
prefs_result = driver.submit_requests()

if isinstance(prefs_result, CascadeError):
    raise RuntimeError(prefs_result.message)

# 2. Update a user preference
pref_payload = preference(name="myPreferenceName", value="newValue")
driver.operations.editPreference(pref_payload)
edit_result = driver.submit_requests()

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
