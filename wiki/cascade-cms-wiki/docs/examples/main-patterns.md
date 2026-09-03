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
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Build a path identifier for the page
    path = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue the read operation
    cascade.operations.read(path)
    
    # Run the queued operations concurrently
    result = cascade.submit_requests()[0]
    
    # Failures are returned as values, not raised
    if isinstance(result, CascadeError):
        print(f"Read failed: {result.message}")
    else:
        # Access asset properties via get() or dynamic attributes
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Build a path identifier for the page to delete
    path = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Configure delete parameters
    params = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    
    # Queue the delete operation
    cascade.operations.delete(path, payload=params)
    
    # Run the queued operations
    result = cascade.submit_requests()[0]
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted!")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    # Build search parameters
    search_info = SearchInformation(siteName="Default", searchTerms="report")
    
    # Queue the search operation
    cascade.operations.search(search_info)
    
    # Run the queued operations
    result = cascade.submit_requests()[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the matched elements
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
with CascadeWrapperBase("https://cascade.example.com", "username", "password") as cascade:
    path = Path(asset_type="page", path="/index", siteName="Default")
    search_info = SearchInformation(siteName="Default", searchTerms="report")

    # Queue multiple independent chains
    cascade.operations.read(path)
    cascade.operations.delete(path, payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(search_info)

    # Submit all chains concurrently; results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.3 -->
