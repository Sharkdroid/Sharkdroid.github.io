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
with CascadeWrapperBase("https://cascade.example.com", "api-key") as cascade:
    # 1. Define a Path identifier pointing to the asset
    path = Path(asset_type="page", site_name="Default", path="/index")
    
    # 2. Queue the read operation
    cascade.operations.read(path)
    
    # 3. Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle failures as returned values, not raised exceptions
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        # Access structured asset fields
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to what was requested, wrapping the server's response.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "api-key") as cascade:
    # 1. Define a Path identifier for the target asset
    path = Path(asset_type="page", site_name="Default", path="/old-page")
    
    # 2. Configure delete parameters payload
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # 3. Queue the delete operation with parameters
    cascade.operations.delete(path, payload=payload)
    
    # 4. Execute the queued requests
    results = cascade.submit_requests()
    result = results[0]

    # 5. Check for API-level failures
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation status only rather than the modified asset data itself. Callers should not expect asset content back from these calls, relying instead on `CascadeSuccess` or error responses.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "api-key") as cascade:
    # 1. Build the required SearchInformation payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="news",
        searchFields=["name"],
        searchTypes=["page"]
    )
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Execute the search
    results = cascade.submit_requests()
    result = results[0]

    # 4. Handle errors before inspecting list elements
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        # Iterate over flat list elements
        for item in result.flat:
            print(item.get_id, item.get_type)
```

The `search` method requires a strongly-typed payload object (no bare identifier shortcut is available), following the same design pattern used by operations like `readAudits` with `auditParameters`. The resulting `ListElements` container provides convenient access to matching items through its `flat` property.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "api-key") as cascade:
    path = Path(asset_type="page", site_name="Default", path="/index")
    delete_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="Default", searchTerms="test")

    # Queue multiple independent chains
    cascade.operations.read(path)
    cascade.operations.delete(path, payload=delete_payload)
    cascade.operations.search(search_payload)

    # All three run concurrently, returning results in creation order
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
