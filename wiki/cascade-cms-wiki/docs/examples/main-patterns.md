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
    # Build a Path identifier pointing to a page asset
    path = Path(asset_type="page", path="/index", siteName="Default")
    
    # Queue the read operation
    cascade.operations.read(path)
    
    # Submit all queued operations concurrently
    result = cascade.submit_requests()
    
    # Failures are returned as values, never raised
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset data
        print(result.displayName)
        print(result.metadata)
```

The `read` pattern represents the response shape most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to the domain of what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Build a Path identifier pointing to the asset to delete
    path = Path(asset_type="page", path="/old-page", siteName="Default")
    
    # Build delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # Queue the delete operation with parameters
    cascade.operations.delete(path, payload=payload)
    
    # Submit the request
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Failed to delete: {result.message}")
    else:
        print("Asset successfully deleted.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation objects (`CascadeSuccess`) only, rather than the modified asset itself. Callers should not expect full asset data back from these operation endpoints.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Construct the required search information payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Submit the request
    result = cascade.submit_requests()
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of elements returned
        for item in result.flat:
            print(item)
```

The `search` operation requires a typed payload object (such as `SearchInformation`) rather than a bare identifier shortcut. Other administrative and query operations follow this same design pattern, including `readAudits` (taking `auditParameters`) and `editWorkflowSettings`.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("config.json") as cascade:
    path = Path(asset_type="page", path="/index", siteName="Default")
    delete_path = Path(asset_type="page", path="/old-page", siteName="Default")
    delete_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="Default", searchTerms="news")

    # Queue three independent chains in a single wrapper block
    cascade.operations.read(path)
    cascade.operations.delete(delete_path, payload=delete_payload)
    cascade.operations.search(search_payload)

    # All three chains run concurrently; results are returned in creation order
    results = cascade.submit_requests()
    print(results)
```

See [Administrative Operations](administrative.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.1.5 -->
