# Administrative Operations: Messages & Preferences

These operations don't touch CMS assets — they manage the current user's
inbox and account preferences. They're grouped separately from the main
patterns doc because they're a self-contained feature area, not part of the
asset read/write/search workflow.

Both examples follow the same wrapper → operations → `submit_requests()`
skeleton as the main patterns, just applied to two unrelated features.

---

## Messages: list, mark, delete

[PLACEHOLDER: Code block showing a two-phase messages flow — first phase: `listMessages()` + `submit_requests()` to retrieve the inbox; second phase: `markMessage(message)` and `deleteMessage(message)` on selected `Message` objects + second `submit_requests()`. Include `isinstance(result, CascadeError)` guards at each phase. Source from `listMessages`, `markMessage`, `deleteMessage`, and `Message` docstrings in operations.md and cmstypes.md.]

!!! note
    `markMessage` and `deleteMessage` both take a `Message` object — typically
    one retrieved from `listMessages` — rather than a bare identifier.

---

## Preferences: read, edit

[PLACEHOLDER: Code block showing a two-call preferences flow — `readPreferences()` + `submit_requests()` to read current preferences, then `editPreference(preference(name=..., value=...))` + `submit_requests()` to update one. Include `isinstance(result, CascadeError)` guards. Source from `readPreferences`, `editPreference`, and `preference` docstrings in operations.md and cmstypes.md.]

!!! note
    `editPreference` takes one `preference` (name/value pair) at a time —
    there is no bulk-preference-update operation.

---

See [Core Patterns](main-patterns.md) for `read`, `delete`, and `search` — the
primary asset-management workflow and response-shape conventions.
