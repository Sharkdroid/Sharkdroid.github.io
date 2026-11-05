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
    # Build a Path identifier pointing to a page in the default site
    identifier = Path(asset_type=AssetTypes.page, path="/index", site_name="default")
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # Check if the result is an API-level error
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow—such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`—meaning they all return a structured object specific to what was requested rather than raw JSON dictionaries.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Build a Path identifier for the asset to delete
    identifier = Path(asset_type=AssetTypes.page, path="/old-page", site_name="default")
    
    # Configure delete parameters
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # Queue the delete operation with parameters
    cascade.operations.delete(identifier, payload=payload)
    
    # Execute the request queue
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation only via a `CascadeSuccess` object rather than the modified asset data. Callers should not expect asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("config.json") as cascade:
    # Construct a SearchInformation payload object
    payload = SearchInformation(
        siteName="default",
        searchTerms="news",
        searchFields=[FieldsSearchTypes.name],
        searchTypes=[AssetTypes.page]
    )
    
    # Queue the search operation
    cascade.operations.search(payload)
    
    # Execute requests
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list elements returned in the search response
        for item in result.flat:
            print(item)
```

The `search` operation requires a strongly-typed payload object (`SearchInformation`) rather than a bare identifier shortcut. Other administrative and query operations follow this exact same pattern by accepting dedicated parameters objects like `auditParameters` for `readAudits`.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("config.json") as cascade:
    path_id = Path(asset_type=AssetTypes.page, path="/index", site_name="default")
    del_id = Path(asset_type=AssetTypes.page, path="/old-page", site_name="default")
    
    # Queue three independent chains (read, delete, and search)
    cascade.operations.read(path_id)
    cascade.operations.delete(del_id, payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="test"))
    
    # All three chains run concurrently; results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
