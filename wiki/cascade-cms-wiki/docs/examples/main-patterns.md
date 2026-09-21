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
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    # Build a Path identifier referencing a page
    path = Path(path="/index", asset_type="page", siteName="default-site")
    
    # Queue the read operation
    cascade.operations.read(path)
    
    # Execute all queued operations concurrently
    result = cascade.submit_requests()
    
    # Check if the operation resulted in an error
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured properties on the resulting Asset
        print(result.displayName)
        print(result.metadata)
```

`read` represents the response shape most other "fetch" operations follow — `readAudits`, `readAccessRights`, `readWorkflowSettings`, etc. — and they all return a structured object specific to what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    # Build a Path identifier referencing an asset to delete
    path = Path(path="/old-page", asset_type="page", siteName="default-site")
    
    # Build delete parameters payload
    payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    
    # Queue the delete operation
    cascade.operations.delete(path, payload=payload)
    
    # Execute requests
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Asset successfully deleted.")
```

`delete` and other mutating operations (`copy`, `move`, `publish`, `checkIn`, `editAccessRights`) return confirmation only — not the modified asset — so callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    # Build SearchInformation payload
    payload = SearchInformation(
        siteName="default-site",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Execute requests
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over elements in the list result using .flat
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
with CascadeWrapperBase("https://cascade.example.com", "username", "password", "default-site") as cascade:
    path = Path(path="/index", asset_type="page", siteName="default-site")
    delete_path = Path(path="/old-page", asset_type="page", siteName="default-site")
    delete_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="default-site", searchTerms="news")

    # Queue multiple independent chains; all three run concurrently upon submission
    cascade.operations.read(path)
    cascade.operations.delete(delete_path, payload=delete_payload)
    cascade.operations.search(search_payload)

    results = cascade.submit_requests()
    # results is a list containing the outcome of each chain in creation order
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.6 -->
