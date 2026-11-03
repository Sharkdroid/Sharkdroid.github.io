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
    # 1. Define the path identifier for the asset
    identifier = Path(asset_type="page", site_name="default", path="/index")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for errors before using the result
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape that most other fetch operations follow, such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to what was requested, which can then be inspected or processed further in your script.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define the path identifier for the asset to delete
    identifier = Path(asset_type="page", site_name="default", path="/old-page")
    
    # 2. Define delete parameters payload
    payload = deleteParameters(
        do_workflow=False,
        destinations=[],
        unpublish=True
    )
    
    # 3. Queue the delete operation with parameters
    cascade.operations.delete(identifier, payload=payload)
    
    # 4. Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # 5. Check for errors before proceeding
    if isinstance(result, CascadeError):
        print(f"Delete failed: {result.message}")
    else:
        print("Delete succeeded!")
```

The `delete` method and other mutating operations like `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation status only rather than the modified asset data. Consequently, scripts should rely on these responses purely for confirmation rather than expecting asset details back.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Construct the required SearchInformation payload
    payload = SearchInformation(
        siteName="default",
        searchTerms="blog"
    )
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Submit all queued requests concurrently
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for errors before iterating results
    if isinstance(result, CascadeError):
        print(f"Search failed: {result.message}")
    else:
        for item in result.flat:
            print(item)
```

The `search` operation requires a strongly-typed payload object and does not support bare identifier shortcuts. Other operations throughout the library follow this exact payload-driven pattern, including `readAudits` (which uses `auditParameters`), `editWorkflowSettings`, and several preference and administrative methods.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    path_id = Path(asset_type="page", site_name="default", path="/index")
    del_path = Path(asset_type="page", site_name="default", path="/old-page")
    del_payload = deleteParameters(do_workflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="default", searchTerms="blog")

    cascade.operations.read(path_id)
    cascade.operations.delete(del_path, payload=del_payload)
    cascade.operations.search(search_payload)

    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
