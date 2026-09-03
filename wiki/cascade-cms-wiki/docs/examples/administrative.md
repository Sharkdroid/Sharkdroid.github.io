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
    raise RuntimeError(result.message)

# Suppose we pick a message from the list elements
message = result.elements[0]

# Phase 2: Mark read and delete
cascade.operations.markMessage(message)
cascade.operations.deleteMessage(message)
results = cascade.submit_requests()

for r in results:
    if isinstance(r, CascadeError):
        raise RuntimeError(r.message)
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
# Phase 1: Read current user preferences
cascade.operations.readPreferences()
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)

# Phase 2: Update a preference using the preference payload
cascade.operations.editPreference(preference(name="theme", value="dark"))
result = cascade.submit_requests()

if isinstance(result, CascadeError):
    raise RuntimeError(result.message)
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.1.3 -->
