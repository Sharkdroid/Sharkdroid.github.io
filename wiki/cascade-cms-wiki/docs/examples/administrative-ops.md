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
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import CascadeSuccess, ListElements

with Cascade(env) as cascade:
    # Phase 1: List inbox messages
    listed = cascade.operations.listMessages().submit_requests(ListElements)

    # Pick a message from the list elements
    message = listed.success[0].flat[0]

    # Phase 2: Mark as read and then delete
    results = (
        cascade.operations
        .markMessage(message)
        .deleteMessage(message)
        .submit_requests(CascadeSuccess)
    )

for failure in results.failed:
    print(f"[{failure.category}] {failure.step_name}: {failure.message}")
```

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

```python
from cascade_cms.wrapper import Cascade
from cascade_cms.cmstypes import CascadeSuccess, SimplePayload, preference

with Cascade(env) as cascade:
    # Read current preferences
    prefs = cascade.operations.readPreferences().submit_requests(SimplePayload)

    # Update a user preference
    results = (
        cascade.operations
        .editPreference(preference(name="pref_name", value="new_value"))
        .submit_requests(CascadeSuccess)
    )

for failure in results.failed:
    print(f"[{failure.category}] {failure.step_name}: {failure.message}")
```

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.

<!-- synthesized-for: 3.9.1 -->
