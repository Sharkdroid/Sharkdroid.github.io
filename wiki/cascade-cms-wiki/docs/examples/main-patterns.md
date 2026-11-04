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
    identifier = Path(asset_type="page", site_name="Default", path="/index")
    
    # 2. Queue the read operation
    cascade.operations.read(identifier)
    
    # 3. Submit requests concurrently and retrieve results
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for errors before inspecting the asset
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print(result.displayName)
        print(result.metadata)
```

The `read` operation represents the response shape most other "fetch" operations follow — such as `readAudits`, `readAccessRights`, and `readWorkflowSettings`. Each of these operations returns a structured object specific to what was requested, wrapping the server's payload into a usable Pydantic model or dynamic asset wrapper.

---

## Pattern 2 — `delete`: a simple success response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Define a Path identifier and deleteParameters payload
    identifier = Path(asset_type="page", site_name="Default", path="/old-page")
    payload = deleteParameters(
        doWorkflow=False,
        destinations=[],
        unpublish=True
    )
    
    # 2. Queue the delete operation
    cascade.operations.delete(identifier, payload=payload)
    
    # 3. Submit requests and retrieve results
    results = cascade.submit_requests()
    result = results[0]
    
    # 4. Check for errors and handle the success response
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        print("Asset deleted successfully.")
```

Mutating operations like `delete`, `copy`, `move`, `publish`, `checkIn`, and `editAccessRights` return confirmation only rather than the modified asset data. Callers should expect a `CascadeSuccess` object on success, so asset data cannot be read back directly from these return values.

---

## Pattern 3 — `search`: payload-driven, list response

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    # 1. Construct the required SearchInformation payload
    payload = SearchInformation(
        siteName="Default",
        searchTerms="blog"
    )
    
    # 2. Queue the search operation
    cascade.operations.search(payload)
    
    # 3. Submit requests and inspect the returned elements
    results = cascade.submit_requests()
    result = results[0]
    
    if isinstance(result, CascadeError):
        print(f"Error: {result.message}")
    else:
        for item in result.flat:
            print(item)
```

The `search` operation requires a typed payload object (like `SearchInformation`) to specify criteria, using no bare identifier shortcuts. Other operations such as `readAudits` (which uses `auditParameters`) and `editWorkflowSettings` follow the same payload-driven pattern.

---

## Chaining and Batching

All three patterns above run a single operation per script. In practice you can
queue multiple chains — even mixing operation types — before calling
`submit_requests()` once:

```python
with CascadeWrapperBase("https://cascade.example.com", "username", "api-key") as cascade:
    identifier = Path(asset_type="page", site_name="Default", path="/index")
    delete_path = Path(asset_type="page", site_name="Default", path="/old-page")
    del_payload = deleteParameters(doWorkflow=False, destinations=[], unpublish=True)
    search_payload = SearchInformation(siteName="Default", searchTerms="blog")

    cascade.operations.read(identifier)
    cascade.operations.delete(delete_path, payload=del_payload)
    cascade.operations.search(search_payload)

    # All three chains run concurrently; results are returned in creation order.
    results = cascade.submit_requests()
```

See [Administrative Operations](administrative-ops.md) for the `messages` and `preferences` operations.

<!-- synthesized-for: 3.9.2 -->
