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
    # Build a Path identifier pointing to a page asset
    identifier = Path(path="index", site_name="default", asset_type=AssetTypes.page)
    
    # Queue the read operation
    cascade.operations.read(identifier)
    
    # Execute the queued operations concurrently
    results = cascade.submit_requests()
    result = results[0]

    # Guard against API-level failures
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow—such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to the domain of what was requested.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    identifier = Path(path="old-page", site_name="default", asset_type=AssetTypes.page)
    
    # Configure delete parameters
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    cascade.operations.delete(identifier, payload=payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Failed to delete: {result.message}")
    else:
        print("Asset deleted successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return a confirmation rather than the modified asset itself. Callers should not expect to receive asset data back from these operations.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # Construct the required search payload
    payload = SearchInformation(
        siteName="default",
        searchTerms="about",
        searchFields=["name"],
        searchTypes=[AssetTypes.page]
    )
    
    cascade.operations.search(payload)
    results = cascade.submit_requests()
    result = results[0]

    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over the flat list of results
        for item in result.flat:
            print(item)
```

The `search` operation requires a typed payload object with no bare identifier shortcut. Other operations like `readAudits` (which uses `auditParameters`), `editWorkflowSettings`, and similar commands follow this exact payload-driven pattern.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    path_id = Path(path="index", site_name="default", asset_type=AssetTypes.page)
    del_path = Path(path="old-page", site_name="default", asset_type=AssetTypes.page)
    
    # Queue three independent chains of different operation types
    cascade.operations.read(path_id)
    cascade.operations.delete(del_path, payload=deleteParameters(doWorkflow=False, destinations=[], unpublish=True))
    cascade.operations.search(SearchInformation(siteName="default", searchTerms="test"))
    
    # All three run concurrently and results are returned in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
