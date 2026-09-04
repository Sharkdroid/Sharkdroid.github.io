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

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define a Path identifier for the asset
    identifier = Path(asset_type="page", path="index", siteName="Default")

    # 2. Queue the read operation
    cascade.operations.read(identifier)

    # 3. Execute all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # 4. Check for API errors before accessing asset fields
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` pattern represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, and others — which all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define a Path identifier for the asset to delete
    identifier = Path(asset_type="page", path="old-page", siteName="Default")

    # 2. Define the delete parameters payload
    payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)

    # 3. Queue the delete operation with parameters
    cascade.operations.delete(identifier, payload=payload)

    # 4. Execute the deletion
    results = cascade.submit_requests()
    result = results[0]

    # 5. Check if the deletion succeeded
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted!")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation only rather than the modified asset, meaning callers should not expect asset data back from these endpoints.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Construct the SearchInformation payload
    payload = SearchInformation(siteName="Default", searchTerms="welcome")

    # 2. Queue the search operation
    cascade.operations.search(payload)

    # 3. Execute the search
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle errors or iterate over results using .flat
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        for element in result.flat:
            print(element)
```

The `search` operation requires a typed payload object with no bare identifier shortcut, following the same payload-driven pattern used by `readAudits` (`auditParameters`), `editWorkflowSettings`, and similar operations.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Queue three independent chains
    cascade.operations.read(Path(asset_type="page", path="index", siteName="Default"))
    cascade.operations.delete(Path(asset_type="page", path="old-page", siteName="Default"))
    cascade.operations.search(SearchInformation(siteName="Default", searchTerms="news"))

    # All three chains run concurrently; results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.3 -->
