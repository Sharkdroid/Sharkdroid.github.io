# Core Patterns: `read`, `delete`, `search`

Every script that uses `cascade_cms` follows the same shape: open the wrapper as
a context manager, queue up one or more operations on `cascade.operations`, then
call `submit_requests()` once to run them all concurrently.

The three examples below use the same skeleton but highlight the **three
distinct response shapes** you'll see across the library:

| Operation | Returns | Why it's shown |
|-----------|---------|----------------|
| `read` | A large, structured `Asset` object | Most operations that touch an existing asset return this shape |
| `delete` | A simple success object (`CascadeSuccess`) | Mutating operations that don't return data use this minimal shape |
| `search` | A list result, driven by a required `SearchInformation` payload | Shows the "operation needs a payload object" pattern |

All three also demonstrate the same failure-handling rule: **failures are
returned as values, not raised.** Always check `isinstance(result, CascadeError)`
before using a result.

---

## Pattern 1 — `read`: fetching a structured asset

[PLACEHOLDER: Code block showing a minimal `read` call using `CascadeWrapperBase`, a `Path` identifier, `cascade.operations.read(identifier)`, `cascade.submit_requests()`, and an `isinstance(result, CascadeError)` guard before accessing `result.displayName` and `result.metadata`. Source from the `read` and `Path` docstrings in operations.md and cmstypes.md. Include inline `# comments` explaining each step.]

[PLACEHOLDER: 2–3 sentence "Takeaway" paragraph below the code block explaining that `read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and that they all return a structured object specific to what was requested.]

---

## Pattern 2 — `delete`: a simple success response

[PLACEHOLDER: Code block showing a `delete` call with a `Path` identifier and a `deleteParameters` payload (`doWorkflow`, `destinations`, `unpublish` fields). Show `isinstance(result, CascadeError)` guard and a success message on the happy path. Source from the `delete` and `deleteParameters` docstrings in operations.md and cmstypes.md.]

[PLACEHOLDER: 2–3 sentence "Takeaway" paragraph explaining that `delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.]

---

## Pattern 3 — `search`: payload-driven, list response

[PLACEHOLDER: Code block showing `SearchInformation` constructed with `siteName`, `searchTerms`, `searchFields`, `searchTypes` fields, passed to `cascade.operations.search(payload)`, with `submit_requests()` and an `isinstance(result, CascadeError)` guard before iterating `result.flat`. Source from `SearchInformation` and `search` docstrings in cmstypes.md and operations.md.]

[PLACEHOLDER: 2–3 sentence "Takeaway" paragraph explaining that `search` requires a typed payload object — there is no bare identifier shortcut — and naming the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.]

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

[PLACEHOLDER: Code block showing three chains queued in a single `CascadeWrapperBase` block — `read`, `delete`, and `search` — before one `submit_requests()` call, with a comment that all three run concurrently and results are returned in creation order. Source from `submit_requests` docstring in wrapper.md.]

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.
