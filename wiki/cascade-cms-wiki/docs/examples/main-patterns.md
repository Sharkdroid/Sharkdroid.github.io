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
with CascadeWrapperBase("config.json") as cascade:
    # Define a Path identifier for the asset
    path = Path(path="index", siteName="Default", asset_type="page")
    
    # Queue the read operation
    cascade.operations.read(path)
    
    # Execute all queued requests
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level errors
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and that they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Define a Path identifier for the asset to delete
    path = Path(path="old-page", siteName="Default", asset_type="page")
    
    # Prepare delete parameters payload
    params = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    
    # Queue the delete operation
    cascade.operations.delete(path, payload=params)
    
    # Execute all queued requests
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level errors
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset deleted successfully.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Construct the required SearchInformation payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Execute all queued requests
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level errors
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of elements
        for element in result.flat:
            print(element)
```

`search` requires a typed payload object — there is no bare identifier shortcut — and naming the other operations that follow the same pattern: `readAudits` (`auditParameters`), `editWorkflowSettings`, etc.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("config.json") as cascade:
    path_read = Path(path="index", siteName="Default", asset_type="page")
    path_delete = Path(path="old-page", siteName="Default", asset_type="page")
    search_payload = SearchInformation(siteName="Default", searchTerms="news")

    # Queue three independent chains
    cascade.operations.read(path_read)
    cascade.operations.delete(path_delete, payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(search_payload)

    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.2.1 -->
